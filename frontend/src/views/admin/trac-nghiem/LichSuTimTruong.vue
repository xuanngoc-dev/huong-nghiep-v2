<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomInput
        v-model="filters.nguoi_dung"
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
        placeholder="Mã yêu cầu, mã/tên ngành"
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
        <CustomOption label="Thành viên" value="thanh-vien" />
        <CustomOption label="Khách" value="khach" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.nam_tuyen_sinh"
        class="filter-select"
        placeholder="Năm tuyển sinh"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="nam in namOptions" :key="nam" :label="String(nam)" :value="nam" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.trang_thai_xu_ly"
        class="filter-select"
        placeholder="Trạng thái"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="(item, ma) in TRANG_THAI" :key="ma" :label="item.nhan" :value="ma" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.loai_luot"
        class="filter-select"
        placeholder="Loại lượt"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="(item, ma) in LOAI_LUOT" :key="ma" :label="item.nhan" :value="ma" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.da_mo_khoa"
        class="filter-select"
        placeholder="Báo cáo chuyên sâu"
        clearable
        @change="onSearch"
      >
        <CustomOption label="Đã mở khóa" :value="true" />
        <CustomOption label="Chưa mở khóa" :value="false" />
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
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Lịch sử tìm trường</h2>
      <span class="toolbar__count">{{ total.toLocaleString('vi-VN') }} lượt</span>
    </div>

    <CustomTable :loading="loading" :data="rows" row-key="id" stripe border>
      <CustomTableColumn label="STT" width="64" align="center">
        <template #default="{ $index }">{{ rowIndex($index) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Thời gian" width="150">
        <template #default="{ row }">{{ formatThoiGian(row.ngay_tao) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Người tìm" min-width="200">
        <template #default="{ row }">
          <div class="cell-stack">
            <span class="nguoi-tim">
              <strong>{{ row.ho_ten || (row.la_khach ? 'Khách chưa nhập tên' : `#${row.tai_khoan_id}`) }}</strong>
              <CustomTag v-if="row.la_khach" type="info" size="small" effect="plain">Khách</CustomTag>
            </span>
            <span v-if="row.email" class="cell-sub">{{ row.email }}</span>
            <span v-if="row.so_dien_thoai" class="cell-sub">{{ row.so_dien_thoai }}</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Ngành" min-width="200">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ row.ten_nganh || row.ma_nganh }}</span>
            <span class="cell-sub">{{ row.ma_nganh }} · Năm {{ row.nam_tuyen_sinh }}</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Tiêu chí" min-width="220">
        <template #default="{ row }">
          <div v-if="nhanTieuChi(row.tieu_chi_tim_kiem).length" class="tag-list">
            <CustomTag v-for="nhan in nhanTieuChi(row.tieu_chi_tim_kiem)" :key="nhan" size="small" effect="plain">
              {{ nhan }}
            </CustomTag>
          </div>
          <span v-else class="cell-sub">Không lọc</span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Kết quả" width="140" align="center">
        <template #default="{ row }">
          <div class="cell-stack cell-center">
            <strong>{{ row.so_truong_phu_hop_so_bo }} / {{ row.so_truong_tim_thay }}</strong>
            <span class="cell-sub">phù hợp / có ngành</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Loại lượt" width="120" align="center">
        <template #default="{ row }">
          <CustomTag :type="LOAI_LUOT[row.loai_luot]?.mau || 'info'" effect="light">
            {{ LOAI_LUOT[row.loai_luot]?.nhan || row.loai_luot }}
          </CustomTag>
          <span v-if="!row.da_tinh_luot" class="cell-sub d-block">Không tính lượt</span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" width="130" align="center">
        <template #default="{ row }">
          <CustomTooltip :content="row.thong_bao_loi || ''" placement="top" :disabled="!row.thong_bao_loi">
            <CustomTag :type="TRANG_THAI[row.trang_thai_xu_ly]?.mau || 'info'" effect="light">
              {{ TRANG_THAI[row.trang_thai_xu_ly]?.nhan || row.trang_thai_xu_ly }}
            </CustomTag>
          </CustomTooltip>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thao tác" width="90" fixed="right" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <CustomTooltip content="Xem chi tiết" placement="top">
              <CustomButton link type="primary" aria-label="Xem chi tiết" @click="moChiTiet(row)">
                <CustomIcon><View /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Chưa có lượt tìm trường nào." />
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

  <CustomDialog v-model="chiTietMo" title="Chi tiết lượt tìm trường" width="min(860px, 94vw)" destroy-on-close>
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
        <p v-else class="cell-sub">Không lọc</p>

        <h3 class="chi-tiet__title">Dữ liệu năng lực</h3>
        <pre class="chi-tiet__json">{{ hienJson(chiTiet.du_lieu_nang_luc) }}</pre>

        <h3 class="chi-tiet__title">Dữ liệu tài chính</h3>
        <pre class="chi-tiet__json">{{ hienJson(chiTiet.du_lieu_tai_chinh) }}</pre>

        <h3 class="chi-tiet__title">
          Trường phù hợp sơ bộ
          <span class="cell-sub">({{ truongKetQua.length }} trường đầu, tổng {{ chiTiet.so_truong_phu_hop_so_bo }})</span>
        </h3>
        <CustomTable v-if="truongKetQua.length" :data="truongKetQua" size="small" border max-height="280">
          <CustomTableColumn type="index" label="STT" width="60" align="center" />
          <CustomTableColumn prop="ma_truong" label="Mã trường" width="110" />
          <CustomTableColumn prop="ten_truong" label="Tên trường" min-width="240" />
          <CustomTableColumn prop="so_chuong_trinh" label="Chương trình" width="110" align="center" />
        </CustomTable>
        <p v-else class="cell-sub">Không có trường nào.</p>

        <p v-if="chiTiet.thong_bao_loi" class="chi-tiet__loi">Lỗi: {{ chiTiet.thong_bao_loi }}</p>
      </template>
    </div>
    <template #footer>
      <CustomButton @click="chiTietMo = false">Đóng</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchChiTietLichSuTimTruong, fetchLichSuTimTruongQuanTri } from '@/api/timTruongPhuHop'

const TRANG_THAI = {
  cho_xu_ly: { nhan: 'Chờ xử lý', mau: 'info' },
  dang_xu_ly: { nhan: 'Đang xử lý', mau: 'warning' },
  thanh_cong: { nhan: 'Thành công', mau: 'success' },
  that_bai: { nhan: 'Thất bại', mau: 'danger' },
}
const LOAI_LUOT = {
  mien_phi: { nhan: 'Miễn phí', mau: 'info' },
  tra_phi: { nhan: 'Trả phí', mau: 'warning' },
  khuyen_mai: { nhan: 'Khuyến mãi', mau: 'success' },
}
const SAP_XEP = {
  ten_asc: 'Tên A → Z',
  ten_desc: 'Tên Z → A',
  chi_tieu_desc: 'Chỉ tiêu nhiều nhất',
  chuong_trinh_desc: 'Nhiều chương trình nhất',
  gan_toi: 'Gần nơi ở nhất',
}
const NAM_HIEN_TAI = new Date().getFullYear()
const namOptions = Array.from({ length: 6 }, (_, index) => NAM_HIEN_TAI + 1 - index)

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const chiTietMo = ref(false)
const chiTiet = ref(null)
const dangTaiChiTiet = ref(false)

const filters = reactive(emptyFilters())

function emptyFilters() {
  return {
    nguoi_dung: '',
    q: '',
    doi_tuong: '',
    nam_tuyen_sinh: '',
    trang_thai_xu_ly: '',
    loai_luot: '',
    da_mo_khoa: '',
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
    tc.tinh && tc.tinh,
    !tc.tinh && tc.khu_vuc && `Miền ${tc.khu_vuc}`,
    tc.loai_co_so,
    tc.sap_xep && tc.sap_xep !== 'ten_asc' && SAP_XEP[tc.sap_xep],
  ].filter(Boolean)
}

function hienJson(value) {
  if (value == null || (typeof value === 'object' && !Object.keys(value).length)) return 'Không có dữ liệu'
  return JSON.stringify(value, null, 2)
}

const truongKetQua = computed(() => chiTiet.value?.du_lieu_ket_qua?.truong || [])

const thongTinChung = computed(() => {
  const item = chiTiet.value
  if (!item) return []
  return [
    { nhan: 'Mã yêu cầu', giaTri: item.ma_yeu_cau },
    {
      nhan: 'Người tìm',
      giaTri:
        [item.la_khach ? 'Khách' : '', item.ho_ten, item.email, item.so_dien_thoai].filter(Boolean).join(' · ') ||
        `#${item.tai_khoan_id}`,
    },
    { nhan: 'Mã thiết bị', giaTri: item.la_khach ? item.ma_thiet_bi : '' },
    { nhan: 'Ngành', giaTri: `${item.ma_nganh}${item.ten_nganh ? ` · ${item.ten_nganh}` : ''}` },
    { nhan: 'Năm tuyển sinh', giaTri: String(item.nam_tuyen_sinh) },
    { nhan: 'Thời gian tạo', giaTri: formatThoiGian(item.ngay_tao) },
    { nhan: 'Hoàn thành', giaTri: item.ngay_hoan_thanh ? formatThoiGian(item.ngay_hoan_thanh) : '' },
    { nhan: 'Trạng thái', giaTri: TRANG_THAI[item.trang_thai_xu_ly]?.nhan || item.trang_thai_xu_ly },
    {
      nhan: 'Loại lượt',
      giaTri: `${LOAI_LUOT[item.loai_luot]?.nhan || item.loai_luot}${item.da_tinh_luot ? '' : ' (không tính lượt)'}`,
    },
    { nhan: 'Kết quả', giaTri: `${item.so_truong_phu_hop_so_bo} phù hợp / ${item.so_truong_tim_thay} có ngành` },
    {
      nhan: 'Báo cáo chuyên sâu',
      giaTri: item.da_mo_khoa_chuyen_sau
        ? `Đã mở khóa${item.ngay_mo_khoa ? ` lúc ${formatThoiGian(item.ngay_mo_khoa)}` : ''}`
        : 'Chưa mở khóa',
    },
    { nhan: 'Phiên bản thuật toán', giaTri: item.phien_ban_thuat_toan },
  ]
})

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
    if (filters.nguoi_dung.trim()) params.nguoi_dung = filters.nguoi_dung.trim()
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.doi_tuong) params.doi_tuong = filters.doi_tuong
    if (filters.nam_tuyen_sinh) params.nam_tuyen_sinh = filters.nam_tuyen_sinh
    if (filters.trang_thai_xu_ly) params.trang_thai_xu_ly = filters.trang_thai_xu_ly
    if (filters.loai_luot) params.loai_luot = filters.loai_luot
    if (filters.da_mo_khoa !== '' && filters.da_mo_khoa !== null) params.da_mo_khoa = filters.da_mo_khoa
    if (filters.khoang_ngay?.length === 2) {
      ;[params.tu_ngay, params.den_ngay] = filters.khoang_ngay
    }
    const data = await fetchLichSuTimTruongQuanTri(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được lịch sử tìm trường'))
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

function onResetFilters() {
  Object.assign(filters, emptyFilters())
  onSearch()
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

async function moChiTiet(row) {
  chiTiet.value = null
  chiTietMo.value = true
  dangTaiChiTiet.value = true
  try {
    chiTiet.value = await fetchChiTietLichSuTimTruong(row.id)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được chi tiết lượt tìm'))
    chiTietMo.value = false
  } finally {
    dangTaiChiTiet.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.filter-code {
  width: 210px;
}

.filter-select {
  width: 160px;
}

.filter-date {
  max-width: 240px;
}

.toolbar__count {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.nguoi-tim {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.cell-center {
  align-items: center;
}

.d-block {
  display: block;
  margin-top: 2px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
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
  grid-template-columns: 140px minmax(0, 1fr);
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

.chi-tiet__json {
  max-height: 200px;
  margin: 0;
  padding: 10px 12px;
  overflow: auto;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  background: var(--el-fill-color-lighter);
  font-family: ui-monospace, Consolas, monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.chi-tiet__loi {
  margin: 12px 0 0;
  color: var(--el-color-danger);
}

@media (max-width: 640px) {
  .filter-code,
  .filter-select,
  .filter-date {
    width: 100%;
    max-width: none;
  }

  .chi-tiet__grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .chi-tiet__row {
    grid-template-columns: 120px minmax(0, 1fr);
  }
}
</style>
