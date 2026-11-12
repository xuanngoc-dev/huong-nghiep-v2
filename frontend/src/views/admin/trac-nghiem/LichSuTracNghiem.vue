<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomInput
        v-model="filters.nguoi_tham_gia"
        class="filter-search"
        placeholder="Tên, email, SĐT"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><User /></CustomIcon>
        </template>
      </CustomInput>
      <CustomInput
        v-model="filters.q"
        class="filter-code"
        placeholder="Mã giao dịch, mã phiên"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect
        v-model="filters.doi_tuong"
        class="filter-select"
        placeholder="Đối tượng"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="item in DOI_TUONG_OPTIONS" :key="item.value" :label="item.label" :value="item.value" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.trang_thai"
        class="filter-select"
        placeholder="Tình trạng"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="item in TRANG_THAI_OPTIONS" :key="item.value" :label="item.label" :value="item.value" />
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
    </div>
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Lịch sử trắc nghiệm</h2>
      <span class="toolbar__count">{{ total.toLocaleString('vi-VN') }} phiên</span>
    </div>

    <CustomTable :loading="loading" :data="rows" row-key="id" stripe border>
      <CustomTableColumn label="STT" width="64" align="center">
        <template #default="{ $index }">{{ rowIndex($index) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Mã giao dịch" min-width="170">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ row.ma_giao_dich || '—' }}</span>
            <span class="cell-sub cell-ssid">
              {{ row.ssid }}
              <CustomButton link type="primary" aria-label="Sao chép mã phiên" @click="copySsid(row)">
                <CustomIcon><CopyDocument /></CustomIcon>
              </CustomButton>
            </span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Người tham gia" min-width="220">
        <template #default="{ row }">
          <div v-if="row.nguoi_khao_sat_id" class="cell-stack">
            <strong>{{ row.ho_ten || `#${row.nguoi_khao_sat_id}` }}</strong>
            <span v-if="row.email" class="cell-sub">{{ row.email }}</span>
            <span v-if="row.so_dien_thoai" class="cell-sub">{{ row.so_dien_thoai }}</span>
          </div>
          <CustomTag v-else type="info" effect="plain">Khách</CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thời gian" width="150">
        <template #default="{ row }">{{ formatThoiGian(row.created_at) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Tiến độ" min-width="170">
        <template #default="{ row }">
          <el-progress :percentage="tienDo(row)" :status="row.da_xong ? 'success' : ''" />
          <span class="cell-sub">{{ row.so_da_tra_loi }}/{{ row.so_cau_hoi }} câu</span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Mã Holland" width="110" align="center">
        <template #default="{ row }">
          <CustomTag v-if="row.ma_noi_bat" type="primary">{{ row.ma_noi_bat }}</CustomTag>
          <span v-else>—</span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Tình trạng" width="150" align="center">
        <template #default="{ row }">
          <CustomTag :type="row.da_xong ? 'success' : 'warning'" effect="light">
            {{ row.da_xong ? 'Hoàn thành' : 'Chưa hoàn thành' }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <div v-if="row.da_xong" class="row-actions">
            <CustomTooltip content="Xem kết quả" placement="top">
              <CustomButton
                link
                type="primary"
                aria-label="Xem kết quả"
                @click="moTab('thpt-thi-dai-hoc-ket-qua', row)"
              >
                <CustomIcon><DataAnalysis /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip content="Ngành phù hợp" placement="top">
              <CustomButton
                link
                type="primary"
                aria-label="Ngành phù hợp"
                @click="moTab('thpt-thi-dai-hoc-nganh-phu-hop', row)"
              >
                <CustomIcon><School /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
          <span v-else class="cell-sub">—</span>
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
  </CustomCard>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchPhienKhaoSatQuanTri } from '@/api/phienKhaoSat'

const TRANG_THAI_OPTIONS = [
  { value: 'hoan-thanh', label: 'Hoàn thành' },
  { value: 'dang-lam', label: 'Chưa hoàn thành' },
]
const DOI_TUONG_OPTIONS = [
  { value: 'thanh-vien', label: 'Thành viên' },
  { value: 'khach', label: 'Khách' },
]

const router = useRouter()
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filters = reactive(emptyFilters())

function emptyFilters() {
  return {
    q: '',
    nguoi_tham_gia: '',
    doi_tuong: '',
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

function rowIndex(index) {
  return (page.value - 1) * pageSize.value + index + 1
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.nguoi_tham_gia.trim()) params.nguoi_tham_gia = filters.nguoi_tham_gia.trim()
    if (filters.doi_tuong) params.doi_tuong = filters.doi_tuong
    if (filters.trang_thai) params.trang_thai = filters.trang_thai
    if (filters.khoang_ngay?.length === 2) {
      ;[params.tu_ngay, params.den_ngay] = filters.khoang_ngay
    }
    const data = await fetchPhienKhaoSatQuanTri(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được lịch sử trắc nghiệm'))
  } finally {
    loading.value = false
  }
}

function onSearch() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

function onPageChange() {
  load()
}

function onSizeChange() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

// Trang kết quả nằm ở giao diện khách, mở tab mới để không rời trang quản trị.
function moTab(name, row) {
  const href = router.resolve({ name, params: { ssid: row.ssid } }).href
  window.open(href, '_blank', 'noopener')
}

async function copySsid(row) {
  try {
    await navigator.clipboard.writeText(row.ssid)
    ElMessage.success('Đã sao chép mã phiên')
  } catch {
    ElMessage.error('Không sao chép được mã phiên')
  }
}

onMounted(load)
</script>

<style scoped>
.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.filter-code {
  width: 190px;
}

.filter-select {
  width: 140px;
}

.filter-date {
  max-width: 240px;
}

.toolbar__count {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.cell-ssid {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: ui-monospace, Consolas, monospace;
}

@media (max-width: 640px) {
  .filter-code,
  .filter-select,
  .filter-date {
    width: 100%;
    max-width: none;
  }
}
</style>
