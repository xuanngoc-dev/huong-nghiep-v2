<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tên khoản chi, nhóm nghề, thị trường"
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
        <CustomSelect v-model="filters.loai_chi_phi" placeholder="Chọn loại chi phí" clearable @change="onSearch">
          <CustomOption v-for="item in LOAI_CHI_PHI" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách chi phí xuất khẩu lao động</h2>
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
            Thêm khoản chi
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
        <CustomTableColumn prop="ten_khoan_chi" label="Khoản chi" min-width="220" />
        <CustomTableColumn label="Loại chi phí" width="180" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauEnum(LOAI_CHI_PHI, row.loai_chi_phi)" effect="light">
              {{ nhanEnum(LOAI_CHI_PHI, row.loai_chi_phi) }}
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
        <CustomTableColumn label="Mức chi" min-width="200" align="right">
          <template #default="{ row }">{{ khoangChiPhi(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Quy đổi VNĐ" min-width="190">
          <template #default="{ row }">{{ row.chi_phi_quy_doi_vnd_text || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Ghi chú" min-width="200">
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_khoan_chi)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có khoản chi phí nào." />
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
    :title="editingId ? 'Cập nhật chi phí xuất khẩu lao động' : 'Thêm chi phí xuất khẩu lao động'"
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
        <CustomFormItem label="Loại chi phí" prop="loai_chi_phi">
          <CustomSelect v-model="form.loai_chi_phi" placeholder="Chọn loại chi phí">
            <CustomOption v-for="item in LOAI_CHI_PHI" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên khoản chi" prop="ten_khoan_chi">
          <CustomInput v-model="form.ten_khoan_chi" maxlength="255" placeholder="Nhập tên khoản chi" />
        </CustomFormItem>
        <CustomFormItem label="Chi phí tối thiểu" prop="chi_phi_min">
          <CustomInputNumber
            v-model="form.chi_phi_min"
            placeholder="Nhập chi phí tối thiểu"
            :min="0"
            :max="9999999999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Chi phí tối đa" prop="chi_phi_max">
          <CustomInputNumber
            v-model="form.chi_phi_max"
            placeholder="Nhập chi phí tối đa"
            :min="0"
            :max="9999999999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Đơn vị tiền" prop="don_vi_tien">
          <CustomSelect
            v-model="form.don_vi_tien"
            placeholder="Chọn đơn vị tiền"
            filterable
            allow-create
            default-first-option
            :clearable="false"
          >
            <CustomOption v-for="item in DON_VI_TIEN_XKLD" :key="item" :label="item" :value="item" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Quy đổi VNĐ (mô tả)" prop="chi_phi_quy_doi_vnd_text">
          <CustomInput
            v-model="form.chi_phi_quy_doi_vnd_text"
            maxlength="255"
            placeholder="Nhập mức quy đổi (ví dụ: 38 - 92 triệu VNĐ)"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput v-model="form.ghi_chu" maxlength="255" placeholder="Nhập ghi chú" />
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
import { chiPhiApi } from '@/api/thptXkld'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangXkld, useLienKetXkld } from '@/composables/useThptXkld'
import { DON_VI_TIEN_XKLD, LOAI_CHI_PHI, mauEnum, nhanEnum } from '@/constants/thptXkld'

const JSON_SAMPLE = `[
  {
    "ma_nhom": "CO_KHI",
    "ma_quoc_gia": "JP",
    "loai_chi_phi": "phi_dich_vu_xuat_canh",
    "ten_khoan_chi": "Phí dịch vụ đưa người lao động đi làm việc",
    "chi_phi_min": 1500,
    "chi_phi_max": 3600,
    "don_vi_tien": "USD",
    "chi_phi_quy_doi_vnd_text": "38 - 92 triệu VNĐ",
    "ghi_chu": "Theo hợp đồng 3 năm"
  }
]`

const filters = reactive({ q: '', thpt_xkld_nhom_nghe_id: '', thpt_xkld_thi_truong_id: '', loai_chi_phi: '' })

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
  api: chiPhiApi,
  nhan: 'khoản chi',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thpt_xkld_nhom_nghe_id) params.thpt_xkld_nhom_nghe_id = filters.thpt_xkld_nhom_nghe_id
    if (filters.thpt_xkld_thi_truong_id) params.thpt_xkld_thi_truong_id = filters.thpt_xkld_thi_truong_id
    if (filters.loai_chi_phi) params.loai_chi_phi = filters.loai_chi_phi
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'khoản chi' })
const formRef = ref()
const form = reactive(emptyForm())

function kiemTraKhoang(_rule, value, callback) {
  const min = form.chi_phi_min
  if (value != null && min != null && min > value) callback(new Error('Tối đa phải ≥ tối thiểu'))
  else callback()
}

const rules = {
  thpt_xkld_nhom_nghe_id: [{ required: true, message: 'Vui lòng chọn nhóm nghề', trigger: 'change' }],
  loai_chi_phi: [{ required: true, message: 'Vui lòng chọn loại chi phí', trigger: 'change' }],
  ten_khoan_chi: [{ required: true, message: 'Vui lòng nhập tên khoản chi', trigger: 'blur' }],
  don_vi_tien: [{ required: true, message: 'Vui lòng chọn đơn vị tiền', trigger: 'change' }],
  chi_phi_max: [{ validator: kiemTraKhoang, trigger: 'change' }],
}

function emptyForm() {
  return {
    thpt_xkld_nhom_nghe_id: null,
    thpt_xkld_thi_truong_id: null,
    loai_chi_phi: '',
    ten_khoan_chi: '',
    chi_phi_min: undefined,
    chi_phi_max: undefined,
    don_vi_tien: 'VND',
    chi_phi_quy_doi_vnd_text: '',
    ghi_chu: '',
  }
}

const dinhDangSo = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })

function khoangChiPhi(row) {
  const tu = row.chi_phi_min == null ? null : Number(row.chi_phi_min)
  const den = row.chi_phi_max == null ? null : Number(row.chi_phi_max)
  if (tu == null && den == null) return '—'
  const giaTri = tu == null || den == null || tu === den
    ? dinhDangSo.format(tu ?? den)
    : `${dinhDangSo.format(tu)} - ${dinhDangSo.format(den)}`
  return `${giaTri} ${row.don_vi_tien}`
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
    loai_chi_phi: item.loai_chi_phi,
    ten_khoan_chi: String(item.ten_khoan_chi ?? '').trim(),
    chi_phi_min: giaTriTuyChon(item.chi_phi_min),
    chi_phi_max: giaTriTuyChon(item.chi_phi_max),
    don_vi_tien: String(item.don_vi_tien || 'VND').trim().toUpperCase(),
    chi_phi_quy_doi_vnd_text: giaTriTuyChon(item.chi_phi_quy_doi_vnd_text),
    ghi_chu: giaTriTuyChon(item.ghi_chu),
  }
}

function openCreate() {
  resetForm()
  // Đang lọc thì chọn sẵn nhóm nghề, thị trường, loại chi phí đó.
  form.thpt_xkld_nhom_nghe_id = filters.thpt_xkld_nhom_nghe_id || null
  form.thpt_xkld_thi_truong_id = filters.thpt_xkld_thi_truong_id || null
  form.loai_chi_phi = filters.loai_chi_phi || ''
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  const values = emptyForm()
  for (const key of Object.keys(values)) {
    if (row[key] == null) continue
    // Decimal trả về dạng chuỗi, đổi sang số cho CustomInputNumber.
    values[key] = key.startsWith('chi_phi_m') ? Number(row[key]) : row[key]
  }
  Object.assign(form, values)
  dialogVisible.value = true
}

async function onSubmitJson() {
  let items
  try {
    items = docMangJson(jsonText.value, 'khoản chi').map((item, index) => {
      const payload = chuanHoa({ ...item, ...lienKetTuJson(item, index + 1) })
      if (!payload.ten_khoan_chi || !payload.loai_chi_phi) {
        throw new Error(`Phần tử thứ ${index + 1} thiếu ten_khoan_chi hoặc loai_chi_phi`)
      }
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: chiPhiApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await chiPhiApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật khoản chi')
    } else {
      await chiPhiApi.create(payload)
      ElMessage.success('Đã thêm khoản chi')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được khoản chi'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
