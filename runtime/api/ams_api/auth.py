import base64
import binascii
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from secrets import token_bytes
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
        payload = base64.urlsafe_b64encode(json.dumps({"kind": "platform", "sub": str(credential["userId"]), "name": credential["name"], "username": username, "exp": int(time() * 1000) + 28_800_000}).encode()).rstrip(b"=").decode()
        return f"{payload}.{hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()}"

    def verify_platform(self, token: str) -> Identity:
        try:
            payload, signature = token.split(".")
            expected = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected): raise ValueError()
            data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
            if data.get("kind") != "platform" or data["exp"] <= int(time() * 1000): raise ValueError()
            return Identity(UUID(data["sub"]), f"{data['username']}@platform.local", data["name"])
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
        return self.issue_user(credential["userId"], credential["name"], credential["email"], credential["passwordChangeRequired"], username)

    def issue_user(self, user_id: UUID, name: str, email: str, password_change_required: bool, username: str) -> str:
        payload = base64.urlsafe_b64encode(json.dumps({"kind": "user", "sub": str(user_id), "name": name, "email": email, "username": username, "change": password_change_required, "exp": int(time() * 1000) + 28_800_000}).encode()).rstrip(b"=").decode()
        return f"{payload}.{hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()}"

    def verify_user(self, token: str) -> Identity:
        try:
            payload, signature = token.split(".")
            if not hmac.compare_digest(signature, hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()): raise ValueError()
            data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
            if data.get("kind") != "user" or data["exp"] <= int(time() * 1000): raise ValueError()
            return Identity(UUID(data["sub"]), data["email"], data["name"], bool(data.get("change")), data["username"])
        except (ValueError, KeyError, json.JSONDecodeError):
            raise ApiError(401, "Please sign in again.")

    async def change_password(self, identity: Identity, password: str) -> str:
        if not identity.password_change_required: raise ApiError(403, "A password change is not required.")
        async with self.db.sessions.begin() as session:
            credential = (await session.execute(text('SELECT * FROM app_private.user_credential(:username)'), {"username": identity.username})).mappings().first()
        if not credential or self.check_password(password, credential["passwordHash"]): raise ApiError(400, "Choose a password different from the temporary password.")
        async with self.db.as_actor(identity) as session:
            await session.execute(text('SELECT app_private.change_user_password(:user, :hash)'), {"user": identity.id, "hash": self.hash_password(password)})
        return self.issue_user(identity.id, identity.name, identity.email, False, identity.username)

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
    elif request.cookies.get(PLATFORM_COOKIE): identity = request.app.state.auth.verify_platform(request.cookies[PLATFORM_COOKIE])
    elif request.cookies.get(USER_COOKIE): identity = request.app.state.auth.verify_user(request.cookies[USER_COOKIE])
    else: raise ApiError(401, "Unauthorized")
    if identity.password_change_required and request.url.path not in {"/api/me", "/api/auth/password/change-required", "/api/auth/password/sign-out"}:
        raise ApiError(403, "Change your temporary password before continuing.")
    return identity
