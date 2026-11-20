<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên quốc gia, tên hướng đi"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.thpt_duhoc_huong_di_id"
          placeholder="Chọn hướng đi"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption v-for="item in huongOptions" :key="item.id" :label="nhanHuong(item)" :value="item.id" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách quốc gia du học</h2>
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
            Thêm quốc gia
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
        <CustomTableColumn label="Quốc gia" min-width="160">
          <template #default="{ row }">{{ row.ten_quoc_gia }} ({{ row.ma_quoc_gia }})</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_huong" label="Hướng đi" min-width="180" />
        <CustomTableColumn label="Đặc điểm nổi bật" min-width="280">
          <template #default="{ row }">{{ row.dac_diem_noi_bat || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Yêu cầu ngoại ngữ riêng" min-width="220">
          <template #default="{ row }">{{ row.yeu_cau_ngoai_ngu_rieng || '—' }}</template>
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
          <CustomEmpty description="Chưa có quốc gia nào." />
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
    :title="editingId ? 'Cập nhật quốc gia du học' : 'Thêm quốc gia du học'"
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
        placeholder="Dán mảng JSON vào đây (dùng ma_huong hoặc thpt_duhoc_huong_di_id)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Hướng đi" prop="thpt_duhoc_huong_di_id">
          <CustomSelect v-model="form.thpt_duhoc_huong_di_id" placeholder="Chọn hướng đi" filterable>
            <CustomOption v-for="item in huongOptions" :key="item.id" :label="nhanHuong(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Mã quốc gia" prop="ma_quoc_gia">
          <CustomInput v-model="form.ma_quoc_gia" maxlength="20" placeholder="Nhập mã quốc gia (ví dụ: DE)" />
        </CustomFormItem>
        <CustomFormItem label="Tên quốc gia" prop="ten_quoc_gia">
          <CustomInput v-model="form.ten_quoc_gia" maxlength="100" placeholder="Nhập tên quốc gia" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Yêu cầu ngoại ngữ riêng" prop="yeu_cau_ngoai_ngu_rieng">
          <CustomInput
            v-model="form.yeu_cau_ngoai_ngu_rieng"
            maxlength="255"
            placeholder="Nhập yêu cầu ngoại ngữ riêng"
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
        <CustomFormItem class="form-grid__full" label="Đặc điểm nổi bật" prop="dac_diem_noi_bat">
          <CustomInput
            v-model="form.dac_diem_noi_bat"
            type="textarea"
            :rows="3"
            maxlength="5000"
            placeholder="Nhập đặc điểm nổi bật"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Cơ hội việc làm, visa" prop="co_hoi_viec_lam_visa">
          <CustomInput
            v-model="form.co_hoi_viec_lam_visa"
            type="textarea"
            :rows="3"
            maxlength="5000"
            placeholder="Nhập cơ hội việc làm, visa"
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
import { quocGiaApi } from '@/api/thptDuHoc'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangDuHoc, useLienKetDuHoc } from '@/composables/useThptDuHoc'

const JSON_SAMPLE = `[
  {
    "ma_huong": "DU_HOC_NGHE",
    "ma_quoc_gia": "DE",
    "ten_quoc_gia": "Đức",
    "dac_diem_noi_bat": "Ausbildung: học nghề kép, được trả lương.",
    "yeu_cau_ngoai_ngu_rieng": "Tiếng Đức B1",
    "thu_tu_hien_thi": 1
  }
]`

const filters = reactive({ q: '', thpt_duhoc_huong_di_id: '' })

const { huongOptions, loadOptions, nhanHuong, lienKetTuJson } = useLienKetDuHoc({ coQuocGia: false })
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
} = useBangDuHoc({
  api: quocGiaApi,
  nhan: 'quốc gia',
  canhBaoXoa: 'Ngành, chi phí, thủ tục và kênh kết nối riêng của quốc gia cũng bị xóa theo.',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thpt_duhoc_huong_di_id) params.thpt_duhoc_huong_di_id = filters.thpt_duhoc_huong_di_id
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'quốc gia' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  thpt_duhoc_huong_di_id: [{ required: true, message: 'Vui lòng chọn hướng đi', trigger: 'change' }],
  ma_quoc_gia: [{ required: true, message: 'Vui lòng nhập mã quốc gia', trigger: 'blur' }],
  ten_quoc_gia: [{ required: true, message: 'Vui lòng nhập tên quốc gia', trigger: 'blur' }],
}

function emptyForm() {
  return {
    thpt_duhoc_huong_di_id: null,
    ma_quoc_gia: '',
    ten_quoc_gia: '',
    dac_diem_noi_bat: '',
    yeu_cau_ngoai_ngu_rieng: '',
    co_hoi_viec_lam_visa: '',
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
    thpt_duhoc_huong_di_id: item.thpt_duhoc_huong_di_id,
    ma_quoc_gia: String(item.ma_quoc_gia ?? '').trim().toUpperCase(),
    ten_quoc_gia: String(item.ten_quoc_gia ?? '').trim(),
    dac_diem_noi_bat: giaTriTuyChon(item.dac_diem_noi_bat),
    yeu_cau_ngoai_ngu_rieng: giaTriTuyChon(item.yeu_cau_ngoai_ngu_rieng),
    co_hoi_viec_lam_visa: giaTriTuyChon(item.co_hoi_viec_lam_visa),
    thu_tu_hien_thi: Number(item.thu_tu_hien_thi) || 0,
  }
}

function openCreate() {
  resetForm()
  // Đang lọc theo một hướng đi thì chọn sẵn hướng đi đó.
  form.thpt_duhoc_huong_di_id = filters.thpt_duhoc_huong_di_id || null
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
    items = docMangJson(jsonText.value, 'quốc gia').map((item, index) => {
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
  await jsonImport.run({ items, createBatch: quocGiaApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await quocGiaApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật quốc gia')
    } else {
      await quocGiaApi.create(payload)
      ElMessage.success('Đã thêm quốc gia')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được quốc gia'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
