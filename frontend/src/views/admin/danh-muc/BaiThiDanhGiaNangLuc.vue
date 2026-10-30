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
const JSON_FIELDS = ['hinh_thuc_thi', 'cau_truc_bai_thi']
const DATE_FIELDS = ['tao_luc', 'cap_nhat_luc']

const COLUMNS = [
  { key: 'id', label: 'ID', width: 80, align: 'right' },
  { key: 'ma_bai_thi', label: 'Mã', width: 120 },
  { key: 'ten_bai_thi', label: 'Tên bài thi', minWidth: 180 },
  { key: 'ten_chi_tiet', label: 'Tên chi tiết', minWidth: 200 },
  { key: 'linh_vuc', label: 'Lĩnh vực', minWidth: 140 },
  { key: 'mon', label: 'Môn', minWidth: 120 },
  { key: 'ten_viet_tat', label: 'Tên viết tắt', width: 130 },
  { key: 'don_vi_to_chuc', label: 'Đơn vị tổ chức', minWidth: 180 },
  { key: 'loai_danh_gia', label: 'Loại đánh giá', minWidth: 150 },
  { key: 'loai_chung_chi', label: 'Loại', width: 130 },
  { key: 'mo_ta', label: 'Mô tả', minWidth: 200 },
  { key: 'doi_tuong_du_thi', label: 'Đối tượng dự thi', minWidth: 180 },
  { key: 'hinh_thuc_thi', label: 'Hình thức thi', minWidth: 160 },
  { key: 'thang_diem', label: 'Thang điểm', width: 160 },
  { key: 'diem_toi_thieu', label: 'Điểm tối thiểu', width: 140, align: 'right' },
  { key: 'don_vi_diem', label: 'Đơn vị điểm', width: 130 },
  { key: 'cau_truc_bai_thi', label: 'Cấu trúc bài thi', minWidth: 180 },
  { key: 'thoi_luong_phut', label: 'Thời lượng (phút)', width: 170, align: 'right' },
  { key: 'cach_cong_bo_ket_qua', label: 'Công bố kết quả', minWidth: 180 },
  { key: 'nam_ap_dung_tu', label: 'Áp dụng từ', width: 120, align: 'right' },
  { key: 'nam_ap_dung_den', label: 'Áp dụng đến', width: 130, align: 'right' },
  { key: 'website_chinh_thuc', label: 'Website', minWidth: 180 },
  { key: 'nguon_du_lieu_url', label: 'Nguồn dữ liệu', minWidth: 180 },
  { key: 'trang_thai', label: 'Trạng thái', width: 150, align: 'center' },
  { key: 'ghi_chu', label: 'Ghi chú', minWidth: 160 },
  { key: 'tao_luc', label: 'Tạo lúc', width: 170, align: 'center' },
  { key: 'cap_nhat_luc', label: 'Cập nhật lúc', width: 170, align: 'center' },
]

const JSON_SAMPLE = `[
  {
    "ma_bai_thi": "HSA",
    "ten_bai_thi": "Đánh giá năng lực HSA",
    "ten_chi_tiet": "Bài thi đánh giá năng lực của Đại học Quốc gia Hà Nội",
    "linh_vuc": "Đánh giá năng lực",
    "mon": "Tổng hợp",
    "ten_viet_tat": "HSA",
    "don_vi_to_chuc": "Đại học Quốc gia Hà Nội",
    "loai_danh_gia": "Năng lực",
    "loai_chung_chi": "trong_nuoc",
    "mo_ta": "Đánh giá năng lực học tập bậc đại học",
    "doi_tuong_du_thi": "Học sinh lớp 12 và thí sinh tự do",
    "hinh_thuc_thi": ["Giấy", "Máy tính"],
    "thang_diem": "0-150",
    "diem_toi_thieu": 0,
    "don_vi_diem": "điểm",
    "cau_truc_bai_thi": [
      { "phan": "Tư duy định lượng", "so_cau": 50, "thoi_luong_phut": 75 },
      { "phan": "Tư duy định tính", "so_cau": 50, "thoi_luong_phut": 60 }
    ],
    "thoi_luong_phut": 195,
    "cach_cong_bo_ket_qua": "Công bố trên website chính thức",
    "nam_ap_dung_tu": 2025,
    "nam_ap_dung_den": null,
    "website_chinh_thuc": "https://hsa.edu.vn",
    "nguon_du_lieu_url": "https://hsa.edu.vn",
    "trang_thai": "Hoạt động",
    "ghi_chu": "Bài thi trong nước"
  },
  {
    "ma_bai_thi": "SAT",
    "ten_bai_thi": "SAT",
    "ten_chi_tiet": "Scholastic Assessment Test",
    "linh_vuc": "Đánh giá năng lực",
    "mon": "Tổng hợp",
    "ten_viet_tat": "SAT",
    "don_vi_to_chuc": "College Board",
    "loai_danh_gia": "Năng lực",
    "loai_chung_chi": "quoc_te",
    "mo_ta": "Bài thi chuẩn hóa dùng cho tuyển sinh đại học",
    "doi_tuong_du_thi": "Học sinh trung học",
    "hinh_thuc_thi": ["Máy tính"],
    "thang_diem": "400-1600",
    "diem_toi_thieu": 400,
    "don_vi_diem": "điểm",
    "cau_truc_bai_thi": [
      { "phan": "Reading and Writing", "thoi_luong_phut": 64 },
      { "phan": "Math", "thoi_luong_phut": 70 }
    ],
    "thoi_luong_phut": 134,
    "cach_cong_bo_ket_qua": "Công bố trên tài khoản College Board",
    "nam_ap_dung_tu": 2024,
    "website_chinh_thuc": "https://satsuite.collegeboard.org",
    "trang_thai": "Hoạt động"
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
    ten_viet_tat: '',
    don_vi_to_chuc: '',
    loai_danh_gia: '',
    loai_chung_chi: 'trong_nuoc',
    mo_ta: '',
    doi_tuong_du_thi: '',
    hinh_thuc_thi: '',
    thang_diem: '',
    diem_toi_thieu: null,
    don_vi_diem: '',
    cau_truc_bai_thi: '',
    thoi_luong_phut: null,
    cach_cong_bo_ket_qua: '',
    nam_ap_dung_tu: null,
    nam_ap_dung_den: null,
    website_chinh_thuc: '',
    nguon_du_lieu_url: '',
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

function fieldError(line, message) {
  return line ? `Phần tử thứ ${line}: ${message}` : message
}

function optionalScore(value, line) {
  if (value === null || value === undefined || value === '') return null
  const number = Number(value)
  if (!Number.isFinite(number) || number < 0 || number > 999999.99) {
    throw new Error(fieldError(line, 'Điểm tối thiểu phải từ 0 đến 999999.99'))
  }
  return Math.round(number * 100) / 100
}

function optionalInt(value, line, label) {
  if (value === null || value === undefined || value === '') return null
  const number = Number(value)
  if (!Number.isInteger(number) || number < 0 || number > 65535) {
    throw new Error(fieldError(line, `${label} phải là số nguyên từ 0 đến 65535`))
  }
  return number
}

function assertYearRange(tu, den, line) {
  if (tu != null && den != null && den < tu) {
    throw new Error(fieldError(line, 'Năm áp dụng đến phải lớn hơn hoặc bằng năm áp dụng từ'))
  }
}

function jsonToEditor(value) {
  if (value == null || value === '') return ''
  if (typeof value === 'string') return value
  return JSON.stringify(value, null, 2)
}

function parseJsonValue(value, line, label) {
  if (value == null || value === '') return null
  if (Array.isArray(value) || (typeof value === 'object' && value !== null)) return value
  const text = String(value).trim()
  if (!text) return null
  let parsed
  try {
    parsed = JSON.parse(text)
  } catch {
    throw new Error(fieldError(line, `${label} không phải JSON hợp lệ`))
  }
  if (parsed == null) return null
  if (typeof parsed !== 'object') {
    throw new Error(fieldError(line, `${label} phải là mảng hoặc object JSON`))
  }
  return parsed
}

function recordFromItem(item, line) {
  const ten = String(item.ten_bai_thi ?? '').trim()
  const ma = String(item.ma_bai_thi ?? '').trim().toUpperCase()
  const loai = String(item.loai_chung_chi ?? '').trim().toLowerCase()
  if (!ten || !ma || !loai) {
    throw new Error(fieldError(line, 'thiếu ten_bai_thi, ma_bai_thi hoặc loai_chung_chi'))
  }
  const namTu = optionalInt(item.nam_ap_dung_tu, line, 'Năm áp dụng từ')
  const namDen = optionalInt(item.nam_ap_dung_den, line, 'Năm áp dụng đến')
  assertYearRange(namTu, namDen, line)
  return {
    ten_bai_thi: ten,
    ma_bai_thi: ma,
    ten_chi_tiet: optionalText(item.ten_chi_tiet),
    linh_vuc: optionalText(item.linh_vuc),
    mon: optionalText(item.mon),
    ten_viet_tat: optionalText(item.ten_viet_tat),
    don_vi_to_chuc: optionalText(item.don_vi_to_chuc),
    loai_danh_gia: optionalText(item.loai_danh_gia),
    loai_chung_chi: loai,
    mo_ta: optionalText(item.mo_ta),
    doi_tuong_du_thi: optionalText(item.doi_tuong_du_thi),
    hinh_thuc_thi: parseJsonValue(item.hinh_thuc_thi, line, 'Hình thức thi'),
    thang_diem: optionalText(item.thang_diem),
    diem_toi_thieu: optionalScore(item.diem_toi_thieu, line),
    don_vi_diem: optionalText(item.don_vi_diem),
    cau_truc_bai_thi: parseJsonValue(item.cau_truc_bai_thi, line, 'Cấu trúc bài thi'),
    thoi_luong_phut: optionalInt(item.thoi_luong_phut, line, 'Thời lượng'),
    cach_cong_bo_ket_qua: optionalText(item.cach_cong_bo_ket_qua),
    nam_ap_dung_tu: namTu,
    nam_ap_dung_den: namDen,
    website_chinh_thuc: optionalText(item.website_chinh_thuc),
    nguon_du_lieu_url: optionalText(item.nguon_du_lieu_url),
    trang_thai: item.trang_thai ?? 'Hoạt động',
    ghi_chu: optionalText(item.ghi_chu),
  }
}

function loaiLabel(value) {
  return LOAI.find((item) => item.value === value)?.label || value || '—'
}

function listToText(value) {
  if (!Array.isArray(value) || !value.length) return ''
  if (value.every((item) => item == null || typeof item !== 'object')) return value.join(', ')
  return JSON.stringify(value)
}

function formatJson(value) {
  if (value == null || value === '') return ''
  if (Array.isArray(value)) return listToText(value)
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
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
  if (JSON_FIELDS.includes(column.key)) return dash(formatJson(value))
  if (column.key === 'loai_chung_chi') return loaiLabel(value)
  if (DATE_FIELDS.includes(column.key)) return formatDateTime(value)
  return dash(value)
}

function statusType(value) {
  if (value === 'Hoạt động' || value === 1 || value === '1') return 'success'
  if (value === 'Ngừng sử dụng' || value === 0 || value === '0') return 'info'
  return 'warning'
}

function statusLabel(value) {
  if (value === 1 || value === '1') return 'Hoạt động'
  if (value === 0 || value === '0') return 'Ngừng sử dụng'
  return value
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
    return recordFromItem(item, line)
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
    ma_bai_thi: row.ma_bai_thi || '',
    ten_bai_thi: row.ten_bai_thi || '',
    ten_chi_tiet: row.ten_chi_tiet || '',
    linh_vuc: row.linh_vuc || '',
    mon: row.mon || '',
    ten_viet_tat: row.ten_viet_tat || '',
    don_vi_to_chuc: row.don_vi_to_chuc || '',
    loai_danh_gia: row.loai_danh_gia || '',
    loai_chung_chi: row.loai_chung_chi,
    mo_ta: row.mo_ta || '',
    doi_tuong_du_thi: row.doi_tuong_du_thi || '',
    hinh_thuc_thi: jsonToEditor(row.hinh_thuc_thi),
    thang_diem: row.thang_diem || '',
    diem_toi_thieu: row.diem_toi_thieu,
    don_vi_diem: row.don_vi_diem || '',
    cau_truc_bai_thi: jsonToEditor(row.cau_truc_bai_thi),
    thoi_luong_phut: row.thoi_luong_phut,
    cach_cong_bo_ket_qua: row.cach_cong_bo_ket_qua || '',
    nam_ap_dung_tu: row.nam_ap_dung_tu,
    nam_ap_dung_den: row.nam_ap_dung_den,
    website_chinh_thuc: row.website_chinh_thuc || '',
    nguon_du_lieu_url: row.nguon_du_lieu_url || '',
    trang_thai: row.trang_thai,
    ghi_chu: row.ghi_chu || '',
    tao_luc: row.tao_luc,
    cap_nhat_luc: row.cap_nhat_luc,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return recordFromItem(form, null)
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
          <CustomOption label="Hoạt động" value="Hoạt động" />
          <CustomOption label="Ngừng sử dụng" value="Ngừng sử dụng" />
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
              {{ statusLabel(row.trang_thai) }}
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
    width="90%"
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
          <code>hinh_thuc_thi</code> và <code>cau_truc_bai_thi</code> là mảng hoặc object JSON.
          Các cột còn lại có thể để trống. <code>id</code>, <code>tao_luc</code> và
          <code>cap_nhat_luc</code> do hệ thống ghi.
        </p>
        <CustomButton text type="primary" @click="fillJsonSample">Điền mẫu</CustomButton>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="26"
        placeholder="Dán mảng JSON vào đây"
      />
    </div>

    <CustomForm v-else ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Tên bài thi" prop="ten_bai_thi">
            <CustomInput v-model="form.ten_bai_thi" maxlength="255" placeholder="Ví dụ: Đánh giá năng lực HSA" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Mã bài thi" prop="ma_bai_thi">
            <CustomInput v-model="form.ma_bai_thi" maxlength="50" placeholder="Ví dụ: HSA" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Loại" prop="loai_chung_chi">
            <CustomSelect v-model="form.loai_chung_chi" :clearable="false" style="width: 100%">
              <CustomOption v-for="item in LOAI" :key="item.value" :label="item.label" :value="item.value" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Tên viết tắt">
            <CustomInput v-model="form.ten_viet_tat" maxlength="50" placeholder="Ví dụ: HSA" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Lĩnh vực">
            <CustomInput v-model="form.linh_vuc" maxlength="150" placeholder="Ví dụ: Đánh giá năng lực" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Môn">
            <CustomInput v-model="form.mon" maxlength="150" placeholder="Ví dụ: Tổng hợp" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Đơn vị tổ chức">
            <CustomInput v-model="form.don_vi_to_chuc" maxlength="255" placeholder="Ví dụ: Đại học Quốc gia Hà Nội" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Loại đánh giá">
            <CustomInput v-model="form.loai_danh_gia" maxlength="50" placeholder="Ví dụ: Năng lực" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" :clearable="false" style="width: 100%">
              <CustomOption label="Hoạt động" value="Hoạt động" />
              <CustomOption label="Ngừng sử dụng" value="Ngừng sử dụng" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Thang điểm">
            <CustomInput v-model="form.thang_diem" maxlength="100" placeholder="Ví dụ: 0-150" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Điểm tối thiểu">
            <CustomInputNumber
              v-model="form.diem_toi_thieu"
              :min="0"
              :max="999999.99"
              :precision="2"
              :step="1"
              :value-on-clear="null"
              controls-position="right"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Đơn vị điểm">
            <CustomInput v-model="form.don_vi_diem" maxlength="30" placeholder="Ví dụ: điểm" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Thời lượng (phút)">
            <CustomInputNumber
              v-model="form.thoi_luong_phut"
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
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Áp dụng từ">
            <CustomInputNumber
              v-model="form.nam_ap_dung_tu"
              :min="0"
              :max="65535"
              :precision="0"
              :step="1"
              :value-on-clear="null"
              controls-position="right"
              placeholder="Năm"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <CustomFormItem label="Áp dụng đến">
            <CustomInputNumber
              v-model="form.nam_ap_dung_den"
              :min="0"
              :max="65535"
              :precision="0"
              :step="1"
              :value-on-clear="null"
              controls-position="right"
              placeholder="Năm"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
          <CustomFormItem label="Website">
            <CustomInput v-model="form.website_chinh_thuc" maxlength="1000" placeholder="https://" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
          <CustomFormItem label="Nguồn dữ liệu">
            <CustomInput v-model="form.nguon_du_lieu_url" maxlength="1000" placeholder="https://" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
          <CustomFormItem label="Tên chi tiết">
            <CustomInput
              v-model="form.ten_chi_tiet"
              maxlength="500"
              placeholder="Tên đầy đủ hoặc mô tả ngắn"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
          <CustomFormItem label="Đối tượng dự thi">
            <CustomInput
              v-model="form.doi_tuong_du_thi"
              type="textarea"
              :rows="3"
              placeholder="Nhóm đối tượng có thể dự thi"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Hình thức thi">
            <CustomInput
              v-model="form.hinh_thuc_thi"
              type="textarea"
              :rows="3"
              placeholder='Mảng hoặc object JSON. Ví dụ: ["Giấy", "Máy tính"]'
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Cấu trúc bài thi">
            <CustomInput
              v-model="form.cau_truc_bai_thi"
              type="textarea"
              :rows="3"
              placeholder='Mảng hoặc object JSON. Ví dụ: [{"phan": "Toán", "so_cau": 50}]'
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
          <CustomFormItem label="Công bố kết quả">
            <CustomInput
              v-model="form.cach_cong_bo_ket_qua"
              type="textarea"
              :rows="3"
              placeholder="Cách đơn vị tổ chức công bố kết quả"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
          <CustomFormItem label="Mô tả">
            <CustomInput
              v-model="form.mo_ta"
              type="textarea"
              :rows="3"
              placeholder="Mục tiêu và phạm vi đánh giá"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-if="editingId" :span="12" :xs="12">
          <CustomFormItem label="Tạo lúc">
            <CustomInput :model-value="formatDateTime(form.tao_luc)" disabled />
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-if="editingId" :span="12" :xs="12">
          <CustomFormItem label="Cập nhật lúc">
            <CustomInput :model-value="formatDateTime(form.cap_nhat_luc)" disabled />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
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
