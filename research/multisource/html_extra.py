"""Phần mở rộng cho trang HTML: các chương và biểu đồ từ results_deep.json.
build_html.py gọi extend(html, ctx) để chèn vào trang gốc."""
from __future__ import annotations

import json
import re


def extend(html: str, H) -> str:
    n, p = H.n, H.p
    D2 = json.loads((H.OUT / "results_deep.json").read_text(encoding="utf-8"))
    cj2, ba2, m52, cl2 = D2["cj"], D2["batf"], D2["m5"], D2["carbo"]
    traj = {t["traj"]: t for t in cj2["trajectory"]}
    gd = cj2["growth_decomp"]
    rfm = {x["segment"]: x for x in cj2["rfm"]}
    ps = cj2["pasta_sauce_full"]
    dyn = {x["category"]: x for x in ba2["dynamics"]}
    ler = {x["category"]: x for x in ba2["lerner"]}
    fc = sorted(m52["forecast"], key=lambda x: x["wrmsse_item"])
    best = fc[0]
    snaive = next(x for x in m52["forecast"] if x["model"] == "Naive mùa vụ 7 ngày")
    pcf = {x["cat"]: x for x in m52["price_change_freq"]}
    pcs = {x["cat"]: x for x in m52["price_change_size"]}
    infl = m52["inflation"]
    infl_avg = {c: sum(r_[c] for r_ in infl if r_.get(c) is not None) / max(1, sum(1 for r_ in infl if r_.get(c) is not None)) for c in ["FOODS", "HOUSEHOLD", "HOBBIES"]}
    rival_rng = (min(-x["rival_promo"] for x in ba2["dynamics"]), max(-x["rival_promo"] for x in ba2["dynamics"]))
    gbm = next(x for x in m52["forecast"] if x["model"].startswith("GBM"))
    ma28 = next(x for x in m52["forecast"] if x["model"] == "Trung bình 28 ngày")
    imp = m52["forecast_importance"][:3]

    data2 = {
        "periods": cj2["periods"], "traj": cj2["trajectory"], "trajDept": cj2["trajectory_dept"], "rfm": cj2["rfm"],
        "rules": cj2["rules_top_lift"], "dyn": ba2["dynamics"], "sim": ba2["profit_sim"], "lerner": ba2["lerner"],
        "pcf": m52["price_change_freq"], "pch": m52["price_change_hist"], "infl": infl,
        "fc": m52["forecast"], "fcTotal": m52["forecast_total"], "fcImp": m52["forecast_importance"], "fcCat": m52["forecast_by_cat"],
        "switch": cl2,
    }

    sec_customers = f"""
<section class="ch" id="khach-hang"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương · Khách hàng theo thời gian</div><h2>Doanh thu panel tăng {p(gd['sales'] and (2.718281828 ** gd['sales'] - 1))} chủ yếu nhờ giỏ lớn hơn</h2>
  <p>Complete Journey theo dõi cùng 2.500 hộ trong 102 tuần. Tăng trưởng được tách thành ba thành phần nhân với nhau: số hộ hoạt động × số chuyến mỗi hộ × giá trị mỗi giỏ.</p></div>
  <div class="finding">
    <div class="panel"><h3>Ba động lực của doanh thu theo chu kỳ 4 tuần</h3><p class="sub">Chỉ số = 100 ở kỳ 3 (tuần 9–12)</p><div class="chart" id="cPeriods"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Hai kỳ đầu thấp do hộ được đưa vào panel dần dần, nên báo cáo so kỳ 3–8 với kỳ 20–25. Phân rã theo log: tổng tăng {n(gd['sales'] * 100, 1)} điểm log = số hộ {n(gd['hh'] * 100, 1)} + chuyến/hộ {n(gd['trips_per_hh'] * 100, 1)} + giá trị giỏ {n(gd['aov'] * 100, 1)} (sai lệch nhỏ do lấy trung bình).</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Hơn một nửa mức tăng đến từ giá trị giỏ, nghĩa là hộ dồn thêm chi tiêu vào cửa hàng (tăng thị phần ví), không phải đến thường xuyên hơn. Giá trị giỏ cũng chứa yếu tố giá: phần lạm phát giá bán lẻ thực phẩm ở Mỹ khoảng 2–3%/năm cần được trừ trước khi gọi đây là tăng trưởng thực.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Quỹ đạo của từng hộ: nửa đầu so với nửa sau</h3><p class="sub">{n(cj2['trajectory_n'])} hộ có mặt từ 120 ngày đầu; cột là số hộ, đường là chênh doanh thu (USD)</p><div class="chart" id="cTraj"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>{n(traj['Tăng chi (>+20%)']['households'])} hộ tăng chi hơn 20%, {n(traj['Giảm chi (<−20%)']['households'])} hộ giảm, {n(traj['Rời bỏ (≥8 tuần không mua)']['households'])} hộ không mua trong 8 tuần cuối. Số hộ tăng chi nhiều bất thường có thể do hộ dùng thẻ thành viên đều hơn theo thời gian, không hẳn là chi tiêu thật tăng.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Nhóm giảm chi và rời bỏ mất {n(-(traj['Giảm chi (<−20%)']['delta'] + traj['Rời bỏ (≥8 tuần không mua)']['delta']), 0)} USD giữa hai nửa, bằng {p(-(traj['Giảm chi (<−20%)']['delta'] + traj['Rời bỏ (≥8 tuần không mua)']['delta']) / traj['Tăng chi (>+20%)']['delta'])} phần tăng của nhóm tăng chi. Giữ chân rẻ hơn thu hút: phát hiện sớm hộ bắt đầu giảm chi (chương rủi ro rời bỏ trong dashboard cũ) có giá trị kinh tế trực tiếp.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Phân khúc RFM tại cuối kỳ</h3><p class="sub">R = số ngày từ lần mua cuối, F = số giỏ, M = tổng chi; chấm điểm theo nhóm 20%</p><div class="chart" id="cRfm"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>RFM chỉ dùng ba trường có sẵn ở mọi hệ thống POS có mã khách, nên chuyển sang chuỗi Việt Nam ngay được. Ngưỡng theo nhóm 20% là tương đối: cùng một hộ có thể đổi phân khúc khi tập khách thay đổi.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>"Nhà vô địch" chiếm {p(rfm['Nhà vô địch']['hh_share'])} số hộ nhưng {p(rfm['Nhà vô địch']['rev_share'])} doanh thu. Nhóm "có nguy cơ mất" chỉ {p(rfm['Có nguy cơ mất (giá trị cao)']['hh_share'])} số hộ nhưng mỗi hộ chi bình quân {n(rfm['Có nguy cơ mất (giá trị cao)']['avg_m'], 0)} USD, cao hơn nhóm trung thành. Đây là nơi chi phí giữ chân mang lại lợi ích lớn nhất.</p></div>
    </div>
  </div>
</div></section>
"""

    sec_forecast = f"""
<section class="ch" id="du-bao"><div class="wrap">
  <div class="ch-head"><div class="eyebrow">Chương · Dự báo</div><h2>Học máy giảm sai số {p(1 - best['wrmsse_item'] / snaive['wrmsse_item'])} so với lặp lại tuần trước, nhưng mô hình đơn giản đã gần bằng</h2>
  <p>Bài toán M5: dự báo 28 ngày cuối (23/04–22/05/2016) cho {n(H.M5['profile']['series'])} chuỗi SKU-cửa hàng. Đánh giá bằng RMSSE có trọng số doanh thu (WRMSSE cấp SKU, cách M5 chấm điểm) và WAPE.</p></div>
  <div class="finding">
    <div class="panel"><h3>So sánh mô hình</h3><p class="sub">Thấp hơn là tốt hơn. GBM huấn luyện trên {n(m52['forecast_train_rows'])} quan sát lấy mẫu từ 420 ngày trước kỳ kiểm tra</p><div class="chart" id="cFc"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Mô hình chỉ dùng thông tin có trước ngày dự báo ít nhất 28 ngày (độ trễ ≥ 28), nên không rò rỉ tương lai và dự báo được cả 28 ngày một lần. Biến quan trọng nhất: {", ".join(x["feature"] for x in imp)}. Sai số theo ngành cao nhất ở Sở thích, nơi {p(H.zero['HOBBIES'])} ngày bằng 0.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Tốt nhất là {best['model']} (WRMSSE {n(best['wrmsse_item'], 3)}, WAPE {p(best['wape'])}), nhưng trung bình 28 ngày đơn giản chỉ kém {p(ma28['wrmsse_item'] / best['wrmsse_item'] - 1, 1)} ở cấp SKU. Khác biệt lớn nằm ở cấp tổng: sai số ngày của GBM là {n(gbm['rmse_total_daily'])} đơn vị so với {n(ma28['rmse_total_daily'])} của trung bình 28 ngày, vì GBM bắt được nhịp cuối tuần. Với cùng mức phục vụ, tồn kho an toàn tỷ lệ với độ lệch chuẩn sai số, nên chuỗi nên bắt đầu bằng mô hình đơn giản cho từng SKU và dùng học máy cho kế hoạch tổng (nhân sự, vận tải, nhập hàng theo ngành).</p></div>
    </div>
  </div>
  <div class="finding full">
    <div class="panel"><h3>Tổng lượng bán 28 ngày: thực tế và dự báo</h3><p class="sub">Tổng toàn bộ 30.490 chuỗi theo ngày</p><div class="chart" id="cFcLine"></div></div>
  </div>
</div></section>
"""

    add_price = f"""
  <div class="finding">
    <div class="panel"><h3>Biên lợi nhuận ngụ ý theo quy tắc Lerner</h3><p class="sub">BATF · (P − MC)/P = 1/|e| nếu nhà bán lẻ định giá tối ưu cho từng SKU; vạch là biên hòa vốn khi giảm giá 20%</p><div class="chart" id="cLerner"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Độ co giãn ở đây là của từng SKU, đã gồm phần khách chuyển từ SKU khác sang. Co giãn của cả ngành sẽ thấp hơn, nên biên ngụ ý cho cả ngành cao hơn con số trên. Không có giá vốn để kiểm tra trực tiếp.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Pizza đông lạnh co giãn mạnh nhất nên biên tối ưu chỉ {p(ler['FROZEN PIZZA']['implied_margin'])}; nước súc miệng {p(ler['ORAL HYGIENE PRODUCTS']['implied_margin'])}. Giảm giá 20% chỉ có lãi khi biên hiện tại thấp hơn {p(ler['FROZEN PIZZA']['breakeven_margin_20pct_cut'])} (pizza) hoặc {p(ler['COLD CEREAL']['breakeven_margin_20pct_cut'])} (ngũ cốc). Đây là cách nối độ co giãn với quyết định giá khi có giá vốn thật.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Giá thay đổi thưa và theo bước lớn</h3><p class="sub">M5 · {n(H.M5['profile']['price_rows'])} quan sát giá tuần; phân bố mức thay đổi khi giá đổi</p><div class="chart" id="cPch"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Chỉ {p(pcf['FOODS']['freq'], 1)} tuần SKU-cửa hàng Thực phẩm có đổi giá (Gia dụng {p(pcf['HOUSEHOLD']['freq'], 1)}, Sở thích {p(pcf['HOBBIES']['freq'], 1)}). Khi đổi, trung vị thay đổi là {p(pcs['FOODS']['median_abs'], 1)}. Biến động giá ít nên ước lượng co giãn từ M5 kém chính xác hơn BATF.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Giá cứng là dấu hiệu của chi phí thay đổi giá (menu cost: in nhãn, cập nhật hệ thống, rủi ro làm khách khó chịu). Giá giữ nguyên trung bình khoảng {n(m52['price_change_freq'] and 1 / pcf['FOODS']['freq'], 0)} tuần ở Thực phẩm. Lạm phát giá bình quân năm của cùng SKU-cửa hàng: Thực phẩm {p(infl_avg['FOODS'], 1)}, Gia dụng {p(infl_avg['HOUSEHOLD'], 1)}, Sở thích {p(infl_avg['HOBBIES'], 1)}.</p></div>
    </div>
  </div>
"""

    add_promo = f"""
  <div class="finding">
    <div class="panel"><h3>Khuyến mãi của đối thủ và tuần sau khuyến mãi</h3><p class="sub">BATF · hệ số trong cùng mô hình hiệu ứng cố định; rival = tỷ lệ SKU khác cùng ngành đang khuyến mãi</p><div class="chart" id="cDyn"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Mô hình chỉ dùng chuỗi tuần liên tiếp và thêm biến trễ khuyến mãi 1–2 tuần. Nếu khách tích trữ, hệ số trễ sẽ âm. Kết quả: trễ 1 tuần dương nhẹ (+1 đến +4%), trễ 2 tuần gần 0. BATF không cho thấy mua dồn rõ ràng, có thể do khuyến mãi thường kéo dài nhiều tuần liên tiếp.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Khi tất cả SKU khác cùng ngành khuyến mãi, lượng bán của một SKU giảm {p(rival_rng[0])}–{p(rival_rng[1])} (mạnh nhất ở ngũ cốc). Đây là ăn mòn lẫn nhau (cannibalization): một phần lượng tăng của SKU khuyến mãi lấy từ SKU khác trong cùng cửa hàng. Đánh giá khuyến mãi phải tính ở cấp ngành, không chỉ ở SKU được giảm giá.</p></div>
    </div>
  </div>
  <div class="finding">
    <div class="panel"><h3>Mô phỏng lợi nhuận khi giảm giá</h3><p class="sub">Dùng độ co giãn và hiệu ứng trưng bày đã ước lượng; biên gộp là giả định vì dữ liệu không có giá vốn</p>
      <div class="sim-ctl"><div class="seg-toggle" role="group" aria-label="Biên gộp"><span class="lbl">Biên gộp</span><button id="simM20" data-m="0.2" aria-pressed="false">20%</button><button id="simM30" data-m="0.3" aria-pressed="true">30%</button><button id="simM40" data-m="0.4" aria-pressed="false">40%</button></div>
      <div class="seg-toggle" role="group" aria-label="Mức giảm giá"><span class="lbl">Giảm giá</span><button id="simC10" data-c="0.1" aria-pressed="true">10%</button><button id="simC20" data-c="0.2" aria-pressed="false">20%</button><button id="simC30" data-c="0.3" aria-pressed="false">30%</button></div></div>
      <div class="chart" id="cSim"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Lượng bán mới = (1 − mức giảm)^e; trường hợp có trưng bày nhân thêm hiệu ứng trưng bày. Lợi nhuận = (biên − mức giảm) × lượng bán, so với lợi nhuận khi không giảm. Mô phỏng chưa trừ ăn mòn SKU khác, nên là cận trên.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Ở biên 30%, giảm giá 10% đơn thuần làm giảm lợi nhuận ở cả bốn ngành; chỉ khi kèm trưng bày thì ngũ cốc, pizza, snack mới có lãi. Giảm 20% chỉ có lãi ở biên 40%, có trưng bày, và chỉ với ngũ cốc và pizza (hai ngành co giãn mạnh nhất). Tiền khuyến mãi nên đi kèm vị trí kệ, và mức giảm phải nhỏ hơn biên một khoảng đủ lớn.</p></div>
    </div>
  </div>
"""

    add_switch = f"""
  <div class="finding">
    <div class="panel"><h3>Ma trận chuyển đổi thương hiệu</h3><p class="sub">Carbo · xác suất lần mua kế tiếp của cùng hộ thuộc thương hiệu ở cột, cho biết lần trước là thương hiệu ở hàng</p>
      <div class="seg-toggle" role="group" aria-label="Chọn ngành"><button id="swSauce" data-s="pasta sauce" aria-pressed="true">Sốt mì Ý</button><button id="swPasta" data-s="pasta" aria-pressed="false">Mì Ý</button></div>
      <div class="chart" id="cSwitch"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><p>Đường chéo là tỷ lệ mua lặp lại. Thị phần dừng tính từ ma trận (vector riêng) gần bằng thị phần hiện tại, nghĩa là thị trường đang ở trạng thái cân bằng trong 2 năm quan sát: không thương hiệu nào đang tăng hay giảm thị phần một cách hệ thống.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Ragu giữ lại {p(cl2['pasta sauce']['repeat']['Ragu'])} khách sốt, nhãn riêng giữ {p(cl2['pasta']['repeat']['Private Label'])} khách mì Ý: ở ngành đồng nhất, khách quen mua hàng rẻ nhất trên kệ. Các thương hiệu nhỏ giữ chân kém (30–45%), nên khuyến mãi của họ chủ yếu tạo lượt mua thử rồi khách quay về thương hiệu cũ.</p></div>
    </div>
  </div>
"""

    add_rules = f"""
  <div class="finding">
    <div class="panel"><h3>Luật kết hợp trên giỏ đầy đủ</h3><p class="sub">CJ · {n(cj2['baskets_n'])} giỏ, 60 nhóm hàng phổ biến nhất, cặp xuất hiện ≥ 1.000 giỏ; 15 cặp có lift cao nhất</p><div class="chart tall" id="cRules"></div></div>
    <div class="lens">
      <div class="d"><div class="tag">Góc dữ liệu</div><span class="big">{n(ps['lift'], 1)} so với {n(H.comp[('pasta', 'pasta sauce')]['lift'], 2)}</span><p>là lift của mì Ý + sốt trên giỏ đầy đủ (CJ) so với trên dữ liệu đã lọc 4 ngành (Carbo). Cùng một cặp hàng, kết luận ngược nhau. Đây là ví dụ rõ nhất cho việc phạm vi dữ liệu quyết định kết quả.</p></div>
      <div class="e"><div class="tag">Góc kinh tế</div><p>Các cặp lift cao là bữa ăn hoàn chỉnh: mì + sốt, phô mai + thịt nguội, cà chua + rau salad, xúc xích + bánh mì. Khách mua giải pháp cho một bữa ăn, không mua từng món. Trưng bày theo bữa ăn và khuyến mãi gói tận dụng độ co giãn chéo âm giữa các món bổ trợ.</p></div>
    </div>
  </div>
"""

    synth_extra = f"""
    <article><div class="who">{H.chip('batf')}</div><h3>Khuyến mãi ăn mòn SKU cùng ngành</h3><p>Đối thủ cùng ngành khuyến mãi làm lượng bán giảm <b>{p(rival_rng[0])}–{p(rival_rng[1])}</b>. Đo hiệu quả ở cấp ngành. Độ tin cậy trung bình.</p></article>
    <article><div class="who">{H.chip('m5')}</div><h3>Học máy cải thiện dự báo rõ rệt</h3><p>{best['model']} giảm WRMSSE <b>{p(1 - best['wrmsse_item'] / snaive['wrmsse_item'])}</b> so với naive mùa vụ; trung bình 28 ngày chỉ kém {p(ma28['wrmsse_item'] / best['wrmsse_item'] - 1, 1)}. Một kỳ kiểm tra 28 ngày, cần thêm kỳ để khẳng định.</p></article>
    <article><div class="who">{H.chip('cj')}{H.chip('carbo')}</div><h3>Phạm vi dữ liệu quyết định kết luận giỏ hàng</h3><p>Lift mì Ý + sốt <b>{n(ps['lift'], 1)}</b> trên giỏ đầy đủ, <b>{n(H.comp[('pasta', 'pasta sauce')]['lift'], 2)}</b> trên dữ liệu lọc ngành. Độ tin cậy cao.</p></article>
"""

    css_extra = """
.sim-ctl { display: flex; flex-wrap: wrap; gap: 8px 16px; }
.seg-toggle .lbl { font: 600 0.7rem/1 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); align-self: center; padding: 0 6px 0 8px; }
.shot-mode .toc, .shot-mode footer.foot { display: none; }
.shot-mode section.ch { padding-block: 24px 4px; }
"""

    js_extra = r"""
const D2 = __D2__;
reg('cPeriods', t => {
  const p = D2.periods, b = p[2];
  const idx = k => p.map(x => +(100 * x[k] / b[k]).toFixed(1));
  const ser = [['Doanh thu', 'sales', t.ink], ['Hộ hoạt động', 'hh', t.src('cj')], ['Chuyến/hộ', 'trips_per_hh', t.src('m5')], ['Giá trị giỏ', 'aov', t.accent]];
  return { xAxis: ax(t, { type: 'category', data: p.map(x => 'K' + x.p4), splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', min: 40 }), tooltip: { trigger: 'axis' },
    series: ser.map(([n, k, c]) => ({ name: n, type: 'line', smooth: true, symbol: 'none', data: idx(k), lineStyle: { width: k === 'sales' ? 3 : 2, color: c }, itemStyle: { color: c } })) };
});
reg('cTraj', t => {
  const order = ['Tăng chi (>+20%)', 'Ổn định (±20%)', 'Giảm chi (<−20%)', 'Rời bỏ (≥8 tuần không mua)'];
  const d = order.map(k => D2.traj.find(x => x.traj === k));
  const col = [t.src('cj'), t.line, t.src('batf'), t.src('carbo')];
  return { xAxis: ax(t, { type: 'category', data: order.map(s => s.split(' (')[0]), splitLine: { show: false } }),
    yAxis: [ax(t, { type: 'value', name: 'Số hộ' }), ax(t, { type: 'value', name: 'Chênh USD', splitLine: { show: false }, axisLabel: { color: t.muted, formatter: v => num(v / 1000) + 'k' } })],
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    series: [{ name: 'Số hộ', type: 'bar', barWidth: '46%', data: d.map((x, i) => ({ value: x.households, itemStyle: { color: col[i], borderRadius: [4, 4, 0, 0] } })) },
      { name: 'Chênh doanh thu nửa sau − nửa đầu', type: 'line', yAxisIndex: 1, data: d.map(x => x.delta), itemStyle: { color: t.ink }, lineStyle: { color: t.ink }, symbolSize: 8, tooltip: { valueFormatter: v => num(v) + ' USD' } }] };
});
reg('cRfm', t => {
  const d = D2.rfm.slice().sort((a, b) => b.rev_share - a.rev_share);
  return { xAxis: ax(t, { type: 'category', data: d.map(x => x.segment), splitLine: { show: false }, axisLabel: { color: t.muted, interval: 0, rotate: 24, fontSize: 10 } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    grid: { left: 12, right: 24, top: 40, bottom: 10, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => { const r = d[p[0].dataIndex]; return `<b>${r.segment}</b><br>${num(r.households)} hộ (${pct(r.hh_share, 1)})<br>Doanh thu: ${pct(r.rev_share, 1)}<br>Chi TB/hộ: ${num(r.avg_m)} USD<br>Recency trung vị: ${num(r.recency)} ngày`; } },
    series: [{ name: '% số hộ', type: 'bar', data: d.map(x => x.hh_share), itemStyle: { color: t.src('cj2'), borderRadius: [4, 4, 0, 0] } },
      { name: '% doanh thu', type: 'bar', data: d.map(x => x.rev_share), itemStyle: { color: t.src('cj'), borderRadius: [4, 4, 0, 0] } }] };
});
reg('cLerner', t => {
  const d = D2.lerner, lab = c => c.charAt(0) + c.slice(1).toLowerCase();
  return { xAxis: ax(t, { type: 'category', data: d.map(x => lab(x.category)), splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', max: 1, axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => pct(v, 1) },
    series: [{ name: 'Biên tối ưu ngụ ý 1/|e|', type: 'bar', barWidth: '42%', data: d.map(x => x.implied_margin), itemStyle: { color: t.src('batf'), borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'insideTop', color: '#fff', fontSize: 11, formatter: p => pct(p.value) } },
      { name: 'Biên hòa vốn khi giảm 20%', type: 'scatter', symbol: 'rect', symbolSize: [46, 4], data: d.map(x => x.breakeven_margin_20pct_cut), itemStyle: { color: t.ink } }] };
});
reg('cPch', t => ({
  xAxis: ax(t, { type: 'category', data: D2.pch.map(x => x.bin), splitLine: { show: false }, axisLabel: { color: t.muted, fontSize: 10, rotate: 30 } }),
  yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => num(v / 1000) + 'k' } }),
  tooltip: { trigger: 'axis', valueFormatter: v => num(v) + ' lần đổi giá' },
  series: [{ type: 'bar', data: D2.pch.map(x => ({ value: x.n, itemStyle: { color: x.bin.startsWith('−') || x.bin.startsWith('≤') ? t.src('carbo') : t.src('m5'), borderRadius: [3, 3, 0, 0] } })) }] }));
reg('cDyn', t => {
  const d = D2.dyn, lab = c => c.charAt(0) + c.slice(1).toLowerCase(), ex = v => Math.exp(v) - 1;
  return { xAxis: ax(t, { type: 'category', data: d.map(x => lab(x.category)), splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => pct(v, 1) },
    series: [['Tuần sau khuyến mãi (trễ 1)', 'promo_l1', t.src('m5')], ['Trễ 2 tuần', 'promo_l2', t.src('cj2')], ['Toàn bộ đối thủ khuyến mãi', 'rival_promo', t.src('carbo')]].map(([n, k, c]) => ({
      name: n, type: 'bar', data: d.map(x => ex(x[k])), itemStyle: { color: c, borderRadius: 3 } })) };
});
let simM = 0.3, simC = 0.1;
reg('cSim', t => {
  const d = D2.sim.filter(x => Math.abs(x.margin - simM) < 1e-6 && Math.abs(x.cut - simC) < 1e-6);
  const lab = c => c.charAt(0) + c.slice(1).toLowerCase();
  return { xAxis: ax(t, { type: 'category', data: d.map(x => lab(x.category)), splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => { const r = d[p[0].dataIndex]; return `<b>${lab(r.category)}</b><br>Lượng bán ×${num(r.units_mult, 2)} (chỉ giá)<br>Lợi nhuận, chỉ giảm giá: ${pct(r.profit_change_price_only, 1)}<br>Lợi nhuận, có trưng bày: ${pct(r.profit_change_with_display, 1)}`; } },
    series: [{ name: 'Chỉ giảm giá', type: 'bar', data: d.map(x => x.profit_change_price_only), itemStyle: { color: t.src('batf2'), borderRadius: 3 }, label: { show: true, position: 'top', color: t.ink, fontSize: 10, formatter: p => pct(p.value) } },
      { name: 'Giảm giá + trưng bày', type: 'bar', data: d.map(x => x.profit_change_with_display), itemStyle: { color: t.src('batf'), borderRadius: 3 }, label: { show: true, position: 'top', color: t.ink, fontSize: 10, formatter: p => pct(p.value) } }],
    markLine: undefined };
});
function rerender(id) { const el = document.getElementById(id); const c = echarts.getInstanceByDom(el); const t = T(); c.setOption(Object.assign(base(t), defs[id](t)), true); }
document.querySelectorAll('[data-m]').forEach(b => b.addEventListener('click', () => { document.querySelectorAll('[data-m]').forEach(x => x.setAttribute('aria-pressed', x === b)); simM = +b.dataset.m; window.echarts && rerender('cSim'); }));
document.querySelectorAll('[data-c]').forEach(b => b.addEventListener('click', () => { document.querySelectorAll('[data-c]').forEach(x => x.setAttribute('aria-pressed', x === b)); simC = +b.dataset.c; window.echarts && rerender('cSim'); }));
let swKey = 'pasta sauce';
reg('cSwitch', t => {
  const s = D2.switch[swKey], b = s.brands, data = [];
  s.matrix.forEach((row, i) => row.forEach((v, j) => data.push([j, i, v])));
  return { grid: { left: 12, right: 24, top: 10, bottom: 56, containLabel: true },
    xAxis: ax(t, { type: 'category', data: b, splitLine: { show: false }, name: 'Lần mua sau', nameLocation: 'middle', nameGap: 28, axisLabel: { color: t.muted, fontSize: 10, interval: 0 } }),
    yAxis: ax(t, { type: 'category', data: b, splitLine: { show: false }, inverse: true, axisLabel: { color: t.muted, fontSize: 10 } }),
    visualMap: { min: 0, max: 0.7, show: false, inRange: { color: [t.surface, t.src('carbo2'), t.src('carbo')] } },
    tooltip: { formatter: p => `${b[p.data[1]]} → ${b[p.data[0]]}: ${pct(p.data[2], 1)}` },
    series: [{ type: 'heatmap', data, label: { show: true, color: t.ink, fontSize: 10, formatter: p => pct(p.data[2]) }, itemStyle: { borderColor: t.surface, borderWidth: 2 } }] };
});
document.querySelectorAll('[data-s]').forEach(b => b.addEventListener('click', () => { document.querySelectorAll('[data-s]').forEach(x => x.setAttribute('aria-pressed', x === b)); swKey = b.dataset.s; window.echarts && rerender('cSwitch'); }));
reg('cRules', t => {
  const d = D2.rules.slice().reverse(), lab = s => s.toLowerCase().replace(/(^|[\s/-])\w/g, m => m.toUpperCase());
  return { grid: { left: 12, right: 50, top: 10, bottom: 24, containLabel: true },
    xAxis: ax(t, { type: 'value' }), yAxis: ax(t, { type: 'category', data: d.map(x => lab(x.a) + ' + ' + lab(x.b)), splitLine: { show: false }, axisLabel: { color: t.ink, fontSize: 10 } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => { const r = d[p[0].dataIndex]; return `<b>${lab(r.a)} + ${lab(r.b)}</b><br>Lift ${num(r.lift, 2)} · ${num(r.n)} giỏ<br>P(B|A) ${pct(r.conf_a_b, 1)} · P(A|B) ${pct(r.conf_b_a, 1)}`; } },
    series: [{ type: 'bar', barWidth: '62%', data: d.map(x => x.lift), itemStyle: { color: t.src('cj'), borderRadius: [0, 4, 4, 0] }, label: { show: true, position: 'right', color: t.ink, fontSize: 10, formatter: p => num(p.value, 1) } }] };
});
reg('cFc', t => {
  const d = D2.fc.slice().sort((a, b) => b.wrmsse_item - a.wrmsse_item);
  return { grid: { left: 12, right: 60, top: 36, bottom: 24, containLabel: true },
    xAxis: ax(t, { type: 'value' }), yAxis: ax(t, { type: 'category', data: d.map(x => x.model), splitLine: { show: false }, axisLabel: { color: t.ink } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => { const r = d[p[0].dataIndex]; return `<b>${r.model}</b><br>WRMSSE ${num(r.wrmsse_item, 3)}<br>WAPE ${pct(r.wape, 1)}<br>Lệch tổng ${pct(r.bias, 1)}`; } },
    series: [{ name: 'WRMSSE', type: 'bar', barWidth: '55%', data: d.map((x, i) => ({ value: x.wrmsse_item, itemStyle: { color: i === d.length - 1 ? t.src('m5') : t.line, borderRadius: [0, 4, 4, 0] } })),
      label: { show: true, position: 'right', color: t.ink, fontSize: 11, formatter: p => num(p.value, 3) } }] };
});
reg('cFcLine', t => {
  const f = D2.fcTotal, keys = ['Naive mùa vụ 7 ngày', 'TB theo thứ, 8 tuần', 'GBM toàn cục (Poisson)'], cols = [t.src('batf'), t.src('lgsr'), t.src('m5')];
  return { xAxis: ax(t, { type: 'category', data: f.dates.map(s => s.slice(8) + '/' + s.slice(5, 7)), splitLine: { show: false }, axisLabel: { color: t.muted, fontSize: 10, hideOverlap: true } }),
    yAxis: ax(t, { type: 'value', scale: true, axisLabel: { color: t.muted, formatter: v => num(v / 1000) + 'k' } }),
    tooltip: { trigger: 'axis', valueFormatter: v => num(v) },
    series: [{ name: 'Thực tế', type: 'line', data: f.actual, symbol: 'circle', symbolSize: 5, lineStyle: { width: 3, color: t.ink }, itemStyle: { color: t.ink } },
      ...keys.map((k, i) => ({ name: k, type: 'line', data: f[k], symbol: 'none', lineStyle: { width: 2, color: cols[i], type: i < 2 ? 'dashed' : 'solid' }, itemStyle: { color: cols[i] } }))] };
});
// Chế độ chụp màn hình cho tài liệu: ?shot=<id chương>&theme=light
(() => { const u = new URLSearchParams(location.search); const th = u.get('theme'); if (th) document.documentElement.setAttribute('data-theme', th);
  const s = u.get('shot'); if (!s) return; document.body.classList.add('shot-mode');
  if (s !== 'hero') { document.querySelector('header.hero').hidden = true; document.querySelectorAll('section.ch').forEach(x => x.hidden = x.id !== s); }
  else document.querySelectorAll('main, footer.foot').forEach(x => x.hidden = true); })();
""".replace("__D2__", json.dumps(data2, ensure_ascii=False, separators=(",", ":")))

    # chèn vào trang
    html = html.replace('<section class="ch" id="gia">', sec_customers + '\n<section class="ch" id="gia">', 1)
    html = html.replace('<section class="ch" id="tong-hop">', sec_forecast + '\n<section class="ch" id="tong-hop">', 1)
    # thêm khối vào cuối các chương hiện có (trước </div></section> của chương)
    def append_to(h, sid, block):
        i = h.index(f'<section class="ch" id="{sid}">')
        j = h.index("</div></section>", i)
        return h[:j] + block + h[j:]
    html = append_to(html, "gia", add_price)
    html = append_to(html, "khuyen-mai", add_promo)
    html = append_to(html, "thu-nhap", add_switch)
    html = append_to(html, "hanh-vi", add_rules)
    i = html.index('<section class="ch" id="tong-hop">')
    j = html.index('</div>\n</div></section>', i)
    html = html[:j] + synth_extra + html[j:]
    html = html.replace('<a href="#tap-trung">Tập trung</a>', '<a href="#tap-trung">Tập trung</a><a href="#khach-hang">Khách hàng</a>')
    html = html.replace('<a href="#tong-hop">Tổng hợp</a>', '<a href="#du-bao">Dự báo</a><a href="#tong-hop">Tổng hợp</a>')
    html = html.replace("@media (max-width: 860px)", css_extra + "\n@media (max-width: 860px)", 1)
    html = html.replace("function boot() {", js_extra + "\nfunction boot() {", 1)
    # đánh số lại chương theo thứ tự xuất hiện
    k = [0]

    def renum(m):
        k[0] += 1
        return f'<div class="eyebrow">Chương {k[0]} · '
    html = re.sub(r'<div class="eyebrow">Chương(?: \d+)? · ', renum, html)
    return html
