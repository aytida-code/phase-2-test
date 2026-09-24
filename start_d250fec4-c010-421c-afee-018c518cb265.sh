#!/bin/sh
set -eu

PORT="${PORT:-8010}"
exec python -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT"
