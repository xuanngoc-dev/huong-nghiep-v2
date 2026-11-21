import { onMounted, onUnmounted, ref, unref, watch } from 'vue'
import { TRANG_THAI_DAU, buocGoChu, chuDangHien } from '@/utils/goChuGoiY'

// Placeholder tự gõ / xóa lần lượt các gợi ý trong `danhSach` (ref hoặc mảng).
// `tamDung` (ref, tùy chọn): true thì dừng hẳn, vd. khi ô đã có chữ nên placeholder không hiện.
// Người dùng bật "giảm chuyển động": không gõ từng ký tự, chỉ đổi cả gợi ý sau mỗi 2.5 giây.
export function useGoChuGoiY(danhSach, tamDung = ref(false)) {
  const chu = ref('')
  let trangThai = { ...TRANG_THAI_DAU }
  let henGio = null
  let giamChuyenDong = false

  function dung() {
    clearTimeout(henGio)
    henGio = null
  }

  function chay() {
    dung()
    const ds = unref(danhSach) || []
    if (!ds.length || unref(tamDung)) return
    if (giamChuyenDong) {
      chu.value = ds[trangThai.chiSo % ds.length]
      henGio = setTimeout(() => {
        trangThai = { ...trangThai, chiSo: (trangThai.chiSo + 1) % ds.length }
        chay()
      }, 2500)
      return
    }
    const { trangThai: moi, cho } = buocGoChu(trangThai, ds)
    trangThai = moi
    chu.value = chuDangHien(trangThai, ds)
    henGio = setTimeout(chay, cho)
  }

  // Đổi danh sách (vd. đổi tab loại tra cứu): gõ lại từ gợi ý đầu.
  watch(
    () => unref(danhSach),
    () => {
      trangThai = { ...TRANG_THAI_DAU }
      chu.value = ''
      chay()
    },
  )

  watch(
    () => unref(tamDung),
    (dangDung) => (dangDung ? dung() : chay()),
  )

  onMounted(() => {
    giamChuyenDong = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
    chay()
  })

  onUnmounted(dung)

  return chu
}
