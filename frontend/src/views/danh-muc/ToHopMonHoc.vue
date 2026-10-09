<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchMonHoc } from '@/api/monHoc'
import {
  createToHopMonHoc,
  createToHopMonHocBulk,
  deleteToHopMonHoc,
  deleteToHopMonHocMany,
  fetchToHopMonHoc,
  updateToHopMonHoc,
} from '@/api/toHopMonHoc'

const JSON_SAMPLE = `[
  {
    "ma_to_hop": "A00",
    "ten_to_hop": "Toán, Lý, Hóa",
    "ds_mon_hoc": ["TOAN", "LY", "HOA"],
    "trang_thai": 1
  },
  {
    "ma_to_hop": "D01",
    "ten_to_hop": "Toán, Văn, Anh",
    "ds_mon_hoc": ["TOAN", "VAN", "ANH"],
    "ghi_chu": "Tổ hợp khối D"
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
const monHocOptions = ref([])

const filters = reactive({
  q: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

const monHocByCode = computed(() => {
  const map = new Map()
  for (const item of monHocOptions.value) map.set(item.ma_mon_hoc, item)
  return map
})

const selectOptions = computed(() => {
  const options = monHocOptions.value.map((item) => ({
    value: item.ma_mon_hoc,
    label: subjectOptionLabel(item),
  }))
  const known = new Set(options.map((item) => item.value))
  for (const code of form.ds_mon_hoc) {
    if (!known.has(code)) {
      options.push({ value: code, label: `${code} (không còn trong danh mục)` })
    }
  }
  return options
})

const rules = {
  ten_to_hop: [{ required: true, message: 'Vui lòng nhập tên tổ hợp', trigger: 'blur' }],
  ma_to_hop: [{ required: true, message: 'Vui lòng nhập mã tổ hợp', trigger: 'blur' }],
  ds_mon_hoc: [
    {
      type: 'array',
      required: true,
      min: 1,
      message: 'Vui lòng chọn ít nhất một môn học',
      trigger: 'change',
    },
  ],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_to_hop: '',
    ten_to_hop: '',
    ds_mon_hoc: [],
    trang_thai: 1,
    ghi_chu: '',
  }
}

function subjectOptionLabel(item) {
  const name = item.ten_viet_tat ? `${item.ten_mon_hoc} (${item.ten_viet_tat})` : item.ten_mon_hoc
  const status = item.trang_thai === 1 ? '' : ' — ngừng sử dụng'
  return `${name} · ${item.ma_mon_hoc}${status}`
}

function subjectLabel(code) {
  const item = monHocByCode.value.get(code)
  if (!item) return code
  return item.ten_viet_tat || item.ten_mon_hoc
}

function resetForm() {
  Object.assign(form, emptyForm())
  form.ds_mon_hoc = []
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
    throw new Error('JSON không hợp lệ. Hãy dán một mảng tổ hợp môn học.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_to_hop": "...", "ma_to_hop": "...", "ds_mon_hoc": [] }]')
  }
  if (!data.length) {
    throw new Error('Mảng tổ hợp môn học đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một tổ hợp môn học`)
    }
    const tenToHop = String(item.ten_to_hop ?? '').trim()
    const maToHop = String(item.ma_to_hop ?? '').trim()
    if (!tenToHop || !maToHop) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_to_hop hoặc ma_to_hop`)
    }
    if (!Array.isArray(item.ds_mon_hoc) || !item.ds_mon_hoc.length) {
      throw new Error(`Phần tử thứ ${line} cần ds_mon_hoc là mảng mã môn học`)
    }
    return {
      ten_to_hop: tenToHop,
      ma_to_hop: maToHop,
      ds_mon_hoc: item.ds_mon_hoc.map((code) => String(code).trim()).filter(Boolean),
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

async function loadMonHocOptions() {
  const pageSize = 100
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchMonHoc({ page: current, page_size: pageSize })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  items.sort((a, b) => a.ma_mon_hoc.localeCompare(b.ma_mon_hoc, 'vi'))
  monHocOptions.value = items
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
    const data = await fetchToHopMonHoc(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách tổ hợp môn học'))
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
  dialogVisible.value = true
  try {
    await loadMonHocOptions()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách môn học'))
  }
}

async function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    ma_to_hop: row.ma_to_hop,
    ten_to_hop: row.ten_to_hop,
    ds_mon_hoc: [...(row.ds_mon_hoc || [])],
    trang_thai: row.trang_thai,
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
  try {
    await loadMonHocOptions()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách môn học'))
  }
}

function payloadFromForm() {
  return {
    ma_to_hop: form.ma_to_hop.trim().toUpperCase(),
    ten_to_hop: form.ten_to_hop.trim(),
    ds_mon_hoc: form.ds_mon_hoc,
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
    const result = await createToHopMonHocBulk(items)
    ElMessage.success(`Đã thêm ${result.created} tổ hợp môn học`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không thêm được danh sách tổ hợp môn học'))
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
      await updateToHopMonHoc(editingId.value, payload)
      ElMessage.success('Đã cập nhật tổ hợp môn học')
    } else {
      await createToHopMonHoc(payload)
      ElMessage.success('Đã thêm tổ hợp môn học')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được tổ hợp môn học'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa tổ hợp "${row.ten_to_hop}" (${row.ma_to_hop})?`,
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
    await deleteToHopMonHoc(row.id)
    ElMessage.success('Đã xóa tổ hợp môn học')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được tổ hợp môn học'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} tổ hợp môn học đã chọn?`, 'Xác nhận xóa', {
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
    const result = await deleteToHopMonHocMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} tổ hợp môn học`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các tổ hợp môn học đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadMonHocOptions().catch(() => {})])
})
</script>

<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="filters">
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm tên, mã tổ hợp hoặc mã môn"
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
        <h2 class="toolbar__title">Danh sách tổ hợp môn học</h2>
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
            Thêm tổ hợp
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
        <CustomTableColumn prop="ma_to_hop" label="Mã tổ hợp" width="130" />
        <CustomTableColumn prop="ten_to_hop" label="Tên tổ hợp" min-width="200" />
        <CustomTableColumn label="Danh sách môn học" min-width="240">
          <template #default="{ row }">
            <span v-if="row.ds_mon_hoc?.length">{{ row.ds_mon_hoc.map(subjectLabel).join(', ') }}</span>
            <span v-else>—</span>
          </template>
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
          <CustomEmpty description="Chưa có tổ hợp môn học nào." />
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
    :title="editingId ? 'Cập nhật tổ hợp môn học' : 'Thêm tổ hợp môn học'"
    width="720px"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_to_hop</code>, <code>ma_to_hop</code> và
          <code>ds_mon_hoc</code> (mảng mã môn học).
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
          <CustomFormItem label="Tên tổ hợp" prop="ten_to_hop">
            <CustomInput v-model="form.ten_to_hop" maxlength="150" placeholder="Ví dụ: Toán, Lý, Hóa" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Mã tổ hợp" prop="ma_to_hop">
            <CustomInput v-model="form.ma_to_hop" maxlength="20" placeholder="Ví dụ: A00" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Danh sách môn học" prop="ds_mon_hoc">
            <CustomSelect
              v-model="form.ds_mon_hoc"
              multiple
              filterable
              placeholder="Chọn một hoặc nhiều môn học"
              style="width: 100%"
              :disabled="!selectOptions.length"
            >
              <CustomOption
                v-for="item in selectOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </CustomSelect>
            <p v-if="!monHocOptions.length" class="field-hint">
              Chưa có môn học. Hãy thêm ở danh mục Môn học trước.
            </p>
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
  width: 300px;
}

.field-hint {
  margin: 6px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.4;
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
