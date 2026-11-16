"""Dựng trang HTML phân tích đa nguồn từ outputs/multisource/results.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
OUT = ROOT / "outputs" / "multisource"
R = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
CJ, BA, CL, LG, M5 = R["cj"], R["batf"], R["carbo"], R["lgsr"], R["m5"]


def n(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def p(x, d=0):
    return n(x * 100, d) + "%"


def mil(x, d=1):
    return n(x / 1e6, d) + " tr"


M5_CELLS = M5["profile"]["series"] * M5["profile"]["days"]
TOTAL_ROWS = (CJ["profile"]["rows"] + CJ["profile"]["causal_rows"] + BA["profile"]["rows"] + CL["profile"]["rows"] + CL["profile"]["causal_rows"]
              + LG["profile"]["rows"] + M5_CELLS + M5["profile"]["price_rows"])

el_b = {e["category"]: e for e in BA["elasticity_category"]}
el_c = {e["commodity"]: e for e in CL["elasticity"]}
el_m = {e["cat"]: e for e in M5["elasticity"]}
snap = {(s["state"], s["cat"]): s for s in M5["snap"]}
ct = {c["type"]: c for c in CJ["campaign_types"]}
cds = {c["type"]: c for c in CJ["campaign_did_summary"]}
ev = {e["event"]: e for e in M5["events"]}
comp = {(c["a"], c["b"]): c for c in CL["complement"]}
loy = {c["commodity"]: c for c in CL["loyalty"]}
cl_comm = {c["commodity"]: c for c in CL["commodity"]}
pl_b = {(x["CATEGORY"], x["is_pl"]): x for x in BA["private_label"]}
inc = CJ["income_gradient"]
incpl = CJ["income_pl_gradient"]
cause = CJ["causal_lift"]
lg_bt = {x["level"]: x for x in LG["basket_type"]}
lg_ps = {x["level"]: x for x in LG["price_sens"]}
lg_fmt = {x["level"]: x for x in LG["store_format"]}
zero = M5["zero_share_by_cat"]
dc = {}
for x in M5["demand_class"]:
    dc.setdefault(x["cat"], {})[x["cls"]] = x
foods_smooth_share = dc["FOODS"]["Đều (smooth)"]["series"] / sum(v["series"] for v in dc["FOODS"].values())
all_series = sum(x["series"] for x in M5["demand_class"])
intermittent_all = sum(x["series"] for x in M5["demand_class"] if x["cls"] in ("Gián đoạn (intermittent)", "Cục (lumpy)")) / all_series

DATA = {
    "lorenz": [
        {"name": "CJ · hộ", "src": "cj", "p": CJ["pareto_households"]},
        {"name": "CJ · sản phẩm", "src": "cj2", "p": CJ["pareto_products"]},
        {"name": "Carbo · hộ", "src": "carbo", "p": CL["pareto_households"]},
        {"name": "LGSR · khách", "src": "lgsr", "p": LG["pareto_customers"]},
        {"name": "M5 · mặt hàng", "src": "m5", "p": M5["pareto_items"]},
    ],
    "elasticity": [{"name": "BATF · " + e["category"].title(), "src": "batf", "v": e["elasticity"], "lo": e["ci_low"], "hi": e["ci_high"]} for e in BA["elasticity_category"]]
    + [{"name": "Carbo · " + e["commodity"].title(), "src": "carbo", "v": e["elasticity"], "lo": e["ci_low"], "hi": e["ci_high"]} for e in CL["elasticity"]]
    + [{"name": "M5 · " + e["cat"].title(), "src": "m5", "v": e["elasticity"], "lo": e["ci_low"], "hi": e["ci_high"]} for e in M5["elasticity"]],
    "seg": BA["elasticity_segment"],
    "promo": [{"name": "CJ · Trưng bày", "src": "cj", "v": cause["lift_display"]}, {"name": "CJ · Tờ rơi", "src": "cj", "v": cause["lift_mailer"]},
              {"name": "CJ · Cả hai", "src": "cj", "v": cause["lift_both"]}]
    + [x for e in BA["elasticity_category"] for x in (
        {"name": f"BATF · {e['category'].title()} · Feature", "src": "batf", "v": e["lift_feature"]},
        {"name": f"BATF · {e['category'].title()} · Display", "src": "batf", "v": e["lift_display"]},
        {"name": f"BATF · {e['category'].title()} · TPR", "src": "batf2", "v": e["lift_tpr"]})]
    + [x for e in CL["elasticity"] for x in (
        {"name": f"Carbo · {e['commodity'].title()} · Feature", "src": "carbo", "v": e["lift_feature"]},
        {"name": f"Carbo · {e['commodity'].title()} · Display", "src": "carbo2", "v": e["lift_display"]})],
    "depth": BA["discount_depth"],
    "snap": M5["snap"], "dom": M5["day_of_month"], "events": M5["events"], "monthly": M5["monthly"], "weekday": M5["weekday"],
    "income": CJ["demo_income"], "kids": CJ["demo_kids"], "size": CJ["demo_size"],
    "heat": LG["heat"], "basket_type": LG["basket_type"], "price_sens": LG["price_sens"], "mission": LG["mission"], "fmt": LG["store_format"],
    "hours": {"cj": CJ["hour"], "carbo": CL["hour"]},
    "complement": CL["complement"], "loyalty": CL["loyalty"], "brands": CL["brands"],
    "campaign_did": CJ["campaign_did"], "campaign_types": CJ["campaign_types"],
    "cj_weekly": CJ["weekly"], "demand": M5["demand_class"], "pl": BA["private_label"],
    "timeline": [
        {"name": "LGSR (mô phỏng)", "src": "lgsr", "start": "2006-04-10", "end": "2008-07-06"},
        {"name": "BATF", "src": "batf", "start": BA["profile"]["start"], "end": BA["profile"]["end"]},
        {"name": "UCI Online Retail", "src": "uci", "start": "2010-12-01", "end": "2011-12-09"},
        {"name": "M5 Walmart", "src": "m5", "start": M5["profile"]["start"], "end": M5["profile"]["end"]},
        {"name": "Complete Journey (bản R)", "src": "cj2", "start": "2017-01-01", "end": "2017-12-31"},
    ],
}

SOURCES = [
    ("cj", "The Complete Journey", "dunnhumby · bản gốc 2 năm", f"{n(CJ['profile']['rows'])} dòng giao dịch, {n(CJ['profile']['households'])} hộ, {n(CJ['profile']['stores'])} cửa hàng, {n(CJ['profile']['products'])} SKU, 102 tuần; thêm {mil(CJ['profile']['causal_rows'])} dòng trưng bày/tờ rơi, 30 chiến dịch và coupon.",
     "Dòng hóa đơn của panel hộ mua thường xuyên", "Ai mua, mua gì, giảm giá bao nhiêu, chiến dịch có kéo thêm chi tiêu không"),
    ("batf", "Breakfast at the Frat", "dunnhumby · 2009–2011", f"{n(BA['profile']['rows'])} dòng cửa hàng × SKU × tuần, {BA['profile']['stores']} cửa hàng ở {', '.join(BA['profile']['states'])}, {BA['profile']['upcs']} SKU, 156 tuần.",
     "Tuần × cửa hàng × SKU, có giá kệ và giá cơ sở", "Độ co giãn giá, hiệu ứng tờ rơi/trưng bày/giảm giá tạm thời, phân khúc cửa hàng"),
    ("carbo", "Carbo-Loading", "dunnhumby · 104 tuần", f"{mil(CL['profile']['rows'])} dòng, {n(CL['profile']['households'])} hộ, {n(CL['profile']['baskets'])} giỏ, {CL['profile']['upcs']} SKU mì Ý, sốt, siro, bột bánh.",
     "Dòng giao dịch hộ trong 4 ngành bổ trợ", "Trung thành thương hiệu, coupon, cặp hàng bổ trợ, mức tập trung thị trường"),
    ("lgsr", "Let’s Get Sort-of-Real", "dunnhumby · mẫu 5.000 khách", f"{mil(LG['profile']['rows'])} dòng, {n(LG['profile']['baskets'])} giỏ, {n(LG['profile']['stores'])} cửa hàng, {LG['profile']['weeks']} tuần. Dữ liệu mô phỏng.",
     "Dòng giỏ hàng có nhãn nhiệm vụ giỏ, độ nhạy giá, định dạng cửa hàng", "Nhịp giờ, loại chuyến mua, phân khúc giá, định dạng cửa hàng"),
    ("m5", "M5 Forecasting", "Walmart · Kaggle, bản Zenodo", f"{n(M5['profile']['series'])} chuỗi SKU-cửa hàng × {n(M5['profile']['days'])} ngày, {M5['profile']['stores']} cửa hàng ở CA, TX, WI; {mil(M5['profile']['price_rows'])} dòng giá tuần, lịch sự kiện và SNAP.",
     "Ngày × cửa hàng × SKU (lượng bán), giá theo tuần", "Dự báo, tính mùa vụ, tác động trợ cấp SNAP, sự kiện, độ co giãn"),
]

FIELDS = [
    ("Mã khách / hộ", ["cj", "carbo", "lgsr"], "Có trong CJ, Carbo; LGSR có nhưng 20% giỏ không thẻ"),
    ("Mã giỏ / hóa đơn", ["cj", "carbo", "lgsr"], ""),
    ("Giờ giao dịch", ["cj", "carbo", "lgsr"], "LGSR theo khung giờ"),
    ("Giá kệ / giá cơ sở", ["batf"], "Chỉ BATF tách giá thực và giá cơ sở"),
    ("Giá bán thực tế", ["cj", "batf", "carbo", "m5"], "CJ, Carbo phải tự suy ra = tiền/đơn vị"),
    ("Giảm giá thẻ thành viên", ["cj"], ""),
    ("Coupon", ["cj", "carbo"], "Carbo: cờ 0/1; CJ: số tiền + chiến dịch"),
    ("Tờ rơi / quảng cáo", ["cj", "batf", "carbo"], "Carbo chỉ từ tuần 43"),
    ("Trưng bày tại cửa hàng", ["cj", "batf", "carbo"], ""),
    ("Chiến dịch marketing trực tiếp", ["cj"], ""),
    ("Nhân khẩu học hộ", ["cj"], "801/2.500 hộ"),
    ("Phân khúc khách / độ nhạy giá", ["lgsr"], "Nhãn có sẵn, dữ liệu mô phỏng"),
    ("Thuộc tính cửa hàng", ["batf", "lgsr", "m5"], "BATF: diện tích, phân khúc; LGSR: định dạng, vùng; M5: bang"),
    ("Thương hiệu / nhãn riêng", ["cj", "batf", "carbo"], ""),
    ("Lịch lễ & sự kiện", ["m5"], ""),
    ("Trợ cấp thực phẩm (SNAP)", ["m5"], "Biến chính sách duy nhất"),
    ("Ngày không bán (zero)", ["m5"], "Chỉ M5 ghi nhận lượng 0 tường minh"),
]


def chip(src):
    lab = {"cj": "CJ", "batf": "BATF", "carbo": "Carbo", "lgsr": "LGSR", "m5": "M5"}[src]
    return f'<span class="chip c-{src}">{lab}</span>'


src_cards = "\n".join(f"""<article class="src" style="--src: var(--{k})">
  <header><span class="src-dot"></span><div><h3>{t}</h3><p class="mono">{sub}</p></div></header>
  <p>{desc}</p>
  <dl><dt>Hạt dữ liệu</dt><dd>{grain}</dd><dt>Trả lời được</dt><dd>{ans}</dd></dl>
</article>""" for k, t, sub, desc, grain, ans in SOURCES)

field_rows = "\n".join(
    "<tr><th scope=\"row\">{}</th>{}<td class=\"note\">{}</td></tr>".format(
        f, "".join(f'<td class="dot-cell">{"<span class=dot style=\"--src:var(--" + s + ")\" title=\"có\"></span>" if s in have else "<span class=nodot>·</span>"}</td>' for s in ["cj", "batf", "carbo", "lgsr", "m5"]), note)
    for f, have, note in FIELDS)

QUALITY = [
    ("cj", "Panel 2.500 hộ, không phải toàn bộ doanh thu cửa hàng", f"Nhân khẩu học chỉ có {CJ['profile']['demographic_households']} hộ ({p(CJ['profile']['demographic_households'] / 2500)}) nhưng chiếm {p(CJ['profile']['demographic_sales_share'])} doanh thu → hộ có hồ sơ là hộ chi nhiều. SALES_VALUE là tiền nhà bán lẻ nhận, không phải giá khách trả; {n(CJ['profile']['nonpos_sales'])} dòng có giá trị ≤ 0.", "Không dùng tổng theo cửa hàng làm doanh thu cửa hàng. Kết luận nhân khẩu học chỉ đại diện nhóm có hồ sơ."),
    ("batf", "Chỉ 55 SKU, 4 ngành, toàn top brand", f"{n(BA['profile']['price_above_base'])} dòng có giá bán cao hơn giá cơ sở; {BA['profile']['missing_base_price']} dòng thiếu giá cơ sở. Dữ liệu chỉ có tuần có bán.", "Ước lượng co giãn tốt nhất trong 5 nguồn vì có giá cơ sở và biến khuyến mãi tách riêng, nhưng không suy rộng ra toàn cửa hàng."),
    ("carbo", "Vũ trụ chỉ gồm 4 ngành", f"Mọi giỏ đều chứa ít nhất một trong 4 ngành, nên lift mì Ý + sốt chỉ {n(comp[('pasta', 'pasta sauce')]['lift'], 2)} dù {p(comp[('pasta', 'pasta sauce')]['conf_b_a'])} giỏ có sốt cũng có mì. Tờ rơi/trưng bày chỉ có từ tuần 43.", "Lift trong dữ liệu đã lọc ngành bị kéo về 1; cần mẫu giỏ đầy đủ mới đo đúng mức bổ trợ."),
    ("lgsr", "Dữ liệu mô phỏng", f"Nhà phát hành ghi rõ đây là dummy data mô phỏng. {p(LG['profile']['share_rows_no_card'])} dòng không có mã khách (giỏ không thẻ); có {LG['profile']['weeks']} tuần thay vì 117 như mô tả.", "Dùng để thử quy trình và phương pháp, không dùng làm bằng chứng kinh tế."),
    ("m5", f"{p(M5['profile']['zero_share'])} ô ngày-SKU bằng 0", f"Ngày 25/12 cả năm gần như không bán (cửa hàng đóng). Không có tồn kho nên không phân biệt được 'không có cầu' với 'hết hàng'. {p(intermittent_all)} chuỗi là nhu cầu gián đoạn hoặc cục.", "Mô hình dự báo phải xử lý nhu cầu gián đoạn; doanh thu phải tự tính = lượng × giá tuần."),
]
quality_rows = "\n".join(f"<tr><td>{chip(s)}</td><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for s, a, b, c in QUALITY)

html = f"""<title>Bản đồ bán lẻ đa nguồn</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="Phân tích tổng hợp 5 bộ dữ liệu bán lẻ (dunnhumby Complete Journey, Breakfast at the Frat, Carbo-Loading, Let's Get Sort-of-Real, Walmart M5) theo góc độ dữ liệu và góc độ kinh tế.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Bố cục: dải mở đầu xanh rêu đậm (nối tiếp nhận diện Retail Intelligence) → mục lục dính → các chương, mỗi phát hiện có hai lớp đọc: Dữ liệu và Kinh tế. */
:root {{
  --bg: #f3f6f4; --surface: #ffffff; --ink: #11231e; --muted: #5d6f68; --line: #dbe4df; --soft: #e8efeb;
  --brand: #173e35; --brand-ink: #eef5f1; --accent: #c4862a; --data: #3f6f95; --econ: #b0702a;
  --cj: #1f6b55; --cj2: #7fb39e; --batf: #c4862a; --batf2: #e2bb7e; --carbo: #a94a3f; --carbo2: #d48f86; --lgsr: #7a65a8; --m5: #3f6f95; --uci: #8a8f8c;
  --display: "Bricolage Grotesque", "Be Vietnam Pro", system-ui, sans-serif;
  --body: "Be Vietnam Pro", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Consolas, monospace;
  --r: 14px;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0c1613; --surface: #12201c; --ink: #e4ede8; --muted: #93a69e; --line: #24372f; --soft: #182a24;
  --brand: #0f2a23; --brand-ink: #e7f1ec; --accent: #e0a24a; --data: #7fa8cc; --econ: #dd9c55;
  --cj: #4fae8c; --cj2: #2f7a62; --batf: #e0a24a; --batf2: #9c763a; --carbo: #dc7a6d; --carbo2: #94534b; --lgsr: #a593d6; --m5: #78a6d1; --uci: #8f9692;
  color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #0c1613; --surface: #12201c; --ink: #e4ede8; --muted: #93a69e; --line: #24372f; --soft: #182a24;
  --brand: #0f2a23; --brand-ink: #e7f1ec; --accent: #e0a24a; --data: #7fa8cc; --econ: #dd9c55;
  --cj: #4fae8c; --cj2: #2f7a62; --batf: #e0a24a; --batf2: #9c763a; --carbo: #dc7a6d; --carbo2: #94534b; --lgsr: #a593d6; --m5: #78a6d1; --uci: #8f9692;
  color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--ink); font: 400 16px/1.65 var(--body); }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--surface); }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
h1, h2, h3 {{ font-family: var(--display); text-wrap: balance; letter-spacing: -0.01em; margin: 0; }}
p {{ margin: 0; }}
.mono {{ font-family: var(--mono); font-size: 0.78rem; letter-spacing: 0.02em; }}
.eyebrow {{ font: 600 0.74rem/1 var(--mono); letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); }}
a {{ color: inherit; }}
a:focus-visible, button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 6px; }}

/* Mở đầu */
.hero {{ background: var(--brand); color: var(--brand-ink); padding-block: 56px 40px; position: relative; overflow: hidden; }}
.hero canvas {{ position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0.55; pointer-events: none; }}
.hero .wrap {{ position: relative; display: grid; gap: 28px; }}
.hero h1 {{ font-size: clamp(2.1rem, 5.4vw, 4.2rem); line-height: 1.02; font-weight: 800; max-width: 17ch; }}
.hero h1 em {{ font-style: normal; color: var(--accent); }}
.hero .lead {{ max-width: 62ch; font-size: 1.08rem; color: color-mix(in srgb, var(--brand-ink) 82%, transparent); }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1px; background: color-mix(in srgb, var(--brand-ink) 18%, transparent); border-radius: var(--r); overflow: hidden; }}
.kpi {{ background: var(--brand); padding: 18px 20px; display: grid; gap: 4px; }}
.kpi b {{ font: 700 clamp(1.6rem, 3vw, 2.2rem)/1.05 var(--display); font-variant-numeric: tabular-nums; }}
.kpi span {{ font-size: 0.84rem; color: color-mix(in srgb, var(--brand-ink) 72%, transparent); }}
.legend-src {{ display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: 0.84rem; }}
.legend-src span {{ display: inline-flex; align-items: center; gap: 7px; }}
.legend-src i {{ width: 10px; height: 10px; border-radius: 50%; background: var(--src); }}

/* Mục lục */
.toc {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: color-mix(in srgb, var(--surface) 92%, transparent); backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); }}
.toc .wrap {{ display: flex; gap: 4px; overflow-x: auto; padding-block: 10px; scrollbar-width: none; }}
.toc a {{ flex: none; text-decoration: none; font-size: 0.86rem; padding: 6px 12px; border-radius: 999px; color: var(--muted); white-space: nowrap; }}
.toc a:hover {{ background: var(--soft); color: var(--ink); }}
.toc a.on {{ background: var(--brand); color: var(--brand-ink); }}

/* Chương */
section.ch {{ padding-block: 64px 8px; scroll-margin-top: 56px; }}
.ch-head {{ display: grid; gap: 12px; margin-bottom: 28px; max-width: 760px; }}
.ch-head h2 {{ font-size: clamp(1.7rem, 3.4vw, 2.5rem); line-height: 1.1; font-weight: 700; }}
.ch-head p {{ color: var(--muted); font-size: 1.04rem; }}
.finding {{ display: grid; grid-template-columns: minmax(0, 1.65fr) minmax(0, 1fr); gap: 20px; margin-bottom: 28px; align-items: start; }}
.finding.full {{ grid-template-columns: minmax(0, 1fr); }}
.panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); padding: 20px 20px 12px; min-width: 0; }}
.panel h3 {{ font-size: 1.12rem; font-weight: 700; margin-bottom: 4px; }}
.panel .sub {{ color: var(--muted); font-size: 0.86rem; margin-bottom: 8px; }}
.chart {{ width: 100%; height: 360px; }}
.chart.tall {{ height: 520px; }}
.chart.xtall {{ height: 640px; }}
.lens {{ display: grid; gap: 14px; min-width: 0; }}
.lens > div {{ padding: 16px 18px; border-radius: var(--r); background: var(--surface); border: 1px solid var(--line); position: relative; }}
.lens .tag {{ font: 600 0.7rem/1 var(--mono); letter-spacing: 0.12em; text-transform: uppercase; display: inline-flex; gap: 6px; align-items: center; margin-bottom: 8px; }}
.lens .d .tag {{ color: var(--data); }}
.lens .e .tag {{ color: var(--econ); }}
.lens .tag::before {{ content: ""; width: 8px; height: 8px; border-radius: 2px; background: currentColor; }}
.lens p {{ font-size: 0.94rem; }}
.lens p + p {{ margin-top: 8px; }}
.big {{ font: 700 2rem/1 var(--display); font-variant-numeric: tabular-nums; display: block; margin-bottom: 6px; }}
.chip {{ display: inline-block; font: 600 0.68rem/1 var(--mono); padding: 4px 7px; border-radius: 6px; color: #fff; letter-spacing: 0.04em; }}
.c-cj {{ background: var(--cj); }} .c-batf {{ background: var(--batf); }} .c-carbo {{ background: var(--carbo); }} .c-lgsr {{ background: var(--lgsr); }} .c-m5 {{ background: var(--m5); }}

/* Nguồn */
.srcs {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }}
.src {{ background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); padding: 18px 20px; display: grid; gap: 10px; align-content: start; }}
.src header {{ display: flex; gap: 12px; align-items: flex-start; }}
.src-dot {{ width: 12px; height: 12px; border-radius: 50%; background: var(--src); margin-top: 8px; flex: none; box-shadow: 0 0 0 4px color-mix(in srgb, var(--src) 22%, transparent); }}
.src h3 {{ font-size: 1.15rem; }}
.src p.mono {{ color: var(--muted); }}
.src > p {{ font-size: 0.93rem; }}
.src dl {{ margin: 0; display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; font-size: 0.86rem; border-top: 1px dashed var(--line); padding-top: 10px; }}
.src dt {{ color: var(--muted); }}
.src dd {{ margin: 0; }}

table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
.tbl {{ overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); }}
th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
thead th {{ font: 600 0.72rem/1.2 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); background: var(--soft); position: sticky; top: 0; }}
tbody tr:last-child th, tbody tr:last-child td {{ border-bottom: 0; }}
.matrix td.dot-cell {{ text-align: center; width: 72px; }}
.matrix .dot {{ display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: var(--src); }}
.matrix .nodot {{ color: var(--line); font-weight: 700; }}
.matrix td.note {{ color: var(--muted); font-size: 0.84rem; min-width: 220px; }}
.matrix th[scope=row] {{ font-weight: 600; white-space: nowrap; }}
.quality td:nth-child(3), .quality td:nth-child(4) {{ min-width: 260px; }}

.callout {{ border-left: 3px solid var(--accent); padding: 4px 0 4px 18px; max-width: 70ch; font-size: 1.02rem; margin-bottom: 24px; }}

/* Tổng hợp */
.synth {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
.synth article {{ background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); padding: 20px; display: grid; gap: 10px; align-content: start; }}
.synth h3 {{ font-size: 1.08rem; }}
.synth .who {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.synth p {{ font-size: 0.93rem; color: var(--muted); }}
.synth p b {{ color: var(--ink); }}
.actions {{ counter-reset: a; display: grid; gap: 12px; }}
.actions li {{ list-style: none; display: grid; grid-template-columns: 44px 1fr; gap: 14px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); padding: 16px 18px; }}
.actions li::before {{ counter-increment: a; content: counter(a, decimal-leading-zero); font: 700 1.3rem/1 var(--display); color: var(--accent); }}
.actions h3 {{ font-size: 1.04rem; margin-bottom: 4px; }}
.actions p {{ font-size: 0.93rem; color: var(--muted); }}
.actions ul {{ margin: 0; padding: 0; }}
footer.foot {{ margin-top: 64px; background: var(--brand); color: var(--brand-ink); padding-block: 36px; font-size: 0.88rem; }}
footer.foot .wrap {{ display: grid; gap: 14px; }}
footer.foot p {{ color: color-mix(in srgb, var(--brand-ink) 78%, transparent); max-width: 90ch; }}
.seg-toggle {{ display: inline-flex; gap: 4px; background: var(--soft); padding: 4px; border-radius: 999px; margin-bottom: 8px; flex-wrap: wrap; }}
.seg-toggle button {{ border: 0; background: transparent; font: 500 0.82rem var(--body); color: var(--muted); padding: 5px 12px; border-radius: 999px; cursor: pointer; }}
.seg-toggle button[aria-pressed="true"] {{ background: var(--surface); color: var(--ink); box-shadow: 0 1px 2px color-mix(in srgb, var(--ink) 15%, transparent); }}

@media (max-width: 860px) {{
  .finding {{ grid-template-columns: minmax(0, 1fr); }}
  .chart {{ height: 320px; }} .chart.tall {{ height: 480px; }} .chart.xtall {{ height: 620px; }}
  .hero {{ padding-block: 40px 28px; }}
}}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto !important; transition: none !important; animation: none !important; }} }}
html {{ scroll-behavior: smooth; }}
</style>

<header class="hero">
  <canvas id="heroCanvas" aria-hidden="true"></canvas>
  <div class="wrap">
    <div class="eyebrow">Retail Intelligence · Phân tích đa nguồn</div>
    <h1>Năm bộ dữ liệu bán lẻ, <em>một</em> cách đọc cho chuỗi siêu thị</h1>
    <p class="lead">Gộp Complete Journey bản gốc 2 năm, Breakfast at the Frat, Carbo-Loading, Let’s Get Sort-of-Real và Walmart M5. Các bộ không có khóa chung nên không nối từng dòng. Chúng được chuẩn hóa về cùng bộ chỉ số rồi so sánh. Mỗi phát hiện được đọc theo hai góc: dữ liệu đo được gì, và kinh tế học nói gì.</p>
    <div class="kpis">
      <div class="kpi"><b>{n(TOTAL_ROWS / 1e6, 0)} triệu</b><span>dòng/ô dữ liệu đã xử lý</span></div>
      <div class="kpi"><b>5</b><span>nguồn mới, cộng 2 nguồn trong dashboard cũ</span></div>
      <div class="kpi"><b>2006–2016</b><span>khoảng thời gian được phủ</span></div>
      <div class="kpi"><b>{n(CJ['profile']['stores'] + BA['profile']['stores'] + CL['profile']['stores'] + LG['profile']['stores'] + M5['profile']['stores'])}</b><span>mã cửa hàng, cộng dồn các nguồn</span></div>
      <div class="kpi"><b>{len(FIELDS)}</b><span>nhóm trường được đối chiếu</span></div>
    </div>
    <div class="legend-src">
      <span style="--src: var(--cj)"><i></i>CJ · Complete Journey</span>
      <span style="--src: var(--batf)"><i></i>BATF · Breakfast at the Frat</span>
      <span style="--src: var(--carbo)"><i></i>Carbo · Carbo-Loading</span>
      <span style="--src: var(--lgsr)"><i></i>LGSR · Sort-of-Real (mô phỏng)</span>
      <span style="--src: var(--m5)"><i></i>M5 · Walmart</span>
    </div>
  </div>
</header>

<nav class="toc" aria-label="Các chương"><div class="wrap">
  <a href="#nguon">Nguồn & trường</a><a href="#du-lieu">Góc dữ liệu</a><a href="#tap-trung">Tập trung</a><a href="#gia">Giá</a><a href="#khuyen-mai">Khuyến mãi</a><a href="#chinh-sach">Lịch & chính sách</a><a href="#thu-nhap">Thu nhập & nhãn riêng</a><a href="#hanh-vi">Hành vi giỏ</a><a href="#tong-hop">Tổng hợp</a><a href="#hanh-dong">Hành động</a>
</div></nav>

<main>
<section class="ch" id="nguon"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 1 · Bản đồ nguồn</div><h2>Mỗi bộ dữ liệu nhìn bán lẻ ở một hạt khác nhau</h2>
  <p>Hạt dữ liệu quyết định câu hỏi trả lời được. Panel hộ cho biết ai mua. Bảng cửa hàng-tuần cho biết giá tác động thế nào. Chuỗi ngày-SKU cho biết cần dự trữ bao nhiêu.</p></div>
  <div class="srcs">{src_cards}</div>
  <div class="finding full" style="margin-top:28px"><div class="panel"><h3>Dòng thời gian các nguồn</h3><p class="sub">Các nguồn có ngày thật. CJ bản gốc và Carbo chỉ ghi số thứ tự ngày/tuần (711 ngày, 104 tuần) nên không đặt được lên trục. Không có hai nguồn nào trùng kỳ và trùng địa bàn.</p><div class="chart" id="cTimeline" style="height:260px"></div></div></div>
  <div class="panel" style="padding:0;overflow:hidden"><div style="padding:20px 20px 8px"><h3>Ma trận trường dữ liệu</h3><p class="sub">Trộn nhiều nguồn có lợi vì mỗi nguồn có những trường nguồn khác không có.</p></div>
  <div class="tbl" style="border:0;border-radius:0"><table class="matrix"><thead><tr><th>Nhóm trường</th><th>CJ</th><th>BATF</th><th>Carbo</th><th>LGSR</th><th>M5</th><th>Ghi chú</th></tr></thead><tbody>{field_rows}</tbody></table></div></div>
</div></section>

<section class="ch" id="du-lieu"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 2 · Góc dữ liệu</div><h2>Trước khi tin con số, cần biết mỗi nguồn sai ở đâu</h2>
  <p>Mỗi nguồn có một điểm mù. Bảng dưới ghi nguồn gốc sai lệch và cách xử lý trong báo cáo này.</p></div>
  <p class="callout">Nguyên tắc trộn: <b>hài hòa ở mức chỉ số, không nối ở mức dòng</b>. Cùng một chỉ số (độ co giãn, mức tăng do trưng bày, tỷ trọng top 20%) được ước lượng riêng trong từng nguồn bằng cùng phương pháp. Kết luận nào lặp lại ở nhiều nguồn độc lập thì đáng tin hơn kết luận chỉ có ở một nguồn.</p>
  <div class="tbl"><table class="quality"><thead><tr><th>Nguồn</th><th>Giới hạn chính</th><th>Bằng chứng trong dữ liệu</th><th>Cách xử lý</th></tr></thead><tbody>{quality_rows}</tbody></table></div>
  <div class="finding" style="margin-top:28px">
    <div class="panel"><h3>Nhu cầu ở cấp SKU-cửa hàng phần lớn là gián đoạn</h3><p class="sub">M5 · phân loại Syntetos–Boylan (ADI 1,32; CV² 0,49) cho {n(all_series)} chuỗi</p><div class="chart" id="cDemand"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><span class="big">{p(intermittent_all)}</span><p>chuỗi SKU-cửa hàng có nhu cầu gián đoạn hoặc cục. Ở ngành Thực phẩm chỉ {p(foods_smooth_share)} chuỗi bán đều. Tỷ lệ ngày bằng 0: Thực phẩm {p(zero['FOODS'])}, Gia dụng {p(zero['HOUSEHOLD'])}, Sở thích {p(zero['HOBBIES'])}.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Lượng bán bằng 0 có thể là không có cầu hoặc hết hàng. Nếu không có dữ liệu tồn kho, mô hình sẽ đánh giá thấp nhu cầu thật của mặt hàng hay hết hàng, và chuỗi sẽ tiếp tục nhập thiếu. Chuỗi Việt Nam cần ghi tồn kho đầu ngày để phân biệt hai trường hợp này.</p></div>
    </div>
  </div>
</div></section>

<section class="ch" id="tap-trung"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 3 · Tập trung doanh thu</div><h2>Quy luật 20/60 xuất hiện ở cả khách hàng lẫn mặt hàng</h2>
  <p>Đường Lorenz của năm góc nhìn gần như chồng lên nhau. Đây là phát hiện ổn định nhất của báo cáo.</p></div>
  <div class="finding">
    <div class="panel"><h3>Tỷ trọng doanh thu tích lũy</h3><p class="sub">Xếp khách hoặc mặt hàng từ chi nhiều đến chi ít. Đường chéo là phân bổ đều.</p><div class="chart" id="cLorenz"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><span class="big">{p(CJ['pareto_households']['top20'])} – {p(LG['pareto_customers']['top20'])}</span><p>doanh thu đến từ 20% khách (CJ, Carbo {p(CL['pareto_households']['top20'])}, LGSR). Với mặt hàng, top 20% SKU của M5 tạo {p(M5['pareto_items']['top20'])} doanh thu. Panel CJ chỉ chọn hộ mua thường xuyên nên mức tập trung thật của cửa hàng còn cao hơn.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Doanh thu tập trung nên giá trị kinh tế nằm ở việc giữ nhóm đầu, không phải kéo thêm khách lẻ. Mất 1% hộ đầu của CJ tương đương mất {p(CJ['pareto_households']['top1'])} doanh thu. Ngân sách CRM nên chia theo giá trị vòng đời. Danh mục hàng nên được rà theo đuôi dài: {p(1 - M5['pareto_items']['curve'][7]['share'])} doanh thu M5 đến từ 40% SKU bán chậm nhất, chiếm kệ và vốn tồn kho.</p></div>
    </div>
  </div>
</div></section>

<section class="ch" id="gia"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 4 · Giá</div><h2>Hàng tùy ý co giãn mạnh, hàng thiết yếu thì gần như không</h2>
  <p>Độ co giãn được ước lượng bằng hồi quy log–log với hiệu ứng cố định SKU×cửa hàng và tuần. BATF và Carbo đã giữ cố định tờ rơi, trưng bày và giảm giá tạm thời. Thanh ngang là khoảng tin cậy 95%.</p></div>
  <div class="finding">
    <div class="panel"><h3>Độ co giãn của lượng bán theo giá</h3><p class="sub">Giá trị −2 nghĩa là giá tăng 1% thì lượng bán giảm khoảng 2%</p><div class="chart tall" id="cElastic"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>BATF đo trên giá kệ thực tế so với giá cơ sở, nên ước lượng sạch nhất. Carbo và M5 phải suy giá từ doanh thu/đơn vị hoặc giá tuần. Biến động giá của hai nguồn này nhỏ hơn và lẫn sai số đo, khiến hệ số bị kéo về 0. Vì vậy cần so sánh theo thứ hạng, không so trị tuyệt đối giữa các nguồn.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><span class="big">{n(el_b['FROZEN PIZZA']['elasticity'], 2)}</span><p>là độ co giãn của pizza đông lạnh, ngành nhạy giá nhất: có nhiều sản phẩm thay thế và dễ tích trữ. Ngũ cốc {n(el_b['COLD CEREAL']['elasticity'], 2)}, snack {n(el_b['BAG SNACKS']['elasticity'], 2)}. Bốn ngành của Carbo ({n(el_c['pasta']['elasticity'], 2)} đến {n(el_c['pancake mixes']['elasticity'], 2)}) và các ngành của M5 đều nằm trong khoảng từ −1 đến 0. Với nhóm ít co giãn, tăng giá nhẹ làm tăng doanh thu. Với nhóm co giãn hơn 1, giảm giá có thể tăng doanh thu nhưng phải so với biên lợi nhuận.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Co giãn theo phân khúc cửa hàng</h3><p class="sub">BATF · cửa hàng Value / Mainstream / Upscale do nhà bán lẻ tự phân loại</p><div class="chart" id="cSeg"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Khoảng tin cậy giữa ba phân khúc chồng lên nhau ở hầu hết ngành. Chỉ có 17 cửa hàng Upscale và 19 cửa hàng Value, nên mẫu chưa đủ để chứng minh khác biệt.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Giả thuyết "cửa hàng bình dân nhạy giá hơn" không được dữ liệu ủng hộ rõ. Snack ở cửa hàng Value thậm chí ít co giãn hơn ({n([s for s in BA['elasticity_segment'] if s['category']=='BAG SNACKS' and s['segment']=='VALUE'][0]['elasticity'], 2)}). Độ nhạy giá phụ thuộc ngành hàng nhiều hơn phụ thuộc vị trí cửa hàng. Nên định giá theo ngành trước, rồi mới tinh chỉnh theo cụm cửa hàng.</p></div>
    </div>
  </div>
</div></section>

<section class="ch" id="khuyen-mai"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 5 · Khuyến mãi</div><h2>Vị trí trên kệ và tờ rơi hiệu quả hơn giảm giá đơn thuần</h2>
  <p>Ba nguồn có biến trưng bày và tờ rơi. Sau khi đã kiểm soát giá, phần còn lại là hiệu ứng của sự chú ý.</p></div>
  <div class="finding">
    <div class="panel"><h3>Mức tăng lượng bán khi có hoạt động</h3><p class="sub">Feature = tờ rơi/quảng cáo; Display = trưng bày; TPR = giảm giá tạm thời không kèm quảng bá</p><div class="chart xtall" id="cPromo"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>CJ chỉ quan sát những tuần có hộ trong panel mua, nên mức tăng ({p(cause['lift_display'])} trưng bày, {p(cause['lift_mailer'])} tờ rơi, {p(cause['lift_both'])} cả hai) là cận dưới. BATF và Carbo đo ở cấp cửa hàng nên ghi được toàn bộ lượng bán. Hiệu ứng tờ rơi bột bánh {p(el_c['pancake mixes']['lift_feature'])} tính trên mẫu nhỏ.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Trưng bày tăng 28–69% lượng bán ở BATF và 33–47% ở Carbo khi giá không đổi. Ngược lại, cờ TPR (chỉ giảm giá) có hệ số ≈ 0 hoặc âm khi đã tính giá: giảm giá chỉ tác động qua mức giá, không có hiệu ứng phụ. Khách mua theo sự chú ý nhiều hơn theo phép tính. Ngân sách trade marketing nên ưu tiên vị trí kệ và tờ rơi, không chỉ đổ vào mức giảm.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Giảm sâu thì bán nhiều, nhưng hiếm</h3><p class="sub">BATF · đơn vị bán trung bình mỗi SKU-cửa hàng-tuần theo độ sâu giảm giá</p><div class="chart" id="cDepth"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>{p(BA['discount_depth'][0]['rows'] / sum(x['rows'] for x in BA['discount_depth']))} quan sát bán đúng giá cơ sở. Nhóm giảm ≥ 40% chỉ có {n(BA['discount_depth'][-1]['rows'])} quan sát, nhưng bán {n(BA['discount_depth'][-1]['units_per_row'], 1)} đơn vị/tuần so với {n(BA['discount_depth'][0]['units_per_row'], 1)} khi không giảm.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Phần lượng bán tăng thêm trong tuần giảm giá gồm ba phần: khách mới, khách chuyển từ thương hiệu khác, và khách mua trước rồi bớt mua tuần sau. Chỉ phần đầu là tăng trưởng thật. Cần đo lượng bán 2–4 tuần sau khuyến mãi để trừ phần mua dồn trước khi tính ROI.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Chiến dịch coupon: chọn đúng người hay tạo thêm chi tiêu?</h3><p class="sub">CJ · 29 chiến dịch. Trục ngang: hộ nhận coupon đã chi nhiều hơn bao nhiêu trước chiến dịch. Trục dọc: chênh tăng trưởng trong chiến dịch so với hộ không nhận (DiD)</p><div class="chart" id="cCampaign"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><span class="big">×{n(1 + cds['TypeA']['level_gap'], 1)}</span><p>là mức chi của hộ nhận chiến dịch TypeA so với hộ không nhận, ngay cả trước khi chiến dịch bắt đầu. Hộ nhận không được chọn ngẫu nhiên, nên so sánh thô sẽ gán nhầm thành tích cho chiến dịch.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Khi so tốc độ tăng chi tiêu, chênh lệch trung vị chỉ {p(cds['TypeA']['did_pp_median'], 1)} (TypeA), {p(cds['TypeB']['did_pp_median'], 1)} (TypeB), {p(cds['TypeC']['did_pp_median'], 1)} (TypeC). Tỷ lệ đổi coupon cao nhất ở TypeA ({p(ct['TypeA']['redemption_rate'], 1)}) vì coupon được cá nhân hóa. Phần lớn coupon có thể đang trợ giá cho chi tiêu vốn sẽ xảy ra. Chuỗi cần nhóm đối chứng ngẫu nhiên (holdout) trước khi mở rộng ngân sách.</p></div>
    </div>
  </div>
</div></section>

<section class="ch" id="chinh-sach"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 6 · Lịch và chính sách</div><h2>Ngày nhận trợ cấp thực phẩm làm giỏ thực phẩm tăng tới {p(snap[('WI', 'FOODS')]['lift'])}</h2>
  <p>M5 ghi những ngày bang chi trả SNAP (tem phiếu thực phẩm cho hộ thu nhập thấp). Đây là biến chính sách duy nhất trong 5 nguồn, và là thí nghiệm tự nhiên tốt về ràng buộc thanh khoản.</p></div>
  <div class="finding">
    <div class="panel"><h3>Mức tăng lượng bán vào ngày SNAP</h3><p class="sub">Hồi quy log lượng bán theo ngày, có hiệu ứng cố định năm-tháng và thứ trong tuần, loại ngày lễ; sai số HAC</p><div class="chart" id="cSnap"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Lịch SNAP khác nhau giữa các bang. CA chi trả ngày 1–10, TX và WI xen kẽ trong 15 ngày đầu. Nhờ khác biệt này có thể tách hiệu ứng SNAP khỏi hiệu ứng nhận lương đầu tháng. Hiệu ứng tập trung ở Thực phẩm (CA {p(snap[('CA', 'FOODS')]['lift'])}, TX {p(snap[('TX', 'FOODS')]['lift'])}, WI {p(snap[('WI', 'FOODS')]['lift'])}), còn Gia dụng và Sở thích chỉ 1,5–3%.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Nếu hộ làm mượt tiêu dùng theo lý thuyết thu nhập thường xuyên, ngày nhận tiền không làm thay đổi lượng mua. Dữ liệu cho thấy điều ngược lại: hộ có ràng buộc thanh khoản chi ngay khi có tiền. Hiệu ứng lan rất ít sang ngành không được trợ cấp, phù hợp với việc SNAP chỉ dùng được cho thực phẩm. Ở Việt Nam, tương tự là ngày nhận lương và ngày chi trả lương hưu, trợ cấp. Chuỗi nên đặt lịch nhập hàng thiết yếu và khuyến mãi theo các ngày này.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Nhịp chi tiêu theo ngày trong tháng</h3><p class="sub">Tổng lượng bán theo bang, chuẩn hóa theo trung bình tháng (1,0 = mức trung bình)</p><div class="chart" id="cDom"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>WI có răng cưa rõ nhất: các ngày 2, 3, 5, 6, 8, 9, 11, 12, 14, 15 (đúng lịch SNAP của WI) cao hơn hẳn các ngày xen giữa. Đường CA cao đều trong 10 ngày đầu rồi giảm dần.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Nửa cuối tháng thấp hơn đầu tháng cho thấy nhu cầu bị giới hạn bởi dòng tiền của hộ. Chương trình giữ khách cuối tháng (gói tiết kiệm, nhãn riêng giá thấp) có thể bù phần thiếu hụt này.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Ngày lễ: nhiều ngày làm giảm doanh số</h3><p class="sub">M5 · lượng bán ngày lễ so với cùng thứ tuần trước và tuần sau. Ngày 25/12 cửa hàng đóng cửa nên bị loại.</p><div class="chart tall" id="cEvents"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Lượng bán đo trong đúng ngày lễ. Phần mua sắm trước lễ (ví dụ trước Lễ Tạ ơn) nằm ở ngày trước đó, nên ngày lễ trông như giảm. Mô hình dự báo cần biến "ngày trước lễ" chứ không chỉ biến "ngày lễ".</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Lễ Tạ ơn {p(ev['Thanksgiving']['lift'])} và Năm mới {p(ev['NewYear']['lift'])}: hộ đã mua trước và ở nhà nấu ăn hoặc đi thăm gia đình. Lễ Lao động {p(ev['LaborDay']['lift'], 0)}: kỳ nghỉ cuối hè gắn với tiệc ngoài trời. Với Tết Nguyên đán, chuỗi Việt Nam cần mô hình riêng cho 2–3 tuần trước Tết và tuần đóng cửa.</p></div>
    </div>
  </div>
</div></section>

<section class="ch" id="thu-nhap"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 7 · Thu nhập và nhãn riêng</div><h2>Thu nhập tăng một bậc, chi tiêu tăng {p(inc['log_spend_per_level'], 1)} và nhãn riêng giảm {n(-incpl['pl_share_per_level'] * 100, 2)} điểm %</h2>
  <p>CJ là nguồn duy nhất có nhân khẩu học. Thu nhập được mã hóa thứ bậc từ Level1 đến Level12, không có số tiền cụ thể.</p></div>
  <div class="finding">
    <div class="panel"><h3>Chi tiêu tuần và tỷ trọng nhãn riêng theo bậc thu nhập</h3><p class="sub">CJ · {inc['n']} hộ có hồ sơ; hồi quy có kiểm soát quy mô hộ</p><div class="chart" id="cIncome"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Các bậc 10–12 chỉ có 5–11 hộ, nên con số ở đầu cao rất nhiễu. Hệ số hồi quy (sai số chuẩn {n(inc['se'], 3)}) đáng tin hơn từng cột. R² chỉ {n(inc['r2'], 2)}: thu nhập giải thích rất ít phần chênh lệch chi tiêu giữa các hộ, còn lại là thói quen và lòng trung thành với cửa hàng.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Mỗi bậc thu nhập chỉ làm chi tiêu tạp hóa tăng {p(inc['log_spend_per_level'], 1)}, trong khi khoảng cách thu nhập giữa hai bậc thường lớn hơn nhiều. Chi tiêu thực phẩm tăng chậm hơn thu nhập, phù hợp quy luật Engel. Nhãn riêng hành xử như hàng cấp thấp (inferior good): hộ thu nhập cao mua ít hơn. Khi kinh tế đi xuống, tỷ trọng nhãn riêng là chỉ báo sớm cho việc khách hạ cấp chi tiêu.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Chênh giá nhãn riêng và thương hiệu quốc gia</h3><p class="sub">BATF · giá bán bình quân (USD/đơn vị)</p><div class="chart" id="cPL"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Giá bình quân tính bằng doanh thu chia đơn vị, nên chịu ảnh hưởng của cỡ gói. BATF có 1–2 SKU nhãn riêng mỗi ngành với cỡ gói tương đương, nên so sánh ở đây tương đối công bằng.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Nhãn riêng rẻ hơn 30–62%. Ở ngũ cốc nhãn riêng khuyến mãi nhiều hơn thương hiệu (TPR {p(pl_b[('COLD CEREAL', True)]['promo'])} so với {p(pl_b[('COLD CEREAL', False)]['promo'])} số tuần). Nhà bán lẻ dùng nhãn riêng làm công cụ cạnh tranh giá và để có thêm sức mặc cả với nhà sản xuất.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Trung thành thương hiệu trong 4 ngành</h3><p class="sub">Carbo · hộ có ≥ 5 lần mua trong ngành; trung thành = ≥ 80% số lần mua cùng một thương hiệu</p><div class="chart" id="cLoyal"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Chỉ số HHI của ngành: bột bánh {n([h for h in CL['hhi'] if h['commodity']=='pancake mixes'][0]['hhi'], 0)}, sốt {n([h for h in CL['hhi'] if h['commodity']=='pasta sauce'][0]['hhi'], 0)}, mì Ý {n([h for h in CL['hhi'] if h['commodity']=='pasta'][0]['hhi'], 0)}, siro {n([h for h in CL['hhi'] if h['commodity']=='syrups'][0]['hhi'], 0)}. Theo ngưỡng 1.500–2.500, ba ngành đầu tập trung ở mức vừa; siro phân tán hơn.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Bột bánh có {p(loy['pancake mixes']['share_loyal_80'])} hộ trung thành, mì Ý chỉ {p(loy['pasta']['share_loyal_80'])}. Mì Ý gần như hàng đồng nhất, cạnh tranh bằng giá; nhãn riêng chiếm {p(cl_comm['pasta']['private_share'])} doanh thu mì Ý so với {p(cl_comm['pasta sauce']['private_share'])} ở sốt. Ngành đồng nhất nên đẩy nhãn riêng. Ngành trung thành cao nên hợp tác với nhãn dẫn đầu.</p></div>
    </div>
  </div>
</div></section>

<section class="ch" id="hanh-vi"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 8 · Hành vi giỏ hàng</div><h2>Phần lớn số lần ghé là chuyến nhỏ, phần lớn doanh thu đến từ chuyến lớn</h2>
  <p>LGSR có nhãn sẵn cho loại chuyến và độ nhạy giá của giỏ. Đây là dữ liệu mô phỏng, nên được dùng để thử phương pháp và đặt giả thuyết.</p></div>
  <div class="finding">
    <div class="panel"><h3>Số giỏ và doanh thu theo loại chuyến và độ nhạy giá</h3><p class="sub">LGSR · {n(LG['profile']['baskets'])} giỏ</p>
      <div class="seg-toggle" role="group" aria-label="Chọn chiều"><button id="btBasket" aria-pressed="true" data-k="basket_type">Loại chuyến</button><button id="btPs" aria-pressed="false" data-k="price_sens">Độ nhạy giá</button><button id="btMission" aria-pressed="false" data-k="mission">Nhiệm vụ giỏ</button><button id="btFmt" aria-pressed="false" data-k="fmt">Định dạng cửa hàng</button></div>
      <div class="chart" id="cBasket"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Small Shop chiếm {p(lg_bt['Small Shop']['baskets'] / LG['profile']['baskets'])} số giỏ nhưng chỉ {p(lg_bt['Small Shop']['spend'] / LG['profile']['spend'])} doanh thu. Full Shop chỉ {p(lg_bt['Full Shop']['baskets'] / LG['profile']['baskets'])} số giỏ nhưng tạo {p(lg_bt['Full Shop']['spend'] / LG['profile']['spend'])}. Giỏ không thẻ thành viên chiếm {p(lg_fmt['SS']['no_card'])} ở cửa hàng nhỏ (SS), cao hơn mức {p(lg_fmt['LS']['no_card'])} ở cửa hàng lớn.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Giá trị giỏ Full Shop ({n(lg_bt['Full Shop']['aov'], 1)}) gấp khoảng {n(lg_bt['Full Shop']['aov'] / lg_bt['Small Shop']['aov'], 0)} lần Small Shop ({n(lg_bt['Small Shop']['aov'], 1)}). Chuyến mua lớn là nơi chuỗi cạnh tranh về giá với đại siêu thị. Chuyến nhỏ là nơi cạnh tranh về sự tiện lợi với cửa hàng tiện lợi. Hai loại chuyến cần hai chiến lược giá khác nhau.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Bản đồ nhiệt thứ × giờ</h3><p class="sub">LGSR · số giỏ</p><div class="chart" id="cHeat"></div></div>
    <div class="panel"><h3>Nhịp giờ ở ba nguồn</h3><p class="sub">Tỷ lệ số giỏ theo giờ</p><div class="chart" id="cHours"></div></div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Bổ trợ trong giỏ: lift phụ thuộc vào vũ trụ dữ liệu</h3><p class="sub">Carbo · lift = P(A và B) / (P(A)·P(B)); confidence = P(B|A)</p><div class="chart" id="cComp"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Bột bánh + siro có lift {n(comp[('pancake mixes', 'syrups')]['lift'], 2)}. Mì Ý + sốt chỉ {n(comp[('pasta', 'pasta sauce')]['lift'], 2)} dù {p(comp[('pasta', 'pasta sauce')]['conf_b_a'])} giỏ có sốt cũng có mì. Lý do là Carbo chỉ giữ giỏ có ít nhất một trong bốn ngành, nên P(A) và P(B) bị thổi phồng. Chạy luật kết hợp trên dữ liệu đã lọc ngành sẽ cho kết quả sai.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Hàng bổ trợ có độ co giãn chéo âm: giảm giá mì Ý kéo theo lượng bán sốt. Chiến lược "hàng mồi" là giảm giá mặt hàng có cầu bổ trợ cao để thu lợi nhuận từ mặt hàng đi kèm có biên tốt hơn (sốt có giá {n(cl_comm['pasta sauce']['avg_price'], 2)} so với mì {n(cl_comm['pasta']['avg_price'], 2)} USD/đơn vị).</p></div>
    </div>
  </div>
</div></section>

<section class="ch" id="tong-hop"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 9 · Tổng hợp</div><h2>Điều gì lặp lại ở nhiều nguồn độc lập</h2>
  <p>Mức tin cậy tăng theo số nguồn độc lập cùng cho một kết quả. Mỗi thẻ ghi rõ nguồn nào ủng hộ.</p></div>
  <div class="synth">
    <article><div class="who">{chip('cj')}{chip('carbo')}{chip('lgsr')}{chip('m5')}</div><h3>Doanh thu tập trung mạnh</h3><p>20% khách hoặc SKU tạo <b>53–66%</b> doanh thu. Hệ số Gini từ {n(CJ['pareto_households']['gini'], 2)} đến {n(LG['pareto_customers']['gini'], 2)}. Độ tin cậy cao.</p></article>
    <article><div class="who">{chip('cj')}{chip('batf')}{chip('carbo')}</div><h3>Trưng bày và tờ rơi tạo lượng bán khi giá không đổi</h3><p>Trưng bày tăng <b>{p(cause['lift_display'])}–69%</b>, tờ rơi tăng <b>{p(cause['lift_mailer'])}–{p(max(e['lift_feature'] for e in CL['elasticity']))}</b> tùy nguồn và ngành. Giảm giá tạm thời không có tác dụng thêm ngoài mức giá. Độ tin cậy cao.</p></article>
    <article><div class="who">{chip('batf')}{chip('carbo')}{chip('m5')}</div><h3>Độ co giãn giá khác nhau theo ngành</h3><p>Hàng tùy ý, dễ thay thế: <b>−1,3 đến −3,0</b>. Hàng thiết yếu: <b>−0,3 đến −0,5</b>. Giá trị tuyệt đối phụ thuộc cách đo giá. Độ tin cậy trung bình.</p></article>
    <article><div class="who">{chip('m5')}</div><h3>Dòng tiền của hộ quyết định thời điểm mua</h3><p>Ngày SNAP tăng Thực phẩm <b>{p(snap[('CA', 'FOODS')]['lift'])}–{p(snap[('WI', 'FOODS')]['lift'])}</b>. Đầu tháng cao hơn cuối tháng. Chỉ có một nguồn nhưng thiết kế gần với thí nghiệm tự nhiên.</p></article>
    <article><div class="who">{chip('cj')}{chip('batf')}{chip('carbo')}</div><h3>Nhãn riêng là công cụ cạnh tranh giá</h3><p>Rẻ hơn 30–62%. Thu nhập càng cao tỷ trọng càng giảm. Chiếm phần lớn ở ngành đồng nhất (mì Ý {p(cl_comm['pasta']['private_share'])}). Độ tin cậy trung bình đến cao.</p></article>
    <article><div class="who">{chip('cj')}</div><h3>Đo coupon dễ bị nhầm do chọn mẫu</h3><p>Hộ nhận coupon đã chi gấp <b>{n(1 + cds['TypeB']['level_gap'], 1)}–{n(1 + cds['TypeA']['level_gap'], 1)} lần</b> từ trước. Chênh lệch tăng trưởng ≈ 0. Cần thử nghiệm có nhóm đối chứng.</p></article>
  </div>
</div></section>

<section class="ch" id="hanh-dong"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương 10 · Hành động cho chuỗi</div><h2>Từ dữ liệu công khai đến thử nghiệm tại chuỗi siêu thị Việt Nam</h2>
  <p>Kết quả trên đến từ thị trường Mỹ và Anh giai đoạn 2006–2016. Chúng dùng để đặt giả thuyết và chọn phương pháp. Mỗi hành động cần được kiểm chứng lại bằng dữ liệu của chính chuỗi.</p></div>
  <ol class="actions">
    <li><div><h3>Ghi đủ trường mà các nguồn công khai thiếu</h3><p>Hóa đơn có mã khách, giá kệ và giá cơ sở theo ngày, cờ tờ rơi/trưng bày theo cửa hàng-SKU-tuần, tồn kho đầu ngày, giá vốn. Thiếu tồn kho thì không phân biệt được hết hàng với không có cầu; thiếu giá vốn thì không tính được ROI khuyến mãi.</p></div></li>
    <li><div><h3>Ước lượng độ co giãn theo ngành trước khi đổi giá</h3><p>Áp dụng mô hình hiệu ứng cố định như BATF cho 20 ngành hàng đầu. Tăng giá nhẹ ở ngành ít co giãn, dùng nhãn riêng để cạnh tranh ở ngành co giãn mạnh.</p></div></li>
    <li><div><h3>Chuyển ngân sách từ giảm giá sang vị trí kệ và tờ rơi</h3><p>Thử theo cặp cửa hàng: một cửa hàng có trưng bày đầu kệ, một cửa hàng không, cùng mức giá. Đo lượng bán 4 tuần sau để trừ phần mua dồn trước.</p></div></li>
    <li><div><h3>Đặt lịch hàng thiết yếu theo ngày nhận lương</h3><p>Lập lịch theo ngày trả lương phổ biến và ngày chi trả lương hưu, trợ cấp. Thêm biến "ngày trước lễ" và cửa sổ Tết vào mô hình dự báo.</p></div></li>
    <li><div><h3>Mọi chiến dịch CRM phải có nhóm đối chứng</h3><p>Giữ ngẫu nhiên 10% khách đủ điều kiện không nhận ưu đãi. Chỉ tính phần chênh lệch với nhóm đối chứng là hiệu quả của chiến dịch.</p></div></li>
    <li><div><h3>Dự báo theo kiểu nhu cầu</h3><p>SKU bán đều dùng mô hình chuỗi thời gian. SKU gián đoạn dùng Croston/TSB hoặc mô hình phân phối. Đánh giá bằng sai số có trọng số doanh thu (WRMSSE như M5) thay vì MAPE.</p></div></li>
  </ol>
</div></section>
</main>

<footer class="foot"><div class="wrap">
  <b>Nguồn và giấy phép</b>
  <p>dunnhumby Source Files (The Complete Journey, Breakfast at the Frat, Carbo-Loading, Let’s Get Sort-of-Real mẫu 5K khách), tải ngày 07/11/2026 tại dunnhumby.com/source-files. M5 Forecasting Accuracy (Walmart, Kaggle), bản lưu Zenodo DOI 10.5281/zenodo.12636070, CC BY 4.0. Let’s Get Sort-of-Real là dữ liệu mô phỏng. Không bộ nào đại diện trực tiếp cho thị trường Việt Nam.</p>
  <p>Phương pháp: độ co giãn và hiệu ứng khuyến mãi dùng hồi quy log–log với hiệu ứng cố định hai chiều (khử trung bình lặp), sai số chuẩn cụm theo SKU×cửa hàng. Hiệu ứng SNAP dùng hiệu ứng cố định năm-tháng và thứ, sai số HAC. Mã nguồn: research/multisource/. Số liệu: outputs/multisource/results.json.</p>
  <p>Dashboard vận hành chi tiết cho Complete Journey 2017 vẫn ở outputs/FINAL/Retail_Intelligence_Dashboard.html.</p>
</div></footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.5.0/echarts.min.js"></script>
<script>
const D = {json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))};
</script>
<script>
(() => {{
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const pct = (v, d = 0) => (v * 100).toFixed(d).replace('.', ',') + '%';
const num = (v, d = 0) => v.toLocaleString('vi-VN', {{ maximumFractionDigits: d, minimumFractionDigits: d }});
const charts = [];
const T = () => ({{ ink: css('--ink'), muted: css('--muted'), line: css('--line'), surface: css('--surface'), accent: css('--accent'),
  src: k => css('--' + k), body: css('--body') }});
function base(t) {{
  return {{ textStyle: {{ fontFamily: t.body, color: t.ink }}, animationDuration: 700,
    grid: {{ left: 12, right: 24, top: 36, bottom: 28, containLabel: true }},
    tooltip: {{ backgroundColor: t.surface, borderColor: t.line, textStyle: {{ color: t.ink, fontFamily: t.body, fontSize: 12 }}, confine: true }},
    legend: {{ textStyle: {{ color: t.muted, fontSize: 11 }}, top: 0, type: 'scroll', icon: 'circle', itemWidth: 9, itemHeight: 9 }} }};
}}
const ax = (t, o = {{}}) => Object.assign({{ axisLine: {{ lineStyle: {{ color: t.line }} }}, axisTick: {{ show: false }},
  axisLabel: {{ color: t.muted, fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: t.line, type: [3, 4] }} }}, nameTextStyle: {{ color: t.muted, fontSize: 11 }} }}, o);
const defs = {{}};
function reg(id, fn) {{ defs[id] = fn; }}
function renderAll() {{
  const t = T();
  for (const [id, fn] of Object.entries(defs)) {{
    const el = document.getElementById(id); if (!el) continue;
    let c = echarts.getInstanceByDom(el); if (c) c.dispose();
    c = echarts.init(el, null, {{ renderer: 'canvas' }});
    c.setOption(Object.assign(base(t), fn(t)));
    charts.push(c);
  }}
}}
window.addEventListener('resize', () => charts.forEach(c => !c.isDisposed() && c.resize()));

reg('cTimeline', t => {{
  const rows = D.timeline;
  return {{ grid: {{ left: 12, right: 24, top: 10, bottom: 24, containLabel: true }},
    xAxis: ax(t, {{ type: 'time', min: '2006-01-01', max: '2018-03-01' }}), yAxis: ax(t, {{ type: 'category', data: rows.map(r => r.name), inverse: true, splitLine: {{ show: false }} }}),
    tooltip: {{ formatter: p => `<b>${{p.name}}</b><br>${{rows[p.dataIndex].start}} → ${{rows[p.dataIndex].end}}` }},
    series: [{{ type: 'custom', renderItem: (params, api) => {{
      const s = api.coord([api.value(0), api.value(2)]), e = api.coord([api.value(1), api.value(2)]), h = api.size([0, 1])[1] * 0.5;
      return {{ type: 'rect', shape: {{ x: s[0], y: s[1] - h / 2, width: Math.max(e[0] - s[0], 3), height: h, r: 5 }}, style: {{ fill: t.src(rows[params.dataIndex].src) }} }};
    }}, encode: {{ x: [0, 1], y: 2 }}, data: rows.map((r, i) => ({{ name: r.name, value: [r.start, r.end, i] }})) }}] }};
}});

reg('cDemand', t => {{
  const cls = ['Đều (smooth)', 'Thất thường (erratic)', 'Gián đoạn (intermittent)', 'Cục (lumpy)'];
  const cats = ['FOODS', 'HOUSEHOLD', 'HOBBIES'];
  const col = [t.src('cj'), t.src('batf'), t.src('m5'), t.src('carbo')];
  const tot = c => D.demand.filter(d => d.cat === c).reduce((a, b) => a + b.series, 0);
  return {{ legend: {{ top: 0 }}, grid: {{ left: 12, right: 24, top: 40, bottom: 24, containLabel: true }},
    xAxis: ax(t, {{ type: 'value', max: 1, axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
    yAxis: ax(t, {{ type: 'category', data: ['Thực phẩm', 'Gia dụng', 'Sở thích'], splitLine: {{ show: false }} }}),
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, valueFormatter: v => pct(v, 1) }},
    series: cls.map((k, i) => ({{ name: k, type: 'bar', stack: 's', barWidth: '55%', itemStyle: {{ color: col[i] }},
      data: cats.map(c => {{ const r = D.demand.find(d => d.cat === c && d.cls === k); return r ? r.series / tot(c) : 0; }}) }})) }};
}});

reg('cLorenz', t => ({{
  xAxis: ax(t, {{ type: 'value', min: 0, max: 1, name: '% khách / mặt hàng', nameLocation: 'middle', nameGap: 26, axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
  yAxis: ax(t, {{ type: 'value', min: 0, max: 1, axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
  grid: {{ left: 12, right: 24, top: 44, bottom: 36, containLabel: true }},
  tooltip: {{ trigger: 'axis', valueFormatter: v => pct(v, 1), axisPointer: {{ type: 'line' }} }},
  series: [{{ name: 'Phân bổ đều', type: 'line', data: [[0, 0], [1, 1]], symbol: 'none', lineStyle: {{ color: t.muted, type: 'dotted', width: 1 }}, tooltip: {{ show: false }} }},
    ...D.lorenz.map(l => ({{ name: l.name, type: 'line', smooth: true, symbol: 'none', lineStyle: {{ width: 2.4, color: t.src(l.src) }}, itemStyle: {{ color: t.src(l.src) }},
      data: [[0, 0], ...l.p.curve.map(c => [c.pop, c.share])],
      markPoint: l.src === 'cj' ? {{ symbol: 'circle', symbolSize: 9, data: [{{ coord: [0.2, l.p.top20], value: pct(l.p.top20) }}], label: {{ position: 'left', color: t.ink, fontSize: 11, formatter: p => 'top 20%: ' + p.value }} }} : undefined }}))] }}));

reg('cElastic', t => {{
  const rows = D.elasticity.slice().reverse();
  return {{ grid: {{ left: 12, right: 50, top: 10, bottom: 30, containLabel: true }},
    xAxis: ax(t, {{ type: 'value', min: -3.5, max: 0.2, interval: 0.5, axisLabel: {{ color: t.muted, formatter: v => num(v, 1) }} }}),
    yAxis: ax(t, {{ type: 'category', data: rows.map(r => r.name), splitLine: {{ show: false }}, axisLabel: {{ color: t.ink, fontSize: 11 }} }}),
    tooltip: {{ formatter: p => {{ const r = rows[p.dataIndex]; return `<b>${{r.name}}</b><br>Co giãn: ${{num(r.v, 2)}}<br>KTC 95%: ${{num(r.lo, 2)}} → ${{num(r.hi, 2)}}`; }} }},
    series: [{{ type: 'custom', renderItem: (params, api) => {{
        const r = rows[params.dataIndex]; const a = api.coord([r.lo, params.dataIndex]), b = api.coord([r.hi, params.dataIndex]), m = api.coord([r.v, params.dataIndex]);
        const c = t.src(r.src);
        return {{ type: 'group', children: [
          {{ type: 'line', shape: {{ x1: a[0], y1: a[1], x2: Math.max(b[0], a[0] + 2), y2: b[1] }}, style: {{ stroke: c, lineWidth: 3, lineCap: 'round' }} }},
          {{ type: 'circle', shape: {{ cx: m[0], cy: m[1], r: 6 }}, style: {{ fill: c, stroke: t.surface, lineWidth: 2 }} }},
          {{ type: 'text', style: {{ x: Math.max(b[0], m[0]) + 10, y: m[1], text: num(r.v, 2), fill: t.ink, fontSize: 11, verticalAlign: 'middle', fontFamily: t.body }} }}] }};
      }}, data: rows.map((r, i) => [r.v, i]),
      markLine: {{ silent: true, symbol: 'none', lineStyle: {{ color: t.muted, type: 'dashed' }}, label: {{ color: t.muted, fontSize: 10, formatter: 'co giãn đơn vị' }}, data: [{{ xAxis: -1 }}] }} }}] }};
}});

reg('cSeg', t => {{
  const cats = [...new Set(D.seg.map(s => s.category))];
  const segs = ['VALUE', 'MAINSTREAM', 'UPSCALE'], cols = [t.src('batf'), t.src('cj'), t.src('lgsr')];
  return {{ xAxis: ax(t, {{ type: 'category', data: cats.map(c => c.charAt(0) + c.slice(1).toLowerCase()), splitLine: {{ show: false }} }}),
    yAxis: ax(t, {{ type: 'value', name: 'Co giãn', axisLabel: {{ color: t.muted, formatter: v => num(v, 1) }} }}),
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, valueFormatter: v => num(v, 2) }},
    series: segs.map((s, i) => ({{ name: s.charAt(0) + s.slice(1).toLowerCase(), type: 'bar', itemStyle: {{ color: cols[i], borderRadius: [0, 0, 4, 4] }},
      data: cats.map(c => {{ const r = D.seg.find(x => x.category === c && x.segment === s); return r ? r.elasticity : null; }}) }})) }};
}});

reg('cPromo', t => {{
  const rows = D.promo.slice().reverse();
  return {{ grid: {{ left: 12, right: 50, top: 10, bottom: 30, containLabel: true }},
    xAxis: ax(t, {{ type: 'value', axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
    yAxis: ax(t, {{ type: 'category', data: rows.map(r => r.name), splitLine: {{ show: false }}, axisLabel: {{ color: t.ink, fontSize: 10.5 }} }}),
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, valueFormatter: v => pct(v, 1) }},
    series: [{{ type: 'bar', barWidth: '62%', data: rows.map(r => ({{ value: r.v, itemStyle: {{ color: t.src(r.src), borderRadius: r.v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4] }} }})),
      label: {{ show: true, position: 'right', color: t.ink, fontSize: 10, formatter: p => pct(p.value) }} }}] }};
}});

reg('cDepth', t => ({{
  grid: {{ left: 12, right: 24, top: 64, bottom: 28, containLabel: true }},
  xAxis: ax(t, {{ type: 'category', data: D.depth.map(d => d.bin), splitLine: {{ show: false }} }}),
  yAxis: [ax(t, {{ type: 'value', name: 'Đơn vị/tuần' }}), ax(t, {{ type: 'value', name: '% quan sát', splitLine: {{ show: false }}, axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }})],
  tooltip: {{ trigger: 'axis' }},
  series: [{{ name: 'Đơn vị bán / SKU-cửa hàng-tuần', type: 'bar', data: D.depth.map(d => +d.units_per_row.toFixed(1)), itemStyle: {{ color: t.src('batf'), borderRadius: [4, 4, 0, 0] }}, barWidth: '48%' }},
    {{ name: '% số quan sát', type: 'line', yAxisIndex: 1, data: D.depth.map(d => d.rows / D.depth.reduce((a, b) => a + b.rows, 0)), itemStyle: {{ color: t.ink }}, lineStyle: {{ color: t.ink }}, tooltip: {{ valueFormatter: v => pct(v, 1) }} }}] }}));

reg('cCampaign', t => {{
  const types = ['TypeA', 'TypeB', 'TypeC'], cols = [t.src('cj'), t.src('batf'), t.src('m5')];
  return {{ xAxis: ax(t, {{ type: 'value', name: 'Chênh chi tiêu trước chiến dịch', nameLocation: 'middle', nameGap: 26, axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
    yAxis: ax(t, {{ type: 'value', name: 'DiD', axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
    grid: {{ left: 12, right: 24, top: 44, bottom: 36, containLabel: true }},
    tooltip: {{ formatter: p => `Chiến dịch ${{p.data[2]}} (${{p.seriesName}})<br>Chênh trước: ${{pct(p.data[0])}}<br>DiD: ${{pct(p.data[1], 1)}}` }},
    series: types.map((k, i) => ({{ name: k, type: 'scatter', symbolSize: 12, itemStyle: {{ color: cols[i], opacity: 0.85 }},
      data: D.campaign_did.filter(d => d.type === k).map(d => [d.level_gap, d.did_pp, d.campaign]),
      markLine: i === 0 ? {{ silent: true, symbol: 'none', lineStyle: {{ color: t.muted }}, label: {{ show: false }}, data: [{{ yAxis: 0 }}] }} : undefined }})) }};
}});

reg('cSnap', t => {{
  const st = ['CA', 'TX', 'WI'], cats = ['FOODS', 'HOUSEHOLD', 'HOBBIES'], lab = ['Thực phẩm', 'Gia dụng', 'Sở thích'], cols = [t.src('cj'), t.src('m5'), t.src('batf')];
  return {{ xAxis: ax(t, {{ type: 'category', data: st, splitLine: {{ show: false }} }}),
    yAxis: ax(t, {{ type: 'value', axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, valueFormatter: v => pct(v, 1) }},
    series: cats.map((c, i) => ({{ name: lab[i], type: 'bar', itemStyle: {{ color: cols[i], borderRadius: [4, 4, 0, 0] }},
      label: {{ show: true, position: 'top', color: t.ink, fontSize: 10, formatter: p => pct(p.value, 1) }},
      data: st.map(s => D.snap.find(x => x.state === s && x.cat === c).lift) }})) }};
}});

reg('cDom', t => {{
  const cols = [t.src('cj'), t.src('batf'), t.src('m5')];
  return {{ xAxis: ax(t, {{ type: 'category', data: D.dom.map(d => d.dom), name: 'Ngày', splitLine: {{ show: false }} }}),
    yAxis: ax(t, {{ type: 'value', min: 0.85, axisLabel: {{ color: t.muted, formatter: v => num(v, 2) }} }}),
    tooltip: {{ trigger: 'axis', valueFormatter: v => num(v, 3) }},
    series: ['CA', 'TX', 'WI'].map((s, i) => ({{ name: s, type: 'line', symbol: 'none', smooth: 0.2, lineStyle: {{ width: 2, color: cols[i] }}, itemStyle: {{ color: cols[i] }},
      data: D.dom.map(d => d[s + '_idx']),
      markLine: i === 0 ? {{ silent: true, symbol: 'none', lineStyle: {{ color: t.muted, type: 'dashed' }}, label: {{ show: false }}, data: [{{ yAxis: 1 }}] }} : undefined }})) }};
}});

reg('cEvents', t => {{
  const rows = D.events.slice();
  const col = {{ National: t.src('cj'), Religious: t.src('lgsr'), Cultural: t.src('batf'), Sporting: t.src('m5') }};
  return {{ grid: {{ left: 12, right: 50, top: 10, bottom: 30, containLabel: true }},
    xAxis: ax(t, {{ type: 'value', axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
    yAxis: ax(t, {{ type: 'category', data: rows.map(r => r.event), splitLine: {{ show: false }}, axisLabel: {{ color: t.ink, fontSize: 10.5 }} }}),
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, formatter: p => `<b>${{rows[p[0].dataIndex].event}}</b> (${{rows[p[0].dataIndex].type}})<br>${{pct(p[0].value, 1)}} · ${{rows[p[0].dataIndex].n}} năm` }},
    series: [{{ type: 'bar', barWidth: '64%', data: rows.map(r => ({{ value: r.lift, itemStyle: {{ color: col[r.type], borderRadius: r.lift >= 0 ? [0, 3, 3, 0] : [3, 0, 0, 3] }} }})),
      label: {{ show: true, position: 'right', color: t.muted, fontSize: 9.5, formatter: p => pct(p.value) }} }}] }};
}});

reg('cIncome', t => {{
  const d = D.income.filter(x => x.level.startsWith('Level'));
  return {{ xAxis: ax(t, {{ type: 'category', data: d.map(x => x.level.replace('Level', 'L')), splitLine: {{ show: false }} }}),
    yAxis: [ax(t, {{ type: 'value', name: 'USD/tuần' }}), ax(t, {{ type: 'value', name: 'Nhãn riêng', min: 0.1, max: 0.35, splitLine: {{ show: false }}, axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }})],
    tooltip: {{ trigger: 'axis', formatter: p => {{ const r = d[p[0].dataIndex]; return `<b>${{r.level}}</b> · ${{r.households}} hộ<br>Chi tiêu/tuần: ${{num(r.weekly_spend, 1)}} USD<br>Giá trị giỏ: ${{num(r.basket_value, 1)}} USD<br>Nhãn riêng: ${{pct(r.pl_share, 1)}}<br>Tỷ lệ giảm giá: ${{pct(r.disc_rate, 1)}}`; }} }},
    series: [{{ name: 'Chi tiêu/tuần (trung vị)', type: 'bar', data: d.map(x => x.weekly_spend), itemStyle: {{ color: t.src('cj'), borderRadius: [4, 4, 0, 0] }}, barWidth: '56%' }},
      {{ name: 'Tỷ trọng nhãn riêng', type: 'line', yAxisIndex: 1, data: d.map(x => x.pl_share), itemStyle: {{ color: t.accent }}, lineStyle: {{ width: 2.4, color: t.accent }}, symbolSize: 7 }}] }};
}});

reg('cPL', t => {{
  const cats = [...new Set(D.pl.map(x => x.CATEGORY))];
  const g = (c, b) => D.pl.find(x => x.CATEGORY === c && x.is_pl === b);
  return {{ xAxis: ax(t, {{ type: 'category', data: cats.map(c => c.charAt(0) + c.slice(1).toLowerCase()), splitLine: {{ show: false }} }}),
    yAxis: ax(t, {{ type: 'value', name: 'USD/đơn vị' }}),
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, valueFormatter: v => num(v, 2) + ' USD' }},
    series: [{{ name: 'Thương hiệu quốc gia', type: 'bar', data: cats.map(c => g(c, false).avg_price), itemStyle: {{ color: t.src('m5'), borderRadius: [4, 4, 0, 0] }} }},
      {{ name: 'Nhãn riêng', type: 'bar', data: cats.map(c => g(c, true).avg_price), itemStyle: {{ color: t.src('batf'), borderRadius: [4, 4, 0, 0] }},
        label: {{ show: true, position: 'top', color: t.ink, fontSize: 10, formatter: p => '−' + pct(1 - p.value / g(cats[p.dataIndex], false).avg_price) }} }}] }};
}});

reg('cLoyal', t => {{
  const d = D.loyalty, lab = {{ 'pancake mixes': 'Bột bánh', 'pasta': 'Mì Ý', 'pasta sauce': 'Sốt mì', 'syrups': 'Siro' }};
  return {{ xAxis: ax(t, {{ type: 'category', data: d.map(x => lab[x.commodity]), splitLine: {{ show: false }} }}),
    yAxis: ax(t, {{ type: 'value', max: 1, axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, valueFormatter: v => pct(v, 1) }},
    series: [{{ name: 'Trung thành (≥80%)', type: 'bar', stack: 's', data: d.map(x => x.share_loyal_80), itemStyle: {{ color: t.src('cj') }} }},
      {{ name: 'Ở giữa', type: 'bar', stack: 's', data: d.map(x => 1 - x.share_loyal_80 - x.share_switcher_50), itemStyle: {{ color: t.line }} }},
      {{ name: 'Hay đổi (<50%)', type: 'bar', stack: 's', data: d.map(x => x.share_switcher_50), itemStyle: {{ color: t.src('carbo') }} }}] }};
}});

let basketKey = 'basket_type';
reg('cBasket', t => {{
  const d = D[basketKey].filter(x => x.level !== 'XX' && x.level !== '(trống)');
  const tb = d.reduce((a, b) => a + b.baskets, 0), ts = d.reduce((a, b) => a + b.spend, 0);
  return {{ xAxis: ax(t, {{ type: 'category', data: d.map(x => x.level), splitLine: {{ show: false }} }}),
    yAxis: [ax(t, {{ type: 'value', axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}), ax(t, {{ type: 'value', name: 'Giá trị giỏ', splitLine: {{ show: false }} }})],
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
    series: [{{ name: '% số giỏ', type: 'bar', data: d.map(x => x.baskets / tb), itemStyle: {{ color: t.src('lgsr'), borderRadius: [4, 4, 0, 0] }}, tooltip: {{ valueFormatter: v => pct(v, 1) }} }},
      {{ name: '% doanh thu', type: 'bar', data: d.map(x => x.spend / ts), itemStyle: {{ color: t.accent, borderRadius: [4, 4, 0, 0] }}, tooltip: {{ valueFormatter: v => pct(v, 1) }} }},
      {{ name: 'Giá trị giỏ TB', type: 'line', yAxisIndex: 1, data: d.map(x => x.aov), itemStyle: {{ color: t.ink }}, lineStyle: {{ color: t.ink }}, tooltip: {{ valueFormatter: v => num(v, 2) }} }}] }};
}});
document.querySelectorAll('.seg-toggle button').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('.seg-toggle button').forEach(x => x.setAttribute('aria-pressed', x === b));
  basketKey = b.dataset.k; const el = document.getElementById('cBasket'); const c = echarts.getInstanceByDom(el); const t = T();
  c.setOption(Object.assign(base(t), defs.cBasket(t)), true);
}}));

reg('cHeat', t => {{
  const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
  const hrs = [...new Set(D.heat.map(h => h.hr))].sort((a, b) => a - b);
  const max = Math.max(...D.heat.map(h => h.baskets));
  return {{ grid: {{ left: 12, right: 24, top: 10, bottom: 56, containLabel: true }},
    xAxis: ax(t, {{ type: 'category', data: hrs, splitLine: {{ show: false }}, name: 'Giờ', nameLocation: 'middle', nameGap: 24 }}),
    yAxis: ax(t, {{ type: 'category', data: days, splitLine: {{ show: false }}, inverse: true }}),
    visualMap: {{ min: 0, max, calculable: false, orient: 'horizontal', left: 'center', bottom: 0, itemHeight: 140, itemWidth: 10, textStyle: {{ color: t.muted, fontSize: 10 }},
      inRange: {{ color: [t.surface, t.src('cj2'), t.src('cj')] }} }},
    tooltip: {{ formatter: p => `${{days[p.data[1]]}} ${{hrs[p.data[0]]}}h: ${{num(p.data[2])}} giỏ` }},
    series: [{{ type: 'heatmap', data: D.heat.map(h => [hrs.indexOf(h.hr), h.wd - 1, h.baskets]), itemStyle: {{ borderColor: t.surface, borderWidth: 1 }} }}] }};
}});

reg('cHours', t => {{
  const norm = arr => {{ const s = arr.reduce((a, b) => a + b.baskets, 0); return arr.map(x => [x.hr_ ?? x.hr, x.baskets / s]); }};
  const lg = {{}}; D.heat.forEach(h => lg[h.hr] = (lg[h.hr] || 0) + h.baskets);
  const lgArr = Object.entries(lg).map(([h, b]) => ({{ hr: +h, baskets: b }}));
  return {{ xAxis: ax(t, {{ type: 'value', min: 0, max: 23, interval: 3, name: 'Giờ', nameLocation: 'middle', nameGap: 24 }}),
    yAxis: ax(t, {{ type: 'value', axisLabel: {{ color: t.muted, formatter: v => pct(v) }} }}),
    grid: {{ left: 12, right: 24, top: 40, bottom: 36, containLabel: true }},
    tooltip: {{ trigger: 'axis', valueFormatter: v => pct(v, 1) }},
    series: [['Complete Journey', norm(D.hours.cj), 'cj'], ['Carbo-Loading', norm(D.hours.carbo), 'carbo'], ['LGSR (mô phỏng)', norm(lgArr), 'lgsr']].map(([n, d, k]) => ({{
      name: n, type: 'line', smooth: true, symbol: 'none', data: d.sort((a, b) => a[0] - b[0]), lineStyle: {{ width: 2.2, color: t.src(k), type: k === 'lgsr' ? 'dashed' : 'solid' }}, itemStyle: {{ color: t.src(k) }} }})) }};
}});

reg('cComp', t => {{
  const lab = {{ 'pancake mixes': 'Bột bánh', 'pasta': 'Mì Ý', 'pasta sauce': 'Sốt', 'syrups': 'Siro' }};
  const d = D.complement.slice().sort((a, b) => a.lift - b.lift);
  return {{ grid: {{ left: 12, right: 40, top: 36, bottom: 24, containLabel: true }},
    xAxis: ax(t, {{ type: 'value', axisLabel: {{ color: t.muted, formatter: v => num(v, 1) }} }}),
    yAxis: ax(t, {{ type: 'category', data: d.map(x => lab[x.a] + ' + ' + lab[x.b]), splitLine: {{ show: false }}, axisLabel: {{ color: t.ink }} }}),
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, formatter: p => {{ const r = d[p[0].dataIndex]; return `<b>${{lab[r.a]}} + ${{lab[r.b]}}</b><br>Lift: ${{num(r.lift, 2)}}<br>Support: ${{pct(r.support, 1)}}<br>P(${{lab[r.b]}}|${{lab[r.a]}}): ${{pct(r.conf_a_b, 1)}}<br>P(${{lab[r.a]}}|${{lab[r.b]}}): ${{pct(r.conf_b_a, 1)}}`; }} }},
    series: [{{ name: 'Lift', type: 'bar', barWidth: '55%', data: d.map(x => ({{ value: x.lift, itemStyle: {{ color: x.lift > 1 ? t.src('carbo') : t.src('carbo2'), borderRadius: [0, 4, 4, 0] }} }})),
      label: {{ show: true, position: 'right', color: t.ink, fontSize: 10, formatter: p => num(p.value, 2) }},
      markLine: {{ silent: true, symbol: 'none', lineStyle: {{ color: t.muted, type: 'dashed' }}, label: {{ color: t.muted, formatter: 'độc lập = 1' }}, data: [{{ xAxis: 1 }}] }} }}] }};
}});

function boot() {{
  if (!window.echarts) {{ document.querySelectorAll('.chart').forEach(el => el.innerHTML = '<p style="color:var(--muted);padding:24px">Biểu đồ cần kết nối mạng để tải thư viện ECharts.</p>'); return; }}
  renderAll();
}}
boot();
const mq = matchMedia('(prefers-color-scheme: dark)');
mq.addEventListener?.('change', () => window.echarts && renderAll());
new MutationObserver(() => window.echarts && renderAll()).observe(document.documentElement, {{ attributes: true, attributeFilter: ['data-theme'] }});

// Mục lục theo vị trí cuộn
const links = [...document.querySelectorAll('.toc a')];
const io = new IntersectionObserver(es => es.forEach(e => {{ if (e.isIntersecting) links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id)); }}), {{ rootMargin: '-40% 0px -55% 0px' }});
document.querySelectorAll('section.ch').forEach(s => io.observe(s));

// Nền mở đầu: các chấm đại diện 5 nguồn, trôi chậm
const cv = document.getElementById('heroCanvas'), ctx = cv.getContext('2d');
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
let W, H, pts = [];
function size() {{ const r = cv.getBoundingClientRect(); W = cv.width = r.width * devicePixelRatio; H = cv.height = r.height * devicePixelRatio;
  const keys = ['cj', 'batf', 'carbo', 'lgsr', 'm5']; pts = Array.from({{ length: 90 }}, (_, i) => ({{ x: Math.random() * W, y: Math.random() * H, r: (1 + Math.random() * 2.4) * devicePixelRatio, k: keys[i % 5], vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25 }})); }}
function draw() {{ ctx.clearRect(0, 0, W, H); const cols = {{}}; ['cj', 'batf', 'carbo', 'lgsr', 'm5'].forEach(k => cols[k] = css('--' + k));
  for (let i = 0; i < pts.length; i++) {{ const a = pts[i];
    for (let j = i + 1; j < pts.length; j++) {{ const b = pts[j], dx = a.x - b.x, dy = a.y - b.y, d = Math.hypot(dx, dy);
      if (d < 120 * devicePixelRatio && a.k !== b.k) {{ ctx.strokeStyle = cols[a.k]; ctx.globalAlpha = (1 - d / (120 * devicePixelRatio)) * .35; ctx.lineWidth = devicePixelRatio * .6; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }} }}
    ctx.globalAlpha = .9; ctx.fillStyle = cols[a.k]; ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, 7); ctx.fill();
    if (!reduce) {{ a.x += a.vx; a.y += a.vy; if (a.x < 0 || a.x > W) a.vx *= -1; if (a.y < 0 || a.y > H) a.vy *= -1; }} }}
  if (!reduce) requestAnimationFrame(draw); }}
size(); draw(); addEventListener('resize', () => {{ size(); if (reduce) draw(); }});
}})();
</script>
"""

import html_extra  # noqa: E402

html = html_extra.extend(html, sys.modules[__name__])
out = OUT / "Phan_tich_da_nguon.html"
out.write_text(html, encoding="utf-8")
print(out, len(html) // 1024, "KB")

# Bản HTML độc lập đầy đủ (doctype, viewport) để mở trực tiếp và chụp màn hình
DEP = OUT / "web"
DEP.mkdir(parents=True, exist_ok=True)
(DEP / "index.html").write_text(
    '<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
    '</head>\n<body>\n' + html + '\n</body>\n</html>\n', encoding="utf-8")
