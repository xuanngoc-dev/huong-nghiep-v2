<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createTruongHoc,
  createTruongHocBulk,
  deleteTruongHoc,
  deleteTruongHocMany,
  fetchTruongHoc,
  updateTruongHoc,
} from '@/api/truongHoc'
import { collectAllPages, downloadExcel } from '@/utils/excelExport'
import {
  TRUONG_HOC_EXPORT_COLUMNS,
  truongHocExportFilename,
  truongHocExportRows,
  truongHocListParams,
} from '@/utils/truongHocExport'

const LOAI_CO_SO = ['Cao đẳng', 'Trường đại học', 'Đại học', 'Học viện']
const LOAI_HINH = ['Công lập', 'Tư thục', 'Có vốn đầu tư nước ngoài']
const TRANG_THAI = ['Đang hoạt động', 'Ngừng hoạt động']
const VUNG_MIEN = ['Bắc', 'Trung', 'Nam']

const TEXT_FIELDS = [
  'ten_tieng_anh',
  'ten_viet_tat',
  'slug',
  'loai_co_so',
  'loai_hinh',
  'co_quan_chu_quan',
  'gioi_thieu_ngan',
  'gioi_thieu_chi_tiet',
  'the_manh',
  'ma_tinh_thanh',
  'ten_tinh_thanh',
  'ma_phuong_xa',
  'ten_phuong_xa',
  'dia_chi_tru_so',
  'vung_mien',
  'so_dien_thoai',
  'email',
  'website',
  'website_tuyen_sinh',
  'hotline_tuyen_sinh',
  'email_tuyen_sinh',
  'logo_url',
  'anh_dai_dien_url',
  'hoc_phi_trung_binh',
  'trang_thai_hoat_dong',
  'nguon_du_lieu_url',
  'ghi_chu',
]
const LIST_FIELDS = ['ten_goi_khac', 'bac_dao_tao', 'linh_vuc_dao_tao_chinh', 'linh_vuc_dao_tao_khac']
const LIST_LABELS = {
  ten_goi_khac: 'Tên gọi khác',
  bac_dao_tao: 'Bậc đào tạo',
  linh_vuc_dao_tao_chinh: 'Lĩnh vực đào tạo chính',
  linh_vuc_dao_tao_khac: 'Lĩnh vực đào tạo khác',
}

const COLUMNS = [
  { key: 'ma_truong', label: 'Mã', width: 110 },
  { key: 'ten_truong', label: 'Tên trường', minWidth: 240 },
  { key: 'ten_tieng_anh', label: 'Tên tiếng Anh', minWidth: 220 },
  { key: 'ten_viet_tat', label: 'Viết tắt', width: 120 },
  { key: 'ten_goi_khac', label: 'Tên gọi khác', minWidth: 180 },
  { key: 'slug', label: 'Slug', minWidth: 160 },
  { key: 'loai_co_so', label: 'Loại cơ sở', width: 150 },
  { key: 'loai_hinh', label: 'Loại hình', width: 180 },
  { key: 'co_quan_chu_quan', label: 'Cơ quan chủ quản', minWidth: 180 },
  { key: 'truong_cha_id', label: 'Trường trực thuộc', width: 250, align: 'center' },
  { key: 'ngay_thanh_lap', label: 'Ngày thành lập', width: 140, align: 'center' },
  { key: 'nam_thanh_lap', label: 'Năm thành lập', width: 150, align: 'center' },
  { key: 'gioi_thieu_ngan', label: 'Giới thiệu ngắn', minWidth: 220 },
  { key: 'gioi_thieu_chi_tiet', label: 'Giới thiệu chi tiết', minWidth: 240 },
  { key: 'the_manh', label: 'Thế mạnh', minWidth: 200 },
  { key: 'bac_dao_tao', label: 'Bậc đào tạo', minWidth: 180 },
  { key: 'linh_vuc_dao_tao_chinh', label: 'Lĩnh vực đào tạo chính', minWidth: 220 },
  { key: 'linh_vuc_dao_tao_khac', label: 'Lĩnh vực đào tạo khác', minWidth: 220 },
  { key: 'ma_tinh_thanh', label: 'Mã tỉnh/thành', width: 140 },
  { key: 'ten_tinh_thanh', label: 'Tỉnh/thành', minWidth: 150 },
  { key: 'ma_phuong_xa', label: 'Mã phường/xã', width: 140 },
  { key: 'ten_phuong_xa', label: 'Phường/xã', minWidth: 150 },
  { key: 'dia_chi_tru_so', label: 'Địa chỉ trụ sở', minWidth: 240 },
  { key: 'vung_mien', label: 'Vùng miền', width: 120 },
  { key: 'vi_do', label: 'Vĩ độ', width: 120, align: 'right' },
  { key: 'kinh_do', label: 'Kinh độ', width: 120, align: 'right' },
  { key: 'so_dien_thoai', label: 'Số điện thoại', minWidth: 150 },
  { key: 'email', label: 'Email', minWidth: 200 },
  { key: 'website', label: 'Website', minWidth: 200 },
  { key: 'website_tuyen_sinh', label: 'Website tuyển sinh', minWidth: 200 },
  { key: 'hotline_tuyen_sinh', label: 'Hotline tuyển sinh', minWidth: 200 },
  { key: 'email_tuyen_sinh', label: 'Email tuyển sinh', minWidth: 200 },
  { key: 'logo_url', label: 'Logo', minWidth: 180 },
  { key: 'anh_dai_dien_url', label: 'Ảnh đại diện', minWidth: 180 },
  { key: 'dien_tich_m2', label: 'Diện tích (m²)', width: 140, align: 'right' },
  { key: 'hoc_phi_trung_binh', label: 'Học phí trung bình', minWidth: 200 },
  { key: 'trang_thai_hoat_dong', label: 'Trạng thái', width: 160 },
  { key: 'nguon_du_lieu_url', label: 'Nguồn dữ liệu', minWidth: 200 },
  { key: 'ngay_xac_minh', label: 'Ngày xác minh', width: 170, align: 'center' },
  { key: 'ghi_chu', label: 'Ghi chú', minWidth: 200 },
  { key: 'tao_luc', label: 'Tạo lúc', width: 170, align: 'center' },
  { key: 'cap_nhat_luc', label: 'Cập nhật lúc', width: 170, align: 'center' },
]

const JSON_SAMPLE = `[
  {
    "ma_truong": "BKA",
    "ten_truong": "Đại học Bách khoa Hà Nội",
    "ten_viet_tat": "HUST",
    "ten_tieng_anh": "Hanoi University of Science and Technology",
    "ten_goi_khac": ["ĐHBK Hà Nội"],
    "slug": "dai-hoc-bach-khoa-ha-noi",
    "loai_co_so": "Đại học",
    "loai_hinh": "Công lập",
    "co_quan_chu_quan": "Bộ Giáo dục và Đào tạo",
    "nam_thanh_lap": 1956,
    "gioi_thieu_ngan": "Trường đại học kỹ thuật.",
    "bac_dao_tao": ["Đại học", "Thạc sĩ", "Tiến sĩ"],
    "linh_vuc_dao_tao_chinh": ["Kỹ thuật", "Công nghệ"],
    "linh_vuc_dao_tao_khac": ["Kinh tế", "Ngoại ngữ"],
    "ten_tinh_thanh": "Hà Nội",
    "dia_chi_tru_so": "Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội",
    "vung_mien": "Bắc",
    "website": "https://hust.edu.vn",
    "email": "hust@hust.edu.vn",
    "so_dien_thoai": "02438694242",
    "trang_thai_hoat_dong": "Đang hoạt động"
  }
]`

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const exporting = ref(false)
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
const jsonImport = useJsonBatchImport({ label: 'trường học' })
const formRef = ref()

const filters = reactive({
  q: '',
  vung_mien: '',
  loai_co_so: '',
  loai_hinh: '',
  trang_thai_hoat_dong: '',
})

const form = reactive(emptyForm())

const rules = {
  ten_truong: [{ required: true, message: 'Vui lòng nhập tên trường', trigger: 'blur' }],
  ma_truong: [{ required: true, message: 'Vui lòng nhập mã trường', trigger: 'blur' }],
  email: [emailRule()],
  email_tuyen_sinh: [emailRule()],
  nam_thanh_lap: [yearRule()],
  vi_do: [rangeRule('Vĩ độ', -90, 90)],
  kinh_do: [rangeRule('Kinh độ', -180, 180)],
  dien_tich_m2: [
    {
      validator: (_rule, value, callback) => {
        if (value === null || value === undefined || value === '') {
          callback()
          return
        }
        const number = Number(value)
        if (!Number.isFinite(number) || number < 0) {
          callback(new Error('Diện tích không được âm'))
          return
        }
        callback()
      },
      trigger: 'change',
    },
  ],
  truong_cha_id: [
    {
      validator: (_rule, value, callback) => {
        if (value === null || value === undefined || value === '') {
          callback()
          return
        }
        const id = Number(value)
        if (!Number.isInteger(id) || id < 1) {
          callback(new Error('ID trường trực thuộc phải là số nguyên dương'))
          return
        }
        callback()
      },
      trigger: 'change',
    },
  ],
}

function emailRule() {
  return {
    validator: (_rule, value, callback) => {
      const text = String(value || '').trim()
      if (!text || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(text)) {
        callback()
        return
      }
      callback(new Error('Email không hợp lệ'))
    },
    trigger: 'blur',
  }
}

function yearRule() {
  return {
    validator: (_rule, value, callback) => {
      if (value === null || value === undefined || value === '') {
        callback()
        return
      }
      const year = Number(value)
      if (!Number.isInteger(year) || year < 1000 || year > 2100) {
        callback(new Error('Năm thành lập từ 1000 đến 2100'))
        return
      }
      callback()
    },
    trigger: 'change',
  }
}

function rangeRule(label, min, max) {
  return {
    validator: (_rule, value, callback) => {
      if (value === null || value === undefined || value === '') {
        callback()
        return
      }
      const number = Number(value)
      if (!Number.isFinite(number) || number < min || number > max) {
        callback(new Error(`${label} từ ${min} đến ${max}`))
        return
      }
      callback()
    },
    trigger: 'change',
  }
}

function emptyForm() {
  const next = {
    ma_truong: '',
    ten_truong: '',
    truong_cha_id: null,
    nam_thanh_lap: null,
    vi_do: null,
    kinh_do: null,
    dien_tich_m2: null,
    ngay_thanh_lap: '',
    ngay_xac_minh: '',
  }
  for (const key of TEXT_FIELDS) next[key] = ''
  for (const key of LIST_FIELDS) next[key] = ''
  return next
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

function optionalYear(value) {
  if (value === null || value === undefined || value === '') return null
  const year = Number(value)
  return Number.isFinite(year) ? year : null
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
    throw new Error('JSON không hợp lệ. Hãy dán một mảng trường học.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_truong": "...", "ma_truong": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng trường học đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một trường học`)
    }
    const ten = String(item.ten_truong ?? '').trim()
    const ma = String(item.ma_truong ?? '').trim()
    if (!ten || !ma) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_truong hoặc ma_truong`)
    }
    const payload = {
      ma_truong: ma,
      ten_truong: ten,
      truong_cha_id: optionalInt(item.truong_cha_id),
      nam_thanh_lap: optionalYear(item.nam_thanh_lap),
      vi_do: optionalNumber(item.vi_do),
      kinh_do: optionalNumber(item.kinh_do),
      dien_tich_m2: optionalNumber(item.dien_tich_m2),
      ngay_thanh_lap: optionalText(item.ngay_thanh_lap),
      ngay_xac_minh: optionalText(item.ngay_xac_minh),
    }
    for (const key of TEXT_FIELDS) payload[key] = optionalText(item[key])
    for (const key of LIST_FIELDS) payload[key] = parseList(item[key], line, LIST_LABELS[key])
    return payload
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

function formatList(value) {
  if (!Array.isArray(value) || !value.length) return '—'
  return value.join(', ')
}

function formatDate(value) {
  if (!value) return '—'
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (!match) return String(value)
  return `${match[3]}/${match[2]}/${match[1]}`
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

function formatNumber(value) {
  if (value === null || value === undefined || value === '') return '—'
  const number = Number(value)
  if (!Number.isFinite(number)) return String(value)
  return number.toLocaleString('vi-VN', { maximumFractionDigits: 7 })
}

function formatCell(row, column) {
  const value = row[column.key]
  if (LIST_FIELDS.includes(column.key)) return formatList(value)
  if (column.key === 'ngay_thanh_lap') return formatDate(value)
  if (column.key === 'ngay_xac_minh' || column.key === 'tao_luc' || column.key === 'cap_nhat_luc') {
    return formatDateTime(value)
  }
  if (column.key === 'vi_do' || column.key === 'kinh_do' || column.key === 'dien_tich_m2') {
    return formatNumber(value)
  }
  return dash(value)
}

function toDateInput(value) {
  if (!value) return ''
  const match = String(value).match(/^(\d{4}-\d{2}-\d{2})/)
  return match ? match[1] : ''
}

function toDateTimeInput(value) {
  if (!value) return ''
  const match = String(value).replace('T', ' ').match(/^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})/)
  return match ? `${match[1]} ${match[2]}:00` : ''
}

async function load() {
  loading.value = true
  try {
    const data = await fetchTruongHoc(truongHocListParams(filters, { page: page.value, pageSize: pageSize.value }))
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách trường học'))
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
  const next = emptyForm()
  next.ma_truong = row.ma_truong
  next.ten_truong = row.ten_truong
  next.truong_cha_id = row.truong_cha_id
  next.nam_thanh_lap = row.nam_thanh_lap
  next.vi_do = row.vi_do
  next.kinh_do = row.kinh_do
  next.dien_tich_m2 = row.dien_tich_m2
  next.ngay_thanh_lap = toDateInput(row.ngay_thanh_lap)
  next.ngay_xac_minh = toDateTimeInput(row.ngay_xac_minh)
  for (const key of TEXT_FIELDS) next[key] = row[key] || ''
  for (const key of LIST_FIELDS) next[key] = listToText(row[key])
  Object.assign(form, next)
  dialogVisible.value = true
}

function payloadFromForm() {
  const payload = {
    ma_truong: form.ma_truong.trim().toUpperCase(),
    ten_truong: form.ten_truong.trim(),
    truong_cha_id: optionalInt(form.truong_cha_id),
    nam_thanh_lap: optionalYear(form.nam_thanh_lap),
    vi_do: optionalNumber(form.vi_do),
    kinh_do: optionalNumber(form.kinh_do),
    dien_tich_m2: optionalNumber(form.dien_tich_m2),
    ngay_thanh_lap: optionalText(form.ngay_thanh_lap),
    ngay_xac_minh: optionalText(form.ngay_xac_minh),
  }
  for (const key of TEXT_FIELDS) payload[key] = optionalText(form[key])
  for (const key of LIST_FIELDS) payload[key] = parseList(form[key], 0, LIST_LABELS[key])
  return payload
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
    createBatch: createTruongHocBulk,
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

  let payload
  try {
    payload = payloadFromForm()
  } catch (error) {
    ElMessage.error(error.message)
    return
  }

  saving.value = true
  try {
    if (editingId.value) {
      await updateTruongHoc(editingId.value, payload)
      ElMessage.success('Đã cập nhật trường học')
    } else {
      await createTruongHoc(payload)
      ElMessage.success('Đã thêm trường học')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được trường học'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa trường "${row.ten_truong}" (${row.ma_truong})?`,
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
    await deleteTruongHoc(row.id)
    ElMessage.success('Đã xóa trường học')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được trường học'))
  }
}

async function onExport() {
  exporting.value = true
  try {
    const items = await collectAllPages((paging) => fetchTruongHoc(truongHocListParams(filters, paging)))
    if (!items.length) {
      ElMessage.warning('Không có trường học nào khớp bộ lọc để xuất')
      return
    }
    await downloadExcel({
      filename: truongHocExportFilename(),
      sheetName: 'Trường học',
      columns: TRUONG_HOC_EXPORT_COLUMNS,
      rows: truongHocExportRows(items),
    })
    ElMessage.success(`Đã xuất ${items.length} trường học`)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xuất được file Excel'))
  } finally {
    exporting.value = false
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} trường học đã chọn?`, 'Xác nhận xóa', {
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
    const result = await deleteTruongHocMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} trường học`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các trường học đã chọn'))
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
          placeholder="Tìm tên, mã, viết tắt, tên tiếng Anh hoặc tỉnh/thành"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.vung_mien"
          class="filter-status"
          placeholder="Vùng miền"
          clearable
          filterable
          allow-create
          default-first-option
          @change="onSearch"
        >
          <CustomOption v-for="item in VUNG_MIEN" :key="item" :label="item" :value="item" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.loai_co_so"
          class="filter-status"
          placeholder="Loại cơ sở"
          clearable
          filterable
          allow-create
          default-first-option
          @change="onSearch"
        >
          <CustomOption v-for="item in LOAI_CO_SO" :key="item" :label="item" :value="item" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.loai_hinh"
          class="filter-status"
          placeholder="Loại hình"
          clearable
          filterable
          allow-create
          default-first-option
          @change="onSearch"
        >
          <CustomOption v-for="item in LOAI_HINH" :key="item" :label="item" :value="item" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.trang_thai_hoat_dong"
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
        <h2 class="toolbar__title">Danh sách trường học</h2>
        <div class="toolbar__actions">
          <CustomButton :loading="exporting" @click="onExport">
            <CustomIcon><Download /></CustomIcon>
            Xuất Excel
          </CustomButton>
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
            Thêm trường
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
          <template #default="{ row }">{{ formatCell(row, column) }}</template>
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
          <CustomEmpty description="Chưa có trường học nào." />
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
    :title="editingId ? 'Cập nhật trường học' : 'Thêm trường học'"
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
          Dán một mảng JSON. Mỗi phần tử cần <code>ten_truong</code> và <code>ma_truong</code>.
          Các danh sách như <code>linh_vuc_dao_tao_chinh</code> là mảng chuỗi.
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
          <CustomFormItem label="Mã trường" prop="ma_truong">
            <CustomInput v-model="form.ma_truong" maxlength="20" placeholder="Ví dụ: BKA" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Tên viết tắt">
            <CustomInput v-model="form.ten_viet_tat" maxlength="50" placeholder="Ví dụ: HUST" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Slug">
            <CustomInput v-model="form.slug" maxlength="255" placeholder="dai-hoc-bach-khoa-ha-noi" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Tên trường" prop="ten_truong">
            <CustomInput v-model="form.ten_truong" maxlength="255" placeholder="Tên đầy đủ tiếng Việt" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Tên tiếng Anh">
            <CustomInput v-model="form.ten_tieng_anh" maxlength="255" placeholder="Tên tiếng Anh" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Tên gọi khác">
            <CustomInput v-model="form.ten_goi_khac" maxlength="5000" placeholder="Phân tách bằng dấu phẩy" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Loại cơ sở">
            <CustomSelect v-model="form.loai_co_so" filterable allow-create default-first-option clearable placeholder="Chọn hoặc nhập" style="width: 100%">
              <CustomOption v-for="item in LOAI_CO_SO" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Loại hình">
            <CustomSelect v-model="form.loai_hinh" filterable allow-create default-first-option clearable placeholder="Chọn hoặc nhập" style="width: 100%">
              <CustomOption v-for="item in LOAI_HINH" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Trạng thái hoạt động">
            <CustomSelect v-model="form.trang_thai_hoat_dong" filterable allow-create default-first-option clearable placeholder="Chọn hoặc nhập" style="width: 100%">
              <CustomOption v-for="item in TRANG_THAI" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Cơ quan chủ quản">
            <CustomInput v-model="form.co_quan_chu_quan" maxlength="255" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="ID trường trực thuộc" prop="truong_cha_id">
            <CustomInputNumber v-model="form.truong_cha_id" :min="1" :step="1" :precision="0" :value-on-clear="null" controls-position="right" style="width: 100%" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Năm thành lập" prop="nam_thanh_lap">
            <CustomInputNumber v-model="form.nam_thanh_lap" :min="1000" :max="2100" :step="1" :precision="0" :value-on-clear="null" controls-position="right" style="width: 100%" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Ngày thành lập">
            <CustomDatePicker v-model="form.ngay_thanh_lap" type="date" value-format="YYYY-MM-DD" format="DD/MM/YYYY" placeholder="Chọn ngày" clearable style="width: 100%" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="6" :xs="12">
          <CustomFormItem label="Mã tỉnh/thành">
            <CustomInput v-model="form.ma_tinh_thanh" maxlength="10" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="6" :xs="12">
          <CustomFormItem label="Tỉnh/thành">
            <CustomInput v-model="form.ten_tinh_thanh" maxlength="100" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="6" :xs="12">
          <CustomFormItem label="Mã phường/xã">
            <CustomInput v-model="form.ma_phuong_xa" maxlength="10" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="6" :xs="12">
          <CustomFormItem label="Phường/xã">
            <CustomInput v-model="form.ten_phuong_xa" maxlength="100" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="16" :xs="24">
          <CustomFormItem label="Địa chỉ trụ sở">
            <CustomInput v-model="form.dia_chi_tru_so" maxlength="500" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Vùng miền">
            <CustomSelect v-model="form.vung_mien" filterable allow-create default-first-option clearable placeholder="Chọn hoặc nhập" style="width: 100%">
              <CustomOption v-for="item in VUNG_MIEN" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Vĩ độ" prop="vi_do">
            <CustomInputNumber v-model="form.vi_do" :min="-90" :max="90" :step="0.000001" :precision="7" :value-on-clear="null" controls-position="right" style="width: 100%" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Kinh độ" prop="kinh_do">
            <CustomInputNumber v-model="form.kinh_do" :min="-180" :max="180" :step="0.000001" :precision="7" :value-on-clear="null" controls-position="right" style="width: 100%" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Diện tích (m²)" prop="dien_tich_m2">
            <CustomInputNumber v-model="form.dien_tich_m2" :min="0" :step="1" :precision="2" :value-on-clear="null" controls-position="right" style="width: 100%" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Học phí trung bình">
            <CustomInput v-model="form.hoc_phi_trung_binh" maxlength="100" placeholder="Ví dụ: 25-35 triệu/năm" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Số điện thoại">
            <CustomInput v-model="form.so_dien_thoai" maxlength="30" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Email" prop="email">
            <CustomInput v-model="form.email" maxlength="255" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Website">
            <CustomInput v-model="form.website" maxlength="500" placeholder="https://..." />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Hotline tuyển sinh">
            <CustomInput v-model="form.hotline_tuyen_sinh" maxlength="30" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Email tuyển sinh" prop="email_tuyen_sinh">
            <CustomInput v-model="form.email_tuyen_sinh" maxlength="255" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Website tuyển sinh">
            <CustomInput v-model="form.website_tuyen_sinh" maxlength="500" placeholder="https://..." />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Logo">
            <CustomInput v-model="form.logo_url" maxlength="1000" placeholder="URL logo" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Ảnh đại diện">
            <CustomInput v-model="form.anh_dai_dien_url" maxlength="1000" placeholder="URL ảnh khuôn viên" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="16" :xs="24">
          <CustomFormItem label="Nguồn dữ liệu">
            <CustomInput v-model="form.nguon_du_lieu_url" maxlength="1000" placeholder="URL nguồn xác minh" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Ngày xác minh">
            <CustomDatePicker v-model="form.ngay_xac_minh" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" format="DD/MM/YYYY HH:mm" placeholder="Chọn thời điểm" clearable style="width: 100%" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Bậc đào tạo">
            <CustomInput v-model="form.bac_dao_tao" type="textarea" :rows="2" maxlength="5000" placeholder="Phân tách bằng dấu phẩy. Ví dụ: Đại học, Thạc sĩ" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Lĩnh vực đào tạo chính">
            <CustomInput v-model="form.linh_vuc_dao_tao_chinh" type="textarea" :rows="2" maxlength="5000" placeholder="Phân tách bằng dấu phẩy" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Lĩnh vực đào tạo khác">
            <CustomInput v-model="form.linh_vuc_dao_tao_khac" type="textarea" :rows="2" maxlength="5000" placeholder="Phân tách bằng dấu phẩy" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Giới thiệu ngắn">
            <CustomInput v-model="form.gioi_thieu_ngan" type="textarea" :rows="2" maxlength="1000" show-word-limit />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Thế mạnh">
            <CustomInput v-model="form.the_manh" type="textarea" :rows="3" maxlength="20000" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Giới thiệu chi tiết">
            <CustomInput v-model="form.gioi_thieu_chi_tiet" type="textarea" :rows="4" maxlength="20000" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Ghi chú">
            <CustomInput v-model="form.ghi_chu" type="textarea" :rows="3" maxlength="20000" />
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
  width: 360px;
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
  width: 190px;
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
