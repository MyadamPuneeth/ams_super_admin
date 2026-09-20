import os
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url: raise RuntimeError("DATABASE_URL is required.")
    # Configuration uses the standard PostgreSQL URL; SQLAlchemy needs its async driver prefix.
    return url.replace("postgresql://", "postgresql+asyncpg://", 1)

class Database:
    def __init__(self) -> None:
        self.engine = create_async_engine(database_url(), pool_pre_ping=True)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    async def verify_runtime_role(self) -> None:
        async with self.sessions() as session:
            row = (await session.execute(text("SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"))).mappings().first()
            # A migration owner can bypass RLS, so fail fast if it reaches request handling.
            if not row or row["current_user"] != "ams_app" or row["rolsuper"] or row["rolbypassrls"]:
                raise RuntimeError("DATABASE_URL must use the restricted ams_app role, not the migration owner.")

    @asynccontextmanager
    async def as_actor(self, actor, academy_id=None):
        async with self.sessions.begin() as session:
            # `true` makes each setting transaction-local, preventing pooled connections
            # from carrying one actor's tenant context into a later request.
            await session.execute(text("SELECT set_config('app.actor', :actor, true), set_config('app.email', :email, true), set_config('app.academy', :academy, true)"), {"actor": str(actor.id), "email": actor.email.lower(), "academy": str(academy_id or "")})
            yield session

    async def close(self) -> None: await self.engine.dispose()
