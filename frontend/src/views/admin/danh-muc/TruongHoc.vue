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

const LOAI_HINH = ['Công lập', 'Tư thục', 'Quốc tế', 'Dân lập']

const JSON_SAMPLE = `[
  {
    "ma_truong": "BKA",
    "ten_truong": "Đại học Bách khoa Hà Nội",
    "ten_viet_tat": "HUST",
    "ten_tieng_anh": "Hanoi University of Science and Technology",
    "khu_vuc": "Hà Nội",
    "dia_chi": "Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội",
    "loai_hinh_dao_tao": "Công lập",
    "nhom_nganh": "Kỹ thuật - Công nghệ",
    "website": "https://hust.edu.vn",
    "email": "hust@hust.edu.vn",
    "so_dien_thoai": "024 3869 4242",
    "hoc_phi_trung_binh": "25-35 triệu/năm",
    "nam_thanh_lap": 1956,
    "trang_thai": 1,
    "gioi_thieu": "Trường đại học kỹ thuật."
  },
  {
    "ma_truong": "KHA",
    "ten_truong": "Đại học Kinh tế Quốc dân",
    "ten_viet_tat": "NEU",
    "khu_vuc": "Hà Nội",
    "loai_hinh_dao_tao": "Công lập",
    "nhom_nganh": "Kinh tế"
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
const jsonImport = useJsonBatchImport({ label: 'trường đại học' })
const formRef = ref()

const filters = reactive({
  q: '',
  khu_vuc: '',
  loai_hinh_dao_tao: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

const rules = {
  ten_truong: [{ required: true, message: 'Vui lòng nhập tên trường', trigger: 'blur' }],
  ma_truong: [{ required: true, message: 'Vui lòng nhập mã trường', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
  email: [
    {
      validator: (_rule, value, callback) => {
        const text = String(value || '').trim()
        if (!text || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(text)) {
          callback()
          return
        }
        callback(new Error('Email không hợp lệ'))
      },
      trigger: 'blur',
    },
  ],
  nam_thanh_lap: [
    {
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
    },
  ],
}

function emptyForm() {
  return {
    ma_truong: '',
    ten_truong: '',
    ten_viet_tat: '',
    ten_tieng_anh: '',
    khu_vuc: '',
    dia_chi: '',
    loai_hinh_dao_tao: '',
    nhom_nganh: '',
    website: '',
    email: '',
    so_dien_thoai: '',
    logo: '',
    anh_bia: '',
    gioi_thieu: '',
    hoc_phi_trung_binh: '',
    nam_thanh_lap: null,
    trang_thai: 1,
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

function optionalYear(value) {
  if (value === null || value === undefined || value === '') return null
  const year = Number(value)
  return Number.isFinite(year) ? year : null
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng trường đại học.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_truong": "...", "ma_truong": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng trường đại học đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một trường đại học`)
    }
    const ten = String(item.ten_truong ?? '').trim()
    const ma = String(item.ma_truong ?? '').trim()
    if (!ten || !ma) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_truong hoặc ma_truong`)
    }
    return {
      ma_truong: ma,
      ten_truong: ten,
      ten_viet_tat: optionalText(item.ten_viet_tat),
      ten_tieng_anh: optionalText(item.ten_tieng_anh),
      khu_vuc: optionalText(item.khu_vuc),
      dia_chi: optionalText(item.dia_chi),
      loai_hinh_dao_tao: optionalText(item.loai_hinh_dao_tao),
      nhom_nganh: optionalText(item.nhom_nganh),
      website: optionalText(item.website),
      email: optionalText(item.email),
      so_dien_thoai: optionalText(item.so_dien_thoai),
      logo: optionalText(item.logo),
      anh_bia: optionalText(item.anh_bia),
      gioi_thieu: optionalText(item.gioi_thieu),
      hoc_phi_trung_binh: optionalText(item.hoc_phi_trung_binh),
      nam_thanh_lap: optionalYear(item.nam_thanh_lap),
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
    if (filters.khu_vuc.trim()) params.khu_vuc = filters.khu_vuc.trim()
    if (filters.loai_hinh_dao_tao) params.loai_hinh_dao_tao = filters.loai_hinh_dao_tao
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchTruongHoc(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách trường đại học'))
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
    ma_truong: row.ma_truong,
    ten_truong: row.ten_truong,
    ten_viet_tat: row.ten_viet_tat || '',
    ten_tieng_anh: row.ten_tieng_anh || '',
    khu_vuc: row.khu_vuc || '',
    dia_chi: row.dia_chi || '',
    loai_hinh_dao_tao: row.loai_hinh_dao_tao || '',
    nhom_nganh: row.nhom_nganh || '',
    website: row.website || '',
    email: row.email || '',
    so_dien_thoai: row.so_dien_thoai || '',
    logo: row.logo || '',
    anh_bia: row.anh_bia || '',
    gioi_thieu: row.gioi_thieu || '',
    hoc_phi_trung_binh: row.hoc_phi_trung_binh || '',
    nam_thanh_lap: row.nam_thanh_lap,
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_truong: form.ma_truong.trim().toUpperCase(),
    ten_truong: form.ten_truong.trim(),
    ten_viet_tat: optionalText(form.ten_viet_tat),
    ten_tieng_anh: optionalText(form.ten_tieng_anh),
    khu_vuc: optionalText(form.khu_vuc),
    dia_chi: optionalText(form.dia_chi),
    loai_hinh_dao_tao: optionalText(form.loai_hinh_dao_tao),
    nhom_nganh: optionalText(form.nhom_nganh),
    website: optionalText(form.website),
    email: optionalText(form.email),
    so_dien_thoai: optionalText(form.so_dien_thoai),
    logo: optionalText(form.logo),
    anh_bia: optionalText(form.anh_bia),
    gioi_thieu: optionalText(form.gioi_thieu),
    hoc_phi_trung_binh: optionalText(form.hoc_phi_trung_binh),
    nam_thanh_lap: optionalYear(form.nam_thanh_lap),
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

  saving.value = true
  try {
    const payload = payloadFromForm()
    if (editingId.value) {
      await updateTruongHoc(editingId.value, payload)
      ElMessage.success('Đã cập nhật trường đại học')
    } else {
      await createTruongHoc(payload)
      ElMessage.success('Đã thêm trường đại học')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được trường đại học'))
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
    ElMessage.success('Đã xóa trường đại học')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được trường đại học'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} trường đại học đã chọn?`, 'Xác nhận xóa', {
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
    ElMessage.success(`Đã xóa ${result.deleted} trường đại học`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các trường đại học đã chọn'))
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
          placeholder="Tìm tên, mã, viết tắt hoặc tên tiếng Anh"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomInput
          v-model="filters.khu_vuc"
          class="filter-region"
          placeholder="Khu vực"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        />
        <CustomSelect
          v-model="filters.loai_hinh_dao_tao"
          class="filter-status"
          placeholder="Loại hình"
          clearable
          @change="onSearch"
        >
          <CustomOption v-for="item in LOAI_HINH" :key="item" :label="item" :value="item" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.trang_thai"
          class="filter-status"
          placeholder="Trạng thái"
          clearable
          @change="onSearch"
        >
          <CustomOption label="Hoạt động" :value="1" />
          <CustomOption label="Khóa" :value="0" />
        </CustomSelect>
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách trường đại học</h2>
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
        <CustomTableColumn prop="ma_truong" label="Mã" width="100" />
        <CustomTableColumn prop="ten_viet_tat" label="Viết tắt" width="110">
          <template #default="{ row }">{{ dash(row.ten_viet_tat) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_truong" label="Tên trường" min-width="240" show-overflow-tooltip />
        <CustomTableColumn prop="khu_vuc" label="Khu vực" min-width="140">
          <template #default="{ row }">{{ dash(row.khu_vuc) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="loai_hinh_dao_tao" label="Loại hình" width="130">
          <template #default="{ row }">{{ dash(row.loai_hinh_dao_tao) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="nhom_nganh" label="Nhóm ngành" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.nhom_nganh) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="hoc_phi_trung_binh" label="Học phí" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.hoc_phi_trung_binh) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="nam_thanh_lap" label="Năm thành lập" width="130" align="center">
          <template #default="{ row }">{{ dash(row.nam_thanh_lap) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Trạng thái" width="130" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
              {{ row.trang_thai === 1 ? 'Hoạt động' : 'Khóa' }}
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
          <CustomEmpty description="Chưa có trường đại học nào." />
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
    :title="editingId ? 'Cập nhật trường đại học' : 'Thêm trường đại học'"
    width="960px"
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
          <CustomFormItem label="Năm thành lập" prop="nam_thanh_lap">
            <CustomInputNumber
              v-model="form.nam_thanh_lap"
              :min="1000"
              :max="2100"
              :step="1"
              :precision="0"
              :value-on-clear="null"
              controls-position="right"
              style="width: 100%"
            />
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
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Khu vực">
            <CustomInput v-model="form.khu_vuc" maxlength="50" placeholder="Tỉnh/thành phố hoặc miền" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Loại hình đào tạo">
            <CustomSelect
              v-model="form.loai_hinh_dao_tao"
              filterable
              allow-create
              default-first-option
              placeholder="Chọn hoặc nhập loại hình"
              style="width: 100%"
            >
              <CustomOption v-for="item in LOAI_HINH" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Nhóm ngành">
            <CustomInput v-model="form.nhom_nganh" maxlength="100" placeholder="Khối ngành chính" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Website">
            <CustomInput v-model="form.website" maxlength="255" placeholder="https://..." />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Email" prop="email">
            <CustomInput v-model="form.email" maxlength="100" placeholder="email@truong.edu.vn" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Số điện thoại">
            <CustomInput v-model="form.so_dien_thoai" maxlength="50" placeholder="Hotline" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Học phí trung bình">
            <CustomInput v-model="form.hoc_phi_trung_binh" maxlength="100" placeholder="Ví dụ: 25-35 triệu/năm" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" :clearable="false" style="width: 100%">
              <CustomOption label="Hoạt động" :value="1" />
              <CustomOption label="Khóa" :value="0" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="24" />
        <CustomCol :span="24">
          <CustomFormItem label="Địa chỉ">
            <CustomInput
              v-model="form.dia_chi"
              type="textarea"
              :rows="2"
              maxlength="5000"
              placeholder="Địa chỉ cơ sở chính"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Logo">
            <CustomInput v-model="form.logo" maxlength="255" placeholder="URL logo" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Ảnh bìa">
            <CustomInput v-model="form.anh_bia" maxlength="255" placeholder="URL ảnh bìa/campus" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Giới thiệu">
            <CustomInput
              v-model="form.gioi_thieu"
              type="textarea"
              :rows="4"
              maxlength="20000"
              show-word-limit
              placeholder="Mô tả chi tiết, lịch sử trường"
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

.filter-region {
  width: 180px;
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
  .filter-region,
  .filter-status {
    width: 100%;
  }
}
</style>
