<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Tìm mã, tên gói cước, ghi chú"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect
        v-model="filters.loai_ap_dung"
        class="filter-status"
        placeholder="Loại áp dụng"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="item in LOAI_AP_DUNG" :key="item.value" :label="item.label" :value="item.value" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.trang_thai"
        class="filter-status"
        placeholder="Trạng thái"
        clearable
        @change="onSearch"
      >
        <CustomOption label="Hoạt động" :value="1" />
        <CustomOption label="Ngừng sử dụng" :value="0" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.co_khuyen_mai"
        class="filter-status"
        placeholder="Khuyến mãi"
        clearable
        @change="onSearch"
      >
        <CustomOption label="Có khuyến mãi" :value="true" />
        <CustomOption label="Không khuyến mãi" :value="false" />
      </CustomSelect>
      <div class="filter-gia">
        <CustomInputNumber
          v-model="filters.gia_tu"
          :min="0"
          :max="GIA_TOI_DA"
          :precision="0"
          :step="1000"
          :controls="false"
          placeholder="Giá gốc từ"
          aria-label="Giá gốc từ"
          @keyup.enter="onSearch"
        />
        <span class="filter-gia__sep">–</span>
        <CustomInputNumber
          v-model="filters.gia_den"
          :min="0"
          :max="GIA_TOI_DA"
          :precision="0"
          :step="1000"
          :controls="false"
          placeholder="Giá gốc đến"
          aria-label="Giá gốc đến"
          @keyup.enter="onSearch"
        />
      </div>
      <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      <CustomButton @click="onResetFilters">
        <CustomIcon><RefreshLeft /></CustomIcon>
        <span>Đặt lại</span>
      </CustomButton>
    </div>
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Danh sách gói cước</h2>
      <div class="toolbar__actions">
        <CustomBadge :value="selectedRows.length" :hidden="!selectedRows.length" type="danger">
          <CustomButton
            type="danger"
            plain
            :disabled="!selectedRows.length"
            :loading="deleting"
            @click="onDeleteSelected"
          >
            <CustomIcon><Delete /></CustomIcon>
            Xóa
          </CustomButton>
        </CustomBadge>
        <CustomButton type="primary" @click="openCreate">
          <CustomIcon><Plus /></CustomIcon>
          Thêm gói cước
        </CustomButton>
      </div>
    </div>

    <CustomTable
      ref="tableRef"
      :loading="loading"
      :data="rows"
      row-key="id"
      stripe
      border
      @selection-change="onSelectionChange"
    >
      <CustomTableColumn type="selection" width="48" reserve-selection align="center" />
      <CustomTableColumn label="STT" width="72" align="center">
        <template #default="{ $index }">{{ rowIndex($index) }}</template>
      </CustomTableColumn>
      <CustomTableColumn prop="ma_goi_cuoc" label="Mã gói" width="130" />
      <CustomTableColumn prop="ten_goi_cuoc" label="Tên gói cước" min-width="200" />
      <CustomTableColumn label="Loại áp dụng" width="130" align="center">
        <template #default="{ row }">
          <CustomTag :type="loaiApDung(row.loai_ap_dung).tag" effect="light">
            {{ loaiApDung(row.loai_ap_dung).label }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <!-- Có khuyến mãi: giá trị gốc gạch ngang, chữ nhỏ; giá trị khuyến mãi in đậm. Không có thì chỉ hiện giá trị gốc. -->
      <CustomTableColumn label="Giá" width="150" align="right">
        <template #default="{ row }">
          <div class="gia-tri">
            <template v-if="coGiaTri(row.gia_khuyen_mai)">
              <span class="gia-tri__goc">{{ formatTien(row.gia_goc) }}</span>
              <span class="gia-tri__km">{{ formatTien(row.gia_khuyen_mai) }}</span>
            </template>
            <span v-else>{{ formatTien(row.gia_goc) }}</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Số lượt" width="120" align="center">
        <template #default="{ row }">
          <div class="gia-tri">
            <template v-if="coGiaTri(row.so_luot_nhan_duoc_khuyen_mai)">
              <span class="gia-tri__goc">{{ formatSo(row.so_luot_nhan_duoc_goc) }}</span>
              <span class="gia-tri__km">{{ formatSo(row.so_luot_nhan_duoc_khuyen_mai) }}</span>
            </template>
            <span v-else>{{ formatSo(row.so_luot_nhan_duoc_goc) }}</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="180">
        <template #default="{ row }">{{ row.ghi_chu || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" width="150" align="center">
        <template #default="{ row }">
          <CustomSwitch
            :model-value="row.trang_thai"
            :active-value="1"
            :inactive-value="0"
            active-text="Hoạt động"
            inactive-text="Ngừng"
            :loading="!!dangDoiTrangThai[row.id]"
            :before-change="() => doiTrangThai(row)"
            :aria-label="`Trạng thái ${row.ten_goi_cuoc}`"
          />
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <CustomTooltip content="Sửa" placement="top">
              <CustomButton link type="primary" aria-label="Sửa" @click="openEdit(row)">
                <CustomIcon><Edit /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip content="Xóa" placement="top">
              <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row)">
                <CustomIcon><Delete /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Chưa có gói cước nào." />
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

  <CustomDialog
    v-model="dialogVisible"
    :title="editingId ? 'Cập nhật gói cước' : 'Thêm gói cước'"
    width="800px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomForm ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem label="Mã gói cước" prop="ma_goi_cuoc">
          <CustomInput v-model="form.ma_goi_cuoc" maxlength="50" placeholder="Ví dụ: TRA_CUU_10" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên gói cước" prop="ten_goi_cuoc">
          <CustomInput v-model="form.ten_goi_cuoc" maxlength="255" placeholder="Ví dụ: Gói tra cứu 10 lượt" />
        </CustomFormItem>
        <CustomFormItem label="Loại áp dụng" prop="loai_ap_dung">
          <CustomSelect v-model="form.loai_ap_dung" :clearable="false">
            <CustomOption v-for="item in LOAI_AP_DUNG" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Trạng thái" prop="trang_thai">
          <CustomSelect v-model="form.trang_thai" :clearable="false">
            <CustomOption label="Hoạt động" :value="1" />
            <CustomOption label="Ngừng sử dụng" :value="0" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Giá gốc (VNĐ)" prop="gia_goc">
          <CustomInputNumber
            v-model="form.gia_goc"
            :min="0"
            :max="GIA_TOI_DA"
            :precision="0"
            :step="1000"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Giá khuyến mãi (VNĐ)" prop="gia_khuyen_mai">
          <CustomInputNumber
            v-model="form.gia_khuyen_mai"
            :min="0"
            :max="GIA_TOI_DA"
            :precision="0"
            :step="1000"
            placeholder="Để trống nếu không khuyến mãi"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Số lượt nhận được (gốc)" prop="so_luot_nhan_duoc_goc">
          <CustomInputNumber
            v-model="form.so_luot_nhan_duoc_goc"
            :min="0"
            :max="LUOT_TOI_DA"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Số lượt nhận được (khuyến mãi)" prop="so_luot_nhan_duoc_khuyen_mai">
          <CustomInputNumber
            v-model="form.so_luot_nhan_duoc_khuyen_mai"
            :min="0"
            :max="LUOT_TOI_DA"
            :precision="0"
            placeholder="Để trống nếu không khuyến mãi"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput
            v-model="form.ghi_chu"
            type="textarea"
            :rows="3"
            maxlength="2000"
            show-word-limit
            placeholder="Điều kiện áp dụng, thời hạn khuyến mãi…"
          />
        </CustomFormItem>
      </div>
    </CustomForm>
    <template #footer>
      <CustomButton @click="dialogVisible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" @click="onSubmit">Lưu</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createCauHinhGoiCuoc,
  deleteCauHinhGoiCuoc,
  deleteCauHinhGoiCuocMany,
  fetchCauHinhGoiCuoc,
  updateCauHinhGoiCuoc,
  updateTrangThaiCauHinhGoiCuoc,
} from '@/api/cauHinhGoiCuoc'

// Giữ khớp với LoaiApDung trong backend/app/schemas/ht_cau_hinh_goi_cuoc.py.
const LOAI_AP_DUNG = [
  { value: 'tra_cuu', label: 'Tra cứu', tag: 'primary' },
  { value: 'khao_sat', label: 'Khảo sát', tag: 'success' },
  { value: 'hoi_dap', label: 'Hỏi đáp', tag: 'warning' },
]
const GIA_TOI_DA = 999_999_999_999
const LUOT_TOI_DA = 1_000_000_000

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const rows = ref([])
const selectedRows = ref([])
const tableRef = ref()
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()
const dangDoiTrangThai = ref({})

const filters = reactive(emptyFilters())

function emptyFilters() {
  return {
    q: '',
    loai_ap_dung: '',
    trang_thai: '',
    co_khuyen_mai: '',
    gia_tu: null,
    gia_den: null,
  }
}

const form = reactive(emptyForm())

function kiemTraGiaKhuyenMai(_rule, value, callback) {
  if (value !== null && value !== undefined && value > (form.gia_goc ?? 0)) {
    callback(new Error('Giá khuyến mãi không được lớn hơn giá gốc'))
    return
  }
  callback()
}

const rules = {
  ma_goi_cuoc: [{ required: true, message: 'Vui lòng nhập mã gói cước', trigger: 'blur' }],
  ten_goi_cuoc: [{ required: true, message: 'Vui lòng nhập tên gói cước', trigger: 'blur' }],
  loai_ap_dung: [{ required: true, message: 'Vui lòng chọn loại áp dụng', trigger: 'change' }],
  gia_goc: [{ required: true, message: 'Vui lòng nhập giá gốc', trigger: 'blur' }],
  gia_khuyen_mai: [{ validator: kiemTraGiaKhuyenMai, trigger: 'blur' }],
  so_luot_nhan_duoc_goc: [{ required: true, message: 'Vui lòng nhập số lượt nhận được', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_goi_cuoc: '',
    ten_goi_cuoc: '',
    loai_ap_dung: 'tra_cuu',
    gia_goc: 0,
    gia_khuyen_mai: null,
    so_luot_nhan_duoc_goc: 0,
    so_luot_nhan_duoc_khuyen_mai: null,
    trang_thai: 1,
    ghi_chu: '',
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  formRef.value?.clearValidate()
}

function loaiApDung(value) {
  return LOAI_AP_DUNG.find((item) => item.value === value) || { label: value || '—', tag: 'info' }
}

function coGiaTri(value) {
  return value !== null && value !== undefined
}

function formatSo(value) {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString('vi-VN')
}

function formatTien(value) {
  if (value === null || value === undefined) return '—'
  return `${formatSo(value)} đ`
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
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.loai_ap_dung) params.loai_ap_dung = filters.loai_ap_dung
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    if (filters.co_khuyen_mai !== '' && filters.co_khuyen_mai !== null) {
      params.co_khuyen_mai = filters.co_khuyen_mai
    }
    if (filters.gia_tu !== null && filters.gia_tu !== undefined) params.gia_tu = filters.gia_tu
    if (filters.gia_den !== null && filters.gia_den !== undefined) params.gia_den = filters.gia_den
    const data = await fetchCauHinhGoiCuoc(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách gói cước'))
  } finally {
    loading.value = false
  }
}

// before-change của switch: gọi API trước và tự gán trạng thái từ kết quả trả về,
// nên luôn trả false để switch không tự lật (lỗi thì giữ nguyên trạng thái cũ).
async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    const data = await updateTrangThaiCauHinhGoiCuoc(row.id, moi)
    row.trang_thai = data.trang_thai
    ElMessage.success(moi === 1 ? `Đã bật "${row.ten_goi_cuoc}"` : `Đã tắt "${row.ten_goi_cuoc}"`)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái'))
  } finally {
    const conLai = { ...dangDoiTrangThai.value }
    delete conLai[row.id]
    dangDoiTrangThai.value = conLai
  }
  return false
}

function onResetFilters() {
  Object.assign(filters, emptyFilters())
  onSearch()
}

function clearSelection() {
  selectedRows.value = []
  tableRef.value?.clearSelection()
}

function onSelectionChange(selection) {
  selectedRows.value = selection
}

function rowIndex(index) {
  return (page.value - 1) * pageSize.value + index + 1
}

function onSearch() {
  clearSelection()
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

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    ma_goi_cuoc: row.ma_goi_cuoc,
    ten_goi_cuoc: row.ten_goi_cuoc,
    loai_ap_dung: row.loai_ap_dung,
    gia_goc: row.gia_goc,
    gia_khuyen_mai: row.gia_khuyen_mai,
    so_luot_nhan_duoc_goc: row.so_luot_nhan_duoc_goc,
    so_luot_nhan_duoc_khuyen_mai: row.so_luot_nhan_duoc_khuyen_mai,
    trang_thai: row.trang_thai,
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_goi_cuoc: form.ma_goi_cuoc.trim(),
    ten_goi_cuoc: form.ten_goi_cuoc.trim(),
    loai_ap_dung: form.loai_ap_dung,
    gia_goc: form.gia_goc ?? 0,
    gia_khuyen_mai: form.gia_khuyen_mai ?? null,
    so_luot_nhan_duoc_goc: form.so_luot_nhan_duoc_goc ?? 0,
    so_luot_nhan_duoc_khuyen_mai: form.so_luot_nhan_duoc_khuyen_mai ?? null,
    trang_thai: form.trang_thai,
    ghi_chu: form.ghi_chu?.trim() || null,
  }
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = payloadFromForm()
    if (editingId.value) {
      await updateCauHinhGoiCuoc(editingId.value, payload)
      ElMessage.success('Đã cập nhật gói cước')
    } else {
      await createCauHinhGoiCuoc(payload)
      ElMessage.success('Đã thêm gói cước')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được gói cước'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`Xóa gói cước "${row.ten_goi_cuoc}"?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  try {
    await deleteCauHinhGoiCuoc(row.id)
    ElMessage.success('Đã xóa gói cước')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được gói cước'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} gói cước đã chọn?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteCauHinhGoiCuocMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} gói cước`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các gói cước đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.filter-status {
  width: 170px;
}

.filter-gia {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.filter-gia :deep(.el-input-number) {
  width: 130px;
}

.gia-tri {
  display: flex;
  flex-direction: column;
  line-height: 1.35;
}

.gia-tri__goc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-decoration: line-through;
}

.gia-tri__km {
  font-weight: 600;
  color: var(--el-color-danger);
}

.filter-gia__sep {
  color: var(--el-text-color-secondary);
}

@media (max-width: 640px) {
  .filter-status,
  .filter-gia {
    width: 100%;
  }

  .filter-gia :deep(.el-input-number) {
    flex: 1;
    width: auto;
  }
}
</style>
