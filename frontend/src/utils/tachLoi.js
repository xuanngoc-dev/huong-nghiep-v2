/**
 * Tách thông báo lỗi dài thành phần đầu + danh sách để hiển thị dạng liệt kê.
 *
 * - Chuỗi "quy_tac_xet_tuyen có 3 lỗi: a; b; c" → { dau: 'quy_tac_xet_tuyen có 3 lỗi:', ds: ['a', 'b', 'c'] }.
 * - Object { thong_bao, loi: [...] } (API quy tắc xét tuyển) → { dau: thong_bao, ds: loi }.
 * - Còn lại → { dau: chuỗi, ds: [] }.
 */
export function tachLoi(noiDung) {
  if (noiDung && typeof noiDung === 'object' && Array.isArray(noiDung.loi)) {
    return { dau: String(noiDung.thong_bao || `Có ${noiDung.loi.length} lỗi:`), ds: noiDung.loi.map(String) }
  }
  const text = String(noiDung ?? '')
  const khop = text.match(/^(.*?\blỗi):\s+(.+)$/s)
  if (khop) {
    const ds = khop[2].split(/;\s+/).filter(Boolean)
    if (ds.length > 1) return { dau: `${khop[1]}:`, ds }
  }
  return { dau: text, ds: [] }
}
