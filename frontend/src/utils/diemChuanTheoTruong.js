/**
 * Dựng bảng điểm chuẩn của một trường trong một năm, theo bố cục bảng chương trình của đề án:
 * mỗi hàng là một chương trình đào tạo (kèm chỉ tiêu, mã xét tuyển), mỗi phương thức tuyển sinh một cột;
 * ô gồm tổ hợp xét tuyển khai trong đề án và điểm chuẩn cùng năm. Mã xét tuyển có điểm chuẩn nhưng
 * không có trong đề án vẫn thành một hàng. Điểm chuẩn không gắn phương thức nằm ở cột "mọi phương thức" (mã rỗng).
 */

const soSanhMa = (a, b) => String(a || '').localeCompare(String(b || ''), 'vi', { numeric: true })

const boDau = (text) =>
  String(text || '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/gi, 'd')
    .toLowerCase()

/**
 * Tiêu chí phụ của một hàng, gom theo nội dung: [{ noiDung, phuongThuc: [mã...] }] theo thứ tự mã phương thức.
 * Phương thức không có tiêu chí phụ thì bỏ qua.
 */
function gomTieuChiPhu(h, maPhuongThuc) {
  const theoNoiDung = new Map()
  for (const ma of Object.keys(h.o).sort(soSanhMa)) {
    if (maPhuongThuc && ma !== maPhuongThuc) continue
    for (const item of h.o[ma].diem) {
      const noiDung = String(item.tieu_chi_phu || '').trim()
      if (!noiDung) continue
      if (!theoNoiDung.has(noiDung)) theoNoiDung.set(noiDung, [])
      const ds = theoNoiDung.get(noiDung)
      if (!ds.includes(ma)) ds.push(ma)
    }
  }
  return [...theoNoiDung].map(([noiDung, phuongThuc]) => ({ noiDung, phuongThuc }))
}

/** Năm mới nhất có chương trình hoặc điểm chuẩn; null nếu không có dữ liệu. */
export function namMoiNhat(chuongTrinh = [], diemChuan = []) {
  const nam = [...chuongTrinh, ...diemChuan].map((item) => item.nam_tuyen_sinh).filter(Boolean)
  return nam.length ? Math.max(...nam) : null
}

/**
 * @param chuongTrinh chương trình đào tạo của năm (lấy kèm phương thức: kem_phuong_thuc).
 * @param diemChuan dòng điểm chuẩn của năm.
 * @param danhMucPhuongThuc danh mục phương thức của Bộ, để lấy tên đầy đủ.
 * @param q lọc theo mã xét tuyển hoặc tên chương trình (không phân biệt dấu).
 * @param maPhuongThuc chỉ hiện một phương thức.
 */
export function bangDiemTheoTruong({ chuongTrinh = [], diemChuan = [], danhMucPhuongThuc = [], q = '', maPhuongThuc = '' } = {}) {
  const tenDanhMuc = new Map(danhMucPhuongThuc.map((item) => [item.ma_phuong_thuc, item.ten_phuong_thuc]))
  const cot = new Map()
  function themCot(ma, maTruong, tenTruong, tenKhac) {
    if (!cot.has(ma)) cot.set(ma, { ma, maTruong: [], tenTruong: [], tenKhac: '' })
    const c = cot.get(ma)
    if (maTruong && maTruong !== ma && !c.maTruong.includes(maTruong)) c.maTruong.push(maTruong)
    if (tenTruong && !c.tenTruong.includes(tenTruong)) c.tenTruong.push(tenTruong)
    if (tenKhac && !c.tenKhac) c.tenKhac = tenKhac
  }
  const oMoi = () => ({ dung: false, toHop: [], diem: [] })

  const hang = []
  const hangTheoMa = new Map()
  for (const ct of chuongTrinh) {
    const h = {
      khoa: `ct-${ct.id}`,
      ten_chuong_trinh: ct.ten_chuong_trinh || '',
      chi_tieu: ct.chi_tieu_tuyen_sinh ?? null,
      ma_xet_tuyen: ct.ma_xet_tuyen || '',
      o: {},
    }
    for (const pt of ct.phuong_thuc || []) {
      const ma = pt.ma_phuong_thuc_cua_bo || ''
      themCot(ma, pt.ma_phuong_thuc_cua_truong, pt.ten_phuong_thuc_cua_truong)
      const o = (h.o[ma] ||= oMoi())
      o.dung = true
      for (const toHop of pt.to_hop_mon_hoc || []) if (!o.toHop.includes(toHop)) o.toHop.push(toHop)
    }
    hang.push(h)
    if (h.ma_xet_tuyen && !hangTheoMa.has(h.ma_xet_tuyen)) hangTheoMa.set(h.ma_xet_tuyen, h)
  }

  for (const item of diemChuan) {
    let h = hangTheoMa.get(item.ma_xet_tuyen)
    if (!h) {
      h = { khoa: `dc-${item.ma_xet_tuyen}`, ten_chuong_trinh: '', chi_tieu: null, ma_xet_tuyen: item.ma_xet_tuyen, o: {} }
      hang.push(h)
      hangTheoMa.set(item.ma_xet_tuyen, h)
    }
    if (!h.ten_chuong_trinh && item.ten_chuong_trinh) h.ten_chuong_trinh = item.ten_chuong_trinh
    const ma = item.ma_phuong_thuc_cua_bo || ''
    themCot(ma, null, null, item.ten_phuong_thuc)
    ;(h.o[ma] ||= oMoi()).diem.push(item)
  }

  for (const h of hang) {
    for (const o of Object.values(h.o)) {
      o.diem.sort((a, b) => soSanhMa(a.ma_to_hop, b.ma_to_hop))
    }
  }

  const tuKhoa = boDau(q.trim())
  const hangLoc = hang
    .filter((h) => !tuKhoa || boDau(`${h.ma_xet_tuyen} ${h.ten_chuong_trinh}`).includes(tuKhoa))
    .filter((h) => !maPhuongThuc || h.o[maPhuongThuc])
    .sort((a, b) => soSanhMa(a.ma_xet_tuyen, b.ma_xet_tuyen) || soSanhMa(a.ten_chuong_trinh, b.ten_chuong_trinh))
  for (const h of hangLoc) h.tieuChiPhu = gomTieuChiPhu(h, maPhuongThuc)

  const cotPhuongThuc = [...cot.values()]
    .filter((c) => !maPhuongThuc || c.ma === maPhuongThuc)
    .sort((a, b) => soSanhMa(a.ma, b.ma))
    .map((c) => ({
      ma: c.ma,
      // Tiêu đề cột chỉ ghi mã; chi tiết hiện khi rê chuột.
      nhan: c.ma || 'Mọi phương thức',
      chiTiet: c.ma
        ? { ten: tenDanhMuc.get(c.ma) || c.tenKhac || '', maTruong: c.maTruong, tenTruong: c.tenTruong }
        : { ten: 'Điểm chuẩn áp dụng cho mọi phương thức', maTruong: [], tenTruong: [] },
    }))

  return { cotPhuongThuc, hang: hangLoc }
}
