import { ref } from 'vue'
import { huongDiApi } from '@/api/thcsHuongDi'
import thcsImage from '@/assets/guest/thcs.jpg'
import thptImage from '@/assets/guest/thpt.jpg'
import phanVanImage from '@/assets/guest/phan-van.jpg'
import nhaTruongImage from '@/assets/guest/nha-truong.jpg'
import sinhVienImage from '@/assets/guest/sinh-vien.jpg'
import thanhNienImage from '@/assets/guest/thanh-nien.jpg'
import nhaTuyenDungImage from '@/assets/guest/nha-tuyen-dung.jpg'

// Định dạng và tải dữ liệu danh mục hướng đi sau THCS cho trang khách.

// Danh mục hướng đi chưa có cột ảnh: gán ảnh có sẵn theo mã hướng đi, mã khác dùng ảnh THCS.
const ANH_HUONG_DI = {
  THPT_CONG_LAP: thptImage,
  THPT_CHUYEN: phanVanImage,
  THPT_TU_THUC: nhaTruongImage,
  THPT_QUOC_TE: sinhVienImage,
  GDNN_GDTX: thcsImage,
  TRUNG_CAP_9_PLUS: thanhNienImage,
  HOC_NGHE_NGAN_HAN: nhaTuyenDungImage,
}

export function anhHuongDi(huong) {
  return ANH_HUONG_DI[huong.ma_huong] || thcsImage
}

const dinhDangSo = new Intl.NumberFormat('vi-VN')

// Chi phí lưu theo VNĐ/tháng; ưu tiên phần mô tả chữ.
export function chiPhi(huong) {
  if (huong.chi_phi_du_kien_text) return huong.chi_phi_du_kien_text
  const min = huong.chi_phi_thang_min != null ? Number(huong.chi_phi_thang_min) : null
  const max = huong.chi_phi_thang_max != null ? Number(huong.chi_phi_thang_max) : null
  if (min == null && max == null) return ''
  if (min != null && max != null && min !== max) return `${dinhDangSo.format(min)} - ${dinhDangSo.format(max)} VNĐ/tháng`
  return `${dinhDangSo.format(max ?? min)} VNĐ/tháng`
}

/** Danh sách hướng đi đang hoạt động, theo thứ tự hiển thị. */
export function useDsHuongDiThcs() {
  const dsHuong = ref([])
  const dangTai = ref(false)
  const loi = ref('')

  async function taiHuongDi() {
    dangTai.value = true
    loi.value = ''
    try {
      const data = await huongDiApi.fetch({ trang_thai: 1, page: 1, page_size: 100 })
      dsHuong.value = data.items || []
    } catch {
      loi.value = 'Không tải được danh sách hướng đi.'
    } finally {
      dangTai.value = false
    }
  }

  return { dsHuong, dangTai, loi, taiHuongDi }
}

/**
 * Mức hợp của một hướng đi với câu trả lời tự đánh giá (0-100).
 * `traLoi`: { tieuChiId: 1-5 }; `diem`: { tieuChiId: điểm phù hợp 1-5 của hướng đi }.
 * Mỗi tiêu chí: càng gần nhau càng hợp (lệch 0 → 1, lệch 4 → 0); chỉ tính tiêu chí đã trả lời và hướng đi có điểm.
 */
export function mucHop(traLoi, diem) {
  const cap = Object.entries(traLoi).filter(([id, u]) => u && diem[id])
  if (!cap.length) return null
  const tong = cap.reduce((sum, [id, u]) => sum + (1 - Math.abs(u - diem[id]) / 4), 0)
  return Math.round((tong / cap.length) * 100)
}
