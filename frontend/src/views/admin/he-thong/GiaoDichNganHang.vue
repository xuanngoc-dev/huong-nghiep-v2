<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Nội dung, mô tả, mã thanh toán, mã tham chiếu"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect v-model="filters.loai_giao_dich" class="filter-status" placeholder="Loại" clearable @change="onSearch">
        <CustomOption label="Tiền vào" value="in" />
        <CustomOption label="Tiền ra" value="out" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.trang_thai_doi_soat"
        class="filter-status"
        placeholder="Đối soát"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="item in TRANG_THAI_DOI_SOAT" :key="item.value" :label="item.label" :value="item.value" />
      </CustomSelect>
      <CustomInput
        v-model="filters.so_tai_khoan"
        class="filter-status"
        placeholder="Số tài khoản"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      />
      <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      <CustomButton @click="onResetFilters">
        <CustomIcon><RefreshLeft /></CustomIcon>
        <span>Đặt lại</span>
      </CustomButton>
    </div>
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Giao dịch ngân hàng</h2>
    </div>

    <!-- Hướng dẫn cấu hình webhook ở cổng thanh toán (SePay). -->
    <!-- <div class="webhook-guide">
      <p>
        URL webhook:
        <code>{{ webhookUrl }}</code>
        <CustomButton link type="primary" aria-label="Sao chép URL webhook" @click="saoChep(webhookUrl)">
          <CustomIcon><CopyDocument /></CustomIcon>
        </CustomButton>
      </p>
      <p>
        Header xác thực: <code>Authorization: Apikey &lt;WEBHOOK_NGAN_HANG_API_KEY&gt;</code> (khóa đặt trong
        <code>backend/.env</code>; để trống thì webhook không xác thực, chỉ dùng cho hệ thống test). Tiền vào có mã giao dịch nạp tiền (dạng DH4K9F7Q) trong nội dung sẽ được đối soát tự động.
      </p>
    </div> -->

    <CustomTable :loading="loading" :data="rows" row-key="id" stripe border>
      <CustomTableColumn label="STT" width="64" align="center">
        <template #default="{ $index }">{{ rowIndex($index) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Thời gian GD" width="170">
        <template #default="{ row }">{{ hienThoiGian(row.thoi_gian_giao_dich) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Ngân hàng" width="150">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ row.ngan_hang || '—' }}</span>
            <small v-if="row.so_tai_khoan">{{ row.so_tai_khoan }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Loại" width="100" align="center">
        <template #default="{ row }">
          <CustomTag :type="row.loai_giao_dich === 'in' ? 'success' : 'info'" effect="light">
            {{ row.loai_giao_dich === 'in' ? 'Tiền vào' : 'Tiền ra' }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Số tiền" width="160" align="right">
        <template #default="{ row }">
          <div class="cell-stack">
            <strong :class="row.loai_giao_dich === 'in' ? 'tien-vao' : 'tien-ra'">
              {{ row.loai_giao_dich === 'in' ? '+' : '-' }}{{ hienTien(row.so_tien) }}
            </strong>
            <small v-if="row.so_du_luy_ke !== null && row.so_du_luy_ke !== undefined">
              Số dư: {{ hienTien(row.so_du_luy_ke) }}
            </small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Nội dung" min-width="240" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ row.noi_dung || '—' }}</span>
            <small v-if="row.mo_ta">{{ row.mo_ta }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Mã tham chiếu" width="150">
        <template #default="{ row }">{{ row.ma_tham_chieu || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Đối soát" min-width="200">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>
              <CustomTag :type="doiSoat(row.trang_thai_doi_soat).tag" effect="light">
                {{ doiSoat(row.trang_thai_doi_soat).label }}
              </CustomTag>
            </span>
            <strong v-if="row.ma_giao_dich_nap_tien" class="ma-nap">{{ row.ma_giao_dich_nap_tien }}</strong>
            <small v-if="row.ghi_chu_doi_soat">{{ row.ghi_chu_doi_soat }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Chưa có giao dịch ngân hàng nào." />
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
  </CustomCard>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { apiBaseUrl } from '@/api/apiUrl'
import { fetchGiaoDichNganHang } from '@/api/napTien'
import { TRANG_THAI_DOI_SOAT, hienThoiGian, hienTien, timTheoGiaTri } from '@/data/napTien'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filters = reactive(emptyFilters())

// Base API có thể là đường dẫn tương đối (/api/v1) khi chạy cùng domain: ghép origin trang hiện tại.
const webhookUrl = (() => {
  const base = apiBaseUrl()
  const full = /^https?:\/\//i.test(base) ? base : `${window.location.origin}${base.startsWith('/') ? '' : '/'}${base}`
  return `${full}/webhook/giao-dich-ngan-hang`
})()

function emptyFilters() {
  return { q: '', loai_giao_dich: '', trang_thai_doi_soat: '', so_tai_khoan: '' }
}

function doiSoat(value) {
  return timTheoGiaTri(TRANG_THAI_DOI_SOAT, value)
}

function rowIndex(index) {
  return (page.value - 1) * pageSize.value + index + 1
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function saoChep(text) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('Đã sao chép URL webhook')
  } catch {
    ElMessage.error('Không sao chép được')
  }
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.loai_giao_dich) params.loai_giao_dich = filters.loai_giao_dich
    if (filters.trang_thai_doi_soat !== '' && filters.trang_thai_doi_soat !== null) {
      params.trang_thai_doi_soat = filters.trang_thai_doi_soat
    }
    if (filters.so_tai_khoan.trim()) params.so_tai_khoan = filters.so_tai_khoan.trim()
    const data = await fetchGiaoDichNganHang(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được giao dịch ngân hàng'))
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
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

onMounted(load)
</script>

<style scoped>
.cell-stack {
  display: flex;
  flex-direction: column;
  gap: 2px;
  line-height: 1.4;
}

.cell-stack small {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.tien-vao {
  color: var(--el-color-success);
}

.tien-ra {
  color: var(--el-color-danger);
}

.ma-nap {
  font-size: 13px;
}

.webhook-guide {
  margin-bottom: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--el-fill-color-lighter);
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.webhook-guide p {
  margin: 0;
  overflow-wrap: anywhere;
}

.webhook-guide code {
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
}
</style>
