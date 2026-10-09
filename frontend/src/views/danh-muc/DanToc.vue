<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createDanToc,
  createDanTocBulk,
  deleteDanToc,
  deleteDanTocMany,
  fetchDanToc,
  updateDanToc,
} from '@/api/danToc'

const JSON_SAMPLE = `[
  {
    "ma_dan_toc": "01",
    "ten_dan_toc": "Kinh",
    "ten_goi_khac": "Việt",
    "dan_so": 82085526,
    "trang_thai": 1,
    "ghi_chu": "Dân tộc đa số"
  },
  {
    "ma_dan_toc": "02",
    "ten_dan_toc": "Tày",
    "ten_goi_khac": "Thổ",
    "dan_so": 1845492
  },
  {
    "ma_dan_toc": "03",
    "ten_dan_toc": "Thái",
    "ten_goi_khac": "Táy",
    "dan_so": 1820792
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
const pageSize = ref(10)
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
  ten_dan_toc: [{ required: true, message: 'Vui lòng nhập tên dân tộc', trigger: 'blur' }],
  ma_dan_toc: [{ required: true, message: 'Vui lòng nhập mã dân tộc', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_dan_toc: '',
    ten_dan_toc: '',
    ten_goi_khac: '',
    dan_so: null,
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
    throw new Error('JSON không hợp lệ. Hãy dán một mảng dân tộc.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_dan_toc": "...", "ma_dan_toc": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng dân tộc đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một dân tộc`)
    }
    const tenDanToc = String(item.ten_dan_toc ?? '').trim()
    const maDanToc = String(item.ma_dan_toc ?? '').trim()
    if (!tenDanToc || !maDanToc) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_dan_toc hoặc ma_dan_toc`)
    }
    return {
      ten_dan_toc: tenDanToc,
      ma_dan_toc: maDanToc,
      ten_goi_khac: item.ten_goi_khac == null ? null : String(item.ten_goi_khac).trim() || null,
      dan_so: item.dan_so ?? null,
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

function formatPopulation(value) {
  if (value === null || value === undefined || value === '') return '—'
  return Number(value).toLocaleString('vi-VN')
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
    const data = await fetchDanToc(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách dân tộc'))
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
    ma_dan_toc: row.ma_dan_toc,
    ten_dan_toc: row.ten_dan_toc,
    ten_goi_khac: row.ten_goi_khac || '',
    dan_so: row.dan_so,
    trang_thai: row.trang_thai,
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_dan_toc: form.ma_dan_toc.trim().toUpperCase(),
    ten_dan_toc: form.ten_dan_toc.trim(),
    ten_goi_khac: form.ten_goi_khac?.trim() || null,
    dan_so: form.dan_so === '' || form.dan_so === undefined ? null : form.dan_so,
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
    const result = await createDanTocBulk(items)
    ElMessage.success(`Đã thêm ${result.created} dân tộc`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không thêm được danh sách dân tộc'))
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
      await updateDanToc(editingId.value, payload)
      ElMessage.success('Đã cập nhật dân tộc')
    } else {
      await createDanToc(payload)
      ElMessage.success('Đã thêm dân tộc')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được dân tộc'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa dân tộc "${row.ten_dan_toc}" (${row.ma_dan_toc})?`,
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
    await deleteDanToc(row.id)
    ElMessage.success('Đã xóa dân tộc')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được dân tộc'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} dân tộc đã chọn?`,
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
    const result = await deleteDanTocMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} dân tộc`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các dân tộc đã chọn'))
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
        placeholder="Tìm tên, mã hoặc tên gọi khác"
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
      <h2 class="toolbar__title">Danh sách dân tộc</h2>
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
          Thêm dân tộc
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
      <CustomTableColumn prop="ma_dan_toc" label="Mã dân tộc" width="120" />
      <CustomTableColumn prop="ten_dan_toc" label="Tên dân tộc" min-width="160" />
      <CustomTableColumn prop="ten_goi_khac" label="Tên gọi khác" min-width="180">
        <template #default="{ row }">{{ row.ten_goi_khac || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Dân số" width="140" align="right">
        <template #default="{ row }">{{ formatPopulation(row.dan_so) }}</template>
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
        <CustomEmpty description="Chưa có dân tộc nào." />
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
    :title="editingId ? 'Cập nhật dân tộc' : 'Thêm dân tộc'"
    width="960px"
    class="dan-toc-dialog"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_dan_toc</code> và <code>ma_dan_toc</code>.
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
          <CustomFormItem label="Tên dân tộc" prop="ten_dan_toc">
            <CustomInput v-model="form.ten_dan_toc" maxlength="150" placeholder="Ví dụ: Kinh" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Mã dân tộc" prop="ma_dan_toc">
            <CustomInput v-model="form.ma_dan_toc" maxlength="20" placeholder="Ví dụ: 01" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Tên gọi khác" prop="ten_goi_khac">
            <CustomInput v-model="form.ten_goi_khac" maxlength="255" placeholder="Ví dụ: Việt" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Dân số" prop="dan_so">
            <CustomInputNumber
              v-model="form.dan_so"
              :min="0"
              :max="200000000"
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
