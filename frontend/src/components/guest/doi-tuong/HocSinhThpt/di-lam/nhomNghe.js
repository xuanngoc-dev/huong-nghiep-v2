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

// Hướng "đi làm ngay" (học sinh không học tiếp) không hiện nghề bắt buộc đào tạo chính quy; nghề chỉ cần chứng chỉ,
// giấy phép (lái xe, an toàn điện…) vẫn hiện kèm yêu cầu bằng cấp.
/** Loại yêu cầu của một nghề: 'chinh_quy' | 'can_bang_cap' | 'di_lam_ngay'. */
export function loaiNghe(nghe) {
  if (Number(nghe?.bat_buoc_dao_tao_chinh_quy) === 1) return 'chinh_quy'
  if (String(nghe?.yeu_cau_bang_cap || '').trim()) return 'can_bang_cap'
  return 'di_lam_ngay'
}

/** Nghề làm được sau THPT mà không học tiếp: không bắt buộc đào tạo chính quy (có thể cần chứng chỉ, giấy phép). */
export function laNgheDiLamNgay(nghe) {
  return loaiNghe(nghe) !== 'chinh_quy'
}

// Bộ lọc nhóm nghề theo mức lương tham khảo (triệu đồng/tháng): ngưỡng tối thiểu của lương khởi điểm thấp nhất
// (luong_khoi_diem_min) hoặc của thu nhập khi có kinh nghiệm (luong_kinh_nghiem_max). Dùng ngưỡng "từ X trở lên" vì
// khoảng lương các nhóm chồng lên nhau nhiều, lọc theo khoảng giao nhau gần như nhóm nào cũng khớp.
export const MUC_LUONG_LOC = [
  { value: 'kd_6', nhom: 'Lương khởi điểm', label: 'Khởi điểm từ 6 triệu', truong: 'luong_khoi_diem_min', tu: 6 },
  { value: 'kd_7', nhom: 'Lương khởi điểm', label: 'Khởi điểm từ 7 triệu', truong: 'luong_khoi_diem_min', tu: 7 },
  { value: 'kd_8', nhom: 'Lương khởi điểm', label: 'Khởi điểm từ 8 triệu', truong: 'luong_khoi_diem_min', tu: 8 },
  { value: 'kn_20', nhom: 'Khi có kinh nghiệm', label: 'Có kinh nghiệm: tới 20 triệu+', truong: 'luong_kinh_nghiem_max', tu: 20 },
  { value: 'kn_30', nhom: 'Khi có kinh nghiệm', label: 'Có kinh nghiệm: tới 30 triệu+', truong: 'luong_kinh_nghiem_max', tu: 30 },
  { value: 'kn_40', nhom: 'Khi có kinh nghiệm', label: 'Có kinh nghiệm: tới 40 triệu+', truong: 'luong_kinh_nghiem_max', tu: 40 },
]

/** MUC_LUONG_LOC gom theo nhóm để hiển thị trong ô chọn: [{ nhom, ds }]. */
export const MUC_LUONG_THEO_NHOM = [...new Set(MUC_LUONG_LOC.map((item) => item.nhom))].map((nhom) => ({
  nhom,
  ds: MUC_LUONG_LOC.filter((item) => item.nhom === nhom),
}))

export function boDau(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .toLowerCase()
}

function khopMucLuong(nhom, mucLuong) {
  const muc = MUC_LUONG_LOC.find((item) => item.value === mucLuong)
  if (!muc) return true
  const giaTri = nhom[muc.truong]
  if (giaTri == null || giaTri === '') return false
  return Number(giaTri) >= muc.tu
}

/**
 * Lọc nghề không bắt buộc đào tạo chính quy (laNgheDiLamNgay). Từ khóa (không phân biệt dấu, hoa thường) tìm trong tên nghề, mô tả, tên và
 * mã nhóm; nhóm nghề, mục tiêu và mức lương tham khảo xét theo nhóm cha (`nhomTheoId`: id → nhóm).
 * Nghề thuộc nhóm không có trong `nhomTheoId` (nhóm đã tắt) bị bỏ.
 */
export function locNgheCuThe(dsNghe, nhomTheoId, { tuKhoa = '', nhomId = null, mucTieu = '', mucLuong = '' } = {}) {
  const q = boDau(tuKhoa.trim())
  return dsNghe.filter((nghe) => {
    const nhom = nhomTheoId[nghe.nhom_nghe_di_lam_id]
    if (!nhom || !laNgheDiLamNgay(nghe)) return false
    if (nhomId && nghe.nhom_nghe_di_lam_id !== nhomId) return false
    if (mucTieu && nhom.nhom_muc_tieu !== mucTieu) return false
    if (!khopMucLuong(nhom, mucLuong)) return false
    if (!q) return true
    return boDau([nghe.ten_nghe, nghe.mo_ta_ngan, nhom.ten_nhom, nhom.ma_nhom].join(' ')).includes(q)
  })
}
