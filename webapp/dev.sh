#!/usr/bin/env bash
# Chế độ phát triển: FastAPI (cổng 8000, tự nạp lại) + Vite (cổng 5173, proxy /api sang 8000)
set -euo pipefail
cd "$(dirname "$0")"
(cd backend && python3 -m uvicorn app.main:app --reload --port 8000) &
trap 'kill 0' EXIT
cd frontend && npm run dev
