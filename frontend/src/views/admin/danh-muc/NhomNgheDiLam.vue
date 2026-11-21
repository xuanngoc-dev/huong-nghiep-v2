<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên, mã Holland"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.loai_hinh_dau_vao"
          class="filter-parent"
          placeholder="Chọn loại hình đầu vào"
          clearable
          @change="onSearch"
        >
          <CustomOption v-for="item in LOAI_HINH_DAU_VAO" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.nhom_muc_tieu"
          class="filter-parent"
          placeholder="Chọn nhóm mục tiêu"
          clearable
          @change="onSearch"
        >
          <CustomOption v-for="item in NHOM_MUC_TIEU" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.trang_thai"
          class="filter-status"
          placeholder="Chọn trạng thái"
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
        <h2 class="toolbar__title">Danh sách nhóm nghề đi làm</h2>
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
            Thêm nhóm nghề
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
        <CustomTableColumn prop="ma_nhom" label="Mã nhóm" width="190" />
        <CustomTableColumn prop="ten_nhom" label="Tên nhóm" min-width="240" />
        <CustomTableColumn label="Loại hình đầu vào" width="170" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.loai_hinh_dau_vao" type="primary" effect="light">
              {{ nhan(LOAI_HINH_DAU_VAO, row.loai_hinh_dau_vao) }}
            </CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Thời gian đào tạo" min-width="180">
          <template #default="{ row }">{{ row.thoi_gian_dao_tao_text || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mức lương" min-width="180">
          <template #default="{ row }">{{ row.muc_luong_text || khoangLuong(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Nhóm mục tiêu" width="160" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.nhom_muc_tieu" :type="mauMucTieu(row.nhom_muc_tieu)" effect="light">
              {{ nhan(NHOM_MUC_TIEU, row.nhom_muc_tieu) }}
            </CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Holland" width="100" align="center">
          <template #default="{ row }">{{ row.ma_holland || '—' }}</template>
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
              :aria-label="`Trạng thái ${row.ten_nhom}`"
            />
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
          <CustomEmpty description="Chưa có nhóm nghề nào." />
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
    :title="editingId ? 'Cập nhật nhóm nghề đi làm' : 'Thêm nhóm nghề đi làm'"
    width="90%"
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
        <CustomFormItem label="Mã nhóm" prop="ma_nhom">
          <CustomInput v-model="form.ma_nhom" maxlength="50" placeholder="Nhập mã nhóm (ví dụ: LAM_DEP)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên nhóm" prop="ten_nhom">
          <CustomInput v-model="form.ten_nhom" maxlength="255" placeholder="Nhập tên nhóm" />
        </CustomFormItem>
        <CustomFormItem label="Loại hình đầu vào" prop="loai_hinh_dau_vao">
          <CustomSelect v-model="form.loai_hinh_dau_vao" placeholder="Chọn loại hình đầu vào" clearable>
            <CustomOption
              v-for="item in LOAI_HINH_DAU_VAO"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Nhóm mục tiêu" prop="nhom_muc_tieu">
          <CustomSelect v-model="form.nhom_muc_tieu" placeholder="Chọn nhóm mục tiêu" clearable>
            <CustomOption v-for="item in NHOM_MUC_TIEU" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Mã Holland" prop="ma_holland">
          <CustomInput v-model="form.ma_holland" maxlength="20" placeholder="Nhập mã Holland (ví dụ: RC)" />
        </CustomFormItem>

        <CustomFormItem class="form-grid__span-2" label="Thời gian đào tạo (mô tả)" prop="thoi_gian_dao_tao_text">
          <CustomInput
            v-model="form.thoi_gian_dao_tao_text"
            maxlength="100"
            placeholder="Nhập thời gian đào tạo (ví dụ: 3 - 6 tháng)"
          />
        </CustomFormItem>
        <CustomFormItem label="Đào tạo tối thiểu (tháng)" prop="thoi_gian_dao_tao_thang_min">
          <CustomInputNumber
            v-model="form.thoi_gian_dao_tao_thang_min"
            placeholder="Nhập số tháng tối thiểu"
            :min="0"
            :max="120"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Đào tạo tối đa (tháng)" prop="thoi_gian_dao_tao_thang_max">
          <CustomInputNumber
            v-model="form.thoi_gian_dao_tao_thang_max"
            placeholder="Nhập số tháng tối đa"
            :min="0"
            :max="120"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Trạng thái" prop="trang_thai">
          <CustomSelect v-model="form.trang_thai" placeholder="Chọn trạng thái" :clearable="false">
            <CustomOption label="Hoạt động" :value="1" />
            <CustomOption label="Ngừng sử dụng" :value="0" />
          </CustomSelect>
        </CustomFormItem>

        <CustomFormItem class="form-grid__span-2" label="Mức lương (mô tả)" prop="muc_luong_text">
          <CustomInput v-model="form.muc_luong_text" maxlength="100" placeholder="Nhập mức lương (ví dụ: 7 - 9 triệu/tháng)" />
        </CustomFormItem>
        <CustomFormItem label="Lương khởi điểm từ (triệu)" prop="luong_khoi_diem_min">
          <CustomInputNumber
            v-model="form.luong_khoi_diem_min"
            placeholder="Nhập lương khởi điểm từ"
            :min="0"
            :max="999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Lương khởi điểm đến (triệu)" prop="luong_khoi_diem_max">
          <CustomInputNumber
            v-model="form.luong_khoi_diem_max"
            placeholder="Nhập lương khởi điểm đến"
            :min="0"
            :max="999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Lương tối đa khi có kinh nghiệm (triệu)" prop="luong_kinh_nghiem_max">
          <CustomInputNumber
            v-model="form.luong_kinh_nghiem_max"
            placeholder="Nhập lương tối đa"
            :min="0"
            :max="999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Đánh giá triển vọng" prop="danh_gia_trien_vong">
          <CustomInput v-model="form.danh_gia_trien_vong" maxlength="255" placeholder="Nhập đánh giá triển vọng" />
        </CustomFormItem>

        <CustomFormItem class="form-grid__full" label="Mô tả đặc điểm" prop="mo_ta_dac_diem">
          <CustomInput
            v-model="form.mo_ta_dac_diem"
            type="textarea"
            :rows="3"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập mô tả đặc điểm công việc"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Điều kiện đầu vào" prop="dieu_kien_dau_vao">
          <CustomInput
            v-model="form.dieu_kien_dau_vao"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập điều kiện đầu vào"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Lộ trình phát triển" prop="lo_trinh_phat_trien">
          <CustomInput
            v-model="form.lo_trinh_phat_trien"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập lộ trình phát triển"
          />
        </CustomFormItem>
        <!-- Các mục giới thiệu hiển thị ở trang chi tiết nhóm nghề của học sinh. -->
        <CustomFormItem
          v-for="muc in MUC_GIOI_THIEU"
          :key="muc.key"
          class="form-grid__full"
          :label="muc.label"
          :prop="muc.key"
        >
          <CustomInput v-model="form[muc.key]" type="textarea" :rows="3" maxlength="10000" :placeholder="muc.placeholder" />
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
  createNhomNgheDiLam,
  createNhomNgheDiLamBulk,
  deleteNhomNgheDiLam,
  deleteNhomNgheDiLamMany,
  fetchNhomNgheDiLam,
  updateNhomNgheDiLam,
  updateTrangThaiNhomNgheDiLam,
  updateTrangThaiNhomNgheDiLamMany,
} from '@/api/nhomNgheDiLam'

const LOAI_HINH_DAU_VAO = [
  { value: 'di_lam_ngay', label: 'Đi làm ngay' },
  { value: 'hoc_nghe_ngan_han', label: 'Học nghề ngắn hạn' },
  { value: 'tu_hoc_ky_nang', label: 'Tự học kỹ năng' },
]

const NHOM_MUC_TIEU = [
  { value: 'kiem_tien_ngay', label: 'Kiếm tiền ngay', mau: 'warning' },
  { value: 'nghe_vung_chac', label: 'Nghề vững chắc', mau: 'success' },
  { value: 'thu_nhap_dot_pha', label: 'Thu nhập đột phá', mau: 'danger' },
]

// Mục giới thiệu nhóm nghề (văn bản dài, tùy chọn).
const MUC_GIOI_THIEU = [
  { key: 'nganh_nay_la_gi', label: 'Ngành này là gì?', placeholder: 'Giới thiệu ngắn gọn nhóm nghề' },
  { key: 'noi_lam_viec_o_dau', label: 'Nơi làm việc ở đâu?', placeholder: 'Nhà máy, cửa hàng, công trường…' },
  {
    key: 'cong_viec_hang_ngay_nhu_the_nao',
    label: 'Công việc hằng ngày như thế nào?',
    placeholder: 'Một ngày làm việc điển hình',
  },
  { key: 'ap_luc_va_rui_ro', label: 'Áp lực và rủi ro', placeholder: 'Khó khăn, rủi ro cần biết trước' },
  { key: 'xu_huong_tuong_lai', label: 'Xu hướng tương lai', placeholder: 'Nhu cầu, thay đổi của nghề trong vài năm tới' },
  { key: 'ket_luan', label: 'Kết luận', placeholder: 'Nghề này phù hợp với ai, nên chuẩn bị gì' },
]

// Các trường số/chọn: chuỗi rỗng hoặc undefined đều gửi null.
const TRUONG_TUY_CHON = [
  'loai_hinh_dau_vao',
  'thoi_gian_dao_tao_text',
  'thoi_gian_dao_tao_thang_min',
  'thoi_gian_dao_tao_thang_max',
  'dieu_kien_dau_vao',
  'muc_luong_text',
  'luong_khoi_diem_min',
  'luong_khoi_diem_max',
  'luong_kinh_nghiem_max',
  'danh_gia_trien_vong',
  'lo_trinh_phat_trien',
  'nhom_muc_tieu',
  'ma_holland',
  ...MUC_GIOI_THIEU.map((muc) => muc.key),
]

function nhan(ds, value) {
  return ds.find((item) => item.value === value)?.label || value || '—'
}

function mauMucTieu(value) {
  return NHOM_MUC_TIEU.find((item) => item.value === value)?.mau || 'info'
}

function khoangLuong(row) {
  const tu = row.luong_khoi_diem_min
  const den = row.luong_khoi_diem_max
  if (tu == null && den == null) return '—'
  if (tu != null && den != null) return `${Number(tu)} - ${Number(den)} triệu`
  return `${Number(tu ?? den)} triệu`
}

const JSON_SAMPLE = `[
  {
    "ma_nhom": "LAM_DEP",
    "ten_nhom": "Làm đẹp: tóc, nail, spa",
    "mo_ta_dac_diem": "Cắt tóc, làm móng, chăm sóc da tại salon, spa.",
    "loai_hinh_dau_vao": "hoc_nghe_ngan_han",
    "thoi_gian_dao_tao_text": "2 - 6 tháng",
    "thoi_gian_dao_tao_thang_min": 2,
    "thoi_gian_dao_tao_thang_max": 6,
    "muc_luong_text": "6 - 10 triệu/tháng",
    "luong_khoi_diem_min": 6,
    "luong_khoi_diem_max": 10,
    "luong_kinh_nghiem_max": 30,
    "nhom_muc_tieu": "nghe_vung_chac",
    "ma_holland": "AS",
    "nganh_nay_la_gi": "Cắt tóc, làm móng, chăm sóc da, trang điểm cho khách.",
    "ket_luan": "Hợp với người khéo tay, có gu thẩm mỹ; có thể mở tiệm với vốn nhỏ."
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
const jsonImport = useJsonBatchImport({ label: 'nhóm nghề' })
const formRef = ref()
const dangDoiTrangThai = ref({})

const filters = reactive({
  q: '',
  loai_hinh_dau_vao: '',
  nhom_muc_tieu: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

function kiemTraKhoang(minKey, nhanLoi) {
  return (_rule, value, callback) => {
    const min = form[minKey]
    if (value != null && min != null && min > value) callback(new Error(nhanLoi))
    else callback()
  }
}

const rules = {
  ma_nhom: [{ required: true, message: 'Vui lòng nhập mã nhóm', trigger: 'blur' }],
  ten_nhom: [{ required: true, message: 'Vui lòng nhập tên nhóm', trigger: 'blur' }],
  mo_ta_dac_diem: [{ required: true, message: 'Vui lòng nhập mô tả đặc điểm', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
  thoi_gian_dao_tao_thang_max: [
    { validator: kiemTraKhoang('thoi_gian_dao_tao_thang_min', 'Tối đa phải ≥ tối thiểu'), trigger: 'change' },
  ],
  luong_khoi_diem_max: [
    { validator: kiemTraKhoang('luong_khoi_diem_min', 'Lương đến phải ≥ lương từ'), trigger: 'change' },
  ],
}

function emptyForm() {
  return {
    ma_nhom: '',
    ten_nhom: '',
    mo_ta_dac_diem: '',
    loai_hinh_dau_vao: '',
    thoi_gian_dao_tao_text: '',
    thoi_gian_dao_tao_thang_min: undefined,
    thoi_gian_dao_tao_thang_max: undefined,
    dieu_kien_dau_vao: '',
    muc_luong_text: '',
    luong_khoi_diem_min: undefined,
    luong_khoi_diem_max: undefined,
    luong_kinh_nghiem_max: undefined,
    danh_gia_trien_vong: '',
    lo_trinh_phat_trien: '',
    nhom_muc_tieu: '',
    ma_holland: '',
    ...Object.fromEntries(MUC_GIOI_THIEU.map((muc) => [muc.key, ''])),
    trang_thai: 1,
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
  const payload = {
    ma_nhom: String(item.ma_nhom ?? '').trim().toUpperCase(),
    ten_nhom: String(item.ten_nhom ?? '').trim(),
    mo_ta_dac_diem: String(item.mo_ta_dac_diem ?? '').trim(),
    trang_thai: item.trang_thai ?? 1,
  }
  for (const key of TRUONG_TUY_CHON) {
    const value = typeof item[key] === 'string' ? item[key].trim() : item[key]
    payload[key] = value === '' || value === undefined ? null : value
  }
  return payload
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng nhóm nghề.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ma_nhom": "...", "ten_nhom": "...", "mo_ta_dac_diem": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng nhóm nghề đang trống')
  }
  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một nhóm nghề`)
    }
    const payload = chuanHoa(item)
    if (!payload.ma_nhom || !payload.ten_nhom || !payload.mo_ta_dac_diem) {
      throw new Error(`Phần tử thứ ${line} thiếu ma_nhom, ten_nhom hoặc mo_ta_dac_diem`)
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

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.loai_hinh_dau_vao) params.loai_hinh_dau_vao = filters.loai_hinh_dau_vao
    if (filters.nhom_muc_tieu) params.nhom_muc_tieu = filters.nhom_muc_tieu
    if (filters.trang_thai !== '' && filters.trang_thai !== null) params.trang_thai = filters.trang_thai
    const data = await fetchNhomNgheDiLam(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nhóm nghề'))
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
  const values = emptyForm()
  for (const key of Object.keys(values)) {
    if (row[key] == null) continue
    // Decimal trả về dạng chuỗi, đổi sang số cho CustomInputNumber.
    values[key] = key.startsWith('luong_') ? Number(row[key]) : row[key]
  }
  Object.assign(form, values)
  dialogVisible.value = true
}

async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    const data = await updateTrangThaiNhomNgheDiLam(row.id, moi)
    row.trang_thai = data.trang_thai
    ElMessage.success(moi === 1 ? `Đã bật "${row.ten_nhom}"` : `Đã tắt "${row.ten_nhom}"`)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái'))
  } finally {
    const conLai = { ...dangDoiTrangThai.value }
    delete conLai[row.id]
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
      `${hanhDong} ${ids.length} nhóm nghề đã chọn đang ${trangThai === 1 ? 'tắt' : 'bật'}?`,
      `Xác nhận ${hanhDong.toLowerCase()} nhóm nghề`,
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
    const result = await updateTrangThaiNhomNgheDiLamMany(ids, trangThai)
    ElMessage.success(`Đã ${trangThai === 1 ? 'bật' : 'tắt'} ${result.updated} nhóm nghề`)
    clearSelection()
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái các nhóm nghề đã chọn'))
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
    createBatch: createNhomNgheDiLamBulk,
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
      await updateNhomNgheDiLam(editingId.value, payload)
      ElMessage.success('Đã cập nhật nhóm nghề')
    } else {
      await createNhomNgheDiLam(payload)
      ElMessage.success('Đã thêm nhóm nghề')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được nhóm nghề'))
  } finally {
    saving.value = false
  }
}

async function xacNhanXoa(noiDung) {
  try {
    await ElMessageBox.confirm(
      `${noiDung} Các nghề cụ thể và liên kết tiêu chí của nhóm cũng bị xóa theo.`,
      'Xác nhận xóa',
      { type: 'warning', confirmButtonText: 'Xóa', cancelButtonText: 'Hủy', confirmButtonClass: 'el-button--danger' },
    )
    return true
  } catch {
    return false
  }
}

async function onDelete(row) {
  if (!(await xacNhanXoa(`Xóa nhóm nghề "${row.ten_nhom}" (${row.ma_nhom})?`))) return
  try {
    await deleteNhomNgheDiLam(row.id)
    ElMessage.success('Đã xóa nhóm nghề')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được nhóm nghề'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return
  if (!(await xacNhanXoa(`Xóa ${ids.length} nhóm nghề đã chọn?`))) return

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteNhomNgheDiLamMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} nhóm nghề`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các nhóm nghề đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>
