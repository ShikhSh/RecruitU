#!/usr/bin/env bash
set -euo pipefail
export $(grep -v '^#' .env | xargs -d '\n')
uvicorn app.main:app --reload --port 8080