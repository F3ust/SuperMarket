"""Mô phỏng giá và khuyến mãi dựa trên các hệ số đã ước lượng.

Mô hình log–log: lượng mới = lượng cũ × (giá mới/giá cũ)^e × (1 + hiệu ứng trưng bày) × (1 + hiệu ứng tờ rơi)
× (1 + ăn mòn do đối thủ khuyến mãi)^tỷ lệ đối thủ. Lợi nhuận so với không khuyến mãi tính trên mỗi đồng doanh thu gốc.
"""
from __future__ import annotations

import math

from .data import results, results_deep


def _batf():
    el = {e["category"]: e for e in results()["batf"]["elasticity_category"]}
    dyn = {d["category"]: d for d in results_deep()["batf"]["dynamics"]}
    return el, dyn


def categories() -> list[dict]:
    el, dyn = _batf()
    return [{"category": c, "elasticity": e["elasticity"], "ci_low": e["ci_low"], "ci_high": e["ci_high"],
             "lift_feature": e["lift_feature"], "lift_display": e["lift_display"], "rival_effect": math.expm1(dyn[c]["rival_promo"]),
             "post_week_effect": math.expm1(dyn[c]["promo_l1"]) + math.expm1(dyn[c]["promo_l2"]),
             "implied_margin": 1 / abs(e["elasticity"])} for c, e in el.items()]


def promotion(category: str, margin: float, cut: float, display: bool, feature: bool, rival_share: float, include_post: bool) -> dict:
    el, dyn = _batf()
    if category not in el:
        raise KeyError(category)
    e, d = el[category], dyn[category]

    def run(cut_, elas):
        q = (1 - cut_) ** elas
        if display:
            q *= 1 + e["lift_display"]
        if feature:
            q *= 1 + e["lift_feature"]
        q *= math.exp(d["rival_promo"] * rival_share)
        profit = (margin - cut_) * q
        if include_post:
            profit += margin * (math.expm1(d["promo_l1"]) + math.expm1(d["promo_l2"]))
        revenue = (1 - cut_) * q
        return q, revenue - 1, profit / margin - 1

    q, rev, prof = run(cut, e["elasticity"])
    _, _, prof_lo = run(cut, e["ci_high"])   # co giãn yếu hơn → lợi nhuận thấp hơn
    _, _, prof_hi = run(cut, e["ci_low"])
    curve = []
    for i in range(0, 41):
        c = i / 100
        qq, rr, pp = run(c, e["elasticity"])
        curve.append({"cut": c, "units_mult": qq, "revenue_change": rr, "profit_change": pp})
    best = max(curve, key=lambda x: x["profit_change"])
    q_price_only = (1 - cut) ** e["elasticity"]
    breakeven = cut * q_price_only / (q_price_only - 1) if q_price_only > 1 else None
    return {"category": category, "elasticity": e["elasticity"], "units_mult": q, "revenue_change": rev, "profit_change": prof,
            "profit_change_range": [min(prof_lo, prof_hi), max(prof_lo, prof_hi)], "best_cut": best["cut"], "best_profit_change": best["profit_change"],
            "breakeven_margin_price_only": breakeven, "curve": curve}


def price(source: str, category: str, change: float) -> dict:
    r = results()
    rows = {"batf": {e["category"]: e for e in r["batf"]["elasticity_category"]},
            "carbo": {e["commodity"]: e for e in r["carbo"]["elasticity"]},
            "m5": {e["cat"]: e for e in r["m5"]["elasticity"]}}
    if source not in rows or category not in rows[source]:
        raise KeyError(f"{source}/{category}")
    e = rows[source][category]
    f = 1 + change

    def at(elas):
        q = f ** elas
        return q - 1, f * q - 1

    u, rv = at(e["elasticity"])
    u_a, rv_a = at(e["ci_low"])
    u_b, rv_b = at(e["ci_high"])
    return {"source": source, "category": category, "elasticity": e["elasticity"], "ci": [e["ci_low"], e["ci_high"]],
            "units_change": u, "units_range": sorted([u_a, u_b]), "revenue_change": rv, "revenue_range": sorted([rv_a, rv_b])}


def price_options() -> dict:
    r = results()
    return {"batf": [e["category"] for e in r["batf"]["elasticity_category"]],
            "carbo": [e["commodity"] for e in r["carbo"]["elasticity"]],
            "m5": [e["cat"] for e in r["m5"]["elasticity"]]}
