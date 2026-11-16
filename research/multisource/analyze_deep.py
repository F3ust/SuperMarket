"""Phân tích chuyên sâu bổ sung → outputs/multisource/results_deep.json

Gồm: (1) CJ động lực khách hàng, RFM, phân rã tăng trưởng; (2) CJ luật kết hợp trên giỏ đầy đủ;
(3) BATF mua dồn sau khuyến mãi, khuyến mãi đối thủ, mô phỏng lợi nhuận, biên Lerner;
(4) M5 độ cứng giá, lạm phát giá, benchmark dự báo 28 ngày; (5) Carbo ma trận chuyển đổi thương hiệu.
Chạy: python3 research/multisource/analyze_deep.py [cj|batf|m5|carbo ...]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import analyze_multisource as A  # noqa: E402  (dùng chung kết nối duckdb, đường dẫn, hàm FE)

con, q, r, records, fe_ols = A.con, A.q, A.r, A.records, A.fe_ols
OUT = A.OUT
RESF = OUT / "results_deep.json"
D: dict = json.loads(RESF.read_text(encoding="utf-8")) if RESF.exists() else {}
T0 = time.time()


def log(m):
    print(f"[{time.time() - T0:6.0f}s] {m}", flush=True)


# ---------------------------------------------------------------- CJ
def cj():
    log("CJ: nạp")
    con.execute(f"""CREATE OR REPLACE TABLE cj AS SELECT * FROM read_csv('{A.CJ}/transaction_data.csv', header=true,
        types={{'BASKET_ID':'BIGINT','PRODUCT_ID':'BIGINT'}})""")
    con.execute(f"CREATE OR REPLACE TABLE cjp AS SELECT * FROM read_csv('{A.CJ}/product.csv', header=true, all_varchar=true)")
    con.execute("ALTER TABLE cjp ALTER PRODUCT_ID TYPE BIGINT")
    o = {}
    # Phân rã tăng trưởng theo kỳ 4 tuần: doanh thu = hộ hoạt động × chuyến/hộ × giá trị giỏ
    g = q("""SELECT ((WEEK_NO-1)//4)+1 AS p4, sum(SALES_VALUE) sales, count(DISTINCT household_key) hh,
        count(DISTINCT BASKET_ID) baskets FROM cj GROUP BY 1 ORDER BY 1""")
    g["trips_per_hh"] = g.baskets / g.hh
    g["aov"] = g.sales / g.baskets
    g["active_rate"] = g.hh / 2500
    o["periods"] = records(g, 3)
    # so sánh 6 kỳ cuối đủ (p4 20-25) với 6 kỳ đầu sau khởi động (p4 3-8): log decomposition
    a, b = g[g.p4.between(3, 8)], g[g.p4.between(20, 25)]
    dec = {}
    for k in ["sales", "hh", "trips_per_hh", "aov"]:
        dec[k] = r(np.log(b[k].mean() / a[k].mean()))
    o["growth_decomp"] = dec

    # Quỹ đạo hộ: nửa đầu (tuần 1–51) vs nửa sau (52–102)
    hh = q("""SELECT household_key, sum(CASE WHEN WEEK_NO<=51 THEN SALES_VALUE ELSE 0 END) h1,
        sum(CASE WHEN WEEK_NO>51 THEN SALES_VALUE ELSE 0 END) h2, max(DAY) last_day, min(DAY) first_day,
        count(DISTINCT BASKET_ID) baskets, sum(SALES_VALUE) total FROM cj GROUP BY 1""")
    hh = hh[hh.first_day <= 120]  # hộ có mặt từ đầu để so sánh công bằng
    hh["chg"] = (hh.h2 - hh.h1) / hh.h1.clip(lower=1)
    hh["traj"] = np.select([hh.last_day < 711 - 56, hh.chg > 0.2, hh.chg < -0.2], ["Rời bỏ (≥8 tuần không mua)", "Tăng chi (>+20%)", "Giảm chi (<−20%)"], "Ổn định (±20%)")
    tj = hh.groupby("traj").agg(households=("household_key", "size"), h1=("h1", "sum"), h2=("h2", "sum"), total=("total", "sum")).reset_index()
    tj["delta"] = tj.h2 - tj.h1
    o["trajectory"] = records(tj, 0)
    o["trajectory_n"] = int(len(hh))
    # Ngành nào kéo tăng/giảm cho từng nhóm
    con.register("hhtraj", hh[["household_key", "traj"]])
    dd = q("""SELECT t.traj, coalesce(p.DEPARTMENT,'?') dept, sum(CASE WHEN WEEK_NO<=51 THEN SALES_VALUE ELSE 0 END) h1,
        sum(CASE WHEN WEEK_NO>51 THEN SALES_VALUE ELSE 0 END) h2 FROM cj JOIN hhtraj t USING(household_key)
        LEFT JOIN cjp p USING(PRODUCT_ID) GROUP BY 1,2""")
    dd["delta"] = dd.h2 - dd.h1
    top_depts = dd.groupby("dept").h1.sum().nlargest(8).index
    dd = dd[dd.dept.isin(top_depts)]
    o["trajectory_dept"] = records(dd, 0)

    # RFM tại ngày 711
    log("CJ: RFM")
    rfm = q("""SELECT household_key, 711-max(DAY) recency, count(DISTINCT BASKET_ID) frequency, sum(SALES_VALUE) monetary FROM cj GROUP BY 1""")
    rfm["R"] = pd.qcut(rfm.recency.rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm.frequency.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm.monetary.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    fm = (rfm.F + rfm.M) / 2

    def seg(row_r, row_fm):
        if row_r >= 4 and row_fm >= 4:
            return "Nhà vô địch"
        if row_r >= 3 and row_fm >= 3:
            return "Trung thành"
        if row_r >= 4 and row_fm < 3:
            return "Mới / tiềm năng"
        if row_r <= 2 and row_fm >= 4:
            return "Có nguy cơ mất (giá trị cao)"
        if row_r <= 2 and row_fm >= 2.5:
            return "Cần chăm sóc"
        if row_r == 3:
            return "Ngủ đông nhẹ"
        return "Đã ngủ đông"

    rfm["segment"] = [seg(a_, b_) for a_, b_ in zip(rfm.R, fm)]
    sg = rfm.groupby("segment").agg(households=("household_key", "size"), monetary=("monetary", "sum"), recency=("recency", "median"),
                                    frequency=("frequency", "median"), avg_m=("monetary", "mean")).reset_index()
    sg["hh_share"] = sg.households / sg.households.sum()
    sg["rev_share"] = sg.monetary / sg.monetary.sum()
    o["rfm"] = records(sg.sort_values("rev_share", ascending=False), 4)
    o["rfm_grid"] = records(rfm.groupby(["R", "F"]).agg(n=("household_key", "size"), m=("monetary", "mean")).reset_index(), 1)

    # Luật kết hợp trên giỏ đầy đủ (COMMODITY)
    log("CJ: luật kết hợp")
    con.execute("""CREATE OR REPLACE TABLE bc AS SELECT DISTINCT BASKET_ID b, p.COMMODITY_DESC c FROM cj JOIN cjp p USING(PRODUCT_ID)
        WHERE QUANTITY>0 AND SALES_VALUE>0 AND p.DEPARTMENT NOT IN ('KIOSK-GAS','MISC SALES TRAN','MISC. TRANS.')
        AND p.COMMODITY_DESC NOT IN ('NO COMMODITY DESCRIPTION','COUPON/MISC ITEMS','')""")
    N = int(q("SELECT count(DISTINCT b) n FROM bc")["n"][0])
    cnt = q("SELECT c, count(*) n FROM bc GROUP BY 1 ORDER BY n DESC")
    top = cnt.head(60)
    con.register("topc", top[["c"]])
    pairs = q("""WITH x AS (SELECT bc.* FROM bc JOIN topc USING(c)) SELECT a.c a, b.c b, count(*) n FROM x a JOIN x b ON a.b=b.b AND a.c<b.c GROUP BY 1,2 HAVING count(*)>=1000""")
    nb = cnt.set_index("c").n
    pairs["support"] = pairs.n / N
    pairs["conf_a_b"] = pairs.n / pairs.a.map(nb)
    pairs["conf_b_a"] = pairs.n / pairs.b.map(nb)
    pairs["lift"] = pairs.n * N / (pairs.a.map(nb) * pairs.b.map(nb))
    o["rules_top_lift"] = records(pairs.sort_values("lift", ascending=False).head(15))
    o["rules_top_support"] = records(pairs.sort_values("support", ascending=False).head(10))
    o["baskets_n"] = N
    o["commodity_top"] = records(top.head(15).assign(share=lambda d: d.n / N))
    # Đối chiếu Carbo: mì Ý + sốt trong giỏ đầy đủ
    pc = q("""WITH x AS (SELECT b, max(CASE WHEN c='DRY NOODLES/PASTA' THEN 1 ELSE 0 END) pa, max(CASE WHEN c='PASTA SAUCE' THEN 1 ELSE 0 END) sa FROM bc GROUP BY 1)
        SELECT count(*) n, sum(pa) pa, sum(sa) sa, sum(pa*sa) AS bothn FROM x""").iloc[0]
    o["pasta_sauce_full"] = {"lift": r(pc.bothn * pc.n / (pc.pa * pc.sa)), "conf_sauce_given_pasta": r(pc.bothn / pc.pa), "conf_pasta_given_sauce": r(pc.bothn / pc.sa),
                             "support": r(pc.bothn / pc.n, 5), "baskets": int(pc.n)}
    D["cj"] = o


# ---------------------------------------------------------------- BATF
def batf():
    log("BATF: động thái khuyến mãi")
    tx = pd.read_parquet(A.CACHE / "batf.parquet")
    pr = pd.read_parquet(A.CACHE / "batf_dh_Products_Lookup.parquet")
    tx = tx.merge(pr[["UPC", "CATEGORY", "MANUFACTURER"]], on="UPC")
    tx = tx[(tx.UNITS > 0) & (tx.PRICE > 0) & (tx.BASE_PRICE > 0)].copy()
    tx = tx.sort_values(["STORE_NUM", "UPC", "WEEK_END_DATE"])
    tx["key"] = tx.STORE_NUM.astype(str) + "_" + tx.UPC.astype(str)
    tx["wk"] = tx.WEEK_END_DATE.dt.strftime("%Y%m%d")
    tx["ly"] = np.log(tx.UNITS)
    tx["lp"] = np.log(tx.PRICE)
    tx["promo"] = ((tx.FEATURE + tx.DISPLAY + tx.TPR_ONLY) > 0).astype(float)
    grp = tx.groupby("key")
    gap = grp.WEEK_END_DATE.diff().dt.days
    for L in (1, 2):
        tx[f"promo_l{L}"] = grp.promo.shift(L)
        tx[f"lp_l{L}"] = grp.lp.shift(L)
    tx["consec"] = (gap == 7) & (grp.WEEK_END_DATE.diff(2).dt.days == 14)
    # khuyến mãi của đối thủ trong cùng ngành-cửa hàng-tuần
    cs = tx.groupby(["STORE_NUM", "CATEGORY", "WEEK_END_DATE"]).agg(cat_promo=("promo", "sum"), cat_n=("promo", "size")).reset_index()
    tx = tx.merge(cs, on=["STORE_NUM", "CATEGORY", "WEEK_END_DATE"])
    tx["rival_promo"] = (tx.cat_promo - tx.promo) / (tx.cat_n - 1).clip(lower=1)
    sub = tx[tx.consec].dropna(subset=["promo_l1", "promo_l2"]).copy()
    for c in ["FEATURE", "DISPLAY", "TPR_ONLY"]:
        sub[c] = sub[c].astype(float)
    out = []
    for cat, g in sub.groupby("CATEGORY"):
        e = fe_ols(g, "ly", ["lp", "FEATURE", "DISPLAY", "TPR_ONLY", "promo_l1", "promo_l2", "rival_promo"], ["key", "wk"], cluster="key")
        out.append({"category": cat, "n": e["n"], **{f"{k}": e[k]["coef"] for k in ["lp", "promo_l1", "promo_l2", "rival_promo"]},
                    **{f"{k}_se": e[k]["se"] for k in ["promo_l1", "promo_l2", "rival_promo"]}})
    o = {"dynamics": out}
    # Mô phỏng lợi nhuận khi giảm giá 10/20/30% với biên gộp giả định
    el = {e["category"]: e for e in A.json.loads((OUT / "results.json").read_text(encoding="utf-8"))["batf"]["elasticity_category"]}
    sim = []
    for cat, e in el.items():
        dyn = next(x for x in out if x["category"] == cat)
        for m in (0.20, 0.30, 0.40):
            for cut in (0.10, 0.20, 0.30):
                q1 = (1 - cut) ** e["elasticity"]  # chỉ hiệu ứng giá, không tờ rơi/trưng bày
                q_disp = q1 * (1 + e["lift_display"])
                prof0 = m
                prof1 = (1 - cut - (1 - m)) * q1
                prof1d = (1 - cut - (1 - m)) * q_disp
                # trừ mua dồn: 2 tuần sau giảm theo hệ số trễ
                dip = np.exp(dyn["promo_l1"]) - 1 + np.exp(dyn["promo_l2"]) - 1
                sim.append({"category": cat, "margin": m, "cut": cut, "units_mult": r(q1), "profit_change_price_only": r(prof1 / prof0 - 1),
                            "profit_change_with_display": r(prof1d / prof0 - 1), "post_dip_weeks": r(dip),
                            "profit_change_net_dip": r((prof1d + prof0 * dip) / prof0 - 1)})
    o["profit_sim"] = sim
    o["lerner"] = [{"category": c, "elasticity": e["elasticity"], "implied_margin": r(1 / abs(e["elasticity"]))} for c, e in el.items()]
    # biên hòa vốn: giảm 20% giá có lãi khi m < m* : (m-0.2)q1 = m → m* = 0.2 q1/(q1-1)
    for x in o["lerner"]:
        q1 = 0.8 ** el[x["category"]]["elasticity"]
        x["breakeven_margin_20pct_cut"] = r(0.2 * q1 / (q1 - 1)) if q1 > 1 else None
    D["batf"] = o


# ---------------------------------------------------------------- M5
def m5():
    log("M5: giá")
    prices = pd.read_csv(A.M5 / "sell_prices.csv")
    cal = pd.read_csv(A.M5 / "calendar.csv", parse_dates=["date"])
    wkdate = cal.groupby("wm_yr_wk").date.min()
    prices["cat"] = prices.item_id.str.split("_").str[0]
    prices = prices.sort_values(["store_id", "item_id", "wm_yr_wk"])
    g = prices.groupby(["store_id", "item_id"]).sell_price
    prices["chg"] = g.diff()
    prices["pct"] = prices.chg / g.shift(1)
    prices["year"] = prices.wm_yr_wk.map(wkdate).dt.year
    v = prices.dropna(subset=["chg"])
    o = {}
    o["price_change_freq"] = records(v.assign(changed=v.chg.abs() > 0.005).groupby("cat").agg(
        freq=("changed", "mean"), up=("pct", lambda s: (s > 0.005).mean()), down=("pct", lambda s: (s < -0.005).mean())).reset_index())
    ch = v[v.chg.abs() > 0.005]
    o["price_change_size"] = records(ch.groupby("cat").pct.agg(median_abs=lambda s: s.abs().median(), mean_up=lambda s: s[s > 0].mean(),
                                                                 mean_down=lambda s: s[s < 0].mean()).reset_index())
    o["duration_weeks"] = {c: r(1 / f) for c, f in v.assign(changed=v.chg.abs() > 0.005).groupby("cat").changed.mean().items()}
    bins = [-1, -0.3, -0.2, -0.1, -0.05, -0.005, 0.005, 0.05, 0.1, 0.2, 0.3, 5]
    lab = ["≤−30%", "−30…−20%", "−20…−10%", "−10…−5%", "−5…0%", "0", "0…5%", "5…10%", "10…20%", "20…30%", ">30%"]
    hist = ch.assign(b=pd.cut(ch.pct, bins, labels=lab)).groupby("b", observed=False).size()
    o["price_change_hist"] = [{"bin": str(k), "n": int(v_)} for k, v_ in hist.items() if k != "0"]
    # chỉ số giá cố định giỏ: trung bình log giá tương đối so với tuần đầu xuất hiện, cùng item-store
    prices["lp"] = np.log(prices.sell_price)
    prices["lp0"] = g.transform(lambda s: np.log(s.iloc[0]))
    yr = prices.groupby(["cat", "year"]).apply(lambda d: np.exp((d.lp - d.lp0).mean()), include_groups=False).unstack(0)
    # lạm phát hằng năm theo chuỗi liên kết: thay đổi giá trung bình của cùng item-store giữa các năm
    ys = prices.groupby(["store_id", "item_id", "cat", "year"]).lp.mean().reset_index()
    ys["dlp"] = ys.groupby(["store_id", "item_id"]).lp.diff()
    ys["dy"] = ys.groupby(["store_id", "item_id"]).year.diff()
    infl = ys[ys.dy == 1].groupby(["cat", "year"]).dlp.mean().unstack(0).apply(np.expm1)
    o["inflation"] = records(infl.reset_index(), 4)
    o["price_level"] = records(yr.reset_index(), 4)

    # Benchmark dự báo 28 ngày (d_1914–d_1941)
    log("M5: benchmark dự báo")
    sales = pd.read_csv(A.M5 / "sales_train_evaluation.csv")
    ids = sales.iloc[:, :6].copy()
    dcols = [c for c in sales.columns if c.startswith("d_")]
    S = sales[dcols].to_numpy(dtype=np.float32)
    del sales
    H = 28
    T = S.shape[1]
    tr, te = S[:, : T - H], S[:, T - H:]
    cal = cal.iloc[:T].reset_index(drop=True)
    # trọng số doanh thu 28 ngày cuối train (như M5)
    last_wk = cal.wm_yr_wk.values[T - H - 28: T - H]
    pr_last = prices[prices.wm_yr_wk.isin(np.unique(last_wk))].groupby(["store_id", "item_id"]).sell_price.mean()
    pidx = pd.MultiIndex.from_arrays([ids.store_id, ids.item_id])
    price_vec = pr_last.reindex(pidx).fillna(0).values
    w = tr[:, -28:].sum(1) * price_vec
    w = w / w.sum()
    # mẫu số RMSSE: sai số naive 1 bước trên train từ ngày bán đầu tiên
    first = np.argmax(tr > 0, axis=1)
    scale = np.zeros(len(tr))
    for i in range(len(tr)):
        y = tr[i, first[i]:]
        scale[i] = np.mean(np.diff(y) ** 2) if len(y) > 1 else np.nan
    scale = np.where((scale > 0) & np.isfinite(scale), scale, np.nan)

    def score(F):
        mse = ((F - te) ** 2).mean(1)
        rmsse = np.sqrt(mse / scale)
        ok = np.isfinite(rmsse)
        return {"wrmsse_item": r(np.nansum(rmsse[ok] * w[ok]) / w[ok].sum()), "wape": r(np.abs(F - te).sum() / te.sum()),
                "bias": r(F.sum() / te.sum() - 1), "rmse_total_daily": r(np.sqrt(((F.sum(0) - te.sum(0)) ** 2).mean()), 1)}

    models = {}
    models["Naive (ngày cuối)"] = np.repeat(tr[:, -1:], H, 1)
    models["Naive mùa vụ 7 ngày"] = np.tile(tr[:, -7:], 4)
    models["Trung bình 28 ngày"] = np.repeat(tr[:, -28:].mean(1, keepdims=True), H, 1)
    # trung bình theo thứ trong 8 tuần cuối
    last56 = tr[:, -56:].reshape(len(tr), 8, 7).mean(1)
    models["TB theo thứ, 8 tuần"] = np.tile(last56, 4)
    # GBM toàn cục, dự báo trực tiếp với độ trễ ≥ 28
    log("M5: huấn luyện GBM")
    from sklearn.ensemble import HistGradientBoostingRegressor
    wd = cal.wday.values
    mo = cal.month.values
    ev = cal.event_name_1.notna().values.astype(np.int8)
    snapm = np.stack([cal[f"snap_{s}"].values for s in ["CA", "TX", "WI"]])
    st_state = ids.state_id.map({"CA": 0, "TX": 1, "WI": 2}).values
    dept = pd.factorize(ids.dept_id)[0]
    store = pd.factorize(ids.store_id)[0]
    # giá ngày
    pw = prices.set_index(["store_id", "item_id", "wm_yr_wk"]).sell_price
    wk_u = np.unique(cal.wm_yr_wk.values)
    P = pw.unstack("wm_yr_wk").reindex(pidx).reindex(columns=wk_u)
    P = P.ffill(axis=1).bfill(axis=1).values.astype(np.float32)
    wk_idx = np.searchsorted(wk_u, cal.wm_yr_wk.values)
    Pd = P[:, wk_idx]
    pref = np.nanmean(P, axis=1, keepdims=True)
    cs = np.concatenate([np.zeros((len(S), 1), np.float32), np.cumsum(S, 1)], 1)

    def feats(day_idx, rows):
        d = day_idx
        f = {
            "lag28": S[rows, d - 28], "lag35": S[rows, d - 35], "lag42": S[rows, d - 42], "lag364": S[rows, d - 364],
            "rm7": (cs[rows, d - 27] - cs[rows, d - 34]) / 7, "rm28": (cs[rows, d - 27] - cs[rows, d - 55]) / 28,
            "rm91": (cs[rows, d - 27] - cs[rows, d - 118]) / 91, "price": Pd[rows, d], "price_rel": Pd[rows, d] / pref[rows, 0],
            "price_chg": Pd[rows, d] / Pd[rows, d - 28] - 1, "wday": np.full(len(rows), wd[d]), "month": np.full(len(rows), mo[d]),
            "event": np.full(len(rows), ev[d]), "snap": snapm[st_state[rows], d], "dept": dept[rows], "store": store[rows],
            "dom": np.full(len(rows), cal.date.dt.day.values[d]),
        }
        return pd.DataFrame(f)

    rng = np.random.default_rng(0)
    train_days = np.arange(T - H - 420, T - H)
    Xs, ys_ = [], []
    for d in train_days:
        rows = rng.choice(len(S), 6000, replace=False)
        rows = rows[first[rows] < d - 60]
        Xs.append(feats(d, rows))
        ys_.append(S[rows, d])
    X = pd.concat(Xs, ignore_index=True)
    y = np.concatenate(ys_)
    gbm = HistGradientBoostingRegressor(loss="poisson", max_iter=400, learning_rate=0.06, max_leaf_nodes=63, min_samples_leaf=100,
                                        categorical_features=[X.columns.get_loc(c) for c in ["dept", "store"]], random_state=0)
    gbm.fit(X, y)
    F = np.zeros_like(te)
    allrows = np.arange(len(S))
    for h in range(H):
        F[:, h] = gbm.predict(feats(T - H + h, allrows))
    models["GBM toàn cục (Poisson)"] = F
    o["forecast"] = [{"model": k, **score(v_)} for k, v_ in models.items()]
    o["forecast_train_rows"] = int(len(X))
    o["forecast_total"] = {"actual": te.sum(0).round(0).tolist(), "dates": cal.date.iloc[T - H:].dt.strftime("%Y-%m-%d").tolist(),
                           **{k: v_.sum(0).round(0).tolist() for k, v_ in models.items()}}
    # tầm quan trọng (permutation nhanh trên mẫu)
    from sklearn.inspection import permutation_importance
    Xv = feats(T - H + 3, rng.choice(len(S), 8000, replace=False))
    yv = te[:, 3][Xv.index] if False else None
    rows = rng.choice(len(S), 8000, replace=False)
    Xv = feats(T - H + 3, rows)
    yv = te[rows, 3]
    pi = permutation_importance(gbm, Xv, yv, n_repeats=3, random_state=0, scoring="neg_mean_squared_error")
    o["forecast_importance"] = sorted([{"feature": c, "importance": r(m_)} for c, m_ in zip(Xv.columns, pi.importances_mean)], key=lambda x: -x["importance"])
    # sai số theo ngành
    by = []
    for c in ["FOODS", "HOUSEHOLD", "HOBBIES"]:
        m_ = (ids.cat_id == c).values
        for k in ["Naive mùa vụ 7 ngày", "TB theo thứ, 8 tuần", "GBM toàn cục (Poisson)"]:
            by.append({"cat": c, "model": k, "wape": r(np.abs(models[k][m_] - te[m_]).sum() / te[m_].sum())})
    o["forecast_by_cat"] = by
    D["m5"] = o


# ---------------------------------------------------------------- Carbo
def carbo():
    log("Carbo: chuyển đổi thương hiệu")
    con.execute(f"CREATE OR REPLACE TABLE cl AS SELECT * FROM read_csv('{A.CL}/dh_transactions.csv', header=true)")
    con.execute(f"CREATE OR REPLACE TABLE clp AS SELECT * FROM read_csv('{A.CL}/dh_product_lookup.csv', header=true, all_varchar=true)")
    con.execute("ALTER TABLE clp ALTER upc TYPE BIGINT")
    o = {}
    for comm in ["pasta sauce", "pasta"]:
        tb = q(f"""WITH b AS (SELECT p.brand, sum(dollar_sales) s FROM cl JOIN clp p USING(upc) WHERE p.commodity='{comm}' GROUP BY 1 ORDER BY s DESC LIMIT 5),
            t AS (SELECT household, basket, day, CASE WHEN p.brand IN (SELECT brand FROM b) THEN p.brand ELSE 'Khác' END br
                  FROM cl JOIN clp p USING(upc) WHERE p.commodity='{comm}'),
            tt AS (SELECT household, basket, min(day) AS d0, mode(br) br FROM t GROUP BY 1,2),
            s AS (SELECT household, br, lead(br) OVER (PARTITION BY household ORDER BY d0, basket) nxt FROM tt)
            SELECT br "from", nxt "to", count(*) n FROM s WHERE nxt IS NOT NULL GROUP BY 1,2""")
        m = tb.pivot(index="from", columns="to", values="n").fillna(0)
        m = m.div(m.sum(1), axis=0)
        order = list(m.sum(0).sort_values(ascending=False).index)
        m = m.reindex(index=order, columns=order)
        o[comm] = {"brands": order, "matrix": [[r(x) for x in row] for row in m.values], "repeat": {b: r(m.loc[b, b]) for b in order}}
        # thị phần dài hạn ngụ ý (vector riêng của ma trận chuyển)
        vals, vecs = np.linalg.eig(m.values.T)
        st_ = np.real(vecs[:, np.argmin(np.abs(vals - 1))])
        o[comm]["steady_share"] = {b: r(s_ / st_.sum()) for b, s_ in zip(order, st_)}
        cur = q(f"""SELECT CASE WHEN p.brand IN ({",".join("'" + b.replace("'", "''") + "'" for b in order if b != "Khác")}) THEN p.brand ELSE 'Khác' END br,
            count(DISTINCT basket) n FROM cl JOIN clp p USING(upc) WHERE p.commodity='{comm}' GROUP BY 1""").set_index("br").n
        o[comm]["current_share"] = {b: r(cur.get(b, 0) / cur.sum()) for b in order}
    D["carbo"] = o


if __name__ == "__main__":
    parts = sys.argv[1:] or ["cj", "batf", "carbo", "m5"]
    fn = {"cj": cj, "batf": batf, "m5": m5, "carbo": carbo}
    for p_ in parts:
        fn[p_]()
        RESF.write_text(json.dumps(D, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        log(f"xong {p_}")
