<template>
  <el-card v-loading="loading" shadow="never" class="history-card">
    <template #header>
      <div>
        <h1 class="history-card__title">Lịch sử trắc nghiệm</h1>
        <!-- <p class="history-card__lead">Các phiên trắc nghiệm Holland bạn đã thực hiện, mới nhất trước.</p> -->
      </div>
    </template>

    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Tìm mã giao dịch"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect
        v-model="filters.trang_thai"
        class="filter-status"
        placeholder="Trạng thái"
        clearable
        @change="onSearch"
      >
        <CustomOption
          v-for="item in TRANG_THAI_OPTIONS"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </CustomSelect>
      <CustomDatePicker
        v-model="filters.khoang_ngay"
        class="filter-date"
        type="daterange"
        value-format="YYYY-MM-DD"
        format="DD/MM/YYYY"
        range-separator="–"
        start-placeholder="Từ ngày"
        end-placeholder="Đến ngày"
        clearable
        @change="onSearch"
      />
      <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      <CustomButton @click="onResetFilters">
        <CustomIcon><RefreshLeft /></CustomIcon>
        <span>Đặt lại</span>
      </CustomButton>
    </div>

    <CustomTable :data="rows" row-key="id">
      <CustomTableColumn type="index" label="STT" width="64" :index="(i) => (page - 1) * pageSize + i + 1" />
      <CustomTableColumn label="Mã giao dịch" min-width="160">
        <template #default="{ row }">{{ row.ma_giao_dich || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Thời gian" min-width="150">
        <template #default="{ row }">{{ formatThoiGian(row.created_at) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Tiến độ" min-width="180">
        <template #default="{ row }">
          <el-progress :percentage="tienDo(row)" :status="row.da_xong ? 'success' : ''" />
          <span class="history-card__sub">{{ row.so_da_tra_loi }}/{{ row.so_cau_hoi }} câu</span>
        </template>
      </CustomTableColumn>
      <!-- <CustomTableColumn label="Mã Holland" width="120" align="center">
        <template #default="{ row }">
          <CustomTag v-if="row.ma_noi_bat" type="primary">{{ row.ma_noi_bat }}</CustomTag>
          <span v-else>—</span>
        </template>
      </CustomTableColumn> -->
      <CustomTableColumn label="Trạng thái" width="130" align="center">
        <template #default="{ row }">
          <CustomTag :type="row.da_xong ? 'success' : 'warning'">
            {{ row.da_xong ? 'Hoàn thành' : 'Đang làm' }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thao tác" width="110" fixed="right" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <template v-if="row.da_xong">
              <CustomTooltip content="Xem kết quả" placement="top">
                <CustomButton link type="primary" aria-label="Xem kết quả" @click="xemKetQua(row)">
                  <CustomIcon><DataAnalysis /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Ngành phù hợp" placement="top">
                <CustomButton link type="primary" aria-label="Ngành phù hợp" @click="xemNganhPhuHop(row)">
                  <CustomIcon><School /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </template>
            <CustomTooltip v-else-if="row.loai_cau_hoi_id_tiep" content="Tiếp tục làm" placement="top">
              <CustomButton link type="warning" aria-label="Tiếp tục làm" @click="lamTiep(row)">
                <CustomIcon><VideoPlay /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Không có phiên trắc nghiệm nào." />
      </template>
    </CustomTable>

    <div class="pager">
      <CustomPagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="onPageChange"
        @size-change="onSizeChange"
      />
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchLichSuKhaoSat } from '@/api/phienKhaoSat'

const TRANG_THAI_OPTIONS = [
  { value: 'hoan-thanh', label: 'Hoàn thành' },
  { value: 'dang-lam', label: 'Đang làm' },
]

const router = useRouter()
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const filters = reactive(emptyFilters())

function emptyFilters() {
  return {
    q: '',
    trang_thai: '',
    khoang_ngay: null,
  }
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function formatThoiGian(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function tienDo(row) {
  if (!row.so_cau_hoi) return 0
  return Math.round((row.so_da_tra_loi / row.so_cau_hoi) * 100)
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai) params.trang_thai = filters.trang_thai
    if (filters.khoang_ngay?.length === 2) {
      ;[params.tu_ngay, params.den_ngay] = filters.khoang_ngay
    }
    const data = await fetchLichSuKhaoSat(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được lịch sử trắc nghiệm'))
  } finally {
    loading.value = false
  }
}

function onPageChange() {
  load()
}

function onSizeChange() {
  page.value = 1
  load()
}

function onSearch() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

function onResetFilters() {
  Object.assign(filters, emptyFilters())
  onSearch()
}

function xemKetQua(row) {
  router.push({ name: 'thpt-thi-dai-hoc-ket-qua', params: { ssid: row.ssid } })
}

function xemNganhPhuHop(row) {
  router.push({ name: 'thpt-thi-dai-hoc-nganh-phu-hop', params: { ssid: row.ssid } })
}

function lamTiep(row) {
  router.push({
    name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    params: { ssid: row.ssid, loaiCauHoiId: row.loai_cau_hoi_id_tiep },
  })
}

onMounted(load)
</script>

<style scoped>
.history-card {
  border-radius: 12px;
}

.history-card__title {
  margin: 0 0 4px;
  font-size: 20px;
  line-height: 1.4;
}

.history-card__lead {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
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

.filter-date {
  max-width: 280px;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.row-actions :deep(.el-icon) {
  font-size: 20px !important;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 767px) {
  .filter-search,
  .filter-status,
  .filter-date {
    width: 100%;
    max-width: none;
  }
}
</style>
