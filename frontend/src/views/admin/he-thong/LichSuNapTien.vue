<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <BoLoc>
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Mã giao dịch, gói, mã tham chiếu, người nạp"
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
        <CustomOption v-for="item in TRANG_THAI_NAP_TIEN" :key="item.value" :label="item.label" :value="item.value" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.loai_ap_dung"
        class="filter-status"
        placeholder="Loại áp dụng"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="item in LOAI_AP_DUNG" :key="item.value" :label="item.label" :value="item.value" />
      </CustomSelect>
      <template #nut>
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        <CustomButton @click="onResetFilters">
          <CustomIcon><RefreshLeft /></CustomIcon>
          <span>Đặt lại</span>
        </CustomButton>
      </template>
    </BoLoc>
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Lịch sử nạp tiền</h2>
    </div>

    <CustomTable :loading="loading" :data="rows" row-key="id" stripe border>
      <CustomTableColumn label="STT" width="64" align="center">
        <template #default="{ $index }">{{ rowIndex($index) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Mã giao dịch" width="150">
        <template #default="{ row }"><strong>{{ row.ma_giao_dich }}</strong></template>
      </CustomTableColumn>
      <CustomTableColumn label="Người nạp" min-width="180">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ row.ho_ten || '—' }}</span>
            <small v-if="row.email">{{ row.email }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Gói" min-width="180">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ row.ten_goi_cuoc }}</span>
            <span>
              <CustomTag :type="loai(row.loai_ap_dung).tag" size="small" effect="light">
                {{ loai(row.loai_ap_dung).label }}
              </CustomTag>
            </span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Nhận được" width="140" align="center">
        <template #default="{ row }">
          {{ hienSo(row.so_luot_nhan_duoc) }} {{ loai(row.loai_ap_dung).donVi || '' }}
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Số tiền" width="150" align="right">
        <template #default="{ row }">
          <div class="cell-stack">
            <strong>{{ hienTien(row.so_tien_nap) }}</strong>
            <small v-if="khacSoTien(row)">Thực nhận: {{ hienTien(row.so_tien_thuc_nhan) }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Ngân hàng" width="150">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ row.ten_ngan_hang_viet_tat || '—' }}</span>
            <small v-if="row.so_tai_khoan_nhan">{{ row.so_tai_khoan_nhan }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Mã tham chiếu" width="140">
        <template #default="{ row }">{{ row.ma_tham_chieu_ngan_hang || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" min-width="160">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>
              <CustomTag :type="trangThai(row.trang_thai).tag" effect="light">
                {{ trangThai(row.trang_thai).label }}
              </CustomTag>
            </span>
            <small v-if="row.ghi_chu">{{ row.ghi_chu }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thời gian" width="210">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ hienThoiGian(row.created_at) }}</span>
            <small v-if="row.thoi_gian_thanh_toan">Báo CK: {{ hienThoiGian(row.thoi_gian_thanh_toan) }}</small>
            <small v-if="row.thoi_gian_xac_nhan">Xác nhận: {{ hienThoiGian(row.thoi_gian_xac_nhan) }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <div v-if="row.trang_thai === 0" class="row-actions">
            <CustomTooltip content="Xác nhận đã nhận tiền" placement="top">
              <CustomButton link type="success" aria-label="Xác nhận" @click="openXacNhan(row)">
                <CustomIcon><CircleCheck /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip content="Từ chối" placement="top">
              <CustomButton link type="danger" aria-label="Từ chối" @click="onTuChoi(row)">
                <CustomIcon><CircleClose /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
          <span v-else class="muted">—</span>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Chưa có giao dịch nạp tiền nào." />
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

  <CustomDialog v-model="dialogVisible" title="Xác nhận đã nhận tiền" width="800px" destroy-on-close @closed="dangXacNhan = null">
    <template v-if="dangXacNhan">
      <dl class="tom-tat">
        <div>
          <dt>Mã giao dịch</dt>
          <dd><strong>{{ dangXacNhan.ma_giao_dich }}</strong></dd>
        </div>
        <div>
          <dt>Người nạp</dt>
          <dd>{{ dangXacNhan.ho_ten || '—' }}<small v-if="dangXacNhan.email"> ({{ dangXacNhan.email }})</small></dd>
        </div>
        <div>
          <dt>Gói</dt>
          <dd>{{ dangXacNhan.ten_goi_cuoc }}</dd>
        </div>
        <div>
          <dt>Số tiền phải nạp</dt>
          <dd><strong>{{ hienTien(dangXacNhan.so_tien_nap) }}</strong></dd>
        </div>
      </dl>
      <p class="canh-bao">
        Xác nhận sẽ cộng {{ hienSo(dangXacNhan.so_luot_nhan_duoc) }} {{ loai(dangXacNhan.loai_ap_dung).donVi || '' }}
        cho người nạp.
      </p>

      <CustomForm ref="formRef" class="form-grid" :model="form" label-position="top">
        <div class="form-grid__body">
          <CustomFormItem label="Số tiền thực nhận (VNĐ)" prop="so_tien_thuc_nhan">
            <CustomInputNumber
              v-model="form.so_tien_thuc_nhan"
              placeholder="Nhập số tiền thực nhận"
              :min="0"
              :precision="0"
              :step="1000"
              controls-position="right"
            />
          </CustomFormItem>
          <CustomFormItem class="form-grid__span-2" label="Mã tham chiếu ngân hàng" prop="ma_tham_chieu_ngan_hang">
            <CustomInput v-model="form.ma_tham_chieu_ngan_hang" maxlength="100" placeholder="Ví dụ: FT24012345678" />
          </CustomFormItem>
          <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
            <CustomInput v-model="form.ghi_chu" placeholder="Nhập ghi chú" type="textarea" :rows="3" maxlength="2000" show-word-limit />
          </CustomFormItem>
        </div>
      </CustomForm>
    </template>
    <template #footer>
      <CustomButton @click="dialogVisible = false">Hủy</CustomButton>
      <CustomButton type="success" :loading="saving" @click="onXacNhan">Xác nhận</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchLichSuNapTien, tuChoiNapTien, xacNhanNapTien } from '@/api/napTien'
import {
  LOAI_AP_DUNG,
  TRANG_THAI_NAP_TIEN,
  hienSo,
  hienThoiGian,
  hienTien,
  timTheoGiaTri,
} from '@/data/napTien'

const loading = ref(false)
const saving = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const dangXacNhan = ref(null)
const formRef = ref()

const filters = reactive(emptyFilters())
const form = reactive({ so_tien_thuc_nhan: null, ma_tham_chieu_ngan_hang: '', ghi_chu: '' })

function emptyFilters() {
  return { q: '', trang_thai: '', loai_ap_dung: '' }
}

function loai(value) {
  return timTheoGiaTri(LOAI_AP_DUNG, value)
}

function trangThai(value) {
  return timTheoGiaTri(TRANG_THAI_NAP_TIEN, value)
}

function khacSoTien(row) {
  return row.so_tien_thuc_nhan !== null && row.so_tien_thuc_nhan !== undefined
    && Number(row.so_tien_thuc_nhan) !== Number(row.so_tien_nap)
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

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai !== '' && filters.trang_thai !== null) params.trang_thai = filters.trang_thai
    if (filters.loai_ap_dung) params.loai_ap_dung = filters.loai_ap_dung
    const data = await fetchLichSuNapTien(params)
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

function openXacNhan(row) {
  dangXacNhan.value = row
  Object.assign(form, {
    so_tien_thuc_nhan: Number(row.so_tien_thuc_nhan ?? row.so_tien_nap) || 0,
    ma_tham_chieu_ngan_hang: row.ma_tham_chieu_ngan_hang || '',
    ghi_chu: '',
  })
  dialogVisible.value = true
}

async function onXacNhan() {
  if (!dangXacNhan.value) return
  saving.value = true
  try {
    await xacNhanNapTien(dangXacNhan.value.id, {
      so_tien_thuc_nhan: form.so_tien_thuc_nhan ?? null,
      ma_tham_chieu_ngan_hang: form.ma_tham_chieu_ngan_hang.trim() || null,
      ghi_chu: form.ghi_chu.trim() || null,
    })
    ElMessage.success(`Đã xác nhận giao dịch ${dangXacNhan.value.ma_giao_dich}`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xác nhận được giao dịch'))
  } finally {
    saving.value = false
  }
}

async function onTuChoi(row) {
  let lyDo
  try {
    const result = await ElMessageBox.prompt(`Lý do từ chối giao dịch ${row.ma_giao_dich}`, 'Từ chối giao dịch', {
      confirmButtonText: 'Từ chối',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
      inputType: 'textarea',
      inputPlaceholder: 'Ví dụ: Không nhận được tiền sau 3 ngày',
      inputValidator: (value) => (String(value || '').trim() ? true : 'Vui lòng nhập lý do từ chối'),
    })
    lyDo = String(result.value).trim()
  } catch {
    return
  }

  try {
    await tuChoiNapTien(row.id, { ghi_chu: lyDo })
    ElMessage.success(`Đã từ chối giao dịch ${row.ma_giao_dich}`)
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không từ chối được giao dịch'))
  }
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

.cell-stack small,
.tom-tat small,
.muted {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.tom-tat {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 12px;
  margin: 0 0 12px;
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--el-fill-color-lighter);
}

.tom-tat dt {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.tom-tat dd {
  margin: 2px 0 0;
  overflow-wrap: anywhere;
}

.canh-bao {
  margin: 0 0 12px;
  color: var(--el-color-warning-dark-2);
  font-size: 13px;
}
</style>
