import ChiTietTruongModal from './ChiTietTruongModal.vue'
import ChiTietNganhModal from './ChiTietNganhModal.vue'
import ChiTietPhuongThucModal from './ChiTietPhuongThucModal.vue'
import ChiTietToHopModal from './ChiTietToHopModal.vue'
import ChiTietBaiThiModal from './ChiTietBaiThiModal.vue'
import ChiTietChungChiModal from './ChiTietChungChiModal.vue'

// Modal chi tiết theo id loại tra cứu trong loaiTraCuu.js (tách riêng để loaiTraCuu.js không import .vue).
export const MODAL_CHI_TIET_THEO_LOAI = {
  truong: ChiTietTruongModal,
  nganh: ChiTietNganhModal,
  'phuong-thuc': ChiTietPhuongThucModal,
  'to-hop': ChiTietToHopModal,
  'bai-thi': ChiTietBaiThiModal,
  'chung-chi': ChiTietChungChiModal,
}
