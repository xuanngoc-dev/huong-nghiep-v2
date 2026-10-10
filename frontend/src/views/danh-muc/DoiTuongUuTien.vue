<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createDoiTuongUuTien,
  createDoiTuongUuTienBulk,
  deleteDoiTuongUuTien,
  deleteDoiTuongUuTienMany,
  fetchDoiTuongUuTien,
  updateDoiTuongUuTien,
} from '@/api/doiTuongUuTien'

const JSON_SAMPLE = `[
  {
    "ma_doi_tuong": "01",
    "ten_doi_tuong": "Đối tượng 01",
    "diem_cong": 2,
    "trang_thai": 1
  },
  {
    "ma_doi_tuong": "05",
    "ten_doi_tuong": "Đối tượng 05",
    "diem_cong": 1
  },
  {
    "ma_doi_tuong": "00",
    "ten_doi_tuong": "Không ưu tiên",
    "diem_cong": 0,
    "ghi_chu": "Không thuộc đối tượng ưu tiên"
  }
]`

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
const createMode = ref('form')
const jsonText = ref('')
const formRef = ref()

const filters = reactive({
  q: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

const rules = {
  ten_doi_tuong: [{ required: true, message: 'Vui lòng nhập tên đối tượng', trigger: 'blur' }],
  ma_doi_tuong: [{ required: true, message: 'Vui lòng nhập mã đối tượng', trigger: 'blur' }],
  diem_cong: [{ required: true, message: 'Vui lòng nhập điểm cộng', trigger: 'change' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_doi_tuong: '',
    ten_doi_tuong: '',
    diem_cong: 0,
    trang_thai: 1,
    ghi_chu: '',
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  formRef.value?.clearValidate()
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng đối tượng ưu tiên.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_doi_tuong": "...", "ma_doi_tuong": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng đối tượng ưu tiên đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một đối tượng ưu tiên`)
    }
    const tenDoiTuong = String(item.ten_doi_tuong ?? '').trim()
    const maDoiTuong = String(item.ma_doi_tuong ?? '').trim()
    if (!tenDoiTuong || !maDoiTuong) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_doi_tuong hoặc ma_doi_tuong`)
    }
    return {
      ten_doi_tuong: tenDoiTuong,
      ma_doi_tuong: maDoiTuong,
      diem_cong: item.diem_cong ?? 0,
      trang_thai: item.trang_thai ?? 1,
      ghi_chu: item.ghi_chu == null ? null : String(item.ghi_chu).trim() || null,
    }
  })
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function formatScore(value) {
  if (value === null || value === undefined || value === '') return '—'
  return Number(value).toLocaleString('vi-VN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchDoiTuongUuTien(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách đối tượng ưu tiên'))
  } finally {
    loading.value = false
  }
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
    ma_doi_tuong: row.ma_doi_tuong,
    ten_doi_tuong: row.ten_doi_tuong,
    diem_cong: row.diem_cong,
    trang_thai: row.trang_thai,
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_doi_tuong: form.ma_doi_tuong.trim().toUpperCase(),
    ten_doi_tuong: form.ten_doi_tuong.trim(),
    diem_cong: form.diem_cong ?? 0,
    trang_thai: form.trang_thai,
    ghi_chu: form.ghi_chu?.trim() || null,
  }
}

function fillJsonSample() {
  jsonText.value = JSON_SAMPLE
}

async function onSubmitJson() {
  let items
  try {
    items = parseJsonItems(jsonText.value)
  } catch (error) {
    ElMessage.error(error.message)
    return
  }

  saving.value = true
  try {
    const result = await createDoiTuongUuTienBulk(items)
    ElMessage.success(`Đã thêm ${result.created} đối tượng ưu tiên`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không thêm được danh sách đối tượng ưu tiên'))
  } finally {
    saving.value = false
  }
}

async function onSubmit() {
  if (!editingId.value && createMode.value === 'json') {
    await onSubmitJson()
    return
  }

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = payloadFromForm()
    if (editingId.value) {
      await updateDoiTuongUuTien(editingId.value, payload)
      ElMessage.success('Đã cập nhật đối tượng ưu tiên')
    } else {
      await createDoiTuongUuTien(payload)
      ElMessage.success('Đã thêm đối tượng ưu tiên')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được đối tượng ưu tiên'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa đối tượng ưu tiên "${row.ten_doi_tuong}" (${row.ma_doi_tuong})?`,
      'Xác nhận xóa',
      {
        type: 'warning',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy',
        confirmButtonClass: 'el-button--danger',
      },
    )
  } catch {
    return
  }

  try {
    await deleteDoiTuongUuTien(row.id)
    ElMessage.success('Đã xóa đối tượng ưu tiên')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được đối tượng ưu tiên'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} đối tượng ưu tiên đã chọn?`,
      'Xác nhận xóa',
      {
        type: 'warning',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy',
        confirmButtonClass: 'el-button--danger',
      },
    )
  } catch {
    return
  }

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteDoiTuongUuTienMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} đối tượng ưu tiên`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các đối tượng ưu tiên đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Tìm tên hoặc mã đối tượng"
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
        <CustomOption label="Hoạt động" :value="1" />
        <CustomOption label="Ngừng sử dụng" :value="0" />
      </CustomSelect>
      <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
    </div>
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Danh sách đối tượng ưu tiên</h2>
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
          Thêm đối tượng
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
      <CustomTableColumn prop="ma_doi_tuong" label="Mã đối tượng" width="140" />
      <CustomTableColumn prop="ten_doi_tuong" label="Tên đối tượng" min-width="200" />
      <CustomTableColumn label="Điểm cộng" width="120" align="right">
        <template #default="{ row }">{{ formatScore(row.diem_cong) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" width="150" align="center">
        <template #default="{ row }">
          <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
            {{ row.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="200">
        <template #default="{ row }">{{ row.ghi_chu || '—' }}</template>
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
        <CustomEmpty description="Chưa có đối tượng ưu tiên nào." />
      </template>
    </CustomTable>

    <div class="pager">
      <CustomPagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
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
    :title="editingId ? 'Cập nhật đối tượng ưu tiên' : 'Thêm đối tượng ưu tiên'"
    width="720px"
    class="doi-tuong-uu-tien-dialog"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomRadioGroup v-if="!editingId" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!editingId && createMode === 'json'" class="json-panel">
      <div class="json-panel__head">
        <p>
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_doi_tuong</code> và <code>ma_doi_tuong</code>.
        </p>
        <CustomButton text type="primary" @click="fillJsonSample">Điền mẫu</CustomButton>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        placeholder="Dán mảng JSON vào đây"
      />
    </div>

    <CustomForm v-else ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Tên đối tượng" prop="ten_doi_tuong">
            <CustomInput v-model="form.ten_doi_tuong" maxlength="150" placeholder="Ví dụ: Đối tượng 01" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Mã đối tượng" prop="ma_doi_tuong">
            <CustomInput v-model="form.ma_doi_tuong" maxlength="20" placeholder="Ví dụ: 01" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Điểm cộng" prop="diem_cong">
            <CustomInputNumber
              v-model="form.diem_cong"
              :min="0"
              :max="99.99"
              :step="0.25"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" :clearable="false" style="width: 100%">
              <CustomOption label="Hoạt động" :value="1" />
              <CustomOption label="Ngừng sử dụng" :value="0" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Ghi chú" prop="ghi_chu">
            <CustomInput
              v-model="form.ghi_chu"
              type="textarea"
              :rows="3"
              maxlength="2000"
              show-word-limit
              placeholder="Ghi chú thêm (nếu có)"
            />
          </CustomFormItem>
        </CustomCol>
      </CustomRow>
    </CustomForm>
    <template #footer>
      <CustomButton @click="dialogVisible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" @click="onSubmit">Lưu</CustomButton>
    </template>
  </CustomDialog>
</template>

<style scoped>
.catalog-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.catalog-card {
  border-radius: 12px;
}

.filters,
.toolbar__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar__title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--el-text-color-primary);
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

.row-actions :deep(.el-icon svg) {
  stroke: currentColor;
  stroke-width: 1.15;
  stroke-linejoin: round;
  paint-order: stroke fill;
}

.filter-search {
  width: 280px;
}

.create-mode {
  margin-bottom: 16px;
}

.json-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.json-panel__head p {
  margin: 0;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.json-input :deep(textarea) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
}

.filter-status {
  width: 170px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 640px) {
  .filter-search,
  .filter-status {
    width: 100%;
  }
}
</style>
