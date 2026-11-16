import { useEffect, useState, type ReactNode } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Home, Menu, Monitor, Moon, Sun, X } from 'lucide-react';
import { DATA, DEPLOY, MODULES, TOOLS } from '../modules';
import { useTheme } from './ui';

const GROUPS = [
  { label: 'Điều hành', items: [TOOLS[0]] },
  { label: 'Phân tích', items: MODULES.map((m) => ({ path: m.path, nav: m.nav, icon: m.icon })) },
  { label: 'Công cụ', items: TOOLS.slice(1) },
  { label: 'Triển khai', items: [DEPLOY, DATA].map((m) => ({ path: m.path, nav: m.nav, icon: m.icon })) },
];

function Item({ to, icon: Icon, children, onClick }: { to: string; icon: typeof Home; children: ReactNode; onClick?: () => void }) {
  return (
    <NavLink to={to} end onClick={onClick}
      className={({ isActive }) => `flex items-center gap-2.5 rounded-lg px-3 py-2 text-[0.9rem] transition ${isActive ? 'bg-brand text-brand-ink' : 'text-muted hover:bg-soft hover:text-ink'}`}>
      <Icon size={17} strokeWidth={1.8} aria-hidden /> <span className="truncate">{children}</span>
    </NavLink>
  );
}

export default function Layout({ children }: { children: ReactNode }) {
  const { theme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const loc = useLocation();
  useEffect(() => { setOpen(false); if (!loc.hash) window.scrollTo({ top: 0 }); }, [loc.pathname, loc.hash]);
  const nextTheme = theme === 'system' ? 'light' : theme === 'light' ? 'dark' : 'system';
  const ThemeIcon = theme === 'light' ? Sun : theme === 'dark' ? Moon : Monitor;

  const nav = (
    <nav aria-label="Điều hướng chính" className="flex flex-col gap-5">
      <div className="flex flex-col gap-0.5"><Item to="/" icon={Home}>Trang chủ</Item></div>
      {GROUPS.map((g) => (
        <div key={g.label}>
          <div className="mb-1.5 px-3 font-mono text-[0.66rem] font-semibold uppercase tracking-[0.14em] text-muted">{g.label}</div>
          <div className="flex flex-col gap-0.5">{g.items.map((it) => <Item key={it.path} to={it.path} icon={it.icon}>{it.nav}</Item>)}</div>
        </div>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen bg-bg text-ink">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-line bg-surface lg:flex">
        <Brand />
        <div className="flex-1 overflow-y-auto px-3 pb-6">{nav}</div>
        <div className="border-t border-line px-5 py-3 text-[0.75rem] text-muted">Bản demo trên dữ liệu bán lẻ công khai.<br />Khi triển khai: dữ liệu POS của siêu thị.</div>
      </aside>
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Điều hướng">
          <button className="absolute inset-0 bg-black/40" aria-label="Đóng điều hướng" onClick={() => setOpen(false)} />
          <div className="absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col bg-surface">
            <div className="flex items-center justify-between pr-3"><Brand /><button onClick={() => setOpen(false)} aria-label="Đóng" className="rounded-lg p-2 hover:bg-soft"><X size={18} /></button></div>
            <div className="flex-1 overflow-y-auto px-3 pb-6">{nav}</div>
          </div>
        </div>
      )}
      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-line bg-surface/90 px-4 py-2.5 backdrop-blur sm:px-6">
          <button className="rounded-lg p-2 hover:bg-soft lg:hidden" onClick={() => setOpen(true)} aria-label="Mở điều hướng"><Menu size={18} /></button>
          <div className="min-w-0 flex-1 truncate text-[0.86rem] text-muted"><b className="font-semibold text-ink">Phân tích kinh doanh siêu thị</b></div>
          <span className="hidden rounded-md bg-soft px-2 py-1 font-mono text-[0.66rem] font-semibold tracking-wider text-muted sm:inline">BẢN DEMO</span>
          <button onClick={() => setTheme(nextTheme)} className="flex items-center gap-1.5 rounded-lg border border-line px-2.5 py-1.5 text-[0.8rem] hover:bg-soft"
            aria-label={`Giao diện: ${theme === 'system' ? 'theo hệ thống' : theme === 'light' ? 'sáng' : 'tối'}. Bấm để đổi`}>
            <ThemeIcon size={15} /> <span className="hidden sm:inline">{theme === 'system' ? 'Hệ thống' : theme === 'light' ? 'Sáng' : 'Tối'}</span>
          </button>
        </header>
        <main id="content" className="mx-auto max-w-[1180px] px-4 pb-20 pt-8 sm:px-6">{children}</main>
      </div>
    </div>
  );
}

function Brand() {
  return (
    <NavLink to="/" className="flex items-center gap-2.5 px-5 py-5">
      <span className="grid h-9 w-9 place-items-center rounded-[9px] bg-brand font-display text-lg font-extrabold text-accent">R</span>
      <span className="leading-tight"><b className="block font-display text-[1.05rem]">retail</b><span className="text-[0.78rem] tracking-wide text-muted">intelligence · demo</span></span>
    </NavLink>
  );
}
