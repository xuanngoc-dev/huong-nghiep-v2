// Dữ liệu giả cho trang tổng quan quản trị — thay bằng API khi backend sẵn sàng.

export const THANG = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12']

export const theThongKe = [
  {
    key: 'tai-khoan',
    title: 'Tài khoản người dùng',
    value: 12846,
    icon: 'User',
    color: '#1f7a4d',
    trend: 8.4,
    xuHuong: [620, 710, 680, 820, 900, 870, 1020, 1100, 1060, 1180, 1250, 1320],
  },
  {
    key: 'luot-trac-nghiem',
    title: 'Lượt trắc nghiệm',
    value: 38420,
    icon: 'EditPen',
    color: '#2f6fdb',
    trend: 12.1,
    xuHuong: [1800, 2100, 2400, 2300, 2900, 3100, 2800, 3300, 3600, 3500, 3900, 4200],
  },
  {
    key: 'hoan-thanh',
    title: 'Tỷ lệ hoàn thành bài',
    value: '82,6',
    donVi: '%',
    icon: 'CircleCheck',
    color: '#e0a526',
    trend: -1.8,
    xuHuong: [84, 85, 83, 84, 86, 85, 84, 83, 84, 83, 82, 82.6],
  },
  {
    key: 'nganh',
    title: 'Ngành đào tạo',
    value: 486,
    icon: 'School',
    color: '#7b61c9',
    trend: 3.2,
    trendLabel: 'so với năm trước',
    xuHuong: [440, 444, 450, 452, 458, 462, 466, 470, 474, 478, 482, 486],
  },
]

export const luotTheoThang = [
  { name: 'Lượt trắc nghiệm', data: [1800, 2100, 2400, 2300, 2900, 3100, 2800, 3300, 3600, 3500, 3900, 4200] },
  { name: 'Tài khoản mới', data: [620, 710, 680, 820, 900, 870, 1020, 1100, 1060, 1180, 1250, 1320] },
]

export const nhomHolland = {
  labels: ['Kỹ thuật (R)', 'Nghiên cứu (I)', 'Nghệ thuật (A)', 'Xã hội (S)', 'Quản lý (E)', 'Nghiệp vụ (C)'],
  values: [6120, 7480, 5230, 8910, 6340, 4340],
  colors: ['#d9534f', '#2f6fdb', '#e0a526', '#1f7a4d', '#7b61c9', '#1a9fb0'],
}

export const topNganh = {
  categories: [
    'Công nghệ thông tin',
    'Quản trị kinh doanh',
    'Sư phạm Tiểu học',
    'Điều dưỡng',
    'Kế toán',
    'Thiết kế đồ họa',
    'Ngôn ngữ Anh',
    'Kỹ thuật cơ khí',
  ],
  series: [{ name: 'Lượt gợi ý', data: [4820, 3960, 3410, 3180, 2950, 2610, 2440, 2120] }],
}

export const theoDoiTuong = {
  categories: ['THCS', 'THPT', 'Sinh viên', 'Thanh niên', 'Phụ huynh'],
  series: [
    { name: 'Hoàn thành', data: [5200, 14800, 6100, 2900, 1350] },
    { name: 'Bỏ dở', data: [1300, 2600, 1500, 900, 470] },
  ],
}

export const topTinhThanh = [
  { ten: 'Hà Nội', khuVuc: 'Bắc', luot: 6840, tyLe: 86 },
  { ten: 'TP. Hồ Chí Minh', khuVuc: 'Nam', luot: 6120, tyLe: 84 },
  { ten: 'Nghệ An', khuVuc: 'Trung', luot: 2950, tyLe: 81 },
  { ten: 'Thanh Hóa', khuVuc: 'Trung', luot: 2710, tyLe: 79 },
  { ten: 'Hải Phòng', khuVuc: 'Bắc', luot: 2280, tyLe: 83 },
  { ten: 'Đà Nẵng', khuVuc: 'Trung', luot: 1960, tyLe: 88 },
]

export const luotGanDay = [
  { id: 1, hoTen: 'Nguyễn Minh Anh', doiTuong: 'THPT', maHolland: 'SIA', nganh: 'Sư phạm Tiểu học', thoiGian: '11/11/2026 09:42', trangThai: 'hoan-thanh' },
  { id: 2, hoTen: 'Trần Đức Huy', doiTuong: 'THPT', maHolland: 'IRC', nganh: 'Công nghệ thông tin', thoiGian: '11/11/2026 09:15', trangThai: 'hoan-thanh' },
  { id: 3, hoTen: 'Lê Thu Trang', doiTuong: 'Sinh viên', maHolland: 'AES', nganh: 'Thiết kế đồ họa', thoiGian: '11/11/2026 08:57', trangThai: 'dang-lam' },
  { id: 4, hoTen: 'Phạm Quốc Bảo', doiTuong: 'THCS', maHolland: 'RIE', nganh: 'Kỹ thuật cơ khí', thoiGian: '11/11/2026 08:31', trangThai: 'hoan-thanh' },
  { id: 5, hoTen: 'Võ Ngọc Hân', doiTuong: 'Thanh niên', maHolland: 'ECS', nganh: 'Quản trị kinh doanh', thoiGian: '10/11/2026 21:08', trangThai: 'bo-do' },
  { id: 6, hoTen: 'Đỗ Gia Khánh', doiTuong: 'THPT', maHolland: 'CEI', nganh: 'Kế toán', thoiGian: '10/11/2026 20:44', trangThai: 'hoan-thanh' },
]

export const hoatDong = [
  { id: 1, noiDung: 'Thêm 24 câu hỏi vào bộ trắc nghiệm Holland', nguoi: 'admin', thoiGian: '10 phút trước', type: 'primary' },
  { id: 2, noiDung: 'Cập nhật đề án tuyển sinh 2027 — ĐH Bách khoa', nguoi: 'ngocpx', thoiGian: '1 giờ trước', type: 'success' },
  { id: 3, noiDung: 'Import 112 ngành đào tạo từ file JSON', nguoi: 'admin', thoiGian: '3 giờ trước', type: 'info' },
  { id: 4, noiDung: 'Khóa 3 tài khoản vi phạm điều khoản', nguoi: 'admin', thoiGian: 'Hôm qua', type: 'warning' },
  { id: 5, noiDung: 'Sao lưu cơ sở dữ liệu định kỳ', nguoi: 'hệ thống', thoiGian: 'Hôm qua', type: 'info' },
]
