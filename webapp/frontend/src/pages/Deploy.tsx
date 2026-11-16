import { DEPLOY } from '../modules';
import ModulePage from './ModulePage';

const DATA_NEEDED = [
  { table: 'Hóa đơn POS', key: 'cửa hàng + ngày + số hóa đơn + dòng', why: 'Doanh thu, số giỏ, giá trị giỏ, giỏ hàng. Giữ cả hoàn/hủy và hóa đơn gốc.', need: 'Bắt buộc' },
  { table: 'Danh mục mặt hàng', key: 'mã hàng + thời gian hiệu lực', why: 'Ngành, nhóm, quy cách, nhãn riêng; ánh xạ mã giữa POS, ERP và kho.', need: 'Bắt buộc' },
  { table: 'Cửa hàng', key: 'mã cửa hàng + thời gian hiệu lực', why: 'Vùng, mô hình, diện tích, ngày mở/đóng: so sánh cửa hàng tương đồng, tăng trưởng cùng cửa hàng.', need: 'Bắt buộc' },
  { table: 'Giá và khuyến mãi', key: 'cửa hàng + mã hàng + khoảng hiệu lực', why: 'Giá kệ, giá cơ sở, giảm giá, tờ rơi, trưng bày: đo độ nhạy giá và hiệu quả khuyến mãi.', need: 'Bắt buộc' },
  { table: 'Thẻ thành viên', key: 'mã khách ẩn danh toàn chuỗi', why: 'Phân khúc khách, khách giảm mua, chiến dịch CRM có nhóm đối chứng.', need: 'Nên có' },
  { table: 'Tồn kho', key: 'địa điểm + mã hàng + ngày', why: 'Phân biệt hết hàng với không có nhu cầu; dự báo và đặt hàng.', need: 'Nên có' },
  { table: 'Giá vốn', key: 'mã hàng + thời gian hiệu lực', why: 'Lãi gộp thực, mô phỏng lợi nhuận khuyến mãi không cần nhập tay biên lãi.', need: 'Nên có' },
];

const ROADMAP = [
  { w: 'Tuần 1–2', t: 'Kết nối và kiểm tra dữ liệu', b: 'Nhận dữ liệu 2 năm của 5–10 cửa hàng thí điểm. Đối soát doanh thu với sổ sách, lập báo cáo chất lượng dữ liệu.' },
  { w: 'Tuần 3–4', t: 'Bảng điều hành chạy trên số liệu thật', b: 'KPI theo kỳ, xếp hạng cửa hàng, cảnh báo, bản tin. Thống nhất định nghĩa doanh thu, cùng cửa hàng, ngày lễ.' },
  { w: 'Tuần 5–8', t: 'Phân tích giá, khuyến mãi, khách hàng', b: 'Độ nhạy giá cho 20 ngành lớn nhất, hiệu quả các đợt khuyến mãi đã chạy, phân khúc khách thành viên.' },
  { w: 'Tuần 9–12', t: 'Thử nghiệm có đối chứng và dự báo', b: 'Một thử nghiệm trưng bày hoặc giá theo cặp cửa hàng, một chiến dịch CRM có nhóm giữ lại. Dự báo 28 ngày cho một ngành hàng, so với cách đặt hàng hiện tại.' },
];

export default function Deploy() {
  return (
    <ModulePage m={DEPLOY}>
      <section className="grid gap-5 border-t border-line pt-8">
        <h2 className="font-display text-[clamp(1.35rem,2.6vw,1.9rem)] font-bold">Dữ liệu siêu thị cần chuẩn bị</h2>
        <div className="overflow-x-auto rounded-card border border-line bg-surface">
          <table className="w-full text-[0.9rem]">
            <thead><tr className="bg-soft text-left font-mono text-[0.68rem] uppercase tracking-wider text-muted"><th className="px-5 py-2.5">Bảng</th><th className="px-4 py-2.5">Khóa</th><th className="px-4 py-2.5">Dùng để</th><th className="px-5 py-2.5">Mức</th></tr></thead>
            <tbody>{DATA_NEEDED.map((d) => (
              <tr key={d.table} className="border-t border-line align-top">
                <td className="whitespace-nowrap px-5 py-3 font-semibold">{d.table}</td><td className="min-w-[180px] px-4 py-3 font-mono text-[0.8rem] text-muted">{d.key}</td>
                <td className="min-w-[260px] px-4 py-3">{d.why}</td>
                <td className="whitespace-nowrap px-5 py-3"><span className={`rounded-full px-2.5 py-0.5 text-[0.78rem] font-medium ${d.need === 'Bắt buộc' ? 'bg-accent/15 text-accent' : 'bg-soft text-muted'}`}>{d.need}</span></td>
              </tr>))}</tbody>
          </table>
        </div>
      </section>
      <section className="grid gap-5 border-t border-line pt-8">
        <h2 className="font-display text-[clamp(1.35rem,2.6vw,1.9rem)] font-bold">Lộ trình thí điểm 12 tuần</h2>
        <ol className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {ROADMAP.map((r) => (
            <li key={r.w} className="grid content-start gap-2 rounded-card border border-line bg-surface p-5">
              <span className="font-mono text-[0.75rem] font-semibold uppercase tracking-wider text-accent">{r.w}</span>
              <h3 className="font-display text-[1.06rem] font-bold">{r.t}</h3><p className="text-[0.9rem] text-muted">{r.b}</p>
            </li>))}
        </ol>
        <p className="max-w-[75ch] text-[0.86rem] text-muted">Các kết quả trong bản demo đến từ thị trường Mỹ và Anh giai đoạn 2006–2016. Chúng dùng để chọn phương pháp và đặt giả thuyết; con số cho siêu thị của bạn cần được đo lại trên dữ liệu của chính chuỗi.</p>
      </section>
    </ModulePage>
  );
}
