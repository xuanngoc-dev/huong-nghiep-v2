<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createChuongTrinhDaoTao,
  deleteChuongTrinhDaoTao,
  deleteChuongTrinhDaoTaoMany,
  fetchChuongTrinhDaoTao,
  importChuongTrinhDaoTao,
  updateChuongTrinhDaoTao,
} from '@/api/chuongTrinhDaoTao'
import { fetchDeAnTuyenSinh } from '@/api/deAnTuyenSinh'
import { fetchTruongHoc } from '@/api/truongHoc'

const TRINH_DO_LABELS = {
  dai_hoc: 'Đại học',
  thac_si: 'Thạc sĩ',
  tien_si: 'Tiến sĩ',
  cao_dang: 'Cao đẳng',
  trung_cap: 'Trung cấp',
}

const HINH_THUC_LABELS = {
  chinh_quy: 'Chính quy',
  lien_thong: 'Liên thông',
  vua_hoc_vua_lam: 'Vừa học vừa làm',
  tu_xa: 'Đào tạo từ xa',
  van_bang_2: 'Văn bằng 2',
}

const JSON_SAMPLE = `[
  {
    "id": 2610001,
    "de_an_id": 2600001,
    "nganh_dao_tao_id": null,
    "ma_xet_tuyen": "BF1",
    "ten_chuong_trinh": "Kỹ thuật Sinh học",
    "trinh_do_dao_tao": "dai_hoc",
    "hinh_thuc_dao_tao": "chinh_quy",
    "co_so_id": null,
    "thoi_gian_dao_tao_nam": null,
    "ngon_ngu_dao_tao": null,
    "chi_tieu_tuyen_sinh": 160,
    "kieu_phan_bo_chi_tieu": null,
    "ghi_chu": "Nhóm: chuong_trinh_chuan; Bảng chương trình, trang 6; chỉ tiêu toàn chương trình, không tách phương thức. nganh_dao_tao_id, co_so_id cần map dm tương ứng. PDF không nêu cách phân bổ chỉ tiêu giữa các phương thức."
  }
]`

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const deAnLoading = ref(false)
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
const jsonImport = useJsonBatchImport({ label: 'chương trình đào tạo' })
const formRef = ref()
const truongOptions = ref([])
const deAnOptions = ref([])
let deAnRequest = 0
let ignoreContextChange = false

const filters = reactive({
  q: '',
  nam_tuyen_sinh: '',
  truong_id: '',
})

const context = reactive({
  truong_id: null,
  nam_tuyen_sinh: new Date().getFullYear(),
  de_an_id: null,
})

const form = reactive(emptyForm())

const rules = {
  ten_chuong_trinh: [{ required: true, message: 'Vui lòng nhập tên chương trình', trigger: 'blur' }],
}

const selectedYear = computed(() => {
  const year = Number(context.nam_tuyen_sinh)
  if (!Number.isInteger(year) || year < 1990 || year > 2100) return null
  return year
})

const contextReady = computed(() => Boolean(context.truong_id) && selectedYear.value != null)

function emptyForm() {
  return {
    nganh_dao_tao_id: null,
    ma_xet_tuyen: '',
    ten_chuong_trinh: '',
    trinh_do_dao_tao: '',
    hinh_thuc_dao_tao: '',
    co_so_id: null,
    thoi_gian_dao_tao_nam: null,
    ngon_ngu_dao_tao: '',
    chi_tieu_tuyen_sinh: null,
    kieu_phan_bo_chi_tieu: '',
    ghi_chu: '',
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'json'
  jsonText.value = ''
  context.truong_id = null
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
  return item.ten_de_an || `Đề án #${item.id}`
}

function codeLabel(value, labels) {
  if (!value) return '—'
  return labels[value] || value
}

function nganhLabel(row) {
  if (!row.nganh_dao_tao_id) return '—'
  if (row.ma_nganh && row.ten_nganh) return `${row.ma_nganh} — ${row.ten_nganh}`
  return row.ten_nganh || String(row.nganh_dao_tao_id)
}

function coSoLabel(row) {
  if (!row.co_so_id) return '—'
  return row.ten_co_so || String(row.co_so_id)
}

function formatQuota(value) {
  if (value == null || value === '') return '—'
  return Number(value).toLocaleString('vi-VN')
}

function formatDuration(value) {
  if (value == null || value === '') return '—'
  return Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 1 })
}

function optionalText(value) {
  if (value == null) return null
  const cleaned = String(value).trim()
  return cleaned || null
}

function optionalNumber(value) {
  if (value == null || value === '') return null
  return Number(value)
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng chương trình đào tạo.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng các chương trình đào tạo.')
  }
  if (!data.length) {
    throw new Error('Mảng chương trình đào tạo đang trống')
  }
  if (data.length > 2000) {
    throw new Error('Chỉ nhập tối đa 2000 chương trình mỗi lần')
  }
  data.forEach((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một chương trình`)
    }
    if (!String(item.ten_chuong_trinh ?? '').trim()) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_chuong_trinh`)
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
  const raw = String(filters.nam_tuyen_sinh ?? '').trim()
  if (!raw) return null
  if (!/^\d{4}$/.test(raw)) return undefined
  const year = Number(raw)
  if (year < 1990 || year > 2100) return undefined
  return year
}

function ensureContext() {
  if (!context.truong_id) {
    ElMessage.error('Vui lòng chọn trường')
    return false
  }
  if (selectedYear.value == null) {
    ElMessage.error('Năm tuyển sinh phải là số từ 1990 đến 2100')
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
  const truongId = context.truong_id
  const year = selectedYear.value
  if (!truongId || year == null) {
    deAnOptions.value = []
    return
  }
  deAnLoading.value = true
  try {
    const data = await fetchDeAnTuyenSinh({
      truong_id: truongId,
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

async function onContextFilterChange() {
  if (ignoreContextChange) return
  context.de_an_id = null
  await loadDeAnOptions()
}

async function load() {
  const year = yearFilter()
  if (year === undefined) {
    ElMessage.error('Năm tuyển sinh phải là số từ 1990 đến 2100')
    return
  }

  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (year != null) params.nam_tuyen_sinh = year
    if (filters.truong_id) params.truong_id = filters.truong_id
    const data = await fetchChuongTrinhDaoTao(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách chương trình đào tạo'))
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

async function openEdit(row) {
  ignoreContextChange = true
  editingId.value = row.id
  createMode.value = 'form'
  context.truong_id = row.truong_id
  context.nam_tuyen_sinh = row.nam_tuyen_sinh
  context.de_an_id = row.de_an_id
  Object.assign(form, {
    nganh_dao_tao_id: row.nganh_dao_tao_id ?? null,
    ma_xet_tuyen: row.ma_xet_tuyen || '',
    ten_chuong_trinh: row.ten_chuong_trinh || '',
    trinh_do_dao_tao: row.trinh_do_dao_tao || '',
    hinh_thuc_dao_tao: row.hinh_thuc_dao_tao || '',
    co_so_id: row.co_so_id ?? null,
    thoi_gian_dao_tao_nam: row.thoi_gian_dao_tao_nam ?? null,
    ngon_ngu_dao_tao: row.ngon_ngu_dao_tao || '',
    chi_tieu_tuyen_sinh: row.chi_tieu_tuyen_sinh ?? null,
    kieu_phan_bo_chi_tieu: row.kieu_phan_bo_chi_tieu || '',
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
    nganh_dao_tao_id: optionalNumber(form.nganh_dao_tao_id),
    ma_xet_tuyen: optionalText(form.ma_xet_tuyen),
    ten_chuong_trinh: form.ten_chuong_trinh.trim(),
    trinh_do_dao_tao: optionalText(form.trinh_do_dao_tao),
    hinh_thuc_dao_tao: optionalText(form.hinh_thuc_dao_tao),
    co_so_id: optionalNumber(form.co_so_id),
    thoi_gian_dao_tao_nam: optionalNumber(form.thoi_gian_dao_tao_nam),
    ngon_ngu_dao_tao: optionalText(form.ngon_ngu_dao_tao),
    chi_tieu_tuyen_sinh: optionalNumber(form.chi_tieu_tuyen_sinh),
    kieu_phan_bo_chi_tieu: optionalText(form.kieu_phan_bo_chi_tieu),
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
    const result = await importChuongTrinhDaoTao(
      {
        de_an_id: context.de_an_id,
        du_lieu: items,
      },
      { skipLoading: true, timeout: 120000 },
    )
    ElMessage.success(`Đã nhập ${result.created} chương trình đào tạo`)
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không nhập được chương trình đào tạo'))
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
      await updateChuongTrinhDaoTao(editingId.value, payload)
      ElMessage.success('Đã cập nhật chương trình đào tạo')
    } else {
      await createChuongTrinhDaoTao(payload)
      ElMessage.success('Đã thêm chương trình đào tạo')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được chương trình đào tạo'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa chương trình "${row.ten_chuong_trinh}"?`,
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
    await deleteChuongTrinhDaoTao(row.id)
    ElMessage.success('Đã xóa chương trình đào tạo')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được chương trình đào tạo'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} chương trình đào tạo đã chọn?`,
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
    const result = await deleteChuongTrinhDaoTaoMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} chương trình đào tạo`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các chương trình đào tạo đã chọn'))
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
          placeholder="Tìm mã xét tuyển, tên chương trình hoặc trường"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.truong_id"
          class="filter-school"
          placeholder="Trường"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in truongOptions"
            :key="item.id"
            :label="schoolLabel(item)"
            :value="item.id"
          />
        </CustomSelect>
        <CustomInput
          v-model="filters.nam_tuyen_sinh"
          class="filter-year"
          placeholder="Năm"
          clearable
          maxlength="4"
          @keyup.enter="onSearch"
          @clear="onSearch"
        />
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách chương trình đào tạo</h2>
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
            Thêm chương trình
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
        <CustomTableColumn prop="id" label="ID" width="110" align="center" />
        <CustomTableColumn label="Đề án" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ deAnOptionLabel(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ma_xet_tuyen" label="Mã xét tuyển" width="130" align="center">
          <template #default="{ row }">{{ row.ma_xet_tuyen || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_chuong_trinh" label="Tên chương trình" min-width="220" show-overflow-tooltip />
        <CustomTableColumn label="Trình độ" width="130">
          <template #default="{ row }">{{ codeLabel(row.trinh_do_dao_tao, TRINH_DO_LABELS) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Hình thức" width="150">
          <template #default="{ row }">{{ codeLabel(row.hinh_thuc_dao_tao, HINH_THUC_LABELS) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Ngành" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ nganhLabel(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Cơ sở" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ coSoLabel(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thời gian (năm)" width="140" align="center">
          <template #default="{ row }">{{ formatDuration(row.thoi_gian_dao_tao_nam) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ngon_ngu_dao_tao" label="Ngôn ngữ" width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.ngon_ngu_dao_tao || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Chỉ tiêu" width="110" align="right">
          <template #default="{ row }">{{ formatQuota(row.chi_tieu_tuyen_sinh) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="kieu_phan_bo_chi_tieu" label="Phân bổ chỉ tiêu" width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.kieu_phan_bo_chi_tieu || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="240" show-overflow-tooltip>
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
          <CustomEmpty description="Chưa có chương trình đào tạo nào." />
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
    :title="editingId ? 'Cập nhật chương trình đào tạo' : 'Thêm chương trình đào tạo'"
    width="90%"
    destroy-on-close
    @closed="resetForm"
  >
    <div class="json-meta">
      <div class="json-school">
        <span class="json-field__label">Trường</span>
        <CustomSelect
          v-model="context.truong_id"
          filterable
          placeholder="Chọn trường"
          style="width: 100%"
          @change="onContextFilterChange"
        >
          <CustomOption
            v-for="item in truongOptions"
            :key="item.id"
            :label="schoolLabel(item)"
            :value="item.id"
          />
        </CustomSelect>
      </div>
      <div class="json-year">
        <span class="json-field__label">Năm tuyển sinh</span>
        <CustomInputNumber
          v-model="context.nam_tuyen_sinh"
          :min="1990"
          :max="2100"
          :step="1"
          :controls="false"
          placeholder="Năm"
          style="width: 100%"
          @change="onContextFilterChange"
        />
      </div>
      <div class="json-proposal">
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
            :label="deAnOptionLabel(item)"
            :value="item.id"
          />
        </CustomSelect>
      </div>
    </div>
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
          Chọn trường, năm và đề án, rồi dán mảng JSON chương trình.
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
        :rows="22"
        :disabled="!context.de_an_id"
        placeholder="Chọn đề án tuyển sinh để dán JSON"
      />
    </div>

    <CustomForm v-else ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Mã xét tuyển" prop="ma_xet_tuyen">
            <CustomInput v-model="form.ma_xet_tuyen" maxlength="20" placeholder="Ví dụ BF1" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="16" :xs="24">
          <CustomFormItem label="Tên chương trình" prop="ten_chuong_trinh">
            <CustomInput v-model="form.ten_chuong_trinh" maxlength="255" placeholder="Tên chương trình hoặc ngành" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Trình độ đào tạo" prop="trinh_do_dao_tao">
            <CustomInput v-model="form.trinh_do_dao_tao" maxlength="30" placeholder="Ví dụ dai_hoc" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Hình thức đào tạo" prop="hinh_thuc_dao_tao">
            <CustomInput v-model="form.hinh_thuc_dao_tao" maxlength="30" placeholder="Ví dụ chinh_quy" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Chỉ tiêu" prop="chi_tieu_tuyen_sinh">
            <CustomInputNumber
              v-model="form.chi_tieu_tuyen_sinh"
              :min="0"
              :step="1"
              :controls="false"
              :value-on-clear="null"
              placeholder="Tổng chỉ tiêu"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Ngành đào tạo" prop="nganh_dao_tao_id">
            <CustomInputNumber
              v-model="form.nganh_dao_tao_id"
              :min="1"
              :step="1"
              :controls="false"
              :value-on-clear="null"
              placeholder="ID ngành, để trống nếu chưa map"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Cơ sở" prop="co_so_id">
            <CustomInputNumber
              v-model="form.co_so_id"
              :min="1"
              :step="1"
              :controls="false"
              :value-on-clear="null"
              placeholder="ID cơ sở thuộc đề án"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Thời gian đào tạo (năm)" prop="thoi_gian_dao_tao_nam">
            <CustomInputNumber
              v-model="form.thoi_gian_dao_tao_nam"
              :min="0"
              :max="999.9"
              :step="0.1"
              :precision="1"
              :controls="false"
              :value-on-clear="null"
              placeholder="Ví dụ 4"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Ngôn ngữ đào tạo" prop="ngon_ngu_dao_tao">
            <CustomInput v-model="form.ngon_ngu_dao_tao" maxlength="100" placeholder="Ngôn ngữ giảng dạy" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Kiểu phân bổ chỉ tiêu" prop="kieu_phan_bo_chi_tieu">
            <CustomInput v-model="form.kieu_phan_bo_chi_tieu" maxlength="30" placeholder="Phân bổ chỉ tiêu" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Ghi chú" prop="ghi_chu">
            <CustomInput
              v-model="form.ghi_chu"
              type="textarea"
              :rows="4"
              maxlength="20000"
              show-word-limit
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

.filter-search,
.filter-school {
  width: 280px;
}

.filter-year {
  width: 110px;
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
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 12px;
}

.json-school,
.json-proposal {
  flex: 1 1 280px;
  max-width: 420px;
}

.json-year {
  width: 160px;
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
  .json-school,
  .json-year,
  .json-proposal {
    width: 100%;
    max-width: none;
  }
}
</style>
