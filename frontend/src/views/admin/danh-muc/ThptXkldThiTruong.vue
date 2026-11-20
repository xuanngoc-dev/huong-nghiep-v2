<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên quốc gia, tên nhóm nghề"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.thpt_xkld_nhom_nghe_id"
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
        <h2 class="toolbar__title">Danh sách thị trường xuất khẩu lao động</h2>
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
            Thêm thị trường
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
        <CustomTableColumn label="Thị trường" min-width="160">
          <template #default="{ row }">{{ row.ten_quoc_gia }} ({{ row.ma_quoc_gia }})</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_nhom" label="Nhóm nghề" min-width="180" />
        <CustomTableColumn label="Loại visa" min-width="160">
          <template #default="{ row }">{{ row.loai_visa || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thu nhập riêng" min-width="200">
          <template #default="{ row }">{{ row.thu_nhap_rieng_text || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Hợp đồng" width="110" align="center">
          <template #default="{ row }">
            {{ row.thoi_han_hop_dong_nam != null ? `${row.thoi_han_hop_dong_nam} năm` : '—' }}
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Đặc điểm thị trường" min-width="280">
          <template #default="{ row }">{{ row.dac_diem_thi_truong || '—' }}</template>
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_quoc_gia)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có thị trường nào." />
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
    :title="editingId ? 'Cập nhật thị trường xuất khẩu lao động' : 'Thêm thị trường xuất khẩu lao động'"
    width="1040px"
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
        placeholder="Dán mảng JSON vào đây (dùng ma_nhom hoặc thpt_xkld_nhom_nghe_id)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Nhóm nghề" prop="thpt_xkld_nhom_nghe_id">
          <CustomSelect v-model="form.thpt_xkld_nhom_nghe_id" placeholder="Chọn nhóm nghề" filterable>
            <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Mã quốc gia" prop="ma_quoc_gia">
          <CustomInput v-model="form.ma_quoc_gia" maxlength="20" placeholder="Nhập mã quốc gia (ví dụ: JP)" />
        </CustomFormItem>
        <CustomFormItem label="Tên quốc gia" prop="ten_quoc_gia">
          <CustomInput v-model="form.ten_quoc_gia" maxlength="100" placeholder="Nhập tên quốc gia" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Loại visa" prop="loai_visa">
          <CustomInput v-model="form.loai_visa" maxlength="100" placeholder="Nhập loại visa (ví dụ: Thực tập sinh kỹ năng)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Thu nhập riêng (mô tả)" prop="thu_nhap_rieng_text">
          <CustomInput
            v-model="form.thu_nhap_rieng_text"
            maxlength="255"
            placeholder="Nhập thu nhập riêng (ví dụ: 180.000 - 220.000 JPY/tháng)"
          />
        </CustomFormItem>
        <CustomFormItem label="Thời hạn hợp đồng (năm)" prop="thoi_han_hop_dong_nam">
          <CustomInputNumber
            v-model="form.thoi_han_hop_dong_nam"
            placeholder="Nhập thời hạn hợp đồng"
            :min="0"
            :max="50"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Thứ tự hiển thị" prop="thu_tu_hien_thi">
          <CustomInputNumber
            v-model="form.thu_tu_hien_thi"
            placeholder="Nhập thứ tự hiển thị"
            :min="0"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Đặc điểm thị trường" prop="dac_diem_thi_truong">
          <CustomInput
            v-model="form.dac_diem_thi_truong"
            type="textarea"
            :rows="3"
            maxlength="5000"
            placeholder="Nhập đặc điểm thị trường"
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
import { thiTruongApi } from '@/api/thptXkld'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangXkld, useLienKetXkld } from '@/composables/useThptXkld'

const JSON_SAMPLE = `[
  {
    "ma_nhom": "CO_KHI",
    "ma_quoc_gia": "JP",
    "ten_quoc_gia": "Nhật Bản",
    "loai_visa": "Thực tập sinh kỹ năng",
    "dac_diem_thi_truong": "Nhu cầu lớn, kỷ luật lao động cao, nhiều đơn hàng cơ khí.",
    "thu_nhap_rieng_text": "180.000 - 220.000 JPY/tháng",
    "thoi_han_hop_dong_nam": 3,
    "thu_tu_hien_thi": 1
  }
]`

const filters = reactive({ q: '', thpt_xkld_nhom_nghe_id: '' })

const { nhomOptions, loadOptions, nhanNhom, lienKetTuJson } = useLienKetXkld({ coThiTruong: false })
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
} = useBangXkld({
  api: thiTruongApi,
  nhan: 'thị trường',
  canhBaoXoa: 'Nghề cụ thể, chi phí, thủ tục và kênh kết nối riêng của thị trường cũng bị xóa theo.',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thpt_xkld_nhom_nghe_id) params.thpt_xkld_nhom_nghe_id = filters.thpt_xkld_nhom_nghe_id
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'thị trường' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  thpt_xkld_nhom_nghe_id: [{ required: true, message: 'Vui lòng chọn nhóm nghề', trigger: 'change' }],
  ma_quoc_gia: [{ required: true, message: 'Vui lòng nhập mã quốc gia', trigger: 'blur' }],
  ten_quoc_gia: [{ required: true, message: 'Vui lòng nhập tên quốc gia', trigger: 'blur' }],
}

function emptyForm() {
  return {
    thpt_xkld_nhom_nghe_id: null,
    ma_quoc_gia: '',
    ten_quoc_gia: '',
    loai_visa: '',
    dac_diem_thi_truong: '',
    thu_nhap_rieng_text: '',
    thoi_han_hop_dong_nam: 3,
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
    thpt_xkld_nhom_nghe_id: item.thpt_xkld_nhom_nghe_id,
    ma_quoc_gia: String(item.ma_quoc_gia ?? '').trim().toUpperCase(),
    ten_quoc_gia: String(item.ten_quoc_gia ?? '').trim(),
    loai_visa: giaTriTuyChon(item.loai_visa),
    dac_diem_thi_truong: giaTriTuyChon(item.dac_diem_thi_truong),
    thu_nhap_rieng_text: giaTriTuyChon(item.thu_nhap_rieng_text),
    thoi_han_hop_dong_nam: giaTriTuyChon(item.thoi_han_hop_dong_nam) ?? 3,
    thu_tu_hien_thi: Number(item.thu_tu_hien_thi) || 0,
  }
}

function openCreate() {
  resetForm()
  // Đang lọc theo một nhóm nghề thì chọn sẵn nhóm nghề đó.
  form.thpt_xkld_nhom_nghe_id = filters.thpt_xkld_nhom_nghe_id || null
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
    items = docMangJson(jsonText.value, 'thị trường').map((item, index) => {
      const payload = chuanHoa({ ...item, ...lienKetTuJson(item, index + 1) })
      if (!payload.ma_quoc_gia || !payload.ten_quoc_gia) {
        throw new Error(`Phần tử thứ ${index + 1} thiếu ma_quoc_gia hoặc ten_quoc_gia`)
      }
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: thiTruongApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await thiTruongApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật thị trường')
    } else {
      await thiTruongApi.create(payload)
      ElMessage.success('Đã thêm thị trường')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được thị trường'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
