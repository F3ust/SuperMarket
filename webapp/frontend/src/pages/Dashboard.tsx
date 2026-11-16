import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, ArrowDownRight, ArrowUpRight, CalendarX2, Info, Newspaper, SlidersHorizontal, Store } from 'lucide-react';
import { fmtNum, fmtPct, useApi } from '../api';
import { ErrorBox, Eyebrow, Panel, RawChart, Segmented, Skeleton } from '../components/ui';
import { ax, base, T } from '../charts/registry';

type Grain = 'month' | 'quarter' | 'year';
type Periods = Record<Grain, string[]> & { default: { grain: Grain; key: string } };
type K = { value: number | null; prev: number | null; yoy: number | null };
type Dash = {
  period: { label: string; prev_label: string; yoy_label: string; start: string; end: string };
  kpis: { revenue: K; units: K; price: K; per_store_day: K; stores: number };
  stores: { store: string; state: string; revenue: number; share: number; per_day: number; yoy: number | null }[];
  depts: { cat: string; cat_vi: string; dept: string; revenue: number; share: number; yoy: number | null; delta: number | null }[];
  trend: Record<string, (number | null)[]>; weekday: { wd: string; revenue: number | null }[]; weekend_share: number | null;
  daily: { d: string; revenue: number }[];
  alerts: { level: 'high' | 'medium' | 'info'; kind: string; title: string; body: string }[]; news: string[];
};

const STATES = [{ v: '', l: 'Tất cả vùng' }, { v: 'CA', l: 'California' }, { v: 'TX', l: 'Texas' }, { v: 'WI', l: 'Wisconsin' }];
const CATS = [{ v: '', l: 'Tất cả ngành' }, { v: 'FOODS', l: 'Thực phẩm' }, { v: 'HOUSEHOLD', l: 'Gia dụng' }, { v: 'HOBBIES', l: 'Giải trí' }];
const STORES = ['CA_1', 'CA_2', 'CA_3', 'CA_4', 'TX_1', 'TX_2', 'TX_3', 'WI_1', 'WI_2', 'WI_3'];

const periodLabel = (g: Grain, k: string) => g === 'year' ? `Năm ${k}` : g === 'quarter' ? `Quý ${k.slice(-1)}/${k.slice(0, 4)}` : `Tháng ${+k.slice(5)}/${k.slice(0, 4)}`;
const usd = (v: number | null | undefined, d = 2) => v == null ? '–' : Math.abs(v) >= 1e6 ? `${fmtNum(v / 1e6, d)} tr` : `${fmtNum(v / 1e3, 0)} nghìn`;

function Delta({ v, label }: { v: number | null; label: string }) {
  if (v == null) return <span className="text-muted">{label}: –</span>;
  const up = v >= 0;
  const Icon = up ? ArrowUpRight : ArrowDownRight;
  return <span className="inline-flex items-center gap-0.5"><b className={`inline-flex items-center font-semibold ${up ? 'text-cj' : 'text-carbo'}`}><Icon size={14} />{fmtPct(Math.abs(v))}</b><span className="text-muted">&nbsp;{label}</span></span>;
}

function KpiCard({ label, value, unit, k }: { label: string; value: string; unit?: string; k: K }) {
  return (
    <div className="grid min-w-0 content-start gap-1 rounded-card border border-line bg-surface px-4 py-4">
      <div className="text-[0.8rem] text-muted">{label}</div>
      <div className="font-display text-[clamp(1.4rem,2.4vw,1.85rem)] font-bold leading-tight tabular">{value}{unit && <span className="ml-1 text-[0.85rem] font-medium text-muted">{unit}</span>}</div>
      <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-[0.78rem]"><Delta v={k.yoy} label="cùng kỳ" /><Delta v={k.prev} label="kỳ trước" /></div>
    </div>
  );
}

function Select({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: { v: string; l: string }[] }) {
  return (
    <label className="grid min-w-0 gap-1 text-[0.78rem]"><span className="text-muted">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)} className="min-w-0 rounded-lg border border-line bg-surface px-3 py-2 text-[0.88rem]">
        {options.map((o) => <option key={o.v} value={o.v}>{o.l}</option>)}</select></label>
  );
}

export default function Dashboard() {
  const { data: periods } = useApi<Periods>('/api/dashboard/periods');
  const [grain, setGrain] = useState<Grain>('month');
  const [key, setKey] = useState('');
  const [state, setState] = useState('');
  const [store, setStore] = useState('');
  const [cat, setCat] = useState('');
  useEffect(() => { if (periods && !periods[grain].includes(key)) setKey(periods[grain][0]); }, [periods, grain, key]);
  const qs = new URLSearchParams(Object.entries({ grain, key, state, store, cat }).filter(([, v]) => v)).toString();
  const { data, error, loading } = useApi<Dash>(key ? `/api/dashboard?${qs}` : null);
  const t = T();

  const trend = useMemo(() => {
    if (!data) return null;
    const years = Object.keys(data.trend);
    const cur = data.period.end.slice(0, 4);
    return {
      ...base(t), grid: { left: 8, right: 16, top: 44, bottom: 8, containLabel: true },
      legend: { top: 0, textStyle: { color: t.muted }, itemWidth: 14, itemHeight: 3 },
      tooltip: { trigger: 'axis', valueFormatter: (v: number) => (v == null ? '–' : usd(v) + ' USD') },
      xAxis: ax(t, { type: 'category', data: Array.from({ length: 12 }, (_, i) => `T${i + 1}`), splitLine: { show: false }, axisLabel: { color: t.muted, interval: 0 } }),
      yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: (v: number) => fmtNum(v / 1e6, 1) + ' tr' } }),
      series: years.map((y) => ({
        name: y, type: 'line', symbol: y === cur ? 'circle' : 'none', symbolSize: 6, smooth: 0.2, data: data.trend[y],
        lineStyle: { width: y === cur ? 3 : 1.4, color: y === cur ? t.accent : t.src('m5'), opacity: y === cur ? 1 : 0.25 + 0.6 * (years.indexOf(y) / years.length) },
        itemStyle: { color: y === cur ? t.accent : t.src('m5') }, z: y === cur ? 5 : 1,
      })),
    };
  }, [data, t.ink]); // eslint-disable-line

  const deptChart = data && {
    ...base(t), grid: { left: 8, right: 56, top: 8, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (p: any) => { const d = data.depts[p[0].dataIndex]; return `<b>${d.dept}</b> · ${d.cat_vi}<br/>Doanh thu: ${usd(d.revenue)} USD (${fmtPct(d.share)})<br/>So với cùng kỳ: ${d.yoy == null ? '–' : (d.yoy > 0 ? '+' : '') + fmtPct(d.yoy)}`; } },
    xAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: (v: number) => fmtNum(v / 1e6, 1) + ' tr' } }),
    yAxis: ax(t, { type: 'category', inverse: true, data: data.depts.map((d) => d.dept), splitLine: { show: false }, axisLabel: { color: t.ink, interval: 0 } }),
    series: [{ type: 'bar', barWidth: '58%', data: data.depts.map((d) => ({ value: Math.round(d.revenue), itemStyle: { color: d.cat === 'FOODS' ? t.src('cj') : d.cat === 'HOUSEHOLD' ? t.src('m5') : t.src('lgsr'), borderRadius: [0, 4, 4, 0] } })),
      label: { show: true, position: 'right', color: t.muted, fontSize: 11, formatter: (p: any) => { const y = data.depts[p.dataIndex].yoy; return y == null ? '' : (y > 0 ? '+' : '') + fmtPct(y, 0); } } }],
  };

  const dailyChart = data && {
    ...base(t), grid: { left: 8, right: 16, top: 16, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis', valueFormatter: (v: number) => usd(v) + ' USD' },
    xAxis: ax(t, { type: 'category', data: data.daily.map((d) => `${d.d.slice(8)}/${d.d.slice(5, 7)}`), splitLine: { show: false } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: (v: number) => fmtNum(v / 1e3) + 'k' } }),
    series: [{ type: 'bar', data: data.daily.map((d) => { const wd = new Date(d.d).getUTCDay(); return { value: Math.round(d.revenue), itemStyle: { color: wd === 0 || wd === 6 ? t.accent : t.src('m5'), borderRadius: [2, 2, 0, 0] } }; }) }],
  };

  const k = data?.kpis;
  const levelIcon = { high: AlertTriangle, medium: AlertTriangle, info: CalendarX2 };
  const levelCls = { high: 'border-carbo/50 bg-carbo/10 text-carbo', medium: 'border-batf/50 bg-batf/10 text-batf', info: 'border-line bg-soft text-muted' };

  return (
    <div className="grid gap-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="grid gap-2"><Eyebrow>Bảng điều hành · Chuỗi demo 10 cửa hàng</Eyebrow>
          <h1 className="font-display text-[clamp(1.7rem,3.4vw,2.4rem)] font-bold leading-[1.1]">{data ? `Kết quả kinh doanh ${data.period.label}` : 'Kết quả kinh doanh'}</h1>
          <p className="max-w-[70ch] text-[0.92rem] text-muted">So với kỳ liền trước và cùng kỳ năm trước. Lọc theo vùng, cửa hàng, ngành hàng.</p></div>
        <Link to="/mo-phong" className="inline-flex items-center gap-2 rounded-lg bg-brand px-4 py-2.5 text-[0.88rem] font-medium text-brand-ink hover:opacity-90"><SlidersHorizontal size={16} />Mô phỏng một quyết định giá</Link>
      </header>

      <div className="sticky top-[53px] z-10 -mx-4 border-y border-line bg-bg/95 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6">
        <div className="flex flex-wrap items-end gap-3">
          <Segmented label="Kỳ" value={grain} options={[{ value: 'month', label: 'Tháng' }, { value: 'quarter', label: 'Quý' }, { value: 'year', label: 'Năm' }]} onChange={(g) => setGrain(g as Grain)} />
          <div className="grid flex-1 grid-cols-2 gap-3 sm:grid-cols-4">
            <Select label="Kỳ báo cáo" value={key} onChange={setKey} options={(periods?.[grain] ?? []).map((p) => ({ v: p, l: periodLabel(grain, p) }))} />
            <Select label="Vùng" value={state} onChange={(v) => { setState(v); setStore(''); }} options={STATES} />
            <Select label="Cửa hàng" value={store} onChange={setStore} options={[{ v: '', l: 'Tất cả cửa hàng' }, ...STORES.filter((s) => !state || s.startsWith(state)).map((s) => ({ v: s, l: s }))]} />
            <Select label="Ngành hàng" value={cat} onChange={setCat} options={CATS} />
          </div>
        </div>
      </div>

      {error && <ErrorBox msg={error} />}
      {!data && !error && <div className="grid gap-4"><Skeleton h={110} /><Skeleton h={360} /></div>}
      {data && k && (
        <div className={`grid gap-6 transition-opacity ${loading ? 'opacity-60' : ''}`}>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <KpiCard label="Doanh thu" value={usd(k.revenue.value)} unit="USD" k={k.revenue} />
            <KpiCard label="Lượng bán" value={(k.units.value ?? 0) >= 1e6 ? fmtNum((k.units.value ?? 0) / 1e6, 2) + ' tr' : fmtNum((k.units.value ?? 0) / 1e3, 0) + ' nghìn'} unit="đơn vị" k={k.units} />
            <KpiCard label="Giá bình quân / đơn vị" value={fmtNum(k.price.value, 2)} unit="USD" k={k.price} />
            <KpiCard label="Doanh thu / cửa hàng / ngày" value={fmtNum(k.per_store_day.value, 0)} unit="USD" k={k.per_store_day} />
          </div>

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
            <Panel title="Bản tin điều hành" sub={`Tự sinh từ số liệu ${data.period.label}, so với ${data.period.yoy_label}`}>
              <ul className="grid gap-2.5 pb-2 pt-1">
                {data.news.map((n) => <li key={n} className="flex gap-2.5 text-[0.93rem]"><Newspaper size={16} className="mt-1 flex-none text-accent" />{n}</li>)}
              </ul>
            </Panel>
            <Panel title="Cần chú ý" sub="Cửa hàng, nhóm hàng giảm so với cùng kỳ; ngày doanh thu bất thường">
              {data.alerts.length === 0
                ? <p className="flex items-center gap-2 pb-3 pt-1 text-[0.92rem] text-muted"><Info size={16} />Không có cửa hàng hay nhóm hàng nào giảm đáng kể so với cùng kỳ.</p>
                : <ul className="grid gap-2 pb-2 pt-1">{data.alerts.map((a) => { const I = levelIcon[a.level]; return (
                  <li key={a.title} className={`rounded-lg border px-3 py-2 ${levelCls[a.level]}`}>
                    <div className="flex items-center gap-1.5 text-[0.86rem] font-semibold"><I size={15} />{a.kind}: {a.title}</div>
                    <p className="mt-0.5 text-[0.82rem] text-ink/80">{a.body}</p></li>); })}</ul>}
            </Panel>
          </div>

          <Panel title="Doanh thu theo tháng, mỗi năm một đường" sub={`Năm của kỳ đang xem tô đậm. Các năm trước để so mùa vụ.`}>{trend && <RawChart option={trend} height={330} />}</Panel>

          <div className="grid gap-5 lg:grid-cols-2">
            <Panel title="Xếp hạng cửa hàng" sub={`Doanh thu ${data.period.label} và tăng trưởng so với cùng kỳ`}>
              <div className="-mx-5 overflow-x-auto pb-1">
                <table className="w-full text-[0.86rem] tabular">
                  <thead><tr className="text-left font-mono text-[0.68rem] uppercase tracking-wider text-muted">
                    <th className="px-5 py-2">Cửa hàng</th><th className="px-2 py-2">Doanh thu (USD)</th><th className="px-2 py-2">Tỷ trọng</th><th className="px-5 py-2 text-right">Cùng kỳ</th></tr></thead>
                  <tbody>{data.stores.map((s) => (
                    <tr key={s.store} className="border-t border-line">
                      <td className="px-5 py-2 font-medium"><span className="inline-flex items-center gap-1.5"><Store size={14} className="text-muted" />{s.store}</span></td>
                      <td className="px-2 py-2">{fmtNum(s.revenue)}</td>
                      <td className="px-2 py-2"><div className="flex items-center gap-2"><div className="h-1.5 w-16 overflow-hidden rounded-full bg-soft"><div className="h-full rounded-full bg-m5" style={{ width: `${Math.min(100, s.share * 400)}%` }} /></div>{fmtPct(s.share, 0)}</div></td>
                      <td className={`px-5 py-2 text-right font-semibold ${s.yoy == null ? 'text-muted' : s.yoy >= 0 ? 'text-cj' : 'text-carbo'}`}>{s.yoy == null ? '–' : (s.yoy > 0 ? '+' : '') + fmtPct(s.yoy)}</td>
                    </tr>))}</tbody>
                </table>
              </div>
            </Panel>
            <Panel title="Doanh thu theo nhóm hàng" sub="Nhãn bên phải: tăng trưởng so với cùng kỳ. Màu: thực phẩm, gia dụng, giải trí">{deptChart && <RawChart option={deptChart} height={Math.max(260, data.depts.length * 38)} />}</Panel>
          </div>

          <Panel title="Doanh thu từng ngày trong kỳ" sub={`Cột cam là thứ Bảy, Chủ nhật: chiếm ${fmtPct(data.weekend_share, 0)} doanh thu.`}>{dailyChart && <RawChart option={dailyChart} height={260} />}</Panel>

          <p className="text-[0.78rem] text-muted">Dữ liệu demo: Walmart M5, 10 cửa hàng ở 3 bang của Mỹ, 2011–2016. Doanh thu = lượng bán × giá niêm yết tuần (USD, trước giảm giá). Khi triển khai, màn hình này đọc dữ liệu POS của siêu thị. <Link to="/du-lieu" className="text-accent hover:underline">Xem nguồn dữ liệu</Link></p>
        </div>
      )}
    </div>
  );
}
