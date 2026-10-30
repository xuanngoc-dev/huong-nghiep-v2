import { HINH_THUC_LABELS, TRINH_DO_LABELS } from './format'

export function col(prop, label, extra = {}) {
  return {
    prop,
    label,
    minWidth: 160,
    ...extra,
  }
}

/** Cột dùng lại ở nhiều mục. Gọi hàm để mỗi component giữ bản riêng, sửa một mục không đụng mục khác. */
export function cotChung() {
  return {
    chuongTrinh: col('chuong_trinh', 'Chương trình', { minWidth: 240 }),
    phuongThuc: col('phuong_thuc', 'Phương thức', { minWidth: 240 }),
    ghiChu: col('ghi_chu', 'Ghi chú', { minWidth: 220 }),
    trangThai: col('trang_thai', 'Trạng thái', { width: 140, minWidth: 140, align: 'center', type: 'status' }),
    nguon: col('nguon_du_lieu_url', 'Nguồn', { minWidth: 220, type: 'link' }),
    trinhDo: col('trinh_do_dao_tao', 'Trình độ', {
      width: 130,
      minWidth: 130,
      type: 'code',
      labels: TRINH_DO_LABELS,
    }),
    hinhThuc: col('hinh_thuc_dao_tao', 'Hình thức', {
      width: 160,
      minWidth: 150,
      type: 'code',
      labels: HINH_THUC_LABELS,
    }),
    nam: col('nam_tuyen_sinh', 'Năm', { width: 90, minWidth: 90, align: 'center' }),
  }
}
