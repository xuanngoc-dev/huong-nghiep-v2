<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchDeAnTuyenSinh } from '@/api/deAnTuyenSinh'
import { fetchTruongHoc } from '@/api/truongHoc'
import {
  createTruSo,
  deleteTruSo,
  deleteTruSoMany,
  fetchTruSo,
  importTruSo,
  updateTruSo,
} from '@/api/truSo'
import { NAM_HOC, laNamHoc, nhanNamHoc } from '@/constants/namHoc'

const VAI_TRO_OPTIONS = [
  { value: 'chinh', label: 'Chính' },
  { value: 'phu', label: 'Phụ' },
]

const LOAI_CO_SO_OPTIONS = [
  { value: 'tru_so', label: 'Trụ sở' },
  { value: 'co_so', label: 'Cơ sở' },
  { value: 'phan_hieu', label: 'Phân hiệu' },
]

const formCol = { span: 4, lg: 4, md: 6, sm: 8, xs: 12 }

const JSON_SAMPLE = `[
  {
    "id": 1,
    "de_an_id": 1,
    "vai_tro": "chinh",
    "ten_co_so": "Cơ sở 1",
    "loai_co_so": "tru_so",
    "dia_chi": "Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội",
    "so_dien_thoai": "02438692222",
    "ghi_chu": null
  }
]`

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const deAnLoading = ref(false)
const filterDeAnLoading = ref(false)
const rows = ref([])
const selectedRows = ref([])
const tableRef = ref()
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('json')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'trụ sở' })
const formRef = ref()
const truongOptions = ref([])
const deAnOptions = ref([])
const filterDeAnOptions = ref([])
let deAnRequest = 0
let filterDeAnRequest = 0
let ignoreContextChange = false

const filters = reactive({
  q: '',
  nam_tuyen_sinh: '',
  ma_truong: '',
  de_an_id: '',
})

const context = reactive({
  ma_truong: null,
  nam_tuyen_sinh: new Date().getFullYear(),
  de_an_id: null,
})

const form = reactive(emptyForm())

const rules = {
  ten_co_so: [{ required: true, message: 'Vui lòng nhập tên cơ sở', trigger: 'blur' }],
}

const selectedYear = computed(() => laNamHoc(context.nam_tuyen_sinh))

const contextReady = computed(() => Boolean(context.ma_truong) && selectedYear.value != null)

const filterDeAnReady = computed(() => Boolean(filters.ma_truong) || yearFilter() != null)

function emptyForm() {
  return {
    vai_tro: '',
    ten_co_so: '',
    loai_co_so: '',
    dia_chi: '',
    so_dien_thoai: '',
    ghi_chu: '',
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'json'
  jsonText.value = ''
  context.ma_truong = null
  context.nam_tuyen_sinh = new Date().getFullYear()
  context.de_an_id = null
  deAnOptions.value = []
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function schoolLabel(school) {
  if (!school) return ''
  return school.ma_truong ? `${school.ma_truong} — ${school.ten_truong}` : school.ten_truong
}

function deAnOptionLabel(item) {
  if (!item) return ''
  const name = item.ten_de_an || `Đề án #${item.id}`
  return [schoolLabel(item), item.nam_tuyen_sinh, name].filter((part) => part != null && part !== '').join(' · ')
}

function codeLabel(value, options) {
  if (!value) return '—'
  return options.find((item) => item.value === value)?.label || value
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
    throw new Error('JSON không hợp lệ. Hãy dán một mảng trụ sở.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng các trụ sở.')
  }
  if (!data.length) {
    throw new Error('Mảng trụ sở đang trống')
  }
  if (data.length > 2000) {
    throw new Error('Chỉ nhập tối đa 2000 trụ sở mỗi lần')
  }
  data.forEach((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một trụ sở`)
    }
    if (!String(item.ten_co_so ?? '').trim()) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_co_so`)
    }
  })
  return data
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function yearFilter() {
  return laNamHoc(filters.nam_tuyen_sinh)
}

function ensureContext() {
  if (!context.ma_truong) {
    ElMessage.error('Vui lòng chọn trường')
    return false
  }
  if (selectedYear.value == null) {
    ElMessage.error('Vui lòng chọn năm học')
    return false
  }
  if (!context.de_an_id) {
    ElMessage.error('Vui lòng chọn đề án tuyển sinh')
    return false
  }
  return true
}

async function loadTruongOptions() {
  const pageSizeOptions = 1000
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchTruongHoc({ page: current, page_size: pageSizeOptions })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  items.sort((a, b) => String(a.ten_truong || '').localeCompare(String(b.ten_truong || ''), 'vi'))
  truongOptions.value = items
}

async function loadDeAnOptions() {
  const requestId = ++deAnRequest
  const truongId = context.ma_truong
  const year = selectedYear.value
  if (!truongId || year == null) {
    deAnOptions.value = []
    return
  }
  deAnLoading.value = true
  try {
    const data = await fetchDeAnTuyenSinh({
      ma_truong: truongId,
      nam_tuyen_sinh: year,
      page: 1,
      page_size: 1000,
    })
    if (requestId !== deAnRequest) return
    deAnOptions.value = data.items || []
  } catch (error) {
    if (requestId !== deAnRequest) return
    deAnOptions.value = []
    ElMessage.error(errorMessage(error, 'Không tải được danh sách đề án tuyển sinh'))
  } finally {
    if (requestId === deAnRequest) deAnLoading.value = false
  }
}

async function loadFilterDeAnOptions() {
  const requestId = ++filterDeAnRequest
  const year = yearFilter()
  if (!filters.ma_truong && year == null) {
    filterDeAnOptions.value = []
    return
  }
  filterDeAnLoading.value = true
  try {
    const params = { page: 1, page_size: 1000 }
    if (filters.ma_truong) params.ma_truong = filters.ma_truong
    if (year != null) params.nam_tuyen_sinh = year
    const data = await fetchDeAnTuyenSinh(params)
    if (requestId !== filterDeAnRequest) return
    filterDeAnOptions.value = data.items || []
  } catch (error) {
    if (requestId !== filterDeAnRequest) return
    filterDeAnOptions.value = []
    ElMessage.error(errorMessage(error, 'Không tải được danh sách đề án tuyển sinh'))
  } finally {
    if (requestId === filterDeAnRequest) filterDeAnLoading.value = false
  }
}

async function onContextFilterChange() {
  if (ignoreContextChange) return
  context.de_an_id = null
  await loadDeAnOptions()
}

function onFilterScopeChange() {
  filters.de_an_id = ''
  onSearch()
}

async function load() {
  const year = yearFilter()

  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (year != null) params.nam_tuyen_sinh = year
    if (filters.ma_truong) params.ma_truong = filters.ma_truong
    if (filters.de_an_id) params.de_an_id = filters.de_an_id
    const data = await fetchTruSo(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách trụ sở'))
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

async function onSearch() {
  clearSelection()
  await loadFilterDeAnOptions()
  if (filters.de_an_id && !filterDeAnOptions.value.some((item) => item.id === filters.de_an_id)) {
    filters.de_an_id = ''
  }
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

async function openEdit(row) {
  ignoreContextChange = true
  editingId.value = row.id
  createMode.value = 'form'
  context.ma_truong = row.ma_truong
  context.nam_tuyen_sinh = row.nam_tuyen_sinh
  context.de_an_id = row.de_an_id
  Object.assign(form, {
    vai_tro: row.vai_tro || '',
    ten_co_so: row.ten_co_so || '',
    loai_co_so: row.loai_co_so || '',
    dia_chi: row.dia_chi || '',
    so_dien_thoai: row.so_dien_thoai || '',
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
  await nextTick()
  ignoreContextChange = false
  await loadDeAnOptions()
}

function payloadFromForm() {
  return {
    de_an_id: context.de_an_id,
    vai_tro: optionalText(form.vai_tro),
    ten_co_so: form.ten_co_so.trim(),
    loai_co_so: optionalText(form.loai_co_so),
    dia_chi: optionalText(form.dia_chi),
    so_dien_thoai: optionalText(form.so_dien_thoai),
    ghi_chu: optionalText(form.ghi_chu),
  }
}

function fillJsonSample() {
  jsonText.value = JSON_SAMPLE
}

async function onSubmitJson() {
  if (!ensureContext()) return

  let items
  try {
    items = parseJsonItems(jsonText.value)
  } catch (error) {
    ElMessage.error(error.message)
    return
  }

  saving.value = true
  try {
    const result = await importTruSo(
      {
        de_an_id: context.de_an_id,
        du_lieu: items,
      },
      { skipLoading: true, timeout: 120000 },
    )
    ElMessage.success(`Đã nhập ${result.created} trụ sở`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không nhập được trụ sở'))
  } finally {
    saving.value = false
  }
}

async function onSubmit() {
  if (!editingId.value && createMode.value === 'json') {
    await onSubmitJson()
    return
  }

  if (!ensureContext()) return
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = payloadFromForm()
    if (editingId.value) {
      await updateTruSo(editingId.value, payload)
      ElMessage.success('Đã cập nhật trụ sở')
    } else {
      await createTruSo(payload)
      ElMessage.success('Đã thêm trụ sở')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được trụ sở'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  const name = row.ten_co_so || `trụ sở #${row.id}`
  try {
    await ElMessageBox.confirm(`Xóa "${name}"?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  try {
    await deleteTruSo(row.id)
    ElMessage.success('Đã xóa trụ sở')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được trụ sở'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} trụ sở đã chọn?`, 'Xác nhận xóa', {
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
    const result = await deleteTruSoMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} trụ sở`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các trụ sở đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadTruongOptions().catch(() => {})])
})
</script>

<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="filters">
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm tên cơ sở, địa chỉ, điện thoại hoặc đề án"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.ma_truong"
          class="filter-school"
          placeholder="Trường"
          clearable
          filterable
          @change="onFilterScopeChange"
        >
          <CustomOption
            v-for="item in truongOptions"
            :key="item.id"
            :label="schoolLabel(item)"
            :value="item.ma_truong"
          />
        </CustomSelect>
        <CustomSelect
          v-model="filters.nam_tuyen_sinh"
          class="filter-year"
          placeholder="Năm học"
          clearable
          @change="onFilterScopeChange"
        >
          <CustomOption v-for="nam in NAM_HOC" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.de_an_id"
          class="filter-proposal"
          placeholder="Đề án tuyển sinh"
          clearable
          filterable
          :disabled="!filterDeAnReady"
          :loading="filterDeAnLoading"
          @change="onSearch"
        >
          <CustomOption
            v-for="item in filterDeAnOptions"
            :key="item.id"
            :label="deAnOptionLabel(item)"
            :value="item.id"
          />
        </CustomSelect>
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách trụ sở</h2>
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
            Thêm trụ sở
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
        <CustomTableColumn prop="nam_tuyen_sinh" label="Năm" width="90" align="center" />
        <CustomTableColumn label="Trường" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ schoolLabel(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Đề án" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">{{ row.ten_de_an || `Đề án #${row.de_an_id}` }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Vai trò" width="110">
          <template #default="{ row }">{{ codeLabel(row.vai_tro, VAI_TRO_OPTIONS) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_co_so" label="Tên cơ sở" min-width="200" show-overflow-tooltip />
        <CustomTableColumn label="Loại cơ sở" width="130">
          <template #default="{ row }">{{ codeLabel(row.loai_co_so, LOAI_CO_SO_OPTIONS) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="dia_chi" label="Địa chỉ" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">{{ row.dia_chi || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="so_dien_thoai" label="Điện thoại" width="140">
          <template #default="{ row }">{{ row.so_dien_thoai || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="200" show-overflow-tooltip>
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
          <CustomEmpty description="Chưa có trụ sở nào." />
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
    :title="editingId ? 'Cập nhật trụ sở' : 'Thêm trụ sở'"
    width="90%"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomRow :gutter="16" align="bottom" class="json-meta">
      <CustomCol :span="8">
        <span class="json-field__label">Trường</span>
        <CustomSelect
          v-model="context.ma_truong"
          filterable
          placeholder="Chọn trường"
          style="width: 100%"
          @change="onContextFilterChange"
        >
          <CustomOption
            v-for="item in truongOptions"
            :key="item.id"
            :label="schoolLabel(item)"
            :value="item.ma_truong"
          />
        </CustomSelect>
      </CustomCol>
      <CustomCol :span="4">
        <span class="json-field__label">Năm học</span>
        <CustomSelect
          v-model="context.nam_tuyen_sinh"
          placeholder="Năm học"
          style="width: 100%"
          @change="onContextFilterChange"
        >
          <CustomOption v-for="nam in NAM_HOC" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
        </CustomSelect>
      </CustomCol>
      <CustomCol :span="8">
        <span class="json-field__label">Đề án tuyển sinh</span>
        <CustomSelect
          v-model="context.de_an_id"
          filterable
          :disabled="!contextReady"
          :loading="deAnLoading"
          placeholder="Chọn đề án"
          style="width: 100%"
        >
          <CustomOption
            v-for="item in deAnOptions"
            :key="item.id"
            :label="item.ten_de_an || `Đề án #${item.id}`"
            :value="item.id"
          />
        </CustomSelect>
      </CustomCol>
    </CustomRow>
    <p v-if="contextReady && !deAnLoading && !deAnOptions.length" class="context-hint">
      Chưa có đề án tuyển sinh cho trường và năm này.
    </p>

    <CustomRadioGroup v-if="!editingId" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!editingId && createMode === 'json'" class="json-panel">
      <div class="json-panel__head">
        <p>
          Chọn trường, năm và đề án, rồi dán mảng JSON trụ sở.
          <code>de_an_id</code> lấy từ đề án đã chọn. <code>id</code> trong file không được lưu.
        </p>
        <CustomButton text type="primary" :disabled="!context.de_an_id" @click="fillJsonSample">
          Điền mẫu
        </CustomButton>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        :disabled="!context.de_an_id"
        placeholder="Chọn đề án tuyển sinh để dán JSON"
      />
    </div>

    <CustomForm v-else ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol v-bind="formCol">
          <CustomFormItem label="Tên cơ sở" prop="ten_co_so">
            <CustomInput v-model="form.ten_co_so" maxlength="255" placeholder="Tên trụ sở, cơ sở hoặc phân hiệu" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-bind="formCol">
          <CustomFormItem label="Vai trò" prop="vai_tro">
            <CustomSelect
              v-model="form.vai_tro"
              filterable
              allow-create
              default-first-option
              clearable
              placeholder="Chính hoặc phụ"
              style="width: 100%"
            >
              <CustomOption
                v-for="item in VAI_TRO_OPTIONS"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-bind="formCol">
          <CustomFormItem label="Loại cơ sở" prop="loai_co_so">
            <CustomSelect
              v-model="form.loai_co_so"
              filterable
              allow-create
              default-first-option
              clearable
              placeholder="Trụ sở, cơ sở hoặc phân hiệu"
              style="width: 100%"
            >
              <CustomOption
                v-for="item in LOAI_CO_SO_OPTIONS"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-bind="formCol">
          <CustomFormItem label="Điện thoại" prop="so_dien_thoai">
            <CustomInput v-model="form.so_dien_thoai" maxlength="30" placeholder="Số liên hệ tại địa điểm" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-bind="formCol">
          <CustomFormItem label="Địa chỉ" prop="dia_chi">
            <CustomInput v-model="form.dia_chi" maxlength="500" placeholder="Địa chỉ đầy đủ" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-bind="formCol">
          <CustomFormItem label="Ghi chú" prop="ghi_chu">
            <CustomInput
              v-model="form.ghi_chu"
              type="text"
              :maxlength="20000"
              placeholder="Thông tin bổ sung"
            />
          </CustomFormItem>
        </CustomCol>
      </CustomRow>
    </CustomForm>
    <template #footer>
      <JsonImportDialogFooter
        :batch="jsonImport"
        :saving="saving"
        :show-progress="false"
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
  font-weight: 400;
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

.filter-search,
.filter-school,
.filter-proposal {
  width: 280px;
}

.filter-year {
  width: 168px;
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

.json-panel__head p,
.context-hint {
  margin: 0;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.context-hint {
  margin: -4px 0 12px;
}

.json-meta {
  margin-bottom: 12px;
}

.json-field__label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  line-height: 22px;
  color: var(--el-text-color-regular);
}

.json-field__label::before {
  content: '*';
  margin-right: 4px;
  color: var(--el-color-danger);
}

.json-input :deep(textarea) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 640px) {
  .filter-search,
  .filter-school,
  .filter-year,
  .filter-proposal {
    width: 100%;
    max-width: none;
  }
}
</style>
