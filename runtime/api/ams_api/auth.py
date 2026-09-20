import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from secrets import token_bytes
from time import time
from uuid import UUID
import httpx
from fastapi import Request
from .errors import ApiError

@dataclass(frozen=True)
class Identity: id: UUID; email: str; name: str

DEMO_PROFILES = [
    {"id": "11111111-1111-4111-8111-111111111111", "name": "Aarav Mehta", "email": "admin@rally.example", "label": "Academy administrator"},
    {"id": "22222222-2222-4222-8222-222222222222", "name": "Nisha Rao", "email": "coach@rally.example", "label": "Coach · Indiranagar only"},
    {"id": "33333333-3333-4333-8333-333333333333", "name": "Dev Sharma", "email": "admin@spin.example", "label": "Second academy administrator"},
    {"id": "44444444-4444-4444-8444-444444444444", "name": "Platform owner", "email": "owner@ams.example", "label": "Academy onboarding"},
    {"id": "55555555-5555-4555-8555-555555555555", "name": "Priya Sen", "email": "priya@example.test", "label": "New invite recipient"},
]

class AuthService:
    def __init__(self) -> None:
        self.demo = os.getenv("DEV_AUTH") == "true"
        # The process-local key deliberately invalidates preview sessions after a restart.
        self.secret = token_bytes(32)
        if self.demo and os.getenv("NODE_ENV") not in ("development", "test"):
            raise RuntimeError("DEV_AUTH requires NODE_ENV=development or test.")
        if not self.demo and (not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_ANON_KEY")):
            raise RuntimeError("Supabase authentication is not configured.")

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
    if not header.startswith("Bearer ") or len(header) > 8192: raise ApiError(401, "Unauthorized")
    return await request.app.state.auth.verify(header[7:])
