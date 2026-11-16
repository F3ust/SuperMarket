import { useEffect, useRef, useState } from 'react';

export type Lens = { big: string | null; paragraphs: string[] };
export type ChartRef = { chart: string; title: string; sub: string | null; controls: (string | null)[] };
export type Finding = { charts: ChartRef[]; data?: Lens; econ?: Lens };
export type Section = {
  id: string; eyebrow: string; title: string; lead: string | null; callout: string | null;
  findings: Finding[]; cards: { sources: string[]; title: string; body: string }[]; actions: { title: string; body: string }[];
};
export type SectionInfo = Pick<Section, 'id' | 'eyebrow' | 'title'>;
export type Meta = {
  kpis: { total_rows: number; sources: number; period: string; stores: number; field_groups: number };
  sources: { key: string; name: string; sub: string; desc: string; grain: string; answers: string }[];
  fields: { field: string; have: string[]; note: string }[];
  quality: { source: string; limit: string; evidence: string; handling: string }[];
};
export type ChartData = { D: any; D2: any };

/** Gốc API. Để trống khi frontend và API cùng domain (Vercel, FastAPI phục vụ dist). Đặt VITE_API_BASE nếu API ở domain khác. */
export const API_BASE = (import.meta.env.VITE_API_BASE ?? '').replace(/\/$/, '');
export const apiUrl = (path: string) => (path.startsWith('http') ? path : API_BASE + path);

const cache = new Map<string, Promise<unknown>>();

export async function getJSON<T>(url: string, useCache = true): Promise<T> {
  if (useCache && cache.has(url)) return cache.get(url) as Promise<T>;
  const p = fetch(apiUrl(url)).then(async (r) => {
    if (!r.ok) throw new Error(`${r.status} ${(await r.json().catch(() => ({}))).detail ?? r.statusText}`);
    return r.json();
  });
  if (useCache) cache.set(url, p);
  p.catch(() => cache.delete(url));
  return p as Promise<T>;
}

export async function postJSON<T>(url: string, body: unknown): Promise<T> {
  const r = await fetch(apiUrl(url), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`${r.status} ${(await r.json().catch(() => ({}))).detail ?? r.statusText}`);
  return r.json();
}

/** Tải dữ liệu GET, trả về {data, error, loading}. */
export function useApi<T>(url: string | null, useCache = true) {
  const [state, setState] = useState<{ data?: T; error?: string; loading: boolean }>({ loading: !!url });
  useEffect(() => {
    if (!url) return;
    let live = true;
    setState((s) => ({ ...s, loading: true, error: undefined }));
    getJSON<T>(url, useCache).then((data) => live && setState({ data, loading: false }), (e) => live && setState({ error: String(e.message ?? e), loading: false }));
    return () => { live = false; };
  }, [url, useCache]);
  return state;
}

/** POST có debounce cho các form mô phỏng. */
export function usePost<T>(url: string, body: unknown, delay = 180) {
  const [state, setState] = useState<{ data?: T; error?: string; loading: boolean }>({ loading: true });
  const key = JSON.stringify(body);
  const seq = useRef(0);
  useEffect(() => {
    const id = ++seq.current;
    setState((s) => ({ ...s, loading: true }));
    const h = setTimeout(() => {
      postJSON<T>(url, JSON.parse(key)).then((data) => id === seq.current && setState({ data, loading: false }),
        (e) => id === seq.current && setState((s) => ({ ...s, error: String(e.message ?? e), loading: false })));
    }, delay);
    return () => clearTimeout(h);
  }, [url, key, delay]);
  return state;
}

export const fmtPct = (v: number | null | undefined, d = 1) => (v == null || Number.isNaN(v) ? '–' : `${(v * 100).toFixed(d).replace('.', ',')}%`);
export const fmtNum = (v: number | null | undefined, d = 0) => (v == null ? '–' : v.toLocaleString('vi-VN', { maximumFractionDigits: d, minimumFractionDigits: d }));
export const signed = (v: number, d = 1) => (v > 0 ? '+' : '') + fmtPct(v, d);
