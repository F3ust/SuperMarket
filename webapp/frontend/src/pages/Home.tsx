import { useEffect, useRef, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BrainCircuit, Cable, Gauge, LayoutDashboard, SlidersHorizontal, TableProperties } from 'lucide-react';
import { fmtNum, useApi, type Meta, type Section } from '../api';
import { MODULES } from '../modules';
import { Skeleton, SourceChip, useTheme } from '../components/ui';

/** Nền mở đầu: các chấm 5 màu nguồn nối với nhau khi gần — hình ảnh của việc trộn 5 nguồn. */
function Constellation() {
  const ref = useRef<HTMLCanvasElement>(null);
  const { tick } = useTheme();
  useEffect(() => {
    const cv = ref.current!;
    const ctx = cv.getContext('2d')!;
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const keys = ['cj', 'batf', 'carbo', 'lgsr', 'm5'];
    const css = getComputedStyle(document.documentElement);
    const col = Object.fromEntries(keys.map((k) => [k, css.getPropertyValue(`--${k}`).trim()]));
    let W = 0, H = 0, raf = 0;
    let pts: { x: number; y: number; r: number; k: string; vx: number; vy: number }[] = [];
    const dpr = devicePixelRatio || 1;
    const size = () => {
      const r = cv.getBoundingClientRect(); W = cv.width = r.width * dpr; H = cv.height = r.height * dpr;
      pts = Array.from({ length: 80 }, (_, i) => ({ x: Math.random() * W, y: Math.random() * H, r: (1 + Math.random() * 2.2) * dpr, k: keys[i % 5], vx: (Math.random() - 0.5) * 0.25, vy: (Math.random() - 0.5) * 0.25 }));
    };
    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      const lim = 120 * dpr;
      for (let i = 0; i < pts.length; i++) {
        const a = pts[i];
        for (let j = i + 1; j < pts.length; j++) {
          const b = pts[j]; const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < lim && a.k !== b.k) { ctx.strokeStyle = col[a.k]; ctx.globalAlpha = (1 - d / lim) * 0.35; ctx.lineWidth = 0.6 * dpr; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }
        }
        ctx.globalAlpha = 0.9; ctx.fillStyle = col[a.k]; ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, 7); ctx.fill();
        if (!reduce) { a.x += a.vx; a.y += a.vy; if (a.x < 0 || a.x > W) a.vx *= -1; if (a.y < 0 || a.y > H) a.vy *= -1; }
      }
      if (!reduce) raf = requestAnimationFrame(draw);
    };
    size(); draw();
    const onR = () => { size(); if (reduce) draw(); };
    addEventListener('resize', onR);
    return () => { cancelAnimationFrame(raf); removeEventListener('resize', onR); };
  }, [tick]);
  return <canvas ref={ref} aria-hidden className="pointer-events-none absolute inset-0 h-full w-full opacity-60" />;
}


const ROLES = [
  { role: 'Ban điều hành', q: 'Chuỗi tăng trưởng ở đâu, nhờ lượng hay giá?', to: '/dieu-hanh', screen: 'Bảng điều hành' },
  { role: 'Quản lý vùng, cửa hàng', q: 'Cửa hàng, nhóm hàng nào đang giảm, ngày nào bất thường?', to: '/dieu-hanh', screen: 'Bảng điều hành · Cần chú ý' },
  { role: 'Ngành hàng', q: 'Ngành nào tăng giá được, giảm giá bao nhiêu thì còn lãi?', to: '/phan-tich/gia-khuyen-mai', screen: 'Giá & khuyến mãi · Mô phỏng' },
  { role: 'Marketing', q: 'Trưng bày, tờ rơi hay coupon: cái nào tạo thêm doanh thu thật?', to: '/phan-tich/gia-khuyen-mai', screen: 'Giá & khuyến mãi' },
  { role: 'CRM', q: 'Nhóm khách nào mang lại doanh thu và nhóm nào đang giảm mua?', to: '/phan-tich/khach-hang', screen: 'Khách hàng' },
  { role: 'Cung ứng', q: 'Cần đặt bao nhiêu hàng cho 4 tuần tới, ở từng cửa hàng?', to: '/phan-tich/du-bao', screen: 'Dự báo nhu cầu' },
];

const STEPS = [
  { icon: Cable, title: 'Kết nối dữ liệu', body: 'Hóa đơn POS, danh mục hàng, giá và khuyến mãi, tồn kho, thẻ thành viên. Kiểm tra chất lượng và đối soát trước khi tính.' },
  { icon: BrainCircuit, title: 'Phân tích và mô hình', body: 'Độ nhạy giá theo ngành, hiệu quả khuyến mãi, phân khúc khách, dự báo nhu cầu. Mỗi con số có khoảng tin cậy và giới hạn đi kèm.' },
  { icon: LayoutDashboard, title: 'Ra quyết định', body: 'Bảng điều hành hằng ngày, cảnh báo, mô phỏng trước khi đổi giá hay chạy khuyến mãi, thử nghiệm có nhóm đối chứng.' },
];

export default function Home() {
  const { data: meta } = useApi<Meta>('/api/meta');
  const { data: synth } = useApi<Section>('/api/sections/tong-hop');
  return (
    <div className="grid gap-14">
      <section className="relative -mx-4 -mt-8 overflow-hidden bg-brand px-4 pb-10 pt-12 text-brand-ink sm:-mx-6 sm:px-8 lg:mx-0 lg:mt-0 lg:rounded-card lg:px-10 lg:pt-14">
        <Constellation />
        <div className="relative grid gap-6">
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-brand-ink/25 px-3 py-1 font-mono text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-accent">Bản demo · Phân tích kinh doanh siêu thị</div>
          <h1 className="max-w-[18ch] font-display text-[clamp(2.1rem,5.2vw,4rem)] font-extrabold leading-[1.02]">Bán gì, giá nào, cho ai: trả lời bằng <span className="text-accent">dữ liệu bán hàng</span> của chính siêu thị</h1>
          <p className="max-w-[60ch] text-[1.06rem] text-brand-ink/80">Bản demo chạy trên 5 bộ dữ liệu bán lẻ thật, hơn 100 triệu dòng giao dịch. Khi kết nối POS, kho và thẻ thành viên của siêu thị, các màn hình dưới đây chạy trên số liệu của chính bạn.</p>
          <div className="flex flex-wrap gap-3">
            <Link to="/dieu-hanh" className="inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-3 font-semibold text-brand hover:opacity-90"><Gauge size={18} />Mở bảng điều hành</Link>
            <Link to="/mo-phong" className="inline-flex items-center gap-2 rounded-lg border border-brand-ink/30 px-5 py-3 font-medium hover:bg-brand-ink/10"><SlidersHorizontal size={18} />Thử mô phỏng khuyến mãi</Link>
          </div>
          {meta ? (
            <div className="mt-2 grid grid-cols-2 gap-px overflow-hidden rounded-card bg-brand-ink/15 md:grid-cols-4">
              {[[`${fmtNum(meta.kpis.total_rows / 1e6)} triệu`, 'dòng dữ liệu đã xử lý'], ['5', 'bộ dữ liệu bán lẻ'], [meta.kpis.period, 'giai đoạn'],
                [fmtNum(meta.kpis.stores), 'cửa hàng trong dữ liệu']].map(([v, l]) => (
                <div key={l} className="bg-brand px-4 py-4"><b className="block font-display text-[clamp(1.3rem,2.4vw,1.8rem)] leading-tight tabular">{v}</b><span className="text-[0.82rem] text-brand-ink/70">{l}</span></div>
              ))}
            </div>
          ) : <Skeleton h={90} />}
        </div>
      </section>

      <section className="grid gap-5">
        <div className="grid gap-1"><Eyebrow>Năng lực phân tích</Eyebrow><h2 className="font-display text-[1.7rem] font-bold">Bản demo trả lời được gì</h2></div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <Capability to="/dieu-hanh" icon={Gauge} title="Bảng điều hành" value="10 cửa hàng" label="doanh thu theo kỳ, so cùng kỳ, xếp hạng cửa hàng, cảnh báo, bản tin tự động" />
          {MODULES.map((m) => <Capability key={m.id} to={m.path} icon={m.icon} title={m.nav} value={m.headline?.value ?? ''} label={m.headline?.label ?? m.lead} />)}
          <Capability to="/mo-phong" icon={SlidersHorizontal} title="Mô phỏng giá & khuyến mãi" value="What-if" label="chọn ngành, biên lãi, mức giảm, trưng bày: xem lượng bán, doanh thu, lợi nhuận trước khi làm" />
        </div>
      </section>

      <section className="grid gap-5">
        <div className="grid gap-1"><Eyebrow>Theo vai trò</Eyebrow><h2 className="font-display text-[1.7rem] font-bold">Mỗi bộ phận mở đúng màn hình của mình</h2></div>
        <div className="overflow-x-auto rounded-card border border-line bg-surface">
          <table className="w-full text-[0.92rem]">
            <thead><tr className="bg-soft text-left font-mono text-[0.68rem] uppercase tracking-wider text-muted"><th className="px-5 py-2.5">Người dùng</th><th className="px-4 py-2.5">Câu hỏi hằng ngày</th><th className="px-5 py-2.5">Màn hình</th></tr></thead>
            <tbody>{ROLES.map((r) => (
              <tr key={r.role} className="border-t border-line">
                <td className="whitespace-nowrap px-5 py-3 font-semibold">{r.role}</td><td className="min-w-[240px] px-4 py-3">{r.q}</td>
                <td className="whitespace-nowrap px-5 py-3"><Link to={r.to} className="inline-flex items-center gap-1 text-accent hover:underline">{r.screen}<ArrowRight size={14} /></Link></td>
              </tr>))}</tbody>
          </table>
        </div>
      </section>

      <section className="grid gap-5">
        <div className="grid gap-1"><Eyebrow>Kết quả từ dữ liệu demo</Eyebrow><h2 className="font-display text-[1.7rem] font-bold">Những phát hiện lặp lại ở nhiều bộ dữ liệu</h2>
          <p className="max-w-[65ch] text-muted">Một kết luận chỉ đáng tin khi nhiều nguồn độc lập cùng cho kết quả. Mỗi thẻ ghi rõ bộ dữ liệu nào xác nhận.</p></div>
        {synth ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {synth.cards.slice(0, 6).map((c) => (
              <article key={c.title} className="grid content-start gap-2 rounded-card border border-line bg-surface p-5">
                <div className="flex flex-wrap gap-1.5">{c.sources.map((x) => <SourceChip key={x} src={x} />)}</div>
                <h3 className="font-display text-[1.04rem] font-bold">{c.title}</h3><p className="text-[0.9rem] text-muted">{c.body}</p>
              </article>))}
          </div>
        ) : <Skeleton h={240} />}
        <Link to="/trien-khai" className="inline-flex w-fit items-center gap-1 text-[0.92rem] font-medium text-accent hover:underline">Xem đủ 9 kết luận và việc nên làm <ArrowRight size={15} /></Link>
      </section>

      <section className="grid gap-5">
        <div className="grid gap-1"><Eyebrow>Cách triển khai</Eyebrow><h2 className="font-display text-[1.7rem] font-bold">Từ dữ liệu của siêu thị đến quyết định</h2></div>
        <ol className="grid gap-4 md:grid-cols-3">
          {STEPS.map((s, i) => (
            <li key={s.title} className="grid content-start gap-2 rounded-card border border-line bg-surface p-5">
              <div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-accent/15 text-accent"><s.icon size={20} /></span><span className="font-mono text-[0.8rem] text-muted">Bước {i + 1}</span></div>
              <h3 className="font-display text-[1.1rem] font-bold">{s.title}</h3><p className="text-[0.9rem] text-muted">{s.body}</p>
            </li>))}
        </ol>
      </section>

      <section className="grid gap-4 rounded-card bg-brand px-6 py-8 text-brand-ink sm:px-10 md:grid-cols-[1fr_auto] md:items-center">
        <div><h2 className="font-display text-[1.6rem] font-bold">Muốn xem trên dữ liệu của siêu thị bạn?</h2>
          <p className="mt-1 max-w-[60ch] text-brand-ink/80">Xem dữ liệu cần chuẩn bị, lộ trình thí điểm 5–10 cửa hàng và những việc nên làm trước.</p></div>
        <div className="flex flex-wrap gap-3">
          <Link to="/trien-khai" className="inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-3 font-semibold text-brand hover:opacity-90">Lộ trình triển khai <ArrowRight size={17} /></Link>
          <Link to="/tra-cuu" className="inline-flex items-center gap-2 rounded-lg border border-brand-ink/30 px-5 py-3 font-medium hover:bg-brand-ink/10"><TableProperties size={17} />Tự tra cứu dữ liệu</Link>
        </div>
      </section>
    </div>
  );
}

function Eyebrow({ children }: { children: ReactNode }) {
  return <div className="font-mono text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-accent">{children}</div>;
}

function Capability({ to, icon: Icon, title, value, label }: { to: string; icon: typeof Gauge; title: string; value: string; label: string }) {
  return (
    <Link to={to} className="group grid content-start gap-3 rounded-card border border-line bg-surface p-5 transition hover:-translate-y-0.5 hover:border-accent">
      <div className="flex items-center justify-between"><span className="grid h-10 w-10 place-items-center rounded-xl bg-brand text-accent"><Icon size={19} /></span>
        <ArrowRight size={17} className="text-muted transition group-hover:translate-x-0.5 group-hover:text-accent" /></div>
      <h3 className="font-display text-[1.15rem] font-bold">{title}</h3>
      <div className="flex items-baseline gap-2"><b className="font-display text-[1.5rem] leading-none text-accent tabular">{value}</b></div>
      <p className="text-[0.88rem] text-muted">{label}</p>
    </Link>
  );
}
