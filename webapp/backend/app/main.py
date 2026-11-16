"""Retail Intelligence API — phân tích bán lẻ đa nguồn.

Chạy phát triển:  uvicorn app.main:app --reload --port 8000  (trong webapp/backend)
Tài liệu API:     http://localhost:8000/docs
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, dashboard, explorer, simulate
from .data import chart_data, content

app = FastAPI(title="Retail Intelligence API", version="1.1.0",
              description="API cho bản demo nền tảng phân tích kinh doanh siêu thị: bảng điều hành, phân hệ phân tích, mô phỏng giá/khuyến mãi, tra cứu dữ liệu.",
              docs_url="/docs" if config.ENABLE_DOCS else None, redoc_url=None, openapi_url="/openapi.json" if config.ENABLE_DOCS else None)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])


# ---------------------------------------------------------------- nội dung
@app.get("/api/health", tags=["hệ thống"])
def health():
    return {"status": "ok", "env": config.APP_ENV, "sections": len(content()["sections"])}


@app.get("/api/meta", tags=["nội dung"], summary="KPI, nguồn dữ liệu, ma trận trường, chất lượng, dòng thời gian")
def meta():
    return content()["meta"]


@app.get("/api/sections", tags=["nội dung"], summary="Danh sách chương")
def sections():
    return [{"id": s["id"], "eyebrow": s["eyebrow"], "title": s["title"]} for s in content()["sections"]]


@app.get("/api/sections/{section_id}", tags=["nội dung"], summary="Nội dung một chương")
def section(section_id: str):
    for s in content()["sections"]:
        if s["id"] == section_id:
            return s
    raise HTTPException(404, f"Không có chương '{section_id}'")


@app.get("/api/charts", tags=["nội dung"], summary="Dữ liệu cho toàn bộ biểu đồ")
def charts():
    return chart_data()


# ---------------------------------------------------------------- bảng điều hành
@app.get("/api/dashboard/periods", tags=["bảng điều hành"], summary="Các kỳ tháng/quý/năm trọn vẹn có dữ liệu")
def dash_periods():
    return dashboard.periods()


@app.get("/api/dashboard", tags=["bảng điều hành"], summary="KPI, so kỳ, xếp hạng cửa hàng, nhóm hàng, cảnh báo và bản tin cho một kỳ")
def dash(grain: Literal["month", "quarter", "year"] = "month", key: str = "2016-04", state: str | None = None,
         store: str | None = None, cat: str | None = None):
    if key not in dashboard.periods()[grain]:
        raise HTTPException(422, f"Kỳ '{key}' không có đủ dữ liệu")
    return dashboard.dashboard(grain, key, state, store, cat)


# ---------------------------------------------------------------- mô phỏng
class PromoIn(BaseModel):
    category: str = Field("COLD CEREAL", description="Ngành BATF")
    margin: float = Field(0.3, ge=0.05, le=0.8, description="Biên gộp hiện tại")
    cut: float = Field(0.1, ge=0, le=0.4, description="Mức giảm giá")
    display: bool = True
    feature: bool = False
    rival_share: float = Field(0.0, ge=0, le=1, description="Tỷ lệ SKU khác cùng ngành đang khuyến mãi")
    include_post: bool = Field(True, description="Tính hiệu ứng 2 tuần sau khuyến mãi")


class PriceIn(BaseModel):
    source: Literal["batf", "carbo", "m5"] = "batf"
    category: str = "FROZEN PIZZA"
    change: float = Field(0.05, ge=-0.5, le=0.5, description="Thay đổi giá, ví dụ 0.05 = +5%")


@app.get("/api/simulate/options", tags=["mô phỏng"])
def sim_options():
    return {"promotion": simulate.categories(), "price": simulate.price_options()}


@app.post("/api/simulate/promotion", tags=["mô phỏng"], summary="Lợi nhuận của một đợt khuyến mãi")
def sim_promotion(body: PromoIn):
    try:
        return simulate.promotion(**body.model_dump())
    except KeyError as e:
        raise HTTPException(422, f"Ngành không hợp lệ: {e}")


@app.post("/api/simulate/price", tags=["mô phỏng"], summary="Tác động của thay đổi giá lên lượng bán và doanh thu")
def sim_price(body: PriceIn):
    try:
        return simulate.price(body.source, body.category, body.change)
    except KeyError as e:
        raise HTTPException(422, f"Nguồn/ngành không hợp lệ: {e}")


# ---------------------------------------------------------------- khám phá
@app.get("/api/explorer/m5/options", tags=["khám phá"])
def m5_options():
    return explorer.m5_options()


@app.get("/api/explorer/m5", tags=["khám phá"], summary="Chuỗi lượng bán/doanh thu Walmart M5 theo bộ lọc")
def m5(state: str | None = None, store: str | None = None, cat: str | None = None, dept: str | None = None,
       freq: Literal["day", "week", "month"] = "week", start: str | None = None, end: str | None = None):
    return explorer.m5_series(state, store, cat, dept, freq, start, end)


@app.get("/api/explorer/cj/options", tags=["khám phá"])
def cj_options():
    return explorer.cj_options()


@app.get("/api/explorer/cj", tags=["khám phá"], summary="Doanh thu tuần Complete Journey theo ngành")
def cj(department: list[str] = Query(default=[])):
    return explorer.cj_series(department)


# ---------------------------------------------------------------- frontend đã build
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if config.SERVE_FRONTEND and DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        f = DIST / path
        if path and f.is_file():
            return FileResponse(f)
        return FileResponse(DIST / "index.html")
