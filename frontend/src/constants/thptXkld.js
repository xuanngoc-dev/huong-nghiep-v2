// Giá trị enum của danh mục xuất khẩu lao động THPT. Khớp backend/app/models/dm_thpt_xkld.py.
export { mauEnum, nhanEnum } from '@/constants/thptDuHoc'

export const YEU_CAU_GIOI_TINH = [
  { value: 'ca_hai', label: 'Cả nam và nữ', mau: 'info' },
  { value: 'nam', label: 'Nam', mau: 'primary' },
  { value: 'nu', label: 'Nữ', mau: 'danger' },
]

export const LOAI_CHI_PHI = [
  { value: 'phi_dich_vu_xuat_canh', label: 'Phí dịch vụ xuất cảnh', mau: 'primary' },
  { value: 'dao_tao_tieng_tay_nghe', label: 'Đào tạo tiếng, tay nghề', mau: 'success' },
  { value: 'kham_suc_khoe_ho_so', label: 'Khám sức khỏe, hồ sơ', mau: 'warning' },
  { value: 'ky_quy_chong_tron', label: 'Ký quỹ chống trốn', mau: 'danger' },
]

export const LOAI_KENH = [
  { value: 'co_quan_nha_nuoc', label: 'Cơ quan nhà nước', mau: 'success' },
  { value: 'doanh_nghiep_cap_phep', label: 'Doanh nghiệp được cấp phép', mau: 'primary' },
  { value: 'trung_tam_lao_dong_ngoai_nuoc', label: 'Trung tâm Lao động ngoài nước', mau: 'warning' },
  { value: 'ho_tro_he_thong', label: 'Hỗ trợ hệ thống', mau: 'info' },
]

// Gợi ý đơn vị tiền (ô chọn vẫn cho nhập mã khác).
export const DON_VI_TIEN_XKLD = ['VND', 'USD', 'JPY', 'KRW', 'TWD', 'EUR', 'AUD', 'SGD', 'CNY']
