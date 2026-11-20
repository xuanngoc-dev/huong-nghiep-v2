// Nhãn và định dạng dùng chung cho các màn hướng "Đi làm ngay sau khi tốt nghiệp".

export const LOAI_HINH_DAU_VAO = [
  {
    value: 'di_lam_ngay',
    label: 'Đi làm ngay',
    moTa: 'Doanh nghiệp đào tạo tại chỗ vài ngày đến vài tuần, có lương ngay.',
  },
  {
    value: 'hoc_nghe_ngan_han',
    label: 'Học nghề ngắn hạn',
    moTa: 'Học 3-12 tháng tại trường nghề, trung tâm để có tay nghề và chứng chỉ.',
  },
  {
    value: 'tu_hoc_ky_nang',
    label: 'Tự học kỹ năng',
    moTa: 'Tự học qua khóa học online, dự án thực tế; phù hợp người chủ động, thích công nghệ.',
  },
]

export const NHOM_MUC_TIEU = [
  { value: 'kiem_tien_ngay', label: 'Kiếm tiền ngay' },
  { value: 'nghe_vung_chac', label: 'Nghề vững chắc' },
  { value: 'thu_nhap_dot_pha', label: 'Thu nhập đột phá' },
]

export function nhan(ds, value) {
  return ds.find((item) => item.value === value)?.label || value
}

// Decimal từ API là chuỗi ("7.00"); bỏ phần thập phân thừa khi hiển thị.
export function soTrieu(value) {
  return Number(value).toLocaleString('vi-VN')
}

export function khoangLuong(nhom) {
  const tu = nhom.luong_khoi_diem_min
  const den = nhom.luong_khoi_diem_max
  if (tu == null && den == null) return 'Đang cập nhật'
  if (tu != null && den != null) return `${soTrieu(tu)} - ${soTrieu(den)} triệu/tháng`
  return `${soTrieu(tu ?? den)} triệu/tháng`
}

export function thoiGianDaoTao(nhom) {
  const tu = nhom.thoi_gian_dao_tao_thang_min
  const den = nhom.thoi_gian_dao_tao_thang_max
  if (tu == null && den == null) return 'Đang cập nhật'
  if (!den) return 'Không cần đào tạo dài'
  return tu != null && tu !== den ? `${tu} - ${den} tháng` : `${den} tháng`
}
