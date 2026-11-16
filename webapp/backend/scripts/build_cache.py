"""Đóng gói dữ liệu cho backend.

1. Sao chép kết quả phân tích (results.json, results_deep.json).
2. Trích nội dung chữ đã kiểm (tiêu đề, đoạn dẫn, Góc dữ liệu, Góc kinh tế) từ trang HTML phân tích → content.json.
3. Tạo bảng tổng hợp cho trang Khám phá dữ liệu:
   - m5_store_dept_daily.parquet: lượng bán & doanh thu theo ngày × cửa hàng × ngành (từ M5 gốc)
   - cj_dept_weekly.parquet: doanh thu, giỏ, hộ, giảm giá theo tuần × ngành (từ Complete Journey gốc)

Chạy từ thư mục gốc SieuThi:  python3 webapp/backend/scripts/build_cache.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
MS = ROOT / "outputs" / "multisource"
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "research" / "multisource"))


def copy_results():
    for f in ["results.json", "results_deep.json"]:
        shutil.copy2(MS / f, OUT / f)


def text(el):
    return " ".join(el.get_text(" ", strip=True).split()) if el else None


def build_content():
    import build_html as H  # dựng lại trang và lấy hằng số nguồn/trường/chất lượng

    soup = BeautifulSoup((MS / "Phan_tich_da_nguon.html").read_text(encoding="utf-8"), "html.parser")
    sections = []
    for sec in soup.select("section.ch"):
        head = sec.select_one(".ch-head")
        s = {"id": sec["id"], "eyebrow": text(head.select_one(".eyebrow")), "title": text(head.select_one("h2")),
             "lead": text(head.select_one("p")), "callout": text(sec.select_one(".callout")), "findings": [], "cards": [], "actions": []}
        for f in sec.select(".finding"):
            panels = f.select(".panel")
            charts = []
            for pnl in panels:
                ch = pnl.select_one(".chart")
                if ch is None:
                    continue
                charts.append({"chart": ch["id"], "title": text(pnl.select_one("h3")), "sub": text(pnl.select_one(".sub")),
                               "controls": [b.get("data-k") or b.get("data-s") or b.get("data-m") or b.get("data-c") for b in pnl.select(".seg-toggle button")]})
            lens = {}
            for kind in ("d", "e"):
                box = f.select_one(f".lens .{kind}")
                if box:
                    big = box.select_one(".big")
                    lens[kind] = {"big": text(big), "paragraphs": [text(p_) for p_ in box.select("p")]}
            if charts:
                s["findings"].append({"charts": charts, "data": lens.get("d"), "econ": lens.get("e")})
        for a in sec.select(".synth article"):
            s["cards"].append({"sources": [c.get_text(strip=True) for c in a.select(".chip")], "title": text(a.select_one("h3")), "body": text(a.select_one("p"))})
        for li in sec.select("ol.actions li"):
            s["actions"].append({"title": text(li.select_one("h3")), "body": text(li.select_one("p"))})
        sections.append(s)

    meta = {
        "kpis": {"total_rows": H.TOTAL_ROWS, "sources": 5, "period": "2006–2016",
                 "stores": H.CJ["profile"]["stores"] + H.BA["profile"]["stores"] + H.CL["profile"]["stores"] + H.LG["profile"]["stores"] + H.M5["profile"]["stores"],
                 "field_groups": len(H.FIELDS)},
        "sources": [{"key": k, "name": t, "sub": sub, "desc": desc, "grain": grain, "answers": ans} for k, t, sub, desc, grain, ans in H.SOURCES],
        "fields": [{"field": f, "have": have, "note": note} for f, have, note in H.FIELDS],
        "quality": [{"source": s_, "limit": a, "evidence": b, "handling": c} for s_, a, b, c in H.QUALITY],
        "timeline": H.DATA["timeline"],
    }
    (OUT / "content.json").write_text(json.dumps({"meta": meta, "sections": sections}, ensure_ascii=False, indent=1), encoding="utf-8")
    # dữ liệu biểu đồ: D (chính) và D2 (chuyên sâu) đúng như trang HTML dùng
    import html_extra  # noqa: F401
    import re
    html = (MS / "Phan_tich_da_nguon.html").read_text(encoding="utf-8")
    d = re.search(r"const D = (\{.*?\});\n</script>", html, re.S).group(1)
    d2 = re.search(r"const D2 = (\{.*?\});\n", html, re.S).group(1)
    (OUT / "chart_data.json").write_text(json.dumps({"D": json.loads(d), "D2": json.loads(d2)}, ensure_ascii=False), encoding="utf-8")
    print("sections:", [s["id"] for s in sections], "charts:", sum(len(f["charts"]) for s in sections for f in s["findings"]))


def build_explorer():
    con = duckdb.connect()
    m5 = ROOT / "data" / "raw_m5"
    if (m5 / "sales_train_evaluation.csv").exists():
        cal = pd.read_csv(m5 / "calendar.csv", parse_dates=["date"])
        sales = pd.read_csv(m5 / "sales_train_evaluation.csv")
        ids = sales.iloc[:, :6]
        dcols = [c for c in sales.columns if c.startswith("d_")]
        S = sales[dcols].to_numpy(np.float32)
        cal = cal[cal.d.isin(dcols)].reset_index(drop=True)
        prices = pd.read_csv(m5 / "sell_prices.csv")
        pidx = pd.MultiIndex.from_arrays([ids.store_id, ids.item_id])
        wk_u = np.unique(cal.wm_yr_wk.values)
        P = prices.set_index(["store_id", "item_id", "wm_yr_wk"]).sell_price.unstack("wm_yr_wk").reindex(pidx).reindex(columns=wk_u).fillna(0).values
        Pd = P[:, np.searchsorted(wk_u, cal.wm_yr_wk.values)]
        R = S * Pd
        rows = []
        for (store, dept), g in ids.groupby(["store_id", "dept_id"]).groups.items():
            ix = np.asarray(list(g))
            rows.append(pd.DataFrame({"date": cal.date.values, "store": store, "state": store[:2], "dept": dept, "cat": dept.rsplit("_", 1)[0],
                                      "units": S[ix].sum(0), "revenue": R[ix].sum(0), "zero_share": (S[ix] == 0).mean(0)}))
        df = pd.concat(rows, ignore_index=True)
        flags = cal[["date", "event_name_1", "event_type_1", "snap_CA", "snap_TX", "snap_WI"]]
        df.to_parquet(OUT / "m5_store_dept_daily.parquet", index=False)
        flags.to_parquet(OUT / "m5_calendar.parquet", index=False)
        print("m5 rows", len(df))
    cj = ROOT / "data" / "raw_dunnhumby" / "dunnhumby_The-Complete-Journey" / "dunnhumby_The-Complete-Journey CSV"
    if (cj / "transaction_data.csv").exists():
        con.execute(f"""COPY (SELECT WEEK_NO AS week, coalesce(p.DEPARTMENT,'(không khớp)') AS department,
            sum(SALES_VALUE) AS sales, count(DISTINCT BASKET_ID) AS baskets, count(DISTINCT household_key) AS households,
            -sum(RETAIL_DISC+COUPON_DISC+COUPON_MATCH_DISC) AS discount,
            sum(CASE WHEN p.BRAND='Private' THEN SALES_VALUE ELSE 0 END) AS private_sales
            FROM read_csv('{cj}/transaction_data.csv', header=true) t
            LEFT JOIN read_csv('{cj}/product.csv', header=true, all_varchar=true) p ON t.PRODUCT_ID::VARCHAR = p.PRODUCT_ID
            GROUP BY ALL) TO '{OUT}/cj_dept_weekly.parquet' (FORMAT parquet)""")
        print("cj ok")


if __name__ == "__main__":
    copy_results()
    build_content()
    build_explorer()
