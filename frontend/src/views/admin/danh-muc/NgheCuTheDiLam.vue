<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tên nghề, mã, tên nhóm"
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
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách nghề cụ thể</h2>
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
            Thêm nghề
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
        <CustomTableColumn prop="ten_nghe" label="Tên nghề" min-width="220" />
        <CustomTableColumn label="Nhóm nghề" min-width="240">
          <template #default="{ row }">{{ row.ten_nhom }} ({{ row.ma_nhom }})</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mô tả ngắn" min-width="280">
          <template #default="{ row }">{{ row.mo_ta_ngan || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Yêu cầu thêm" min-width="200">
          <template #default="{ row }">{{ row.yeu_cau_them || '—' }}</template>
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
          <CustomEmpty description="Chưa có nghề cụ thể nào." />
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
    :title="editingId ? 'Cập nhật nghề cụ thể' : 'Thêm nghề cụ thể'"
    width="800px"
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
        placeholder="Dán mảng JSON vào đây (dùng ma_nhom hoặc nhom_nghe_di_lam_id)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Nhóm nghề" prop="nhom_nghe_di_lam_id">
          <CustomSelect v-model="form.nhom_nghe_di_lam_id" placeholder="Chọn nhóm nghề" filterable>
            <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên nghề" prop="ten_nghe">
          <CustomInput v-model="form.ten_nghe" maxlength="255" placeholder="Nhập tên nghề" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Yêu cầu thêm" prop="yeu_cau_them">
          <CustomInput v-model="form.yeu_cau_them" maxlength="500" placeholder="Nhập yêu cầu thêm (nếu có)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mô tả ngắn" prop="mo_ta_ngan">
          <CustomInput
            v-model="form.mo_ta_ngan"
            type="textarea"
            :rows="3"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập mô tả ngắn"
          />
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
import { onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createNgheCuTheDiLam,
  createNgheCuTheDiLamBulk,
  deleteNgheCuTheDiLam,
  deleteNgheCuTheDiLamMany,
  fetchNgheCuTheDiLam,
  fetchNhomNgheDiLam,
  updateNgheCuTheDiLam,
} from '@/api/nhomNgheDiLam'

const JSON_SAMPLE = `[
  {
    "ma_nhom": "LAM_DEP",
    "ten_nghe": "Thợ trang điểm",
    "mo_ta_ngan": "Trang điểm cô dâu, sự kiện, chụp ảnh.",
    "yeu_cau_them": "Có bộ dụng cụ cá nhân"
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
const jsonImport = useJsonBatchImport({ label: 'nghề cụ thể' })
const formRef = ref()
const nhomOptions = ref([])

const filters = reactive({
  q: '',
  nhom_nghe_di_lam_id: '',
})

const form = reactive(emptyForm())

const rules = {
  nhom_nghe_di_lam_id: [{ required: true, message: 'Vui lòng chọn nhóm nghề', trigger: 'change' }],
  ten_nghe: [{ required: true, message: 'Vui lòng nhập tên nghề', trigger: 'blur' }],
}

function emptyForm() {
  return {
    nhom_nghe_di_lam_id: null,
    ten_nghe: '',
    mo_ta_ngan: '',
    yeu_cau_them: '',
  }
}

function nhanNhom(item) {
  return `${item.ten_nhom} (${item.ma_nhom})`
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng nghề cụ thể.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ma_nhom": "...", "ten_nghe": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng nghề cụ thể đang trống')
  }
  const theoMa = new Map(nhomOptions.value.map((item) => [item.ma_nhom, item.id]))
  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một nghề cụ thể`)
    }
    const ten = String(item.ten_nghe ?? '').trim()
    if (!ten) throw new Error(`Phần tử thứ ${line} thiếu ten_nghe`)
    let nhomId = Number(item.nhom_nghe_di_lam_id) || null
    if (!nhomId && item.ma_nhom) {
      const ma = String(item.ma_nhom).trim().toUpperCase()
      nhomId = theoMa.get(ma)
      if (!nhomId) throw new Error(`Phần tử thứ ${line}: không tìm thấy nhóm nghề có mã ${ma}`)
    }
    if (!nhomId) throw new Error(`Phần tử thứ ${line} thiếu ma_nhom hoặc nhom_nghe_di_lam_id`)
    return {
      nhom_nghe_di_lam_id: nhomId,
      ten_nghe: ten,
      mo_ta_ngan: item.mo_ta_ngan == null ? null : String(item.mo_ta_ngan).trim() || null,
      yeu_cau_them: item.yeu_cau_them == null ? null : String(item.yeu_cau_them).trim() || null,
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
    nhomOptions.value = await loadAll(fetchNhomNgheDiLam)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nhóm nghề'))
  }
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.nhom_nghe_di_lam_id) params.nhom_nghe_di_lam_id = filters.nhom_nghe_di_lam_id
    const data = await fetchNgheCuTheDiLam(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nghề cụ thể'))
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
  // Đang lọc theo một nhóm thì chọn sẵn nhóm đó.
  form.nhom_nghe_di_lam_id = filters.nhom_nghe_di_lam_id || null
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    nhom_nghe_di_lam_id: row.nhom_nghe_di_lam_id,
    ten_nghe: row.ten_nghe,
    mo_ta_ngan: row.mo_ta_ngan || '',
    yeu_cau_them: row.yeu_cau_them || '',
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    nhom_nghe_di_lam_id: form.nhom_nghe_di_lam_id,
    ten_nghe: form.ten_nghe.trim(),
    mo_ta_ngan: form.mo_ta_ngan?.trim() || null,
    yeu_cau_them: form.yeu_cau_them?.trim() || null,
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
    createBatch: createNgheCuTheDiLamBulk,
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
      await updateNgheCuTheDiLam(editingId.value, payload)
      ElMessage.success('Đã cập nhật nghề cụ thể')
    } else {
      await createNgheCuTheDiLam(payload)
      ElMessage.success('Đã thêm nghề cụ thể')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được nghề cụ thể'))
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
  if (!(await xacNhanXoa(`Xóa nghề "${row.ten_nghe}"?`))) return
  try {
    await deleteNgheCuTheDiLam(row.id)
    ElMessage.success('Đã xóa nghề cụ thể')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được nghề cụ thể'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return
  if (!(await xacNhanXoa(`Xóa ${ids.length} nghề cụ thể đã chọn?`))) return

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteNgheCuTheDiLamMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} nghề cụ thể`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các nghề cụ thể đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
