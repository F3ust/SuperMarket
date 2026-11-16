"""Bảng điều hành: KPI theo kỳ, so kỳ trước và cùng kỳ năm trước, xếp hạng cửa hàng, cảnh báo, bản tin tự động.

Dữ liệu demo là Walmart M5 (10 cửa hàng, 3 bang, 3 ngành, 7 nhóm hàng; 29/01/2011–22/05/2016).
Doanh thu = lượng bán × giá niêm yết tuần, nên là doanh thu ước tính trước giảm giá.
"""
from __future__ import annotations

import datetime as dt
import re

import pandas as pd

from .explorer import M5, _q

FIRST, LAST = dt.date(2011, 1, 29), dt.date(2016, 5, 22)
CAT_VI = {"FOODS": "Thực phẩm", "HOUSEHOLD": "Gia dụng", "HOBBIES": "Giải trí"}
STATE_VI = {"CA": "California", "TX": "Texas", "WI": "Wisconsin"}
DOW_VI = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"]


def _month_end(y: int, m: int) -> dt.date:
    return (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))


def _bounds(grain: str, key: str) -> tuple[dt.date, dt.date, str]:
    if grain == "year":
        y = int(key)
        return dt.date(y, 1, 1), dt.date(y, 12, 31), f"năm {y}"
    if grain == "quarter":
        y, q = int(key[:4]), int(key[-1])
        return dt.date(y, 3 * q - 2, 1), _month_end(y, 3 * q), f"quý {q}/{y}"
    y, m = int(key[:4]), int(key[5:7])
    return dt.date(y, m, 1), _month_end(y, m), f"tháng {m}/{y}"


def _shift(grain: str, key: str, back: int) -> str:
    """Kỳ cách `back` kỳ về trước (cùng loại kỳ)."""
    if grain == "year":
        return str(int(key) - back)
    if grain == "quarter":
        i = int(key[:4]) * 4 + int(key[-1]) - 1 - back
        return f"{i // 4}-Q{i % 4 + 1}"
    i = int(key[:4]) * 12 + int(key[5:7]) - 1 - back
    return f"{i // 12}-{i % 12 + 1:02d}"


def periods() -> dict:
    """Các kỳ trọn vẹn có trong dữ liệu."""
    months, quarters, years = [], [], []
    y, m = 2011, 2
    while _month_end(y, m) <= LAST:
        months.append(f"{y}-{m:02d}")
        y, m = (y + (m == 12), m % 12 + 1)
    for y in range(2011, 2017):
        for q in range(1, 5):
            s, e, _ = _bounds("quarter", f"{y}-Q{q}")
            if s >= FIRST and e <= LAST:
                quarters.append(f"{y}-Q{q}")
        if dt.date(y, 1, 1) >= FIRST and dt.date(y, 12, 31) <= LAST:
            years.append(str(y))
    return {"month": months[::-1], "quarter": quarters[::-1], "year": years[::-1], "default": {"grain": "month", "key": months[-1]}}


def _where(state: str | None, store: str | None, cat: str | None) -> tuple[str, list]:
    w, p = [], []
    for col, v in (("state", state), ("store", store), ("cat", cat)):
        if v:
            w.append(f"{col} = ?")
            p.append(v)
    return (" AND ".join(w) or "1=1"), p


def _agg(s: dt.date, e: dt.date, w: str, p: list, by: str | None = None) -> pd.DataFrame:
    g = f"{by}, " if by else ""
    return _q(f"""SELECT {g} sum(revenue) AS revenue, sum(units) AS units, count(DISTINCT date) AS "days", count(DISTINCT store) AS stores
        FROM '{M5}' WHERE {w} AND date BETWEEN ?::DATE AND ?::DATE {'GROUP BY ' + by if by else ''}""", p + [str(s), str(e)])


def _chg(a: float | None, b: float | None) -> float | None:
    return None if not a or not b else a / b - 1


def dashboard(grain: str, key: str, state: str | None, store: str | None, cat: str | None) -> dict:
    grain = grain if grain in ("month", "quarter", "year") else "month"
    s, e, label = _bounds(grain, key)
    prev_key, yoy_key = _shift(grain, key, 1), _shift(grain, key, {"month": 12, "quarter": 4, "year": 1}[grain])
    ps, pe, plabel = _bounds(grain, prev_key)
    ys, ye, ylabel = _bounds(grain, yoy_key)
    w, p = _where(state, store, cat)

    def kpi(a, b, c):
        a0, b0, c0 = (x.iloc[0] if len(x) else None for x in (a, b, c))
        out = {}
        for k in ("revenue", "units"):
            v = float(a0[k] or 0)
            out[k] = {"value": v, "prev": _chg(v, float(b0[k] or 0) if ps >= FIRST else None), "yoy": _chg(v, float(c0[k] or 0) if ys >= FIRST else None)}
        price = lambda r: float(r.revenue) / float(r.units) if r is not None and r.units else None
        out["price"] = {"value": price(a0), "prev": _chg(price(a0), price(b0)) if ps >= FIRST else None, "yoy": _chg(price(a0), price(c0)) if ys >= FIRST else None}
        rpd = lambda r: float(r.revenue) / (float(r.days) * float(r.stores)) if r is not None and r.days else None
        out["per_store_day"] = {"value": rpd(a0), "prev": _chg(rpd(a0), rpd(b0)) if ps >= FIRST else None, "yoy": _chg(rpd(a0), rpd(c0)) if ys >= FIRST else None}
        out["stores"] = int(a0.stores or 0)
        return out

    cur, prv, yoy = _agg(s, e, w, p), _agg(ps, pe, w, p), _agg(ys, ye, w, p)
    kpis = kpi(cur, prv, yoy)

    # Cửa hàng: doanh thu kỳ này, cùng kỳ, tăng trưởng
    sc, sy = _agg(s, e, w, p, "store"), _agg(ys, ye, w, p, "store")
    st = sc.merge(sy[["store", "revenue"]].rename(columns={"revenue": "rev_yoy"}), on="store", how="left")
    st["yoy"] = st.revenue / st.rev_yoy - 1 if ys >= FIRST else None
    st["share"] = st.revenue / st.revenue.sum()
    st["per_day"] = st.revenue / st.days
    st = st.sort_values("revenue", ascending=False)
    stores = [{"store": r.store, "state": r.store[:2], "revenue": float(r.revenue), "share": float(r.share), "per_day": float(r.per_day),
               "yoy": (None if pd.isna(r.yoy) else float(r.yoy))} for r in st.itertuples()]

    # Ngành và nhóm hàng
    dc, dy = _agg(s, e, w, p, "cat, dept"), _agg(ys, ye, w, p, "cat, dept")
    dd = dc.merge(dy[["dept", "revenue"]].rename(columns={"revenue": "rev_yoy"}), on="dept", how="left").sort_values("revenue", ascending=False)
    dd["yoy"] = dd.revenue / dd.rev_yoy - 1 if ys >= FIRST else None
    depts = [{"cat": r.cat, "cat_vi": CAT_VI.get(r.cat, r.cat), "dept": r.dept, "revenue": float(r.revenue), "share": float(r.revenue / dd.revenue.sum()),
              "yoy": (None if pd.isna(r.yoy) else float(r.yoy)), "delta": (None if pd.isna(r.rev_yoy) else float(r.revenue - r.rev_yoy))} for r in dd.itertuples()]

    # Xu hướng: doanh thu theo tháng, mỗi năm một đường, đến hết kỳ đang xem
    tr = _q(f"""SELECT year(date) y, month(date) m, sum(revenue) revenue FROM '{M5}' WHERE {w} AND date <= ?::DATE AND date >= DATE '2011-02-01'
        GROUP BY 1,2 ORDER BY 1,2""", p + [str(e)])
    trend = {str(y): [None] * 12 for y in sorted(tr.y.unique())}
    for r in tr.itertuples():
        if _month_end(int(r.y), int(r.m)) <= LAST:
            trend[str(r.y)][int(r.m) - 1] = float(r.revenue)

    # Ngày trong kỳ và thứ trong tuần
    daily = _q(f"""SELECT date::DATE d, sum(revenue) revenue, sum(units) units FROM '{M5}' WHERE {w} AND date BETWEEN ?::DATE AND ?::DATE GROUP BY 1 ORDER BY 1""", p + [str(s), str(e)])
    daily["wd"] = pd.to_datetime(daily.d).dt.dayofweek.map(lambda x: (x + 1) % 7)
    daily = daily[daily.units > 0]
    wd = daily.groupby("wd").revenue.mean().reindex(range(7))
    weekday = [{"wd": DOW_VI[i], "revenue": (None if pd.isna(v) else float(v))} for i, v in wd.items()]
    weekend_share = float(daily[daily.wd.isin([0, 6])].revenue.sum() / daily.revenue.sum()) if len(daily) else None

    # Cảnh báo: cửa hàng và nhóm hàng giảm so với cùng kỳ; ngày bất thường
    alerts = []
    for r in stores:
        if r["yoy"] is not None and r["yoy"] < -0.03:
            alerts.append({"level": "high" if r["yoy"] < -0.1 else "medium", "kind": "Cửa hàng", "title": _vn(f"{r['store']} giảm {abs(r['yoy']) * 100:.1f}% so với cùng kỳ"),
                           "body": _vn(f"Doanh thu {label}: {_money(r['revenue'])}. Kiểm tra cơ cấu ngành, giá và tồn kho của cửa hàng này.")})
    for r in depts:
        if r["yoy"] is not None and r["yoy"] < -0.05:
            alerts.append({"level": "medium", "kind": "Nhóm hàng", "title": _vn(f"{r['dept']} giảm {abs(r['yoy']) * 100:.1f}% so với cùng kỳ"),
                           "body": _vn(f"{r['cat_vi']}, chiếm {r['share'] * 100:.1f}% doanh thu kỳ. Xem độ co giãn giá và lịch khuyến mãi của nhóm.")})
    if len(daily) >= 20:
        med = daily.revenue.median()
        low = daily[daily.revenue < 0.4 * med]
        for r in low.itertuples():
            alerts.append({"level": "info", "kind": "Ngày bất thường", "title": f"{pd.Timestamp(r.d):%d/%m/%Y}: " + ("gần như không có doanh thu" if r.revenue < 0.02 * med else f"doanh thu chỉ bằng {r.revenue / med * 100:.0f}% ngày thường"),
                           "body": "Thường là ngày lễ hoặc cửa hàng đóng cửa. Loại khỏi dữ liệu huấn luyện dự báo hoặc gắn cờ ngày lễ."})
    alerts = sorted(alerts, key=lambda a: {"high": 0, "medium": 1, "info": 2}[a["level"]])[:8]

    # Bản tin tự động
    news = []
    k = kpis["revenue"]
    if k["yoy"] is not None:
        news.append(f"Doanh thu {label} đạt {k['value'] / 1e6:.2f} triệu USD, {'tăng' if k['yoy'] >= 0 else 'giảm'} {abs(k['yoy']) * 100:.1f}% so với {ylabel}.")
    if kpis["units"]["yoy"] is not None and kpis["price"]["yoy"] is not None:
        news.append(f"Lượng bán {'tăng' if kpis['units']['yoy'] >= 0 else 'giảm'} {abs(kpis['units']['yoy']) * 100:.1f}%, giá bình quân mỗi đơn vị "
                    f"{'tăng' if kpis['price']['yoy'] >= 0 else 'giảm'} {abs(kpis['price']['yoy']) * 100:.1f}%: tăng trưởng đến chủ yếu từ "
                    f"{'lượng' if abs(kpis['units']['yoy']) >= abs(kpis['price']['yoy']) else 'giá và cơ cấu hàng'}.")
    contrib = [d for d in depts if d["delta"] is not None]
    if contrib and k["yoy"] is not None:
        top = max(contrib, key=lambda d: d["delta"])
        bot = min(contrib, key=lambda d: d["delta"])
        tot = sum(d["delta"] for d in contrib)
        if tot and top["delta"] > 0:
            news.append(f"Nhóm {top['dept']} ({top['cat_vi']}) đóng góp nhiều nhất vào thay đổi so với cùng kỳ: +{_money(top['delta'])}.")
        if bot["delta"] < 0:
            news.append(f"Nhóm {bot['dept']} kéo giảm {_money(abs(bot['delta']))}.")
    if stores and stores[0]["yoy"] is not None:
        best = max((x for x in stores if x["yoy"] is not None), key=lambda x: x["yoy"])
        worst = min((x for x in stores if x["yoy"] is not None), key=lambda x: x["yoy"])
        if best["store"] != worst["store"]:
            news.append(f"Cửa hàng tăng mạnh nhất là {best['store']} ({best['yoy'] * 100:+.1f}%), yếu nhất là {worst['store']} ({worst['yoy'] * 100:+.1f}%).")
    if weekend_share is not None:
        news.append(f"Thứ Bảy và Chủ nhật chiếm {weekend_share * 100:.0f}% doanh thu (2/7 = 29% số ngày): xếp ca và bổ sung hàng nên dồn vào cuối tuần.")
    news = [_vn(n) for n in news]

    return {"period": {"grain": grain, "key": key, "label": label, "start": str(s), "end": str(e), "prev_label": plabel, "yoy_label": ylabel},
            "kpis": kpis, "stores": stores, "depts": depts, "trend": trend, "weekday": weekday, "weekend_share": weekend_share,
            "daily": [{"d": str(r.d)[:10], "revenue": float(r.revenue)} for r in daily.itertuples()], "alerts": alerts, "news": news}


def _money(v: float) -> str:
    return f"{v / 1e6:.2f} triệu USD" if abs(v) >= 1e6 else f"{v / 1e3:.0f} nghìn USD"


def _vn(s: str) -> str:
    """Đổi dấu thập phân sang kiểu Việt trong các số dạng 1.23 / +4.5 (không đụng dấu chấm cuối câu)."""
    return re.sub(r"(?<=\d)\.(?=\d)", ",", s)
