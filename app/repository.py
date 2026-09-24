"""Raw-SQL data access for letters."""

from app.db import get_pool


async def insert_letter(value: str) -> dict:
    """Persist a letter and return the created row."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        record = await connection.fetchrow(
            """
            INSERT INTO letters (value)
            VALUES ($1)
            RETURNING id, value, created_at
            """,
            value,
        )
    return dict(record)


async def list_letters() -> list[dict]:
    """Return all persisted letters, newest first."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        records = await connection.fetch(
            """
            SELECT id, value, created_at
            FROM letters
            ORDER BY created_at DESC, id DESC
            """
        )
    return [dict(record) for record in records]


async def get_letter(letter_id: int) -> dict | None:
    """Return a letter by primary key, or ``None`` when absent."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        record = await connection.fetchrow(
            """
            SELECT id, value, created_at
            FROM letters
            WHERE id = $1
            """,
            letter_id,
        )
    return dict(record) if record is not None else None
