"""FastAPI application for generating and storing random letters."""

import random
import string
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse

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


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home() -> str:
    """Render the existing application's browser-facing generator page."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Random Letter Generator</title>
</head>
<body>
  <main>
    <h1>Random Letter Generator</h1>
    <section aria-labelledby="random-number-heading">
      <h2 id="random-number-heading">Random Number</h2>
      <p>Generate a random integer in the inclusive range 1 through 100.</p>
      <button id="generate-number" type="button">Generate</button>
      <p id="random-number-result" aria-live="polite">No number generated yet.</p>
    </section>
  </main>
  <script>
    const button = document.getElementById("generate-number");
    const result = document.getElementById("random-number-result");

    button.addEventListener("click", async () => {
      try {
        const response = await fetch("/random-number");
        if (!response.ok) {
          throw new Error("Unable to generate a random number.");
        }
        const data = await response.json();
        result.textContent = `Generated number: ${data.value}`;
      } catch (error) {
        result.textContent = error.message;
      }
    });
  </script>
</body>
</html>"""


@app.get(
    "/random-number",
    summary="Generate a random number from 1 through 100",
    description="Returns a newly generated integer in the inclusive range 1 through 100.",
)
async def generate_random_number() -> dict[str, int]:
    """Generate a transient random integer in the inclusive range 1 through 100."""
    return {"value": random.randint(1, 100)}


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
