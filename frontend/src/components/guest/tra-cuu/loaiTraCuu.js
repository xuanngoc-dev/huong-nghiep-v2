// Các loại tra cứu danh mục cho khách: dùng ở trang /tra-cuu và mục "Khám phá" trên trang chủ.
// Mỗi loại: params gửi kèm API danh sách, boLoc (lọc thêm, tùy chọn),
// the(item) → nội dung thẻ kết quả, chiTiet(item) → các dòng trong hộp chi tiết (bỏ dòng rỗng).
// Hàm gọi API gắn theo id ở TraCuu.vue / LandingExplore.vue để file này không phụ thuộc axios (test được).

function noiDanhSach(value) {
  return Array.isArray(value) ? value.filter(Boolean).join(', ') : value
}

function coGiaTri(value) {
  return value !== null && value !== undefined && String(value).trim() !== ''
}

function dong(label, value, link = false) {
  return { label, value: noiDanhSach(value), link }
}

function locDong(rows) {
  return rows.filter((row) => coGiaTri(row.value))
}

function locTags(tags) {
  return tags.filter(coGiaTri)
}

/** Loại cơ sở; chưa khai báo thì đoán từ tên trường (cùng quy tắc loai_hien_thi ở backend). */
export function loaiCoSo(item) {
  if (coGiaTri(item.loai_co_so)) return item.loai_co_so
  const ten = item.ten_truong || ''
  if (ten.includes('Học viện')) return 'Học viện'
  if (ten.includes('Cao đẳng')) return 'Cao đẳng'
  if (ten.includes('Đại học')) return 'Đại học'
  return null
}

export const LOAI_TRA_CUU = [
  {
    id: 'truong',
    label: 'Trường ĐH, CĐ',
    placeholder: 'Tên trường, mã trường hoặc tên viết tắt...',
    params: {},
    boLoc: {
      key: 'loai_co_so',
      label: 'Loại cơ sở',
      options: ['Đại học', 'Học viện', 'Cao đẳng'],
    },
    the: (item) => ({
      tieuDe: item.ten_truong,
      ma: item.ma_truong,
      tags: locTags([loaiCoSo(item), item.loai_hinh, item.ten_tinh_thanh]),
      moTa: item.gioi_thieu_ngan,
    }),
    chiTiet: (item) =>
      locDong([
        dong('Mã trường', item.ma_truong),
        dong('Tên tiếng Anh', item.ten_tieng_anh),
        dong('Tên viết tắt', item.ten_viet_tat),
        dong('Loại cơ sở', loaiCoSo(item)),
        dong('Loại hình', item.loai_hinh),
        dong('Cơ quan chủ quản', item.co_quan_chu_quan),
        dong('Năm thành lập', item.nam_thanh_lap),
        dong('Bậc đào tạo', item.bac_dao_tao),
        dong('Lĩnh vực đào tạo chính', item.linh_vuc_dao_tao_chinh),
        dong('Địa chỉ', item.dia_chi_tru_so || item.ten_tinh_thanh),
        dong('Học phí trung bình', item.hoc_phi_trung_binh),
        dong('Hotline tuyển sinh', item.hotline_tuyen_sinh),
        dong('Email tuyển sinh', item.email_tuyen_sinh),
        dong('Website', item.website, true),
        dong('Website tuyển sinh', item.website_tuyen_sinh, true),
        dong('Giới thiệu', item.gioi_thieu_ngan),
      ]),
  },
  {
    id: 'nganh',
    label: 'Ngành đào tạo',
    placeholder: 'Tên ngành hoặc mã ngành...',
    params: { trang_thai: 1 },
    the: (item) => ({
      tieuDe: item.ten_nganh,
      ma: item.ma_nganh,
      tags: locTags([item.ten_nhom_nganh, item.trinh_do, item.thoi_gian_dao_tao]),
      moTa: item.mo_ta,
    }),
    chiTiet: (item) =>
      locDong([
        dong('Mã ngành', item.ma_nganh),
        dong('Tên tiếng Anh', item.ten_tieng_anh),
        dong('Nhóm ngành', item.ten_nhom_nganh),
        dong('Trình độ', item.trinh_do),
        dong('Thời gian đào tạo', item.thoi_gian_dao_tao),
        dong('Nhóm Holland', item.ma_holand),
        dong('Mô tả', item.mo_ta),
      ]),
  },
  {
    id: 'phuong-thuc',
    label: 'Phương thức tuyển sinh',
    placeholder: 'Tên hoặc mã phương thức...',
    params: { trang_thai: 1 },
    the: (item) => ({
      tieuDe: item.ten_phuong_thuc,
      ma: item.ma_phuong_thuc,
      tags: [],
      moTa: item.giai_thich,
    }),
    chiTiet: (item) =>
      locDong([
        dong('Mã phương thức', item.ma_phuong_thuc),
        dong('Giải thích', item.giai_thich),
        dong('Trường hợp cụ thể', item.truong_hop_cu_the),
        dong('Lưu ý', item.luu_y),
      ]),
  },
  {
    id: 'to-hop',
    label: 'Tổ hợp môn',
    placeholder: 'Mã tổ hợp (A00, D01...) hoặc tên môn...',
    params: { trang_thai: 1 },
    the: (item) => ({
      tieuDe: item.ten_to_hop,
      ma: item.ma_to_hop,
      // ds_mon_hoc là mã môn (VAN, TOAN...) và đã có trong tên tổ hợp: không hiện lại.
      tags: [],
      moTa: item.ghi_chu,
    }),
    chiTiet: (item) =>
      locDong([
        dong('Mã tổ hợp', item.ma_to_hop),
        dong('Môn học', item.ten_to_hop),
        dong('Ghi chú', item.ghi_chu),
      ]),
  },
  {
    id: 'bai-thi',
    label: 'Bài thi đánh giá năng lực',
    placeholder: 'Tên bài thi, tên viết tắt hoặc đơn vị tổ chức...',
    params: {},
    the: (item) => ({
      tieuDe: item.ten_bai_thi,
      ma: item.ten_viet_tat || item.ma_bai_thi,
      tags: locTags([item.loai_danh_gia, item.don_vi_to_chuc]),
      moTa: item.mo_ta,
    }),
    chiTiet: (item) =>
      locDong([
        dong('Tên đầy đủ', item.ten_chi_tiet),
        dong('Đơn vị tổ chức', item.don_vi_to_chuc),
        dong('Loại đánh giá', item.loai_danh_gia),
        dong('Đối tượng dự thi', item.doi_tuong_du_thi),
        dong('Thang điểm', item.thang_diem),
        dong('Thời lượng', coGiaTri(item.thoi_luong_phut) ? `${item.thoi_luong_phut} phút` : null),
        dong('Cách công bố kết quả', item.cach_cong_bo_ket_qua),
        dong('Website', item.website_chinh_thuc, true),
        dong('Mô tả', item.mo_ta),
      ]),
  },
  {
    id: 'chung-chi',
    label: 'Chứng chỉ ngoại ngữ',
    placeholder: 'Tên chứng chỉ (IELTS, TOEIC...) hoặc ngôn ngữ...',
    params: {},
    the: (item) => ({
      tieuDe: item.ten_chung_chi,
      ma: item.ma_chung_chi,
      tags: locTags([item.ten_ngon_ngu, item.loai_chung_chi, item.don_vi_cap]),
      moTa: item.ten_chi_tiet || item.ghi_chu,
    }),
    chiTiet: (item) =>
      locDong([
        dong('Tên đầy đủ', item.ten_chi_tiet),
        dong('Ngôn ngữ', item.ten_ngon_ngu),
        dong('Đơn vị cấp', item.don_vi_cap),
        dong('Thang điểm', item.thang_diem),
        dong('Kỹ năng đánh giá', item.ky_nang_duoc_danh_gia),
        dong('Hình thức thi', item.hinh_thuc_thi),
        dong(
          'Thời hạn hiệu lực',
          coGiaTri(item.thoi_han_hieu_luc_thang) ? `${item.thoi_han_hieu_luc_thang} tháng` : null,
        ),
        dong('Ghi chú', item.ghi_chu),
      ]),
  },
]

export const LOAI_TRA_CUU_MAC_DINH = LOAI_TRA_CUU[0].id

/** Loại tra cứu theo id; id lạ (vd. sửa tay query ?loai=) → loại mặc định. */
export function timLoaiTraCuu(id) {
  return LOAI_TRA_CUU.find((loai) => loai.id === id) || LOAI_TRA_CUU[0]
}
