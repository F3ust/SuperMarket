"""Truy vấn bảng tổng hợp bằng duckdb cho trang Khám phá dữ liệu."""
from __future__ import annotations

import os
import threading

import duckdb

from .data import parquet

_lock = threading.Lock()
# Serverless (Vercel) chỉ ghi được /tmp; duckdb cần thư mục home cho cấu hình nội bộ.
_con = duckdb.connect(config={"home_directory": "/tmp"} if os.getenv("VERCEL") else {})
M5 = str(parquet("m5_store_dept_daily.parquet"))
CAL = str(parquet("m5_calendar.parquet"))
CJ = str(parquet("cj_dept_weekly.parquet"))
FREQ = {"day": "day", "week": "week", "month": "month"}


def _q(sql: str, params: list | None = None):
    with _lock:
        return _con.execute(sql, params or []).df()


def m5_options() -> dict:
    d = _q(f"SELECT DISTINCT state, store, cat, dept FROM '{M5}' ORDER BY 1,2,3,4")
    return {"states": sorted(d.state.unique().tolist()), "stores": sorted(d.store.unique().tolist()),
            "cats": sorted(d.cat.unique().tolist()), "depts": sorted(d.dept.unique().tolist()), "min_date": "2011-01-29", "max_date": "2016-05-22"}


def m5_series(state: str | None, store: str | None, cat: str | None, dept: str | None, freq: str, start: str | None, end: str | None) -> dict:
    where, params = ["1=1"], []
    for col, v in (("state", state), ("store", store), ("cat", cat), ("dept", dept)):
        if v:
            where.append(f"{col} = ?")
            params.append(v)
    if start:
        where.append("date >= ?::DATE")
        params.append(start)
    if end:
        where.append("date <= ?::DATE")
        params.append(end)
    f = FREQ.get(freq, "week")
    w = " AND ".join(where)
    df = _q(f"""SELECT date_trunc('{f}', date)::DATE AS period, sum(units) AS units, sum(revenue) AS revenue
        FROM '{M5}' WHERE {w} GROUP BY 1 ORDER BY 1""", params)
    df = df[df.units > 0] if f == "day" else df
    summary = _q(f"""SELECT sum(units) units, sum(revenue) revenue, avg(zero_share) zero_share, count(DISTINCT store) stores,
        count(DISTINCT dept) depts FROM '{M5}' WHERE {w}""", params).iloc[0]
    snap_state = state or (store[:2] if store else None)
    snap = None
    if snap_state and f == "day":
        s = _q(f"""WITH d AS (SELECT date, sum(units) u FROM '{M5}' WHERE {w} GROUP BY 1),
            j AS (SELECT d.*, c.snap_{snap_state} snap, strftime(d.date, '%Y-%m') ym, dayofweek(d.date) wd FROM d JOIN '{CAL}' c USING(date) WHERE u > 0)
            SELECT avg(CASE WHEN snap=1 THEN u END)/avg(CASE WHEN snap=0 THEN u END) - 1 AS raw_lift FROM j""", params).iloc[0]
        snap = {"state": snap_state, "raw_lift": float(s.raw_lift)}
    top = _q(f"""SELECT dept, sum(revenue) revenue, sum(units) units FROM '{M5}' WHERE {w} GROUP BY 1 ORDER BY revenue DESC""", params)
    wd = _q(f"""SELECT dayofweek(date) AS wd, avg(u) AS units FROM (SELECT date, sum(units) u FROM '{M5}' WHERE {w} GROUP BY 1) WHERE u > 0 GROUP BY 1 ORDER BY 1""", params)
    return {"series": [{"period": str(r.period), "units": float(r.units), "revenue": float(r.revenue)} for r in df.itertuples()],
            "summary": {k: (float(summary[k]) if summary[k] is not None else None) for k in summary.index},
            "by_dept": top.to_dict("records"), "weekday": wd.to_dict("records"), "snap": snap}


def cj_options() -> dict:
    d = _q(f"SELECT department, sum(sales) s FROM '{CJ}' GROUP BY 1 ORDER BY s DESC")
    return {"departments": d.department.tolist()}


def cj_series(departments: list[str]) -> dict:
    params: list = []
    where = "1=1"
    if departments:
        where = f"department IN ({','.join('?' for _ in departments)})"
        params = list(departments)
    df = _q(f"""SELECT week, sum(sales) sales, sum(baskets) baskets, sum(discount) discount, sum(private_sales) private_sales
        FROM '{CJ}' WHERE {where} GROUP BY 1 ORDER BY 1""", params)
    df["disc_rate"] = df.discount / df.sales
    df["private_share"] = df.private_sales / df.sales
    mix = _q(f"""SELECT department, sum(sales) sales, sum(private_sales)/sum(sales) private_share, sum(discount)/sum(sales) disc_rate
        FROM '{CJ}' WHERE {where} GROUP BY 1 ORDER BY sales DESC LIMIT 15""", params)
    first, last = df[df.week.between(9, 32)].sales.sum(), df[df.week.between(79, 102)].sales.sum()
    return {"series": df.to_dict("records"), "mix": mix.to_dict("records"),
            "summary": {"sales": float(df.sales.sum()), "disc_rate": float(df.discount.sum() / df.sales.sum()),
                        "private_share": float(df.private_sales.sum() / df.sales.sum()), "growth_first_last_24w": float(last / first - 1) if first else None}}
