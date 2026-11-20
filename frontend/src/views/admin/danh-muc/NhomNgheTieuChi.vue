<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên nhóm nghề hoặc tiêu chí"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.nhom_nghe_di_lam_id"
          class="filter-parent"
          placeholder="Chọn nhóm nghề"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.tieu_chi_goi_y_id"
          class="filter-parent"
          placeholder="Chọn tiêu chí"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in tieuChiOptions"
            :key="item.id"
            :label="nhanTieuChi(item)"
            :value="item.id"
          />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Tiêu chí của nhóm nghề</h2>
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
            Gắn tiêu chí
          </CustomButton>
        </div>
      </div>

      <CustomTable
        ref="tableRef"
        :loading="loading"
        :data="rows"
        :row-key="khoa"
        stripe
        border
        @selection-change="onSelectionChange"
      >
        <CustomTableColumn type="selection" width="48" reserve-selection align="center" />
        <CustomTableColumn label="STT" width="72" align="center">
          <template #default="{ $index }">{{ rowIndex($index) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Nhóm nghề" min-width="240">
          <template #default="{ row }">{{ row.ten_nhom }} ({{ row.ma_nhom }})</template>
        </CustomTableColumn>
        <CustomTableColumn label="Tiêu chí" min-width="260">
          <template #default="{ row }">{{ row.ten_tieu_chi }} ({{ row.ma_tieu_chi }})</template>
        </CustomTableColumn>
        <CustomTableColumn label="Nhóm tiêu chí" width="150" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.nhom_tieu_chi" type="info" effect="light">{{ row.nhom_tieu_chi }}</CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Điểm phù hợp" width="140" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.diem_phu_hop" :type="mauDiem(row.diem_phu_hop)" effect="light">
              {{ row.diem_phu_hop }}/5
            </CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Ghi chú" min-width="220">
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
          <CustomEmpty description="Chưa gắn tiêu chí nào cho nhóm nghề." />
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
    :title="dangSua ? 'Cập nhật tiêu chí của nhóm nghề' : 'Gắn tiêu chí cho nhóm nghề'"
    width="800px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomRadioGroup v-if="!dangSua" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!dangSua && createMode === 'json'" class="json-panel">
      <div class="json-panel__head">
        <div class="json-panel__actions">
          <JsonFileButton v-model="jsonText" />
          <CustomButton text type="primary" @click="fillJsonSample">Điền mẫu</CustomButton>
        </div>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        placeholder="Dán mảng JSON vào đây (dùng ma_nhom, ma_tieu_chi hoặc id)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Nhóm nghề" prop="nhom_nghe_di_lam_id">
          <CustomSelect
            v-model="form.nhom_nghe_di_lam_id"
            placeholder="Chọn nhóm nghề"
            filterable
            :disabled="dangSua"
          >
            <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tiêu chí" prop="tieu_chi_goi_y_id">
          <CustomSelect v-model="form.tieu_chi_goi_y_id" placeholder="Chọn tiêu chí" filterable :disabled="dangSua">
            <CustomOption
              v-for="item in tieuChiOptions"
              :key="item.id"
              :label="nhanTieuChi(item)"
              :value="item.id"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Điểm phù hợp" prop="diem_phu_hop">
          <CustomSelect v-model="form.diem_phu_hop" placeholder="Chọn điểm phù hợp" clearable>
            <CustomOption v-for="item in MUC_DIEM" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput v-model="form.ghi_chu" maxlength="500" show-word-limit placeholder="Nhập ghi chú (nếu có)" />
        </CustomFormItem>
      </div>
    </CustomForm>
    <template #footer>
      <JsonImportDialogFooter
        :batch="jsonImport"
        :saving="saving"
        :show-progress="!dangSua && createMode === 'json'"
        @cancel="dialogVisible = false"
        @save="onSubmit"
      />
    </template>
  </CustomDialog>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createNhomNgheTieuChi,
  createNhomNgheTieuChiBulk,
  deleteNhomNgheTieuChi,
  deleteNhomNgheTieuChiMany,
  fetchNhomNgheDiLam,
  fetchNhomNgheTieuChi,
  fetchTieuChiGoiY,
  updateNhomNgheTieuChi,
} from '@/api/nhomNgheDiLam'

const MUC_DIEM = [
  { value: 1, label: '1 - Rất ít phù hợp' },
  { value: 2, label: '2 - Ít phù hợp' },
  { value: 3, label: '3 - Phù hợp vừa' },
  { value: 4, label: '4 - Phù hợp' },
  { value: 5, label: '5 - Rất phù hợp' },
]

const JSON_SAMPLE = `[
  {
    "ma_nhom": "LAM_DEP",
    "ma_tieu_chi": "KHEO_TAY",
    "diem_phu_hop": 5,
    "ghi_chu": "Yêu cầu tỉ mỉ cao"
  },
  {
    "nhom_nghe_di_lam_id": 1,
    "tieu_chi_goi_y_id": 2,
    "diem_phu_hop": 3
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
// Dòng đang sửa (khóa ghép không đổi được khi sửa).
const dangSua = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'liên kết' })
const formRef = ref()
const nhomOptions = ref([])
const tieuChiOptions = ref([])

const filters = reactive({
  q: '',
  nhom_nghe_di_lam_id: '',
  tieu_chi_goi_y_id: '',
})

const form = reactive(emptyForm())

const rules = {
  nhom_nghe_di_lam_id: [{ required: true, message: 'Vui lòng chọn nhóm nghề', trigger: 'change' }],
  tieu_chi_goi_y_id: [{ required: true, message: 'Vui lòng chọn tiêu chí', trigger: 'change' }],
}

function emptyForm() {
  return {
    nhom_nghe_di_lam_id: null,
    tieu_chi_goi_y_id: null,
    diem_phu_hop: null,
    ghi_chu: '',
  }
}

function khoa(row) {
  return `${row.nhom_nghe_di_lam_id}-${row.tieu_chi_goi_y_id}`
}

function nhanNhom(item) {
  return `${item.ten_nhom} (${item.ma_nhom})`
}

function nhanTieuChi(item) {
  return `${item.ten_tieu_chi} (${item.ma_tieu_chi})`
}

function mauDiem(diem) {
  if (diem >= 5) return 'success'
  if (diem >= 4) return 'primary'
  if (diem >= 3) return 'warning'
  return 'info'
}

function resetForm() {
  Object.assign(form, emptyForm())
  dangSua.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonImport.reset()
  formRef.value?.clearValidate()
}

// Nhận id hoặc mã; mã được đổi sang id theo danh sách đã tải.
function timId(item, line, { idKey, maKey, options, nhanLoi }) {
  const id = Number(item[idKey]) || null
  if (id) return id
  if (!item[maKey]) throw new Error(`Phần tử thứ ${line} thiếu ${maKey} hoặc ${idKey}`)
  const ma = String(item[maKey]).trim().toUpperCase()
  const found = options.find((o) => o[maKey] === ma)
  if (!found) throw new Error(`Phần tử thứ ${line}: không tìm thấy ${nhanLoi} có mã ${ma}`)
  return found.id
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng liên kết.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ma_nhom": "...", "ma_tieu_chi": "...", "diem_phu_hop": 5 }]')
  }
  if (!data.length) {
    throw new Error('Mảng liên kết đang trống')
  }
  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một liên kết`)
    }
    const diem = item.diem_phu_hop == null ? null : Number(item.diem_phu_hop)
    if (diem !== null && !(Number.isInteger(diem) && diem >= 1 && diem <= 5)) {
      throw new Error(`Phần tử thứ ${line}: diem_phu_hop phải là số nguyên 1-5`)
    }
    return {
      nhom_nghe_di_lam_id: timId(item, line, {
        idKey: 'nhom_nghe_di_lam_id',
        maKey: 'ma_nhom',
        options: nhomOptions.value,
        nhanLoi: 'nhóm nghề',
      }),
      tieu_chi_goi_y_id: timId(item, line, {
        idKey: 'tieu_chi_goi_y_id',
        maKey: 'ma_tieu_chi',
        options: tieuChiOptions.value,
        nhanLoi: 'tiêu chí',
      }),
      diem_phu_hop: diem,
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

async function loadAll(fetchFn) {
  const size = 100
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchFn({ page: current, page_size: size })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  return items
}

async function loadOptions() {
  try {
    const [nhom, tieuChi] = await Promise.all([loadAll(fetchNhomNgheDiLam), loadAll(fetchTieuChiGoiY)])
    nhomOptions.value = nhom
    tieuChiOptions.value = tieuChi
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nhóm nghề / tiêu chí'))
  }
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.nhom_nghe_di_lam_id) params.nhom_nghe_di_lam_id = filters.nhom_nghe_di_lam_id
    if (filters.tieu_chi_goi_y_id) params.tieu_chi_goi_y_id = filters.tieu_chi_goi_y_id
    const data = await fetchNhomNgheTieuChi(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách liên kết'))
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
  // Đang lọc thì chọn sẵn nhóm nghề / tiêu chí đó.
  form.nhom_nghe_di_lam_id = filters.nhom_nghe_di_lam_id || null
  form.tieu_chi_goi_y_id = filters.tieu_chi_goi_y_id || null
  dialogVisible.value = true
}

function openEdit(row) {
  dangSua.value = row
  Object.assign(form, {
    nhom_nghe_di_lam_id: row.nhom_nghe_di_lam_id,
    tieu_chi_goi_y_id: row.tieu_chi_goi_y_id,
    diem_phu_hop: row.diem_phu_hop,
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
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
    createBatch: createNhomNgheTieuChiBulk,
    jsonText,
    saving,
    dialogVisible,
    reload: load,
  })
}

async function onSubmit() {
  if (!dangSua.value && createMode.value === 'json') {
    await onSubmitJson()
    return
  }

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const phan = { diem_phu_hop: form.diem_phu_hop ?? null, ghi_chu: form.ghi_chu?.trim() || null }
    if (dangSua.value) {
      await updateNhomNgheTieuChi(dangSua.value.nhom_nghe_di_lam_id, dangSua.value.tieu_chi_goi_y_id, phan)
      ElMessage.success('Đã cập nhật liên kết')
    } else {
      await createNhomNgheTieuChi({
        nhom_nghe_di_lam_id: form.nhom_nghe_di_lam_id,
        tieu_chi_goi_y_id: form.tieu_chi_goi_y_id,
        ...phan,
      })
      ElMessage.success('Đã gắn tiêu chí cho nhóm nghề')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được liên kết'))
  } finally {
    saving.value = false
  }
}

async function xacNhanXoa(noiDung) {
  try {
    await ElMessageBox.confirm(noiDung, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
    return true
  } catch {
    return false
  }
}

async function onDelete(row) {
  if (!(await xacNhanXoa(`Bỏ tiêu chí "${row.ten_tieu_chi}" khỏi nhóm nghề "${row.ten_nhom}"?`))) return
  try {
    await deleteNhomNgheTieuChi(row.nhom_nghe_di_lam_id, row.tieu_chi_goi_y_id)
    ElMessage.success('Đã xóa liên kết')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được liên kết'))
  }
}

async function onDeleteSelected() {
  const items = selectedRows.value.map((row) => ({
    nhom_nghe_di_lam_id: row.nhom_nghe_di_lam_id,
    tieu_chi_goi_y_id: row.tieu_chi_goi_y_id,
  }))
  if (!items.length) return
  if (!(await xacNhanXoa(`Xóa ${items.length} liên kết đã chọn?`))) return

  deleting.value = true
  try {
    const daChon = new Set(selectedRows.value.map(khoa))
    const removedOnPage = rows.value.filter((row) => daChon.has(khoa(row))).length
    const result = await deleteNhomNgheTieuChiMany(items)
    ElMessage.success(`Đã xóa ${result.deleted} liên kết`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các liên kết đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
