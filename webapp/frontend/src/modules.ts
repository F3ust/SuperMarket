import {
  BarChart3, Database, Gauge, Rocket, ShoppingBasket, SlidersHorizontal, Tag, TableProperties, TrendingUp, Users,
} from 'lucide-react';

export type Module = {
  id: string; path: string; nav: string; icon: typeof Gauge; title: string; lead: string;
  questions: string[]; roles: string[]; sections: string[]; headline?: { value: string; label: string };
};

/** Các phân hệ phân tích. Mỗi phân hệ gom các phần phân tích đã kiểm chứng theo nghiệp vụ của siêu thị. */
export const MODULES: Module[] = [
  {
    id: 'khach-hang', path: '/phan-tich/khach-hang', nav: 'Khách hàng', icon: Users,
    title: 'Ai mang lại doanh thu, và họ đang thay đổi thế nào',
    lead: 'Phân hệ theo dõi từng hộ khách qua thẻ thành viên: mức tập trung doanh thu, động lực tăng trưởng, phân khúc RFM, thu nhập và mức trung thành với thương hiệu.',
    questions: ['Bao nhiêu phần trăm khách tạo ra phần lớn doanh thu?', 'Doanh thu tăng nhờ thêm khách, khách ghé nhiều hơn hay giỏ lớn hơn?', 'Nhóm khách nào đang giảm mua và cần chăm sóc?', 'Khách thu nhập nào chuộng nhãn riêng?'],
    roles: ['CRM', 'Marketing', 'Ban điều hành'], sections: ['tap-trung', 'khach-hang', 'thu-nhap'],
    headline: { value: '20% → 53–66%', label: '20% khách hoặc mặt hàng tạo ra 53–66% doanh thu' },
  },
  {
    id: 'gia-khuyen-mai', path: '/phan-tich/gia-khuyen-mai', nav: 'Giá & khuyến mãi', icon: Tag,
    title: 'Định giá và khuyến mãi sao cho vẫn có lãi',
    lead: 'Ước lượng độ nhạy giá theo ngành hàng và phân khúc cửa hàng, tách hiệu ứng của trưng bày, tờ rơi, giảm giá, coupon, và tính lãi thực của một đợt khuyến mãi.',
    questions: ['Ngành nào tăng giá được mà ít mất khách?', 'Giảm giá bao nhiêu thì còn lãi?', 'Trưng bày, tờ rơi hay giảm giá hiệu quả hơn?', 'Coupon thật sự tạo thêm chi tiêu, hay chỉ trúng khách vốn đã mua?'],
    roles: ['Ngành hàng', 'Marketing'], sections: ['gia', 'khuyen-mai'],
    headline: { value: '×2,8', label: 'hộ nhận coupon vốn đã chi gấp 2,8 lần ngay trước chiến dịch: so sánh thô sẽ đo nhầm hiệu quả' },
  },
  {
    id: 'gio-hang', path: '/phan-tich/gio-hang', nav: 'Giỏ hàng & thời điểm', icon: ShoppingBasket,
    title: 'Khách mua gì cùng nhau, vào lúc nào',
    lead: 'Phân loại chuyến mua, nhịp theo giờ và thứ, sản phẩm hay được mua cùng nhau, và tác động của ngày nhận trợ cấp, ngày lễ lên doanh số.',
    questions: ['Khách đi chợ theo kiểu nào, kiểu nào mang lại doanh thu?', 'Giờ nào, ngày nào đông khách nhất?', 'Sản phẩm nào nên đặt cạnh nhau?', 'Ngày nhận lương, trợ cấp và ngày lễ ảnh hưởng thế nào?'],
    roles: ['Vận hành cửa hàng', 'Marketing', 'Ngành hàng'], sections: ['hanh-vi', 'chinh-sach'],
    headline: { value: 'tới +30%', label: 'lượng thực phẩm bán ra vào ngày hộ nhận trợ cấp thực phẩm' },
  },
  {
    id: 'du-bao', path: '/phan-tich/du-bao', nav: 'Dự báo nhu cầu', icon: TrendingUp,
    title: 'Dự báo lượng bán 28 ngày tới cho từng mặt hàng tại từng cửa hàng',
    lead: 'So sánh mô hình học máy với các cách lập kế hoạch đơn giản trên 30.490 chuỗi mặt hàng × cửa hàng, chấm điểm theo cách của cuộc thi M5.',
    questions: ['Cần đặt bao nhiêu hàng cho 4 tuần tới?', 'Mô hình học máy tốt hơn cách làm hiện tại bao nhiêu?', 'Mặt hàng nào khó dự báo, cần cách khác?'],
    roles: ['Cung ứng', 'Ngành hàng'], sections: ['du-bao'],
    headline: { value: '−22%', label: 'sai số dự báo so với lặp lại số tuần trước' },
  },
];

export const DEPLOY: Module = {
  id: 'trien-khai', path: '/trien-khai', nav: 'Kết quả & triển khai', icon: Rocket,
  title: 'Áp dụng cho siêu thị của bạn',
  lead: 'Những kết luận lặp lại ở nhiều bộ dữ liệu độc lập, các việc nên làm trước, dữ liệu cần có và lộ trình thí điểm.',
  questions: [], roles: ['Ban điều hành'], sections: ['tong-hop', 'hanh-dong'],
};

export const DATA: Module = {
  id: 'du-lieu', path: '/du-lieu', nav: 'Dữ liệu demo', icon: Database,
  title: 'Bản demo chạy trên dữ liệu nào',
  lead: 'Năm bộ dữ liệu bán lẻ công khai của Mỹ và Anh, giai đoạn 2006–2016. Mỗi bộ có điểm mạnh và điểm mù riêng; phần này ghi rõ để người xem biết con số nào đáng tin đến đâu.',
  questions: [], roles: [], sections: ['nguon', 'du-lieu'],
};

export const TOOLS = [
  { path: '/dieu-hanh', nav: 'Bảng điều hành', icon: Gauge },
  { path: '/mo-phong', nav: 'Mô phỏng giá & KM', icon: SlidersHorizontal },
  { path: '/tra-cuu', nav: 'Tra cứu dữ liệu', icon: TableProperties },
];

/** Đường dẫn mới cho link /chuong/:id cũ. */
export function pathForSection(id: string): string {
  for (const m of [...MODULES, DEPLOY, DATA]) if (m.sections.includes(id)) return `${m.path}#${id}`;
  return '/';
}

export const ICON_CHART = BarChart3;
