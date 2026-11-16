"""Điểm vào serverless của Vercel: Vercel nhận biến ASGI `app` và chạy FastAPI.

Mọi request /api/*, /docs, /openapi.json được rewrite về hàm này (xem vercel.json);
FastAPI vẫn thấy đường dẫn gốc nên dùng chung router với bản chạy local.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app  # noqa: E402,F401
