/** Màu lấy từ biến CSS để đổi sáng/tối không cần class dark: */
const v = (n) => `rgb(var(--${n}) / <alpha-value>)`;
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: v('bg-rgb'), surface: v('surface-rgb'), ink: v('ink-rgb'), muted: v('muted-rgb'), line: v('line-rgb'), soft: v('soft-rgb'),
        brand: v('brand-rgb'), 'brand-ink': v('brand-ink-rgb'), accent: v('accent-rgb'), data: v('data-rgb'), econ: v('econ-rgb'),
        cj: v('cj-rgb'), batf: v('batf-rgb'), carbo: v('carbo-rgb'), lgsr: v('lgsr-rgb'), m5: v('m5-rgb'),
      },
      fontFamily: {
        display: ['"Bricolage Grotesque"', '"Be Vietnam Pro"', 'system-ui', 'sans-serif'],
        sans: ['"Be Vietnam Pro"', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'Consolas', 'monospace'],
      },
      borderRadius: { card: '14px' },
    },
  },
  safelist: ['bg-cj', 'bg-batf', 'bg-carbo', 'bg-lgsr', 'bg-m5'],
  plugins: [],
};
