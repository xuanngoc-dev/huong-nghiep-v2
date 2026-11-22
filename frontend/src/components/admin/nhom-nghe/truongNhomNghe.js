// Nhãn các trường của nhóm nghề đi làm, dùng chung cho form, bảng và modal chi tiết (khu quản trị).

export const LOAI_HINH_DAU_VAO = [
  { value: 'di_lam_ngay', label: 'Đi làm ngay' },
  { value: 'hoc_nghe_ngan_han', label: 'Học nghề ngắn hạn' },
  { value: 'tu_hoc_ky_nang', label: 'Tự học kỹ năng' },
]

export const NHOM_MUC_TIEU = [
  { value: 'kiem_tien_ngay', label: 'Kiếm tiền ngay', mau: 'warning' },
  { value: 'nghe_vung_chac', label: 'Nghề vững chắc', mau: 'success' },
  { value: 'thu_nhap_dot_pha', label: 'Thu nhập đột phá', mau: 'danger' },
]

// Mục giới thiệu nhóm nghề (văn bản dài, tùy chọn).
export const MUC_GIOI_THIEU = [
  { key: 'nganh_nay_la_gi', label: 'Ngành này là gì?', placeholder: 'Giới thiệu ngắn gọn nhóm nghề' },
  { key: 'noi_lam_viec_o_dau', label: 'Nơi làm việc ở đâu?', placeholder: 'Nhà máy, cửa hàng, công trường…' },
  {
    key: 'cong_viec_hang_ngay_nhu_the_nao',
    label: 'Công việc hằng ngày như thế nào?',
    placeholder: 'Một ngày làm việc điển hình',
  },
  { key: 'ap_luc_va_rui_ro', label: 'Áp lực và rủi ro', placeholder: 'Khó khăn, rủi ro cần biết trước' },
  { key: 'xu_huong_tuong_lai', label: 'Xu hướng tương lai', placeholder: 'Nhu cầu, thay đổi của nghề trong vài năm tới' },
  { key: 'ket_luan', label: 'Kết luận', placeholder: 'Nghề này phù hợp với ai, nên chuẩn bị gì' },
]
