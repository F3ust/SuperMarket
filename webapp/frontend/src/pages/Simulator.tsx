import { useState } from 'react';
import { fmtPct, signed, useApi, usePost } from '../api';
import { ErrorBox, Eyebrow, Kpi, Panel, RawChart, Segmented, Skeleton } from '../components/ui';
import { ax, base, T } from '../charts/registry';

type PromoCat = { category: string; elasticity: number; lift_display: number; lift_feature: number; rival_effect: number; implied_margin: number };
type Options = { promotion: PromoCat[]; price: Record<string, string[]> };
type PromoOut = { units_mult: number; revenue_change: number; profit_change: number; profit_change_range: [number, number]; best_cut: number; best_profit_change: number;
  breakeven_margin_price_only: number | null; elasticity: number; curve: { cut: number; units_mult: number; revenue_change: number; profit_change: number }[] };
type PriceOut = { elasticity: number; ci: [number, number]; units_change: number; units_range: [number, number]; revenue_change: number; revenue_range: [number, number] };

const title = (s: string) => s.charAt(0) + s.slice(1).toLowerCase();

function Slider({ id, label, value, min, max, step, fmt, onChange }: { id: string; label: string; value: number; min: number; max: number; step: number; fmt: (v: number) => string; onChange: (v: number) => void }) {
  return (
    <label htmlFor={id} className="grid gap-1.5">
      <span className="flex justify-between text-[0.86rem]"><span className="text-muted">{label}</span><b className="tabular">{fmt(value)}</b></span>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} className="w-full" />
    </label>
  );
}
function Toggle({ id, label, checked, onChange }: { id: string; label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label htmlFor={id} className="flex cursor-pointer items-center justify-between gap-3 rounded-lg border border-line px-3 py-2 text-[0.88rem]">
      {label}
      <input id={id} type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} className="h-4 w-4 accent-[var(--accent)]" />
    </label>
  );
}

function Promotion({ cats }: { cats: PromoCat[] }) {
  const [p, setP] = useState({ category: 'COLD CEREAL', margin: 0.3, cut: 0.1, display: true, feature: false, rival_share: 0, include_post: true });
  const set = (k: keyof typeof p) => (v: unknown) => setP((s) => ({ ...s, [k]: v }));
  const { data: r, error } = usePost<PromoOut>('/api/simulate/promotion', p);
  const cat = cats.find((c) => c.category === p.category)!;
  const t = T();
  const option = r && {
    ...base(t),
    grid: { left: 12, right: 56, top: 40, bottom: 36, containLabel: true },
    tooltip: { trigger: 'axis', valueFormatter: (v: number) => fmtPct(v, 1) },
    xAxis: ax(t, { type: 'value', min: 0, max: 0.4, name: 'Mức giảm giá', nameLocation: 'middle', nameGap: 26, axisLabel: { color: t.muted, formatter: (v: number) => fmtPct(v, 0) } }),
    yAxis: ax(t, { type: 'value', axisLabel: { color: t.muted, formatter: (v: number) => fmtPct(v, 0) } }),
    series: [
      { name: 'Lợi nhuận', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 3, color: t.accent }, itemStyle: { color: t.accent }, data: r.curve.map((c) => [c.cut, c.profit_change]),
        markLine: { silent: true, symbol: 'none', lineStyle: { color: t.muted, type: 'dashed' }, label: { color: t.muted, formatter: 'hòa vốn' }, data: [{ yAxis: 0 }] },
        markPoint: { symbol: 'circle', symbolSize: 12, itemStyle: { color: t.ink }, label: { show: false }, data: [{ coord: [p.cut, r.profit_change] }] } },
      { name: 'Doanh thu', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2, color: t.src('m5'), type: 'dashed' }, itemStyle: { color: t.src('m5') }, data: r.curve.map((c) => [c.cut, c.revenue_change]) },
    ],
  };
  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)]">
      <Panel title="Tham số" sub="Hệ số lấy từ mô hình hiệu ứng cố định trên Breakfast at the Frat">
        <div className="grid gap-4 pb-3">
          <label htmlFor="cat" className="grid gap-1.5 text-[0.86rem]"><span className="text-muted">Ngành hàng</span>
            <select id="cat" value={p.category} onChange={(e) => set('category')(e.target.value)} className="rounded-lg border border-line bg-surface px-3 py-2">
              {cats.map((c) => <option key={c.category} value={c.category}>{title(c.category)} (e = {c.elasticity.toFixed(2).replace('.', ',')})</option>)}
            </select></label>
          <Slider id="margin" label="Biên gộp hiện tại" value={p.margin} min={0.1} max={0.6} step={0.01} fmt={(v) => fmtPct(v, 0)} onChange={set('margin')} />
          <Slider id="cut" label="Mức giảm giá" value={p.cut} min={0} max={0.4} step={0.01} fmt={(v) => fmtPct(v, 0)} onChange={set('cut')} />
          <Toggle id="display" label={`Trưng bày (+${fmtPct(cat.lift_display, 0)} lượng)`} checked={p.display} onChange={set('display')} />
          <Toggle id="feature" label={`Tờ rơi (+${fmtPct(cat.lift_feature, 0)} lượng)`} checked={p.feature} onChange={set('feature')} />
          <Slider id="rival" label="Tỷ lệ đối thủ cùng ngành khuyến mãi" value={p.rival_share} min={0} max={1} step={0.05} fmt={(v) => fmtPct(v, 0)} onChange={set('rival_share')} />
          <Toggle id="post" label="Tính hiệu ứng 2 tuần sau" checked={p.include_post} onChange={set('include_post')} />
        </div>
      </Panel>
      <div className="grid min-w-0 content-start gap-5">
        {error && <ErrorBox msg={error} />}
        {r ? (
          <>
            <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
              <Kpi label="Lượng bán" value={`×${r.units_mult.toFixed(2).replace('.', ',')}`} hint="so với không khuyến mãi" />
              <Kpi label="Doanh thu" value={signed(r.revenue_change)} tone={r.revenue_change >= 0 ? 'up' : 'down'} />
              <Kpi label="Lợi nhuận gộp" value={signed(r.profit_change)} tone={r.profit_change >= 0 ? 'up' : 'down'} hint={`KTC co giãn: ${signed(r.profit_change_range[0], 0)} → ${signed(r.profit_change_range[1], 0)}`} />
              <Kpi label="Mức giảm có lợi nhuận cao nhất" value={fmtPct(r.best_cut, 0)} hint={r.best_cut === 0 && (p.display || p.feature) ? `chỉ trưng bày/tờ rơi, không giảm giá: ${signed(r.best_profit_change)}` : `lợi nhuận ${signed(r.best_profit_change)}`} />
            </div>
            <Panel title="Lợi nhuận và doanh thu theo mức giảm giá" sub="Chấm đen là lựa chọn hiện tại; trên đường đứt là có lãi so với không khuyến mãi"><RawChart option={option!} height={330} /></Panel>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-card border border-line bg-surface px-5 py-4 text-[0.92rem]"><div className="mb-2 font-mono text-[0.68rem] font-semibold uppercase tracking-[0.12em] text-data">Cách tính</div>
                Lượng mới = (1 − mức giảm)<sup>e</sup> × (1 + trưng bày) × (1 + tờ rơi) × e<sup>β·đối thủ</sup>. Lợi nhuận = (biên − mức giảm) × lượng, so với biên × 1 khi không khuyến mãi. Biên gộp là giả định của người dùng vì dữ liệu không có giá vốn.</div>
              <div className="rounded-card border border-line bg-surface px-5 py-4 text-[0.92rem]"><div className="mb-2 font-mono text-[0.68rem] font-semibold uppercase tracking-[0.12em] text-econ">Đọc kết quả</div>
                {r.breakeven_margin_price_only != null
                  ? <>Chỉ xét giá, giảm {fmtPct(p.cut, 0)} có lãi khi biên hiện tại thấp hơn <b>{fmtPct(r.breakeven_margin_price_only, 0)}</b>. Biên tối ưu ngụ ý của ngành theo quy tắc Lerner: <b>{fmtPct(cat.implied_margin, 0)}</b>.</>
                  : <>Không giảm giá thì không có thay đổi do giá.</>}
                {' '}Mô phỏng chưa trừ phần ăn mòn SKU khác khi chính mình khuyến mãi, nên là cận trên.</div>
            </div>
          </>
        ) : <Skeleton h={420} />}
      </div>
    </div>
  );
}

function Price({ options }: { options: Record<string, string[]> }) {
  const [src, setSrc] = useState<'batf' | 'carbo' | 'm5'>('batf');
  const [cat, setCat] = useState('FROZEN PIZZA');
  const [change, setChange] = useState(0.05);
  const category = options[src].includes(cat) ? cat : options[src][0];
  const { data: r } = usePost<PriceOut>('/api/simulate/price', { source: src, category, change });
  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)]">
      <Panel title="Thay đổi giá" sub="Dùng độ co giãn đã ước lượng và khoảng tin cậy 95%">
        <div className="grid gap-4 pb-3">
          <Segmented value={src} options={[{ value: 'batf', label: 'BATF' }, { value: 'carbo', label: 'Carbo' }, { value: 'm5', label: 'M5' }]} onChange={(v) => { setSrc(v); setCat(options[v][0]); }} />
          <label htmlFor="pcat" className="grid gap-1.5 text-[0.86rem]"><span className="text-muted">Ngành</span>
            <select id="pcat" value={category} onChange={(e) => setCat(e.target.value)} className="rounded-lg border border-line bg-surface px-3 py-2">
              {options[src].map((c) => <option key={c} value={c}>{title(c)}</option>)}</select></label>
          <Slider id="chg" label="Thay đổi giá" value={change} min={-0.3} max={0.3} step={0.01} fmt={(v) => signed(v, 0)} onChange={setChange} />
        </div>
      </Panel>
      {r ? (
        <div className="grid content-start gap-3 sm:grid-cols-3">
          <Kpi label="Độ co giãn" value={r.elasticity.toFixed(2).replace('.', ',')} hint={`KTC ${r.ci[0].toFixed(2)} → ${r.ci[1].toFixed(2)}`.replace(/\./g, ',')} />
          <Kpi label="Lượng bán" value={signed(r.units_change)} tone={r.units_change >= 0 ? 'up' : 'down'} hint={`${signed(r.units_range[0])} → ${signed(r.units_range[1])}`} />
          <Kpi label="Doanh thu" value={signed(r.revenue_change)} tone={r.revenue_change >= 0 ? 'up' : 'down'} hint={`${signed(r.revenue_range[0])} → ${signed(r.revenue_range[1])}`} />
          <p className="text-[0.9rem] text-muted sm:col-span-3">{Math.abs(r.elasticity) < 1
            ? 'Ngành ít co giãn (|e| < 1): tăng giá làm doanh thu tăng vì lượng bán giảm ít hơn mức tăng giá.'
            : 'Ngành co giãn mạnh (|e| > 1): tăng giá làm doanh thu giảm; giảm giá tăng doanh thu nhưng chỉ có lãi khi biên đủ lớn.'} Co giãn của Carbo và M5 tính từ giá suy ra nên có thể bị kéo về 0.</p>
        </div>
      ) : <Skeleton h={200} />}
    </div>
  );
}

export default function Simulator() {
  const { data, error } = useApi<Options>('/api/simulate/options');
  const [tab, setTab] = useState<'promo' | 'price'>('promo');
  return (
    <div className="grid gap-6">
      <header className="grid max-w-3xl gap-3"><Eyebrow>Công cụ · Mô phỏng giá & khuyến mãi</Eyebrow>
        <h1 className="font-display text-[clamp(1.7rem,3.4vw,2.5rem)] font-bold leading-[1.1]">Thử quyết định trước khi làm thật: đợt giảm giá này có lãi không?</h1>
        <p className="text-[1.03rem] text-muted">Nhập biên lãi gộp của ngành, chọn mức giảm và hình thức hỗ trợ. Hệ thống tính lượng bán, doanh thu, lợi nhuận và mức giảm tốt nhất từ phản ứng của khách đã đo được: độ nhạy giá, hiệu ứng trưng bày, tờ rơi, hàng cùng ngành bị lấn át và tuần sau khuyến mãi.</p></header>
      <Segmented value={tab} options={[{ value: 'promo', label: 'Khuyến mãi' }, { value: 'price', label: 'Thay đổi giá' }]} onChange={setTab} />
      {error && <ErrorBox msg={error} />}
      {data ? (tab === 'promo' ? <Promotion cats={data.promotion} /> : <Price options={data.price} />) : !error && <Skeleton h={420} />}
    </div>
  );
}
