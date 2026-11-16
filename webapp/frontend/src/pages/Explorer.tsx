import { useMemo, useState } from 'react';
import { fmtNum, fmtPct, signed, useApi } from '../api';
import { ErrorBox, Eyebrow, Kpi, Panel, RawChart, Segmented, Skeleton } from '../components/ui';
import { ax, base, T } from '../charts/registry';

type M5Opt = { states: string[]; stores: string[]; cats: string[]; depts: string[]; min_date: string; max_date: string };
type M5Out = { series: { period: string; units: number; revenue: number }[]; summary: { units: number; revenue: number; zero_share: number; stores: number; depts: number };
  by_dept: { dept: string; revenue: number; units: number }[]; weekday: { wd: number; units: number }[]; snap: { state: string; raw_lift: number } | null };
type CJOut = { series: { week: number; sales: number; baskets: number; disc_rate: number; private_share: number }[];
  mix: { department: string; sales: number; private_share: number; disc_rate: number }[]; summary: { sales: number; disc_rate: number; private_share: number; growth_first_last_24w: number | null } };

function Select({ id, label, value, options, onChange, all = 'Tất cả' }: { id: string; label: string; value: string; options: string[]; onChange: (v: string) => void; all?: string }) {
  return (
    <label htmlFor={id} className="grid gap-1 text-[0.8rem]"><span className="text-muted">{label}</span>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)} className="rounded-lg border border-line bg-surface px-3 py-2 text-[0.88rem]">
        <option value="">{all}</option>{options.map((o) => <option key={o} value={o}>{o}</option>)}</select></label>
  );
}

function M5() {
  const { data: opt } = useApi<M5Opt>('/api/explorer/m5/options');
  const [f, setF] = useState({ state: '', store: '', cat: '', dept: '', freq: 'week', start: '', end: '' });
  const set = (k: keyof typeof f) => (v: string) => setF((s) => ({ ...s, [k]: v, ...(k === 'state' ? { store: '' } : {}), ...(k === 'cat' ? { dept: '' } : {}) }));
  const qs = new URLSearchParams(Object.entries(f).filter(([, v]) => v)).toString();
  const { data, error, loading } = useApi<M5Out>(`/api/explorer/m5?${qs}`);
  const t = T();
  const stores = (opt?.stores ?? []).filter((s) => !f.state || s.startsWith(f.state));
  const depts = (opt?.depts ?? []).filter((d) => !f.cat || d.startsWith(f.cat));
  const line = useMemo(() => data && {
    ...base(t), grid: { left: 12, right: 24, top: 40, bottom: 56, containLabel: true },
    tooltip: { trigger: 'axis' },
    dataZoom: [{ type: 'inside' }, { type: 'slider', height: 18, bottom: 8, borderColor: t.line, textStyle: { color: t.muted } }],
    xAxis: ax(t, { type: 'time' }),
    yAxis: [ax(t, { type: 'value', name: 'Đơn vị', axisLabel: { color: t.muted, formatter: (v: number) => fmtNum(v / 1000) + 'k' } }),
      ax(t, { type: 'value', name: 'USD', splitLine: { show: false }, axisLabel: { color: t.muted, formatter: (v: number) => fmtNum(v / 1000) + 'k' } })],
    series: [{ name: 'Lượng bán', type: 'line', symbol: 'none', lineStyle: { width: 1.6, color: t.src('m5') }, itemStyle: { color: t.src('m5') }, data: data.series.map((r) => [r.period, r.units]) },
      { name: 'Doanh thu', type: 'line', yAxisIndex: 1, symbol: 'none', lineStyle: { width: 1.4, color: t.accent }, itemStyle: { color: t.accent }, data: data.series.map((r) => [r.period, Math.round(r.revenue)]) }],
  }, [data, t.ink]); // eslint-disable-line
  const days = ['', 'CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
  const bars = data && {
    ...base(t), grid: { left: 12, right: 16, top: 20, bottom: 24, containLabel: true }, tooltip: { trigger: 'axis', valueFormatter: (v: number) => fmtNum(v) },
    xAxis: ax(t, { type: 'category', data: data.weekday.map((w) => days[w.wd + 1] ?? w.wd), splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: (v: number) => fmtNum(v / 1000) + 'k' } }),
    series: [{ type: 'bar', data: data.weekday.map((w) => Math.round(w.units)), itemStyle: { color: t.src('m5'), borderRadius: [4, 4, 0, 0] }, barWidth: '55%' }],
  };
  const dept = data && {
    ...base(t), grid: { left: 12, right: 40, top: 10, bottom: 20, containLabel: true }, tooltip: { trigger: 'axis', valueFormatter: (v: number) => fmtNum(v) + ' USD' },
    xAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: (v: number) => fmtNum(v / 1e6) + ' tr' } }),
    yAxis: ax(t, { type: 'category', inverse: true, data: data.by_dept.map((d) => d.dept), splitLine: { show: false } }),
    series: [{ type: 'bar', data: data.by_dept.map((d) => Math.round(d.revenue)), itemStyle: { color: t.accent, borderRadius: [0, 4, 4, 0] }, barWidth: '55%' }],
  };
  return (
    <div className="grid gap-5">
      <Panel>
        <div className="grid grid-cols-2 gap-3 pb-2 md:grid-cols-4 xl:grid-cols-7">
          <Select id="st" label="Bang" value={f.state} options={opt?.states ?? []} onChange={set('state')} />
          <Select id="sto" label="Cửa hàng" value={f.store} options={stores} onChange={set('store')} />
          <Select id="ca" label="Ngành" value={f.cat} options={opt?.cats ?? []} onChange={set('cat')} />
          <Select id="de" label="Nhóm hàng" value={f.dept} options={depts} onChange={set('dept')} />
          <label htmlFor="fr" className="grid gap-1 text-[0.8rem]"><span className="text-muted">Tần suất</span>
            <select id="fr" value={f.freq} onChange={(e) => set('freq')(e.target.value)} className="rounded-lg border border-line bg-surface px-3 py-2 text-[0.88rem]">
              <option value="day">Ngày</option><option value="week">Tuần</option><option value="month">Tháng</option></select></label>
          <label htmlFor="sd" className="grid gap-1 text-[0.8rem]"><span className="text-muted">Từ ngày</span>
            <input id="sd" type="date" min={opt?.min_date} max={opt?.max_date} value={f.start} onChange={(e) => set('start')(e.target.value)} className="rounded-lg border border-line bg-surface px-3 py-2 text-[0.88rem]" /></label>
          <label htmlFor="ed" className="grid gap-1 text-[0.8rem]"><span className="text-muted">Đến ngày</span>
            <input id="ed" type="date" min={opt?.min_date} max={opt?.max_date} value={f.end} onChange={(e) => set('end')(e.target.value)} className="rounded-lg border border-line bg-surface px-3 py-2 text-[0.88rem]" /></label>
        </div>
      </Panel>
      {error && <ErrorBox msg={error} />}
      {data ? (
        <div className={`grid gap-5 transition-opacity ${loading ? 'opacity-60' : ''}`}>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Kpi label="Lượng bán" value={fmtNum(data.summary.units)} hint={`${data.summary.stores} cửa hàng · ${data.summary.depts} nhóm hàng`} />
            <Kpi label="Doanh thu (lượng × giá tuần)" value={`${fmtNum(data.summary.revenue / 1e6, 1)} tr USD`} />
            <Kpi label="Tỷ lệ SKU-ngày bằng 0" value={fmtPct(data.summary.zero_share)} hint="trung bình trong phạm vi lọc" />
            <Kpi label="Ngày SNAP so với ngày thường" value={data.snap ? signed(data.snap.raw_lift) : '–'} hint={data.snap ? `bang ${data.snap.state}, so sánh thô` : 'chọn 1 bang và tần suất Ngày'} />
          </div>
          <Panel title="Lượng bán và doanh thu" sub="Kéo thanh dưới hoặc cuộn trên biểu đồ để phóng to một giai đoạn">{line && <RawChart option={line} height={360} />}</Panel>
          <div className="grid gap-5 lg:grid-cols-2">
            <Panel title="Lượng bán trung bình theo thứ" sub="Ngày có bán">{bars && <RawChart option={bars} height={280} />}</Panel>
            <Panel title="Doanh thu theo nhóm hàng">{dept && <RawChart option={dept} height={280} />}</Panel>
          </div>
        </div>
      ) : !error && <Skeleton h={480} />}
    </div>
  );
}

function CJ() {
  const { data: opt } = useApi<{ departments: string[] }>('/api/explorer/cj/options');
  const [sel, setSel] = useState<string[]>(['GROCERY', 'PRODUCE', 'MEAT']);
  const qs = sel.map((d) => `department=${encodeURIComponent(d)}`).join('&');
  const { data, error, loading } = useApi<CJOut>(`/api/explorer/cj?${qs}`);
  const t = T();
  const line = data && {
    ...base(t), grid: { left: 12, right: 24, top: 40, bottom: 30, containLabel: true }, tooltip: { trigger: 'axis' },
    xAxis: ax(t, { type: 'category', data: data.series.map((r) => r.week), name: 'Tuần', nameLocation: 'middle', nameGap: 24, splitLine: { show: false } }),
    yAxis: [ax(t, { type: 'value', name: 'USD', axisLabel: { color: t.muted, formatter: (v: number) => fmtNum(v / 1000) + 'k' } }),
      ax(t, { type: 'value', max: 0.5, splitLine: { show: false }, axisLabel: { color: t.muted, formatter: (v: number) => fmtPct(v, 0) } })],
    series: [{ name: 'Doanh thu', type: 'bar', data: data.series.map((r) => Math.round(r.sales)), itemStyle: { color: t.src('cj'), borderRadius: [2, 2, 0, 0] } },
      { name: 'Tỷ lệ giảm giá', type: 'line', yAxisIndex: 1, symbol: 'none', smooth: true, lineStyle: { color: t.accent, width: 2 }, itemStyle: { color: t.accent }, data: data.series.map((r) => r.disc_rate), tooltip: { valueFormatter: (v: number) => fmtPct(v) } },
      { name: 'Tỷ trọng nhãn riêng', type: 'line', yAxisIndex: 1, symbol: 'none', smooth: true, lineStyle: { color: t.src('lgsr'), width: 2 }, itemStyle: { color: t.src('lgsr') }, data: data.series.map((r) => r.private_share), tooltip: { valueFormatter: (v: number) => fmtPct(v) } }],
  };
  const toggle = (d: string) => setSel((s) => (s.includes(d) ? s.filter((x) => x !== d) : [...s, d]));
  return (
    <div className="grid gap-5">
      <Panel title="Chọn ngành hàng" sub="Không chọn = toàn bộ. Complete Journey, 2.500 hộ, 102 tuần.">
        <div className="flex flex-wrap gap-1.5 pb-2">
          {(opt?.departments ?? []).slice(0, 24).map((d) => (
            <button key={d} type="button" aria-pressed={sel.includes(d)} onClick={() => toggle(d)}
              className={`rounded-full border px-3 py-1 text-[0.78rem] transition ${sel.includes(d) ? 'border-cj bg-cj text-white' : 'border-line text-muted hover:text-ink'}`}>{d}</button>))}
          {sel.length > 0 && <button type="button" onClick={() => setSel([])} className="px-2 text-[0.78rem] text-accent hover:underline">Bỏ chọn</button>}
        </div>
      </Panel>
      {error && <ErrorBox msg={error} />}
      {data ? (
        <div className={`grid gap-5 ${loading ? 'opacity-60' : ''}`}>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Kpi label="Doanh thu 102 tuần" value={`${fmtNum(data.summary.sales / 1e6, 2)} tr USD`} />
            <Kpi label="Tăng trưởng (24 tuần cuối so với tuần 9–32)" value={data.summary.growth_first_last_24w != null ? signed(data.summary.growth_first_last_24w) : '–'} tone={(data.summary.growth_first_last_24w ?? 0) >= 0 ? 'up' : 'down'} />
            <Kpi label="Tỷ lệ giảm giá" value={fmtPct(data.summary.disc_rate)} hint="thẻ + coupon / doanh thu" />
            <Kpi label="Tỷ trọng nhãn riêng" value={fmtPct(data.summary.private_share)} />
          </div>
          <Panel title="Doanh thu tuần, giảm giá và nhãn riêng">{line && <RawChart option={line} height={360} />}</Panel>
          <Panel title="Cơ cấu ngành đã chọn">
            <div className="-mx-5 overflow-x-auto"><table className="w-full text-[0.88rem] tabular">
              <thead><tr className="bg-soft font-mono text-[0.7rem] uppercase tracking-wider text-muted">{['Ngành', 'Doanh thu (USD)', 'Tỷ trọng', 'Nhãn riêng', 'Giảm giá'].map((h) => <th key={h} className="px-4 py-2 text-left">{h}</th>)}</tr></thead>
              <tbody>{data.mix.map((m) => (<tr key={m.department} className="border-t border-line"><td className="px-4 py-2 font-medium">{m.department}</td><td className="px-4 py-2">{fmtNum(m.sales)}</td>
                <td className="px-4 py-2">{fmtPct(m.sales / data.summary.sales)}</td><td className="px-4 py-2">{fmtPct(m.private_share)}</td><td className="px-4 py-2">{fmtPct(m.disc_rate)}</td></tr>))}</tbody>
            </table></div>
          </Panel>
        </div>
      ) : !error && <Skeleton h={420} />}
    </div>
  );
}

export default function Explorer() {
  const [tab, setTab] = useState<'m5' | 'cj'>('m5');
  return (
    <div className="grid gap-6">
      <header className="grid max-w-3xl gap-3"><Eyebrow>Công cụ · Tra cứu dữ liệu</Eyebrow>
        <h1 className="font-display text-[clamp(1.7rem,3.4vw,2.5rem)] font-bold leading-[1.1]">Tự lọc và đào sâu số liệu bán hàng</h1>
        <p className="text-[1.03rem] text-muted">Chuỗi cửa hàng: lượng bán và doanh thu theo ngày, tuần, tháng cho từng vùng, cửa hàng, nhóm hàng. Khách thành viên: doanh thu tuần, tỷ lệ giảm giá và nhãn riêng theo ngành hàng. Truy vấn chạy trực tiếp trên máy chủ.</p></header>
      <Segmented value={tab} options={[{ value: 'm5', label: 'Chuỗi cửa hàng (M5)' }, { value: 'cj', label: 'Khách thành viên (CJ)' }]} onChange={setTab} />
      {tab === 'm5' ? <M5 /> : <CJ />}
    </div>
  );
}
