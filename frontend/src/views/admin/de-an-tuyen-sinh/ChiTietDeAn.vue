<template>
  <div v-loading="loading" class="detail">
    <p v-if="subtitle" class="detail__subtitle">{{ subtitle }}</p>
    <el-tabs v-model="activeTab" class="detail__tabs">
      <el-tab-pane
        v-for="tab in tabs"
        :key="tab.key"
        :name="tab.key"
        :label="tabLabel(tab)"
        lazy
      >
        <component
          :is="tab.component"
          v-if="tab.overview"
          :de-an="deAn"
          :loading="loading"
        />
        <component :is="tab.component" v-else-if="tab.quyTac && props.deAnId" :de-an-id="props.deAnId" />
        <component
          :is="tab.component"
          v-else-if="tab.merged"
          :programs="rowsOf('dats_chuong_trinh_dao_tao')"
          :methods="rowsOf('dats_phuong_thuc')"
          :criteria="rowsOf('dats_tieu_chi_xet_tuyen')"
        />
        <component :is="tab.component" v-else :rows="rowsOf(tab.key)" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
/** Nội dung chi tiết đề án tuyển sinh theo tab; dùng trong ChiTietDeAnDialog và trang Chương trình & phương thức. */
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchDeAnTuyenSinhChiTiet } from '@/api/deAnTuyenSinh'
import TongQuan from './chi-tiet/TongQuan.vue'
import TruSo from './chi-tiet/TruSo.vue'
import Website from './chi-tiet/Website.vue'
import LienHe from './chi-tiet/LienHe.vue'
import ChuongTrinh from './chi-tiet/ChuongTrinh.vue'
import KeHoach from './chi-tiet/KeHoach.vue'
import ToHop from './chi-tiet/ToHop.vue'
import NhanSu from './chi-tiet/NhanSu.vue'
import CoSoVatChat from './chi-tiet/CoSoVatChat.vue'
import QuyMo from './chi-tiet/QuyMo.vue'
import TyLeViecLam from './chi-tiet/TyLeViecLam.vue'
import TrinhDoNganh from './chi-tiet/TrinhDoNganh.vue'
import DoiTuong from './chi-tiet/DoiTuong.vue'
import DieuKien from './chi-tiet/DieuKien.vue'
import TieuChi from './chi-tiet/TieuChi.vue'
import DiemCong from './chi-tiet/DiemCong.vue'
import QuyTacPhanBo from './chi-tiet/QuyTacPhanBo.vue'
import HoSo from './chi-tiet/HoSo.vue'
import QuyDoiNguong from './chi-tiet/QuyDoiNguong.vue'
import QuyDoiDiem from './chi-tiet/QuyDoiDiem.vue'
import XetTuyenThang from './chi-tiet/XetTuyenThang.vue'
import UuTien from './chi-tiet/UuTien.vue'
import QuyTacXetTuyen from './chi-tiet/QuyTacXetTuyen.vue'

const tabs = [
  { key: 'tong_quan', label: 'Tổng quan', component: TongQuan, overview: true },
  { key: 'quy_tac', label: 'Quy tắc xét tuyển', component: QuyTacXetTuyen, quyTac: true },
  { key: 'dats_tru_so', label: 'Trụ sở', component: TruSo },
  { key: 'dats_website', label: 'Website', component: Website },
  { key: 'dats_lien_he_tuyen_sinh', label: 'Liên hệ', component: LienHe },
  { key: 'dats_chuong_trinh_dao_tao', label: 'Chương trình & phương thức', component: ChuongTrinh, merged: true },
  { key: 'dats_ke_hoach_tuyen_sinh', label: 'Kế hoạch', component: KeHoach },
  { key: 'dats_phuong_thuc_to_hop', label: 'Tổ hợp', component: ToHop },
  { key: 'dats_nhan_su', label: 'Nhân sự', component: NhanSu },
  { key: 'dats_co_so_vat_chat', label: 'Cơ sở vật chất', component: CoSoVatChat },
  { key: 'dats_quy_mo_dao_tao', label: 'Quy mô', component: QuyMo },
  { key: 'dats_ty_le_viec_lam', label: 'Tỷ lệ việc làm', component: TyLeViecLam },
  { key: 'dats_trinh_do_nganh', label: 'Trình độ ngành', component: TrinhDoNganh },
  { key: 'dats_doi_tuong_du_tuyen', label: 'Đối tượng', component: DoiTuong },
  { key: 'dats_dieu_kien_du_tuyen', label: 'Điều kiện', component: DieuKien },
  { key: 'dats_tieu_chi_xet_tuyen', label: 'Tiêu chí', component: TieuChi },
  { key: 'dats_diem_cong', label: 'Điểm cộng', component: DiemCong },
  { key: 'dats_quy_tac_phan_bo', label: 'Quy tắc phân bổ', component: QuyTacPhanBo },
  { key: 'dats_ho_so_du_tuyen', label: 'Hồ sơ', component: HoSo },
  { key: 'dats_quy_doi_nguong_dau_vao', label: 'Quy đổi ngưỡng', component: QuyDoiNguong },
  { key: 'dats_quy_doi_diem_trung_tuyen', label: 'Quy đổi điểm', component: QuyDoiDiem },
  { key: 'dats_chinh_sach_xet_tuyen_thang', label: 'Xét tuyển thẳng', component: XetTuyenThang },
  { key: 'dats_chinh_sach_uu_tien_xet_tuyen', label: 'Ưu tiên', component: UuTien },
]

const props = defineProps({
  deAnId: { type: Number, default: null },
  // Tab mở khi đổi đề án.
  tabMacDinh: { type: String, default: 'tong_quan' },
  // Tải lại khi true (dialog truyền trạng thái mở; trang luôn true).
  active: { type: Boolean, default: true },
})

const loading = ref(false)
const activeTab = ref(props.tabMacDinh)
const detail = ref(null)
let requestSerial = 0

const deAn = computed(() => detail.value?.de_an || null)

const subtitle = computed(() => {
  const item = deAn.value
  if (!item) return ''
  const school = item.ma_truong ? `${item.ma_truong} — ${item.ten_truong}` : item.ten_truong
  return [school, item.nam_tuyen_sinh, item.ten_de_an].filter(Boolean).join(' · ')
})

function tabLabel(tab) {
  if (tab.overview || tab.quyTac || !detail.value) return tab.label
  const count = detail.value.bang?.[tab.key]?.length || 0
  return `${tab.label} (${count})`
}

function rowsOf(key) {
  return detail.value?.bang?.[key] || []
}

function errorMessage(error) {
  const message = error?.response?.data?.detail
  if (typeof message === 'string') return message
  return 'Không tải được chi tiết đề án tuyển sinh'
}

async function loadDetail(id) {
  const serial = ++requestSerial
  loading.value = true
  detail.value = null
  try {
    const data = await fetchDeAnTuyenSinhChiTiet(id, { skipLoading: true, timeout: 120000 })
    if (serial !== requestSerial) return
    detail.value = data
  } catch (error) {
    if (serial !== requestSerial) return
    ElMessage.error(errorMessage(error))
  } finally {
    if (serial === requestSerial) loading.value = false
  }
}

watch(
  () => [props.active, props.deAnId],
  ([open, id]) => {
    if (!id) {
      detail.value = null
      return
    }
    if (!open) return
    activeTab.value = props.tabMacDinh
    loadDetail(id)
  },
  { immediate: true },
)
</script>

<style scoped>
.detail {
  display: flex;
  flex-direction: column;
  min-height: 420px;
}

.detail__subtitle {
  margin: 0 0 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.detail__tabs {
  min-height: 0;
}
</style>
