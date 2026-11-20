<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tiêu đề, nội dung, hướng đi"
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
        <CustomSelect v-model="filters.loai" placeholder="Chọn loại" clearable @change="onSearch">
          <CustomOption v-for="item in LOAI_UU_NHUOC_DIEM" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Ưu điểm, nhược điểm của hướng đi sau THCS</h2>
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
            Thêm ưu/nhược điểm
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
        <CustomTableColumn label="Loại" width="130" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauEnum(LOAI_UU_NHUOC_DIEM, row.loai)" effect="light">
              {{ nhanEnum(LOAI_UU_NHUOC_DIEM, row.loai) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="tieu_de" label="Tiêu đề" min-width="220" />
        <CustomTableColumn prop="noi_dung_chi_tiet" label="Nội dung chi tiết" min-width="320" />
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.tieu_de)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có ưu/nhược điểm nào." />
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
    :title="editingId ? 'Cập nhật ưu/nhược điểm' : 'Thêm ưu/nhược điểm'"
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
        <CustomFormItem label="Loại" prop="loai">
          <CustomSelect v-model="form.loai" placeholder="Chọn loại" :clearable="false">
            <CustomOption
              v-for="item in LOAI_UU_NHUOC_DIEM"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tiêu đề" prop="tieu_de">
          <CustomInput v-model="form.tieu_de" maxlength="255" placeholder="Nhập tiêu đề" />
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
        <CustomFormItem class="form-grid__full" label="Nội dung chi tiết" prop="noi_dung_chi_tiet">
          <CustomInput
            v-model="form.noi_dung_chi_tiet"
            type="textarea"
            :rows="4"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập nội dung chi tiết"
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
import { uuNhuocDiemApi } from '@/api/thcsHuongDi'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, useBangThcs, useHuongDiThcs } from '@/composables/useThcsHuongDi'
import { LOAI_UU_NHUOC_DIEM, mauEnum, nhanEnum } from '@/constants/thcsHuongDi'

const JSON_SAMPLE = `[
  {
    "ma_huong": "THPT_CONG_LAP",
    "loai": "uu_diem",
    "tieu_de": "Lộ trình rõ ràng lên đại học",
    "noi_dung_chi_tiet": "Chương trình phổ thông đầy đủ, thuận lợi khi thi tốt nghiệp và xét tuyển đại học.",
    "thu_tu_hien_thi": 1
  },
  {
    "ma_huong": "THPT_CONG_LAP",
    "loai": "nhuoc_diem",
    "tieu_de": "Áp lực thi tuyển lớp 10",
    "noi_dung_chi_tiet": "Tỷ lệ chọi cao ở nhiều địa phương, cần ôn luyện sớm.",
    "thu_tu_hien_thi": 1
  }
]`

const filters = reactive({ q: '', thcs_huong_di_id: '', loai: '' })

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
  api: uuNhuocDiemApi,
  nhan: 'ưu/nhược điểm',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thcs_huong_di_id) params.thcs_huong_di_id = filters.thcs_huong_di_id
    if (filters.loai) params.loai = filters.loai
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'ưu/nhược điểm' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  thcs_huong_di_id: [{ required: true, message: 'Vui lòng chọn hướng đi', trigger: 'change' }],
  loai: [{ required: true, message: 'Vui lòng chọn loại', trigger: 'change' }],
  tieu_de: [{ required: true, message: 'Vui lòng nhập tiêu đề', trigger: 'blur' }],
  noi_dung_chi_tiet: [{ required: true, message: 'Vui lòng nhập nội dung chi tiết', trigger: 'blur' }],
}

function emptyForm() {
  return {
    thcs_huong_di_id: null,
    loai: 'uu_diem',
    tieu_de: '',
    noi_dung_chi_tiet: '',
    thu_tu_hien_thi: 0,
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
    thcs_huong_di_id: item.thcs_huong_di_id,
    loai: item.loai,
    tieu_de: String(item.tieu_de ?? '').trim(),
    noi_dung_chi_tiet: String(item.noi_dung_chi_tiet ?? '').trim(),
    thu_tu_hien_thi: Number(item.thu_tu_hien_thi) || 0,
  }
}

function openCreate() {
  resetForm()
  // Đang lọc thì chọn sẵn hướng đi, loại đó.
  form.thcs_huong_di_id = filters.thcs_huong_di_id || null
  if (filters.loai) form.loai = filters.loai
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
  const loaiHopLe = LOAI_UU_NHUOC_DIEM.map((item) => item.value)
  let items
  try {
    items = docMangJson(jsonText.value, 'ưu/nhược điểm').map((item, index) => {
      const line = index + 1
      const payload = chuanHoa({ ...item, thcs_huong_di_id: huongTuJson(item, line) })
      if (!loaiHopLe.includes(payload.loai)) {
        throw new Error(`Phần tử thứ ${line}: loai phải là ${loaiHopLe.join(' hoặc ')}`)
      }
      if (!payload.tieu_de || !payload.noi_dung_chi_tiet) {
        throw new Error(`Phần tử thứ ${line} thiếu tieu_de hoặc noi_dung_chi_tiet`)
      }
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: uuNhuocDiemApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await uuNhuocDiemApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật ưu/nhược điểm')
    } else {
      await uuNhuocDiemApi.create(payload)
      ElMessage.success('Đã thêm ưu/nhược điểm')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được ưu/nhược điểm'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadHuongOptions()
  load()
})
</script>
