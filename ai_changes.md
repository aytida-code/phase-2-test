COMMIT_MESSAGE: Add transient random number generator

# Change Summary

Added a public `GET /random-number` FastAPI endpoint that returns a newly generated transient integer as `{"value": <integer>}`. The value is generated independently for each request and is in the inclusive range 1 through 100.

Added the smallest browser-facing page at `/` because the existing application had no templates, static files, or browser page to extend. The page provides visible range guidance, a **Generate** button, a live result area, and client-side `fetch('/random-number')` behavior that updates the result without a page reload.

# Preserved Behavior

- Kept the exported `app` object and FastAPI lifespan unchanged.
- Kept `POST /letters/generate`, `GET /letters`, and `GET /letters/{letter_id}` unchanged.
- Added no authentication, persistence, database model, messaging, environment configuration, or infrastructure for the random-number feature.

# Verification

- Installed only the repository-pinned application dependencies in the verification environment.
- Ran `python -m compileall app` successfully.
- Imported `app.main` successfully.
- Booted the unchanged FastAPI application on safe port 8010 against a temporary PostgreSQL instance used only for verification.
- Verified live `GET /random-number` returned HTTP 200 JSON with exactly an integer `value` in the range 1–100.
- Verified the browser page includes the Generate control, result area, inclusive-range text, click handler, and in-page fetch call.
- Verified the pre-existing `GET /letters` route still returned HTTP 200 with a JSON list.
