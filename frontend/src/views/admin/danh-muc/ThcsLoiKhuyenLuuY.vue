<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo nội dung, hướng đi"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.thcs_huong_di_id"
          placeholder="Chọn hướng đi"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption v-for="item in huongOptions" :key="item.id" :label="nhanHuong(item)" :value="item.id" />
        </CustomSelect>
        <CustomSelect v-model="filters.doi_tuong_nhan" placeholder="Chọn đối tượng nhận" clearable @change="onSearch">
          <CustomOption
            v-for="item in DOI_TUONG_NHAN_LUU_Y"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Lời khuyên, lưu ý theo hướng đi sau THCS</h2>
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
            Thêm lời khuyên
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
        <CustomTableColumn prop="ten_huong" label="Hướng đi" min-width="180" />
        <CustomTableColumn label="Đối tượng nhận" width="200" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauEnum(DOI_TUONG_NHAN_LUU_Y, row.doi_tuong_nhan)" effect="light">
              {{ nhanEnum(DOI_TUONG_NHAN_LUU_Y, row.doi_tuong_nhan) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="noi_dung_luu_y" label="Nội dung lưu ý" min-width="380" />
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, rutGon(row.noi_dung_luu_y))">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có lời khuyên, lưu ý nào." />
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
    :title="editingId ? 'Cập nhật lời khuyên, lưu ý' : 'Thêm lời khuyên, lưu ý'"
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
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        placeholder="Dán mảng JSON vào đây (dùng ma_huong hoặc thcs_huong_di_id)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Hướng đi" prop="thcs_huong_di_id">
          <CustomSelect v-model="form.thcs_huong_di_id" placeholder="Chọn hướng đi" filterable>
            <CustomOption v-for="item in huongOptions" :key="item.id" :label="nhanHuong(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Đối tượng nhận" prop="doi_tuong_nhan">
          <CustomSelect v-model="form.doi_tuong_nhan" placeholder="Chọn đối tượng nhận" :clearable="false">
            <CustomOption
              v-for="item in DOI_TUONG_NHAN_LUU_Y"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
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
        <CustomFormItem class="form-grid__full" label="Nội dung lưu ý" prop="noi_dung_luu_y">
          <CustomInput
            v-model="form.noi_dung_luu_y"
            type="textarea"
            :rows="4"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập nội dung lưu ý"
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
import { loiKhuyenLuuYApi } from '@/api/thcsHuongDi'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, useBangThcs, useHuongDiThcs } from '@/composables/useThcsHuongDi'
import { DOI_TUONG_NHAN_LUU_Y, mauEnum, nhanEnum } from '@/constants/thcsHuongDi'

const JSON_SAMPLE = `[
  {
    "ma_huong": "THPT_CONG_LAP",
    "doi_tuong_nhan": "hoc_sinh",
    "noi_dung_luu_y": "Lập kế hoạch ôn thi vào lớp 10 từ đầu năm lớp 9, ưu tiên 3 môn thi chính.",
    "thu_tu_hien_thi": 1
  },
  {
    "ma_huong": "THPT_CONG_LAP",
    "doi_tuong_nhan": "phu_huynh",
    "noi_dung_luu_y": "Tìm hiểu tỷ lệ chọi của các trường trong khu vực để chọn nguyện vọng phù hợp.",
    "thu_tu_hien_thi": 2
  }
]`

const filters = reactive({ q: '', thcs_huong_di_id: '', doi_tuong_nhan: '' })

const { huongOptions, loadHuongOptions, nhanHuong, huongTuJson } = useHuongDiThcs()
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
  api: loiKhuyenLuuYApi,
  nhan: 'lời khuyên, lưu ý',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thcs_huong_di_id) params.thcs_huong_di_id = filters.thcs_huong_di_id
    if (filters.doi_tuong_nhan) params.doi_tuong_nhan = filters.doi_tuong_nhan
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'lời khuyên, lưu ý' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  thcs_huong_di_id: [{ required: true, message: 'Vui lòng chọn hướng đi', trigger: 'change' }],
  noi_dung_luu_y: [{ required: true, message: 'Vui lòng nhập nội dung lưu ý', trigger: 'blur' }],
}

function emptyForm() {
  return {
    thcs_huong_di_id: null,
    doi_tuong_nhan: 'ca_hai',
    noi_dung_luu_y: '',
    thu_tu_hien_thi: 0,
  }
}

function rutGon(text) {
  return text.length > 60 ? `${text.slice(0, 60)}…` : text
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
    thcs_huong_di_id: item.thcs_huong_di_id,
    doi_tuong_nhan: item.doi_tuong_nhan || 'ca_hai',
    noi_dung_luu_y: String(item.noi_dung_luu_y ?? '').trim(),
    thu_tu_hien_thi: Number(item.thu_tu_hien_thi) || 0,
  }
}

function openCreate() {
  resetForm()
  // Đang lọc thì chọn sẵn hướng đi, đối tượng đó.
  form.thcs_huong_di_id = filters.thcs_huong_di_id || null
  if (filters.doi_tuong_nhan) form.doi_tuong_nhan = filters.doi_tuong_nhan
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
  const doiTuongHopLe = DOI_TUONG_NHAN_LUU_Y.map((item) => item.value)
  let items
  try {
    items = docMangJson(jsonText.value, 'lời khuyên, lưu ý').map((item, index) => {
      const line = index + 1
      const payload = chuanHoa({ ...item, thcs_huong_di_id: huongTuJson(item, line) })
      if (!doiTuongHopLe.includes(payload.doi_tuong_nhan)) {
        throw new Error(`Phần tử thứ ${line}: doi_tuong_nhan phải là ${doiTuongHopLe.join(', ')}`)
      }
      if (!payload.noi_dung_luu_y) throw new Error(`Phần tử thứ ${line} thiếu noi_dung_luu_y`)
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({
    items,
    createBatch: loiKhuyenLuuYApi.createBulk,
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
    const payload = chuanHoa(form)
    if (editingId.value) {
      await loiKhuyenLuuYApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật lời khuyên, lưu ý')
    } else {
      await loiKhuyenLuuYApi.create(payload)
      ElMessage.success('Đã thêm lời khuyên, lưu ý')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được lời khuyên, lưu ý'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadHuongOptions()
  load()
})
</script>
