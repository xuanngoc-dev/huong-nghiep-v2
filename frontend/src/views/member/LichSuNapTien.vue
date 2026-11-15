<template>
  <el-card v-loading="loading" shadow="never" class="history-card">
    <template #header>
      <div class="history-card__header">
        <h1 class="history-card__title">Lịch sử nạp tiền</h1>
        <CustomButton type="primary" @click="router.push({ name: 'nap-tien' })">
          <CustomIcon><Wallet /></CustomIcon>
          <span>Nạp tiền</span>
        </CustomButton>
      </div>
    </template>

    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Mã giao dịch, tên gói"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect v-model="filters.trang_thai" class="filter-status" placeholder="Trạng thái" clearable @change="onSearch">
        <CustomOption v-for="item in TRANG_THAI_NAP_TIEN" :key="item.value" :label="item.label" :value="item.value" />
      </CustomSelect>
      <CustomSelect v-model="filters.loai_ap_dung" class="filter-status" placeholder="Loại" clearable @change="onSearch">
        <CustomOption v-for="item in LOAI_AP_DUNG" :key="item.value" :label="item.label" :value="item.value" />
      </CustomSelect>
      <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      <CustomButton @click="onResetFilters">
        <CustomIcon><RefreshLeft /></CustomIcon>
        <span>Đặt lại</span>
      </CustomButton>
    </div>

    <CustomTable :data="rows" row-key="id">
      <CustomTableColumn type="index" label="STT" width="64" :index="(i) => (page - 1) * pageSize + i + 1" />
      <CustomTableColumn label="Thời gian" width="170">
        <template #default="{ row }">{{ hienThoiGian(row.created_at) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Mã giao dịch" width="140">
        <template #default="{ row }"><strong>{{ row.ma_giao_dich }}</strong></template>
      </CustomTableColumn>
      <CustomTableColumn label="Gói" min-width="200">
        <template #default="{ row }">
          <div>{{ row.ten_goi_cuoc }}</div>
          <CustomTag size="small" :type="loai(row).tag" effect="light">{{ loai(row).label }}</CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Nhận được" width="140">
        <template #default="{ row }">{{ hienSo(row.so_luot_nhan_duoc) }} {{ loai(row).donVi }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Số tiền" width="130" align="right">
        <template #default="{ row }">{{ hienTien(row.so_tien_nap) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Ngân hàng" width="140">
        <template #default="{ row }">
          <div>{{ row.ten_ngan_hang_viet_tat || '—' }}</div>
          <span v-if="row.so_tai_khoan_nhan" class="history-card__sub">{{ row.so_tai_khoan_nhan }}</span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" min-width="170">
        <template #default="{ row }">
          <CustomTag :type="trangThai(row).tag" effect="light">{{ trangThai(row).label }}</CustomTag>
          <div v-if="row.trang_thai === 1 && row.thoi_gian_xac_nhan" class="history-card__sub">
            Cộng lúc {{ hienThoiGian(row.thoi_gian_xac_nhan) }}
          </div>
          <div v-else-if="row.trang_thai === 0 && row.thoi_gian_thanh_toan" class="history-card__sub">
            Đã báo chuyển khoản, đang chờ ngân hàng
          </div>
          <div v-if="row.trang_thai === 3 && row.ghi_chu" class="history-card__sub">{{ row.ghi_chu }}</div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thao tác" width="190" fixed="right" align="center">
        <template #default="{ row }">
          <div v-if="row.trang_thai === 0" class="row-actions">
            <CustomButton size="small" type="primary" @click="moThanhToan(row)">Thanh toán</CustomButton>
            <CustomButton size="small" @click="onHuy(row)">Hủy</CustomButton>
          </div>
          <span v-else class="history-card__sub">—</span>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Bạn chưa có giao dịch nạp tiền nào." />
      </template>
    </CustomTable>

    <div class="pager">
      <CustomPagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="onSizeChange"
      />
    </div>

    <ThanhToanDialog v-model="thanhToanMo" :giao-dich="giaoDich" @updated="onUpdated" />
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import ThanhToanDialog from '@/components/member/ThanhToanDialog.vue'
import { fetchNapTienCuaToi, huyNapTien } from '@/api/napTien'
import {
  LOAI_AP_DUNG,
  TRANG_THAI_NAP_TIEN,
  hienSo,
  hienThoiGian,
  hienTien,
  timTheoGiaTri,
} from '@/data/napTien'

defineOptions({ name: 'MemberLichSuNapTien' })

const router = useRouter()
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const thanhToanMo = ref(false)
const giaoDich = ref(null)

function emptyFilters() {
  return { q: '', trang_thai: '', loai_ap_dung: '' }
}

const filters = reactive(emptyFilters())

function loai(row) {
  return timTheoGiaTri(LOAI_AP_DUNG, row.loai_ap_dung)
}

function trangThai(row) {
  return timTheoGiaTri(TRANG_THAI_NAP_TIEN, row.trang_thai)
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai !== '' && filters.trang_thai !== null) params.trang_thai = filters.trang_thai
    if (filters.loai_ap_dung) params.loai_ap_dung = filters.loai_ap_dung
    const data = await fetchNapTienCuaToi(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được lịch sử nạp tiền'))
  } finally {
    loading.value = false
  }
}

function onSearch() {
  if (page.value !== 1) {
    page.value = 1
  }
  load()
}

function onResetFilters() {
  Object.assign(filters, emptyFilters())
  onSearch()
}

function onSizeChange() {
  page.value = 1
  load()
}

function moThanhToan(row) {
  giaoDich.value = row
  thanhToanMo.value = true
}

// Modal lưu ngân hàng/báo chuyển khoản: cập nhật dòng tương ứng trong bảng.
function onUpdated(data) {
  giaoDich.value = data
  const index = rows.value.findIndex((row) => row.id === data.id)
  if (index >= 0) rows.value.splice(index, 1, data)
}

async function onHuy(row) {
  try {
    await ElMessageBox.confirm(`Hủy giao dịch ${row.ma_giao_dich} (${row.ten_goi_cuoc})?`, 'Xác nhận hủy', {
      type: 'warning',
      confirmButtonText: 'Hủy giao dịch',
      cancelButtonText: 'Không',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }
  try {
    onUpdated(await huyNapTien(row.id))
    ElMessage.success('Đã hủy giao dịch')
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không hủy được giao dịch'))
  }
}

// Đóng modal thì tải lại: giao dịch có thể đã được xác nhận qua webhook.
watch(thanhToanMo, (open) => {
  if (!open) load()
})

onMounted(load)
</script>

<style scoped>
.history-card {
  border-radius: 12px;
}

.history-card__header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.history-card__title {
  margin: 0;
  font-size: 20px;
  line-height: 1.4;
}

.history-card__sub {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.filter-search {
  width: 240px;
}

.filter-status {
  width: 160px;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 767px) {
  .filter-search,
  .filter-status {
    width: 100%;
  }

  .pager {
    justify-content: center;
  }
}
</style>
