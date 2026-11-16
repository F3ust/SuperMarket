"""Hồ sơ dữ liệu (data profiling) cho toàn bộ nguồn thô của dự án.

Đọc trực tiếp data/raw*, tính quy mô, phạm vi thời gian, khóa, giá trị thiếu, trùng lặp,
giá trị bất thường và độ khớp khóa giữa các bảng. Ghi outputs/data_report/profile.json.

Chạy: python3 research/data_report/profile_data.py   (khoảng 3–6 phút, cần duckdb, pandas, openpyxl)
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data"
OUT = ROOT / "outputs" / "data_report"
OUT.mkdir(parents=True, exist_ok=True)
CJ = D / "raw_dunnhumby/dunnhumby_The-Complete-Journey/dunnhumby_The-Complete-Journey CSV"
CARBO = D / "raw_dunnhumby/dunnhumby_Carbo-Loading/dunnhumby - Carbo-Loading CSV"
LGSR = D / "raw_dunnhumby/dunnhumby_Let's-Get-Sort-of-Real-(Sample-5K-customers)"
M5 = D / "raw_m5"
BATF_CACHE = ROOT / "outputs/multisource/_cache"

con = duckdb.connect()
con.execute("SET threads TO 8")
P: dict = {"generated": time.strftime("%Y-%m-%d %H:%M"), "sources": {}}


def q(sql: str):
    return con.execute(sql).fetchall()


def one(sql: str):
    rows = con.execute(sql).fetchall()  # đọc hết kết quả: duckdb 2.x không cho chạy lệnh mới khi kết quả cũ còn dở
    r = rows[0] if rows else None
    return r[0] if r and len(r) == 1 else r


def csv(path: Path, **kw) -> str:
    p = str(path).replace("'", "''")
    opts = ", ".join(f"{k}={v}" for k, v in kw.items())
    return f"read_csv_auto('{p}', sample_size=-1{', ' + opts if opts else ''})"


def table_profile(src: str, name: str, file_desc: str, mb: float) -> dict:
    """Quy mô + giá trị thiếu và số giá trị khác nhau theo cột."""
    cols = q(f"DESCRIBE SELECT * FROM {src}")
    n = one(f"SELECT count(*) FROM {src}")
    exprs = ", ".join(f'count(*) - count("{c[0]}"), approx_count_distinct("{c[0]}")' for c in cols)
    r = con.execute(f"SELECT {exprs} FROM {src}").fetchall()[0]
    out = []
    for i, c in enumerate(cols):
        out.append({"name": c[0], "type": c[1], "nulls": int(r[2 * i]), "null_pct": (r[2 * i] / n if n else 0), "distinct": int(r[2 * i + 1])})
    print(f"  {name}: {n:,} dòng, {len(cols)} cột")
    return {"name": name, "file": file_desc, "mb": round(mb, 1), "rows": int(n), "cols": out}


def size_mb(paths) -> float:
    return sum(os.path.getsize(p) for p in paths) / 1e6


def log(s):
    print(time.strftime("%H:%M:%S"), s, flush=True)


# ------------------------------------------------------------------ Complete Journey (bản gốc dunnhumby)
def complete_journey():
    log("Complete Journey")
    t = {}
    for f, name in [("transaction_data.csv", "transaction_data"), ("causal_data.csv", "causal_data"), ("product.csv", "product"),
                    ("hh_demographic.csv", "hh_demographic"), ("campaign_table.csv", "campaign_table"), ("campaign_desc.csv", "campaign_desc"),
                    ("coupon.csv", "coupon"), ("coupon_redempt.csv", "coupon_redempt")]:
        t[name] = table_profile(csv(CJ / f), name, f, size_mb([CJ / f]))
    tx = csv(CJ / "transaction_data.csv")
    con.execute(f"CREATE OR REPLACE TEMP TABLE cj AS SELECT * FROM {tx}")
    chk = {
        "households": one("SELECT count(DISTINCT household_key) FROM cj"),
        "baskets": one("SELECT count(DISTINCT BASKET_ID) FROM cj"),
        "products": one("SELECT count(DISTINCT PRODUCT_ID) FROM cj"),
        "stores": one("SELECT count(DISTINCT STORE_ID) FROM cj"),
        "day_min": one("SELECT min(DAY) FROM cj"), "day_max": one("SELECT max(DAY) FROM cj"),
        "week_min": one("SELECT min(WEEK_NO) FROM cj"), "week_max": one("SELECT max(WEEK_NO) FROM cj"),
        "sales_total": one("SELECT sum(SALES_VALUE) FROM cj"),
        "sales_le0": one("SELECT count(*) FROM cj WHERE SALES_VALUE <= 0"),
        "sales_eq0": one("SELECT count(*) FROM cj WHERE SALES_VALUE = 0"),
        "qty_eq0": one("SELECT count(*) FROM cj WHERE QUANTITY = 0"),
        "qty_gt1000": one("SELECT count(*) FROM cj WHERE QUANTITY > 1000"),
        "retail_disc_pos": one("SELECT count(*) FROM cj WHERE RETAIL_DISC > 0"),
        "coupon_disc_pos": one("SELECT count(*) FROM cj WHERE COUPON_DISC > 0"),
        "disc_total": one("SELECT -sum(RETAIL_DISC + COUPON_DISC + COUPON_MATCH_DISC) FROM cj"),
        "dup_rows": one("SELECT count(*) - count(*) FILTER (WHERE rn = 1) FROM (SELECT row_number() OVER (PARTITION BY household_key, BASKET_ID, DAY, PRODUCT_ID, QUANTITY, SALES_VALUE, STORE_ID, RETAIL_DISC, TRANS_TIME, COUPON_DISC, COUPON_MATCH_DISC) rn FROM cj)"),
        "tx_product_not_in_lookup": one(f"SELECT count(DISTINCT PRODUCT_ID) FROM cj WHERE PRODUCT_ID NOT IN (SELECT PRODUCT_ID FROM {csv(CJ / 'product.csv')})"),
        "hh_with_demo": one(f"SELECT count(DISTINCT household_key) FROM {csv(CJ / 'hh_demographic.csv')}"),
        "hh_in_campaign": one(f"SELECT count(DISTINCT household_key) FROM {csv(CJ / 'campaign_table.csv')}"),
        "days_missing": one("SELECT (max(DAY) - min(DAY) + 1) - count(DISTINCT DAY) FROM cj"),
        "trans_time_bad": one("SELECT count(*) FROM cj WHERE TRY_CAST(TRANS_TIME AS INT) IS NULL OR TRY_CAST(TRANS_TIME AS INT) % 100 > 59 OR TRY_CAST(TRANS_TIME AS INT) > 2359"),
        "baskets_multi_store": one("SELECT count(*) FROM (SELECT BASKET_ID FROM cj GROUP BY 1 HAVING count(DISTINCT STORE_ID) > 1)"),
        "baskets_multi_day": one("SELECT count(*) FROM (SELECT BASKET_ID FROM cj GROUP BY 1 HAVING count(DISTINCT DAY) > 1)"),
        "store_top10_share": one("SELECT sum(s) / (SELECT sum(SALES_VALUE) FROM cj) FROM (SELECT sum(SALES_VALUE) s FROM cj GROUP BY STORE_ID ORDER BY s DESC LIMIT 10)"),
        "hh_txn_weeks_median": one("SELECT median(w) FROM (SELECT household_key, count(DISTINCT WEEK_NO) w FROM cj GROUP BY 1)"),
    }
    cz = csv(CJ / "causal_data.csv")
    chk["causal_display_dist"] = q(f"SELECT display, count(*) FROM {cz} GROUP BY 1 ORDER BY 1")
    chk["causal_mailer_dist"] = q(f"SELECT mailer, count(*) FROM {cz} GROUP BY 1 ORDER BY 1")
    chk["causal_week_min"], chk["causal_week_max"] = one(f"SELECT min(WEEK_NO), max(WEEK_NO) FROM {cz}")
    chk["causal_stores"] = one(f"SELECT count(DISTINCT STORE_ID) FROM {cz}")
    chk["dept_top"] = q("SELECT p.DEPARTMENT, sum(SALES_VALUE) s FROM cj JOIN " + csv(CJ / "product.csv") + " p USING (PRODUCT_ID) GROUP BY 1 ORDER BY s DESC LIMIT 8")
    chk["income_dist"] = q(f"SELECT classification_3, count(*) FROM {csv(CJ / 'hh_demographic.csv')} GROUP BY 1 ORDER BY 2 DESC")
    con.execute("DROP TABLE cj")
    P["sources"]["cj"] = {"tables": list(t.values()), "checks": chk}


# ------------------------------------------------------------------ Carbo-Loading
def carbo():
    log("Carbo-Loading")
    t = [table_profile(csv(CARBO / "dh_transactions.csv"), "dh_transactions", "dh_transactions.csv", size_mb([CARBO / "dh_transactions.csv"])),
         table_profile(csv(CARBO / "dh_causal_lookup.csv"), "dh_causal_lookup", "dh_causal_lookup.csv", size_mb([CARBO / "dh_causal_lookup.csv"])),
         table_profile(csv(CARBO / "dh_product_lookup.csv"), "dh_product_lookup", "dh_product_lookup.csv", size_mb([CARBO / "dh_product_lookup.csv"]))]
    tx = csv(CARBO / "dh_transactions.csv")
    con.execute(f"CREATE OR REPLACE TEMP TABLE cb AS SELECT * FROM {tx}")
    pl = csv(CARBO / "dh_product_lookup.csv")
    chk = {
        "households": one("SELECT count(DISTINCT household) FROM cb"), "baskets": one("SELECT count(DISTINCT basket) FROM cb"),
        "stores": one("SELECT count(DISTINCT store) FROM cb"), "upcs": one("SELECT count(DISTINCT upc) FROM cb"),
        "week_min": one("SELECT min(week) FROM cb"), "week_max": one("SELECT max(week) FROM cb"),
        "day_min": one("SELECT min(day) FROM cb"), "day_max": one("SELECT max(day) FROM cb"),
        "sales_total": one("SELECT sum(dollar_sales) FROM cb"),
        "sales_le0": one("SELECT count(*) FROM cb WHERE dollar_sales <= 0"), "units_le0": one("SELECT count(*) FROM cb WHERE units <= 0"),
        "coupon_rows": one("SELECT count(*) FROM cb WHERE coupon = 1"),
        "dup_rows": one("SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT * FROM cb)) FROM cb"),
        "upc_not_in_lookup": one(f"SELECT count(DISTINCT upc) FROM cb WHERE TRY_CAST(upc AS BIGINT) NOT IN (SELECT upc FROM {pl})"),
        "commodity_sales": q(f"SELECT p.commodity, sum(dollar_sales) FROM cb JOIN {pl} p ON TRY_CAST(cb.upc AS BIGINT) = p.upc GROUP BY 1 ORDER BY 2 DESC"),
        "geography": q("SELECT geography, count(DISTINCT store) FROM cb GROUP BY 1 ORDER BY 1"),
        "price_outlier": one("SELECT count(*) FROM cb WHERE units > 0 AND dollar_sales / units > 20"),
    }
    cz = csv(CARBO / "dh_causal_lookup.csv")
    chk["feature_dist"] = q(f"SELECT feature_desc, count(*) FROM {cz} GROUP BY 1 ORDER BY 2 DESC")
    chk["display_dist"] = q(f"SELECT display_desc, count(*) FROM {cz} GROUP BY 1 ORDER BY 2 DESC")
    con.execute("DROP TABLE cb")
    P["sources"]["carbo"] = {"tables": t, "checks": chk}


# ------------------------------------------------------------------ Breakfast at the Frat (đọc từ cache parquet của bước phân tích)
def batf():
    log("Breakfast at the Frat")
    xl = D / "raw_dunnhumby/dunnhumby_Breakfast-at-the-Frat/dunnhumby - Breakfast at the Frat.xlsx"
    t = []
    for n in ["dh_Transaction_Data", "dh_Products_Lookup", "dh_Store_Lookup"]:
        f = BATF_CACHE / f"batf_{n}.parquet"
        t.append(table_profile(f"read_parquet('{f}')", n, f"{xl.name} · sheet {n}", size_mb([xl]) if n == "dh_Transaction_Data" else 0))
    tx = f"read_parquet('{BATF_CACHE / 'batf_dh_Transaction_Data.parquet'}')"
    cols = [c[0] for c in q(f"DESCRIBE SELECT * FROM {tx}")]
    up = {c.upper(): c for c in cols}
    g = lambda k: f'"{up[k]}"'
    chk = {
        "columns": cols,
        "weeks": one(f"SELECT count(DISTINCT {g('WEEK_END_DATE')}) FROM {tx}"),
        "week_min": str(one(f"SELECT min({g('WEEK_END_DATE')}) FROM {tx}")), "week_max": str(one(f"SELECT max({g('WEEK_END_DATE')}) FROM {tx}")),
        "stores": one(f"SELECT count(DISTINCT {g('STORE_NUM')}) FROM {tx}"), "upcs": one(f"SELECT count(DISTINCT {g('UPC')}) FROM {tx}"),
        "units_total": one(f"SELECT sum({g('UNITS')}) FROM {tx}"), "spend_total": one(f"SELECT sum({g('SPEND')}) FROM {tx}"),
        "price_null": one(f"SELECT count(*) - count({g('PRICE')}) FROM {tx}"), "base_price_null": one(f"SELECT count(*) - count({g('BASE_PRICE')}) FROM {tx}"),
        "price_gt_base": one(f"SELECT count(*) FROM {tx} WHERE {g('PRICE')} > {g('BASE_PRICE')} * 1.01"),
        "feature_rate": one(f"SELECT avg({g('FEATURE')}::DOUBLE) FROM {tx}"), "display_rate": one(f"SELECT avg({g('DISPLAY')}::DOUBLE) FROM {tx}"),
        "tpr_rate": one(f"SELECT avg({g('TPR_ONLY')}::DOUBLE) FROM {tx}"),
        "units_le0": one(f"SELECT count(*) FROM {tx} WHERE {g('UNITS')} <= 0"),
        "dup_keys": one(f"SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT {g('WEEK_END_DATE')}, {g('STORE_NUM')}, {g('UPC')} FROM {tx})) FROM {tx}"),
        "panel_fill": one(f"SELECT count(*)::DOUBLE / (count(DISTINCT {g('WEEK_END_DATE')}) * count(DISTINCT {g('STORE_NUM')} || '-' || {g('UPC')})) FROM {tx}"),
    }
    P["sources"]["batf"] = {"tables": t, "checks": chk}


# ------------------------------------------------------------------ Let's Get Sort-of-Real
def lgsr():
    log("Let's Get Sort-of-Real")
    files = sorted(glob.glob(str(LGSR / "transactions_*.csv")))
    pat = str(LGSR / "transactions_*.csv").replace("'", "''")
    src = f"read_csv('{pat}', auto_detect=true, union_by_name=true, sample_size=20000)"
    t = [table_profile(src, "transactions_YYYYWW", f"{len(files)} file tuần transactions_*.csv", size_mb(files)),
         table_profile(csv(LGSR / "time.csv"), "time", "time.csv", size_mb([LGSR / "time.csv"]))]
    con.execute(f"CREATE OR REPLACE TEMP TABLE lg AS SELECT * FROM {src}")
    chk = {
        "files": len(files), "weeks": one("SELECT count(DISTINCT SHOP_WEEK) FROM lg"),
        "week_min": one("SELECT min(SHOP_WEEK) FROM lg"), "week_max": one("SELECT max(SHOP_WEEK) FROM lg"),
        "date_min": one("SELECT min(SHOP_DATE) FROM lg"), "date_max": one("SELECT max(SHOP_DATE) FROM lg"),
        "customers": one("SELECT count(DISTINCT CUST_CODE) FROM lg"), "anon_rows": one("SELECT count(*) FROM lg WHERE CUST_CODE IS NULL"),
        "baskets": one("SELECT count(DISTINCT BASKET_ID) FROM lg"), "stores": one("SELECT count(DISTINCT STORE_CODE) FROM lg"),
        "products": one("SELECT count(DISTINCT PROD_CODE) FROM lg"), "spend_total": one("SELECT sum(SPEND) FROM lg"),
        "spend_le0": one("SELECT count(*) FROM lg WHERE SPEND <= 0"),
        "hour_range": q("SELECT min(SHOP_HOUR), max(SHOP_HOUR) FROM lg")[0],
        "seg_null": one("SELECT count(*) FROM lg WHERE seg_1 IS NULL"),
        "basket_type": q("SELECT BASKET_TYPE, count(DISTINCT BASKET_ID) FROM lg GROUP BY 1 ORDER BY 2 DESC"),
        "store_format": q("SELECT STORE_FORMAT, count(DISTINCT STORE_CODE) FROM lg GROUP BY 1 ORDER BY 1"),
        "region": q("SELECT STORE_REGION, count(DISTINCT STORE_CODE) FROM lg GROUP BY 1 ORDER BY 1"),
        "weeks_missing": [w for w in range(200607, 200820) if w % 100 <= 52 and w % 100 >= 1] ,
    }
    present = {r[0] for r in q("SELECT DISTINCT SHOP_WEEK FROM lg")}
    chk["weeks_missing"] = [w for w in chk["weeks_missing"] if w not in present]
    con.execute("DROP TABLE lg")
    P["sources"]["lgsr"] = {"tables": t, "checks": chk}


# ------------------------------------------------------------------ Walmart M5
def m5():
    log("Walmart M5")
    sales = M5 / "sales_train_evaluation.csv"
    t = [table_profile(csv(M5 / "calendar.csv"), "calendar", "calendar.csv", size_mb([M5 / "calendar.csv"])),
         table_profile(csv(M5 / "sell_prices.csv"), "sell_prices", "sell_prices.csv", size_mb([M5 / "sell_prices.csv"]))]
    # Bảng bán dạng rộng: 6 cột định danh + 1.941 cột ngày
    df = pd.read_csv(sales)
    idc = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
    dcols = [c for c in df.columns if c.startswith("d_")]
    v = df[dcols].to_numpy()
    first = (v > 0).argmax(axis=1)
    started = (pd.Series(range(len(dcols))).values[None, :] >= first[:, None])
    t.insert(0, {"name": "sales_train_evaluation", "file": sales.name, "mb": round(size_mb([sales]), 1), "rows": int(len(df)),
                 "cols": [{"name": c, "type": "VARCHAR", "nulls": int(df[c].isna().sum()), "null_pct": 0.0, "distinct": int(df[c].nunique())} for c in idc]
                 + [{"name": f"d_1 … d_{len(dcols)}", "type": "INT (lượng bán ngày)", "nulls": int(pd.isna(v).sum()), "null_pct": 0.0, "distinct": int(len(dcols))}]})
    pr = csv(M5 / "sell_prices.csv")
    chk = {
        "series": int(len(df)), "days": len(dcols), "items": int(df.item_id.nunique()), "stores": int(df.store_id.nunique()),
        "depts": int(df.dept_id.nunique()), "cats": int(df.cat_id.nunique()), "states": int(df.state_id.nunique()),
        "cells": int(v.size), "units_total": int(v.sum()), "neg_cells": int((v < 0).sum()),
        "zero_share_all": float((v == 0).mean()), "zero_share_after_launch": float(((v == 0) & started).sum() / started.sum()),
        "leading_zero_share": float((~started).sum() / v.size),
        "never_sold": int((v.sum(axis=1) == 0).sum()),
        "zero_share_by_cat": {c: float((df.loc[df.cat_id == c, dcols].to_numpy() == 0).mean()) for c in sorted(df.cat_id.unique())},
        "all_zero_days": [dcols[i] for i in range(len(dcols)) if v[:, i].sum() < 0.01 * v.sum(axis=0).mean()],
        "price_rows": one(f"SELECT count(*) FROM {pr}"), "price_null": one(f"SELECT count(*) - count(sell_price) FROM {pr}"),
        "price_le0": one(f"SELECT count(*) FROM {pr} WHERE sell_price <= 0"),
        "price_min": one(f"SELECT min(sell_price) FROM {pr}"), "price_max": one(f"SELECT max(sell_price) FROM {pr}"),
        "price_changes_share": one(f"SELECT avg(CASE WHEN sell_price <> lag_p THEN 1.0 ELSE 0 END) FROM (SELECT sell_price, lag(sell_price) OVER (PARTITION BY store_id, item_id ORDER BY wm_yr_wk) lag_p FROM {pr}) WHERE lag_p IS NOT NULL"),
        "events": one(f"SELECT count(*) FROM {csv(M5 / 'calendar.csv')} WHERE event_name_1 IS NOT NULL"),
        "snap_days": {s: one(f"SELECT sum(snap_{s}) FROM {csv(M5 / 'calendar.csv')}") for s in ("CA", "TX", "WI")},
        "date_min": str(one(f"SELECT min(date) FROM {csv(M5 / 'calendar.csv')}")), "date_max": str(one(f"SELECT max(date) FROM {csv(M5 / 'calendar.csv')}")),
    }
    # Độ phủ giá: tỷ lệ ô bán > 0 có giá tuần tương ứng
    cal = pd.read_csv(M5 / "calendar.csv", usecols=["d", "wm_yr_wk"])
    wk = dict(zip(cal.d, cal.wm_yr_wk))
    pk = set(map(tuple, pd.read_csv(M5 / "sell_prices.csv", usecols=["store_id", "item_id", "wm_yr_wk"]).to_numpy()))
    sold, priced = 0, 0
    sample = df.sample(3000, random_state=1)
    arr = sample[dcols].to_numpy()
    for i, (st, it) in enumerate(zip(sample.store_id, sample.item_id)):
        for j in arr[i].nonzero()[0]:
            sold += 1
            priced += (st, it, wk[dcols[j]]) in pk
    chk["sold_cells_with_price"] = priced / sold if sold else None
    chk["validation_vs_evaluation"] = "sales_train_validation.csv là 1.913 ngày đầu của sales_train_evaluation.csv (dùng bản evaluation 1.941 ngày)"
    P["sources"]["m5"] = {"tables": t, "checks": chk}


# ------------------------------------------------------------------ Nguồn của bản khảo sát đầu: UCI Online Retail, CJ gói R
def early():
    log("UCI Online Retail + Complete Journey gói R")
    xl = D / "raw/Online Retail.xlsx"
    df = pd.read_excel(xl, dtype={"InvoiceNo": str, "StockCode": str})
    con.register("ol", df)
    t = [table_profile("ol", "Online Retail", xl.name, size_mb([xl]))]
    chk = {
        "date_min": str(df.InvoiceDate.min()), "date_max": str(df.InvoiceDate.max()),
        "invoices": int(df.InvoiceNo.nunique()), "customers": int(df.CustomerID.nunique()), "countries": int(df.Country.nunique()),
        "uk_share_rows": float((df.Country == "United Kingdom").mean()),
        "cust_null": int(df.CustomerID.isna().sum()), "cancel_rows": int(df.InvoiceNo.str.startswith("C").sum()),
        "qty_le0": int((df.Quantity <= 0).sum()), "price_le0": int((df.UnitPrice <= 0).sum()),
        "dup_rows": int(df.duplicated().sum()),
        "non_product_codes": int(df.StockCode.str.fullmatch(r"(POST|D|M|BANK CHARGES|C2|DOT|CRUK|PADS|AMAZONFEE|S|B|m)").fillna(False).sum()),
    }
    con.unregister("ol")
    r = {"online_retail": {"tables": t, "checks": chk}}
    try:
        try:
            import pyreadr  # bản cài bằng pip (Linux/macOS)
        except ImportError:
            sys.path.insert(0, str(ROOT / "research" / "vendor"))  # bản kèm repo (Windows)
            import pyreadr
        tx = list(pyreadr.read_r(str(D / "raw/transactions.rds")).values())[0]
        r["cj_r"] = {"rows": int(len(tx)), "cols": list(tx.columns), "households": int(tx.household_id.nunique()),
                     "date_min": str(pd.to_datetime(tx.transaction_timestamp).min()), "date_max": str(pd.to_datetime(tx.transaction_timestamp).max()),
                     "sales_total": float(tx.sales_value.sum())}
    except Exception as e:  # pyreadr có thể không cài
        r["cj_r"] = {"error": f"{type(e).__name__}: {e}"}
    P["sources"]["early"] = r


# ------------------------------------------------------------------ Dữ liệu đóng gói cho web
def web():
    log("Dữ liệu web")
    wd = ROOT / "webapp/backend/data"
    files = []
    for f in sorted(wd.iterdir()):
        e = {"file": f.name, "kb": round(f.stat().st_size / 1e3, 1), "sha256": hashlib.sha256(f.read_bytes()).hexdigest()[:16]}
        if f.suffix == ".parquet":
            e["rows"] = one(f"SELECT count(*) FROM read_parquet('{f}')")
            e["cols"] = [c[0] for c in q(f"DESCRIBE SELECT * FROM read_parquet('{f}')")]
        files.append(e)
    m = wd / "m5_store_dept_daily.parquet"
    rec = {"units_total": one(f"SELECT sum(units) FROM read_parquet('{m}')"), "revenue_total": one(f"SELECT sum(revenue) FROM read_parquet('{m}')"),
           "date_min": str(one(f"SELECT min(date) FROM read_parquet('{m}')"))[:10], "date_max": str(one(f"SELECT max(date) FROM read_parquet('{m}')"))[:10]}
    P["web"] = {"files": files, "m5_reconcile": rec}


def raw_inventory():
    inv = []
    for f in sorted(D.rglob("*")):
        if f.is_file():
            inv.append({"path": str(f.relative_to(ROOT)).replace("\\", "/"), "mb": round(f.stat().st_size / 1e6, 2)})
    P["inventory"] = {"files": len(inv), "total_mb": round(sum(x["mb"] for x in inv), 1),
                      "by_folder": {k: round(sum(x["mb"] for x in inv if x["path"].startswith(f"data/{k}/")), 1) for k in ("raw", "raw_dunnhumby", "raw_m5")},
                      "large": [x for x in inv if x["mb"] >= 50]}


def save():
    (OUT / "profile.json").write_text(json.dumps(P, ensure_ascii=False, indent=1, default=lambda o: float(o) if hasattr(o, "__float__") else str(o)), encoding="utf-8")


if __name__ == "__main__":
    # python3 profile_data.py [cj carbo batf lgsr m5 early web]  — chạy lại một phần, giữ kết quả cũ của phần khác
    steps = {"cj": complete_journey, "carbo": carbo, "batf": batf, "lgsr": lgsr, "m5": m5, "early": early, "web": web}
    only = sys.argv[1:] or list(steps)
    if sys.argv[1:] and (OUT / "profile.json").exists():
        old = json.loads((OUT / "profile.json").read_text(encoding="utf-8"))
        P["sources"] = old.get("sources", {})
        P["web"] = old.get("web")
    raw_inventory()
    for k in only:
        t0 = time.time()
        steps[k]()
        save()
        log(f"  {k} xong sau {time.time() - t0:.0f}s")
    log(f"Đã ghi {OUT / 'profile.json'}")
