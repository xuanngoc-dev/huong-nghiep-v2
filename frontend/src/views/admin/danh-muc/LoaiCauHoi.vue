<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm tên loại câu hỏi"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.doi_tuong_ap_dung"
          class="filter-parent"
          placeholder="Chọn đối tượng áp dụng"
          clearable
          @change="onSearch"
        >
          <CustomOption v-for="item in DOI_TUONG_AP_DUNG" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.trang_thai"
          class="filter-status"
          placeholder="Trạng thái"
          clearable
          @change="onSearch"
        >
          <CustomOption label="Hoạt động" :value="1" />
          <CustomOption label="Ngừng sử dụng" :value="0" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách loại câu hỏi</h2>
        <div class="toolbar__actions">
          <!-- Bật chỉ áp dụng cho dòng đã chọn đang tắt, Tắt cho dòng đang bật; badge là số dòng sẽ đổi. -->
          <CustomBadge :value="idsDangTat.length" :hidden="!idsDangTat.length" type="success">
            <CustomButton
              type="success"
              plain
              :disabled="!idsDangTat.length"
              :loading="dangDoiNhieu === 1"
              @click="doiTrangThaiDaChon(1)"
            >
              <CustomIcon><CircleCheck /></CustomIcon>
              Bật
            </CustomButton>
          </CustomBadge>
          <CustomBadge :value="idsDangBat.length" :hidden="!idsDangBat.length" type="warning">
            <CustomButton
              type="warning"
              plain
              :disabled="!idsDangBat.length"
              :loading="dangDoiNhieu === 0"
              @click="doiTrangThaiDaChon(0)"
            >
              <CustomIcon><CircleClose /></CustomIcon>
              Tắt
            </CustomButton>
          </CustomBadge>
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
            Thêm loại câu hỏi
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
        <CustomTableColumn prop="id" label="ID" width="100" align="center" />
        <CustomTableColumn prop="thu_tu_uu_tien" label="Thứ tự hiển thị" width="180" align="center" />
        <CustomTableColumn prop="ten_loai_cau_hoi" label="Tên loại câu hỏi" min-width="220" />
        <CustomTableColumn label="Loại trả lời" width="130" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.loai_tra_loi === 'tinh_huong' ? 'warning' : 'primary'" effect="light">
              {{ nhanLoaiTraLoi(row.loai_tra_loi) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Đối tượng áp dụng" min-width="200">
          <template #default="{ row }">
            <span v-if="row.doi_tuong_ap_dung?.length" class="tieu-de-list">
              <CustomTooltip
                v-for="ma in row.doi_tuong_ap_dung"
                :key="ma"
                :content="timDoiTuongApDung(ma)?.label || `Mã ${ma}`"
                placement="top"
              >
                <CustomTag type="success" effect="light" size="small">
                  {{ timDoiTuongApDung(ma)?.nhanNgan || `Mã ${ma}` }}
                </CustomTag>
              </CustomTooltip>
            </span>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Tiêu đề câu trả lời" min-width="240">
          <template #default="{ row }">
            <span v-if="row.danh_sach_tieu_de_cau_tra_loi?.length" class="tieu-de-list">
              <CustomTag
                v-for="(item, index) in row.danh_sach_tieu_de_cau_tra_loi"
                :key="index"
                type="info"
                effect="plain"
                size="small"
              >
                {{ nhanTieuDe(item) }}
              </CustomTag>
            </span>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Trạng thái" width="150" align="center">
          <template #default="{ row }">
            <CustomSwitch
              :model-value="row.trang_thai"
              :active-value="1"
              :inactive-value="0"
              active-text="Hoạt động"
              inactive-text="Ngừng"
              :loading="!!dangDoiTrangThai[row.id]"
              :before-change="() => doiTrangThai(row)"
              :aria-label="`Trạng thái ${row.ten_loai_cau_hoi}`"
            />
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="220" >
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
          <CustomEmpty description="Chưa có loại câu hỏi nào." />
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
    :title="editingId ? 'Cập nhật loại câu hỏi' : 'Thêm loại câu hỏi'"
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
        placeholder="Dán mảng JSON vào đây"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Tên loại câu hỏi" prop="ten_loai_cau_hoi">
          <CustomInput
            v-model="form.ten_loai_cau_hoi"
            maxlength="150"
            placeholder="Ví dụ: Trắc nghiệm một đáp án"
          />
        </CustomFormItem>
        <CustomFormItem label="Thứ tự ưu tiên" prop="thu_tu_uu_tien">
          <CustomInputNumber
            v-model="form.thu_tu_uu_tien"
            placeholder="Nhập thứ tự ưu tiên"
            :min="1"
            :max="9999"
            :step="1"
            :precision="0"
            controls-position="right"
          />
          <!-- <p class="field-hint">Được trùng; cùng thứ tự thì loại tạo trước đứng trước.</p> -->
        </CustomFormItem>
        <CustomFormItem label="Trạng thái" prop="trang_thai">
          <CustomSelect v-model="form.trang_thai" placeholder="Chọn trạng thái" :clearable="false">
            <CustomOption label="Hoạt động" :value="1" />
            <CustomOption label="Ngừng sử dụng" :value="0" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Loại trả lời" prop="loai_tra_loi">
          <CustomSelect v-model="form.loai_tra_loi" placeholder="Chọn loại trả lời" :clearable="false">
            <CustomOption v-for="item in LOAI_TRA_LOI" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Đối tượng áp dụng" prop="doi_tuong_ap_dung">
          <CustomSelect
            v-model="form.doi_tuong_ap_dung"
            multiple
            clearable
            placeholder="Chọn đối tượng áp dụng (chọn được nhiều)"
          >
            <CustomOption v-for="item in DOI_TUONG_AP_DUNG" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Danh sách tiêu đề câu trả lời">
          <CustomTable :data="form.tieu_de_cau_tra_loi" border size="small" class="tieu-de-table">
            <CustomTableColumn label="STT" width="60" align="center">
              <template #default="{ $index }">{{ $index + 1 }}</template>
            </CustomTableColumn>
            <CustomTableColumn label="Tiêu đề" min-width="220">
              <template #default="{ row }">
                <CustomInput v-model="row.tieu_de" maxlength="255" placeholder="Nhập tiêu đề" />
              </template>
            </CustomTableColumn>
            <CustomTableColumn label="Số điểm" width="150">
              <template #default="{ row }">
                <CustomInputNumber
                  v-model="row.diem"
                  :min="-1000"
                  :max="1000"
                  :step="1"
                  :precision="0"
                  controls-position="right"
                  placeholder="Nhập số điểm"
                />
              </template>
            </CustomTableColumn>
            <CustomTableColumn label="Thao tác" width="100" align="center">
              <template #default="{ $index }">
                <div class="row-actions">
                  <CustomTooltip content="Xóa" placement="top">
                    <CustomButton link type="danger" aria-label="Xóa" @click="xoaTieuDe($index)">
                      <CustomIcon><Delete /></CustomIcon>
                    </CustomButton>
                  </CustomTooltip>
                  <CustomTooltip v-if="$index === form.tieu_de_cau_tra_loi.length - 1" content="Thêm" placement="top">
                    <CustomButton link type="primary" aria-label="Thêm" @click="themTieuDe">
                      <CustomIcon><Plus /></CustomIcon>
                    </CustomButton>
                  </CustomTooltip>
                </div>
              </template>
            </CustomTableColumn>
            <template #empty>
              <CustomButton link type="primary" @click="themTieuDe">
                <CustomIcon><Plus /></CustomIcon>
                Thêm tiêu đề câu trả lời
              </CustomButton>
            </template>
          </CustomTable>
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput
            v-model="form.ghi_chu"
            type="textarea"
            :rows="3"
            maxlength="2000"
            show-word-limit
            placeholder="Ghi chú thêm (nếu có)"
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
  <XacNhanXoaDialog ref="xacNhanRef" />
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import XacNhanXoaDialog from '@/components/admin/XacNhanXoaDialog.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createLoaiCauHoi,
  createLoaiCauHoiBulk,
  deleteLoaiCauHoi,
  deleteLoaiCauHoiMany,
  fetchAnhHuongXoaLoaiCauHoi,
  fetchLoaiCauHoi,
  updateLoaiCauHoi,
  updateTrangThaiLoaiCauHoi,
  updateTrangThaiLoaiCauHoiMany,
} from '@/api/loaiCauHoi'
import { DOI_TUONG_AP_DUNG, timDoiTuongApDung } from '@/constants/doiTuongApDung'

const LOAI_TRA_LOI = [
  { value: 'diem_so', label: 'Điểm số' },
  { value: 'tinh_huong', label: 'Tình huống' },
]

function nhanLoaiTraLoi(value) {
  return LOAI_TRA_LOI.find((item) => item.value === value)?.label || value || '—'
}

// Dữ liệu cũ có thể là chuỗi; dòng không có tiêu đề thì bỏ, không còn dòng nào thì gửi null.
function docTieuDe(ds) {
  return (ds || []).map((item) =>
    typeof item === 'string' ? { tieu_de: item, diem: null } : { tieu_de: item.tieu_de || '', diem: item.diem ?? null },
  )
}

function guiTieuDe(ds) {
  const conLai = ds
    .map((item) => ({ tieu_de: item.tieu_de.trim(), diem: item.diem ?? null }))
    .filter((item) => item.tieu_de)
  return conLai.length ? conLai : null
}

function nhanTieuDe(item) {
  if (typeof item === 'string') return item
  return item.diem == null ? item.tieu_de : `${item.tieu_de} (${item.diem})`
}

function themTieuDe() {
  const ds = form.tieu_de_cau_tra_loi
  // Điểm gợi ý: dòng trước + 1 (thang mức độ), dòng đầu là 1.
  const diemTruoc = ds.length ? ds[ds.length - 1].diem : 0
  ds.push({ tieu_de: '', diem: diemTruoc == null ? null : diemTruoc + 1 })
}

function xoaTieuDe(index) {
  form.tieu_de_cau_tra_loi.splice(index, 1)
}

const JSON_SAMPLE = `[
  {
    "ten_loai_cau_hoi": "Trắc nghiệm một đáp án",
    "thu_tu_uu_tien": 1,
    "trang_thai": 1,
    "loai_tra_loi": "diem_so",
    "doi_tuong_ap_dung": [1, 2],
    "danh_sach_tieu_de_cau_tra_loi": [
      { "tieu_de": "Rất không thích", "diem": 1 },
      { "tieu_de": "Không thích", "diem": 2 },
      { "tieu_de": "Bình thường", "diem": 3 },
      { "tieu_de": "Thích", "diem": 4 },
      { "tieu_de": "Rất thích", "diem": 5 }
    ]
  },
  {
    "ten_loai_cau_hoi": "Trắc nghiệm nhiều đáp án",
    "thu_tu_uu_tien": 2,
    "loai_tra_loi": "tinh_huong",
    "doi_tuong_ap_dung": [1],
    "ghi_chu": "Chọn một hoặc nhiều phương án"
  }
]`

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const rows = ref([])
const selectedRows = ref([])
const idsDangBat = computed(() => selectedRows.value.filter((row) => row.trang_thai === 1).map((row) => row.id))
const idsDangTat = computed(() => selectedRows.value.filter((row) => row.trang_thai !== 1).map((row) => row.id))
// Trạng thái đang áp dụng cho các dòng đã chọn (1 bật / 0 tắt), null khi không chạy.
const dangDoiNhieu = ref(null)
const tableRef = ref()
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'loại câu hỏi' })
const formRef = ref()
const dangDoiTrangThai = ref({})

const filters = reactive({
  q: '',
  doi_tuong_ap_dung: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

const rules = {
  ten_loai_cau_hoi: [{ required: true, message: 'Vui lòng nhập tên loại câu hỏi', trigger: 'blur' }],
  thu_tu_uu_tien: [{ required: true, message: 'Vui lòng nhập thứ tự ưu tiên', trigger: 'change' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
  loai_tra_loi: [{ required: true, message: 'Vui lòng chọn loại trả lời', trigger: 'change' }],
  doi_tuong_ap_dung: [
    { type: 'array', required: true, min: 1, message: 'Vui lòng chọn ít nhất một đối tượng áp dụng', trigger: 'change' },
  ],
}

function emptyForm() {
  return {
    ten_loai_cau_hoi: '',
    ghi_chu: '',
    thu_tu_uu_tien: 1,
    trang_thai: 1,
    loai_tra_loi: 'diem_so',
    doi_tuong_ap_dung: [],
    tieu_de_cau_tra_loi: [],
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

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng loại câu hỏi.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_loai_cau_hoi": "...", "thu_tu_uu_tien": 1 }]')
  }
  if (!data.length) {
    throw new Error('Mảng loại câu hỏi đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một loại câu hỏi`)
    }
    const ten = String(item.ten_loai_cau_hoi ?? '').trim()
    const order = Number(item.thu_tu_uu_tien)
    if (!ten || !Number.isInteger(order) || order < 1) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_loai_cau_hoi hoặc thu_tu_uu_tien`)
    }
    return {
      ten_loai_cau_hoi: ten,
      thu_tu_uu_tien: order,
      trang_thai: item.trang_thai ?? 1,
      ghi_chu: item.ghi_chu == null ? null : String(item.ghi_chu).trim() || null,
      loai_tra_loi: item.loai_tra_loi ?? 'diem_so',
      danh_sach_tieu_de_cau_tra_loi: Array.isArray(item.danh_sach_tieu_de_cau_tra_loi)
        ? item.danh_sach_tieu_de_cau_tra_loi
        : null,
      doi_tuong_ap_dung: docDoiTuongJson(item.doi_tuong_ap_dung, line),
    }
  })
}

// JSON nhập vào: mảng mã số trong DOI_TUONG_AP_DUNG; không có thì null.
function docDoiTuongJson(value, line) {
  if (value == null) return null
  if (!Array.isArray(value)) throw new Error(`Phần tử thứ ${line}: doi_tuong_ap_dung phải là mảng, ví dụ [1, 2]`)
  const sai = value.filter((ma) => !timDoiTuongApDung(ma))
  if (sai.length) throw new Error(`Phần tử thứ ${line}: đối tượng áp dụng không hợp lệ: ${sai.join(', ')}`)
  return value.length ? value : null
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    if (filters.doi_tuong_ap_dung) params.doi_tuong_ap_dung = filters.doi_tuong_ap_dung
    const data = await fetchLoaiCauHoi(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách loại câu hỏi'))
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
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    ten_loai_cau_hoi: row.ten_loai_cau_hoi,
    ghi_chu: row.ghi_chu || '',
    thu_tu_uu_tien: row.thu_tu_uu_tien,
    trang_thai: row.trang_thai,
    loai_tra_loi: row.loai_tra_loi || 'diem_so',
    doi_tuong_ap_dung: [...(row.doi_tuong_ap_dung || [])],
    tieu_de_cau_tra_loi: docTieuDe(row.danh_sach_tieu_de_cau_tra_loi),
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ten_loai_cau_hoi: form.ten_loai_cau_hoi.trim(),
    thu_tu_uu_tien: form.thu_tu_uu_tien,
    trang_thai: form.trang_thai,
    ghi_chu: form.ghi_chu?.trim() || null,
    loai_tra_loi: form.loai_tra_loi,
    danh_sach_tieu_de_cau_tra_loi: guiTieuDe(form.tieu_de_cau_tra_loi),
    doi_tuong_ap_dung: [...form.doi_tuong_ap_dung],
  }
}

async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    const data = await updateTrangThaiLoaiCauHoi(row.id, moi)
    row.trang_thai = data.trang_thai
    ElMessage.success(moi === 1 ? `Đã bật "${row.ten_loai_cau_hoi}"` : `Đã tắt "${row.ten_loai_cau_hoi}"`)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái'))
  } finally {
    const { [row.id]: _bo, ...conLai } = dangDoiTrangThai.value
    dangDoiTrangThai.value = conLai
  }
  return false
}

async function doiTrangThaiDaChon(trangThai) {
  const ids = trangThai === 1 ? idsDangTat.value : idsDangBat.value
  if (!ids.length) return
  const hanhDong = trangThai === 1 ? 'Bật' : 'Tắt'
  try {
    await ElMessageBox.confirm(
      `${hanhDong} ${ids.length} loại câu hỏi đã chọn đang ${trangThai === 1 ? 'tắt' : 'bật'}?`,
      `Xác nhận ${hanhDong.toLowerCase()} loại câu hỏi`,
      {
        type: 'warning',
        confirmButtonText: hanhDong,
        cancelButtonText: 'Hủy',
        confirmButtonClass: trangThai === 1 ? 'el-button--success' : 'el-button--warning',
      },
    )
  } catch {
    return
  }
  dangDoiNhieu.value = trangThai
  try {
    const result = await updateTrangThaiLoaiCauHoiMany(ids, trangThai)
    ElMessage.success(`Đã ${trangThai === 1 ? 'bật' : 'tắt'} ${result.updated} loại câu hỏi`)
    clearSelection()
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái các loại câu hỏi đã chọn'))
  } finally {
    dangDoiNhieu.value = null
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
    createBatch: createLoaiCauHoiBulk,
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
      await updateLoaiCauHoi(editingId.value, payload)
      ElMessage.success('Đã cập nhật loại câu hỏi')
    } else {
      await createLoaiCauHoi(payload)
      ElMessage.success('Đã thêm loại câu hỏi')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được loại câu hỏi'))
  } finally {
    saving.value = false
  }
}

const xacNhanRef = ref()

// Còn câu hỏi / phiên khảo sát liên quan thì liệt kê số lượng sẽ bị xóa kèm.
function xacNhanXoa(ids, tieuDe) {
  return xacNhanRef.value.mo({
    tieuDe,
    taiAnhHuong: () => fetchAnhHuongXoaLoaiCauHoi(ids),
    dongLienQuan: (a) =>
      a.so_cau_hoi || a.so_phien
        ? [
            { du_lieu: 'Câu hỏi trắc nghiệm', so_luong: a.so_cau_hoi, ghi_chu: 'Các câu hỏi thuộc loại này' },
            { du_lieu: 'Đáp án', so_luong: a.so_dap_an, ghi_chu: 'Đáp án của các câu hỏi trên' },
            {
              du_lieu: 'Phiên khảo sát đã thực hiện',
              so_luong: a.so_phien,
              ghi_chu: 'Phiên có câu hỏi thuộc loại này; xóa cả phiên',
            },
          ]
        : [],
  })
}

async function onDelete(row) {
  const xacNhan = await xacNhanXoa([row.id], `Xóa loại câu hỏi "${row.ten_loai_cau_hoi}"`)
  if (!xacNhan) return

  try {
    await deleteLoaiCauHoi(row.id, xacNhan.xoaLienQuan)
    ElMessage.success('Đã xóa loại câu hỏi')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được loại câu hỏi'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  const xacNhan = await xacNhanXoa(ids, `Xóa ${ids.length} loại câu hỏi đã chọn`)
  if (!xacNhan) return

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteLoaiCauHoiMany(ids, xacNhan.xoaLienQuan)
    ElMessage.success(`Đã xóa ${result.deleted} loại câu hỏi`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các loại câu hỏi đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.tieu-de-table {
  width: 100%;
}

.tieu-de-list {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
