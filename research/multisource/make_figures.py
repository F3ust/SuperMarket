"""Vẽ biểu đồ PNG cho báo cáo Word từ outputs/multisource/results.json."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "multisource"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)
R = json.loads((OUT / "results.json").read_text(encoding="utf-8"))

INK = "#16302a"
MUTED = "#6b7a74"
GRID = "#e3e8e4"
PAL = ["#1f5c4a", "#d08a2c", "#4f7fa8", "#a8483f", "#7d6aa6", "#6f9b5a", "#c2a14a"]
SRC = {"cj": "#1f5c4a", "batf": "#d08a2c", "carbo": "#a8483f", "lgsr": "#7d6aa6", "m5": "#4f7fa8"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": GRID, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.titleweight": "bold", "axes.titlesize": 11, "axes.titlecolor": INK, "axes.titlelocation": "left",
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 160, "savefig.bbox": "tight", "legend.frameon": False,
})


def save(fig, name):
    fig.savefig(FIG / name, facecolor="white")
    plt.close(fig)


def pct(x, d=0):
    return f"{x * 100:.{d}f}%"


# 1. Lorenz đa nguồn
def lorenz():
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    series = [("CJ – hộ", R["cj"]["pareto_households"], SRC["cj"]), ("CJ – sản phẩm", R["cj"]["pareto_products"], "#7fb09d"),
              ("Carbo – hộ", R["carbo"]["pareto_households"], SRC["carbo"]), ("LGSR – khách", R["lgsr"]["pareto_customers"], SRC["lgsr"]),
              ("M5 – mặt hàng", R["m5"]["pareto_items"], SRC["m5"])]
    for name, p, c in series:
        x = [0] + [pt["pop"] for pt in p["curve"]]
        y = [0] + [pt["share"] for pt in p["curve"]]
        ax.plot(x, y, color=c, lw=2, label=f"{name} (top 20% = {pct(p['top20'])}, Gini {p['gini']:.2f})")
    ax.plot([0, 1], [0, 1], color=MUTED, ls=":", lw=1)
    ax.axvline(0.2, color=GRID, lw=1.2)
    ax.set_xlabel("Tỷ lệ tích lũy khách/mặt hàng (xếp từ lớn đến nhỏ)")
    ax.set_ylabel("Tỷ lệ tích lũy doanh thu")
    ax.xaxis.set_major_formatter(lambda v, _: pct(v))
    ax.yaxis.set_major_formatter(lambda v, _: pct(v))
    ax.legend(fontsize=7.8, loc="lower right")
    ax.set_title("Mức tập trung doanh thu ở 5 góc nhìn")
    save(fig, "f01_lorenz.png")


# 2. Forest plot co giãn giá
def forest():
    rows = []
    for e in R["batf"]["elasticity_category"]:
        rows.append(("BATF · " + e["category"].title(), e["elasticity"], e["ci_low"], e["ci_high"], SRC["batf"]))
    for e in R["carbo"]["elasticity"]:
        rows.append(("Carbo · " + e["commodity"].title(), e["elasticity"], e["ci_low"], e["ci_high"], SRC["carbo"]))
    for e in R["m5"]["elasticity"]:
        rows.append(("M5 · " + e["cat"].title(), e["elasticity"], e["ci_low"], e["ci_high"], SRC["m5"]))
    rows = rows[::-1]
    fig, ax = plt.subplots(figsize=(6.6, 0.36 * len(rows) + 1))
    for i, (n, v, lo, hi, c) in enumerate(rows):
        ax.plot([lo, hi], [i, i], color=c, lw=2.2, solid_capstyle="round")
        ax.scatter([v], [i], color=c, s=36, zorder=3)
        ax.text(hi + 0.08, i, f"{v:.2f}", va="center", fontsize=8, color=INK)
    ax.axvline(-1, color=MUTED, ls="--", lw=1)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.text(-1, len(rows) - 0.3, " co giãn đơn vị (−1)", fontsize=7.5, color=MUTED)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.set_xlabel("Độ co giãn của lượng bán theo giá (log–log, hiệu ứng cố định)")
    ax.set_title("Khách phản ứng với giá mạnh đến đâu?")
    ax.grid(axis="y", visible=False)
    save(fig, "f02_elasticity.png")


# 3. BATF co giãn theo phân khúc cửa hàng
def batf_segment():
    d = pd.DataFrame(R["batf"]["elasticity_segment"])
    cats = sorted(d.category.unique())
    segs = ["VALUE", "MAINSTREAM", "UPSCALE"]
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    w = 0.26
    for j, s in enumerate(segs):
        vals = [d[(d.category == c) & (d.segment == s)].elasticity.mean() for c in cats]
        ax.bar(np.arange(len(cats)) + (j - 1) * w, vals, w, label=s.title(), color=PAL[j])
    ax.set_xticks(range(len(cats)), [c.title() for c in cats], fontsize=8.5)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_ylabel("Độ co giãn giá")
    ax.legend(ncol=3, fontsize=8)
    ax.set_title("Co giãn giá theo phân khúc cửa hàng (Breakfast at the Frat)")
    save(fig, "f03_batf_segment.png")


# 4. Hiệu ứng khuyến mãi
def promo():
    rows = []
    cl = R["cj"]["causal_lift"]
    rows += [("CJ · Trưng bày", cl["lift_display"], SRC["cj"]), ("CJ · Tờ rơi", cl["lift_mailer"], SRC["cj"]), ("CJ · Cả hai", cl["lift_both"], SRC["cj"])]
    for e in R["batf"]["elasticity_category"]:
        n = e["category"].title()
        rows += [(f"BATF · {n} · Feature", e["lift_feature"], SRC["batf"]), (f"BATF · {n} · Display", e["lift_display"], SRC["batf"]),
                 (f"BATF · {n} · TPR", e["lift_tpr"], "#e7b878")]
    for e in R["carbo"]["elasticity"]:
        n = e["commodity"].title()
        rows += [(f"Carbo · {n} · Feature", e["lift_feature"], SRC["carbo"]), (f"Carbo · {n} · Display", e["lift_display"], "#d38c84")]
    rows = rows[::-1]
    fig, ax = plt.subplots(figsize=(6.6, 0.27 * len(rows) + 1))
    ax.barh(range(len(rows)), [r[1] for r in rows], color=[r[2] for r in rows], height=0.7)
    for i, r in enumerate(rows):
        ax.text(r[1] + (0.01 if r[1] >= 0 else -0.01), i, pct(r[1]), va="center", ha="left" if r[1] >= 0 else "right", fontsize=7.4, color=INK)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=7.6)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.xaxis.set_major_formatter(lambda v, _: pct(v))
    ax.set_xlim(-0.22, None)
    ax.set_xlabel("Mức tăng lượng bán khi có hoạt động (đã giữ giá cố định ở BATF/Carbo)")
    ax.set_title("Trưng bày và tờ rơi tạo thêm bao nhiêu lượng bán?")
    ax.grid(axis="y", visible=False)
    save(fig, "f04_promo.png")


# 5. SNAP
def snap():
    d = pd.DataFrame(R["m5"]["snap"])
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw={"width_ratios": [1, 1.4]})
    ax = axes[0]
    cats = ["FOODS", "HOUSEHOLD", "HOBBIES"]
    for j, c in enumerate(cats):
        sub = d[d.cat == c].set_index("state").reindex(["CA", "TX", "WI"])
        ax.bar(np.arange(3) + (j - 1) * 0.26, sub.lift, 0.26, color=PAL[j], label=c.title(),
               yerr=[sub.lift - sub.ci_low, sub.ci_high - sub.lift], error_kw={"lw": 0.8, "ecolor": MUTED})
    ax.set_xticks(range(3), ["CA", "TX", "WI"])
    ax.yaxis.set_major_formatter(lambda v, _: pct(v))
    ax.legend(fontsize=7.5)
    ax.set_title("Ngày SNAP: mức tăng lượng bán")
    ax = axes[1]
    dm = pd.DataFrame(R["m5"]["day_of_month"])
    for j, s in enumerate(["CA", "TX", "WI"]):
        ax.plot(dm.dom, dm[f"{s}_idx"], color=PAL[j], lw=1.8, label=s)
    ax.axhline(1, color=MUTED, lw=0.8)
    ax.set_xlabel("Ngày trong tháng")
    ax.set_ylabel("Chỉ số so với TB tháng")
    ax.legend(fontsize=7.5, ncol=3)
    ax.set_title("Nhịp chi tiêu theo ngày trong tháng (M5)")
    fig.tight_layout()
    save(fig, "f05_snap.png")


# 6. Sự kiện
def events():
    d = pd.DataFrame(R["m5"]["events"]).sort_values("lift")
    fig, ax = plt.subplots(figsize=(6.6, 0.22 * len(d) + 1))
    col = {"National": PAL[0], "Religious": PAL[4], "Cultural": PAL[1], "Sporting": PAL[2]}
    ax.barh(range(len(d)), d.lift, color=[col.get(t, MUTED) for t in d.type], height=0.72)
    ax.set_yticks(range(len(d)), d.event, fontsize=7.4)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.xaxis.set_major_formatter(lambda v, _: pct(v))
    ax.set_title("Ngày lễ/sự kiện so với cùng thứ tuần trước và sau (M5)")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=v, label=k) for k, v in col.items()], fontsize=7.5, loc="lower right")
    ax.grid(axis="y", visible=False)
    save(fig, "f06_events.png")


# 7. Thu nhập vs chi tiêu và nhãn riêng (CJ)
def income():
    d = pd.DataFrame(R["cj"]["demo_income"])
    d = d[d.level.str.startswith("Level")]
    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    x = d.level.str.replace("Level", "").astype(int)
    ax.bar(x, d.weekly_spend, color=SRC["cj"], alpha=0.85, label="Chi tiêu/tuần (trung vị, USD)")
    ax.set_xlabel("Bậc thu nhập (Level1 thấp → Level12 cao, mã hóa thứ bậc)")
    ax.set_ylabel("USD/tuần")
    for xi, n in zip(x, d.households):
        ax.text(xi, 1, f"n={n}", ha="center", fontsize=6.5, color="white", rotation=90, va="bottom")
    ax2 = ax.twinx()
    ax2.plot(x, d.pl_share, color=PAL[1], lw=2.2, marker="o", label="Tỷ trọng nhãn riêng")
    ax2.yaxis.set_major_formatter(lambda v, _: pct(v))
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    ax.set_xticks(range(1, 13))
    ax.set_title("Thu nhập cao hơn → chi nhiều hơn, ít nhãn riêng hơn? (CJ, 801 hộ)")
    save(fig, "f07_income.png")


# 8. LGSR heatmap
def heat():
    d = pd.DataFrame(R["lgsr"]["heat"])
    m = d.pivot(index="wd", columns="hr", values="baskets").fillna(0)
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    im = ax.imshow(m.values, aspect="auto", cmap="YlGn")
    ax.set_yticks(range(len(m.index)), ["CN", "T2", "T3", "T4", "T5", "T6", "T7"][: len(m.index)])
    ax.set_xticks(range(len(m.columns)), m.columns, fontsize=7)
    ax.set_xlabel("Giờ")
    ax.grid(False)
    fig.colorbar(im, ax=ax, label="Số giỏ")
    ax.set_title("Giỏ hàng theo thứ × giờ (LGSR, 5K khách)")
    save(fig, "f08_heat.png")


# 9. Nhiệm vụ giỏ & độ nhạy giá
def missions():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
    for ax, key, title in [(axes[0], "basket_type", "Loại chuyến mua"), (axes[1], "price_sens", "Độ nhạy giá của giỏ")]:
        d = pd.DataFrame(R["lgsr"][key])
        d = d[d.level != "XX"]
        tot = d.spend.sum()
        ax.bar(d.level, d.baskets / d.baskets.sum(), color=PAL[2], label="% số giỏ", width=0.38, align="edge")
        ax.bar(d.level, d.spend / tot, color=PAL[1], label="% doanh thu", width=-0.38, align="edge")
        ax.yaxis.set_major_formatter(lambda v, _: pct(v))
        ax.set_title(title)
        ax.legend(fontsize=7.5)
    fig.tight_layout()
    save(fig, "f09_missions.png")


# 10. Carbo bổ trợ & trung thành
def carbo_fig():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    d = pd.DataFrame(R["carbo"]["complement"])
    d["pair"] = d.a.str.title() + " + " + d.b.str.title()
    d = d.sort_values("lift")
    axes[0].barh(d.pair, d.lift, color=SRC["carbo"])
    axes[0].axvline(1, color=MUTED, ls="--", lw=1)
    axes[0].set_title("Lift cùng giỏ (Carbo)")
    axes[0].tick_params(axis="y", labelsize=7.5)
    lo = pd.DataFrame(R["carbo"]["loyalty"])
    axes[1].bar(lo.commodity.str.title(), lo.share_loyal_80, color=PAL[0], label="Trung thành ≥80%")
    axes[1].bar(lo.commodity.str.title(), lo.share_switcher_50, bottom=lo.share_loyal_80, color=PAL[1], label="Hay đổi (<50%)")
    axes[1].yaxis.set_major_formatter(lambda v, _: pct(v))
    axes[1].tick_params(axis="x", labelsize=7.5)
    axes[1].legend(fontsize=7.2)
    axes[1].set_title("Cơ cấu trung thành thương hiệu")
    fig.tight_layout()
    save(fig, "f10_carbo.png")


# 11. M5 lịch & phân loại nhu cầu
def m5_fig():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw={"width_ratios": [1.5, 1]})
    d = pd.DataFrame(R["m5"]["monthly"])
    for j, c in enumerate(["FOODS", "HOUSEHOLD", "HOBBIES"]):
        axes[0].plot(pd.to_datetime(d.date), d[c] / 1e3, color=PAL[j], lw=1.6, label=c.title())
    axes[0].set_ylabel("Nghìn đơn vị/tháng")
    axes[0].legend(fontsize=7.5)
    axes[0].set_title("Lượng bán theo tháng (M5)")
    dc = pd.DataFrame(R["m5"]["demand_class"])
    pv = dc.pivot(index="cat", columns="cls", values="series").fillna(0)
    pv = pv.div(pv.sum(axis=1), axis=0)
    left = np.zeros(len(pv))
    for j, c in enumerate(pv.columns):
        axes[1].barh(pv.index, pv[c], left=left, color=PAL[j % len(PAL)], label=c)
        left += pv[c].values
    axes[1].xaxis.set_major_formatter(lambda v, _: pct(v))
    axes[1].legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    axes[1].set_title("Kiểu nhu cầu SKU-cửa hàng")
    fig.tight_layout()
    save(fig, "f11_m5.png")


# 12. CJ: chiến dịch
def campaigns():
    d = pd.DataFrame(R["cj"]["campaign_did"])
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
    ct = pd.DataFrame(R["cj"]["campaign_types"])
    axes[0].bar(ct.type, ct.redemption_rate, color=[PAL[0], PAL[1], PAL[2]])
    for i, v in enumerate(ct.redemption_rate):
        axes[0].text(i, v, pct(v, 1), ha="center", va="bottom", fontsize=8)
    axes[0].yaxis.set_major_formatter(lambda v, _: pct(v))
    axes[0].set_title("Tỷ lệ hộ đổi coupon / hộ nhận")
    col = {"TypeA": PAL[0], "TypeB": PAL[1], "TypeC": PAL[2]}
    axes[1].scatter(d.level_gap, d.did_pp, c=[col[t] for t in d.type], s=30)
    axes[1].axhline(0, color=MUTED, lw=0.8)
    axes[1].xaxis.set_major_formatter(lambda v, _: pct(v))
    axes[1].yaxis.set_major_formatter(lambda v, _: pct(v))
    axes[1].set_xlabel("Chênh chi tiêu trước chiến dịch (nhận vs không)")
    axes[1].set_ylabel("Chênh tăng trưởng (DiD)")
    axes[1].set_title("Hộ được chọn vốn đã chi nhiều hơn")
    fig.tight_layout()
    save(fig, "f12_campaigns.png")


# 13. Discount depth BATF
def depth():
    d = pd.DataFrame(R["batf"]["discount_depth"])
    fig, ax = plt.subplots(figsize=(6.6, 3))
    ax.bar(d["bin"], d.units_per_row, color=SRC["batf"])
    ax2 = ax.twinx()
    ax2.plot(d["bin"], d.rows / d.rows.sum(), color=INK, marker="o", lw=1.5)
    ax2.yaxis.set_major_formatter(lambda v, _: pct(v))
    ax2.grid(False)
    ax.set_ylabel("Đơn vị bán / cửa hàng-SKU-tuần")
    ax2.set_ylabel("% số quan sát")
    ax.set_xlabel("Độ sâu giảm giá so với giá cơ sở")
    ax.set_title("Giảm sâu bán nhiều hơn, nhưng hiếm (BATF)")
    save(fig, "f13_depth.png")


# 14. Giờ mua CJ vs Carbo
def hours():
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    for key, lab, c in [("cj", "Complete Journey", SRC["cj"]), ("carbo", "Carbo-Loading", SRC["carbo"])]:
        d = pd.DataFrame(R[key]["hour"])
        ax.plot(d.hr_, d.baskets / d.baskets.sum(), color=c, lw=2, label=lab)
    d = pd.DataFrame(R["lgsr"]["heat"]).groupby("hr").baskets.sum()
    ax.plot(d.index, d / d.sum(), color=SRC["lgsr"], lw=2, ls="--", label="LGSR (mô phỏng)")
    ax.yaxis.set_major_formatter(lambda v, _: pct(v))
    ax.set_xlabel("Giờ trong ngày")
    ax.set_ylabel("% số giỏ")
    ax.legend(fontsize=8)
    ax.set_title("Nhịp giờ mua sắm ở ba nguồn")
    save(fig, "f14_hours.png")


if __name__ == "__main__":
    for f in [lorenz, forest, batf_segment, promo, snap, events, income, heat, missions, carbo_fig, m5_fig, campaigns, depth, hours]:
        try:
            f()
            print("ok", f.__name__)
        except Exception as e:  # noqa: BLE001
            print("FAIL", f.__name__, repr(e))


# ---------------------------------------------------------------- Hình cho phân tích chuyên sâu
D2 = json.loads((OUT / "results_deep.json").read_text(encoding="utf-8"))


def deep_customers():
    p = pd.DataFrame(D2["cj"]["periods"])
    b = p.iloc[2]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw={"width_ratios": [1.3, 1]})
    for k, lab, c in [("sales", "Doanh thu", INK), ("hh", "Hộ hoạt động", SRC["cj"]), ("trips_per_hh", "Chuyến/hộ", SRC["m5"]), ("aov", "Giá trị giỏ", PAL[1])]:
        axes[0].plot(p.p4, 100 * p[k] / b[k], lw=2.4 if k == "sales" else 1.6, color=c, label=lab)
    axes[0].set_xlabel("Kỳ 4 tuần")
    axes[0].set_title("Chỉ số động lực (kỳ 3 = 100)")
    axes[0].legend(fontsize=7.5)
    t = pd.DataFrame(D2["cj"]["trajectory"]).set_index("traj")
    order = ["Tăng chi (>+20%)", "Ổn định (±20%)", "Giảm chi (<−20%)", "Rời bỏ (≥8 tuần không mua)"]
    t = t.loc[order]
    axes[1].bar([o.split(" (")[0] for o in order], t.households, color=[SRC["cj"], GRID, PAL[1], SRC["carbo"]])
    for i, (h, dlt) in enumerate(zip(t.households, t.delta)):
        axes[1].text(i, h, f"{h}\n{dlt / 1000:+.0f}k USD", ha="center", va="bottom", fontsize=7)
    axes[1].tick_params(axis="x", labelsize=7.5)
    axes[1].set_title("Quỹ đạo hộ: số hộ, chênh doanh thu")
    axes[1].set_ylim(0, t.households.max() * 1.3)
    fig.tight_layout()
    save(fig, "f15_customers.png")


def deep_rfm():
    d = pd.DataFrame(D2["cj"]["rfm"]).sort_values("rev_share", ascending=False)
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    x = np.arange(len(d))
    ax.bar(x - 0.2, d.hh_share, 0.4, color="#7fb09d", label="% số hộ")
    ax.bar(x + 0.2, d.rev_share, 0.4, color=SRC["cj"], label="% doanh thu")
    ax.set_xticks(x, d.segment, rotation=18, fontsize=7.8, ha="right")
    ax.yaxis.set_major_formatter(lambda v, _: pct(v))
    ax.legend(fontsize=8)
    ax.set_title("Phân khúc RFM (CJ, ngày 711)")
    save(fig, "f16_rfm.png")


def deep_rules():
    d = pd.DataFrame(D2["cj"]["rules_top_lift"]).iloc[::-1]
    lab = (d.a.str.title() + " + " + d.b.str.title())
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.barh(lab, d.lift, color=SRC["cj"])
    for i, v in enumerate(d.lift):
        ax.text(v + 0.1, i, f"{v:.1f}", va="center", fontsize=7.5)
    ax.tick_params(axis="y", labelsize=7.4)
    ax.set_xlabel("Lift")
    ax.set_title("15 cặp nhóm hàng có lift cao nhất (CJ, giỏ đầy đủ)")
    ax.grid(axis="y", visible=False)
    save(fig, "f17_rules.png")


def deep_dyn():
    d = pd.DataFrame(D2["batf"]["dynamics"])
    fig, ax = plt.subplots(figsize=(6.8, 3.1))
    x = np.arange(len(d))
    for j, (k, lab, c) in enumerate([("promo_l1", "Trễ 1 tuần", SRC["m5"]), ("promo_l2", "Trễ 2 tuần", "#7fb09d"), ("rival_promo", "Toàn bộ đối thủ khuyến mãi", SRC["carbo"])]):
        ax.bar(x + (j - 1) * 0.26, np.expm1(d[k]), 0.26, color=c, label=lab)
    ax.set_xticks(x, d.category.str.title(), fontsize=8)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.yaxis.set_major_formatter(lambda v, _: pct(v))
    ax.legend(fontsize=7.5, ncol=3)
    ax.set_title("Tuần sau khuyến mãi và khuyến mãi của đối thủ (BATF)")
    save(fig, "f18_dynamics.png")


def deep_sim():
    d = pd.DataFrame(D2["batf"]["profit_sim"])
    cats = sorted(d.category.unique())
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), sharey=True)
    for ax, col, title in [(axes[0], "profit_change_price_only", "Chỉ giảm giá"), (axes[1], "profit_change_with_display", "Giảm giá + trưng bày")]:
        m = d[d.margin == 0.3].pivot(index="category", columns="cut", values=col).reindex(cats)
        im = ax.imshow(m.values.clip(-1, 1), cmap="RdYlGn", vmin=-0.6, vmax=0.6, aspect="auto")
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                ax.text(j, i, pct(m.values[i, j]), ha="center", va="center", fontsize=8)
        ax.set_xticks(range(3), ["−10%", "−20%", "−30%"])
        ax.set_yticks(range(len(cats)), [c.title() for c in cats], fontsize=8)
        ax.grid(False)
        ax.set_title(title + " (biên 30%)", fontsize=10)
    fig.tight_layout()
    save(fig, "f19_profit_sim.png")


def deep_price():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1))
    l = pd.DataFrame(D2["batf"]["lerner"])
    axes[0].bar(l.category.str.title().str.replace(" Products", ""), l.implied_margin, color=SRC["batf"], label="Biên tối ưu 1/|e|")
    axes[0].scatter(l.category.str.title().str.replace(" Products", ""), l.breakeven_margin_20pct_cut, marker="_", s=600, color=INK, label="Biên hòa vốn khi giảm 20%")
    axes[0].yaxis.set_major_formatter(lambda v, _: pct(v))
    axes[0].tick_params(axis="x", labelsize=7.2)
    axes[0].legend(fontsize=7)
    axes[0].set_title("Biên ngụ ý (Lerner, BATF)")
    h = pd.DataFrame(D2["m5"]["price_change_hist"])
    axes[1].bar(h["bin"], h.n / 1000, color=[SRC["carbo"] if b.startswith(("−", "≤")) else SRC["m5"] for b in h["bin"]])
    axes[1].tick_params(axis="x", labelsize=6.8, rotation=45)
    axes[1].set_ylabel("Nghìn lần đổi giá")
    axes[1].set_title("Mức thay đổi khi giá đổi (M5)")
    fig.tight_layout()
    save(fig, "f20_price.png")


def deep_forecast():
    f = pd.DataFrame(D2["m5"]["forecast"]).sort_values("wrmsse_item")
    t = D2["m5"]["forecast_total"]
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1, 1.5]})
    axes[0].barh(f.model[::-1], f.wrmsse_item[::-1], color=[SRC["m5"] if m.startswith("GBM") else GRID for m in f.model[::-1]])
    for i, v in enumerate(f.wrmsse_item[::-1]):
        axes[0].text(v + 0.01, i, f"{v:.3f}", va="center", fontsize=7.5)
    axes[0].tick_params(axis="y", labelsize=7.5)
    axes[0].set_title("WRMSSE (thấp = tốt)")
    axes[0].grid(axis="y", visible=False)
    x = pd.to_datetime(t["dates"])
    axes[1].plot(x, np.array(t["actual"]) / 1e3, color=INK, lw=2.4, label="Thực tế")
    for k, c, ls in [("Naive mùa vụ 7 ngày", PAL[1], "--"), ("Trung bình 28 ngày", MUTED, ":"), ("GBM toàn cục (Poisson)", SRC["m5"], "-")]:
        axes[1].plot(x, np.array(t[k]) / 1e3, color=c, ls=ls, lw=1.6, label=k)
    axes[1].set_ylabel("Nghìn đơn vị/ngày")
    axes[1].legend(fontsize=6.8)
    axes[1].tick_params(axis="x", labelsize=7, rotation=30)
    axes[1].set_title("Tổng 28 ngày kiểm tra")
    fig.tight_layout()
    save(fig, "f21_forecast.png")


def deep_switch():
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.4))
    for ax, k, title in [(axes[0], "pasta sauce", "Sốt mì Ý"), (axes[1], "pasta", "Mì Ý")]:
        s = D2["carbo"][k]
        m = np.array(s["matrix"])
        ax.imshow(m, cmap="Reds", vmin=0, vmax=0.75)
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                ax.text(j, i, f"{m[i, j] * 100:.0f}", ha="center", va="center", fontsize=7, color="white" if m[i, j] > 0.45 else INK)
        ax.set_xticks(range(len(s["brands"])), s["brands"], rotation=40, ha="right", fontsize=7)
        ax.set_yticks(range(len(s["brands"])), s["brands"], fontsize=7)
        ax.grid(False)
        ax.set_title(f"{title}: lần trước (hàng) → lần sau (cột), %", fontsize=9)
    fig.tight_layout()
    save(fig, "f22_switch.png")


if __name__ == "__main__":
    for f in [deep_customers, deep_rfm, deep_rules, deep_dyn, deep_sim, deep_price, deep_forecast, deep_switch]:
        try:
            f()
            print("ok", f.__name__)
        except Exception as e:  # noqa: BLE001
            print("FAIL", f.__name__, repr(e))
