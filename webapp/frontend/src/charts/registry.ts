// @ts-nocheck
/* Cấu hình biểu đồ ECharts, chuyển nguyên từ trang phân tích tĩnh đã kiểm (research/multisource/build_html.py, html_extra.py).
   Mỗi biểu đồ là một hàm thuần: (bộ màu theo theme, dữ liệu) → option. Dữ liệu D/D2 lấy từ API /api/charts. */

let D: any = {};
let D2: any = {};
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const pct = (v, d = 0) => (v * 100).toFixed(d).replace('.', ',') + '%';
const num = (v, d = 0) => v.toLocaleString('vi-VN', { maximumFractionDigits: d, minimumFractionDigits: d });
const T = () => ({ ink: css('--ink'), muted: css('--muted'), line: css('--line'), surface: css('--surface'), accent: css('--accent'),
  src: k => css('--' + k), body: css('--body') });
function base(t) {
  return { textStyle: { fontFamily: t.body, color: t.ink }, animationDuration: 700,
    grid: { left: 12, right: 24, top: 36, bottom: 28, containLabel: true },
    tooltip: { backgroundColor: t.surface, borderColor: t.line, textStyle: { color: t.ink, fontFamily: t.body, fontSize: 12 }, confine: true },
    legend: { textStyle: { color: t.muted, fontSize: 11 }, top: 0, type: 'scroll', icon: 'circle', itemWidth: 9, itemHeight: 9 } };
}
const ax = (t, o = {}) => Object.assign({ axisLine: { lineStyle: { color: t.line } }, axisTick: { show: false },
  axisLabel: { color: t.muted, fontSize: 11 }, splitLine: { lineStyle: { color: t.line, type: [3, 4] } }, nameTextStyle: { color: t.muted, fontSize: 11 } }, o);
const defs = {};
function reg(id, fn) { defs[id] = fn; }

reg('cTimeline', t => {
  const rows = D.timeline;
  return { grid: { left: 12, right: 24, top: 10, bottom: 24, containLabel: true },
    xAxis: ax(t, { type: 'time', min: '2006-01-01', max: '2018-03-01' }), yAxis: ax(t, { type: 'category', data: rows.map(r => r.name), inverse: true, splitLine: { show: false } }),
    tooltip: { formatter: p => `<b>${p.name}</b><br>${rows[p.dataIndex].start} → ${rows[p.dataIndex].end}` },
    series: [{ type: 'custom', renderItem: (params, api) => {
      const s = api.coord([api.value(0), api.value(2)]), e = api.coord([api.value(1), api.value(2)]), h = api.size([0, 1])[1] * 0.5;
      return { type: 'rect', shape: { x: s[0], y: s[1] - h / 2, width: Math.max(e[0] - s[0], 3), height: h, r: 5 }, style: { fill: t.src(rows[params.dataIndex].src) } };
    }, encode: { x: [0, 1], y: 2 }, data: rows.map((r, i) => ({ name: r.name, value: [r.start, r.end, i] })) }] };
});

reg('cDemand', t => {
  const cls = ['Đều (smooth)', 'Thất thường (erratic)', 'Gián đoạn (intermittent)', 'Cục (lumpy)'];
  const cats = ['FOODS', 'HOUSEHOLD', 'HOBBIES'];
  const col = [t.src('cj'), t.src('batf'), t.src('m5'), t.src('carbo')];
  const tot = c => D.demand.filter(d => d.cat === c).reduce((a, b) => a + b.series, 0);
  return { legend: { top: 0 }, grid: { left: 12, right: 24, top: 40, bottom: 24, containLabel: true },
    xAxis: ax(t, { type: 'value', max: 1, axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    yAxis: ax(t, { type: 'category', data: ['Thực phẩm', 'Gia dụng', 'Sở thích'], splitLine: { show: false } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => pct(v, 1) },
    series: cls.map((k, i) => ({ name: k, type: 'bar', stack: 's', barWidth: '55%', itemStyle: { color: col[i] },
      data: cats.map(c => { const r = D.demand.find(d => d.cat === c && d.cls === k); return r ? r.series / tot(c) : 0; }) })) };
});

reg('cLorenz', t => ({
  xAxis: ax(t, { type: 'value', min: 0, max: 1, name: '% khách / mặt hàng', nameLocation: 'middle', nameGap: 26, axisLabel: { color: t.muted, formatter: v => pct(v) } }),
  yAxis: ax(t, { type: 'value', min: 0, max: 1, axisLabel: { color: t.muted, formatter: v => pct(v) } }),
  grid: { left: 12, right: 24, top: 44, bottom: 36, containLabel: true },
  tooltip: { trigger: 'axis', valueFormatter: v => pct(v, 1), axisPointer: { type: 'line' } },
  series: [{ name: 'Phân bổ đều', type: 'line', data: [[0, 0], [1, 1]], symbol: 'none', lineStyle: { color: t.muted, type: 'dotted', width: 1 }, tooltip: { show: false } },
    ...D.lorenz.map(l => ({ name: l.name, type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2.4, color: t.src(l.src) }, itemStyle: { color: t.src(l.src) },
      data: [[0, 0], ...l.p.curve.map(c => [c.pop, c.share])],
      markPoint: l.src === 'cj' ? { symbol: 'circle', symbolSize: 9, data: [{ coord: [0.2, l.p.top20], value: pct(l.p.top20) }], label: { position: 'left', color: t.ink, fontSize: 11, formatter: p => 'top 20%: ' + p.value } } : undefined }))] }));

reg('cElastic', t => {
  const rows = D.elasticity.slice().reverse();
  return { grid: { left: 12, right: 50, top: 28, bottom: 30, containLabel: true },
    xAxis: ax(t, { type: 'value', min: -3.5, max: 0.2, interval: 0.5, axisLabel: { color: t.muted, formatter: v => num(v, 1) } }),
    yAxis: ax(t, { type: 'category', data: rows.map(r => r.name), splitLine: { show: false }, axisLabel: { color: t.ink, fontSize: 11 } }),
    tooltip: { formatter: p => { const r = rows[p.dataIndex]; return `<b>${r.name}</b><br>Co giãn: ${num(r.v, 2)}<br>KTC 95%: ${num(r.lo, 2)} → ${num(r.hi, 2)}`; } },
    series: [{ type: 'custom', renderItem: (params, api) => {
        const r = rows[params.dataIndex]; const a = api.coord([r.lo, params.dataIndex]), b = api.coord([r.hi, params.dataIndex]), m = api.coord([r.v, params.dataIndex]);
        const c = t.src(r.src);
        return { type: 'group', children: [
          { type: 'line', shape: { x1: a[0], y1: a[1], x2: Math.max(b[0], a[0] + 2), y2: b[1] }, style: { stroke: c, lineWidth: 3, lineCap: 'round' } },
          { type: 'circle', shape: { cx: m[0], cy: m[1], r: 6 }, style: { fill: c, stroke: t.surface, lineWidth: 2 } },
          { type: 'text', style: { x: Math.max(b[0], m[0]) + 10, y: m[1], text: num(r.v, 2), fill: t.ink, fontSize: 11, verticalAlign: 'middle', fontFamily: t.body } }] };
      }, data: rows.map((r, i) => [r.v, i]),
      markLine: { silent: true, symbol: 'none', lineStyle: { color: t.muted, type: 'dashed' }, label: { color: t.muted, fontSize: 10, formatter: 'co giãn đơn vị' }, data: [{ xAxis: -1 }] } }] };
});

reg('cSeg', t => {
  const cats = [...new Set(D.seg.map(s => s.category))];
  const segs = ['VALUE', 'MAINSTREAM', 'UPSCALE'], cols = [t.src('batf'), t.src('cj'), t.src('lgsr')];
  return { xAxis: ax(t, { type: 'category', data: cats.map(c => c.charAt(0) + c.slice(1).toLowerCase()), splitLine: { show: false }, axisLabel: { color: t.muted, interval: 0, fontSize: 10 } }),
    yAxis: ax(t, { type: 'value', name: 'Co giãn', axisLabel: { color: t.muted, formatter: v => num(v, 1) } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => num(v, 2) },
    series: segs.map((s, i) => ({ name: s.charAt(0) + s.slice(1).toLowerCase(), type: 'bar', itemStyle: { color: cols[i], borderRadius: [0, 0, 4, 4] },
      data: cats.map(c => { const r = D.seg.find(x => x.category === c && x.segment === s); return r ? r.elasticity : null; }) })) };
});

reg('cPromo', t => {
  const rows = D.promo.slice().reverse();
  return { grid: { left: 12, right: 50, top: 10, bottom: 30, containLabel: true },
    xAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    yAxis: ax(t, { type: 'category', data: rows.map(r => r.name), splitLine: { show: false }, axisLabel: { color: t.ink, fontSize: 10.5 } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => pct(v, 1) },
    series: [{ type: 'bar', barWidth: '62%', data: rows.map(r => ({ value: r.v, itemStyle: { color: t.src(r.src), borderRadius: r.v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4] } })),
      label: { show: true, position: 'right', color: t.ink, fontSize: 10, formatter: p => pct(p.value) } }] };
});

reg('cDepth', t => ({
  grid: { left: 12, right: 24, top: 64, bottom: 28, containLabel: true },
  xAxis: ax(t, { type: 'category', data: D.depth.map(d => d.bin), splitLine: { show: false } }),
  yAxis: [ax(t, { type: 'value', name: 'Đơn vị/tuần' }), ax(t, { type: 'value', name: '% quan sát', splitLine: { show: false }, axisLabel: { color: t.muted, formatter: v => pct(v) } })],
  tooltip: { trigger: 'axis' },
  series: [{ name: 'Đơn vị bán / SKU-cửa hàng-tuần', type: 'bar', data: D.depth.map(d => +d.units_per_row.toFixed(1)), itemStyle: { color: t.src('batf'), borderRadius: [4, 4, 0, 0] }, barWidth: '48%' },
    { name: '% số quan sát', type: 'line', yAxisIndex: 1, data: D.depth.map(d => d.rows / D.depth.reduce((a, b) => a + b.rows, 0)), itemStyle: { color: t.ink }, lineStyle: { color: t.ink }, tooltip: { valueFormatter: v => pct(v, 1) } }] }));

reg('cCampaign', t => {
  const types = ['TypeA', 'TypeB', 'TypeC'], cols = [t.src('cj'), t.src('batf'), t.src('m5')];
  return { xAxis: ax(t, { type: 'value', name: 'Chênh chi tiêu trước chiến dịch', nameLocation: 'middle', nameGap: 26, axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    yAxis: ax(t, { type: 'value', name: 'DiD', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    grid: { left: 12, right: 24, top: 44, bottom: 36, containLabel: true },
    tooltip: { formatter: p => `Chiến dịch ${p.data[2]} (${p.seriesName})<br>Chênh trước: ${pct(p.data[0])}<br>DiD: ${pct(p.data[1], 1)}` },
    series: types.map((k, i) => ({ name: k, type: 'scatter', symbolSize: 12, itemStyle: { color: cols[i], opacity: 0.85 },
      data: D.campaign_did.filter(d => d.type === k).map(d => [d.level_gap, d.did_pp, d.campaign]),
      markLine: i === 0 ? { silent: true, symbol: 'none', lineStyle: { color: t.muted }, label: { show: false }, data: [{ yAxis: 0 }] } : undefined })) };
});

reg('cSnap', t => {
  const st = ['CA', 'TX', 'WI'], cats = ['FOODS', 'HOUSEHOLD', 'HOBBIES'], lab = ['Thực phẩm', 'Gia dụng', 'Sở thích'], cols = [t.src('cj'), t.src('m5'), t.src('batf')];
  return { xAxis: ax(t, { type: 'category', data: st, splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => pct(v, 1) },
    series: cats.map((c, i) => ({ name: lab[i], type: 'bar', itemStyle: { color: cols[i], borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top', color: t.ink, fontSize: 10, formatter: p => pct(p.value, 1) },
      data: st.map(s => D.snap.find(x => x.state === s && x.cat === c).lift) })) };
});

reg('cDom', t => {
  const cols = [t.src('cj'), t.src('batf'), t.src('m5')];
  return { xAxis: ax(t, { type: 'category', data: D.dom.map(d => d.dom), name: 'Ngày', splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', min: 0.85, axisLabel: { color: t.muted, formatter: v => num(v, 2) } }),
    tooltip: { trigger: 'axis', valueFormatter: v => num(v, 3) },
    series: ['CA', 'TX', 'WI'].map((s, i) => ({ name: s, type: 'line', symbol: 'none', smooth: 0.2, lineStyle: { width: 2, color: cols[i] }, itemStyle: { color: cols[i] },
      data: D.dom.map(d => d[s + '_idx']),
      markLine: i === 0 ? { silent: true, symbol: 'none', lineStyle: { color: t.muted, type: 'dashed' }, label: { show: false }, data: [{ yAxis: 1 }] } : undefined })) };
});

reg('cEvents', t => {
  const rows = D.events.slice();
  const col = { National: t.src('cj'), Religious: t.src('lgsr'), Cultural: t.src('batf'), Sporting: t.src('m5') };
  return { grid: { left: 12, right: 50, top: 10, bottom: 30, containLabel: true },
    xAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    yAxis: ax(t, { type: 'category', data: rows.map(r => r.event), splitLine: { show: false }, axisLabel: { color: t.ink, fontSize: 10.5 } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => `<b>${rows[p[0].dataIndex].event}</b> (${rows[p[0].dataIndex].type})<br>${pct(p[0].value, 1)} · ${rows[p[0].dataIndex].n} năm` },
    series: [{ type: 'bar', barWidth: '64%', data: rows.map(r => ({ value: r.lift, itemStyle: { color: col[r.type], borderRadius: r.lift >= 0 ? [0, 3, 3, 0] : [3, 0, 0, 3] } })),
      label: { show: true, position: 'right', color: t.muted, fontSize: 9.5, formatter: p => pct(p.value) } }] };
});

reg('cIncome', t => {
  const d = D.income.filter(x => x.level.startsWith('Level'));
  return { xAxis: ax(t, { type: 'category', data: d.map(x => x.level.replace('Level', 'L')), splitLine: { show: false } }),
    yAxis: [ax(t, { type: 'value', name: 'USD/tuần' }), ax(t, { type: 'value', name: 'Nhãn riêng', min: 0.1, max: 0.35, splitLine: { show: false }, axisLabel: { color: t.muted, formatter: v => pct(v) } })],
    tooltip: { trigger: 'axis', formatter: p => { const r = d[p[0].dataIndex]; return `<b>${r.level}</b> · ${r.households} hộ<br>Chi tiêu/tuần: ${num(r.weekly_spend, 1)} USD<br>Giá trị giỏ: ${num(r.basket_value, 1)} USD<br>Nhãn riêng: ${pct(r.pl_share, 1)}<br>Tỷ lệ giảm giá: ${pct(r.disc_rate, 1)}`; } },
    series: [{ name: 'Chi tiêu/tuần (trung vị)', type: 'bar', data: d.map(x => x.weekly_spend), itemStyle: { color: t.src('cj'), borderRadius: [4, 4, 0, 0] }, barWidth: '56%' },
      { name: 'Tỷ trọng nhãn riêng', type: 'line', yAxisIndex: 1, data: d.map(x => x.pl_share), itemStyle: { color: t.accent }, lineStyle: { width: 2.4, color: t.accent }, symbolSize: 7 }] };
});

reg('cPL', t => {
  const cats = [...new Set(D.pl.map(x => x.CATEGORY))];
  const g = (c, b) => D.pl.find(x => x.CATEGORY === c && x.is_pl === b);
  return { xAxis: ax(t, { type: 'category', data: cats.map(c => c.charAt(0) + c.slice(1).toLowerCase()), splitLine: { show: false }, axisLabel: { color: t.muted, interval: 0, fontSize: 10 } }),
    yAxis: ax(t, { type: 'value', name: 'USD/đơn vị' }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => num(v, 2) + ' USD' },
    series: [{ name: 'Thương hiệu quốc gia', type: 'bar', data: cats.map(c => g(c, false).avg_price), itemStyle: { color: t.src('m5'), borderRadius: [4, 4, 0, 0] } },
      { name: 'Nhãn riêng', type: 'bar', data: cats.map(c => g(c, true).avg_price), itemStyle: { color: t.src('batf'), borderRadius: [4, 4, 0, 0] },
        label: { show: true, position: 'top', color: t.ink, fontSize: 10, formatter: p => '−' + pct(1 - p.value / g(cats[p.dataIndex], false).avg_price) } }] };
});

reg('cLoyal', t => {
  const d = D.loyalty, lab = { 'pancake mixes': 'Bột bánh', 'pasta': 'Mì Ý', 'pasta sauce': 'Sốt mì', 'syrups': 'Siro' };
  return { xAxis: ax(t, { type: 'category', data: d.map(x => lab[x.commodity]), splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', max: 1, axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => pct(v, 1) },
    series: [{ name: 'Trung thành (≥80%)', type: 'bar', stack: 's', data: d.map(x => x.share_loyal_80), itemStyle: { color: t.src('cj') } },
      { name: 'Ở giữa', type: 'bar', stack: 's', data: d.map(x => 1 - x.share_loyal_80 - x.share_switcher_50), itemStyle: { color: t.line } },
      { name: 'Hay đổi (<50%)', type: 'bar', stack: 's', data: d.map(x => x.share_switcher_50), itemStyle: { color: t.src('carbo') } }] };
});

let basketKey = 'basket_type';
reg('cBasket', t => {
  const d = D[basketKey].filter(x => x.level !== 'XX' && x.level !== '(trống)');
  const tb = d.reduce((a, b) => a + b.baskets, 0), ts = d.reduce((a, b) => a + b.spend, 0);
  return { xAxis: ax(t, { type: 'category', data: d.map(x => x.level), splitLine: { show: false } }),
    yAxis: [ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }), ax(t, { type: 'value', name: 'Giá trị giỏ', splitLine: { show: false } })],
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    series: [{ name: '% số giỏ', type: 'bar', data: d.map(x => x.baskets / tb), itemStyle: { color: t.src('lgsr'), borderRadius: [4, 4, 0, 0] }, tooltip: { valueFormatter: v => pct(v, 1) } },
      { name: '% doanh thu', type: 'bar', data: d.map(x => x.spend / ts), itemStyle: { color: t.accent, borderRadius: [4, 4, 0, 0] }, tooltip: { valueFormatter: v => pct(v, 1) } },
      { name: 'Giá trị giỏ TB', type: 'line', yAxisIndex: 1, data: d.map(x => x.aov), itemStyle: { color: t.ink }, lineStyle: { color: t.ink }, tooltip: { valueFormatter: v => num(v, 2) } }] };
});

reg('cHeat', t => {
  const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
  const hrs = [...new Set(D.heat.map(h => h.hr))].sort((a, b) => a - b);
  const max = Math.max(...D.heat.map(h => h.baskets));
  return { grid: { left: 12, right: 24, top: 10, bottom: 56, containLabel: true },
    xAxis: ax(t, { type: 'category', data: hrs, splitLine: { show: false }, name: 'Giờ', nameLocation: 'middle', nameGap: 24 }),
    yAxis: ax(t, { type: 'category', data: days, splitLine: { show: false }, inverse: true }),
    visualMap: { min: 0, max, calculable: false, orient: 'horizontal', left: 'center', bottom: 0, itemHeight: 140, itemWidth: 10, textStyle: { color: t.muted, fontSize: 10 },
      inRange: { color: [t.surface, t.src('cj2'), t.src('cj')] } },
    tooltip: { formatter: p => `${days[p.data[1]]} ${hrs[p.data[0]]}h: ${num(p.data[2])} giỏ` },
    series: [{ type: 'heatmap', data: D.heat.map(h => [hrs.indexOf(h.hr), h.wd - 1, h.baskets]), itemStyle: { borderColor: t.surface, borderWidth: 1 } }] };
});

reg('cHours', t => {
  const norm = arr => { const s = arr.reduce((a, b) => a + b.baskets, 0); return arr.map(x => [x.hr_ ?? x.hr, x.baskets / s]); };
  const lg = {}; D.heat.forEach(h => lg[h.hr] = (lg[h.hr] || 0) + h.baskets);
  const lgArr = Object.entries(lg).map(([h, b]) => ({ hr: +h, baskets: b }));
  return { xAxis: ax(t, { type: 'value', min: 0, max: 23, interval: 3, name: 'Giờ', nameLocation: 'middle', nameGap: 24 }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    grid: { left: 12, right: 24, top: 40, bottom: 36, containLabel: true },
    tooltip: { trigger: 'axis', valueFormatter: v => pct(v, 1) },
    series: [['Complete Journey', norm(D.hours.cj), 'cj'], ['Carbo-Loading', norm(D.hours.carbo), 'carbo'], ['LGSR (mô phỏng)', norm(lgArr), 'lgsr']].map(([n, d, k]) => ({
      name: n, type: 'line', smooth: true, symbol: 'none', data: d.sort((a, b) => a[0] - b[0]), lineStyle: { width: 2.2, color: t.src(k), type: k === 'lgsr' ? 'dashed' : 'solid' }, itemStyle: { color: t.src(k) } })) };
});

reg('cComp', t => {
  const lab = { 'pancake mixes': 'Bột bánh', 'pasta': 'Mì Ý', 'pasta sauce': 'Sốt', 'syrups': 'Siro' };
  const d = D.complement.slice().sort((a, b) => a.lift - b.lift);
  return { grid: { left: 12, right: 40, top: 36, bottom: 24, containLabel: true },
    xAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => num(v, 1) } }),
    yAxis: ax(t, { type: 'category', data: d.map(x => lab[x.a] + ' + ' + lab[x.b]), splitLine: { show: false }, axisLabel: { color: t.ink } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => { const r = d[p[0].dataIndex]; return `<b>${lab[r.a]} + ${lab[r.b]}</b><br>Lift: ${num(r.lift, 2)}<br>Support: ${pct(r.support, 1)}<br>P(${lab[r.b]}|${lab[r.a]}): ${pct(r.conf_a_b, 1)}<br>P(${lab[r.a]}|${lab[r.b]}): ${pct(r.conf_b_a, 1)}`; } },
    series: [{ name: 'Lift', type: 'bar', barWidth: '55%', data: d.map(x => ({ value: x.lift, itemStyle: { color: x.lift > 1 ? t.src('carbo') : t.src('carbo2'), borderRadius: [0, 4, 4, 0] } })),
      label: { show: true, position: 'right', color: t.ink, fontSize: 10, formatter: p => num(p.value, 2) },
      markLine: { silent: true, symbol: 'none', lineStyle: { color: t.muted, type: 'dashed' }, label: { color: t.muted, formatter: 'độc lập = 1' }, data: [{ xAxis: 1 }] } }] };
});


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
  return { xAxis: ax(t, { type: 'category', data: d.map(x => lab(x.category)), splitLine: { show: false }, axisLabel: { color: t.muted, interval: 0, fontSize: 10 } }),
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
  return { xAxis: ax(t, { type: 'category', data: d.map(x => lab(x.category)), splitLine: { show: false }, axisLabel: { color: t.muted, interval: 0, fontSize: 10 } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => pct(v, 1) },
    series: [['Tuần sau khuyến mãi (trễ 1)', 'promo_l1', t.src('m5')], ['Trễ 2 tuần', 'promo_l2', t.src('cj2')], ['Toàn bộ đối thủ khuyến mãi', 'rival_promo', t.src('carbo')]].map(([n, k, c]) => ({
      name: n, type: 'bar', data: d.map(x => ex(x[k])), itemStyle: { color: c, borderRadius: 3 } })) };
});
let simM = 0.3, simC = 0.1;
reg('cSim', t => {
  const d = D2.sim.filter(x => Math.abs(x.margin - simM) < 1e-6 && Math.abs(x.cut - simC) < 1e-6);
  const lab = c => c.charAt(0) + c.slice(1).toLowerCase();
  return { xAxis: ax(t, { type: 'category', data: d.map(x => lab(x.category)), splitLine: { show: false }, axisLabel: { color: t.muted, interval: 0, fontSize: 10 } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: v => pct(v) } }),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => { const r = d[p[0].dataIndex]; return `<b>${lab(r.category)}</b><br>Lượng bán ×${num(r.units_mult, 2)} (chỉ giá)<br>Lợi nhuận, chỉ giảm giá: ${pct(r.profit_change_price_only, 1)}<br>Lợi nhuận, có trưng bày: ${pct(r.profit_change_with_display, 1)}`; } },
    series: [{ name: 'Chỉ giảm giá', type: 'bar', data: d.map(x => x.profit_change_price_only), itemStyle: { color: t.src('batf2'), borderRadius: 3 }, label: { show: true, position: 'top', color: t.ink, fontSize: 10, formatter: p => pct(p.value) } },
      { name: 'Giảm giá + trưng bày', type: 'bar', data: d.map(x => x.profit_change_with_display), itemStyle: { color: t.src('batf'), borderRadius: 3 }, label: { show: true, position: 'top', color: t.ink, fontSize: 10, formatter: p => pct(p.value) } }],
    markLine: undefined };
});
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


export type ChartState = { basketKey?: string; swKey?: string; simM?: number; simC?: number };
export function chartOption(id: string, data: { D: any; D2: any }, state: ChartState = {}) {
  D = data.D; D2 = data.D2;
  if (state.basketKey) basketKey = state.basketKey;
  if (state.swKey) swKey = state.swKey;
  if (state.simM) simM = state.simM;
  if (state.simC) simC = state.simC;
  const fn = defs[id];
  if (!fn) return null;
  const t = T();
  return Object.assign(base(t), fn(t));
}
export const chartIds = () => Object.keys(defs);
export { T, base, ax, pct, num };
