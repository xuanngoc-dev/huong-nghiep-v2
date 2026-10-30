<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createBangCapChungChi,
  createBangCapChungChiBulk,
  deleteBangCapChungChi,
  deleteBangCapChungChiMany,
  fetchBangCapChungChi,
  updateBangCapChungChi,
} from '@/api/bangCapChungChi'

const LOAI = [
  { value: 'trong_nuoc', label: 'Trong nước' },
  { value: 'quoc_te', label: 'Quốc tế' },
]
const TRANG_THAI = ['Hoạt động', 'Ngừng sử dụng']
const LIST_FIELDS = ['ky_nang_duoc_danh_gia', 'hinh_thuc_thi']
const SCORE_FIELDS = ['thang_diem_min', 'thang_diem_max']

const COLUMNS = [
  { key: 'ma_chung_chi', label: 'Mã', width: 120 },
  { key: 'ten_chung_chi', label: 'Tên chứng chỉ', minWidth: 180 },
  { key: 'ten_chi_tiet', label: 'Tên chi tiết', minWidth: 200 },
  { key: 'linh_vuc', label: 'Lĩnh vực', minWidth: 140 },
  { key: 'mon', label: 'Môn', minWidth: 120 },
  { key: 'ma_ngon_ngu', label: 'Mã ngôn ngữ', width: 130 },
  { key: 'ten_ngon_ngu', label: 'Tên ngôn ngữ', minWidth: 140 },
  { key: 'don_vi_cap', label: 'Đơn vị cấp', minWidth: 180 },
  { key: 'loai_chung_chi', label: 'Loại', width: 140 },
  { key: 'thang_diem', label: 'Thang điểm', width: 130 },
  { key: 'thang_diem_min', label: 'Điểm thấp nhất', width: 150, align: 'right' },
  { key: 'thang_diem_max', label: 'Điểm cao nhất', width: 150, align: 'right' },
  { key: 'don_vi_diem', label: 'Đơn vị điểm', width: 130 },
  { key: 'ky_nang_duoc_danh_gia', label: 'Kỹ năng đánh giá', minWidth: 180 },
  { key: 'hinh_thuc_thi', label: 'Hình thức thi', minWidth: 160 },
  { key: 'ghi_chu_hinh_thuc_thi', label: 'Ghi chú hình thức thi', minWidth: 200 },
  { key: 'thoi_han_hieu_luc_thang', label: 'Hiệu lực (tháng)', width: 200, align: 'right' },
  { key: 'trang_thai', label: 'Trạng thái', width: 150, align: 'center' },
  { key: 'ghi_chu', label: 'Ghi chú', minWidth: 160 },
  { key: 'tao_luc', label: 'Tạo lúc', width: 170, align: 'center' },
  { key: 'cap_nhat_luc', label: 'Cập nhật lúc', width: 170, align: 'center' },
]

const JSON_SAMPLE = `[
  {
    "ma_chung_chi": "IELTS",
    "ten_chung_chi": "IELTS Academic",
    "ten_chi_tiet": "International English Language Testing System",
    "linh_vuc": "Ngoại ngữ",
    "mon": "Tiếng Anh",
    "ma_ngon_ngu": "en",
    "ten_ngon_ngu": "Tiếng Anh",
    "loai_chung_chi": "quoc_te",
    "thang_diem": "0-9",
    "thang_diem_min": 0,
    "thang_diem_max": 9,
    "don_vi_diem": "band",
    "ky_nang_duoc_danh_gia": ["Nghe", "Nói", "Đọc", "Viết"],
    "hinh_thuc_thi": ["Giấy", "Máy tính"],
    "thoi_han_hieu_luc_thang": 24,
    "don_vi_cap": "British Council",
    "trang_thai": "Hoạt động",
    "ghi_chu": "Chứng chỉ quốc tế"
  },
  {
    "ma_chung_chi": "VSTEP",
    "ten_chung_chi": "VSTEP",
    "ten_chi_tiet": "Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam",
    "linh_vuc": "Ngoại ngữ",
    "mon": "Tiếng Anh",
    "ten_ngon_ngu": "Tiếng Anh",
    "loai_chung_chi": "trong_nuoc",
    "thang_diem": "Bậc 1-6",
    "thang_diem_min": 1,
    "thang_diem_max": 6,
    "don_vi_cap": "Bộ Giáo dục và Đào tạo"
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
const jsonImport = useJsonBatchImport({ label: 'bằng cấp chứng chỉ' })
const formRef = ref()

const filters = reactive({
  q: '',
  trang_thai: '',
  loai_chung_chi: '',
})

const form = reactive(emptyForm())

const rules = {
  ten_chung_chi: [{ required: true, message: 'Vui lòng nhập tên chứng chỉ', trigger: 'blur' }],
  ma_chung_chi: [{ required: true, message: 'Vui lòng nhập mã chứng chỉ', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_chung_chi: '',
    ten_chung_chi: '',
    ten_chi_tiet: '',
    linh_vuc: '',
    mon: '',
    ma_ngon_ngu: '',
    ten_ngon_ngu: '',
    don_vi_cap: '',
    loai_chung_chi: 'trong_nuoc',
    thang_diem: '',
    thang_diem_min: null,
    thang_diem_max: null,
    don_vi_diem: '',
    ky_nang_duoc_danh_gia: '',
    hinh_thuc_thi: '',
    ghi_chu_hinh_thuc_thi: '',
    thoi_han_hieu_luc_thang: null,
    trang_thai: 'Hoạt động',
    ghi_chu: '',
    tao_luc: '',
    cap_nhat_luc: '',
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

function optionalNumber(value) {
  if (value === null || value === undefined || value === '') return null
  const number = Number(value)
  return Number.isFinite(number) ? number : null
}

function optionalInt(value) {
  if (value === null || value === undefined || value === '') return null
  const number = Number(value)
  return Number.isInteger(number) ? number : null
}

function loaiLabel(value) {
  return LOAI.find((item) => item.value === value)?.label || value || '—'
}

function listToText(value) {
  if (!Array.isArray(value) || !value.length) return ''
  return value.join(', ')
}

function parseList(value, line, label) {
  if (value == null || value === '') return null
  let items = value
  if (typeof value === 'string') {
    const text = value.trim()
    if (!text) return null
    if (text.startsWith('[')) {
      try {
        items = JSON.parse(text)
      } catch {
        throw new Error(line ? `Phần tử thứ ${line}: ${label} không phải JSON hợp lệ` : `${label} không phải JSON hợp lệ`)
      }
    } else {
      items = text.split(',')
    }
  }
  if (!Array.isArray(items)) {
    throw new Error(line ? `Phần tử thứ ${line}: ${label} phải là mảng chuỗi` : `${label} phải là mảng chuỗi`)
  }
  const cleaned = []
  for (const item of items) {
    const text = String(item ?? '').trim()
    if (text) cleaned.push(text)
  }
  return cleaned.length ? cleaned : null
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng bằng cấp chứng chỉ.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_chung_chi": "...", "ma_chung_chi": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng bằng cấp chứng chỉ đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một bằng cấp chứng chỉ`)
    }
    const ten = String(item.ten_chung_chi ?? '').trim()
    const ma = String(item.ma_chung_chi ?? '').trim()
    if (!ten || !ma) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_chung_chi hoặc ma_chung_chi`)
    }
    const thangMin = optionalNumber(item.thang_diem_min)
    const thangMax = optionalNumber(item.thang_diem_max)
    if (thangMin != null && thangMax != null && thangMax < thangMin) {
      throw new Error(`Phần tử thứ ${line}: điểm cao nhất phải lớn hơn hoặc bằng điểm thấp nhất`)
    }
    return {
      ten_chung_chi: ten,
      ma_chung_chi: ma,
      ten_chi_tiet: optionalText(item.ten_chi_tiet),
      linh_vuc: optionalText(item.linh_vuc),
      mon: optionalText(item.mon),
      ma_ngon_ngu: optionalText(item.ma_ngon_ngu),
      ten_ngon_ngu: optionalText(item.ten_ngon_ngu),
      loai_chung_chi: optionalText(item.loai_chung_chi),
      thang_diem: optionalText(item.thang_diem),
      thang_diem_min: thangMin,
      thang_diem_max: thangMax,
      don_vi_diem: optionalText(item.don_vi_diem),
      ky_nang_duoc_danh_gia: parseList(item.ky_nang_duoc_danh_gia, line, 'Kỹ năng được đánh giá'),
      hinh_thuc_thi: parseList(item.hinh_thuc_thi, line, 'Hình thức thi'),
      ghi_chu_hinh_thuc_thi: optionalText(item.ghi_chu_hinh_thuc_thi),
      thoi_han_hieu_luc_thang: optionalInt(item.thoi_han_hieu_luc_thang),
      don_vi_cap: optionalText(item.don_vi_cap),
      trang_thai: item.trang_thai ?? 'Hoạt động',
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

function formatDateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatCell(row, column) {
  const value = row[column.key]
  if (LIST_FIELDS.includes(column.key)) return dash(listToText(value))
  if (column.key === 'loai_chung_chi') return loaiLabel(value)
  if (column.key === 'tao_luc' || column.key === 'cap_nhat_luc') return formatDateTime(value)
  if (SCORE_FIELDS.includes(column.key) && value != null && value !== '') return value
  return dash(value)
}

function statusType(value) {
  if (value === 'Hoạt động' || value === 1 || value === '1') return 'success'
  if (value === 'Ngừng sử dụng' || value === 0 || value === '0') return 'info'
  return 'warning'
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai) params.trang_thai = filters.trang_thai
    if (filters.loai_chung_chi) params.loai_chung_chi = filters.loai_chung_chi
    const data = await fetchBangCapChungChi(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách bằng cấp chứng chỉ'))
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
    ma_chung_chi: row.ma_chung_chi || '',
    ten_chung_chi: row.ten_chung_chi || '',
    ten_chi_tiet: row.ten_chi_tiet || '',
    linh_vuc: row.linh_vuc || '',
    mon: row.mon || '',
    ma_ngon_ngu: row.ma_ngon_ngu || '',
    ten_ngon_ngu: row.ten_ngon_ngu || '',
    don_vi_cap: row.don_vi_cap || '',
    loai_chung_chi: row.loai_chung_chi || '',
    thang_diem: row.thang_diem || '',
    thang_diem_min: row.thang_diem_min,
    thang_diem_max: row.thang_diem_max,
    don_vi_diem: row.don_vi_diem || '',
    ky_nang_duoc_danh_gia: listToText(row.ky_nang_duoc_danh_gia),
    hinh_thuc_thi: listToText(row.hinh_thuc_thi),
    ghi_chu_hinh_thuc_thi: row.ghi_chu_hinh_thuc_thi || '',
    thoi_han_hieu_luc_thang: row.thoi_han_hieu_luc_thang,
    trang_thai: row.trang_thai || 'Hoạt động',
    ghi_chu: row.ghi_chu || '',
    tao_luc: row.tao_luc,
    cap_nhat_luc: row.cap_nhat_luc,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_chung_chi: form.ma_chung_chi.trim().toUpperCase(),
    ten_chung_chi: form.ten_chung_chi.trim(),
    ten_chi_tiet: optionalText(form.ten_chi_tiet),
    linh_vuc: optionalText(form.linh_vuc),
    mon: optionalText(form.mon),
    ma_ngon_ngu: optionalText(form.ma_ngon_ngu),
    ten_ngon_ngu: optionalText(form.ten_ngon_ngu),
    don_vi_cap: optionalText(form.don_vi_cap),
    loai_chung_chi: optionalText(form.loai_chung_chi),
    thang_diem: optionalText(form.thang_diem),
    thang_diem_min: optionalNumber(form.thang_diem_min),
    thang_diem_max: optionalNumber(form.thang_diem_max),
    don_vi_diem: optionalText(form.don_vi_diem),
    ky_nang_duoc_danh_gia: parseList(form.ky_nang_duoc_danh_gia, null, 'Kỹ năng được đánh giá'),
    hinh_thuc_thi: parseList(form.hinh_thuc_thi, null, 'Hình thức thi'),
    ghi_chu_hinh_thuc_thi: optionalText(form.ghi_chu_hinh_thuc_thi),
    thoi_han_hieu_luc_thang: optionalInt(form.thoi_han_hieu_luc_thang),
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
    createBatch: createBangCapChungChiBulk,
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
  if (
    form.thang_diem_min != null
    && form.thang_diem_max != null
    && Number(form.thang_diem_max) < Number(form.thang_diem_min)
  ) {
    ElMessage.error('Điểm cao nhất phải lớn hơn hoặc bằng điểm thấp nhất')
    return
  }

  saving.value = true
  try {
    const payload = payloadFromForm()
    if (editingId.value) {
      await updateBangCapChungChi(editingId.value, payload)
      ElMessage.success('Đã cập nhật bằng cấp chứng chỉ')
    } else {
      await createBangCapChungChi(payload)
      ElMessage.success('Đã thêm bằng cấp chứng chỉ')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được bằng cấp chứng chỉ'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa bằng cấp chứng chỉ "${row.ten_chung_chi}" (${row.ma_chung_chi})?`,
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
    await deleteBangCapChungChi(row.id)
    ElMessage.success('Đã xóa bằng cấp chứng chỉ')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được bằng cấp chứng chỉ'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} bằng cấp chứng chỉ đã chọn?`, 'Xác nhận xóa', {
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
    const result = await deleteBangCapChungChiMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} bằng cấp chứng chỉ`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các bằng cấp chứng chỉ đã chọn'))
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
          placeholder="Tìm tên, mã, lĩnh vực, môn hoặc ngôn ngữ"
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
          filterable
          allow-create
          default-first-option
          @change="onSearch"
        >
          <CustomOption v-for="item in LOAI" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.trang_thai"
          class="filter-status"
          placeholder="Trạng thái"
          clearable
          filterable
          allow-create
          default-first-option
          @change="onSearch"
        >
          <CustomOption v-for="item in TRANG_THAI" :key="item" :label="item" :value="item" />
        </CustomSelect>
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách bằng cấp chứng chỉ</h2>
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
            Thêm bằng cấp
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
        <CustomTableColumn
          v-for="column in COLUMNS"
          :key="column.key"
          :prop="column.key"
          :label="column.label"
          :width="column.width"
          :min-width="column.minWidth"
          :align="column.align"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <CustomTag
              v-if="column.key === 'trang_thai' && row.trang_thai"
              :type="statusType(row.trang_thai)"
              effect="light"
            >
              {{ row.trang_thai }}
            </CustomTag>
            <span v-else>{{ formatCell(row, column) }}</span>
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
          <CustomEmpty description="Chưa có bằng cấp chứng chỉ nào." />
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
    :title="editingId ? 'Cập nhật bằng cấp chứng chỉ' : 'Thêm bằng cấp chứng chỉ'"
    width="1080px"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_chung_chi</code> và <code>ma_chung_chi</code>.
          <code>loai_chung_chi</code> dùng <code>trong_nuoc</code> hoặc <code>quoc_te</code>.
          Kỹ năng và hình thức thi là mảng chuỗi.
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
          <CustomFormItem label="Tên chứng chỉ" prop="ten_chung_chi">
            <CustomInput v-model="form.ten_chung_chi" maxlength="255" placeholder="Ví dụ: IELTS Academic" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Mã chứng chỉ" prop="ma_chung_chi">
            <CustomInput v-model="form.ma_chung_chi" maxlength="50" placeholder="Ví dụ: IELTS" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Loại">
            <CustomSelect v-model="form.loai_chung_chi" filterable allow-create default-first-option clearable style="width: 100%">
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
          <CustomFormItem label="Mã ngôn ngữ">
            <CustomInput v-model="form.ma_ngon_ngu" maxlength="10" placeholder="Ví dụ: en" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Tên ngôn ngữ">
            <CustomInput v-model="form.ten_ngon_ngu" maxlength="100" placeholder="Ví dụ: Tiếng Anh" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Đơn vị cấp">
            <CustomInput v-model="form.don_vi_cap" maxlength="255" placeholder="Ví dụ: British Council" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" filterable allow-create default-first-option style="width: 100%">
              <CustomOption v-for="item in TRANG_THAI" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Thang điểm">
            <CustomInput v-model="form.thang_diem" maxlength="100" placeholder="Ví dụ: 0-9" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Điểm thấp nhất">
            <CustomInputNumber
              v-model="form.thang_diem_min"
              :min="0"
              :max="9999.99"
              :precision="2"
              :step="0.5"
              :value-on-clear="null"
              controls-position="right"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Điểm cao nhất">
            <CustomInputNumber
              v-model="form.thang_diem_max"
              :min="0"
              :max="9999.99"
              :precision="2"
              :step="0.5"
              :value-on-clear="null"
              controls-position="right"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Đơn vị điểm">
            <CustomInput v-model="form.don_vi_diem" maxlength="30" placeholder="Ví dụ: band" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Hiệu lực (tháng)">
            <CustomInputNumber
              v-model="form.thoi_han_hieu_luc_thang"
              :min="0"
              :max="65535"
              :precision="0"
              :step="1"
              :value-on-clear="null"
              controls-position="right"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Tên chi tiết">
            <CustomInput v-model="form.ten_chi_tiet" maxlength="500" placeholder="Tên đầy đủ hoặc mô tả ngắn" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Kỹ năng được đánh giá">
            <CustomInput
              v-model="form.ky_nang_duoc_danh_gia"
              type="textarea"
              :rows="2"
              maxlength="5000"
              placeholder="Phân tách bằng dấu phẩy. Ví dụ: Nghe, Nói, Đọc, Viết"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Hình thức thi">
            <CustomInput
              v-model="form.hinh_thuc_thi"
              type="textarea"
              :rows="2"
              maxlength="5000"
              placeholder="Phân tách bằng dấu phẩy. Ví dụ: Giấy, Máy tính"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Ghi chú hình thức thi">
            <CustomInput
              v-model="form.ghi_chu_hinh_thuc_thi"
              type="textarea"
              :rows="2"
              maxlength="2000"
              placeholder="Mô tả hoặc lưu ý về hình thức thi"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-if="editingId" :span="12" :xs="24">
          <CustomFormItem label="Tạo lúc">
            <CustomInput :model-value="formatDateTime(form.tao_luc)" disabled />
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-if="editingId" :span="12" :xs="24">
          <CustomFormItem label="Cập nhật lúc">
            <CustomInput :model-value="formatDateTime(form.cap_nhat_luc)" disabled />
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
  width: 320px;
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
