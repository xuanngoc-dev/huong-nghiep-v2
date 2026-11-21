// Lọc danh sách bài viết cẩm nang theo chủ đề và từ khóa (tiêu đề, tóm tắt), không phân biệt hoa thường và dấu.

function boDau(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .toLowerCase()
}

/** Bài khớp `chuDe` (rỗng = mọi chủ đề) và chứa `tuKhoa`, mới nhất trước. */
export function locBaiViet(danhSach, { chuDe = '', tuKhoa = '' } = {}) {
  const q = boDau(tuKhoa.trim())
  return danhSach
    .filter((item) => !chuDe || item.category === chuDe)
    .filter((item) => !q || boDau(`${item.title} ${item.summary}`).includes(q))
    .sort((a, b) => String(b.date).localeCompare(String(a.date)))
}
