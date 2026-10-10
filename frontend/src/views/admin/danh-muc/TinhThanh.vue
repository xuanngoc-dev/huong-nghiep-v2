<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createTinhThanh,
  createTinhThanhBulk,
  deleteTinhThanh,
  deleteTinhThanhMany,
  fetchTinhThanh,
  updateTinhThanh,
} from '@/api/tinhThanh'

const KHU_VUC_OPTIONS = ['Bắc', 'Trung', 'Nam']

const JSON_SAMPLE = `[
  {
    "ten_tinh": "Hà Nội",
    "ma_tinh": "01",
    "khu_vuc": "Bắc",
    "dien_tich": 3358.6,
    "nam_thanh_lap": 1010,
    "trang_thai": 1,
    "ghi_chu": "Thủ đô"
  },
  {
    "ten_tinh": "Đà Nẵng",
    "ma_tinh": "48",
    "khu_vuc": "Trung"
  },
  {
    "ten_tinh": "TP. Hồ Chí Minh",
    "ma_tinh": "79",
    "khu_vuc": "Nam"
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
  khu_vuc: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

const rules = {
  ten_tinh: [{ required: true, message: 'Vui lòng nhập tên tỉnh', trigger: 'blur' }],
  ma_tinh: [{ required: true, message: 'Vui lòng nhập mã tỉnh', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ten_tinh: '',
    ma_tinh: '',
    khu_vuc: '',
    dien_tich: null,
    nam_thanh_lap: null,
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
    throw new Error('JSON không hợp lệ. Hãy dán một mảng tỉnh thành.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_tinh": "...", "ma_tinh": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng tỉnh thành đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một tỉnh thành`)
    }
    const tenTinh = String(item.ten_tinh ?? '').trim()
    const maTinh = String(item.ma_tinh ?? '').trim()
    if (!tenTinh || !maTinh) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_tinh hoặc ma_tinh`)
    }
    return {
      ten_tinh: tenTinh,
      ma_tinh: maTinh,
      khu_vuc: item.khu_vuc == null ? null : String(item.khu_vuc).trim() || null,
      dien_tich: item.dien_tich ?? null,
      nam_thanh_lap: item.nam_thanh_lap ?? null,
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

function formatArea(value) {
  if (value === null || value === undefined || value === '') return '—'
  return `${Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 2 })} km²`
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.khu_vuc) params.khu_vuc = filters.khu_vuc
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchTinhThanh(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách tỉnh thành'))
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
    ten_tinh: row.ten_tinh,
    ma_tinh: row.ma_tinh,
    khu_vuc: row.khu_vuc || '',
    dien_tich: row.dien_tich,
    nam_thanh_lap: row.nam_thanh_lap,
    trang_thai: row.trang_thai,
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ten_tinh: form.ten_tinh.trim(),
    ma_tinh: form.ma_tinh.trim().toUpperCase(),
    khu_vuc: form.khu_vuc?.trim() || null,
    dien_tich: form.dien_tich === '' || form.dien_tich === undefined ? null : form.dien_tich,
    nam_thanh_lap:
      form.nam_thanh_lap === '' || form.nam_thanh_lap === undefined ? null : form.nam_thanh_lap,
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
    const result = await createTinhThanhBulk(items)
    ElMessage.success(`Đã thêm ${result.created} tỉnh thành`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không thêm được danh sách tỉnh thành'))
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
      await updateTinhThanh(editingId.value, payload)
      ElMessage.success('Đã cập nhật tỉnh thành')
    } else {
      await createTinhThanh(payload)
      ElMessage.success('Đã thêm tỉnh thành')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được tỉnh thành'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa tỉnh thành "${row.ten_tinh}" (${row.ma_tinh})?`,
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
    await deleteTinhThanh(row.id)
    ElMessage.success('Đã xóa tỉnh thành')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được tỉnh thành'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} tỉnh thành đã chọn?`,
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
    const result = await deleteTinhThanhMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} tỉnh thành`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các tỉnh thành đã chọn'))
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
        placeholder="Tìm tên hoặc mã tỉnh"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect
        v-model="filters.khu_vuc"
        class="filter-region"
        placeholder="Khu vực"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="item in KHU_VUC_OPTIONS" :key="item" :label="item" :value="item" />
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
      <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
    </div>
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Danh sách tỉnh thành</h2>
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
          Thêm tỉnh thành
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
      <CustomTableColumn prop="ma_tinh" label="Mã tỉnh" width="110" />
      <CustomTableColumn prop="ten_tinh" label="Tên tỉnh" min-width="180" />
      <CustomTableColumn prop="khu_vuc" label="Khu vực" min-width="220">
        <template #default="{ row }">{{ row.khu_vuc || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Diện tích" width="150" align="right">
        <template #default="{ row }">{{ formatArea(row.dien_tich) }}</template>
      </CustomTableColumn>
      <CustomTableColumn prop="nam_thanh_lap" label="Năm thành lập" width="140" align="center">
        <template #default="{ row }">{{ row.nam_thanh_lap || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" width="150" align="center">
        <template #default="{ row }">
          <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
            {{ row.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="180" show-overflow-tooltip>
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
        <CustomEmpty description="Chưa có tỉnh thành nào." />
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
    :title="editingId ? 'Cập nhật tỉnh thành' : 'Thêm tỉnh thành'"
    width="960px"
    class="tinh-thanh-dialog"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_tinh</code> và <code>ma_tinh</code>.
          <code>khu_vuc</code> dùng Bắc, Trung hoặc Nam.
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
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Tên tỉnh" prop="ten_tinh">
            <CustomInput v-model="form.ten_tinh" maxlength="150" placeholder="Ví dụ: Hà Nội" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Mã tỉnh" prop="ma_tinh">
            <CustomInput v-model="form.ma_tinh" maxlength="20" placeholder="Ví dụ: 01" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Khu vực" prop="khu_vuc">
            <CustomSelect v-model="form.khu_vuc" placeholder="Chọn khu vực" clearable style="width: 100%">
              <CustomOption v-for="item in KHU_VUC_OPTIONS" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Diện tích (km²)" prop="dien_tich">
            <CustomInputNumber
              v-model="form.dien_tich"
              :min="0"
              :precision="2"
              :step="1"
              controls-position="right"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Năm thành lập" prop="nam_thanh_lap">
            <CustomInputNumber
              v-model="form.nam_thanh_lap"
              :min="1000"
              :max="2100"
              :step="1"
              :precision="0"
              controls-position="right"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
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
  width: 240px;
}

.filter-region {
  width: 160px;
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
  .filter-region,
  .filter-status {
    width: 100%;
  }
}
</style>
