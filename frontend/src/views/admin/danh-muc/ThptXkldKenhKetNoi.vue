<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tên kênh, liên hệ, nhóm nghề, thị trường"
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
          @change="onDoiNhomLoc"
        >
          <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.thpt_xkld_thi_truong_id"
          placeholder="Chọn thị trường"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in thiTruongCuaNhom(filters.thpt_xkld_nhom_nghe_id)"
            :key="item.id"
            :label="nhanThiTruong(item, !filters.thpt_xkld_nhom_nghe_id)"
            :value="item.id"
          />
        </CustomSelect>
        <CustomSelect v-model="filters.loai_kenh" placeholder="Chọn loại kênh" clearable @change="onSearch">
          <CustomOption v-for="item in LOAI_KENH" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách kênh kết nối xuất khẩu lao động</h2>
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
            Thêm kênh
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
        <CustomTableColumn prop="ten_kenh" label="Tên kênh" min-width="220" />
        <CustomTableColumn label="Loại kênh" width="170" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauEnum(LOAI_KENH, row.loai_kenh)" effect="light">
              {{ nhanEnum(LOAI_KENH, row.loai_kenh) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_nhom" label="Nhóm nghề" min-width="170" />
        <CustomTableColumn label="Thị trường" width="130" align="center">
          <template #default="{ row }">
            <span v-if="row.ten_quoc_gia">{{ row.ten_quoc_gia }}</span>
            <CustomTag v-else type="info" effect="light">Chung</CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Thông tin liên hệ" min-width="200">
          <template #default="{ row }">{{ row.thong_tin_lien_he || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mô tả hỗ trợ" min-width="260">
          <template #default="{ row }">{{ row.mo_ta_ho_tro || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Lưu ý" min-width="220">
          <template #default="{ row }">{{ row.luu_y_tranh_rui_ro || '—' }}</template>
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_kenh)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có kênh kết nối nào." />
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
    :title="editingId ? 'Cập nhật kênh kết nối' : 'Thêm kênh kết nối'"
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
        placeholder="Dán mảng JSON vào đây (dùng ma_nhom, ma_quoc_gia hoặc id tương ứng)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Nhóm nghề" prop="thpt_xkld_nhom_nghe_id">
          <CustomSelect
            v-model="form.thpt_xkld_nhom_nghe_id"
            placeholder="Chọn nhóm nghề"
            filterable
            @change="boThiTruongSaiNhom(form)"
          >
            <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Thị trường" prop="thpt_xkld_thi_truong_id">
          <CustomSelect
            v-model="form.thpt_xkld_thi_truong_id"
            placeholder="Chọn thị trường (trống = chung)"
            clearable
            filterable
            :disabled="!form.thpt_xkld_nhom_nghe_id"
          >
            <CustomOption
              v-for="item in thiTruongCuaNhom(form.thpt_xkld_nhom_nghe_id)"
              :key="item.id"
              :label="nhanThiTruong(item)"
              :value="item.id"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Loại kênh" prop="loai_kenh">
          <CustomSelect v-model="form.loai_kenh" placeholder="Chọn loại kênh">
            <CustomOption v-for="item in LOAI_KENH" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên kênh" prop="ten_kenh">
          <CustomInput v-model="form.ten_kenh" maxlength="255" placeholder="Nhập tên kênh" />
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
        <CustomFormItem class="form-grid__span-2" label="Thông tin liên hệ" prop="thong_tin_lien_he">
          <CustomInput
            v-model="form.thong_tin_lien_he"
            maxlength="255"
            placeholder="Nhập thông tin liên hệ (website, email, điện thoại)"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Lưu ý tránh rủi ro" prop="luu_y_tranh_rui_ro">
          <CustomInput v-model="form.luu_y_tranh_rui_ro" maxlength="255" placeholder="Nhập lưu ý tránh rủi ro" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mô tả hỗ trợ" prop="mo_ta_ho_tro">
          <CustomInput
            v-model="form.mo_ta_ho_tro"
            type="textarea"
            :rows="3"
            maxlength="5000"
            placeholder="Nhập mô tả hỗ trợ"
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
import { kenhKetNoiApi } from '@/api/thptXkld'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangXkld, useLienKetXkld } from '@/composables/useThptXkld'
import { LOAI_KENH, mauEnum, nhanEnum } from '@/constants/thptXkld'

const JSON_SAMPLE = `[
  {
    "ma_nhom": "CO_KHI",
    "ma_quoc_gia": "JP",
    "loai_kenh": "co_quan_nha_nuoc",
    "ten_kenh": "Cục Quản lý lao động ngoài nước",
    "thong_tin_lien_he": "dolab.gov.vn",
    "mo_ta_ho_tro": "Tra cứu danh sách doanh nghiệp được cấp phép, tiếp nhận phản ánh.",
    "luu_y_tranh_rui_ro": "Kiểm tra giấy phép doanh nghiệp trước khi nộp tiền",
    "thu_tu_hien_thi": 1
  }
]`

const filters = reactive({ q: '', thpt_xkld_nhom_nghe_id: '', thpt_xkld_thi_truong_id: '', loai_kenh: '' })

const { nhomOptions, loadOptions, thiTruongCuaNhom, nhanNhom, nhanThiTruong, boThiTruongSaiNhom, lienKetTuJson } =
  useLienKetXkld()
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
  api: kenhKetNoiApi,
  nhan: 'kênh kết nối',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thpt_xkld_nhom_nghe_id) params.thpt_xkld_nhom_nghe_id = filters.thpt_xkld_nhom_nghe_id
    if (filters.thpt_xkld_thi_truong_id) params.thpt_xkld_thi_truong_id = filters.thpt_xkld_thi_truong_id
    if (filters.loai_kenh) params.loai_kenh = filters.loai_kenh
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'kênh kết nối' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  thpt_xkld_nhom_nghe_id: [{ required: true, message: 'Vui lòng chọn nhóm nghề', trigger: 'change' }],
  loai_kenh: [{ required: true, message: 'Vui lòng chọn loại kênh', trigger: 'change' }],
  ten_kenh: [{ required: true, message: 'Vui lòng nhập tên kênh', trigger: 'blur' }],
}

function emptyForm() {
  return {
    thpt_xkld_nhom_nghe_id: null,
    thpt_xkld_thi_truong_id: null,
    loai_kenh: '',
    ten_kenh: '',
    thong_tin_lien_he: '',
    mo_ta_ho_tro: '',
    luu_y_tranh_rui_ro: '',
    thu_tu_hien_thi: 0,
  }
}

function onDoiNhomLoc() {
  boThiTruongSaiNhom(filters)
  onSearch()
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
    thpt_xkld_thi_truong_id: item.thpt_xkld_thi_truong_id || null,
    loai_kenh: item.loai_kenh,
    ten_kenh: String(item.ten_kenh ?? '').trim(),
    thong_tin_lien_he: giaTriTuyChon(item.thong_tin_lien_he),
    mo_ta_ho_tro: giaTriTuyChon(item.mo_ta_ho_tro),
    luu_y_tranh_rui_ro: giaTriTuyChon(item.luu_y_tranh_rui_ro),
    thu_tu_hien_thi: Number(item.thu_tu_hien_thi) || 0,
  }
}

function openCreate() {
  resetForm()
  // Đang lọc thì chọn sẵn nhóm nghề, thị trường, loại kênh đó.
  form.thpt_xkld_nhom_nghe_id = filters.thpt_xkld_nhom_nghe_id || null
  form.thpt_xkld_thi_truong_id = filters.thpt_xkld_thi_truong_id || null
  form.loai_kenh = filters.loai_kenh || ''
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
    items = docMangJson(jsonText.value, 'kênh kết nối').map((item, index) => {
      const payload = chuanHoa({ ...item, ...lienKetTuJson(item, index + 1) })
      if (!payload.ten_kenh || !payload.loai_kenh) {
        throw new Error(`Phần tử thứ ${index + 1} thiếu ten_kenh hoặc loai_kenh`)
      }
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: kenhKetNoiApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await kenhKetNoiApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật kênh kết nối')
    } else {
      await kenhKetNoiApi.create(payload)
      ElMessage.success('Đã thêm kênh kết nối')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được kênh kết nối'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
