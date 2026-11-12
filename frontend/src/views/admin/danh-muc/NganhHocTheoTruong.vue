<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { JSON_BATCH_TIMEOUT } from '@/composables/useJsonBatchImport'
import {
  createNganhHocTheoTruong,
  deleteNganhHocTheoTruong,
  deleteNganhHocTheoTruongMany,
  fetchNamHocNganhTheoTruong,
  fetchNganhHocTheoTruong,
  importNganhHocTheoTruong,
  kiemTraTruongImport,
  updateNganhHocTheoTruong,
} from '@/api/nganhHocTheoTruong'
import { fetchTruongHoc } from '@/api/truongHoc'
import { fetchNganh } from '@/api/nganhDaoTao'

const NAM_HIEN_TAI = new Date().getFullYear()
const JSON_TOI_DA_MB = 5
// Số ngành gửi mỗi lần import; thanh tiến độ tăng theo từng lô.
const IMPORT_LO = 50
const JSON_SAMPLE = `[
  {
    "ma_truong": "BKA",
    "nam_tuyen_sinh": ${NAM_HIEN_TAI},
    "chuong_trinh_dao_tao": [
      {
        "ma_xet_tuyen": "BF1",
        "ma_nganh": "7420202",
        "ten_nganh": "Kỹ thuật sinh học",
        "ten_chuong_trinh": "Kỹ thuật Sinh học"
      }
    ]
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
const formRef = ref()
const createMode = ref('form')
const jsonText = ref('')
const jsonFileInput = ref()
// Cùng cấu trúc với useJsonBatchImport để dùng chung JsonImportDialogFooter, nhưng đếm theo ngành.
const importBatch = reactive({
  label: 'ngành',
  batchSize: IMPORT_LO,
  progress: { total: 0, done: 0, active: false, failed: false },
})

function resetImport() {
  Object.assign(importBatch.progress, { total: 0, done: 0, active: false, failed: false })
}

const namHocOptions = ref([])
const filterTruongOptions = ref([])
const formTruongOptions = ref([])
const dangTimTruong = ref(false)

const filters = reactive({
  q: '',
  ma_truong: '',
  nam_hoc: '',
})

const form = reactive(emptyForm())

const rules = {
  ma_truong: [{ required: true, message: 'Vui lòng chọn trường', trigger: 'change' }],
  nam_hoc: [{ required: true, message: 'Vui lòng nhập năm học', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_truong: '',
    nam_hoc: NAM_HIEN_TAI,
    ma_nganh: '',
    ma_xet_tuyen: '',
    ten_nganh: '',
    ten_chuong_trinh: '',
    ghi_chu: '',
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  resetImport()
  formRef.value?.clearValidate()
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
    if (filters.ma_truong) params.ma_truong = filters.ma_truong
    if (filters.nam_hoc) params.nam_hoc = filters.nam_hoc
    const data = await fetchNganhHocTheoTruong(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách ngành đào tạo'))
  } finally {
    loading.value = false
  }
}

async function loadNamHocOptions() {
  try {
    namHocOptions.value = await fetchNamHocNganhTheoTruong()
  } catch {
    namHocOptions.value = []
  }
}

async function timTruong(query) {
  dangTimTruong.value = true
  try {
    const params = { page: 1, page_size: 20 }
    if (query?.trim()) params.q = query.trim()
    const data = await fetchTruongHoc(params, { skipLoading: true })
    return data.items.map((item) => ({ ma_truong: item.ma_truong, ten_truong: item.ten_truong }))
  } catch {
    return []
  } finally {
    dangTimTruong.value = false
  }
}

async function timTruongBoLoc(query) {
  filterTruongOptions.value = await timTruong(query)
}

async function timTruongForm(query) {
  formTruongOptions.value = await timTruong(query)
}

// Gợi ý mã ngành từ danh mục ngành đào tạo; chọn gợi ý sẽ điền luôn tên ngành.
async function goiYNganh(query, callback) {
  try {
    const params = { page: 1, page_size: 20 }
    if (query?.trim()) params.q = query.trim()
    const data = await fetchNganh(params, { skipLoading: true })
    callback(data.items.map((item) => ({ ma_nganh: item.ma_nganh, ten_nganh: item.ten_nganh })))
  } catch {
    callback([])
  }
}

function chonNganh(item) {
  form.ma_nganh = item.ma_nganh
  form.ten_nganh = item.ten_nganh
  formRef.value?.clearValidate(['ma_nganh', 'ten_nganh'])
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
  // Đang lọc theo một trường thì điền sẵn trường đó.
  if (filters.ma_truong) {
    form.ma_truong = filters.ma_truong
    formTruongOptions.value = filterTruongOptions.value.filter((item) => item.ma_truong === filters.ma_truong)
  }
  if (filters.nam_hoc) form.nam_hoc = filters.nam_hoc
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  formTruongOptions.value = [{ ma_truong: row.ma_truong, ten_truong: row.ten_truong || row.ma_truong }]
  Object.assign(form, {
    ma_truong: row.ma_truong,
    nam_hoc: row.nam_hoc,
    ma_nganh: row.ma_nganh || '',
    ma_xet_tuyen: row.ma_xet_tuyen || '',
    ten_nganh: row.ten_nganh || '',
    ten_chuong_trinh: row.ten_chuong_trinh || '',
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
}

function textValue(value) {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

function payloadFromForm() {
  return {
    ma_truong: form.ma_truong,
    nam_hoc: form.nam_hoc,
    ma_nganh: textValue(form.ma_nganh).toUpperCase() || null,
    ma_xet_tuyen: textValue(form.ma_xet_tuyen).toUpperCase() || null,
    ten_nganh: textValue(form.ten_nganh).replace(/\s+/g, ' ') || null,
    ten_chuong_trinh: textValue(form.ten_chuong_trinh) || null,
    ghi_chu: textValue(form.ghi_chu) || null,
  }
}

// Ngành không có thông tin nào thì không lưu (khớp với kiểm tra ở backend).
function nganhTrong(item) {
  return !(item.ma_xet_tuyen || item.ma_nganh || item.ten_nganh || item.ten_chuong_trinh)
}

// Chấp nhận cả dữ liệu dán thiếu ngoặc vuông ({...}, {...}) hoặc còn dấu phẩy thừa cuối mảng/đối tượng.
function parseJsonText(text) {
  let source = text.trim().replace(/,\s*$/, '')
  if (source.startsWith('{')) source = `[${source}]`
  try {
    return JSON.parse(source)
  } catch {
    try {
      return JSON.parse(source.replace(/,(\s*[\]}])/g, '$1'))
    } catch {
      throw new Error('JSON không hợp lệ. Hãy kiểm tra lại dấu ngoặc và dấu phẩy.')
    }
  }
}

function parseJsonItems(text) {
  if (!text.trim()) throw new Error('Chưa có dữ liệu JSON')
  const data = parseJsonText(text)
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng các trường, ví dụ [{ "ma_truong": "...", ... }]')
  }
  if (!data.length) throw new Error('Mảng trường đang trống')

  return data.map((truong, index) => {
    const viTri = `Trường thứ ${index + 1}`
    if (!truong || typeof truong !== 'object' || Array.isArray(truong)) {
      throw new Error(`${viTri}: phải là một đối tượng`)
    }
    const maTruong = textValue(truong.ma_truong).toUpperCase()
    if (!maTruong) throw new Error(`${viTri}: thiếu ma_truong`)
    const nam = Number(truong.nam_tuyen_sinh)
    if (!Number.isInteger(nam) || nam < 2000 || nam > 2100) {
      throw new Error(`${viTri} (${maTruong}): nam_tuyen_sinh phải là năm từ 2000 đến 2100`)
    }
    const chuongTrinh = truong.chuong_trinh_dao_tao ?? []
    if (!Array.isArray(chuongTrinh)) {
      throw new Error(`${viTri} (${maTruong}): chuong_trinh_dao_tao phải là mảng`)
    }

    return {
      ma_truong: maTruong,
      nam_tuyen_sinh: nam,
      chuong_trinh_dao_tao: chuongTrinh.map((ct, ctIndex) => {
        const viTriCt = `${viTri} (${maTruong}), chương trình thứ ${ctIndex + 1}`
        if (!ct || typeof ct !== 'object' || Array.isArray(ct)) {
          throw new Error(`${viTriCt}: phải là một đối tượng`)
        }
        // Các thông tin ngành đều có thể null/để trống.
        return {
          ma_xet_tuyen: textValue(ct.ma_xet_tuyen).toUpperCase() || null,
          ma_nganh: textValue(ct.ma_nganh).toUpperCase() || null,
          ten_nganh: textValue(ct.ten_nganh).replace(/\s+/g, ' ') || null,
          ten_chuong_trinh: textValue(ct.ten_chuong_trinh) || null,
          ghi_chu: textValue(ct.ghi_chu) || null,
        }
      }),
    }
  })
}

// Trải phẳng thành từng ngành để chia lô và tính tiến độ theo số ngành.
function trai(items) {
  const rows = []
  let boQua = 0
  for (const truong of items) {
    for (const ct of truong.chuong_trinh_dao_tao) {
      if (nganhTrong(ct)) {
        boQua += 1
        continue
      }
      rows.push({ ma_truong: truong.ma_truong, nam_tuyen_sinh: truong.nam_tuyen_sinh, ct })
    }
  }
  return { rows, boQua }
}

// Gom các ngành của một lô về lại cấu trúc theo trường để gửi API.
function gomTheoTruong(rows) {
  const groups = new Map()
  for (const row of rows) {
    const key = `${row.ma_truong}|${row.nam_tuyen_sinh}`
    if (!groups.has(key)) {
      groups.set(key, { ma_truong: row.ma_truong, nam_tuyen_sinh: row.nam_tuyen_sinh, chuong_trinh_dao_tao: [] })
    }
    groups.get(key).chuong_trinh_dao_tao.push(row.ct)
  }
  return [...groups.values()]
}

// Chia lô khoảng IMPORT_LO ngành, nhưng các ngành cùng trường, năm và mã xét tuyển luôn nằm chung một lô
// để backend so khớp đúng khi một mã xét tuyển có nhiều ngành.
function chiaLo(rows) {
  const nhom = new Map()
  rows.forEach((row, index) => {
    const key = row.ct.ma_xet_tuyen ? `${row.ma_truong}|${row.nam_tuyen_sinh}|${row.ct.ma_xet_tuyen}` : `#${index}`
    if (!nhom.has(key)) nhom.set(key, [])
    nhom.get(key).push(row)
  })
  const lo = []
  let hienTai = []
  for (const cacDong of nhom.values()) {
    hienTai.push(...cacDong)
    if (hienTai.length >= IMPORT_LO) {
      lo.push(hienTai)
      hienTai = []
    }
  }
  if (hienTai.length) lo.push(hienTai)
  return lo
}

function soMaNhieuNganh(rows) {
  const dem = new Map()
  for (const { ma_truong, nam_tuyen_sinh, ct } of rows) {
    if (!ct.ma_xet_tuyen) continue
    const key = `${ma_truong}|${nam_tuyen_sinh}|${ct.ma_xet_tuyen}`
    dem.set(key, (dem.get(key) || 0) + 1)
  }
  return [...dem.values()].filter((n) => n > 1).length
}

// Tóm tắt nhanh nội dung đang dán để người dùng kiểm tra trước khi lưu.
const jsonTomTat = computed(() => {
  if (!jsonText.value.trim()) return null
  try {
    const items = parseJsonItems(jsonText.value)
    const { rows, boQua } = trai(items)
    let text = `${items.length} trường · ${rows.length} ngành sẽ import`
    const nhieuNganh = soMaNhieuNganh(rows)
    if (nhieuNganh) text += ` · ${nhieuNganh} mã xét tuyển có nhiều ngành`
    if (boQua) text += ` · bỏ qua ${boQua} ngành không có thông tin`
    return { ok: true, text }
  } catch (error) {
    return { ok: false, text: error.message }
  }
})

function fillJsonSample() {
  jsonText.value = JSON_SAMPLE
}

function chonFileJson() {
  jsonFileInput.value?.click()
}

async function docFileJson(file) {
  if (!file) return
  if (!/\.json$/i.test(file.name) && file.type !== 'application/json') {
    ElMessage.error('Chỉ nhận file .json')
    return
  }
  if (file.size > JSON_TOI_DA_MB * 1024 * 1024) {
    ElMessage.error(`File JSON tối đa ${JSON_TOI_DA_MB}MB`)
    return
  }
  try {
    jsonText.value = await file.text()
    ElMessage.success(`Đã đọc file ${file.name}`)
  } catch {
    ElMessage.error('Không đọc được file')
  }
}

function onChonFileJson(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  docFileJson(file)
}

function onDropFileJson(event) {
  docFileJson(event.dataTransfer?.files?.[0])
}

async function onSubmitJson() {
  let items
  try {
    items = parseJsonItems(jsonText.value)
  } catch (error) {
    ElMessage.error(error.message)
    return
  }

  const { rows: cacDong, boQua } = trai(items)
  let rows = cacDong
  if (!rows.length) {
    ElMessage.error('Không có ngành nào có thông tin để import')
    return
  }
  const progress = importBatch.progress
  saving.value = true
  progress.failed = false
  try {
    // Kiểm tra mã trường trước, để không lưu dở dang rồi mới báo lỗi ở lô sau.
    const { thieu } = await kiemTraTruongImport([...new Set(rows.map((row) => row.ma_truong))])
    if (thieu.length) {
      ElMessage.error(`Mã trường không tồn tại: ${thieu.join(', ')}`)
      return
    }
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không kiểm tra được mã trường'))
    return
  } finally {
    saving.value = false
  }

  const thongKe = { them_moi: 0, cap_nhat: 0 }
  saving.value = true
  // Sắp lại theo lô để phần chưa lưu (khi lỗi) là đúng các dòng phía sau.
  const cacLo = chiaLo(rows)
  rows = cacLo.flat()
  progress.total = rows.length
  progress.done = 0
  progress.active = true
  try {
    for (const lo of cacLo) {
      const result = await importNganhHocTheoTruong(gomTheoTruong(lo), {
        skipLoading: true,
        timeout: JSON_BATCH_TIMEOUT,
      })
      thongKe.them_moi += result.them_moi
      thongKe.cap_nhat += result.cap_nhat
      progress.done += lo.length
    }
  } catch (error) {
    progress.failed = true
    const daLuu = progress.done
    // Giữ lại phần chưa lưu trong ô JSON để lưu tiếp.
    if (daLuu > 0) jsonText.value = JSON.stringify(gomTheoTruong(rows.slice(daLuu)), null, 2)
    const timeout = error?.code === 'ECONNABORTED' || /timeout/i.test(error?.message || '')
    const detail = timeout
      ? 'Hết thời gian chờ, lô đang gửi có thể đã được lưu.'
      : errorMessage(error, 'Không import được ngành theo trường.')
    ElMessage.error(daLuu > 0 ? `Đã lưu ${daLuu}/${rows.length} ngành. ${detail} Phần chưa lưu vẫn nằm trong ô JSON.` : detail)
    if (daLuu > 0 || timeout) await Promise.all([load(), loadNamHocOptions()]).catch(() => {})
    return
  } finally {
    saving.value = false
    progress.active = false
  }

  let message = `Đã import ${rows.length} ngành: ${thongKe.them_moi} thêm mới, ${thongKe.cap_nhat} cập nhật`
  if (boQua) message += `, bỏ qua ${boQua} ngành không có thông tin`
  ElMessage.success(message)
  dialogVisible.value = false
  try {
    await Promise.all([load(), loadNamHocOptions()])
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Đã import nhưng không tải lại được danh sách'))
  }
}

async function onSubmit() {
  if (!editingId.value && createMode.value === 'json') {
    await onSubmitJson()
    return
  }

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  const payload = payloadFromForm()
  if (nganhTrong(payload)) {
    ElMessage.error('Cần nhập ít nhất một trong: mã xét tuyển, mã ngành, tên ngành, tên chương trình')
    return
  }

  saving.value = true
  try {
    if (editingId.value) {
      await updateNganhHocTheoTruong(editingId.value, payload)
      ElMessage.success('Đã cập nhật ngành đào tạo')
    } else {
      await createNganhHocTheoTruong(payload)
      ElMessage.success('Đã thêm ngành đào tạo')
    }
    dialogVisible.value = false
    await Promise.all([load(), loadNamHocOptions()])
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được ngành đào tạo'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa ngành ${[row.ma_xet_tuyen, row.ten_nganh || row.ten_chuong_trinh || row.ma_nganh].filter(Boolean).join(' – ')} (${row.ma_truong}, ${row.nam_hoc})?`,
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
    await deleteNganhHocTheoTruong(row.id)
    ElMessage.success('Đã xóa ngành đào tạo')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await Promise.all([load(), loadNamHocOptions()])
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được ngành đào tạo'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} ngành đào tạo đã chọn?`, 'Xác nhận xóa', {
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
    const result = await deleteNganhHocTheoTruongMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} ngành đào tạo`)
    clearSelection()
    loadNamHocOptions()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các ngành đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  load()
  loadNamHocOptions()
  timTruongBoLoc('')
})
</script>

<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Mã ngành, mã xét tuyển, tên ngành"
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
        class="filter-truong"
        placeholder="Trường"
        filterable
        remote
        :remote-method="timTruongBoLoc"
        :loading="dangTimTruong"
        clearable
        @change="onSearch"
      >
        <CustomOption
          v-for="item in filterTruongOptions"
          :key="item.ma_truong"
          :label="`${item.ma_truong} – ${item.ten_truong}`"
          :value="item.ma_truong"
        />
      </CustomSelect>
      <CustomSelect
        v-model="filters.nam_hoc"
        class="filter-nam"
        placeholder="Năm học"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="nam in namHocOptions" :key="nam" :label="String(nam)" :value="nam" />
      </CustomSelect>
      <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
    </div>
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Ngành theo trường</h2>
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
          Thêm ngành
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
      <CustomTableColumn label="STT" width="64" align="center">
        <template #default="{ $index }">{{ rowIndex($index) }}</template>
      </CustomTableColumn>
      <CustomTableColumn prop="nam_hoc" label="Năm học" width="96" align="center" />
      <CustomTableColumn label="Trường" min-width="240">
        <template #default="{ row }">
          <div class="cell-stack">
            <strong>{{ row.ma_truong }}</strong>
            <span class="cell-sub">{{ row.ten_truong || '—' }}</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Mã xét tuyển" width="130">
        <template #default="{ row }">{{ row.ma_xet_tuyen || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Mã ngành" width="110">
        <template #default="{ row }">{{ row.ma_nganh || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Ngành / Chương trình" min-width="260">
        <template #default="{ row }">
          <div class="cell-stack">
            <span>{{ row.ten_nganh || '—' }}</span>
            <span v-if="row.ten_chuong_trinh" class="cell-sub">{{ row.ten_chuong_trinh }}</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Ghi chú" min-width="180">
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
        <CustomEmpty description="Chưa có ngành đào tạo nào." />
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
    :title="editingId ? 'Cập nhật ngành đào tạo' : 'Thêm ngành đào tạo'"
    width="760px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomRadioGroup v-if="!editingId" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Import JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div
      v-if="!editingId && createMode === 'json'"
      class="json-panel"
      @dragover.prevent
      @drop.prevent="onDropFileJson"
    >
      <div class="json-panel__head">
        <p>
          Chọn file <code>.json</code>, kéo thả file vào đây hoặc dán nội dung. Dữ liệu là một mảng trường, mỗi
          trường gồm <code>ma_truong</code>, <code>nam_tuyen_sinh</code> và mảng
          <code>chuong_trinh_dao_tao</code> (<code>ma_xet_tuyen</code>, <code>ma_nganh</code>,
          <code>ten_nganh</code>, <code>ten_chuong_trinh</code>, có thể để <code>null</code>). Một mã xét tuyển có thể gồm nhiều
          ngành; ngành đã có sẽ được cập nhật.
        </p>
        <div class="json-panel__actions">
          <CustomButton type="primary" plain @click="chonFileJson">
            <CustomIcon><Upload /></CustomIcon>
            <span>Chọn file</span>
          </CustomButton>
          <CustomButton text type="primary" @click="fillJsonSample">Điền mẫu</CustomButton>
        </div>
        <input ref="jsonFileInput" type="file" accept=".json,application/json" hidden @change="onChonFileJson" />
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        :disabled="saving"
        placeholder="Dán mảng JSON vào đây"
      />
      <p
        v-if="jsonTomTat"
        class="json-panel__summary"
        :class="{ 'json-panel__summary--error': !jsonTomTat.ok }"
      >
        {{ jsonTomTat.text }}
      </p>
    </div>

    <CustomForm v-else ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol :span="16" :xs="24">
          <CustomFormItem label="Trường" prop="ma_truong">
            <CustomSelect
              v-model="form.ma_truong"
              placeholder="Gõ mã hoặc tên trường để tìm"
              filterable
              remote
              :remote-method="timTruongForm"
              :loading="dangTimTruong"
              style="width: 100%"
              @focus="!formTruongOptions.length && timTruongForm('')"
            >
              <CustomOption
                v-for="item in formTruongOptions"
                :key="item.ma_truong"
                :label="`${item.ma_truong} – ${item.ten_truong}`"
                :value="item.ma_truong"
              />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="12">
          <CustomFormItem label="Năm học" prop="nam_hoc">
            <CustomInputNumber
              v-model="form.nam_hoc"
              :min="2000"
              :max="2100"
              :step="1"
              step-strictly
              controls-position="right"
              style="width: 100%"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="6" :xs="12">
          <CustomFormItem label="Mã ngành" prop="ma_nganh">
            <el-autocomplete
              v-model="form.ma_nganh"
              :fetch-suggestions="goiYNganh"
              value-key="ma_nganh"
              maxlength="20"
              placeholder="Ví dụ: 7480201"
              clearable
              :debounce="300"
              style="width: 100%"
              @select="chonNganh"
            >
              <template #default="{ item }">
                <span class="nganh-option">
                  <strong>{{ item.ma_nganh }}</strong>
                  <small>{{ item.ten_nganh }}</small>
                </span>
              </template>
            </el-autocomplete>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="6" :xs="12">
          <CustomFormItem label="Mã xét tuyển" prop="ma_xet_tuyen">
            <CustomInput v-model="form.ma_xet_tuyen" maxlength="50" placeholder="Ví dụ: 7480201_CLC" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Tên ngành" prop="ten_nganh">
            <CustomInput v-model="form.ten_nganh" maxlength="255" placeholder="Ví dụ: Công nghệ thông tin" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Tên chương trình" prop="ten_chuong_trinh">
            <CustomInput
              v-model="form.ten_chuong_trinh"
              maxlength="255"
              placeholder="Ví dụ: Chương trình chất lượng cao"
            />
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
            />
          </CustomFormItem>
        </CustomCol>
      </CustomRow>
    </CustomForm>
    <template #footer>
      <JsonImportDialogFooter
        :batch="importBatch"
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

.filter-search {
  width: 240px;
}

.filter-truong {
  width: 260px;
}

.filter-nam {
  width: 130px;
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

.cell-stack {
  display: flex;
  flex-direction: column;
  min-width: 0;
  line-height: 1.4;
}

.cell-sub {
  color: var(--el-text-color-secondary);
  font-size: 12px;
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

.nganh-option {
  display: flex;
  align-items: baseline;
  gap: 8px;
  min-width: 0;
}

.nganh-option small {
  overflow: hidden;
  color: var(--el-text-color-secondary);
  text-overflow: ellipsis;
  white-space: nowrap;
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

.json-panel__actions {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 4px;
}

.json-input :deep(textarea) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
}

.json-panel__summary {
  margin: 6px 0 0;
  color: var(--el-color-success);
  font-size: 13px;
  line-height: 1.4;
}

.json-panel__summary--error {
  color: var(--el-color-danger);
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 640px) {
  .filter-search,
  .filter-truong,
  .filter-nam {
    width: 100%;
  }

  .json-panel__head {
    flex-direction: column;
  }
}
</style>
