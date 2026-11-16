import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import ReactECharts from 'echarts-for-react';
import { chartOption, type ChartState } from '../charts/registry';
import { useApi, type ChartData, type Lens } from '../api';

/* ---------------- Theme: 'system' | 'light' | 'dark'; tick tăng mỗi khi màu đổi để biểu đồ vẽ lại */
type Theme = 'system' | 'light' | 'dark';
const ThemeCtx = createContext<{ theme: Theme; setTheme: (t: Theme) => void; tick: number }>({ theme: 'system', setTheme: () => {}, tick: 0 });

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    try { return (localStorage.getItem('ri-theme') as Theme) || 'system'; } catch { return 'system'; }
  });
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const el = document.documentElement;
    if (theme === 'system') el.removeAttribute('data-theme'); else el.setAttribute('data-theme', theme);
    try { if (theme === 'system') localStorage.removeItem('ri-theme'); else localStorage.setItem('ri-theme', theme); } catch { /* bỏ qua */ }
    setTick((x) => x + 1);
  }, [theme]);
  useEffect(() => {
    const mq = matchMedia('(prefers-color-scheme: dark)');
    const f = () => setTick((x) => x + 1);
    mq.addEventListener('change', f);
    return () => mq.removeEventListener('change', f);
  }, []);
  return <ThemeCtx.Provider value={{ theme, setTheme: setThemeState, tick }}>{children}</ThemeCtx.Provider>;
}
export const useTheme = () => useContext(ThemeCtx);

/* ---------------- Biểu đồ theo id trong registry */
const HEIGHT: Record<string, number> = { cTimeline: 260, cElastic: 520, cEvents: 560, cPromo: 680, cRules: 520 };

export function useChartData() {
  return useApi<ChartData>('/api/charts');
}

export function Chart({ id, state, height }: { id: string; state?: ChartState; height?: number }) {
  const { tick } = useTheme();
  const { data, error } = useChartData();
  if (error) return <ErrorBox msg={error} />;
  if (!data) return <Skeleton h={height ?? HEIGHT[id] ?? 360} />;
  const option = chartOption(id, data, state);
  if (!option) return <ErrorBox msg={`Không có biểu đồ ${id}`} />;
  return <ReactECharts key={`${id}-${tick}-${JSON.stringify(state ?? {})}`} option={option} notMerge style={{ height: height ?? HEIGHT[id] ?? 360, width: '100%' }} opts={{ renderer: 'canvas' }} />;
}

/** Biểu đồ với option tự dựng (trang Mô phỏng, Khám phá). */
export function RawChart({ option, height = 340 }: { option: object; height?: number }) {
  const { tick } = useTheme();
  return <ReactECharts key={tick} option={option} notMerge style={{ height, width: '100%' }} />;
}

/* ---------------- Khối giao diện */
export const SRC_LABEL: Record<string, string> = { cj: 'CJ', batf: 'BATF', carbo: 'Carbo', lgsr: 'LGSR', m5: 'M5' };
const SRC_BG: Record<string, string> = { cj: 'bg-cj', batf: 'bg-batf', carbo: 'bg-carbo', lgsr: 'bg-lgsr', m5: 'bg-m5' };
export function SourceChip({ src }: { src: string }) {
  const k = src.toLowerCase();
  return <span className={`inline-block rounded-md px-1.5 py-1 font-mono text-[0.68rem] font-semibold leading-none tracking-wide text-white ${SRC_BG[k] ?? 'bg-muted'}`}>{SRC_LABEL[k] ?? src}</span>;
}

export function Panel({ title, sub, children, className = '' }: { title?: string; sub?: string | null; children: ReactNode; className?: string }) {
  return (
    <div className={`min-w-0 rounded-card border border-line bg-surface p-5 pb-3 ${className}`}>
      {title && <h3 className="font-display text-[1.08rem] font-bold leading-snug">{title}</h3>}
      {sub && <p className="mb-2 mt-1 text-[0.84rem] text-muted">{sub}</p>}
      {children}
    </div>
  );
}

export function LensCard({ kind, lens }: { kind: 'data' | 'econ'; lens?: Lens }) {
  if (!lens) return null;
  const isData = kind === 'data';
  return (
    <div className="rounded-card border border-line bg-surface px-5 py-4">
      <div className={`mb-2 flex items-center gap-1.5 font-mono text-[0.68rem] font-semibold uppercase tracking-[0.12em] ${isData ? 'text-data' : 'text-econ'}`}>
        <span className={`inline-block h-2 w-2 rounded-sm ${isData ? 'bg-data' : 'bg-econ'}`} />{isData ? 'Dữ liệu cho thấy' : 'Ý nghĩa kinh doanh'}
      </div>
      {lens.big && <div className="mb-1.5 font-display text-[2rem] font-bold leading-none tabular">{lens.big}</div>}
      <div className="space-y-2 text-[0.93rem]">{lens.paragraphs.map((p, i) => <p key={i}>{p}</p>)}</div>
    </div>
  );
}

export function Segmented<T extends string | number>({ label, value, options, onChange }: { label?: string; value: T; options: { value: T; label: string }[]; onChange: (v: T) => void }) {
  return (
    <div role="group" aria-label={label} className="inline-flex flex-wrap items-center gap-1 rounded-full bg-soft p-1">
      {label && <span className="px-2 font-mono text-[0.66rem] font-semibold uppercase tracking-wider text-muted">{label}</span>}
      {options.map((o) => (
        <button key={String(o.value)} type="button" aria-pressed={o.value === value} onClick={() => onChange(o.value)}
          className={`rounded-full px-3 py-1 text-[0.82rem] font-medium transition ${o.value === value ? 'bg-surface text-ink shadow-sm' : 'text-muted hover:text-ink'}`}>{o.label}</button>
      ))}
    </div>
  );
}

export function Kpi({ label, value, hint, tone }: { label: string; value: ReactNode; hint?: ReactNode; tone?: 'up' | 'down' }) {
  return (
    <div className="min-w-0 rounded-card border border-line bg-surface px-4 py-3.5">
      <div className="text-[0.8rem] text-muted">{label}</div>
      <div className={`mt-1 font-display text-[1.6rem] font-bold leading-tight tabular ${tone === 'up' ? 'text-cj' : tone === 'down' ? 'text-carbo' : ''}`}>{value}</div>
      {hint && <div className="mt-0.5 text-[0.78rem] text-muted">{hint}</div>}
    </div>
  );
}

export function Skeleton({ h = 300 }: { h?: number }) {
  return <div className="animate-pulse rounded-lg bg-soft" style={{ height: h }} aria-label="Đang tải" />;
}
export function ErrorBox({ msg }: { msg: string }) {
  return <div className="rounded-lg border border-carbo/40 bg-carbo/10 px-4 py-3 text-sm text-carbo">Không tải được dữ liệu: {msg}. Vui lòng thử lại sau ít phút.</div>;
}
export function Eyebrow({ children }: { children: ReactNode }) {
  return <div className="font-mono text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-accent">{children}</div>;
}
