import base64
import binascii
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from secrets import token_bytes, token_urlsafe
from datetime import datetime, timezone
from time import time
from uuid import UUID
import httpx
from fastapi import Request
from sqlalchemy import text
from .database import Database
from .errors import ApiError

@dataclass(frozen=True)
class Identity: id: UUID; email: str; name: str; password_change_required: bool = False; username: str = ""

PLATFORM_COOKIE = "ams_platform_session"
USER_COOKIE = "ams_user_session"
MOBILE_COOKIE = "ams_mobile_session"

DEMO_PROFILES = [
    {"id": "11111111-1111-4111-8111-111111111111", "name": "Aarav Mehta", "email": "admin@rally.example", "label": "Academy administrator"},
    {"id": "22222222-2222-4222-8222-222222222222", "name": "Nisha Rao", "email": "coach@rally.example", "label": "Coach · Indiranagar only"},
    {"id": "33333333-3333-4333-8333-333333333333", "name": "Dev Sharma", "email": "admin@spin.example", "label": "Second academy administrator"},
    {"id": "44444444-4444-4444-8444-444444444444", "name": "Platform owner", "email": "owner@ams.example", "label": "Academy onboarding"},
    {"id": "55555555-5555-4555-8555-555555555555", "name": "Priya Sen", "email": "priya@example.test", "label": "New invite recipient"},
]

class AuthService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.demo = os.getenv("DEV_AUTH") == "true"
        if self.demo and os.getenv("NODE_ENV") not in ("development", "test"):
            raise RuntimeError("DEV_AUTH requires NODE_ENV=development or test.")
        configured_secret = os.getenv("PLATFORM_SESSION_SECRET", "").encode()
        if os.getenv("NODE_ENV") == "production" and len(configured_secret) < 32:
            raise RuntimeError("PLATFORM_SESSION_SECRET must contain at least 32 characters.")
        # Development sessions deliberately expire after an API restart.
        self.secret = configured_secret or token_bytes(32)
        dummy_salt = bytes(16)
        dummy_digest = hashlib.scrypt(b"unavailable-platform-password", salt=dummy_salt, n=16384, r=8, p=1, dklen=32)
        self.dummy_hash = f"scrypt$16384$8$1${base64.b64encode(dummy_salt).decode()}${base64.b64encode(dummy_digest).decode()}"
        if not self.demo and (not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_ANON_KEY")):
            raise RuntimeError("Supabase authentication is not configured.")

    @staticmethod
    def check_password(password: str, encoded: str) -> bool:
        try:
            algorithm, cost, block_size, parallelism, salt, expected = encoded.split("$")
            if algorithm != "scrypt": raise ValueError()
            actual = hashlib.scrypt(password.encode(), salt=base64.b64decode(salt), n=int(cost), r=int(block_size), p=int(parallelism), dklen=len(base64.b64decode(expected)))
            return hmac.compare_digest(actual, base64.b64decode(expected))
        except (ValueError, TypeError, binascii.Error):
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        salt = token_bytes(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
        return f"scrypt$16384$8$1${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"

    async def platform_sign_in(self, username: str, password: str) -> str:
        async with self.db.sessions.begin() as session:
            credential = (await session.execute(text('SELECT * FROM app_private.platform_owner_credential(:username)'), {"username": username})).mappings().first()
            password_valid = self.check_password(password, credential["passwordHash"] if credential and credential["passwordHash"] else self.dummy_hash)
            valid = bool(credential and credential["active"] and password_valid)
            locked = bool(credential and credential["lockedUntil"] and credential["lockedUntil"] > datetime.now(timezone.utc))
            authenticated = valid and not locked
            if credential and not locked: await session.execute(text('SELECT app_private.record_platform_login(:owner, :valid)'), {"owner": credential["userId"], "valid": authenticated})
        if not authenticated: raise ApiError(401, "Invalid username or password.")
        return self.issue_platform(credential["userId"], credential["name"], username, credential["passwordHash"])

    def credential_tag(self, password_hash: str) -> str:
        return hmac.new(self.secret, password_hash.encode(), hashlib.sha256).hexdigest()

    def issue_platform(self, user_id: UUID, name: str, username: str, password_hash: str) -> str:
        payload = base64.urlsafe_b64encode(json.dumps({"kind": "platform", "sub": str(user_id), "name": name, "username": username, "pwd": self.credential_tag(password_hash), "exp": int(time() * 1000) + 28_800_000}).encode()).rstrip(b"=").decode()
        return f"{payload}.{hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()}"

    async def verify_platform(self, token: str) -> Identity:
        try:
            payload, signature = token.split(".")
            expected = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected): raise ValueError()
            data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
            if data.get("kind") != "platform" or data["exp"] <= int(time() * 1000): raise ValueError()
            async with self.db.sessions.begin() as session:
                credential = (await session.execute(text('SELECT * FROM app_private.platform_owner_credential(:username)'), {"username": data["username"]})).mappings().first()
            if not credential or not credential["active"] or str(credential["userId"]) != data["sub"] or not hmac.compare_digest(data.get("pwd", ""), self.credential_tag(credential["passwordHash"] or "")): raise ValueError()
            return Identity(UUID(data["sub"]), f"{data['username']}@platform.local", data["name"], username=data["username"])
        except (ValueError, KeyError, json.JSONDecodeError):
            raise ApiError(401, "Please sign in again.")

    async def password_sign_in(self, username: str, password: str) -> str:
        async with self.db.sessions.begin() as session:
            credential = (await session.execute(text('SELECT * FROM app_private.user_credential(:username)'), {"username": username})).mappings().first()
            password_valid = self.check_password(password, credential["passwordHash"] if credential else self.dummy_hash)
            valid = bool(credential and credential["active"] and password_valid)
            locked = bool(credential and credential["lockedUntil"] and credential["lockedUntil"] > datetime.now(timezone.utc))
            authenticated = valid and not locked
            if credential and not locked: await session.execute(text('SELECT app_private.record_user_login(:user, :valid)'), {"user": credential["userId"], "valid": authenticated})
        if not authenticated: raise ApiError(401, "Invalid username or password.")
        return self.issue_user(credential["userId"], credential["name"], credential["email"], credential["passwordChangeRequired"], username, credential["passwordHash"])

    async def mobile_sign_in(self, username: str, password: str) -> str:
        # Use the same lockout and password checks as the user application.
        await self.password_sign_in(username, password)
        token = token_urlsafe(48)
        async with self.db.sessions.begin() as session:
            credential = (await session.execute(text('SELECT * FROM app_private.user_credential(:username)'), {"username": username})).mappings().first()
            await session.execute(text('SELECT app_private.create_mobile_session(:user,:hash)'), {"user": credential["userId"], "hash": hashlib.sha256(token.encode()).hexdigest()})
        return token

    async def mobile_identity(self, token: str) -> Identity:
        async with self.db.sessions.begin() as session:
            value = (await session.execute(text('SELECT * FROM app_private.mobile_session(:hash)'), {"hash": hashlib.sha256(token.encode()).hexdigest()})).mappings().first()
        if not value: raise ApiError(401, "Please sign in again.")
        return Identity(value["userId"], value["email"], value["name"], value["passwordChangeRequired"], value["username"])

    async def mobile_sign_out(self, token: str) -> None:
        async with self.db.sessions.begin() as session:
            await session.execute(text('SELECT app_private.revoke_mobile_session(:hash)'), {"hash": hashlib.sha256(token.encode()).hexdigest()})

    async def mobile_change_password(self, identity: Identity, password: str) -> str:
        await self.change_password(identity, password)
        token = token_urlsafe(48)
        async with self.db.sessions.begin() as session:
            await session.execute(text('SELECT app_private.create_mobile_session(:user,:hash)'), {"user": identity.id, "hash": hashlib.sha256(token.encode()).hexdigest()})
        return token

    def issue_user(self, user_id: UUID, name: str, email: str, password_change_required: bool, username: str, password_hash: str) -> str:
        payload = base64.urlsafe_b64encode(json.dumps({"kind": "user", "sub": str(user_id), "name": name, "email": email, "username": username, "change": password_change_required, "pwd": self.credential_tag(password_hash), "exp": int(time() * 1000) + 28_800_000}).encode()).rstrip(b"=").decode()
        return f"{payload}.{hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()}"

    async def verify_user(self, token: str) -> Identity:
        try:
            payload, signature = token.split(".")
            if not hmac.compare_digest(signature, hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()): raise ValueError()
            data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
            if data.get("kind") != "user" or data["exp"] <= int(time() * 1000): raise ValueError()
            async with self.db.sessions.begin() as session:
                credential = (await session.execute(text('SELECT * FROM app_private.user_credential(:username)'), {"username": data["username"]})).mappings().first()
            if not credential or not credential["active"] or str(credential["userId"]) != data["sub"] or not hmac.compare_digest(data.get("pwd", ""), self.credential_tag(credential["passwordHash"])): raise ValueError()
            return Identity(UUID(data["sub"]), data["email"], data["name"], credential["passwordChangeRequired"], data["username"])
        except (ValueError, KeyError, json.JSONDecodeError):
            raise ApiError(401, "Please sign in again.")

    async def change_password(self, identity: Identity, password: str) -> str:
        if not identity.password_change_required: raise ApiError(403, "A password change is not required.")
        return await self.update_password(identity, None, password)

    async def update_password(self, identity: Identity, current_password: str | None, password: str) -> str:
        async with self.db.sessions.begin() as session:
            credential = (await session.execute(text('SELECT * FROM app_private.user_credential(:username)'), {"username": identity.username})).mappings().first()
        if not credential or credential["userId"] != identity.id or not credential["active"]: raise ApiError(401, "Please sign in again.")
        if current_password is not None and not self.check_password(current_password, credential["passwordHash"]): raise ApiError(401, "Current password is incorrect.")
        if self.check_password(password, credential["passwordHash"]): raise ApiError(400, "Choose a different new password.")
        password_hash = self.hash_password(password)
        async with self.db.as_actor(identity) as session:
            await session.execute(text('SELECT app_private.change_user_password(:user, :hash)'), {"user": identity.id, "hash": password_hash})
        return self.issue_user(identity.id, identity.name, identity.email, False, identity.username, password_hash)

    async def mobile_update_password(self, identity: Identity, current_password: str, password: str) -> str:
        await self.update_password(identity, current_password, password)
        token = token_urlsafe(48)
        async with self.db.sessions.begin() as session:
            await session.execute(text('SELECT app_private.create_mobile_session(:user,:hash)'), {"user": identity.id, "hash": hashlib.sha256(token.encode()).hexdigest()})
        return token

    async def update_platform_password(self, identity: Identity, current_password: str, password: str) -> str:
        async with self.db.sessions.begin() as session:
            credential = (await session.execute(text('SELECT * FROM app_private.platform_owner_credential(:username)'), {"username": identity.username})).mappings().first()
        if not credential or credential["userId"] != identity.id or not credential["active"]: raise ApiError(401, "Please sign in again.")
        if not self.check_password(current_password, credential["passwordHash"] or ""): raise ApiError(401, "Current password is incorrect.")
        if self.check_password(password, credential["passwordHash"]): raise ApiError(400, "Choose a different new password.")
        password_hash = self.hash_password(password)
        async with self.db.as_actor(identity) as session:
            await session.execute(text('SELECT app_private.change_platform_password(:owner,:hash)'), {"owner": identity.id, "hash": password_hash})
        return self.issue_platform(identity.id, identity.name, identity.username, password_hash)

    def issue_demo(self, user_id: UUID) -> str:
        if not self.demo or not any(item["id"] == str(user_id) for item in DEMO_PROFILES): raise ApiError(401, "Unauthorized")
        # Preview tokens only identify one fixed fixture account; production uses Supabase.
        payload = base64.urlsafe_b64encode(json.dumps({"sub": str(user_id), "exp": int(time() * 1000) + 3_600_000}).encode()).rstrip(b"=").decode()
        return f"{payload}.{hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()}"

    async def verify(self, token: str) -> Identity:
        if self.demo:
            try:
                payload, signature = token.split(".")
                expected = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
                if not hmac.compare_digest(signature, expected): raise ValueError()
                data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
                profile = next(item for item in DEMO_PROFILES if item["id"] == data["sub"])
                if data["exp"] <= int(time() * 1000): raise ValueError()
                return Identity(UUID(profile["id"]), profile["email"], profile["name"])
            except (ValueError, KeyError, StopIteration, json.JSONDecodeError):
                raise ApiError(401, "Please sign in again.")
        # Ask Supabase for the authenticated user rather than trusting browser claims.
        headers = {"apikey": os.environ["SUPABASE_ANON_KEY"], "Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{os.environ['SUPABASE_URL'].rstrip('/')}/auth/v1/user", headers=headers)
        data = response.json() if response.is_success else {}
        if not data.get("email") or not data.get("email_confirmed_at"): raise ApiError(401, "A verified account is required.")
        email = data["email"].lower()
        return Identity(UUID(data["id"]), email, str(data.get("user_metadata", {}).get("name") or email.split("@")[0])[:100])

async def actor(request: Request) -> Identity:
    header = request.headers.get("authorization", "")
    if header.startswith("Bearer ") and len(header) <= 8192: identity = await request.app.state.auth.verify(header[7:])
    elif request.headers.get("x-ams-client") == "mobile" and request.cookies.get(MOBILE_COOKIE): identity = await request.app.state.auth.mobile_identity(request.cookies[MOBILE_COOKIE])
    elif request.cookies.get(PLATFORM_COOKIE): identity = await request.app.state.auth.verify_platform(request.cookies[PLATFORM_COOKIE])
    elif request.cookies.get(USER_COOKIE): identity = await request.app.state.auth.verify_user(request.cookies[USER_COOKIE])
    else: raise ApiError(401, "Unauthorized")
    if identity.password_change_required and request.url.path not in {"/api/me", "/api/auth/password/change-required", "/api/auth/password/sign-out", "/api/auth/mobile/change-required", "/api/auth/mobile/sign-out"}:
        raise ApiError(403, "Change your temporary password before continuing.")
    return identity
