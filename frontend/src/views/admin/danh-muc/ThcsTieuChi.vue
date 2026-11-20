<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên, mô tả tiêu chí"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect v-model="filters.nhom_tieu_chi" placeholder="Chọn nhóm tiêu chí" clearable @change="onSearch">
          <CustomOption v-for="nhom in nhomOptions" :key="nhom" :label="nhom" :value="nhom" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Tiêu chí đánh giá hướng đi sau THCS</h2>
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
        <CustomTableColumn prop="ma_tieu_chi" label="Mã tiêu chí" width="170" />
        <CustomTableColumn prop="ten_tieu_chi" label="Tên tiêu chí" min-width="220" />
        <CustomTableColumn label="Nhóm tiêu chí" width="170" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.nhom_tieu_chi" type="info" effect="light">{{ row.nhom_tieu_chi }}</CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Mô tả" min-width="280">
          <template #default="{ row }">{{ row.mo_ta_tieu_chi || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="thu_tu_hien_thi" label="Thứ tự" width="90" align="center" />
        <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <CustomTooltip content="Sửa" placement="top">
                <CustomButton link type="primary" aria-label="Sửa" @click="openEdit(row)">
                  <CustomIcon><Edit /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Xóa" placement="top">
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_tieu_chi)">
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
          @current-change="load"
          @size-change="onSearch"
        />
      </div>
    </CustomCard>
  </div>

  <CustomDialog
    v-model="dialogVisible"
    :title="editingId ? 'Cập nhật tiêu chí' : 'Thêm tiêu chí'"
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
          <CustomButton text type="primary" @click="jsonText = JSON_SAMPLE">Điền mẫu</CustomButton>
        </div>
      </div>
      <CustomInput v-model="jsonText" class="json-input" type="textarea" :rows="16" placeholder="Dán mảng JSON vào đây" />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem label="Mã tiêu chí" prop="ma_tieu_chi">
          <CustomInput v-model="form.ma_tieu_chi" maxlength="50" placeholder="Nhập mã tiêu chí (ví dụ: HOC_LUC)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên tiêu chí" prop="ten_tieu_chi">
          <CustomInput v-model="form.ten_tieu_chi" maxlength="255" placeholder="Nhập tên tiêu chí" />
        </CustomFormItem>
        <CustomFormItem label="Nhóm tiêu chí" prop="nhom_tieu_chi">
          <!-- Chọn nhóm đã có hoặc gõ nhóm mới. -->
          <CustomSelect
            v-model="form.nhom_tieu_chi"
            placeholder="Chọn hoặc nhập nhóm tiêu chí"
            filterable
            allow-create
            default-first-option
            clearable
          >
            <CustomOption v-for="nhom in nhomOptions" :key="nhom" :label="nhom" :value="nhom" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Thứ tự hiển thị" prop="thu_tu_hien_thi">
          <CustomInputNumber
            v-model="form.thu_tu_hien_thi"
            placeholder="Nhập thứ tự hiển thị"
            :min="0"
            :max="100000"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mô tả tiêu chí" prop="mo_ta_tieu_chi">
          <CustomInput
            v-model="form.mo_ta_tieu_chi"
            maxlength="255"
            show-word-limit
            placeholder="Nhập mô tả tiêu chí"
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
import { ElMessage } from 'element-plus'
import { tieuChiApi } from '@/api/thcsHuongDi'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangThcs } from '@/composables/useThcsHuongDi'

const JSON_SAMPLE = `[
  {
    "ma_tieu_chi": "HOC_LUC",
    "ten_tieu_chi": "Học lực lớp 9",
    "mo_ta_tieu_chi": "Kết quả học tập và khả năng thi tuyển vào lớp 10",
    "nhom_tieu_chi": "Năng lực",
    "thu_tu_hien_thi": 1
  },
  {
    "ma_tieu_chi": "TAI_CHINH",
    "ten_tieu_chi": "Khả năng tài chính gia đình",
    "nhom_tieu_chi": "Hoàn cảnh",
    "thu_tu_hien_thi": 2
  }
]`

const filters = reactive({ q: '', nhom_tieu_chi: '' })
const nhomOptions = ref([])

const {
  loading,
  deleting,
  rows,
  selectedRows,
  tableRef,
  total,
  page,
  pageSize,
  load,
  onSelectionChange,
  rowIndex,
  onSearch,
  onDelete,
  onDeleteSelected,
} = useBangThcs({
  api: tieuChiApi,
  nhan: 'tiêu chí',
  canhBaoXoa: 'Điểm phù hợp của các hướng đi với tiêu chí cũng bị xóa theo.',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.nhom_tieu_chi) params.nhom_tieu_chi = filters.nhom_tieu_chi
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'tiêu chí' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  ma_tieu_chi: [{ required: true, message: 'Vui lòng nhập mã tiêu chí', trigger: 'blur' }],
  ten_tieu_chi: [{ required: true, message: 'Vui lòng nhập tên tiêu chí', trigger: 'blur' }],
}

function emptyForm() {
  return {
    ma_tieu_chi: '',
    ten_tieu_chi: '',
    mo_ta_tieu_chi: '',
    nhom_tieu_chi: '',
    thu_tu_hien_thi: 0,
  }
}

async function loadNhom() {
  try {
    nhomOptions.value = await tieuChiApi.fetchNhom()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nhóm tiêu chí'))
  }
}

async function taiLai() {
  await Promise.all([load(), loadNhom()])
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
    mo_ta_tieu_chi: giaTriTuyChon(item.mo_ta_tieu_chi),
    nhom_tieu_chi: giaTriTuyChon(item.nhom_tieu_chi),
    thu_tu_hien_thi: Number(item.thu_tu_hien_thi) || 0,
  }
}

function openCreate() {
  resetForm()
  form.nhom_tieu_chi = filters.nhom_tieu_chi || ''
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  const values = emptyForm()
  for (const key of Object.keys(values)) {
    if (row[key] != null) values[key] = row[key]
  }
  Object.assign(form, values)
  dialogVisible.value = true
}

async function onSubmitJson() {
  let items
  try {
    items = docMangJson(jsonText.value, 'tiêu chí').map((item, index) => {
      const payload = chuanHoa(item)
      if (!payload.ma_tieu_chi || !payload.ten_tieu_chi) {
        throw new Error(`Phần tử thứ ${index + 1} thiếu ma_tieu_chi hoặc ten_tieu_chi`)
      }
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: tieuChiApi.createBulk, jsonText, saving, dialogVisible, reload: taiLai })
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
      await tieuChiApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật tiêu chí')
    } else {
      await tieuChiApi.create(payload)
      ElMessage.success('Đã thêm tiêu chí')
    }
    dialogVisible.value = false
    await taiLai()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được tiêu chí'))
  } finally {
    saving.value = false
  }
}

onMounted(taiLai)
</script>
