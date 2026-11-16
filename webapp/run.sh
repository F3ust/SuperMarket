#!/usr/bin/env bash
# Chạy bản production: build frontend (nếu chưa có) rồi FastAPI phục vụ cả API lẫn giao diện ở http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")"
[ -d frontend/node_modules ] || (cd frontend && npm install --no-audit --no-fund)
[ -d frontend/dist ] || (cd frontend && npm run build)
cd backend && exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
