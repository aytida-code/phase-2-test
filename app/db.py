"""asyncpg connection-pool lifecycle helpers."""

import asyncpg

from app.config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def init_pool() -> asyncpg.Pool:
    """Create the shared pool and ensure the application's table exists."""
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
        async with _pool.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS letters (
                    id SERIAL PRIMARY KEY,
                    value CHAR(1) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
    return _pool


async def close_pool() -> None:
    """Close and clear the shared pool, if it has been initialized."""
    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_pool() -> asyncpg.Pool:
    """Return the initialized pool."""
    if _pool is None:
        raise RuntimeError("Database pool has not been initialized")
    return _pool
