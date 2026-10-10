<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchLinhVuc } from '@/api/linhVucDaoTao'
import {
  createNhomNganh,
  createNhomNganhBulk,
  deleteNhomNganh,
  deleteNhomNganhMany,
  fetchNhomNganh,
  updateNhomNganh,
} from '@/api/nhomNganhDaoTao'

const JSON_SAMPLE = `[
  {
    "ma_linh_vuc": "748",
    "ma_nhom_nganh": "74802",
    "ten_nhom_nganh": "Công nghệ thông tin",
    "ten_tieng_anh": "Information technology",
    "trang_thai": 1
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
const linhVucOptions = ref([])

const filters = reactive({
  q: '',
  trang_thai: '',
  ma_linh_vuc: '',
})

const form = reactive(emptyForm())

const rules = {
  ma_linh_vuc: [{ required: true, message: 'Vui lòng chọn lĩnh vực', trigger: 'change' }],
  ten_nhom_nganh: [{ required: true, message: 'Vui lòng nhập tên nhóm ngành', trigger: 'blur' }],
  ma_nhom_nganh: [{ required: true, message: 'Vui lòng nhập mã nhóm ngành', trigger: 'blur' }],
  ten_tieng_anh: [{ required: true, message: 'Vui lòng nhập tên tiếng Anh', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_linh_vuc: '',
    ma_nhom_nganh: '',
    ten_nhom_nganh: '',
    ten_tieng_anh: '',
    mo_ta: '',
    trang_thai: 1,
  }
}

function parentLabel(item) {
  const suffix = item.trang_thai === 1 ? '' : ' — ngừng sử dụng'
  return `${item.ma_linh_vuc} · ${item.ten_linh_vuc}${suffix}`
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
    throw new Error('JSON không hợp lệ. Hãy dán một mảng nhóm ngành.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ma_linh_vuc": "748", "ten_nhom_nganh": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng nhóm ngành đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một nhóm ngành`)
    }
    const maLinhVuc = String(item.ma_linh_vuc ?? '').trim()
    const ten = String(item.ten_nhom_nganh ?? '').trim()
    const ma = String(item.ma_nhom_nganh ?? '').trim()
    const tenTiengAnh = String(item.ten_tieng_anh ?? '').trim()
    if (!maLinhVuc || !ten || !ma || !tenTiengAnh) {
      throw new Error(
        `Phần tử thứ ${line} thiếu ma_linh_vuc, ten_nhom_nganh, ma_nhom_nganh hoặc ten_tieng_anh`,
      )
    }
    return {
      ma_linh_vuc: maLinhVuc,
      ten_nhom_nganh: ten,
      ma_nhom_nganh: ma,
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

async function loadLinhVucOptions() {
  const pageSize = 100
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchLinhVuc({ page: current, page_size: pageSize })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  items.sort((a, b) => a.ma_linh_vuc.localeCompare(b.ma_linh_vuc, 'vi'))
  linhVucOptions.value = items
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
    if (filters.ma_linh_vuc) params.ma_linh_vuc = filters.ma_linh_vuc
    const data = await fetchNhomNganh(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nhóm ngành'))
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

async function openCreate() {
  resetForm()
  if (filters.ma_linh_vuc) form.ma_linh_vuc = filters.ma_linh_vuc
  dialogVisible.value = true
  await loadLinhVucOptions().catch(() => {})
}

async function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    ma_linh_vuc: row.ma_linh_vuc,
    ma_nhom_nganh: row.ma_nhom_nganh,
    ten_nhom_nganh: row.ten_nhom_nganh,
    ten_tieng_anh: row.ten_tieng_anh,
    mo_ta: row.mo_ta || '',
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
  await loadLinhVucOptions().catch(() => {})
}

function payloadFromForm() {
  return {
    ma_linh_vuc: String(form.ma_linh_vuc).trim().toUpperCase(),
    ma_nhom_nganh: form.ma_nhom_nganh.trim().toUpperCase(),
    ten_nhom_nganh: form.ten_nhom_nganh.trim(),
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
    const result = await createNhomNganhBulk(items)
    ElMessage.success(`Đã thêm ${result.created} nhóm ngành`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không thêm được danh sách nhóm ngành'))
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
      await updateNhomNganh(editingId.value, payload)
      ElMessage.success('Đã cập nhật nhóm ngành')
    } else {
      await createNhomNganh(payload)
      ElMessage.success('Đã thêm nhóm ngành')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được nhóm ngành'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa nhóm ngành "${row.ten_nhom_nganh}" (${row.ma_nhom_nganh})?`,
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
    await deleteNhomNganh(row.id)
    ElMessage.success('Đã xóa nhóm ngành')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được nhóm ngành'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} nhóm ngành đã chọn?`, 'Xác nhận xóa', {
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
    const result = await deleteNhomNganhMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} nhóm ngành`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các nhóm ngành đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadLinhVucOptions().catch(() => {})])
})
</script>

<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="filters">
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm tên, mã hoặc lĩnh vực"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.ma_linh_vuc"
          class="filter-parent"
          placeholder="Lĩnh vực"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in linhVucOptions"
            :key="item.id"
            :label="parentLabel(item)"
            :value="item.ma_linh_vuc"
          />
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
        <h2 class="toolbar__title">Danh sách nhóm ngành đào tạo</h2>
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
            Thêm nhóm ngành
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
        <CustomTableColumn prop="ma_nhom_nganh" label="Mã" width="120" />
        <CustomTableColumn prop="ten_nhom_nganh" label="Tên nhóm ngành" min-width="200" />
        <CustomTableColumn label="Lĩnh vực" min-width="220">
          <template #default="{ row }">{{ row.ma_linh_vuc }} · {{ row.ten_linh_vuc }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_tieng_anh" label="Tên tiếng Anh" min-width="180" />
        <CustomTableColumn label="Trạng thái" width="150" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
              {{ row.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="mo_ta" label="Mô tả" min-width="200">
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
          <CustomEmpty description="Chưa có nhóm ngành nào." />
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
    :title="editingId ? 'Cập nhật nhóm ngành' : 'Thêm nhóm ngành'"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ma_linh_vuc</code>, <code>ten_nhom_nganh</code>,
          <code>ma_nhom_nganh</code> và <code>ten_tieng_anh</code>.
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
        <CustomCol :span="24">
          <CustomFormItem label="Lĩnh vực" prop="ma_linh_vuc">
            <CustomSelect
              v-model="form.ma_linh_vuc"
              filterable
              placeholder="Chọn lĩnh vực đào tạo"
              style="width: 100%"
              :disabled="!linhVucOptions.length"
            >
              <CustomOption
                v-for="item in linhVucOptions"
                :key="item.id"
                :label="parentLabel(item)"
                :value="item.ma_linh_vuc"
              />
            </CustomSelect>
            <p v-if="!linhVucOptions.length" class="field-hint">
              Chưa có lĩnh vực. Hãy thêm ở danh mục Lĩnh vực đào tạo trước.
            </p>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Tên nhóm ngành" prop="ten_nhom_nganh">
            <CustomInput v-model="form.ten_nhom_nganh" maxlength="255" placeholder="Ví dụ: Công nghệ thông tin" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Mã nhóm ngành" prop="ma_nhom_nganh">
            <CustomInput v-model="form.ma_nhom_nganh" maxlength="20" placeholder="Ví dụ: 74802" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Tên tiếng Anh" prop="ten_tieng_anh">
            <CustomInput
              v-model="form.ten_tieng_anh"
              maxlength="255"
              placeholder="Ví dụ: Information technology"
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
              placeholder="Mô tả nhóm ngành (nếu có)"
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

.filter-parent {
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

.field-hint {
  margin: 6px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.4;
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
  .filter-parent,
  .filter-status {
    width: 100%;
  }
}
</style>
