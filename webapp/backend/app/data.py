"""Nạp dữ liệu đã đóng gói một lần khi khởi động."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .config import DATA_DIR


def _load(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


@lru_cache
def content() -> dict:
    return _load("content.json")


@lru_cache
def chart_data() -> dict:
    return _load("chart_data.json")


@lru_cache
def results() -> dict:
    return _load("results.json")


@lru_cache
def results_deep() -> dict:
    return _load("results_deep.json")


def parquet(name: str) -> Path:
    return DATA_DIR / name
