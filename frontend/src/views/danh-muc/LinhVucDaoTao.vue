<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createLinhVuc,
  createLinhVucBulk,
  deleteLinhVuc,
  deleteLinhVucMany,
  fetchLinhVuc,
  updateLinhVuc,
} from '@/api/linhVucDaoTao'

const JSON_SAMPLE = `[
  {
    "ma_linh_vuc": "748",
    "ten_linh_vuc": "Máy tính và công nghệ thông tin",
    "ten_tieng_anh": "Computing and information technology",
    "trang_thai": 1
  },
  {
    "ma_linh_vuc": "734",
    "ten_linh_vuc": "Kinh doanh và quản lý",
    "ten_tieng_anh": "Business and management"
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
  ten_linh_vuc: [{ required: true, message: 'Vui lòng nhập tên lĩnh vực', trigger: 'blur' }],
  ma_linh_vuc: [{ required: true, message: 'Vui lòng nhập mã lĩnh vực', trigger: 'blur' }],
  ten_tieng_anh: [{ required: true, message: 'Vui lòng nhập tên tiếng Anh', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_linh_vuc: '',
    ten_linh_vuc: '',
    ten_tieng_anh: '',
    mo_ta: '',
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

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng lĩnh vực đào tạo.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_linh_vuc": "...", "ma_linh_vuc": "748" }]')
  }
  if (!data.length) {
    throw new Error('Mảng lĩnh vực đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một lĩnh vực`)
    }
    const ten = String(item.ten_linh_vuc ?? '').trim()
    const ma = String(item.ma_linh_vuc ?? '').trim()
    const tenTiengAnh = String(item.ten_tieng_anh ?? '').trim()
    if (!ten || !ma || !tenTiengAnh) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_linh_vuc, ma_linh_vuc hoặc ten_tieng_anh`)
    }
    return {
      ten_linh_vuc: ten,
      ma_linh_vuc: ma,
      ten_tieng_anh: tenTiengAnh,
      mo_ta: item.mo_ta == null ? null : String(item.mo_ta).trim() || null,
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
    const data = await fetchLinhVuc(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách lĩnh vực'))
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
    ma_linh_vuc: row.ma_linh_vuc,
    ten_linh_vuc: row.ten_linh_vuc,
    ten_tieng_anh: row.ten_tieng_anh,
    mo_ta: row.mo_ta || '',
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_linh_vuc: form.ma_linh_vuc.trim().toUpperCase(),
    ten_linh_vuc: form.ten_linh_vuc.trim(),
    ten_tieng_anh: form.ten_tieng_anh.trim(),
    mo_ta: form.mo_ta?.trim() || null,
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
    const result = await createLinhVucBulk(items)
    ElMessage.success(`Đã thêm ${result.created} lĩnh vực`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không thêm được danh sách lĩnh vực'))
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
      await updateLinhVuc(editingId.value, payload)
      ElMessage.success('Đã cập nhật lĩnh vực')
    } else {
      await createLinhVuc(payload)
      ElMessage.success('Đã thêm lĩnh vực')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được lĩnh vực'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa lĩnh vực "${row.ten_linh_vuc}" (${row.ma_linh_vuc})?`,
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
    await deleteLinhVuc(row.id)
    ElMessage.success('Đã xóa lĩnh vực')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được lĩnh vực'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} lĩnh vực đã chọn?`, 'Xác nhận xóa', {
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
    const result = await deleteLinhVucMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} lĩnh vực`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các lĩnh vực đã chọn'))
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
          placeholder="Tìm tên, mã hoặc tên tiếng Anh"
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
        <h2 class="toolbar__title">Danh sách lĩnh vực đào tạo</h2>
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
            Thêm lĩnh vực
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
        <CustomTableColumn prop="ma_linh_vuc" label="Mã" width="110" />
        <CustomTableColumn prop="ten_linh_vuc" label="Tên lĩnh vực" min-width="220" />
        <CustomTableColumn prop="ten_tieng_anh" label="Tên tiếng Anh" min-width="220" />
        <CustomTableColumn label="Trạng thái" width="150" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
              {{ row.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="mo_ta" label="Mô tả" min-width="240">
          <template #default="{ row }">{{ row.mo_ta || '—' }}</template>
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
          <CustomEmpty description="Chưa có lĩnh vực đào tạo nào." />
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
    :title="editingId ? 'Cập nhật lĩnh vực' : 'Thêm lĩnh vực'"
    width="760px"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_linh_vuc</code>, <code>ma_linh_vuc</code> và
          <code>ten_tieng_anh</code>.
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
          <CustomFormItem label="Tên lĩnh vực" prop="ten_linh_vuc">
            <CustomInput
              v-model="form.ten_linh_vuc"
              maxlength="255"
              placeholder="Ví dụ: Máy tính và công nghệ thông tin"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Mã lĩnh vực" prop="ma_linh_vuc">
            <CustomInput v-model="form.ma_linh_vuc" maxlength="20" placeholder="Ví dụ: 748" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Tên tiếng Anh" prop="ten_tieng_anh">
            <CustomInput
              v-model="form.ten_tieng_anh"
              maxlength="255"
              placeholder="Ví dụ: Computing and information technology"
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
          <CustomFormItem label="Mô tả" prop="mo_ta">
            <CustomInput
              v-model="form.mo_ta"
              type="textarea"
              :rows="3"
              maxlength="5000"
              show-word-limit
              placeholder="Mô tả lĩnh vực (nếu có)"
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
