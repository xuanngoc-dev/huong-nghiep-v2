<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createBaiThiDanhGiaNangLuc,
  createBaiThiDanhGiaNangLucBulk,
  deleteBaiThiDanhGiaNangLuc,
  deleteBaiThiDanhGiaNangLucMany,
  fetchBaiThiDanhGiaNangLuc,
  updateBaiThiDanhGiaNangLuc,
} from '@/api/baiThiDanhGiaNangLuc'

const LOAI = [
  { value: 'trong_nuoc', label: 'Trong nước' },
  { value: 'quoc_te', label: 'Quốc tế' },
]

const JSON_SAMPLE = `[
  {
    "ma_bai_thi": "HSA",
    "ten_bai_thi": "Đánh giá năng lực HSA",
    "ten_chi_tiet": "Bài thi đánh giá năng lực của Đại học Quốc gia Hà Nội",
    "linh_vuc": "Đánh giá năng lực",
    "mon": "Tổng hợp",
    "thang_diem": "0-150",
    "loai_chung_chi": "trong_nuoc",
    "trang_thai": 1,
    "ghi_chu": "Bài thi trong nước"
  },
  {
    "ma_bai_thi": "SAT",
    "ten_bai_thi": "SAT",
    "ten_chi_tiet": "Scholastic Assessment Test",
    "linh_vuc": "Đánh giá năng lực",
    "mon": "Tổng hợp",
    "thang_diem": "400-1600",
    "loai_chung_chi": "quoc_te"
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
const jsonImport = useJsonBatchImport({ label: 'bài thi đánh giá năng lực' })
const formRef = ref()

const filters = reactive({
  q: '',
  trang_thai: '',
  loai_chung_chi: '',
})

const form = reactive(emptyForm())

const rules = {
  ten_bai_thi: [{ required: true, message: 'Vui lòng nhập tên bài thi', trigger: 'blur' }],
  ma_bai_thi: [{ required: true, message: 'Vui lòng nhập mã bài thi', trigger: 'blur' }],
  loai_chung_chi: [{ required: true, message: 'Vui lòng chọn loại', trigger: 'change' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_bai_thi: '',
    ten_bai_thi: '',
    ten_chi_tiet: '',
    linh_vuc: '',
    mon: '',
    loai_chung_chi: 'trong_nuoc',
    thang_diem: '',
    trang_thai: 1,
    ghi_chu: '',
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function optionalText(value) {
  if (value == null) return null
  const text = String(value).trim()
  return text || null
}

function loaiLabel(value) {
  return LOAI.find((item) => item.value === value)?.label || value || '—'
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng bài thi đánh giá năng lực.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_bai_thi": "...", "ma_bai_thi": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng bài thi đánh giá năng lực đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một bài thi đánh giá năng lực`)
    }
    const ten = String(item.ten_bai_thi ?? '').trim()
    const ma = String(item.ma_bai_thi ?? '').trim()
    const loai = String(item.loai_chung_chi ?? '').trim().toLowerCase()
    if (!ten || !ma || !loai) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_bai_thi, ma_bai_thi hoặc loai_chung_chi`)
    }
    return {
      ten_bai_thi: ten,
      ma_bai_thi: ma,
      ten_chi_tiet: optionalText(item.ten_chi_tiet),
      linh_vuc: optionalText(item.linh_vuc),
      mon: optionalText(item.mon),
      loai_chung_chi: loai,
      thang_diem: optionalText(item.thang_diem),
      trang_thai: item.trang_thai ?? 1,
      ghi_chu: optionalText(item.ghi_chu),
    }
  })
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function dash(value) {
  if (value === null || value === undefined || value === '') return '—'
  return value
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
    if (filters.loai_chung_chi) params.loai_chung_chi = filters.loai_chung_chi
    const data = await fetchBaiThiDanhGiaNangLuc(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách bài thi đánh giá năng lực'))
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
    ma_bai_thi: row.ma_bai_thi,
    ten_bai_thi: row.ten_bai_thi,
    ten_chi_tiet: row.ten_chi_tiet || '',
    linh_vuc: row.linh_vuc || '',
    mon: row.mon || '',
    loai_chung_chi: row.loai_chung_chi,
    thang_diem: row.thang_diem || '',
    trang_thai: row.trang_thai,
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_bai_thi: form.ma_bai_thi.trim().toUpperCase(),
    ten_bai_thi: form.ten_bai_thi.trim(),
    ten_chi_tiet: optionalText(form.ten_chi_tiet),
    linh_vuc: optionalText(form.linh_vuc),
    mon: optionalText(form.mon),
    loai_chung_chi: form.loai_chung_chi,
    thang_diem: optionalText(form.thang_diem),
    trang_thai: form.trang_thai,
    ghi_chu: optionalText(form.ghi_chu),
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

  await jsonImport.run({
    items,
    createBatch: createBaiThiDanhGiaNangLucBulk,
    jsonText,
    saving,
    dialogVisible,
    reload: load,
  })
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
      await updateBaiThiDanhGiaNangLuc(editingId.value, payload)
      ElMessage.success('Đã cập nhật bài thi đánh giá năng lực')
    } else {
      await createBaiThiDanhGiaNangLuc(payload)
      ElMessage.success('Đã thêm bài thi đánh giá năng lực')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được bài thi đánh giá năng lực'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa bài thi đánh giá năng lực "${row.ten_bai_thi}" (${row.ma_bai_thi})?`,
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
    await deleteBaiThiDanhGiaNangLuc(row.id)
    ElMessage.success('Đã xóa bài thi đánh giá năng lực')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được bài thi đánh giá năng lực'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} bài thi đánh giá năng lực đã chọn?`, 'Xác nhận xóa', {
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
    const result = await deleteBaiThiDanhGiaNangLucMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} bài thi đánh giá năng lực`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các bài thi đánh giá năng lực đã chọn'))
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
          placeholder="Tìm tên, mã, lĩnh vực hoặc môn"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.loai_chung_chi"
          class="filter-status"
          placeholder="Loại"
          clearable
          @change="onSearch"
        >
          <CustomOption v-for="item in LOAI" :key="item.value" :label="item.label" :value="item.value" />
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
        <h2 class="toolbar__title">Danh sách bài thi đánh giá năng lực</h2>
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
            Thêm bài thi
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
        <CustomTableColumn prop="ma_bai_thi" label="Mã" width="120" />
        <CustomTableColumn prop="ten_bai_thi" label="Tên bài thi" min-width="180" />
        <CustomTableColumn prop="ten_chi_tiet" label="Tên chi tiết" min-width="200" >
          <template #default="{ row }">{{ dash(row.ten_chi_tiet) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="linh_vuc" label="Lĩnh vực" min-width="140">
          <template #default="{ row }">{{ dash(row.linh_vuc) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="mon" label="Môn" min-width="120">
          <template #default="{ row }">{{ dash(row.mon) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Loại" width="130">
          <template #default="{ row }">{{ loaiLabel(row.loai_chung_chi) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="thang_diem" label="Thang điểm" width="130">
          <template #default="{ row }">{{ dash(row.thang_diem) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Trạng thái" width="150" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
              {{ row.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="160" >
          <template #default="{ row }">{{ dash(row.ghi_chu) }}</template>
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
          <CustomEmpty description="Chưa có bài thi đánh giá năng lực nào." />
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
    :title="editingId ? 'Cập nhật bài thi đánh giá năng lực' : 'Thêm bài thi đánh giá năng lực'"
    width="960px"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_bai_thi</code>, <code>ma_bai_thi</code> và
          <code>loai_chung_chi</code> (<code>trong_nuoc</code> hoặc <code>quoc_te</code>).
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
          <CustomFormItem label="Tên bài thi" prop="ten_bai_thi">
            <CustomInput v-model="form.ten_bai_thi" maxlength="255" placeholder="Ví dụ: Đánh giá năng lực HSA" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Mã bài thi" prop="ma_bai_thi">
            <CustomInput v-model="form.ma_bai_thi" maxlength="50" placeholder="Ví dụ: HSA" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Loại" prop="loai_chung_chi">
            <CustomSelect v-model="form.loai_chung_chi" :clearable="false" style="width: 100%">
              <CustomOption v-for="item in LOAI" :key="item.value" :label="item.label" :value="item.value" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Lĩnh vực">
            <CustomInput v-model="form.linh_vuc" maxlength="150" placeholder="Ví dụ: Ngoại ngữ" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Môn">
            <CustomInput v-model="form.mon" maxlength="150" placeholder="Ví dụ: Tiếng Anh" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Thang điểm">
            <CustomInput v-model="form.thang_diem" maxlength="100" placeholder="Ví dụ: 0-9" />
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
          <CustomFormItem label="Tên chi tiết">
            <CustomInput
              v-model="form.ten_chi_tiet"
              maxlength="500"
              placeholder="Tên đầy đủ hoặc mô tả ngắn"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Ghi chú">
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
      <JsonImportDialogFooter
        :batch="jsonImport"
        :saving="saving"
        :show-progress="!editingId && createMode === 'json'"
        @cancel="dialogVisible = false"
        @save="onSubmit"
      />
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
