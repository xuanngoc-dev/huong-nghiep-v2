<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm tên đề án, trường hoặc năm"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.ma_truong"
          class="filter-school"
          placeholder="Trường"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in truongOptions"
            :key="item.id"
            :label="schoolLabel(item)"
            :value="item.ma_truong"
          />
        </CustomSelect>
        <CustomSelect
          v-model="filters.nam_tuyen_sinh"
          class="filter-year"
          placeholder="Năm học"
          clearable
          @change="onSearch"
        >
          <CustomOption v-for="nam in NAM_HOC" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.trang_thai"
          class="filter-status"
          placeholder="Trạng thái"
          clearable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in STATUS_OPTIONS"
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
        <h2 class="toolbar__title">Danh sách đề án tuyển sinh</h2>
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
            Thêm đề án
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
        <CustomTableColumn prop="nam_tuyen_sinh" label="Năm" width="90" align="center" />
        <CustomTableColumn label="Trường" min-width="240">
          <template #default="{ row }">{{ schoolLabel(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_de_an" label="Tên đề án" min-width="240">
          <template #default="{ row }">
            <CustomButton link type="primary" class="name-link" @click="openDetail(row)">
              {{ row.ten_de_an || 'Xem chi tiết' }}
            </CustomButton>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Chỉ tiêu" width="120" align="right">
          <template #default="{ row }">{{ formatQuota(row.chi_tieu) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Hình thức" min-width="180">
          <template #default="{ row }">{{ formatForms(row.hinh_thuc_dao_tao) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Ngày công bố" width="140" align="center">
          <template #default="{ row }">{{ formatDate(row.ngay_cong_bo) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Trạng thái" width="140" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.trang_thai" :type="statusMeta(row.trang_thai)?.tag || 'info'" effect="light">
              {{ statusMeta(row.trang_thai)?.label || row.trang_thai }}
            </CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Thao tác" width="170" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <CustomTooltip content="Xem chi tiết" placement="top">
                <CustomButton link type="primary" aria-label="Xem chi tiết" @click="openDetail(row)">
                  <CustomIcon><View /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Sửa" placement="top">
                <CustomButton link type="primary" aria-label="Sửa" @click="openEdit(row)">
                  <CustomIcon><Edit /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Sao chép sang năm khác" placement="top">
                <CustomButton link type="primary" aria-label="Sao chép sang năm khác" @click="openSaoChep(row)">
                  <CustomIcon><CopyDocument /></CustomIcon>
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
          <CustomEmpty description="Chưa có đề án tuyển sinh nào." />
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

  <ChiTietDeAnDialog v-model="detailVisible" :de-an-id="detailId" />

  <CustomDialog v-model="saoChep.visible" title="Sao chép đề án sang năm khác" width="640px">
    <p class="sao-chep__mo-ta">
      Tạo đề án mới của <strong>{{ saoChep.nguon ? schoolLabel(saoChep.nguon) : '' }}</strong> từ đề án năm
      {{ saoChep.nguon?.nam_tuyen_sinh }}: chép toàn bộ cơ sở, chương trình, phương thức, tổ hợp, điều kiện…
      Mã xét tuyển cũ được lưu vào "mã xét tuyển năm trước" của từng chương trình.
    </p>
    <CustomForm class="form-grid" label-position="top" @submit.prevent>
      <div class="form-grid__body">
        <CustomFormItem label="Năm tuyển sinh mới" required>
          <CustomSelect v-model="saoChep.nam" placeholder="Chọn năm tuyển sinh mới">
            <CustomOption v-for="nam in namHocSaoChep" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên đề án mới">
          <CustomInput
            v-model="saoChep.ten"
            maxlength="255"
            placeholder="Để trống thì đổi năm trong tên đề án gốc"
          />
        </CustomFormItem>
      </div>
    </CustomForm>
    <template #footer>
      <CustomButton @click="saoChep.visible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saoChep.dangLuu" :disabled="!saoChep.nam" @click="onSaoChep">
        Sao chép
      </CustomButton>
    </template>
  </CustomDialog>

  <CustomDialog
    v-model="dialogVisible"
    :title="editingId ? 'Cập nhật đề án tuyển sinh' : 'Thêm đề án tuyển sinh'"
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
        <!-- <p>
          Dán hoặc chọn file JSON một trường, một năm. Các bảng con nằm trong
          <code>dats_tuyen_sinh</code> (chương trình, phương thức, tổ hợp, điều kiện, ...)
          được nhập cùng đề án. Nếu file có <code>thong_tin_import.ma_truong</code> và
          <code>nam_tuyen_sinh</code>, trường và năm lấy từ file. Mã phương thức của Bộ và mã tổ hợp
          phải có trong danh mục. <code>to_hop_mon_hoc</code> để trống nghĩa là phương thức áp dụng mọi tổ hợp;
          nếu có thì là mảng mã tổ hợp, ví dụ ["A01"].
        </p> -->
        <div class="json-panel__actions">
          <CustomButton text type="primary" @click="openJsonFile">Chọn file</CustomButton>
          <CustomButton text type="primary" @click="fillJsonSample">Điền mẫu</CustomButton>
        </div>
        <input
          ref="jsonFileRef"
          class="json-file"
          type="file"
          accept=".json,application/json"
          @change="onJsonFile"
        />
      </div>
      <div class="json-meta">
        <div class="json-school">
          <span class="json-field__label">Trường</span>
          <CustomSelect
            v-model="jsonTruongId"
            filterable
            placeholder="Chọn trường"
            style="width: 100%"
          >
            <CustomOption
              v-for="item in truongOptions"
              :key="item.id"
              :label="schoolLabel(item)"
              :value="item.ma_truong"
            />
          </CustomSelect>
        </div>
        <div class="json-year">
          <span class="json-field__label">Năm học</span>
          <CustomSelect v-model="jsonNamTuyenSinh" placeholder="Năm học" style="width: 100%">
            <CustomOption v-for="nam in namHocJson" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
          </CustomSelect>
        </div>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="26"
        placeholder="Dán JSON một trường, một năm vào đây"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Trường" prop="ma_truong">
          <CustomSelect
            v-model="form.ma_truong"
            filterable
            placeholder="Chọn trường"
          >
            <CustomOption
              v-for="item in truongOptions"
              :key="item.id"
              :label="schoolLabel(item)"
              :value="item.ma_truong"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Năm học" prop="nam_tuyen_sinh">
          <CustomSelect v-model="form.nam_tuyen_sinh" placeholder="Năm học">
            <CustomOption v-for="nam in namHocForm" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Chỉ tiêu" prop="chi_tieu">
          <CustomInputNumber
            v-model="form.chi_tieu"
            :min="0"
            :step="1"
            :controls="false"
            placeholder="Tổng chỉ tiêu"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên đề án" prop="ten_de_an">
          <CustomInput v-model="form.ten_de_an" maxlength="255" placeholder="Tên đề án tuyển sinh" />
        </CustomFormItem>
        <CustomFormItem label="Trạng thái" prop="trang_thai">
          <CustomSelect v-model="form.trang_thai" clearable placeholder="Chọn trạng thái">
            <CustomOption v-if="form.trang_thai === 'cong_bo'" label="Đã công bố (trạng thái cũ)" value="cong_bo" />
            <CustomOption
              v-for="item in STATUS_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Ngày công bố" prop="ngay_cong_bo">
          <CustomDatePicker
            v-model="form.ngay_cong_bo"
            type="date"
            value-format="YYYY-MM-DD"
            format="DD/MM/YYYY"
            placeholder="Chọn ngày"
            clearable
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Hình thức đào tạo" prop="hinh_thuc_dao_tao">
          <CustomSelect
            v-model="form.hinh_thuc_dao_tao"
            multiple
            filterable
            allow-create
            default-first-option
            :show-select-all="false"
            placeholder="Chọn hoặc nhập hình thức"
          >
            <CustomOption v-for="item in HINH_THUC_OPTIONS" :key="item" :label="item" :value="item" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Nguồn dữ liệu" prop="nguon_du_lieu_url">
          <CustomInput
            v-model="form.nguon_du_lieu_url"
            maxlength="1000"
            placeholder="Đường dẫn đề án gốc"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Giới thiệu" prop="gioi_thieu">
          <CustomInput
            v-model="form.gioi_thieu"
            type="textarea"
            :rows="4"
            maxlength="20000"
            show-word-limit
            placeholder="Nội dung tổng quan đề án"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput
            v-model="form.ghi_chu"
            type="textarea"
            :rows="4"
            maxlength="20000"
            show-word-limit
            placeholder="Ghi chú, cập nhật"
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import { baoLoi } from '@/utils/baoLoi'
import {
  createDeAnTuyenSinh,
  deleteDeAnTuyenSinh,
  deleteDeAnTuyenSinhMany,
  fetchDeAnTuyenSinh,
  importDeAnTuyenSinh,
  saoChepDeAnTuyenSinh,
  updateDeAnTuyenSinh,
} from '@/api/deAnTuyenSinh'
import { fetchTruongHoc } from '@/api/truongHoc'
import { NAM_HOC, danhSachNamHoc, laNamHoc, nhanNamHoc } from '@/constants/namHoc'
import ChiTietDeAnDialog from './ChiTietDeAnDialog.vue'

const STATUS_OPTIONS = [
  { value: 'nhap', label: 'Nháp', tag: 'info' },
  { value: 'da_cong_bo', label: 'Đã công bố', tag: 'success' },
  { value: 'het_hieu_luc', label: 'Hết hiệu lực', tag: 'warning' },
]

const HINH_THUC_OPTIONS = [
  'Chính quy',
  'Liên thông',
  'Vừa học vừa làm',
  'Đào tạo từ xa',
  'Văn bằng 2',
]

const IMPORT_LABELS = {
  dats_tuyen_sinh: 'đề án',
  dats_tru_so: 'trụ sở',
  dats_website: 'website',
  dats_lien_he_tuyen_sinh: 'liên hệ',
  dats_chuong_trinh_dao_tao: 'chương trình',
  dats_ke_hoach_tuyen_sinh: 'kế hoạch',
  dats_phuong_thuc: 'phương thức',
  dats_phuong_thuc_to_hop: 'tổ hợp',
  dats_nhan_su: 'nhân sự',
  dats_co_so_vat_chat: 'cơ sở vật chất',
  dats_quy_mo_dao_tao: 'quy mô',
  dats_ty_le_viec_lam: 'tỷ lệ việc làm',
  dats_trinh_do_nganh: 'trình độ ngành',
  dats_doi_tuong_du_tuyen: 'đối tượng',
  dats_dieu_kien_du_tuyen: 'điều kiện',
  dats_tieu_chi_xet_tuyen: 'tiêu chí',
  dats_diem_cong: 'điểm cộng',
  dats_quy_tac_phan_bo: 'quy tắc phân bổ',
  dats_ho_so_du_tuyen: 'hồ sơ',
  dats_quy_doi_nguong_dau_vao: 'quy đổi ngưỡng',
  dats_quy_doi_diem_trung_tuyen: 'quy đổi điểm',
  dats_chinh_sach_xet_tuyen_thang: 'xét tuyển thẳng',
  dats_chinh_sach_uu_tien_xet_tuyen: 'ưu tiên',
}

const JSON_SAMPLE = `{
  "thong_tin_import": {
    "phien_ban_cau_truc": "3.2",
    "pham_vi": "mot_truong_mot_nam",
    "ma_truong": "BKA",
    "nam_tuyen_sinh": 2026,
    "kieu_cau_truc": "mot_de_an_long_nhau",
    "xu_ly_khi_da_ton_tai": "tu_choi"
  },
  "dats_tuyen_sinh": {
    "chi_tieu": 9880,
    "ten_de_an": "Thông tin tuyển sinh đại học chính quy năm 2026 - Đại học Bách khoa Hà Nội",
    "hinh_thuc_dao_tao": ["Chính quy"],
    "gioi_thieu": "Mẫu rút gọn. File đầy đủ lồng chương trình, phương thức và tổ hợp.",
    "ngay_cong_bo": "2026-03-03",
    "nguon_du_lieu_url": null,
    "trang_thai": null,
    "ghi_chu": null,
    "dats_lien_he_tuyen_sinh": [
      { "ten_don_vi": "Ban Tuyển sinh - Hướng nghiệp" }
    ],
    "dats_doi_tuong_du_tuyen": [
      {
        "ma_doi_tuong": "THPT",
        "ten_doi_tuong": "Thí sinh xét tuyển kết quả thi THPT"
      }
    ],
    "dats_dieu_kien_du_tuyen": [
      {
        "ma_dieu_kien": "DK_THPT",
        "ten_dieu_kien": "Tốt nghiệp THPT",
        "loai_dieu_kien": "bat_buoc",
        "noi_dung_dieu_kien": "Đã tốt nghiệp THPT",
        "ma_doi_tuong_du_tuyen": "THPT"
      }
    ],
    "dats_chuong_trinh_dao_tao": [
      {
        "ma_xet_tuyen": "BF1",
        "ten_chuong_trinh": "Kỹ thuật Sinh học",
        "trinh_do_dao_tao": "dai_hoc",
        "hinh_thuc_dao_tao": "chinh_quy",
        "dats_phuong_thuc": [
          {
            "ma_phuong_thuc_cua_bo": "100",
            "ma_phuong_thuc_cua_truong": "THPT",
            "ten_phuong_thuc_cua_truong": "Xét kết quả thi THPT",
            "to_hop_mon_hoc": ["A00"],
            "dats_phuong_thuc_to_hop": [
              { "thu_tu_hien_thi": 1, "ma_to_hop": "A00" }
            ]
          }
        ],
        "dats_trinh_do_nganh": [
          { "trinh_do_dao_tao": "dai_hoc", "hinh_thuc_dao_tao": "chinh_quy" }
        ]
      }
    ]
  }
}`

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
const detailVisible = ref(false)
const detailId = ref(null)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonFileRef = ref(null)
const jsonTruongId = ref(null)
const jsonNamTuyenSinh = ref(new Date().getFullYear())
const jsonImport = useJsonBatchImport({ label: 'đề án tuyển sinh' })
const formRef = ref()
const truongOptions = ref([])
const saoChep = reactive({ visible: false, dangLuu: false, nguon: null, nam: null, ten: '' })

const filters = reactive({
  q: '',
  trang_thai: '',
  nam_tuyen_sinh: '',
  ma_truong: '',
})

const form = reactive(emptyForm())

const rules = {
  ma_truong: [{ required: true, message: 'Vui lòng chọn trường', trigger: 'change' }],
  nam_tuyen_sinh: [{ required: true, message: 'Vui lòng chọn năm học', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_truong: null,
    nam_tuyen_sinh: new Date().getFullYear(),
    chi_tieu: null,
    ten_de_an: '',
    hinh_thuc_dao_tao: [],
    gioi_thieu: '',
    ngay_cong_bo: '',
    nguon_du_lieu_url: '',
    trang_thai: 'nhap',
    ghi_chu: '',
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonTruongId.value = null
  jsonNamTuyenSinh.value = new Date().getFullYear()
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function schoolLabel(school) {
  if (!school) return ''
  return school.ma_truong ? `${school.ma_truong} — ${school.ten_truong}` : school.ten_truong
}

function statusMeta(value) {
  return STATUS_OPTIONS.find((item) => item.value === (value === 'cong_bo' ? 'da_cong_bo' : value)) || null
}

function formatDate(value) {
  if (!value) return '—'
  const [year, month, day] = String(value).slice(0, 10).split('-')
  if (!year || !month || !day) return value
  return `${day}/${month}/${year}`
}

function formatQuota(value) {
  if (value == null || value === '') return '—'
  return Number(value).toLocaleString('vi-VN')
}

function formatForms(value) {
  if (!Array.isArray(value) || !value.length) return '—'
  return value.join(', ')
}

function optionalText(value) {
  if (value == null) return null
  const cleaned = String(value).trim()
  return cleaned || null
}

function selectedJsonYear() {
  const year = Number(jsonNamTuyenSinh.value)
  if (!Number.isInteger(year) || year < 1990 || year > 2100) return null
  return year
}

function selectedJsonSchool() {
  const code = jsonTruongId.value
  if (code == null || code === '') return null
  return truongOptions.value.find((school) => school.ma_truong === code) || null
}

function parseJsonDocument(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một đề án theo cấu trúc một trường, một năm.')
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    throw new Error('JSON phải là một object có khóa dats_tuyen_sinh.')
  }
  if (
    data.thong_tin_import != null &&
    (typeof data.thong_tin_import !== 'object' || Array.isArray(data.thong_tin_import))
  ) {
    throw new Error('thong_tin_import phải là object')
  }
  const item = data.dats_tuyen_sinh
  if (!item || typeof item !== 'object' || Array.isArray(item)) {
    throw new Error('Thiếu object dats_tuyen_sinh')
  }
  return data
}

function applyDocumentSelection(data) {
  const info = data.thong_tin_import && !Array.isArray(data.thong_tin_import) ? data.thong_tin_import : {}
  const yearValue = info.nam_tuyen_sinh ?? data.dats_tuyen_sinh?.nam_tuyen_sinh
  if (yearValue != null && yearValue !== '') {
    const year = Number(yearValue)
    if (!Number.isInteger(year) || year < 1990 || year > 2100) {
      throw new Error('Năm tuyển sinh trong file phải là số từ 1990 đến 2100')
    }
    jsonNamTuyenSinh.value = year
  }
  const code = info.ma_truong
  if (code == null || String(code).trim() === '') return
  const school = truongOptions.value.find(
    (item) => String(item.ma_truong || '').trim().toUpperCase() === String(code).trim().toUpperCase(),
  )
  if (!school) {
    throw new Error(`Không tìm thấy trường có mã ${String(code).trim()}`)
  }
  jsonTruongId.value = school.ma_truong
}

function importSummary(counts, quyTac) {
  const parts = Object.entries(counts || {})
    .filter(([, count]) => Number(count) > 0)
    .map(([table, count]) => `${count} ${IMPORT_LABELS[table] || table}`)
  const tomTat = parts.length ? `Đã nhập ${parts.join(', ')}` : 'Đã nhập đề án tuyển sinh'
  if (!quyTac) return tomTat
  const soDong = quyTac.so_dong || {}
  return (
    `${tomTat}; quy tắc xét tuyển: ${soDong.xt_cong_thuc || 0} công thức, ${soDong.xt_phuong_an || 0} phương án, ` +
    `${soDong.dats_hoc_phi || 0} học phí, ${soDong.xt_diem_chuan || 0} điểm chuẩn`
  )
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function yearFilter() {
  return laNamHoc(filters.nam_tuyen_sinh)
}

const namHocForm = computed(() => danhSachNamHoc(new Date().getFullYear(), form.nam_tuyen_sinh))
// Năm đích: đến năm sau năm hiện tại (và sau năm của đề án gốc), bỏ năm của chính đề án gốc.
const namHocSaoChep = computed(() => {
  const namGoc = Number(saoChep.nguon?.nam_tuyen_sinh)
  const namCuoi = Math.max(new Date().getFullYear() + 1, namGoc + 1 || 0)
  return danhSachNamHoc(namCuoi).filter((nam) => nam !== namGoc)
})
const namHocJson = computed(() => danhSachNamHoc(new Date().getFullYear(), jsonNamTuyenSinh.value))

async function loadTruongOptions() {
  const pageSizeOptions = 1000
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchTruongHoc({ page: current, page_size: pageSizeOptions })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  items.sort((a, b) => String(a.ten_truong || '').localeCompare(String(b.ten_truong || ''), 'vi'))
  truongOptions.value = items
}

async function load() {
  const year = yearFilter()

  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai) params.trang_thai = filters.trang_thai
    if (year != null) params.nam_tuyen_sinh = year
    if (filters.ma_truong) params.ma_truong = filters.ma_truong
    const data = await fetchDeAnTuyenSinh(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    baoLoi(errorMessage(error, 'Không tải được danh sách đề án tuyển sinh'))
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

function openDetail(row) {
  detailId.value = row.id
  detailVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    ma_truong: row.ma_truong,
    nam_tuyen_sinh: row.nam_tuyen_sinh,
    chi_tieu: row.chi_tieu ?? null,
    ten_de_an: row.ten_de_an || '',
    hinh_thuc_dao_tao: Array.isArray(row.hinh_thuc_dao_tao) ? [...row.hinh_thuc_dao_tao] : [],
    gioi_thieu: row.gioi_thieu || '',
    ngay_cong_bo: row.ngay_cong_bo ? String(row.ngay_cong_bo).slice(0, 10) : '',
    nguon_du_lieu_url: row.nguon_du_lieu_url || '',
    trang_thai: row.trang_thai || '',
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ma_truong: form.ma_truong,
    nam_tuyen_sinh: form.nam_tuyen_sinh,
    chi_tieu: form.chi_tieu == null || form.chi_tieu === '' ? null : Number(form.chi_tieu),
    ten_de_an: optionalText(form.ten_de_an),
    hinh_thuc_dao_tao: form.hinh_thuc_dao_tao?.length ? form.hinh_thuc_dao_tao : null,
    gioi_thieu: optionalText(form.gioi_thieu),
    ngay_cong_bo: form.ngay_cong_bo || null,
    nguon_du_lieu_url: optionalText(form.nguon_du_lieu_url),
    trang_thai: optionalText(form.trang_thai),
    ghi_chu: optionalText(form.ghi_chu),
  }
}

function fillJsonSample() {
  jsonText.value = JSON_SAMPLE
  try {
    applyDocumentSelection(parseJsonDocument(jsonText.value))
  } catch (error) {
    baoLoi(error.message)
  }
}

function openJsonFile() {
  jsonFileRef.value?.click()
}

function onJsonFile(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    jsonText.value = String(reader.result || '')
    try {
      applyDocumentSelection(parseJsonDocument(jsonText.value))
    } catch (error) {
      baoLoi(error.message)
    }
  }
  reader.onerror = () => {
    baoLoi('Không đọc được file JSON')
  }
  reader.readAsText(file)
}

async function onSubmitJson() {
  let document
  try {
    document = parseJsonDocument(jsonText.value)
    applyDocumentSelection(document)
  } catch (error) {
    baoLoi(error.message)
    return
  }

  const schoolAfterFile = selectedJsonSchool()
  const yearAfterFile = selectedJsonYear()
  if (!schoolAfterFile) {
    baoLoi('Vui lòng chọn trường')
    return
  }
  if (yearAfterFile == null) {
    baoLoi('Năm tuyển sinh phải là số từ 1990 đến 2100')
    return
  }

  saving.value = true
  try {
    const result = await importDeAnTuyenSinh(
      {
        ma_truong: schoolAfterFile.ma_truong,
        nam_tuyen_sinh: yearAfterFile,
        du_lieu: document,
      },
      { skipLoading: true, timeout: 300000 },
    )
    ElMessage.success(importSummary(result?.counts, result?.quy_tac))
    // Khối quy_tac_xet_tuyen không khớp chương trình / cơ sở của file, quy định chưa mô hình hóa...
    const canhBao = result?.quy_tac?.canh_bao || []
    if (canhBao.length) {
      ElMessage.warning({ message: `Quy tắc xét tuyển: ${canhBao.join('; ')}`, duration: 10000, showClose: true })
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không nhập được đề án tuyển sinh'))
  } finally {
    saving.value = false
  }
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
      await updateDeAnTuyenSinh(editingId.value, payload)
      ElMessage.success('Đã cập nhật đề án tuyển sinh')
    } else {
      await createDeAnTuyenSinh(payload)
      ElMessage.success('Đã thêm đề án tuyển sinh')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không lưu được đề án tuyển sinh'))
  } finally {
    saving.value = false
  }
}

function openSaoChep(row) {
  Object.assign(saoChep, { visible: true, dangLuu: false, nguon: row, nam: Number(row.nam_tuyen_sinh) + 1, ten: '' })
}

async function onSaoChep() {
  const nguon = saoChep.nguon
  saoChep.dangLuu = true
  try {
    const result = await saoChepDeAnTuyenSinh(
      nguon.id,
      { nam_tuyen_sinh: saoChep.nam, ten_de_an: optionalText(saoChep.ten) },
      { timeout: 120000 },
    )
    const chuongTrinh = result.counts?.dats_chuong_trinh_dao_tao || 0
    ElMessage.success(`Đã tạo đề án năm ${result.de_an.nam_tuyen_sinh} (${chuongTrinh} chương trình)`)
    saoChep.visible = false
    await load()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không sao chép được đề án tuyển sinh'))
  } finally {
    saoChep.dangLuu = false
  }
}

async function onDelete(row) {
  const name = row.ten_de_an || `năm ${row.nam_tuyen_sinh}`
  try {
    await ElMessageBox.confirm(
      `Xóa đề án "${name}" của ${row.ten_truong}? Dữ liệu liên quan của đề án cũng bị xóa.`,
      'Xác nhận xóa',
      {
        type: 'warning',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy',
        confirmButtonClass: 'el-button--danger',
      },
    )
  } catch {
    return
  }

  try {
    await deleteDeAnTuyenSinh(row.id)
    ElMessage.success('Đã xóa đề án tuyển sinh')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không xóa được đề án tuyển sinh'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} đề án tuyển sinh đã chọn? Dữ liệu liên quan của các đề án cũng bị xóa.`,
      'Xác nhận xóa',
      {
        type: 'warning',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy',
        confirmButtonClass: 'el-button--danger',
      },
    )
  } catch {
    return
  }

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteDeAnTuyenSinhMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} đề án tuyển sinh`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không xóa được các đề án tuyển sinh đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadTruongOptions().catch(() => {})])
})
</script>

<style scoped>
.name-link {
  max-width: 100%;
  height: auto;
  padding: 0;
  white-space: normal;
  text-align: left;
  line-height: 1.4;
}

.json-panel__actions {
  display: flex;
  flex-shrink: 0;
  gap: 4px;
}

.json-file {
  display: none;
}

.json-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 12px;
}

.json-school {
  flex: 1 1 320px;
  max-width: 480px;
}

.json-year {
  width: 180px;
}

@media (max-width: 640px) {
  .json-school,
  .json-year {
    width: 100%;
    max-width: none;
  }
}

.sao-chep__mo-ta {
  margin: 0 0 16px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}
</style>
