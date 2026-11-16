import { useEffect, useState, type ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ArrowRight, CheckCircle2, HelpCircle, SlidersHorizontal, UserRound } from 'lucide-react';
import { useApi, type Finding, type Meta, type Section } from '../api';
import { Chart, ErrorBox, Eyebrow, LensCard, Panel, Segmented, Skeleton, SourceChip } from '../components/ui';
import { MODULES, type Module } from '../modules';

const BASKET = [{ value: 'basket_type', label: 'Loại chuyến' }, { value: 'price_sens', label: 'Độ nhạy giá' }, { value: 'mission', label: 'Nhiệm vụ giỏ' }, { value: 'fmt', label: 'Định dạng cửa hàng' }];
const SWITCH = [{ value: 'pasta sauce', label: 'Sốt mì Ý' }, { value: 'pasta', label: 'Mì Ý' }];

function ChartBlock({ c }: { c: Finding['charts'][number] }) {
  const [basketKey, setBasket] = useState('basket_type');
  const [swKey, setSw] = useState('pasta sauce');
  const [simM, setM] = useState(0.3);
  const [simC, setC] = useState(0.1);
  return (
    <Panel title={c.title} sub={c.sub}>
      {c.chart === 'cBasket' && <div className="mb-2"><Segmented label="Chiều" value={basketKey} options={BASKET} onChange={setBasket} /></div>}
      {c.chart === 'cSwitch' && <div className="mb-2"><Segmented value={swKey} options={SWITCH} onChange={setSw} /></div>}
      {c.chart === 'cSim' && (
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <Segmented label="Biên gộp" value={simM} options={[0.2, 0.3, 0.4].map((v) => ({ value: v, label: `${v * 100}%` }))} onChange={setM} />
          <Segmented label="Giảm giá" value={simC} options={[0.1, 0.2, 0.3].map((v) => ({ value: v, label: `${Math.round(v * 100)}%` }))} onChange={setC} />
          <Link to="/mo-phong" className="ml-auto inline-flex items-center gap-1 text-[0.82rem] font-medium text-accent hover:underline"><SlidersHorizontal size={14} />Mở công cụ mô phỏng</Link>
        </div>
      )}
      <Chart id={c.chart} state={{ basketKey, swKey, simM, simC }} />
    </Panel>
  );
}

function FindingView({ f }: { f: Finding }) {
  const hasLens = f.data || f.econ;
  if (!hasLens) {
    return <div className={`grid gap-5 ${f.charts.length > 1 ? 'lg:grid-cols-2' : ''}`}>{f.charts.map((c) => <ChartBlock key={c.chart} c={c} />)}</div>;
  }
  return (
    <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1.65fr)_minmax(0,1fr)]">
      <div className="grid min-w-0 gap-5">{f.charts.map((c) => <ChartBlock key={c.chart} c={c} />)}</div>
      <div className="grid min-w-0 gap-4"><LensCard kind="data" lens={f.data} /><LensCard kind="econ" lens={f.econ} /></div>
    </div>
  );
}

function SourcesBlock() {
  const { data: meta } = useApi<Meta>('/api/meta');
  if (!meta) return <Skeleton h={300} />;
  const keys = ['cj', 'batf', 'carbo', 'lgsr', 'm5'];
  return (
    <div className="grid gap-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {meta.sources.map((s) => (
          <article key={s.key} className="grid content-start gap-2.5 rounded-card border border-line bg-surface px-5 py-4">
            <div className="flex items-start gap-3">
              <span className={`mt-2 h-3 w-3 flex-none rounded-full bg-${s.key}`} style={{ boxShadow: `0 0 0 4px rgb(var(--${s.key}-rgb) / .2)` }} />
              <div><h3 className="font-display text-[1.12rem] font-bold">{s.name}</h3><p className="font-mono text-[0.74rem] text-muted">{s.sub}</p></div>
            </div>
            <p className="text-[0.92rem]">{s.desc}</p>
            <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 border-t border-dashed border-line pt-2.5 text-[0.85rem]">
              <dt className="text-muted">Hạt dữ liệu</dt><dd>{s.grain}</dd><dt className="text-muted">Trả lời được</dt><dd>{s.answers}</dd>
            </dl>
          </article>
        ))}
      </div>
      <Panel title="Ma trận trường dữ liệu" sub="Mỗi nguồn có những trường nguồn khác không có — đó là lý do trộn nhiều nguồn.">
        <div className="-mx-5 overflow-x-auto">
          <table className="w-full text-[0.88rem]">
            <thead><tr className="bg-soft font-mono text-[0.7rem] uppercase tracking-wider text-muted">
              <th className="px-4 py-2.5 text-left">Nhóm trường</th>{keys.map((k) => <th key={k} className="px-2 py-2.5"><SourceChip src={k} /></th>)}<th className="px-4 py-2.5 text-left">Ghi chú</th></tr></thead>
            <tbody>{meta.fields.map((f) => (
              <tr key={f.field} className="border-t border-line">
                <th scope="row" className="whitespace-nowrap px-4 py-2 text-left font-semibold">{f.field}</th>
                {keys.map((k) => <td key={k} className="px-2 py-2 text-center">{f.have.includes(k) ? <span className={`inline-block h-3.5 w-3.5 rounded-full bg-${k}`} title="có" /> : <span className="text-line">·</span>}</td>)}
                <td className="min-w-[220px] px-4 py-2 text-[0.82rem] text-muted">{f.note}</td>
              </tr>))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}

function QualityBlock() {
  const { data: meta } = useApi<Meta>('/api/meta');
  if (!meta) return <Skeleton h={300} />;
  return (
    <div className="overflow-x-auto rounded-card border border-line bg-surface">
      <table className="w-full text-[0.88rem]">
        <thead><tr className="bg-soft font-mono text-[0.7rem] uppercase tracking-wider text-muted">
          {['Nguồn', 'Giới hạn chính', 'Bằng chứng trong dữ liệu', 'Cách xử lý'].map((h) => <th key={h} className="px-4 py-2.5 text-left">{h}</th>)}</tr></thead>
        <tbody>{meta.quality.map((q) => (
          <tr key={q.source} className="border-t border-line align-top">
            <td className="px-4 py-3"><SourceChip src={q.source} /></td><td className="min-w-[180px] px-4 py-3 font-semibold">{q.limit}</td>
            <td className="min-w-[260px] px-4 py-3">{q.evidence}</td><td className="min-w-[240px] px-4 py-3 text-muted">{q.handling}</td>
          </tr>))}
        </tbody>
      </table>
    </div>
  );
}


const stripEyebrow = (t: string) => t.replace(/^Chương \d+ · /, '');

function SectionBlock({ id, index }: { id: string; index: number }) {
  const { data: s, error } = useApi<Section>(`/api/sections/${id}`);
  if (error) return <ErrorBox msg={error} />;
  if (!s) return <Skeleton h={420} />;
  return (
    <section id={id} className="grid scroll-mt-20 gap-6">
      <header className="grid max-w-3xl gap-2 border-t border-line pt-8">
        <div className="flex items-center gap-2 font-mono text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-muted">
          <span className="grid h-6 w-6 place-items-center rounded-md bg-accent/15 text-accent">{index + 1}</span>{stripEyebrow(s.eyebrow)}
        </div>
        <h2 className="font-display text-[clamp(1.35rem,2.6vw,1.9rem)] font-bold leading-[1.15]">{s.title}</h2>
        {s.lead && <p className="text-[0.98rem] text-muted">{s.lead}</p>}
      </header>
      {s.callout && <p className="max-w-[70ch] border-l-[3px] border-accent pl-4 text-[1rem]">{s.callout}</p>}
      {id === 'nguon' && <SourcesBlock />}
      {id === 'du-lieu' && <QualityBlock />}
      {s.findings.map((f, i) => <FindingView key={i} f={f} />)}
      {s.cards.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {s.cards.map((c) => (
            <article key={c.title} className="grid content-start gap-2.5 rounded-card border border-line bg-surface p-5">
              <div className="flex flex-wrap items-center gap-1.5"><span className="mr-1 text-[0.74rem] text-muted">Xác nhận bởi</span>{c.sources.map((x) => <SourceChip key={x} src={x} />)}</div>
              <h3 className="font-display text-[1.06rem] font-bold">{c.title}</h3><p className="text-[0.92rem] text-muted">{c.body}</p>
            </article>))}
        </div>
      )}
      {s.actions.length > 0 && (
        <ol className="grid gap-3">
          {s.actions.map((a, i) => (
            <li key={a.title} className="grid grid-cols-[44px_1fr] gap-3.5 rounded-card border border-line bg-surface px-5 py-4">
              <span className="font-display text-[1.3rem] font-bold text-accent">{String(i + 1).padStart(2, '0')}</span>
              <div><h3 className="mb-1 font-display text-[1.03rem] font-bold">{a.title}</h3><p className="text-[0.92rem] text-muted">{a.body}</p></div>
            </li>))}
        </ol>
      )}
    </section>
  );
}

export default function ModulePage({ m, children }: { m: Module; children?: ReactNode }) {
  const { hash } = useLocation();
  useEffect(() => {
    if (!hash) return;
    const t = setTimeout(() => document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth' }), 400);
    return () => clearTimeout(t);
  }, [hash]);
  const idx = MODULES.findIndex((x) => x.id === m.id);
  const next = idx >= 0 ? MODULES[idx + 1] : undefined;
  const Icon = m.icon;
  return (
    <article className="grid gap-10">
      <header className="grid gap-6 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)] lg:items-end">
        <div className="grid gap-3">
          <Eyebrow><span className="inline-flex items-center gap-1.5"><Icon size={14} />{idx >= 0 ? 'Phân hệ phân tích' : 'Bản demo'} · {m.nav}</span></Eyebrow>
          <h1 className="font-display text-[clamp(1.8rem,3.6vw,2.7rem)] font-bold leading-[1.08]">{m.title}</h1>
          <p className="max-w-[62ch] text-[1.03rem] text-muted">{m.lead}</p>
          {m.roles.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 text-[0.8rem]"><UserRound size={14} className="text-muted" /><span className="text-muted">Dành cho</span>
              {m.roles.map((r) => <span key={r} className="rounded-full border border-line px-2.5 py-0.5">{r}</span>)}</div>
          )}
        </div>
        {m.questions.length > 0 && (
          <div className="rounded-card border border-line bg-surface p-5">
            <div className="mb-2 flex items-center gap-1.5 font-mono text-[0.68rem] font-semibold uppercase tracking-[0.12em] text-accent"><HelpCircle size={13} />Câu hỏi phân hệ trả lời</div>
            <ul className="grid gap-1.5 text-[0.9rem]">{m.questions.map((q) => <li key={q} className="flex gap-2"><CheckCircle2 size={16} className="mt-0.5 flex-none text-cj" />{q}</li>)}</ul>
          </div>
        )}
      </header>
      {m.headline && (
        <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 rounded-card bg-brand px-6 py-5 text-brand-ink">
          <b className="font-display text-[clamp(1.8rem,4vw,2.6rem)] leading-none text-accent tabular">{m.headline.value}</b>
          <span className="max-w-[60ch] text-[0.98rem] text-brand-ink/85">{m.headline.label}</span>
        </div>
      )}
      {m.sections.length > 1 && (
        <nav aria-label="Mục trong phân hệ" className="-mt-4 flex flex-wrap gap-2 text-[0.84rem]">
          {m.sections.map((id, i) => <a key={id} href={`#${id}`} className="rounded-full bg-soft px-3 py-1 text-muted hover:text-ink">{i + 1}. <SectionName id={id} /></a>)}
        </nav>
      )}
      {m.sections.map((id, i) => <SectionBlock key={id} id={id} index={i} />)}
      {children}
      {next && (
        <Link to={next.path} className="group mt-2 flex items-center justify-between gap-4 rounded-card border border-line bg-surface px-6 py-5 hover:border-accent">
          <div><div className="text-[0.8rem] text-muted">Phân hệ tiếp theo</div><div className="font-display text-[1.2rem] font-bold">{next.nav}: {next.title}</div></div>
          <ArrowRight className="flex-none text-accent transition group-hover:translate-x-1" />
        </Link>
      )}
    </article>
  );
}

function SectionName({ id }: { id: string }) {
  const { data } = useApi<{ id: string; eyebrow: string }[]>('/api/sections');
  const s = data?.find((x) => x.id === id);
  return <>{s ? stripEyebrow(s.eyebrow) : id}</>;
}
