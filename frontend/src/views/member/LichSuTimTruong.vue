<template>
  <el-card v-loading="loading" shadow="never" class="history-card">
    <template #header>
      <div>
        <h1 class="history-card__title">Lịch sử tìm trường</h1>
      </div>
    </template>

    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Tìm mã hoặc tên ngành"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect
        v-model="filters.nam_tuyen_sinh"
        class="filter-status"
        placeholder="Năm tuyển sinh"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="nam in namOptions" :key="nam" :label="String(nam)" :value="nam" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.trang_thai_xu_ly"
        class="filter-status"
        placeholder="Trạng thái"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="(item, ma) in TRANG_THAI" :key="ma" :label="item.nhan" :value="ma" />
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
      <CustomTableColumn label="Thời gian" min-width="150">
        <template #default="{ row }">{{ formatThoiGian(row.ngay_tao) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Ngành" min-width="200">
        <template #default="{ row }">
          <div class="history-card__stack">
            <span>{{ row.ten_nganh || row.ma_nganh }}</span>
            <span class="history-card__sub">{{ row.ma_nganh }} · Năm {{ row.nam_tuyen_sinh }}</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Tiêu chí" min-width="200">
        <template #default="{ row }">
          <div v-if="nhanTieuChi(row.tieu_chi_tim_kiem).length" class="tag-list">
            <CustomTag v-for="nhan in nhanTieuChi(row.tieu_chi_tim_kiem)" :key="nhan" size="small" effect="plain">
              {{ nhan }}
            </CustomTag>
          </div>
          <span v-else class="history-card__sub">Không lọc</span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Trường phù hợp" width="140" align="center">
        <template #default="{ row }">
          <strong>{{ row.so_truong_phu_hop_so_bo }}</strong>
          <span class="history-card__sub"> / {{ row.so_truong_tim_thay }} trường</span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" width="130" align="center">
        <template #default="{ row }">
          <CustomTag :type="TRANG_THAI[row.trang_thai_xu_ly]?.mau || 'info'">
            {{ TRANG_THAI[row.trang_thai_xu_ly]?.nhan || row.trang_thai_xu_ly }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thao tác" width="110" fixed="right" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <CustomTooltip content="Xem chi tiết" placement="top">
              <CustomButton link type="primary" aria-label="Xem chi tiết" @click="moChiTiet(row)">
                <CustomIcon><View /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip content="Tìm lại ngành này" placement="top">
              <CustomButton link type="primary" aria-label="Tìm lại ngành này" @click="timLai(row)">
                <CustomIcon><School /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Bạn chưa tìm trường phù hợp lần nào." />
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

  <CustomDialog v-model="chiTietMo" title="Chi tiết lượt tìm trường" width="min(760px, 94vw)" destroy-on-close>
    <div v-loading="dangTaiChiTiet" class="chi-tiet">
      <template v-if="chiTiet">
        <dl class="chi-tiet__grid">
          <div v-for="dong in thongTinChung" :key="dong.nhan" class="chi-tiet__row">
            <dt>{{ dong.nhan }}</dt>
            <dd>{{ dong.giaTri || '—' }}</dd>
          </div>
        </dl>

        <h3 class="chi-tiet__title">Tiêu chí tìm kiếm</h3>
        <div v-if="nhanTieuChi(chiTiet.tieu_chi_tim_kiem).length" class="tag-list">
          <CustomTag v-for="nhan in nhanTieuChi(chiTiet.tieu_chi_tim_kiem)" :key="nhan" effect="plain">{{ nhan }}</CustomTag>
        </div>
        <p v-else class="history-card__sub">Không lọc</p>

        <h3 class="chi-tiet__title">
          Trường phù hợp sơ bộ
          <span class="history-card__sub">({{ chiTiet.so_truong_phu_hop_so_bo }} trường)</span>
        </h3>
        <CustomTable v-if="truongKetQua.length" :data="truongKetQua" size="small" border max-height="300">
          <CustomTableColumn type="index" label="STT" width="60" align="center" />
          <CustomTableColumn prop="ma_truong" label="Mã trường" width="110" />
          <CustomTableColumn prop="ten_truong" label="Tên trường" min-width="220" />
          <CustomTableColumn prop="so_chuong_trinh" label="Chương trình" width="110" align="center" />
        </CustomTable>
        <p v-else class="history-card__sub">Không có trường nào khớp tiêu chí.</p>
        <p v-if="chiTiet.so_truong_phu_hop_so_bo > truongKetQua.length" class="history-card__sub chi-tiet__note">
          Chỉ lưu {{ truongKetQua.length }} trường đầu. Bấm “Tìm lại” để xem đầy đủ danh sách hiện tại.
        </p>
      </template>
    </div>
    <template #footer>
      <CustomButton @click="chiTietMo = false">Đóng</CustomButton>
      <CustomButton v-if="chiTiet" type="primary" @click="timLai(chiTiet)">Tìm lại</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchChiTietLichSuTimTruongCuaToi, fetchLichSuTimTruongCuaToi } from '@/api/timTruongPhuHop'

const TRANG_THAI = {
  cho_xu_ly: { nhan: 'Chờ xử lý', mau: 'info' },
  dang_xu_ly: { nhan: 'Đang xử lý', mau: 'warning' },
  thanh_cong: { nhan: 'Thành công', mau: 'success' },
  that_bai: { nhan: 'Thất bại', mau: 'danger' },
}
const SAP_XEP = {
  ten_desc: 'Tên Z → A',
  chi_tieu_desc: 'Chỉ tiêu nhiều nhất',
  chuong_trinh_desc: 'Nhiều chương trình nhất',
  gan_toi: 'Gần nơi ở nhất',
}
const NAM_HIEN_TAI = new Date().getFullYear()
const namOptions = Array.from({ length: 6 }, (_, index) => NAM_HIEN_TAI + 1 - index)

const router = useRouter()
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const chiTietMo = ref(false)
const chiTiet = ref(null)
const dangTaiChiTiet = ref(false)

const filters = reactive(emptyFilters())

function emptyFilters() {
  return {
    q: '',
    nam_tuyen_sinh: '',
    trang_thai_xu_ly: '',
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

function nhanTieuChi(tc) {
  if (!tc) return []
  return [
    tc.tu_khoa && `Từ khóa: ${tc.tu_khoa}`,
    tc.tinh,
    !tc.tinh && tc.khu_vuc && `Miền ${tc.khu_vuc}`,
    tc.loai_co_so,
    SAP_XEP[tc.sap_xep],
  ].filter(Boolean)
}

const truongKetQua = computed(() => chiTiet.value?.du_lieu_ket_qua?.truong || [])

const thongTinChung = computed(() => {
  const item = chiTiet.value
  if (!item) return []
  return [
    { nhan: 'Ngành', giaTri: `${item.ma_nganh}${item.ten_nganh ? ` · ${item.ten_nganh}` : ''}` },
    { nhan: 'Năm tuyển sinh', giaTri: String(item.nam_tuyen_sinh) },
    { nhan: 'Thời gian', giaTri: formatThoiGian(item.ngay_tao) },
    { nhan: 'Trạng thái', giaTri: TRANG_THAI[item.trang_thai_xu_ly]?.nhan || item.trang_thai_xu_ly },
    { nhan: 'Trường có ngành', giaTri: `${item.so_truong_tim_thay} trường` },
    { nhan: 'Phù hợp sơ bộ', giaTri: `${item.so_truong_phu_hop_so_bo} trường` },
  ]
})

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.nam_tuyen_sinh) params.nam_tuyen_sinh = filters.nam_tuyen_sinh
    if (filters.trang_thai_xu_ly) params.trang_thai_xu_ly = filters.trang_thai_xu_ly
    if (filters.khoang_ngay?.length === 2) {
      ;[params.tu_ngay, params.den_ngay] = filters.khoang_ngay
    }
    const data = await fetchLichSuTimTruongCuaToi(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được lịch sử tìm trường'))
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

async function moChiTiet(row) {
  chiTiet.value = null
  chiTietMo.value = true
  dangTaiChiTiet.value = true
  try {
    chiTiet.value = await fetchChiTietLichSuTimTruongCuaToi(row.id)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được chi tiết lượt tìm'))
    chiTietMo.value = false
  } finally {
    dangTaiChiTiet.value = false
  }
}

// Mở lại trang Trường phù hợp của ngành; tìm lại ở đó mới tính lượt.
function timLai(row) {
  chiTietMo.value = false
  router.push({ name: 'thpt-thi-dai-hoc-truong-phu-hop', params: { maNganh: row.ma_nganh } })
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

.history-card__sub {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.history-card__stack {
  display: flex;
  flex-direction: column;
  line-height: 1.4;
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

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
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

.chi-tiet {
  min-height: 120px;
}

.chi-tiet__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 24px;
  margin: 0 0 8px;
}

.chi-tiet__row {
  display: grid;
  grid-template-columns: 130px minmax(0, 1fr);
  gap: 8px;
}

.chi-tiet__row dt {
  color: var(--el-text-color-secondary);
  font-weight: 400;
}

.chi-tiet__row dd {
  margin: 0;
  overflow-wrap: anywhere;
}

.chi-tiet__title {
  margin: 16px 0 8px;
  font-size: 14px;
  font-weight: 600;
}

.chi-tiet__note {
  margin: 8px 0 0;
}

@media (max-width: 767px) {
  .filter-search,
  .filter-status,
  .filter-date {
    width: 100%;
    max-width: none;
  }

  .chi-tiet__grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
