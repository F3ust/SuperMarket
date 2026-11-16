"""Cấu hình theo môi trường, đọc từ biến môi trường (Vercel: Project → Settings → Environment Variables).

APP_ENV          development | preview | production   (mặc định development)
CORS_ORIGINS     danh sách origin, cách nhau dấu phẩy  (mặc định Vite dev :5173; production cùng domain nên để trống)
ENABLE_DOCS      1/0 bật /docs và /openapi.json        (mặc định: bật trừ production)
DATA_DIR         thư mục dữ liệu đã đóng gói          (mặc định backend/data)
SERVE_FRONTEND   1/0 FastAPI phục vụ frontend/dist     (mặc định 1; trên Vercel tắt vì CDN phục vụ)
"""
from __future__ import annotations

import os
from pathlib import Path


_BACKEND = Path(__file__).resolve().parents[1]


def _load_env_files() -> None:
    """Nạp backend/.env.local rồi backend/.env.<APP_ENV>. Biến đã có trong môi trường (Vercel Dashboard, shell) luôn được ưu tiên."""
    env = os.getenv("APP_ENV") or os.getenv("VERCEL_ENV") or "development"
    for name in (".env.local", f".env.{env}"):
        f = _BACKEND / name
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env_files()


def _flag(name: str, default: bool) -> bool:
    v = os.getenv(name)
    return default if v is None or v == "" else v.strip().lower() in ("1", "true", "yes", "on")


APP_ENV = os.getenv("APP_ENV") or os.getenv("VERCEL_ENV") or "development"
IS_PROD = APP_ENV == "production"
ON_VERCEL = bool(os.getenv("VERCEL"))
_cors = os.getenv("CORS_ORIGINS")
CORS_ORIGINS = [o.strip() for o in (_cors if _cors is not None else ("" if IS_PROD else "http://localhost:5173,http://127.0.0.1:5173")).split(",") if o.strip()]
ENABLE_DOCS = _flag("ENABLE_DOCS", not IS_PROD)
DATA_DIR = Path(os.getenv("DATA_DIR") or _BACKEND / "data")
SERVE_FRONTEND = _flag("SERVE_FRONTEND", not ON_VERCEL)
