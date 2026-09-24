"""FastAPI application for generating and storing random letters."""

import random
import string
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from app import db, repository, schemas


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize and dispose of the database pool with the application."""
    await db.init_pool()
    try:
        yield
    finally:
        await db.close_pool()


app = FastAPI(title="Random Letter Generator", lifespan=lifespan)


@app.post(
    "/letters/generate",
    response_model=schemas.LetterOut,
    status_code=status.HTTP_201_CREATED,
)
async def generate_letter() -> dict:
    """Generate one uppercase English letter and persist it."""
    value = random.choice(string.ascii_uppercase)
    return await repository.insert_letter(value)


@app.get("/letters", response_model=list[schemas.LetterOut])
async def get_letters() -> list[dict]:
    """List generated letters with the newest record first."""
    return await repository.list_letters()


@app.get("/letters/{letter_id}", response_model=schemas.LetterOut)
async def get_letter(letter_id: int) -> dict:
    """Fetch a single generated letter."""
    letter = await repository.get_letter(letter_id)
    if letter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Letter not found")
    return letter
