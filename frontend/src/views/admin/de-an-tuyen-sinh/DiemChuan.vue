<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="filters">
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã xét tuyển, tên chương trình, trường"
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
          placeholder="Chọn trường"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption v-for="item in truongOptions" :key="item.id" :label="schoolLabel(item)" :value="item.ma_truong" />
        </CustomSelect>
        <CustomSelect v-model="filters.nam_tuyen_sinh" class="filter-year" placeholder="Chọn năm" clearable @change="onSearch">
          <CustomOption v-for="nam in namOptions" :key="nam" :label="String(nam)" :value="nam" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.ma_phuong_thuc_cua_bo"
          class="filter-status"
          placeholder="Chọn phương thức"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in phuongThucOptions"
            :key="item.id"
            :label="phuongThucLabel(item)"
            :value="item.ma_phuong_thuc"
          />
        </CustomSelect>
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">{{ tieuDe }}</h2>
        <div class="toolbar__actions">
          <CustomRadioGroup v-model="cheDo" @change="onSearch">
            <CustomRadioButton value="danh-sach">Danh sách</CustomRadioButton>
            <CustomRadioButton value="theo-truong">Theo trường</CustomRadioButton>
          </CustomRadioGroup>
          <CustomBadge v-if="cheDo === 'danh-sach'" :value="selectedRows.length" :hidden="!selectedRows.length" type="danger">
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
            Thêm điểm chuẩn
          </CustomButton>
        </div>
      </div>

      <BangDiemTheoTruong
        v-if="cheDo === 'theo-truong'"
        :chuong-trinh="chuongTrinhNam"
        :diem-chuan="diemChuanNam"
        :danh-muc-phuong-thuc="phuongThucOptions"
        :q="filters.q"
        :ma-phuong-thuc="filters.ma_phuong_thuc_cua_bo"
        :loading="loading"
        :empty-text="
          filters.ma_truong
            ? `Trường chưa có chương trình hoặc điểm chuẩn năm ${filters.nam_tuyen_sinh || ''}.`
            : 'Chọn trường để xem bảng điểm chuẩn.'
        "
        @sua="openEdit"
      />

      <CustomTable
        v-else
        ref="tableRef"
        :loading="loading"
        :data="rows"
        row-key="id"
        stripe
        border
        @selection-change="(selection) => (selectedRows = selection)"
      >
        <CustomTableColumn type="selection" width="48" reserve-selection align="center" />
        <CustomTableColumn label="STT" width="64" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="nam_tuyen_sinh" label="Năm" width="80" align="center" />
        <CustomTableColumn label="Trường" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ schoolLabel(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ma_xet_tuyen" label="Mã xét tuyển" width="160" />
        <CustomTableColumn label="Chương trình" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ row.ten_chuong_trinh || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Phương thức" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.ma_phuong_thuc_cua_bo ? phuongThucLabel(row) : 'Mọi phương thức' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Tổ hợp" width="140" align="center">
          <template #default="{ row }">{{ row.ma_to_hop || 'Mọi tổ hợp' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Điểm chuẩn" width="150" align="center">
          <template #default="{ row }">
            <strong>{{ soDiem(row.diem_chuan) }}</strong> / {{ soDiem(row.thang_diem) }}
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Tiêu chí phụ" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.tieu_chi_phu || '—' }}</template>
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
          <CustomEmpty description="Chưa có điểm chuẩn nào." />
        </template>
      </CustomTable>

      <div v-if="cheDo === 'danh-sach'" class="pager">
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
    :title="editingId ? 'Cập nhật điểm chuẩn' : 'Thêm điểm chuẩn'"
    width="1040px"
    destroy-on-close
  >
    <CustomRadioGroup v-if="!editingId" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!editingId && createMode === 'json'" class="json-panel">
      <p class="json-panel__mo-ta">
        Dán mảng điểm chuẩn. Mỗi phần tử cần <code>ma_truong</code>, <code>nam_tuyen_sinh</code>,
        <code>ma_xet_tuyen</code>, <code>diem_chuan</code>; <code>ma_phuong_thuc_cua_bo</code> và
        <code>to_hop_id</code> để trống nghĩa là áp dụng chung. Một dòng lỗi thì không lưu dòng nào.
        <CustomButton text type="primary" @click="jsonText = JSON_SAMPLE">Điền mẫu</CustomButton>
      </p>
      <CustomInput
        v-model="jsonText"
        type="textarea"
        :rows="14"
        placeholder="Dán mảng JSON điểm chuẩn"
        class="json-panel__input"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Trường" prop="ma_truong">
          <CustomSelect v-model="form.ma_truong" filterable placeholder="Chọn trường" @change="loadMaXetTuyen">
            <CustomOption
              v-for="item in truongOptions"
              :key="item.id"
              :label="schoolLabel(item)"
              :value="item.ma_truong"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Năm tuyển sinh" prop="nam_tuyen_sinh">
          <CustomInputNumber
            v-model="form.nam_tuyen_sinh"
            :min="1990"
            :max="2100"
            :controls="false"
            placeholder="Nhập năm tuyển sinh"
          />
        </CustomFormItem>
        <CustomFormItem label="Mã xét tuyển" prop="ma_xet_tuyen">
          <CustomSelect
            v-model="form.ma_xet_tuyen"
            filterable
            allow-create
            default-first-option
            :loading="maXetTuyenLoading"
            placeholder="Chọn hoặc nhập mã xét tuyển"
            @change="onMaXetTuyenChange"
          >
            <CustomOption
              v-for="item in maXetTuyenOptions"
              :key="item.ma"
              :label="`${item.ma} — ${item.ten}`"
              :value="item.ma"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên chương trình" prop="ten_chuong_trinh">
          <CustomInput v-model="form.ten_chuong_trinh" maxlength="255" placeholder="Nhập tên chương trình" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Phương thức" prop="ma_phuong_thuc_cua_bo">
          <CustomSelect
            v-model="form.ma_phuong_thuc_cua_bo"
            filterable
            clearable
            placeholder="Chọn phương thức (trống = mọi phương thức)"
          >
            <CustomOption
              v-for="item in phuongThucOptions"
              :key="item.id"
              :label="phuongThucLabel(item)"
              :value="item.ma_phuong_thuc"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Tổ hợp" prop="to_hop_id">
          <CustomSelect v-model="form.to_hop_id" filterable clearable placeholder="Chọn tổ hợp (trống = mọi tổ hợp)">
            <CustomOption v-for="item in toHopOptions" :key="item.id" :label="item.ma_to_hop" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Điểm chuẩn" prop="diem_chuan">
          <CustomInputNumber
            v-model="form.diem_chuan"
            :min="0"
            :precision="2"
            :step="0.25"
            :controls="false"
            placeholder="Nhập điểm chuẩn"
          />
        </CustomFormItem>
        <CustomFormItem label="Thang điểm" prop="thang_diem">
          <CustomInputNumber
            v-model="form.thang_diem"
            :min="1"
            :precision="2"
            :controls="false"
            placeholder="Nhập thang điểm"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tiêu chí phụ" prop="tieu_chi_phu">
          <CustomInput v-model="form.tieu_chi_phu" maxlength="255" placeholder="Nhập tiêu chí phụ (nếu có)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Nguồn dữ liệu" prop="nguon_du_lieu_url">
          <CustomInput v-model="form.nguon_du_lieu_url" maxlength="1000" placeholder="Nhập đường dẫn nguồn công bố" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput v-model="form.ghi_chu" type="textarea" :rows="2" placeholder="Nhập ghi chú" />
        </CustomFormItem>
      </div>
    </CustomForm>

    <template #footer>
      <CustomButton @click="dialogVisible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" @click="onSubmit">Lưu</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/**
 * Điểm chuẩn các năm (xt_diem_chuan, bước 1.6): nhập theo mã trường + năm + mã xét tuyển, có thể riêng
 * từng phương thức / tổ hợp. Dùng làm mốc so sánh khi tìm trường phù hợp.
 */
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import BangDiemTheoTruong from '@/components/admin/diem-chuan/BangDiemTheoTruong.vue'
import { baoLoi } from '@/utils/baoLoi'
import { namMoiNhat } from '@/utils/diemChuanTheoTruong'
import { fetchChuongTrinhDaoTao } from '@/api/chuongTrinhDaoTao'
import {
  createDiemChuan,
  createDiemChuanBulk,
  deleteDiemChuan,
  deleteDiemChuanMany,
  fetchDiemChuan,
  updateDiemChuan,
} from '@/api/diemChuan'
import { fetchPhuongThucTuyenSinh } from '@/api/phuongThucTuyenSinh'
import { fetchToHopMonHoc } from '@/api/toHopMonHoc'
import { fetchTruongHoc } from '@/api/truongHoc'

defineOptions({ name: 'DiemChuan' })

const JSON_SAMPLE = `[
  {
    "ma_truong": "BKA",
    "nam_tuyen_sinh": 2025,
    "ma_xet_tuyen": "IT1",
    "ten_chuong_trinh": "Khoa học máy tính",
    "ma_phuong_thuc_cua_bo": "100",
    "to_hop_id": null,
    "diem_chuan": 28.5,
    "thang_diem": 30,
    "tieu_chi_phu": null,
    "nguon_du_lieu_url": null,
    "ghi_chu": null
  }
]`

const NAM_HIEN_TAI = new Date().getFullYear()
const NAM_MAC_DINH = Array.from({ length: 8 }, (_, i) => NAM_HIEN_TAI - i)

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const rows = ref([])
// 'danh-sach': bảng phẳng có phân trang; 'theo-truong': bảng chéo năm × phương thức của một trường.
const cheDo = ref('danh-sach')
// Chế độ theo trường tải toàn bộ điểm chuẩn và chương trình (mọi năm) của trường, rồi lọc năm tại chỗ.
const diemChuanTruong = ref([])
const chuongTrinhTruong = ref([])
let chuongTrinhCuaTruong = ''
const chuongTrinhNam = computed(() =>
  chuongTrinhTruong.value.filter((item) => item.nam_tuyen_sinh === filters.nam_tuyen_sinh),
)
const diemChuanNam = computed(() =>
  diemChuanTruong.value.filter((item) => item.nam_tuyen_sinh === filters.nam_tuyen_sinh),
)
// 8 năm gần nhất, cộng các năm có đề án hoặc điểm chuẩn của trường đang xem (kể cả năm sau, năm cũ hơn).
const namOptions = computed(() => {
  const nam = new Set(NAM_MAC_DINH)
  for (const item of [...chuongTrinhTruong.value, ...diemChuanTruong.value]) {
    if (item.nam_tuyen_sinh) nam.add(item.nam_tuyen_sinh)
  }
  return [...nam].sort((a, b) => b - a)
})
const tieuDe = computed(() =>
  cheDo.value === 'theo-truong' && filters.nam_tuyen_sinh
    ? `Điểm chuẩn năm ${filters.nam_tuyen_sinh}`
    : 'Điểm chuẩn các năm',
)
const selectedRows = ref([])
const tableRef = ref()
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const formRef = ref()
const truongOptions = ref([])
const phuongThucOptions = ref([])
const toHopOptions = ref([])
const maXetTuyenOptions = ref([])
const maXetTuyenLoading = ref(false)

const filters = reactive({ q: '', ma_truong: '', nam_tuyen_sinh: '', ma_phuong_thuc_cua_bo: '' })
const form = reactive(emptyForm())

const rules = {
  ma_truong: [{ required: true, message: 'Vui lòng chọn trường', trigger: 'change' }],
  nam_tuyen_sinh: [{ required: true, message: 'Vui lòng nhập năm tuyển sinh', trigger: 'blur' }],
  ma_xet_tuyen: [{ required: true, message: 'Vui lòng chọn hoặc nhập mã xét tuyển', trigger: 'change' }],
  diem_chuan: [
    { required: true, message: 'Vui lòng nhập điểm chuẩn', trigger: 'blur' },
    {
      validator: (_rule, value, callback) =>
        value != null && form.thang_diem != null && value > form.thang_diem
          ? callback(new Error('Điểm chuẩn không được lớn hơn thang điểm'))
          : callback(),
      trigger: 'blur',
    },
  ],
  thang_diem: [{ required: true, message: 'Vui lòng nhập thang điểm', trigger: 'blur' }],
}

function emptyForm() {
  return {
    ma_truong: filters?.ma_truong || '',
    nam_tuyen_sinh: NAM_HIEN_TAI - 1,
    ma_xet_tuyen: '',
    ten_chuong_trinh: '',
    ma_phuong_thuc_cua_bo: '',
    to_hop_id: null,
    diem_chuan: null,
    thang_diem: 30,
    tieu_chi_phu: '',
    nguon_du_lieu_url: '',
    ghi_chu: '',
  }
}

function schoolLabel(item) {
  if (!item) return ''
  return item.ten_truong ? `${item.ma_truong} — ${item.ten_truong}` : item.ma_truong
}

// Dùng cho cả dòng danh mục (ma_phuong_thuc) và dòng điểm chuẩn (ma_phuong_thuc_cua_bo).
function phuongThucLabel(item) {
  const ma = item.ma_phuong_thuc_cua_bo || item.ma_phuong_thuc
  return item.ten_phuong_thuc ? `${ma} — ${item.ten_phuong_thuc}` : ma
}

function soDiem(value) {
  return Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 2 })
}

function optionalText(value) {
  const cleaned = String(value ?? '').trim()
  return cleaned || null
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function loadTatCaTruong() {
  const items = []
  for (let trang = 1; trang <= 20; trang += 1) {
    const data = await fetchTruongHoc({ page: trang, page_size: 1000 })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
  }
  return items
}

async function loadOptions() {
  const [truong, phuongThuc, toHop] = await Promise.all([
    loadTatCaTruong(),
    fetchPhuongThucTuyenSinh({ page: 1, page_size: 1000 }),
    fetchToHopMonHoc({ page: 1, page_size: 1000 }),
  ])
  truongOptions.value = truong.sort((a, b) =>
    String(a.ten_truong || '').localeCompare(String(b.ten_truong || ''), 'vi'),
  )
  phuongThucOptions.value = phuongThuc.items || []
  toHopOptions.value = (toHop.items || []).sort((a, b) => a.ma_to_hop.localeCompare(b.ma_to_hop))
}

// Gợi ý mã xét tuyển từ chương trình trong các đề án của trường (mã mới nhất đứng trước).
async function loadMaXetTuyen() {
  maXetTuyenOptions.value = []
  if (!form.ma_truong) return
  maXetTuyenLoading.value = true
  try {
    const data = await fetchChuongTrinhDaoTao({ ma_truong: form.ma_truong, page: 1, page_size: 1000 })
    const theoMa = new Map()
    for (const item of data.items || []) {
      if (item.ma_xet_tuyen && !theoMa.has(item.ma_xet_tuyen)) {
        theoMa.set(item.ma_xet_tuyen, { ma: item.ma_xet_tuyen, ten: item.ten_chuong_trinh })
      }
    }
    maXetTuyenOptions.value = [...theoMa.values()].sort((a, b) => a.ma.localeCompare(b.ma))
  } catch {
    maXetTuyenOptions.value = []
  } finally {
    maXetTuyenLoading.value = false
  }
}

function onMaXetTuyenChange(value) {
  const goiY = maXetTuyenOptions.value.find((item) => item.ma === value)
  if (goiY && !form.ten_chuong_trinh) form.ten_chuong_trinh = goiY.ten
}

function filterParams() {
  const params = {}
  if (filters.q.trim()) params.q = filters.q.trim()
  if (filters.ma_truong) params.ma_truong = filters.ma_truong
  if (filters.nam_tuyen_sinh) params.nam_tuyen_sinh = filters.nam_tuyen_sinh
  if (filters.ma_phuong_thuc_cua_bo) params.ma_phuong_thuc_cua_bo = filters.ma_phuong_thuc_cua_bo
  return params
}

function load() {
  return cheDo.value === 'theo-truong' ? loadTheoTruong() : loadDanhSach()
}

async function loadTatCaTrang(fetcher, params) {
  const items = []
  for (let trang = 1; trang <= 20; trang += 1) {
    const data = await fetcher({ ...params, page: trang, page_size: 1000 })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
  }
  return items
}

// Chương trình đào tạo kèm phương thức, tổ hợp của trường (mọi năm); mỗi trường chỉ tải một lần.
async function loadChuongTrinhTruong(maTruong) {
  if (chuongTrinhCuaTruong === maTruong) return
  chuongTrinhTruong.value = await loadTatCaTrang(fetchChuongTrinhDaoTao, { ma_truong: maTruong, kem_phuong_thuc: true })
  chuongTrinhCuaTruong = maTruong
}

async function loadTheoTruong() {
  diemChuanTruong.value = []
  if (!filters.ma_truong) {
    chuongTrinhTruong.value = []
    chuongTrinhCuaTruong = ''
    return
  }
  loading.value = true
  try {
    const [items] = await Promise.all([
      loadTatCaTrang(fetchDiemChuan, { ma_truong: filters.ma_truong }),
      loadChuongTrinhTruong(filters.ma_truong),
    ])
    diemChuanTruong.value = items
    // Bảng theo trường xem một năm: chưa chọn năm thì lấy năm mới nhất có dữ liệu.
    if (!filters.nam_tuyen_sinh) {
      filters.nam_tuyen_sinh = namMoiNhat(chuongTrinhTruong.value, items) || NAM_HIEN_TAI
    }
  } catch (error) {
    baoLoi(errorMessage(error, 'Không tải được điểm chuẩn của trường'))
  } finally {
    loading.value = false
  }
}

async function loadDanhSach() {
  loading.value = true
  try {
    const data = await fetchDiemChuan({ ...filterParams(), page: page.value, page_size: pageSize.value })
    rows.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    rows.value = []
    total.value = 0
    baoLoi(errorMessage(error, 'Không tải được danh sách điểm chuẩn'))
  } finally {
    loading.value = false
  }
}

function onSearch() {
  tableRef.value?.clearSelection()
  if (page.value !== 1) page.value = 1
  load()
}

function openCreate() {
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  Object.assign(form, emptyForm())
  dialogVisible.value = true
  loadMaXetTuyen()
}

function openEdit(row) {
  editingId.value = row.id
  createMode.value = 'form'
  Object.assign(form, {
    ma_truong: row.ma_truong,
    nam_tuyen_sinh: row.nam_tuyen_sinh,
    ma_xet_tuyen: row.ma_xet_tuyen,
    ten_chuong_trinh: row.ten_chuong_trinh || '',
    ma_phuong_thuc_cua_bo: row.ma_phuong_thuc_cua_bo || '',
    to_hop_id: row.to_hop_id ?? null,
    diem_chuan: row.diem_chuan,
    thang_diem: row.thang_diem,
    tieu_chi_phu: row.tieu_chi_phu || '',
    nguon_du_lieu_url: row.nguon_du_lieu_url || '',
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
  loadMaXetTuyen()
}

function payloadFromForm() {
  return {
    ma_truong: form.ma_truong,
    nam_tuyen_sinh: form.nam_tuyen_sinh,
    ma_xet_tuyen: String(form.ma_xet_tuyen).trim(),
    ten_chuong_trinh: optionalText(form.ten_chuong_trinh),
    ma_phuong_thuc_cua_bo: optionalText(form.ma_phuong_thuc_cua_bo),
    to_hop_id: form.to_hop_id || null,
    diem_chuan: form.diem_chuan,
    thang_diem: form.thang_diem,
    tieu_chi_phu: optionalText(form.tieu_chi_phu),
    nguon_du_lieu_url: optionalText(form.nguon_du_lieu_url),
    ghi_chu: optionalText(form.ghi_chu),
  }
}

function parseJson() {
  let data
  try {
    data = JSON.parse(jsonText.value)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng điểm chuẩn.')
  }
  if (!Array.isArray(data)) data = [data]
  if (!data.length) throw new Error('Mảng điểm chuẩn đang trống')
  return data
}

async function onSubmit() {
  if (!editingId.value && createMode.value === 'json') {
    let items
    try {
      items = parseJson()
    } catch (error) {
      baoLoi(error.message)
      return
    }
    saving.value = true
    try {
      const result = await createDiemChuanBulk(items, { timeout: 120000 })
      ElMessage.success(`Đã nhập ${result.created} dòng điểm chuẩn`)
      dialogVisible.value = false
      await load()
    } catch (error) {
      baoLoi(errorMessage(error, 'Không nhập được điểm chuẩn'))
    } finally {
      saving.value = false
    }
    return
  }

  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await updateDiemChuan(editingId.value, payloadFromForm())
      ElMessage.success('Đã cập nhật điểm chuẩn')
    } else {
      await createDiemChuan(payloadFromForm())
      ElMessage.success('Đã thêm điểm chuẩn')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không lưu được điểm chuẩn'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa điểm chuẩn ${row.ma_xet_tuyen} năm ${row.nam_tuyen_sinh} của ${row.ma_truong}?`,
      'Xác nhận xóa',
      { type: 'warning', confirmButtonText: 'Xóa', cancelButtonText: 'Hủy', confirmButtonClass: 'el-button--danger' },
    )
  } catch {
    return
  }
  try {
    await deleteDiemChuan(row.id)
    ElMessage.success('Đã xóa điểm chuẩn')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) page.value -= 1
    await load()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không xóa được điểm chuẩn'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} dòng điểm chuẩn đã chọn?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }
  deleting.value = true
  try {
    const result = await deleteDiemChuanMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} dòng điểm chuẩn`)
    tableRef.value?.clearSelection()
    if (rows.value.length === ids.length && page.value > 1) page.value -= 1
    await load()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không xóa được điểm chuẩn'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  load()
  loadOptions().catch(() => baoLoi('Không tải được danh mục trường, phương thức, tổ hợp'))
})
</script>

<style scoped>
.create-mode {
  margin-bottom: 16px;
}

.json-panel__mo-ta {
  margin: 0 0 12px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.json-panel__input :deep(textarea) {
  font-family: var(--el-font-family-mono, monospace);
  font-size: 13px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
