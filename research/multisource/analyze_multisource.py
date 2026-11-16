"""Phân tích đa nguồn: Complete Journey (bản gốc 2 năm), Breakfast at the Frat, Carbo-Loading,
Let's Get Sort-of-Real (mẫu 5K khách), M5 Walmart. Xuất outputs/multisource/results.json.

Chạy: python3 research/multisource/analyze_multisource.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
DH = ROOT / "data" / "raw_dunnhumby"
M5 = ROOT / "data" / "raw_m5"
OUT = ROOT / "outputs" / "multisource"
CACHE = OUT / "_cache"
OUT.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)

CJ = DH / "dunnhumby_The-Complete-Journey" / "dunnhumby_The-Complete-Journey CSV"
CL = DH / "dunnhumby_Carbo-Loading" / "dunnhumby - Carbo-Loading CSV"
BATF_XLSX = DH / "dunnhumby_Breakfast-at-the-Frat" / "dunnhumby - Breakfast at the Frat.xlsx"
LG = str(next(DH.glob("dunnhumby_Let*Sample-5K*"))).replace("'", "''")

con = duckdb.connect()
con.execute("SET memory_limit='4GB'; SET threads=8; SET preserve_insertion_order=false")
R: dict = {}
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.0f}s] {msg}", flush=True)


def q(sql):
    return con.execute(sql).df()


def r(x, n=4):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), n)


def records(df, n=4):
    out = []
    for row in df.to_dict("records"):
        out.append({k: (r(v, n) if isinstance(v, (float, np.floating)) else (int(v) if isinstance(v, (np.integer,)) else v)) for k, v in row.items()})
    return out


def within(df, y, xs, groups, iters=4):
    """Khử hiệu ứng cố định nhiều chiều bằng demeaning lặp (alternating projections)."""
    d = df[[y] + xs].astype(float).copy()
    for _ in range(iters):
        for g in groups:
            d = d - d.groupby(df[g].values).transform("mean")
    return d


def fe_ols(df, y, xs, groups, cluster=None):
    d = within(df, y, xs, groups)
    m = sm.OLS(d[y].values, d[xs].values)
    if cluster is not None:
        res = m.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df[cluster])[0]})
    else:
        res = m.fit(cov_type="HC1")
    return {x: {"coef": r(res.params[i]), "se": r(res.bse[i]), "ci_low": r(res.params[i] - 1.96 * res.bse[i]),
                "ci_high": r(res.params[i] + 1.96 * res.bse[i])} for i, x in enumerate(xs)} | {"n": int(len(df))}


def pareto(values):
    v = np.sort(np.asarray(values, dtype=float))[::-1]
    v = v[v > 0]
    c = np.cumsum(v) / v.sum()
    pts = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    curve = [{"pop": p, "share": r(c[max(int(np.ceil(p * len(v))) - 1, 0)])} for p in pts]
    gini = 1 - 2 * np.trapezoid(np.concatenate([[0], np.cumsum(np.sort(v)) / v.sum()]), dx=1 / len(v))
    return {"curve": curve, "top20": r(c[int(np.ceil(0.2 * len(v))) - 1]), "top1": r(c[max(int(np.ceil(0.01 * len(v))) - 1, 0)]),
            "gini": r(gini), "n": int(len(v))}


# ---------------------------------------------------------------- Complete Journey (bản gốc)
def complete_journey():
    log("CJ: nạp giao dịch")
    con.execute(f"""CREATE OR REPLACE TABLE cj AS SELECT * FROM read_csv('{CJ}/transaction_data.csv', header=true,
        types={{'BASKET_ID':'BIGINT','PRODUCT_ID':'BIGINT'}})""")
    con.execute(f"CREATE OR REPLACE TABLE cjp AS SELECT * FROM read_csv('{CJ}/product.csv', header=true, all_varchar=true)")
    con.execute("ALTER TABLE cjp ALTER PRODUCT_ID TYPE BIGINT")
    con.execute(f"CREATE OR REPLACE TABLE cjd AS SELECT * FROM read_csv('{CJ}/hh_demographic.csv', header=true, all_varchar=true)")
    o = {}
    o["profile"] = records(q("""SELECT count(*) AS "rows", count(DISTINCT household_key) households, count(DISTINCT BASKET_ID) baskets,
        count(DISTINCT STORE_ID) stores, count(DISTINCT PRODUCT_ID) products, min(DAY) day_min, max(DAY) day_max,
        max(WEEK_NO) AS "weeks", sum(SALES_VALUE) sales, sum(RETAIL_DISC) retail_disc, sum(COUPON_DISC) coupon_disc,
        sum(COUPON_MATCH_DISC) coupon_match_disc,
        sum(CASE WHEN QUANTITY<=0 THEN 1 ELSE 0 END) nonpos_qty, sum(CASE WHEN SALES_VALUE<=0 THEN 1 ELSE 0 END) nonpos_sales,
        avg(CASE WHEN RETAIL_DISC<>0 THEN 1 ELSE 0 END) share_loyalty_disc, avg(CASE WHEN COUPON_DISC<>0 THEN 1 ELSE 0 END) share_coupon
        FROM cj"""), 2)[0]
    o["profile"]["duplicate_rows"] = int(q("SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT * FROM cj)) n FROM cj")["n"][0])
    o["profile"]["unmatched_products"] = int(q("SELECT count(*) n FROM cj LEFT JOIN cjp USING(PRODUCT_ID) WHERE cjp.PRODUCT_ID IS NULL")["n"][0])
    o["profile"]["demographic_households"] = int(q("SELECT count(*) n FROM cjd")["n"][0])
    o["profile"]["demographic_sales_share"] = r(q("SELECT sum(CASE WHEN d.household_key IS NOT NULL THEN SALES_VALUE END)/sum(SALES_VALUE) s FROM cj LEFT JOIN cjd d ON cj.household_key=d.household_key::INT")["s"][0])
    o["profile"]["causal_rows"] = None

    o["weekly"] = records(q("""SELECT WEEK_NO AS wk_, sum(SALES_VALUE) sales, count(DISTINCT BASKET_ID) baskets,
        count(DISTINCT household_key) households, sum(SALES_VALUE)/count(DISTINCT BASKET_ID) aov,
        -sum(RETAIL_DISC+COUPON_DISC+COUPON_MATCH_DISC)/nullif(sum(SALES_VALUE),0) disc_rate
        FROM cj GROUP BY 1 ORDER BY 1"""), 3)

    hh = q("SELECT household_key, sum(SALES_VALUE) s FROM cj GROUP BY 1")
    o["pareto_households"] = pareto(hh["s"])
    prod = q("SELECT PRODUCT_ID, sum(SALES_VALUE) s FROM cj GROUP BY 1")
    o["pareto_products"] = pareto(prod["s"])

    o["departments"] = records(q("""SELECT coalesce(p.DEPARTMENT,'(không khớp)') department, sum(SALES_VALUE) sales,
        sum(CASE WHEN p.BRAND='Private' THEN SALES_VALUE ELSE 0 END)/sum(SALES_VALUE) private_share,
        -sum(RETAIL_DISC+COUPON_DISC+COUPON_MATCH_DISC)/sum(SALES_VALUE) disc_rate, count(*) lines
        FROM cj LEFT JOIN cjp p USING(PRODUCT_ID) GROUP BY 1 ORDER BY sales DESC LIMIT 12"""))
    o["commodities"] = records(q("""SELECT p.COMMODITY_DESC commodity, p.DEPARTMENT department, sum(SALES_VALUE) sales,
        count(DISTINCT household_key) hh, sum(CASE WHEN p.BRAND='Private' THEN SALES_VALUE ELSE 0 END)/sum(SALES_VALUE) private_share,
        -sum(RETAIL_DISC+COUPON_DISC+COUPON_MATCH_DISC)/sum(SALES_VALUE) disc_rate
        FROM cj JOIN cjp p USING(PRODUCT_ID) WHERE p.DEPARTMENT NOT IN ('KIOSK-GAS','MISC SALES TRAN','MISC. TRANS.')
        GROUP BY 1,2 ORDER BY sales DESC LIMIT 20"""))
    o["brand_split"] = records(q("""SELECT p.BRAND brand, sum(SALES_VALUE) sales, count(*) lines FROM cj JOIN cjp p USING(PRODUCT_ID) GROUP BY 1"""))

    # Giờ trong ngày
    o["hour"] = records(q("SELECT (TRY_CAST(TRANS_TIME AS INT)//100)::INT AS hr_, sum(SALES_VALUE) sales, count(DISTINCT BASKET_ID) baskets FROM cj GROUP BY 1 ORDER BY 1"))

    # Nhân khẩu học: chi tiêu theo tuần hoạt động, tỷ trọng nhãn riêng
    log("CJ: nhân khẩu học")
    demo = q("""WITH h AS (SELECT household_key, sum(SALES_VALUE) s, count(DISTINCT BASKET_ID) b,
            (max(DAY)-min(DAY)+1)/7.0 wk,
            sum(CASE WHEN p.BRAND='Private' THEN SALES_VALUE ELSE 0 END) pl,
            -sum(RETAIL_DISC+COUPON_DISC+COUPON_MATCH_DISC) disc
            FROM cj LEFT JOIN cjp p USING(PRODUCT_ID) GROUP BY 1)
        SELECT d.*, h.s, h.b, h.wk, h.pl, h.disc FROM h JOIN cjd d ON h.household_key=d.household_key::INT""")
    demo["weekly_spend"] = demo.s / demo.wk.clip(lower=4)
    demo["basket_value"] = demo.s / demo.b
    demo["pl_share"] = demo.pl / demo.s
    demo["disc_rate"] = demo.disc / demo.s
    demo["trips_per_week"] = demo.b / demo.wk.clip(lower=4)

    def by(col, order=None):
        g = demo.groupby(col).agg(households=("s", "size"), weekly_spend=("weekly_spend", "median"),
                                  basket_value=("basket_value", "median"), pl_share=("pl_share", "mean"),
                                  disc_rate=("disc_rate", "mean"), trips_per_week=("trips_per_week", "median")).reset_index()
        g = g.rename(columns={col: "level"})
        if order:
            g["k"] = g["level"].map({v: i for i, v in enumerate(order)})
            g = g.sort_values("k").drop(columns="k")
        return records(g, 4)

    inc_order = [f"Level{i}" for i in range(1, 13)]
    age_order = [f"Age Group{i}" for i in range(1, 7)]
    o["demo_income"] = by("classification_3", inc_order)
    o["demo_age"] = by("classification_1", age_order)
    o["demo_size"] = by("classification_4", ["1", "2", "3", "4", "5+"])
    o["demo_kids"] = by("KID_CATEGORY_DESC", ["None/Unknown", "1", "2", "3+"])
    # độ co giãn chi tiêu theo thu nhập (thứ bậc) — hồi quy log chi tiêu tuần theo bậc thu nhập
    d2 = demo[demo.classification_3.isin(inc_order)].copy()
    d2["inc"] = d2.classification_3.str.replace("Level", "").astype(int)
    d2["hs"] = d2.classification_4.str.replace("+", "").astype(int)
    X = sm.add_constant(d2[["inc", "hs"]].astype(float))
    m = sm.OLS(np.log(d2.weekly_spend), X).fit(cov_type="HC1")
    o["income_gradient"] = {"log_spend_per_level": r(m.params["inc"]), "se": r(m.bse["inc"]), "hh_size": r(m.params["hs"]),
                            "r2": r(m.rsquared), "n": int(len(d2))}
    m2 = sm.OLS(d2.pl_share, X).fit(cov_type="HC1")
    o["income_pl_gradient"] = {"pl_share_per_level": r(m2.params["inc"], 5), "se": r(m2.bse["inc"], 5), "n": int(len(d2))}

    # Chiến dịch & coupon
    log("CJ: chiến dịch")
    con.execute(f"CREATE OR REPLACE TABLE cjct AS SELECT * FROM read_csv('{CJ}/campaign_table.csv', header=true)")
    con.execute(f"CREATE OR REPLACE TABLE cjcd AS SELECT * FROM read_csv('{CJ}/campaign_desc.csv', header=true)")
    con.execute(f"CREATE OR REPLACE TABLE cjcr AS SELECT * FROM read_csv('{CJ}/coupon_redempt.csv', header=true)")
    o["campaign_types"] = records(q("""SELECT t.DESCRIPTION type, count(DISTINCT t.CAMPAIGN) campaigns, count(*) targets,
        count(DISTINCT t.household_key) households,
        (SELECT count(*) FROM (SELECT DISTINCT r.household_key, r.CAMPAIGN FROM cjcr r JOIN cjcd c USING(CAMPAIGN) WHERE c.DESCRIPTION=t.DESCRIPTION)) redeeming_pairs,
        avg(d.END_DAY-d.START_DAY) avg_days
        FROM cjct t JOIN cjcd d USING(CAMPAIGN) GROUP BY 1 ORDER BY 1"""))
    for c in o["campaign_types"]:
        c["redemption_rate"] = r(c["redeeming_pairs"] / c["targets"])
    # DiD thô: chi tiêu/ngày trong chiến dịch so với 30 ngày trước, nhóm nhận vs không nhận
    did = q("""WITH daily AS (SELECT household_key, DAY, sum(SALES_VALUE) s FROM cj GROUP BY 1,2),
        act AS (SELECT household_key, min(DAY) f, max(DAY) l FROM cj GROUP BY 1),
        base AS (SELECT c.CAMPAIGN, c.DESCRIPTION, c.START_DAY, c.END_DAY, a.household_key,
                 (t.household_key IS NOT NULL) treated
                 FROM cjcd c CROSS JOIN act a
                 LEFT JOIN cjct t ON t.CAMPAIGN=c.CAMPAIGN AND t.household_key=a.household_key
                 WHERE a.f <= c.START_DAY-30 AND a.l >= c.END_DAY)
        SELECT b.CAMPAIGN, b.DESCRIPTION, b.treated,
          sum(CASE WHEN d.DAY BETWEEN b.START_DAY AND b.END_DAY THEN d.s ELSE 0 END)/(max(b.END_DAY-b.START_DAY+1)*count(DISTINCT b.household_key)) during,
          sum(CASE WHEN d.DAY BETWEEN b.START_DAY-30 AND b.START_DAY-1 THEN d.s ELSE 0 END)/(30.0*count(DISTINCT b.household_key)) pre,
          count(DISTINCT b.household_key) n
        FROM base b LEFT JOIN daily d ON d.household_key=b.household_key AND d.DAY BETWEEN b.START_DAY-30 AND b.END_DAY
        GROUP BY 1,2,3""")
    piv = did.pivot_table(index=["CAMPAIGN", "DESCRIPTION"], columns="treated", values=["during", "pre", "n"]).dropna()
    piv.columns = [f"{a}_{'t' if b else 'c'}" for a, b in piv.columns]
    piv = piv.reset_index()
    piv["growth_t"] = piv.during_t / piv.pre_t - 1
    piv["growth_c"] = piv.during_c / piv.pre_c - 1
    piv["did_pp"] = piv.growth_t - piv.growth_c
    piv["level_gap"] = piv.pre_t / piv.pre_c - 1
    o["campaign_did"] = records(piv[["CAMPAIGN", "DESCRIPTION", "n_t", "n_c", "pre_t", "pre_c", "growth_t", "growth_c", "did_pp", "level_gap"]].rename(
        columns={"CAMPAIGN": "campaign", "DESCRIPTION": "type"}))
    o["campaign_did_summary"] = records(piv.groupby("DESCRIPTION").agg(campaigns=("CAMPAIGN", "size"), did_pp_median=("did_pp", "median"),
                                                                        did_pp_mean=("did_pp", "mean"), level_gap=("level_gap", "median")).reset_index().rename(columns={"DESCRIPTION": "type"}))

    # Causal: trưng bày & tờ rơi
    log("CJ: causal (trưng bày/tờ rơi) — file 700MB")
    con.execute(f"""CREATE OR REPLACE TABLE cjc AS SELECT PRODUCT_ID::BIGINT pid, STORE_ID::INT sid, WEEK_NO::INT wk,
        display::VARCHAR display, mailer::VARCHAR mailer FROM read_csv('{CJ}/causal_data.csv', header=true, all_varchar=true)""")
    o["profile"]["causal_rows"] = int(q("SELECT count(*) n FROM cjc")["n"][0])
    o["causal_mix"] = {
        "display": records(q("SELECT display code, count(*) n FROM cjc GROUP BY 1 ORDER BY 1")),
        "mailer": records(q("SELECT mailer code, count(*) n FROM cjc GROUP BY 1 ORDER BY 1")),
    }
    psw = q("""WITH s AS (SELECT PRODUCT_ID pid, STORE_ID sid, WEEK_NO wk, sum(QUANTITY) units, sum(SALES_VALUE) sales,
                count(DISTINCT household_key) hh FROM cj JOIN cjp USING(PRODUCT_ID)
                WHERE DEPARTMENT NOT IN ('KIOSK-GAS','MISC SALES TRAN','MISC. TRANS.') AND QUANTITY>0 AND SALES_VALUE>0
                GROUP BY 1,2,3),
        cov AS (SELECT DISTINCT pid, sid FROM cjc)
        SELECT s.*, coalesce(c.display,'0')<>'0' disp, coalesce(c.mailer,'0')<>'0' mail
        FROM s JOIN cov USING(pid,sid) LEFT JOIN cjc c USING(pid,sid,wk)""")
    psw["key"] = psw.pid.astype(str) + "_" + psw.sid.astype(str)
    psw["ly"] = np.log(psw.units)
    psw["d"] = psw.disp.astype(float)
    psw["m"] = psw.mail.astype(float)
    psw["dm"] = psw.d * psw.m
    vc = psw.groupby("key")[["d", "m"]].agg(["min", "max"])
    keep = vc.index[(vc[("d", "max")] > vc[("d", "min")]) | (vc[("m", "max")] > vc[("m", "min")])]
    sub = psw[psw.key.isin(keep)].copy()
    est = fe_ols(sub, "ly", ["d", "m", "dm"], ["key", "wk"], cluster="key")
    o["causal_lift"] = {k: v for k, v in est.items()}
    o["causal_lift"]["pairs"] = int(len(keep))
    o["causal_lift"]["lift_display"] = r(np.exp(est["d"]["coef"]) - 1)
    o["causal_lift"]["lift_mailer"] = r(np.exp(est["m"]["coef"]) - 1)
    o["causal_lift"]["lift_both"] = r(np.exp(est["d"]["coef"] + est["m"]["coef"] + est["dm"]["coef"]) - 1)
    del psw, sub
    R["cj"] = o


# ---------------------------------------------------------------- Breakfast at the Frat
def batf():
    pq = CACHE / "batf.parquet"
    if not pq.exists():
        log("BATF: đọc xlsx (chậm, cache lần đầu)")
        sheets = pd.read_excel(BATF_XLSX, sheet_name=None, header=1, engine="openpyxl")
        for k, v in sheets.items():
            v.dropna(axis=1, how="all").to_parquet(CACHE / f"batf_{k.replace(' ', '_')}.parquet")
        sheets["dh Transaction Data"].dropna(axis=1, how="all").to_parquet(pq)
    log("BATF: phân tích")
    tx = pd.read_parquet(pq)
    st = pd.read_parquet(CACHE / "batf_dh_Store_Lookup.parquet")
    pr = pd.read_parquet(CACHE / "batf_dh_Products_Lookup.parquet")
    tx = tx.merge(pr[["UPC", "MANUFACTURER", "CATEGORY", "SUB_CATEGORY", "DESCRIPTION"]], on="UPC", how="left")
    tx = tx.merge(st[["STORE_ID", "SEG_VALUE_NAME", "ADDRESS_STATE_PROV_CODE", "SALES_AREA_SIZE_NUM", "AVG_WEEKLY_BASKETS"]],
                  left_on="STORE_NUM", right_on="STORE_ID", how="left")
    o = {}
    o["profile"] = {"rows": int(len(tx)), "stores": int(tx.STORE_NUM.nunique()), "upcs": int(tx.UPC.nunique()),
                    "weeks": int(tx.WEEK_END_DATE.nunique()), "start": str(tx.WEEK_END_DATE.min().date()), "end": str(tx.WEEK_END_DATE.max().date()),
                    "states": sorted(st.ADDRESS_STATE_PROV_CODE.dropna().unique().tolist()), "spend": r(tx.SPEND.sum(), 2),
                    "missing_price": int(tx.PRICE.isna().sum()), "missing_base_price": int(tx.BASE_PRICE.isna().sum()),
                    "nonpos_units": int((tx.UNITS <= 0).sum()),
                    "price_above_base": int((tx.PRICE > tx.BASE_PRICE + 0.01).sum()),
                    "share_feature": r(tx.FEATURE.mean()), "share_display": r(tx.DISPLAY.mean()), "share_tpr": r(tx.TPR_ONLY.mean()),
                    "segments": records(st.groupby("SEG_VALUE_NAME").agg(stores=("STORE_ID", "size"), avg_baskets=("AVG_WEEKLY_BASKETS", "mean"),
                                                                         area=("SALES_AREA_SIZE_NUM", "mean")).reset_index(), 1)}
    tx = tx[(tx.UNITS > 0) & (tx.PRICE > 0) & (tx.BASE_PRICE > 0)].copy()
    tx["disc_depth"] = (1 - tx.PRICE / tx.BASE_PRICE).clip(lower=0)
    o["weekly"] = records(tx.groupby(["WEEK_END_DATE", "CATEGORY"]).SPEND.sum().unstack().reset_index().assign(
        WEEK_END_DATE=lambda d: d.WEEK_END_DATE.dt.strftime("%Y-%m-%d")).rename(columns={"WEEK_END_DATE": "week"}), 2)
    tx["ly"] = np.log(tx.UNITS)
    tx["lp"] = np.log(tx.PRICE)
    tx["key"] = tx.STORE_NUM.astype(str) + "_" + tx.UPC.astype(str)
    tx["wk"] = tx.WEEK_END_DATE.dt.strftime("%Y%m%d")
    for c in ["FEATURE", "DISPLAY", "TPR_ONLY"]:
        tx[c] = tx[c].astype(float)
    el = []
    for cat, g in tx.groupby("CATEGORY"):
        e = fe_ols(g, "ly", ["lp", "FEATURE", "DISPLAY", "TPR_ONLY"], ["key", "wk"], cluster="key")
        el.append({"category": cat, "elasticity": e["lp"]["coef"], "se": e["lp"]["se"], "ci_low": e["lp"]["ci_low"], "ci_high": e["lp"]["ci_high"],
                   "lift_feature": r(np.exp(e["FEATURE"]["coef"]) - 1), "lift_display": r(np.exp(e["DISPLAY"]["coef"]) - 1),
                   "lift_tpr": r(np.exp(e["TPR_ONLY"]["coef"]) - 1), "n": e["n"]})
    o["elasticity_category"] = el
    seg = []
    for (cat, s), g in tx.groupby(["CATEGORY", "SEG_VALUE_NAME"]):
        e = fe_ols(g, "ly", ["lp", "FEATURE", "DISPLAY", "TPR_ONLY"], ["key", "wk"], cluster="key")
        seg.append({"category": cat, "segment": s, "elasticity": e["lp"]["coef"], "se": e["lp"]["se"], "n": e["n"]})
    o["elasticity_segment"] = seg
    # nhãn riêng vs quốc gia
    tx["is_pl"] = tx.MANUFACTURER.eq("PRIVATE LABEL")
    pl = tx.groupby(["CATEGORY", "is_pl"]).agg(spend=("SPEND", "sum"), units=("UNITS", "sum"), base=("BASE_PRICE", "mean"),
                                                 disc=("disc_depth", "mean"), promo=("TPR_ONLY", "mean")).reset_index()
    pl["avg_price"] = pl.spend / pl.units
    o["private_label"] = records(pl, 3)
    # phân bố độ sâu giảm giá
    bins = [-0.001, 0.0001, 0.1, 0.2, 0.3, 0.4, 1]
    labels = ["0%", "0–10%", "10–20%", "20–30%", "30–40%", "≥40%"]
    tx["dbin"] = pd.cut(tx.disc_depth, bins, labels=labels)
    dd = tx.groupby("dbin", observed=False).agg(rows=("UNITS", "size"), units=("UNITS", "sum"), spend=("SPEND", "sum")).reset_index()
    dd["units_per_row"] = dd.units / dd.rows
    o["discount_depth"] = records(dd.rename(columns={"dbin": "bin"}).assign(bin=lambda d: d.bin.astype(str)), 3)
    # cửa hàng: quy mô vs tỷ lệ chi tiêu
    sto = tx.groupby(["STORE_NUM", "SEG_VALUE_NAME"]).agg(spend=("SPEND", "sum"), visits=("VISITS", "sum"),
                                                           area=("SALES_AREA_SIZE_NUM", "first"), baskets=("AVG_WEEKLY_BASKETS", "first"),
                                                           price=("PRICE", "mean")).reset_index()
    o["stores"] = records(sto, 2)
    o["segment_summary"] = records(tx.groupby("SEG_VALUE_NAME").agg(spend_per_row=("SPEND", "mean"), price_idx=("PRICE", "mean"),
                                                                    disc=("disc_depth", "mean"), feature=("FEATURE", "mean"),
                                                                    display=("DISPLAY", "mean")).reset_index().rename(columns={"SEG_VALUE_NAME": "segment"}))
    R["batf"] = o


# ---------------------------------------------------------------- Carbo-Loading
def carbo():
    log("Carbo: nạp")
    con.execute(f"CREATE OR REPLACE TABLE cl AS SELECT * FROM read_csv('{CL}/dh_transactions.csv', header=true)")
    con.execute(f"CREATE OR REPLACE TABLE clp AS SELECT * FROM read_csv('{CL}/dh_product_lookup.csv', header=true, all_varchar=true)")
    con.execute("ALTER TABLE clp ALTER upc TYPE BIGINT")
    con.execute(f"CREATE OR REPLACE TABLE clc AS SELECT * FROM read_csv('{CL}/dh_causal_lookup.csv', header=true)")
    o = {}
    o["profile"] = records(q("""SELECT count(*) AS "rows", count(DISTINCT household) households, count(DISTINCT basket) baskets,
        count(DISTINCT store) stores, count(DISTINCT upc) upcs, max(week) AS "weeks", sum(dollar_sales) sales,
        avg(coupon) coupon_rate, sum(CASE WHEN dollar_sales<=0 THEN 1 ELSE 0 END) nonpos_sales,
        sum(CASE WHEN units<=0 THEN 1 ELSE 0 END) nonpos_units FROM cl"""), 4)[0]
    o["profile"]["unmatched_upc"] = int(q("SELECT count(*) n FROM cl LEFT JOIN clp USING(upc) WHERE clp.upc IS NULL")["n"][0])
    o["profile"]["causal_rows"] = int(q("SELECT count(*) n FROM clc")["n"][0])
    o["commodity"] = records(q("""SELECT p.commodity, sum(dollar_sales) sales, sum(units) units, count(DISTINCT household) hh,
        avg(coupon) coupon_rate, sum(dollar_sales)/sum(units) avg_price,
        sum(CASE WHEN lower(p.brand) LIKE '%private%' THEN dollar_sales ELSE 0 END)/sum(dollar_sales) private_share
        FROM cl JOIN clp p USING(upc) GROUP BY 1 ORDER BY sales DESC"""))
    o["brands"] = records(q("""WITH b AS (SELECT p.commodity, p.brand, sum(dollar_sales) sales, count(DISTINCT household) hh
        FROM cl JOIN clp p USING(upc) GROUP BY 1,2)
        SELECT *, sales/sum(sales) OVER (PARTITION BY commodity) share FROM b
        QUALIFY row_number() OVER (PARTITION BY commodity ORDER BY sales DESC)<=6 ORDER BY commodity, sales DESC"""))
    # HHI theo ngành
    o["hhi"] = records(q("""WITH b AS (SELECT p.commodity, p.brand, sum(dollar_sales) s FROM cl JOIN clp p USING(upc) GROUP BY 1,2),
        sh AS (SELECT commodity, s/sum(s) OVER (PARTITION BY commodity) sh FROM b)
        SELECT commodity, sum((sh*100)^2) hhi, count(*) brands FROM sh GROUP BY 1 ORDER BY 1"""), 1)
    # bổ trợ trong giỏ
    log("Carbo: bổ trợ giỏ")
    cb = q("""WITH x AS (SELECT DISTINCT basket, p.commodity c FROM cl JOIN clp p USING(upc))
        SELECT a.c a, b.c b, count(*) n FROM x a JOIN x b ON a.basket=b.basket AND a.c<b.c GROUP BY 1,2""")
    nb = q("SELECT p.commodity c, count(DISTINCT basket) n FROM cl JOIN clp p USING(upc) GROUP BY 1").set_index("c").n
    N = int(q("SELECT count(DISTINCT basket) n FROM cl")["n"][0])
    cb["support"] = cb.n / N
    cb["lift"] = cb.n * N / (cb.a.map(nb) * cb.b.map(nb))
    cb["conf_a_b"] = cb.n / cb.a.map(nb)
    cb["conf_b_a"] = cb.n / cb.b.map(nb)
    o["complement"] = records(cb.sort_values("lift", ascending=False))
    # trung thành thương hiệu
    log("Carbo: trung thành")
    loy = q("""WITH h AS (SELECT household, p.commodity, p.brand, count(DISTINCT basket) trips FROM cl JOIN clp p USING(upc) GROUP BY 1,2,3),
        t AS (SELECT household, commodity, sum(trips) tot, max(trips) top, count(*) nbrands FROM h GROUP BY 1,2)
        SELECT commodity, top/tot sow, nbrands FROM t WHERE tot>=5""")
    lo = []
    for c, g in loy.groupby("commodity"):
        lo.append({"commodity": c, "households": int(len(g)), "median_sow": r(g.sow.median()), "share_loyal_80": r((g.sow >= 0.8).mean()),
                   "share_switcher_50": r((g.sow < 0.5).mean()), "median_brands": r(g.nbrands.median())})
    o["loyalty"] = lo
    o["loyalty_hist"] = records(loy.assign(b=pd.cut(loy.sow, [0, .3, .4, .5, .6, .7, .8, .9, .999, 1.0], include_lowest=True).astype(str))
                                .groupby(["commodity", "b"]).size().reset_index(name="n"))
    # coupon: lần đầu mua bằng coupon
    o["coupon_first"] = records(q("""WITH f AS (SELECT household, p.commodity, min(day) d0 FROM cl JOIN clp p USING(upc) GROUP BY 1,2),
        fc AS (SELECT f.household, f.commodity, max(cl.coupon) first_coupon FROM f JOIN cl ON cl.household=f.household AND cl.day=f.d0
               JOIN clp p ON p.upc=cl.upc AND p.commodity=f.commodity GROUP BY 1,2),
        rep AS (SELECT household, p.commodity, count(DISTINCT basket) trips FROM cl JOIN clp p USING(upc) GROUP BY 1,2)
        SELECT fc.commodity, fc.first_coupon, count(*) hh, avg(CASE WHEN trips>1 THEN 1 ELSE 0 END) repeat_rate, median(trips) med_trips
        FROM fc JOIN rep USING(household, commodity) GROUP BY 1,2 ORDER BY 1,2"""))
    # giờ mua
    o["hour"] = records(q("SELECT (TRY_CAST(time_of_transaction AS INT)//100)::INT AS hr_, sum(dollar_sales) sales, count(DISTINCT basket) baskets FROM cl GROUP BY 1 ORDER BY 1"))
    o["pareto_households"] = pareto(q("SELECT household, sum(dollar_sales) s FROM cl GROUP BY 1")["s"])
    # độ co giãn giá + feature/display (tuần 43–104 có causal)
    log("Carbo: co giãn")
    w = q("""WITH s AS (SELECT upc, store, week, sum(units) u, sum(dollar_sales) d FROM cl WHERE units>0 AND dollar_sales>0 AND week>=43 GROUP BY 1,2,3)
        SELECT s.*, p.commodity, coalesce(c.feature_desc,'Not on Feature') f, coalesce(c.display_desc,'Not on Display') dsp
        FROM s JOIN clp p USING(upc) LEFT JOIN (SELECT upc, store, week, any_value(feature_desc) feature_desc, any_value(display_desc) display_desc
            FROM clc GROUP BY 1,2,3) c USING(upc, store, week)""")
    w["ly"] = np.log(w.u)
    w["lp"] = np.log(w.d / w.u)
    w["feat"] = (~w.f.str.contains("Not on", case=False)).astype(float)
    w["disp"] = (~w.dsp.str.contains("Not on", case=False)).astype(float)
    w["key"] = w.upc.astype(str) + "_" + w.store.astype(str)
    el = []
    for c, g in w.groupby("commodity"):
        g = g[g.groupby("key").key.transform("size") >= 8]
        e = fe_ols(g, "ly", ["lp", "feat", "disp"], ["key", "week"], cluster="key")
        el.append({"commodity": c, "elasticity": e["lp"]["coef"], "se": e["lp"]["se"], "ci_low": e["lp"]["ci_low"], "ci_high": e["lp"]["ci_high"],
                   "lift_feature": r(np.exp(e["feat"]["coef"]) - 1), "lift_display": r(np.exp(e["disp"]["coef"]) - 1), "n": e["n"]})
    o["elasticity"] = el
    o["weekly"] = records(q("""SELECT week AS wk_, p.commodity, sum(dollar_sales) sales FROM cl JOIN clp p USING(upc) GROUP BY 1,2 ORDER BY 1"""), 2)
    R["carbo"] = o


# ---------------------------------------------------------------- Let's Get Sort-of-Real (5K)
def lgsr():
    log("LGSR: nạp 117 tuần")
    con.execute(f"""CREATE OR REPLACE TABLE lg AS SELECT * FROM read_csv('{LG}/transactions_*.csv', header=true, union_by_name=true,
        types={{'BASKET_ID':'BIGINT','SHOP_DATE':'VARCHAR'}})""")
    o = {}
    o["profile"] = records(q("""SELECT count(*) AS "rows", count(DISTINCT CUST_CODE) customers, count(DISTINCT BASKET_ID) baskets,
        count(DISTINCT STORE_CODE) stores, count(DISTINCT PROD_CODE) products, count(DISTINCT SHOP_WEEK) AS "weeks",
        min(SHOP_DATE) AS "start", max(SHOP_DATE) AS "end_", sum(SPEND) spend,
        avg(CASE WHEN CUST_CODE IS NULL THEN 1 ELSE 0 END) share_rows_no_card,
        avg(CASE WHEN seg_1 IS NULL THEN 1 ELSE 0 END) share_seg1_null,
        sum(CASE WHEN SPEND<=0 THEN 1 ELSE 0 END) nonpos_spend FROM lg"""), 4)[0]
    o["profile"]["baskets_no_card"] = int(q("SELECT count(DISTINCT BASKET_ID) n FROM lg WHERE CUST_CODE IS NULL")["n"][0])
    bsk = """(SELECT BASKET_ID, any_value(CUST_CODE) cust, any_value(BASKET_SIZE) size, any_value(BASKET_PRICE_SENSITIVITY) ps,
        any_value(BASKET_TYPE) btype, any_value(BASKET_DOMINANT_MISSION) mission, any_value(STORE_FORMAT) fmt,
        any_value(STORE_REGION) region, any_value(SHOP_WEEKDAY) wd, any_value(SHOP_HOUR) hr, any_value(seg_1) seg1, any_value(seg_2) seg2,
        sum(SPEND) spend, sum(QUANTITY) items, count(*) lines FROM lg GROUP BY 1)"""
    con.execute(f"CREATE OR REPLACE TABLE lgb AS SELECT * FROM {bsk}")
    for k, col in [("price_sens", "ps"), ("basket_type", "btype"), ("mission", "mission"), ("store_format", "fmt"), ("region", "region"),
                   ("basket_size", "size"), ("seg1", "seg1"), ("seg2", "seg2")]:
        o[k] = records(q(f"""SELECT coalesce({col}::VARCHAR,'(trống)') AS "level", count(*) baskets, sum(spend) spend, avg(spend) aov,
            avg(items) items, avg(CASE WHEN cust IS NULL THEN 1 ELSE 0 END) no_card FROM lgb GROUP BY 1 ORDER BY spend DESC"""))
    o["heat"] = records(q("SELECT wd, hr, count(*) baskets, sum(spend) spend FROM lgb GROUP BY 1,2 ORDER BY 1,2"))
    o["mission_x_ps"] = records(q("SELECT mission, ps, count(*) baskets, avg(spend) aov FROM lgb GROUP BY 1,2"))
    o["format_x_ps"] = records(q("SELECT fmt, ps, count(*) baskets, sum(spend) spend FROM lgb GROUP BY 1,2"))
    o["weekly"] = records(q("""SELECT SHOP_WEEK AS wk_, sum(SPEND) spend, count(DISTINCT BASKET_ID) baskets FROM lg GROUP BY 1 ORDER BY 1"""), 2)
    o["pareto_customers"] = pareto(q("SELECT CUST_CODE, sum(SPEND) s FROM lg WHERE CUST_CODE IS NOT NULL GROUP BY 1")["s"])
    o["pareto_products"] = pareto(q("SELECT PROD_CODE, sum(SPEND) s FROM lg GROUP BY 1")["s"])
    # khách: chi tiêu theo tuần và phân khúc giá chiếm ưu thế
    o["customer_ps"] = records(q("""WITH c AS (SELECT cust, mode(ps) ps, count(*) b, sum(spend) s FROM lgb WHERE cust IS NOT NULL GROUP BY 1)
        SELECT ps, count(*) customers, median(b) med_baskets, median(s) med_spend, median(s/b) med_aov FROM c GROUP BY 1 ORDER BY 1"""))
    R["lgsr"] = o


# ---------------------------------------------------------------- M5 Walmart
def m5():
    log("M5: nạp")
    cal = pd.read_csv(M5 / "calendar.csv", parse_dates=["date"])
    sales = pd.read_csv(M5 / "sales_train_evaluation.csv")
    ids = sales.iloc[:, :6]
    dcols = [c for c in sales.columns if c.startswith("d_")]
    S = sales[dcols].to_numpy(dtype=np.float32)
    del sales
    cal = cal[cal.d.isin(dcols)].reset_index(drop=True)
    o = {}
    prices = pd.read_csv(M5 / "sell_prices.csv")
    o["profile"] = {"series": int(len(ids)), "items": int(ids.item_id.nunique()), "stores": int(ids.store_id.nunique()),
                    "states": sorted(ids.state_id.unique().tolist()), "days": int(len(dcols)), "start": str(cal.date.min().date()),
                    "end": str(cal.date.max().date()), "units": int(S.sum()), "zero_share": r((S == 0).mean()),
                    "price_rows": int(len(prices)), "events": int(cal.event_name_1.notna().sum()),
                    "categories": ids.cat_id.value_counts().to_dict(), "depts": int(ids.dept_id.nunique())}
    # doanh thu: units × giá tuần
    log("M5: doanh thu tuần")
    wk = cal.wm_yr_wk.values
    uwk, widx = np.unique(wk, return_inverse=True)
    W = np.zeros((S.shape[0], len(uwk)), dtype=np.float32)
    for j in range(len(uwk)):
        W[:, j] = S[:, widx == j].sum(axis=1)
    long = pd.DataFrame({"row": np.repeat(np.arange(len(ids)), len(uwk)), "wm_yr_wk": np.tile(uwk, len(ids)), "units": W.ravel()})
    long["store_id"] = ids.store_id.values[long.row]
    long["item_id"] = ids.item_id.values[long.row]
    long = long.merge(prices, on=["store_id", "item_id", "wm_yr_wk"], how="inner")
    long["rev"] = long.units * long.sell_price
    long["cat"] = ids.cat_id.values[long.row]
    long["state"] = ids.state_id.values[long.row]
    o["profile"]["revenue"] = r(long.rev.sum(), 0)
    item_rev = long.groupby("row").rev.sum()
    o["pareto_series"] = pareto(item_rev.values)
    o["pareto_items"] = pareto(long.groupby("item_id").rev.sum().values)
    wkd = cal.groupby("wm_yr_wk").date.min()
    rv = long.groupby(["wm_yr_wk", "cat"]).rev.sum().unstack()
    rv.index = [str(wkd[i].date()) for i in rv.index]
    o["weekly_rev"] = records(rv.reset_index().rename(columns={"index": "week"}), 0)
    o["state_cat"] = records(long.groupby(["state", "cat"]).agg(rev=("rev", "sum"), units=("units", "sum")).reset_index(), 0)
    o["store_rev"] = records(long.assign(store=ids.store_id.values[long.row]).groupby("store").rev.sum().reset_index(), 0)

    # theo ngày
    tot = S.sum(axis=0)
    daily = pd.DataFrame({"date": cal.date, "units": tot})
    for c in ["FOODS", "HOUSEHOLD", "HOBBIES"]:
        daily[c] = S[(ids.cat_id == c).values].sum(axis=0)
    for s in ["CA", "TX", "WI"]:
        daily[s] = S[(ids.state_id == s).values].sum(axis=0)
    o["monthly"] = records(daily.set_index("date")[["FOODS", "HOUSEHOLD", "HOBBIES"]].resample("MS").sum().iloc[:-1].reset_index()
                           .assign(date=lambda d: d.date.dt.strftime("%Y-%m")), 0)
    o["weekday"] = records(daily.assign(wd=cal.weekday.values).groupby("wd")[["FOODS", "HOUSEHOLD", "HOBBIES"]].mean().reset_index(), 0)
    o["christmas_zero"] = [str(d.date()) for d in daily.date[daily.units < 100]]

    # SNAP: FOODS theo bang, FE năm-tháng & thứ, loại ngày lễ
    log("M5: SNAP")
    snap = []
    for s in ["CA", "TX", "WI"]:
        for c in ["FOODS", "HOUSEHOLD", "HOBBIES"]:
            y = S[((ids.state_id == s) & (ids.cat_id == c)).values].sum(axis=0)
            d = pd.DataFrame({"ly": np.log(np.maximum(y, 1)), "snap": cal[f"snap_{s}"].values.astype(float),
                              "ym": cal.date.dt.strftime("%Y%m").values, "wd": cal.wday.values, "ev": cal.event_name_1.notna().astype(float).values})
            d = d[y > 100]
            X = pd.get_dummies(d[["ym", "wd"]].astype(str), drop_first=True).astype(float)
            X["snap"] = d.snap
            X["ev"] = d.ev
            res = sm.OLS(d.ly, sm.add_constant(X)).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
            snap.append({"state": s, "cat": c, "lift": r(np.exp(res.params["snap"]) - 1), "se": r(res.bse["snap"]),
                         "ci_low": r(np.exp(res.params["snap"] - 1.96 * res.bse["snap"]) - 1), "ci_high": r(np.exp(res.params["snap"] + 1.96 * res.bse["snap"]) - 1)})
    o["snap"] = snap
    # SNAP: ngày trong tháng (FOODS, chuẩn hóa theo trung bình tháng)
    dm = daily.assign(dom=daily.date.dt.day, ym=daily.date.dt.to_period("M"))
    dm = dm[dm.units > 100]
    for s in ["CA", "TX", "WI"]:
        dm[f"{s}_idx"] = dm[s] / dm.groupby("ym")[s].transform("mean")
    o["day_of_month"] = records(dm.groupby("dom")[["CA_idx", "TX_idx", "WI_idx"]].mean().reset_index(), 4)
    o["snap_days"] = {s: sorted(cal.loc[cal[f"snap_{s}"] == 1, "date"].dt.day.unique().tolist()) for s in ["CA", "TX", "WI"]}

    # sự kiện: so với cùng thứ tuần trước/sau
    ev = []
    dd = daily.set_index("date").units
    for _, row in cal[cal.event_name_1.notna()].iterrows():
        dte = row.date
        ref = [dd.get(dte - pd.Timedelta(days=7)), dd.get(dte + pd.Timedelta(days=7))]
        ref = [x for x in ref if x is not None and x > 100]
        if ref and dd.get(dte, 0) > 100:
            ev.append({"event": row.event_name_1, "type": row.event_type_1, "ratio": dd[dte] / np.mean(ref) - 1})
    evd = pd.DataFrame(ev).groupby(["event", "type"]).ratio.agg(["mean", "count"]).reset_index().sort_values("mean")
    o["events"] = records(evd.rename(columns={"mean": "lift", "count": "n"}))

    # độ co giãn giá (tuần có bán), FE series & tuần×bang
    log("M5: co giãn giá")
    p = long[(long.units > 0)].copy()
    p["ly"] = np.log(p.units)
    p["lp"] = np.log(p.sell_price)
    p["key"] = p.row
    p["sw"] = p.state + "_" + p.wm_yr_wk.astype(str)
    var = p.groupby("key").lp.transform("std")
    p = p[var > 0.01]
    el = []
    for c, g in p.groupby("cat"):
        e = fe_ols(g, "ly", ["lp"], ["key", "sw"], cluster="key")
        el.append({"cat": c, "elasticity": e["lp"]["coef"], "se": e["lp"]["se"], "ci_low": e["lp"]["ci_low"], "ci_high": e["lp"]["ci_high"], "n": e["n"]})
    o["elasticity"] = el
    # giá: lạm phát giá danh mục (chỉ số giá cố định giỏ)
    pi = prices.merge(pd.DataFrame({"item_id": ids.item_id, "cat": ids.cat_id}).drop_duplicates("item_id"), on="item_id")
    base = pi[pi.wm_yr_wk == pi.wm_yr_wk.min() + 0].groupby(["store_id", "item_id"]).sell_price.first()
    pidx = pi.groupby(["cat", "wm_yr_wk"]).sell_price.median().unstack(0)
    o["price_median"] = records(pidx.iloc[::4].reset_index().assign(wm_yr_wk=lambda d: d.wm_yr_wk.map(lambda x: str(wkd.get(x, pd.NaT).date()) if x in wkd else str(x))), 3)

    # tính gián đoạn (Syntetos–Boylan)
    log("M5: phân loại nhu cầu")
    cls = []
    for i in range(S.shape[0]):
        y = S[i]
        nz = np.nonzero(y)[0]
        if len(nz) < 2:
            cls.append("không đủ dữ liệu")
            continue
        y = y[nz[0]:]
        nzv = y[y > 0]
        adi = len(y) / len(nzv)
        cv2 = (nzv.std() / nzv.mean()) ** 2
        cls.append("Đều (smooth)" if adi < 1.32 and cv2 < 0.49 else "Thất thường (erratic)" if adi < 1.32 else "Gián đoạn (intermittent)" if cv2 < 0.49 else "Cục (lumpy)")
    cl = pd.DataFrame({"cls": cls, "cat": ids.cat_id, "rev": item_rev.reindex(range(len(ids))).fillna(0).values})
    o["demand_class"] = records(cl.groupby(["cat", "cls"]).agg(series=("cls", "size"), rev=("rev", "sum")).reset_index(), 0)
    o["zero_share_by_cat"] = {c: r((S[(ids.cat_id == c).values] == 0).mean()) for c in ["FOODS", "HOUSEHOLD", "HOBBIES"]}
    R["m5"] = o


if __name__ == "__main__":
    import sys
    parts = sys.argv[1:] or ["cj", "batf", "carbo", "lgsr", "m5"]
    resf = OUT / "results.json"
    if resf.exists():
        R.update(json.loads(resf.read_text(encoding="utf-8")))
    fn = {"cj": complete_journey, "batf": batf, "carbo": carbo, "lgsr": lgsr, "m5": m5}
    for p in parts:
        fn[p]()
        resf.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        log(f"xong {p}")
