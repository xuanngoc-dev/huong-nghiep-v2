<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createPhuongThucTuyenSinh,
  createPhuongThucTuyenSinhBulk,
  deletePhuongThucTuyenSinh,
  deletePhuongThucTuyenSinhMany,
  fetchPhuongThucTuyenSinh,
  updatePhuongThucTuyenSinh,
} from '@/api/phuongThucTuyenSinh'

const JSON_SAMPLE = `[
  {
    "ma_phuong_thuc": "100",
    "ten_phuong_thuc": "Xét kết quả thi tốt nghiệp THPT",
    "giai_thich": "Dùng điểm thi tốt nghiệp THPT để xét tuyển.",
    "truong_hop_cu_the": "Thí sinh đăng ký nguyện vọng trên hệ thống của Bộ.",
    "luu_y": "Mỗi ngành có tổ hợp xét tuyển riêng.",
    "trang_thai": 1
  },
  {
    "ma_phuong_thuc": "200",
    "ten_phuong_thuc": "Xét học bạ THPT",
    "giai_thich": "Dùng điểm học bạ các năm THPT."
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
  ten_phuong_thuc: [{ required: true, message: 'Vui lòng nhập tên phương thức', trigger: 'blur' }],
  ma_phuong_thuc: [{ required: true, message: 'Vui lòng nhập mã phương thức', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_phuong_thuc: '',
    ten_phuong_thuc: '',
    giai_thich: '',
    truong_hop_cu_the: '',
    luu_y: '',
    trang_thai: 1,
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  formRef.value?.clearValidate()
}

function optionalText(value) {
  if (value == null) return null
  const cleaned = String(value).trim()
  return cleaned || null
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng phương thức tuyển sinh.')
  }
  if (!Array.isArray(data)) {
    throw new Error(
      'JSON phải là một mảng, ví dụ [{ "ten_phuong_thuc": "...", "ma_phuong_thuc": "..." }]',
    )
  }
  if (!data.length) {
    throw new Error('Mảng phương thức tuyển sinh đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một phương thức tuyển sinh`)
    }
    const tenPhuongThuc = String(item.ten_phuong_thuc ?? '').trim()
    const maPhuongThuc = String(item.ma_phuong_thuc ?? '').trim()
    if (!tenPhuongThuc || !maPhuongThuc) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_phuong_thuc hoặc ma_phuong_thuc`)
    }
    return {
      ten_phuong_thuc: tenPhuongThuc,
      ma_phuong_thuc: maPhuongThuc,
      giai_thich: optionalText(item.giai_thich),
      truong_hop_cu_the: optionalText(item.truong_hop_cu_the),
      luu_y: optionalText(item.luu_y),
      trang_thai: item.trang_thai ?? 1,
    }
  })
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
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchPhuongThucTuyenSinh(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách phương thức tuyển sinh'))
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
    ma_phuong_thuc: row.ma_phuong_thuc,
    ten_phuong_thuc: row.ten_phuong_thuc,
    giai_thich: row.giai_thich || '',
    truong_hop_cu_the: row.truong_hop_cu_the || '',
    luu_y: row.luu_y || '',
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_phuong_thuc: form.ma_phuong_thuc.trim().toUpperCase(),
    ten_phuong_thuc: form.ten_phuong_thuc.trim(),
    giai_thich: form.giai_thich?.trim() || null,
    truong_hop_cu_the: form.truong_hop_cu_the?.trim() || null,
    luu_y: form.luu_y?.trim() || null,
    trang_thai: form.trang_thai,
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
    const result = await createPhuongThucTuyenSinhBulk(items)
    ElMessage.success(`Đã thêm ${result.created} phương thức tuyển sinh`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không thêm được danh sách phương thức tuyển sinh'))
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
      await updatePhuongThucTuyenSinh(editingId.value, payload)
      ElMessage.success('Đã cập nhật phương thức tuyển sinh')
    } else {
      await createPhuongThucTuyenSinh(payload)
      ElMessage.success('Đã thêm phương thức tuyển sinh')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được phương thức tuyển sinh'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa phương thức "${row.ten_phuong_thuc}" (${row.ma_phuong_thuc})?`,
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
    await deletePhuongThucTuyenSinh(row.id)
    ElMessage.success('Đã xóa phương thức tuyển sinh')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được phương thức tuyển sinh'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} phương thức tuyển sinh đã chọn?`,
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
    const result = await deletePhuongThucTuyenSinhMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} phương thức tuyển sinh`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các phương thức tuyển sinh đã chọn'))
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
        placeholder="Tìm tên hoặc mã phương thức"
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
      <h2 class="toolbar__title">Danh sách phương thức tuyển sinh</h2>
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
          Thêm phương thức
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
      <CustomTableColumn prop="ma_phuong_thuc" label="Mã PT" width="80" />
      <CustomTableColumn prop="ten_phuong_thuc" label="Tên phương thức" min-width="240" />
      <CustomTableColumn prop="giai_thich" label="Giải thích" min-width="220">
        <template #default="{ row }">{{ row.giai_thich || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn
        prop="truong_hop_cu_the"
        label="Trường hợp cụ thể"
        min-width="320"
        
      >
        <template #default="{ row }">{{ row.truong_hop_cu_the || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn prop="luu_y" label="Lưu ý" min-width="350" >
        <template #default="{ row }">{{ row.luu_y || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" width="150" align="center">
        <template #default="{ row }">
          <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
            {{ row.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' }}
          </CustomTag>
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
        <CustomEmpty description="Chưa có phương thức tuyển sinh nào." />
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
    :title="editingId ? 'Cập nhật phương thức tuyển sinh' : 'Thêm phương thức tuyển sinh'"
    width="1200px"
    class="phuong-thuc-dialog"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_phuong_thuc</code> và
          <code>ma_phuong_thuc</code>.
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
          <CustomFormItem label="Tên phương thức" prop="ten_phuong_thuc">
            <CustomInput
              v-model="form.ten_phuong_thuc"
              maxlength="255"
              placeholder="Ví dụ: Xét kết quả thi tốt nghiệp THPT"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Mã phương thức" prop="ma_phuong_thuc">
            <CustomInput v-model="form.ma_phuong_thuc" maxlength="20" placeholder="Ví dụ: 100" />
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
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Giải thích" prop="giai_thich">
            <CustomInput
              v-model="form.giai_thich"
              type="textarea"
              :rows="3"
              maxlength="5000"
              show-word-limit
              placeholder="Giải thích phương thức"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Trường hợp cụ thể" prop="truong_hop_cu_the">
            <CustomInput
              v-model="form.truong_hop_cu_the"
              type="textarea"
              :rows="3"
              maxlength="5000"
              show-word-limit
              placeholder="Ví dụ áp dụng"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Lưu ý" prop="luu_y">
            <CustomInput
              v-model="form.luu_y"
              type="textarea"
              :rows="3"
              maxlength="5000"
              show-word-limit
              placeholder="Những điểm cần lưu ý"
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
