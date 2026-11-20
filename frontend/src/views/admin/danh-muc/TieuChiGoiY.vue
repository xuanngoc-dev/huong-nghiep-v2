<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên tiêu chí"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.nhom_tieu_chi"
          class="filter-parent"
          placeholder="Chọn nhóm tiêu chí"
          clearable
          @change="onSearch"
        >
          <CustomOption v-for="item in nhomOptions" :key="item" :label="item" :value="item" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách tiêu chí gợi ý</h2>
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
            Thêm tiêu chí
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
        <CustomTableColumn prop="ma_tieu_chi" label="Mã tiêu chí" width="220" />
        <CustomTableColumn prop="ten_tieu_chi" label="Tên tiêu chí" min-width="280" />
        <CustomTableColumn label="Nhóm tiêu chí" width="180" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.nhom_tieu_chi" type="info" effect="light">{{ row.nhom_tieu_chi }}</CustomTag>
            <span v-else>—</span>
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
          <CustomEmpty description="Chưa có tiêu chí nào." />
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
    :title="editingId ? 'Cập nhật tiêu chí gợi ý' : 'Thêm tiêu chí gợi ý'"
    width="560px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomRadioGroup v-if="!editingId" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!editingId && createMode === 'json'" class="json-panel">
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
        placeholder="Dán mảng JSON vào đây"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem label="Mã tiêu chí" prop="ma_tieu_chi">
          <CustomInput v-model="form.ma_tieu_chi" maxlength="50" placeholder="Nhập mã tiêu chí (ví dụ: KHEO_TAY)" />
        </CustomFormItem>
        <CustomFormItem label="Nhóm tiêu chí" prop="nhom_tieu_chi">
          <CustomSelect
            v-model="form.nhom_tieu_chi"
            placeholder="Chọn hoặc nhập nhóm tiêu chí"
            clearable
            filterable
            allow-create
            default-first-option
          >
            <CustomOption v-for="item in nhomGoiY" :key="item" :label="item" :value="item" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên tiêu chí" prop="ten_tieu_chi">
          <CustomInput v-model="form.ten_tieu_chi" maxlength="255" placeholder="Nhập tên tiêu chí" />
        </CustomFormItem>
      </div>
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

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createTieuChiGoiY,
  createTieuChiGoiYBulk,
  deleteTieuChiGoiY,
  deleteTieuChiGoiYMany,
  fetchNhomTieuChi,
  fetchTieuChiGoiY,
  updateTieuChiGoiY,
} from '@/api/nhomNgheDiLam'

// Nhóm gợi ý sẵn khi nhập; vẫn cho tạo nhóm mới.
const NHOM_MAC_DINH = ['Sở thích', 'Năng lực', 'Hoàn cảnh', 'Mục tiêu']

const JSON_SAMPLE = `[
  {
    "ma_tieu_chi": "THICH_LAM_NGOAI_TROI",
    "ten_tieu_chi": "Thích làm việc ngoài trời",
    "nhom_tieu_chi": "Sở thích"
  },
  {
    "ma_tieu_chi": "GIOI_NGOAI_NGU",
    "ten_tieu_chi": "Giao tiếp được ngoại ngữ",
    "nhom_tieu_chi": "Năng lực"
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
const jsonImport = useJsonBatchImport({ label: 'tiêu chí' })
const formRef = ref()
const nhomOptions = ref([])
const nhomGoiY = computed(() => [...new Set([...NHOM_MAC_DINH, ...nhomOptions.value])])

const filters = reactive({
  q: '',
  nhom_tieu_chi: '',
})

const form = reactive(emptyForm())

const rules = {
  ma_tieu_chi: [{ required: true, message: 'Vui lòng nhập mã tiêu chí', trigger: 'blur' }],
  ten_tieu_chi: [{ required: true, message: 'Vui lòng nhập tên tiêu chí', trigger: 'blur' }],
}

function emptyForm() {
  return {
    ma_tieu_chi: '',
    ten_tieu_chi: '',
    nhom_tieu_chi: '',
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

function chuanHoa(item) {
  return {
    ma_tieu_chi: String(item.ma_tieu_chi ?? '').trim().toUpperCase(),
    ten_tieu_chi: String(item.ten_tieu_chi ?? '').trim(),
    nhom_tieu_chi: item.nhom_tieu_chi == null ? null : String(item.nhom_tieu_chi).trim() || null,
  }
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng tiêu chí.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ma_tieu_chi": "...", "ten_tieu_chi": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng tiêu chí đang trống')
  }
  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một tiêu chí`)
    }
    const payload = chuanHoa(item)
    if (!payload.ma_tieu_chi || !payload.ten_tieu_chi) {
      throw new Error(`Phần tử thứ ${line} thiếu ma_tieu_chi hoặc ten_tieu_chi`)
    }
    return payload
  })
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function loadNhom() {
  try {
    nhomOptions.value = await fetchNhomTieuChi()
  } catch {
    nhomOptions.value = []
  }
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.nhom_tieu_chi) params.nhom_tieu_chi = filters.nhom_tieu_chi
    const data = await fetchTieuChiGoiY(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách tiêu chí'))
  } finally {
    loading.value = false
  }
}

// Sau khi thêm/sửa/xóa có thể phát sinh hoặc mất nhóm tiêu chí.
async function reload() {
  await Promise.all([load(), loadNhom()])
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
    ma_tieu_chi: row.ma_tieu_chi,
    ten_tieu_chi: row.ten_tieu_chi,
    nhom_tieu_chi: row.nhom_tieu_chi || '',
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
    createBatch: createTieuChiGoiYBulk,
    jsonText,
    saving,
    dialogVisible,
    reload,
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
    const payload = chuanHoa(form)
    if (editingId.value) {
      await updateTieuChiGoiY(editingId.value, payload)
      ElMessage.success('Đã cập nhật tiêu chí')
    } else {
      await createTieuChiGoiY(payload)
      ElMessage.success('Đã thêm tiêu chí')
    }
    dialogVisible.value = false
    await reload()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được tiêu chí'))
  } finally {
    saving.value = false
  }
}

async function xacNhanXoa(noiDung) {
  try {
    await ElMessageBox.confirm(
      `${noiDung} Liên kết của tiêu chí với các nhóm nghề cũng bị xóa theo.`,
      'Xác nhận xóa',
      { type: 'warning', confirmButtonText: 'Xóa', cancelButtonText: 'Hủy', confirmButtonClass: 'el-button--danger' },
    )
    return true
  } catch {
    return false
  }
}

async function onDelete(row) {
  if (!(await xacNhanXoa(`Xóa tiêu chí "${row.ten_tieu_chi}" (${row.ma_tieu_chi})?`))) return
  try {
    await deleteTieuChiGoiY(row.id)
    ElMessage.success('Đã xóa tiêu chí')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await reload()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được tiêu chí'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return
  if (!(await xacNhanXoa(`Xóa ${ids.length} tiêu chí đã chọn?`))) return

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteTieuChiGoiYMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} tiêu chí`)
    clearSelection()
    loadNhom()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các tiêu chí đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(reload)
</script>
