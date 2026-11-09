<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import {
  createNganh,
  createNganhBulk,
  deleteNganh,
  deleteNganhMany,
  fetchNganh,
  updateNganh,
} from '@/api/nganhDaoTao'
import { fetchNhomNganh } from '@/api/nhomNganhDaoTao'
import { DON_VI_TIEN, DON_VI_TIEN_MAC_DINH } from '@/constants/donViTien'
import { KY_LUONG_MAC_DINH, maKyLuong } from '@/constants/kyLuong'
import { danhSachCap, danhSachMucLuong, noiCap, noiMucLuong } from '@/utils/capTenGiaTri'
import BangMucLuong from './BangMucLuong.vue'
import BangTenGiaTri from './BangTenGiaTri.vue'

const TRINH_DO = ['Trung cấp', 'Cao đẳng', 'Đại học', 'Thạc sĩ', 'Tiến sĩ']

const JSON_SAMPLE = `[
  {
    "ma_nhom_nganh": "74802",
    "ma_nganh": "7480201",
    "ten_nganh": "Công nghệ thông tin",
    "ten_tieng_anh": "Information technology",
    "trinh_do": "Đại học",
    "ma_holand": ["R", "I"],
    "hinh_anh_mo_ta": "https://example.com/cntt.jpg",
    "muc_luong_tham_khao": [
      { "name": "1 năm", "min": 10, "max": 15, "unit": "VND", "period": "thang" },
      { "name": "3 năm", "min": 15.5, "max": 20, "unit": "VND", "period": "thang" }
    ],
    "mo_ta_cong_viec": [
      { "name": "Nhiệm vụ chính", "value": "Phân tích yêu cầu và xây dựng phần mềm.", "ghi_chu": "Làm việc với nhóm sản phẩm" }
    ],
    "lo_trinh_phat_trien": [
      { "name": "Năm 1-2", "value": "Thực tập, lập trình viên mới", "ghi_chu": "" },
      { "name": "Năm 3-5", "value": "Lập trình viên chính" }
    ],
    "nhan_dan": "Nhu cầu cao",
    "thoi_gian_dao_tao": "4 năm",
    "chi_tiet": "Ngành đào tạo về phần mềm, dữ liệu và hệ thống thông tin.",
    "trang_thai": 1
  }
]`

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
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'ngành' })
const formRef = ref()
const nhomOptions = ref([])
const hollandOptions = ref([])

const filters = reactive({
  q: '',
  trang_thai: '',
  ma_nhom_nganh: '',
})

const form = reactive(emptyForm())

const trinhDoOptions = computed(() => {
  const current = form.trinh_do?.trim()
  if (current && !TRINH_DO.includes(current)) return [current, ...TRINH_DO]
  return TRINH_DO
})

const hollandSelectOptions = computed(() => {
  const known = new Set(hollandOptions.value.map((item) => item.ma_nhom))
  const extras = (form.ma_holand || [])
    .filter((code) => !known.has(code))
    .map((code) => ({ ma_nhom: code, ten_nhom: 'không còn trong danh mục', trang_thai: 0 }))
  return [...hollandOptions.value, ...extras]
})

const rules = {
  ma_nhom_nganh: [{ required: true, message: 'Vui lòng chọn nhóm ngành', trigger: 'change' }],
  ten_nganh: [{ required: true, message: 'Vui lòng nhập tên ngành', trigger: 'blur' }],
  ma_nganh: [{ required: true, message: 'Vui lòng nhập mã ngành', trigger: 'blur' }],
  ten_tieng_anh: [{ required: true, message: 'Vui lòng nhập tên tiếng Anh', trigger: 'blur' }],
  trinh_do: [{ required: true, message: 'Vui lòng chọn trình độ', trigger: 'change' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_nhom_nganh: '',
    ma_nganh: '',
    ten_nganh: '',
    ten_tieng_anh: '',
    trinh_do: '',
    ma_holand: [],
    mo_ta: '',
    hinh_anh_mo_ta: '',
    muc_luong_tham_khao: [],
    mo_ta_cong_viec: [],
    lo_trinh_phat_trien: [],
    nhan_dan: '',
    thoi_gian_dao_tao: '',
    chi_tiet: '',
    trang_thai: 1,
  }
}

function optionalText(value) {
  if (value == null) return null
  const text = String(value).trim()
  return text || null
}

function hienNhapTien(value) {
  if (value == null || value === '') return ''
  const num = Number(value)
  if (!Number.isFinite(num) || num < 0) return ''
  return String(num)
}

function copyMucLuong(value) {
  return danhSachMucLuong(value).map((item) => ({
    name: item.name,
    min: hienNhapTien(item.min),
    max: hienNhapTien(item.max),
    unit: item.unit || DON_VI_TIEN_MAC_DINH,
    period: maKyLuong(item.period) || KY_LUONG_MAC_DINH,
  }))
}

function copyCap(value) {
  return danhSachCap(value).map((item) => ({
    name: item.name,
    value: item.value,
    ghi_chu: item.ghi_chu || '',
  }))
}

function docSoTien(value) {
  const raw = String(value ?? '').trim().replace(',', '.')
  const text = raw.endsWith('.') ? raw.slice(0, -1) : raw
  if (!/^\d+(\.\d+)?$/.test(text)) return null
  const num = Number(text)
  return Number.isFinite(num) ? num : null
}

function chuanMucLuong(rows, label) {
  const cleaned = []
  const units = new Set(DON_VI_TIEN.map((item) => item.value))
  for (const [index, item] of (rows || []).entries()) {
    const name = String(item?.name || '').trim()
    const minText = String(item?.min ?? '').trim()
    const maxText = String(item?.max ?? '').trim()
    const unit = String(item?.unit || '').trim().toUpperCase() || DON_VI_TIEN_MAC_DINH
    const period = maKyLuong(item?.period)
    if (!name && !minText && !maxText) continue
    const line = `${label}: dòng ${index + 1}`
    if (!name || !minText || !maxText) {
      throw new Error(`${line} cần đủ kinh nghiệm, mức từ và mức đến`)
    }
    const min = docSoTien(minText)
    const max = docSoTien(maxText)
    if (min == null || max == null) {
      throw new Error(`${line} chỉ nhập số không âm`)
    }
    if (min > max) throw new Error(`${line} có mức từ lớn hơn mức đến`)
    if (!units.has(unit)) throw new Error(`${line} có đơn vị tính không hợp lệ`)
    if (!period) throw new Error(`${line} có thời gian lương không hợp lệ`)
    cleaned.push({ name, min, max, unit, period })
  }
  return cleaned.length ? cleaned : null
}

function chuanCap(rows, label) {
  const cleaned = []
  for (const [index, item] of (rows || []).entries()) {
    const name = String(item?.name || '').trim()
    const value = String(item?.value || '').trim()
    const ghiChu = String(item?.ghi_chu || '').trim()
    if (!name && !value && !ghiChu) continue
    if (!name || !value) {
      throw new Error(`${label}: dòng ${index + 1} cần cả tên và giá trị`)
    }
    cleaned.push(ghiChu ? { name, value, ghi_chu: ghiChu } : { name, value })
  }
  return cleaned.length ? cleaned : null
}

function parseMucLuong(value, line) {
  if (value == null || value === '') return null
  if (!Array.isArray(value)) {
    throw new Error(`Phần tử thứ ${line}: muc_luong_tham_khao phải là mảng {name, min, max, unit, period}`)
  }
  return chuanMucLuong(value, `Phần tử thứ ${line}, mức lương`)
}

function parseCap(value, line, field) {
  if (value == null || value === '') return null
  if (!Array.isArray(value)) {
    throw new Error(`Phần tử thứ ${line}: ${field} phải là mảng object {name, value, ghi_chu}`)
  }
  return chuanCap(value, `Phần tử thứ ${line}, ${field}`)
}

function parentLabel(item) {
  const suffix = item.trang_thai === 1 ? '' : ' — ngừng sử dụng'
  return `${item.ma_nhom_nganh} · ${item.ten_nhom_nganh}${suffix}`
}

function hollandLabel(item) {
  const suffix = item.trang_thai === 1 ? '' : ' — ngừng sử dụng'
  return `${item.ten_nhom} · ${item.ma_nhom}${suffix}`
}

function resetForm() {
  Object.assign(form, emptyForm())
  form.ma_holand = []
  form.muc_luong_tham_khao = []
  form.mo_ta_cong_viec = []
  form.lo_trinh_phat_trien = []
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function parseHolland(value, line) {
  if (value == null || value === '') return null
  if (!Array.isArray(value)) {
    throw new Error(`Phần tử thứ ${line} cần ma_holand là mảng mã, ví dụ ["R", "I"]`)
  }
  const codes = value.map((code) => String(code).trim()).filter(Boolean)
  return codes.length ? codes : null
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng ngành đào tạo.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ma_nhom_nganh": "74802", "ten_nganh": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng ngành đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một ngành`)
    }
    const maNhom = String(item.ma_nhom_nganh ?? '').trim()
    const ten = String(item.ten_nganh ?? '').trim()
    const ma = String(item.ma_nganh ?? '').trim()
    const tenTiengAnh = String(item.ten_tieng_anh ?? '').trim()
    const trinhDo = String(item.trinh_do ?? '').trim()
    if (!maNhom || !ten || !ma || !tenTiengAnh || !trinhDo) {
      throw new Error(
        `Phần tử thứ ${line} thiếu ma_nhom_nganh, ten_nganh, ma_nganh, ten_tieng_anh hoặc trinh_do`,
      )
    }
    return {
      ma_nhom_nganh: maNhom,
      ten_nganh: ten,
      ma_nganh: ma,
      ten_tieng_anh: tenTiengAnh,
      trinh_do: trinhDo,
      ma_holand: parseHolland(item.ma_holand, line),
      mo_ta: optionalText(item.mo_ta),
      hinh_anh_mo_ta: optionalText(item.hinh_anh_mo_ta),
      muc_luong_tham_khao: parseMucLuong(item.muc_luong_tham_khao, line),
      mo_ta_cong_viec: parseCap(item.mo_ta_cong_viec, line, 'mo_ta_cong_viec'),
      lo_trinh_phat_trien: parseCap(item.lo_trinh_phat_trien, line, 'lo_trinh_phat_trien'),
      nhan_dan: optionalText(item.nhan_dan),
      thoi_gian_dao_tao: optionalText(item.thoi_gian_dao_tao),
      chi_tiet: optionalText(item.chi_tiet),
      trang_thai: item.trang_thai ?? 1,
    }
  })
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function loadAll(fetchFn) {
  const pageSize = 100
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchFn({ page: current, page_size: pageSize })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  return items
}

async function loadOptions() {
  const [groups, holland] = await Promise.all([loadAll(fetchNhomNganh), loadAll(fetchNhomHolland)])
  groups.sort((a, b) => a.ma_nhom_nganh.localeCompare(b.ma_nhom_nganh, 'vi'))
  holland.sort((a, b) => a.ma_nhom.localeCompare(b.ma_nhom, 'vi'))
  nhomOptions.value = groups
  hollandOptions.value = holland
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
    if (filters.ma_nhom_nganh) params.ma_nhom_nganh = filters.ma_nhom_nganh
    const data = await fetchNganh(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách ngành'))
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

async function openCreate() {
  resetForm()
  if (filters.ma_nhom_nganh) form.ma_nhom_nganh = filters.ma_nhom_nganh
  dialogVisible.value = true
  await loadOptions().catch(() => {})
}

async function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    ma_nhom_nganh: row.ma_nhom_nganh,
    ma_nganh: row.ma_nganh,
    ten_nganh: row.ten_nganh,
    ten_tieng_anh: row.ten_tieng_anh,
    trinh_do: row.trinh_do,
    ma_holand: [...(row.ma_holand || [])],
    mo_ta: row.mo_ta || '',
    hinh_anh_mo_ta: row.hinh_anh_mo_ta || '',
    muc_luong_tham_khao: copyMucLuong(row.muc_luong_tham_khao),
    mo_ta_cong_viec: copyCap(row.mo_ta_cong_viec),
    lo_trinh_phat_trien: copyCap(row.lo_trinh_phat_trien),
    nhan_dan: row.nhan_dan || '',
    thoi_gian_dao_tao: row.thoi_gian_dao_tao || '',
    chi_tiet: row.chi_tiet || '',
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
  await loadOptions().catch(() => {})
}

function payloadFromForm() {
  return {
    ma_nhom_nganh: String(form.ma_nhom_nganh).trim().toUpperCase(),
    ma_nganh: form.ma_nganh.trim().toUpperCase(),
    ten_nganh: form.ten_nganh.trim(),
    ten_tieng_anh: form.ten_tieng_anh.trim(),
    trinh_do: form.trinh_do.trim(),
    ma_holand: form.ma_holand?.length ? form.ma_holand : null,
    mo_ta: optionalText(form.mo_ta),
    hinh_anh_mo_ta: optionalText(form.hinh_anh_mo_ta),
    muc_luong_tham_khao: chuanMucLuong(form.muc_luong_tham_khao, 'Mức lương tham khảo'),
    mo_ta_cong_viec: chuanCap(form.mo_ta_cong_viec, 'Mô tả công việc'),
    lo_trinh_phat_trien: chuanCap(form.lo_trinh_phat_trien, 'Lộ trình phát triển'),
    nhan_dan: optionalText(form.nhan_dan),
    thoi_gian_dao_tao: optionalText(form.thoi_gian_dao_tao),
    chi_tiet: optionalText(form.chi_tiet),
    trang_thai: form.trang_thai,
  }
}

const SAMPLE_MO_TA = `Ngành Công nghệ thông tin đào tạo khả năng phân tích bài toán, thiết kế giải pháp và xây dựng phần mềm cho doanh nghiệp, cơ quan và dịch vụ số. Người học được trang bị tư duy thuật toán, lập trình, cơ sở dữ liệu, mạng máy tính, an toàn thông tin và cách triển khai sản phẩm theo dự án.

Chương trình gắn lý thuyết với thực hành: làm bài tập lớn, tham gia nhóm, đọc tài liệu kỹ thuật và trình bày kết quả cho người dùng không chuyên. Sinh viên rèn thói quen viết mã rõ ràng, kiểm thử, quản lý phiên bản và tiếp nhận phản hồi để chỉnh sửa sản phẩm.

Ngành phù hợp với người kiên nhẫn, ham học công nghệ mới và muốn tạo ra ứng dụng có người dùng thật. Sau tốt nghiệp có thể làm lập trình, kiểm thử, phân tích nghiệp vụ, vận hành hệ thống hoặc học tiếp về dữ liệu, trí tuệ nhân tạo và điện toán đám mây.`

const SAMPLE_CHI_TIET = `Mục tiêu đào tạo
Đào tạo cử nhân có nền tảng vững về khoa học máy tính và kỹ năng nghề để tham gia xây dựng, bảo trì và cải tiến hệ thống thông tin. Người học biết chuyển yêu cầu thực tế thành đặc tả, thiết kế, mã nguồn và tài liệu bàn giao. Kết thúc chương trình, sinh viên có thể làm việc độc lập ở mức cơ bản và phối hợp trong nhóm sản phẩm.

Kiến thức cốt lõi
Toán rời rạc, xác suất thống kê và tư duy thuật toán giúp đánh giá độ phức tạp của lời giải. Cấu trúc dữ liệu, lập trình hướng đối tượng, cơ sở dữ liệu quan hệ và phi quan hệ là phần bắt buộc. Kiến trúc máy tính, hệ điều hành và mạng máy tính giải thích cách chương trình chạy trên hạ tầng thật. An toàn thông tin, kiểm thử và quy trình phát triển phần mềm được học song song với đồ án.

Kỹ năng nghề nghiệp
Sinh viên viết được ứng dụng web hoặc dịch vụ phía máy chủ, thiết kế lược đồ dữ liệu, truy vấn và tối ưu các thao tác thường gặp. Biết dùng Git, trình soạn mã, công cụ gỡ lỗi và môi trường triển khai thử. Đọc được tài liệu tiếng Anh ở mức chuyên ngành, ước lượng công việc và báo cáo tiến độ. Kỹ năng giao tiếp giúp làm rõ yêu cầu mơ hồ trước khi lập trình.

Môi trường và cơ hội
Người làm nghề thường ngồi theo nhóm nhỏ, làm việc theo sprint, họp ngắn và demo định kỳ. Việc có thể ở công ty sản phẩm, gia công phần mềm, ngân hàng, viễn thông, y tế, giáo dục hoặc cơ quan nhà nước đang chuyển đổi số. Vị trí khởi đầu thường là lập trình viên, kiểm thử viên hoặc nhân viên vận hành. Sau vài năm có thể đi sâu frontend, backend, dữ liệu, bảo mật, điện toán đám mây hoặc đảm nhận vai trò dẫn dắt kỹ thuật.

Phẩm chất cần có
Cần sự cẩn thận khi xử lý dữ liệu và lỗi biên, sẵn sàng học lại công cụ khi công nghệ đổi, và tôn trọng người dùng cuối. Ngành đòi hỏi thời gian thực hành ngoài giờ lý thuyết. Người chỉ muốn học thuộc mà không làm dự án sẽ khó theo kịp. Ngược lại, người chịu làm bài, hỏi khi kẹt và ghi lại cách mình sửa lỗi sẽ tiến bộ đều.

Lưu ý khi nhập học
Nên củng cố tiếng Anh và toán trước năm nhất. Chọn đề tài đồ án gắn với một người dùng cụ thể để portafolio có bằng chứng làm được việc. Thực tập nên xin sớm, dù vị trí còn nhỏ, vì kinh nghiệm dự án thật thường quyết định mức lương năm đầu hơn điểm tổng kết.`

const SAMPLE_MUC_LUONG = [
  { name: 'Thực tập', min: '3', max: '6', unit: 'VND', period: 'thang' },
  { name: 'Mới ra trường', min: '8', max: '12', unit: 'VND', period: 'thang' },
  { name: 'Dưới 1 năm', min: '10', max: '15', unit: 'VND', period: 'thang' },
  { name: '1–2 năm', min: '15', max: '22', unit: 'VND', period: 'thang' },
  { name: '2–3 năm', min: '20', max: '30', unit: 'VND', period: 'thang' },
  { name: '3–5 năm', min: '28', max: '45', unit: 'VND', period: 'thang' },
  { name: '5–8 năm', min: '40', max: '70', unit: 'VND', period: 'thang' },
  { name: 'Trên 8 năm', min: '60', max: '99', unit: 'VND', period: 'thang' },
]

const SAMPLE_MO_TA_CONG_VIEC = [
  {
    name: 'Phân tích yêu cầu',
    value:
      'Làm việc với người dùng và phân tích nghiệp vụ để viết lại bài toán bằng ngôn ngữ rõ: ai dùng, dữ liệu vào ra, quy tắc và ngoại lệ. Chốt phạm vi trước khi ước lượng và lập trình.',
    ghi_chu: 'Ưu tiên các luồng chính, ghi lại giả định còn mở',
  },
  {
    name: 'Thiết kế giải pháp',
    value:
      'Phác thảo luồng màn hình, cấu trúc mô-đun và lược đồ dữ liệu. Chọn cách lưu trữ, phân quyền và điểm tích hợp với hệ thống có sẵn để nhóm triển khai thống nhất.',
    ghi_chu: 'Vẽ sơ đồ ngắn, tránh thiết kế quá sớm toàn bộ hệ thống',
  },
  {
    name: 'Lập trình tính năng',
    value:
      'Viết mã cho giao diện, dịch vụ và truy cập dữ liệu theo đặc tả đã chốt. Tách hàm nhỏ, đặt tên dễ đọc và xử lý lỗi có thông báo người dùng hiểu được.',
    ghi_chu: 'Mỗi lần chỉ một tính năng, có tiêu chí xong việc',
  },
  {
    name: 'Kiểm thử và sửa lỗi',
    value:
      'Viết ca kiểm thử cho đường đúng và đường sai, chạy lại sau mỗi sửa đổi. Ghi lại bước tái hiện lỗi, nguyên nhân và cách khắc phục để người sau không gặp lại.',
    ghi_chu: 'Lỗi dữ liệu biên và phân quyền cần được kiểm tra riêng',
  },
  {
    name: 'Quản lý mã nguồn',
    value:
      'Đưa thay đổi lên nhánh riêng, mô tả nội dung commit và tạo yêu cầu xem lại. Phản hồi nhận xét của đồng nghiệp rồi mới hợp nhất vào nhánh chính.',
    ghi_chu: 'Không đẩy bí mật, khóa hay tệp cấu hình nội bộ',
  },
  {
    name: 'Làm việc nhóm',
    value:
      'Họp ngắn để đồng bộ việc đang kẹt, cập nhật bảng công việc và hỗ trợ thành viên khi tắc ở môi trường hoặc dữ liệu mẫu. Giữ thái độ cụ thể khi góp ý mã.',
    ghi_chu: 'Báo sớm nếu trễ hạn thay vì đợi đến ngày demo',
  },
  {
    name: 'Tài liệu và bàn giao',
    value:
      'Viết hướng dẫn cài đặt, mô tả API và cách vận hành các tác vụ định kỳ. Tài liệu đủ để người mới chạy được hệ thống mà không phải hỏi lại từng lệnh.',
    ghi_chu: 'Cập nhật tài liệu cùng lúc với mã, không để cuối dự án',
  },
  {
    name: 'Vận hành và cải tiến',
    value:
      'Theo dõi lỗi trên môi trường thật, xử lý sự cố theo mức ưu tiên và đề xuất cải thiện hiệu năng hoặc trải nghiệm sau khi có số liệu sử dụng.',
    ghi_chu: 'Chỉ tối ưu đoạn thực sự chậm hoặc hay lỗi',
  },
]

const SAMPLE_LO_TRINH = [
  {
    name: 'Năm 1',
    value:
      'Học nhập môn lập trình, toán rời rạc và cách máy tính biểu diễn dữ liệu. Làm các bài tập nhỏ đến chương trình hoàn chỉnh một chức năng, tập thói quen đọc lỗi và sửa từng bước.',
    ghi_chu: 'Nên luyện gõ mã mỗi tuần, chưa cần công nghệ mới',
  },
  {
    name: 'Năm 2',
    value:
      'Học cấu trúc dữ liệu, cơ sở dữ liệu và lập trình hướng đối tượng. Bắt đầu làm ứng dụng có nhiều màn hình, biết tách giao diện, xử lý nghiệp vụ và lưu trữ.',
    ghi_chu: 'Làm một dự án cá nhân để giữ mạch thực hành',
  },
  {
    name: 'Năm 3',
    value:
      'Đi vào chuyên ngành như web, di động hoặc dữ liệu. Tham gia đồ án nhóm, thực tập ngắn và học quy trình: yêu cầu, thiết kế, mã, kiểm thử, trình bày.',
    ghi_chu: 'Xin thực tập sớm dù vị trí còn hỗ trợ',
  },
  {
    name: 'Năm 4',
    value:
      'Hoàn thành đồ án tốt nghiệp gắn với bài toán có người dùng. Hoàn thiện hồ sơ năng lực: mã nguồn, mô tả việc đã làm và kết quả đo được.',
    ghi_chu: 'Chọn đề tài đủ nhỏ để làm xong và demo được',
  },
  {
    name: '0–2 năm đi làm',
    value:
      'Đảm nhận tính năng nhỏ trong sản phẩm có sẵn, sửa lỗi và học quy ước của nhóm. Mục tiêu là giao việc đúng hạn, hỏi đúng chỗ và để lại mã người khác đọc được.',
    ghi_chu: 'Cấp độ lập trình viên mới',
  },
  {
    name: '2–4 năm',
    value:
      'Tự nhận một phân hệ, ước lượng công việc và hướng dẫn thực tập sinh. Bắt đầu chọn hướng sâu: giao diện, máy chủ, dữ liệu hoặc vận hành.',
    ghi_chu: 'Cấp độ lập trình viên chính',
  },
  {
    name: '4–7 năm',
    value:
      'Chịu trách nhiệm chất lượng một mảng sản phẩm, đưa ra phương án kỹ thuật và xử lý sự cố khó. Tham gia phỏng vấn và xây dựng quy ước mã của nhóm.',
    ghi_chu: 'Có thể hướng tới trưởng nhóm kỹ thuật',
  },
  {
    name: 'Sau 7 năm',
    value:
      'Làm kiến trúc sư giải pháp hoặc quản lý nhóm kỹ thuật: cân bằng chi phí, rủi ro và tốc độ giao hàng. Vẫn giữ thời gian đọc mã và thử nghiệm công nghệ trước khi áp dụng rộng.',
    ghi_chu: 'Nhánh quản lý hoặc nhánh chuyên gia đều hợp lệ',
  },
]

function fillFormSample() {
  if (!editingId.value) {
    const nhom = nhomOptions.value.find((item) => item.trang_thai === 1) || nhomOptions.value[0]
    if (nhom) form.ma_nhom_nganh = nhom.ma_nhom_nganh
    form.ten_nganh = 'Công nghệ thông tin'
    form.ma_nganh = '7480201'
    form.ten_tieng_anh = 'Information Technology'
    form.trinh_do = 'Đại học'
    form.ma_holand = hollandOptions.value
      .filter((item) => item.trang_thai === 1)
      .slice(0, 2)
      .map((item) => item.ma_nhom)
    form.nhan_dan = 'Nhu cầu cao'
    form.thoi_gian_dao_tao = '4 năm'
    form.hinh_anh_mo_ta = 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=1200&q=80'
    form.trang_thai = 1
  }

  form.mo_ta = SAMPLE_MO_TA
  form.chi_tiet = SAMPLE_CHI_TIET
  form.muc_luong_tham_khao = SAMPLE_MUC_LUONG.map((item) => ({ ...item }))
  form.mo_ta_cong_viec = SAMPLE_MO_TA_CONG_VIEC.map((item) => ({ ...item }))
  form.lo_trinh_phat_trien = SAMPLE_LO_TRINH.map((item) => ({ ...item }))
  formRef.value?.clearValidate()
  ElMessage.success('Đã điền dữ liệu mẫu')
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
    createBatch: createNganhBulk,
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

  let payload
  try {
    payload = payloadFromForm()
  } catch (error) {
    ElMessage.error(error.message)
    return
  }

  saving.value = true
  try {
    if (editingId.value) {
      await updateNganh(editingId.value, payload)
      ElMessage.success('Đã cập nhật ngành')
    } else {
      await createNganh(payload)
      ElMessage.success('Đã thêm ngành')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được ngành'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`Xóa ngành "${row.ten_nganh}" (${row.ma_nganh})?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  try {
    await deleteNganh(row.id)
    ElMessage.success('Đã xóa ngành')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được ngành'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} ngành đã chọn?`, 'Xác nhận xóa', {
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
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteNganhMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} ngành`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các ngành đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadOptions().catch(() => {})])
})
</script>

<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="filters">
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm tên, mã, trình độ hoặc Holland"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.ma_nhom_nganh"
          class="filter-parent"
          placeholder="Nhóm ngành"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in nhomOptions"
            :key="item.id"
            :label="parentLabel(item)"
            :value="item.ma_nhom_nganh"
          />
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
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách ngành đào tạo</h2>
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
            Thêm ngành
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
        <CustomTableColumn prop="ma_nganh" label="Mã" width="130" />
        <CustomTableColumn prop="ten_nganh" label="Tên ngành" min-width="200" />
        <CustomTableColumn label="Nhóm ngành" min-width="200">
          <template #default="{ row }">{{ row.ma_nhom_nganh }} · {{ row.ten_nhom_nganh }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_tieng_anh" label="Tên tiếng Anh" min-width="180" />
        <CustomTableColumn prop="trinh_do" label="Trình độ" width="130" />
        <CustomTableColumn label="Nhãn dán" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.nhan_dan || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thời gian đào tạo" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.thoi_gian_dao_tao || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mức lương tham khảo" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ noiMucLuong(row.muc_luong_tham_khao, ' · ') || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mô tả công việc" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ noiCap(row.mo_ta_cong_viec, ' · ') || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Lộ trình phát triển" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ noiCap(row.lo_trinh_phat_trien, ' · ') || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mã Holland" min-width="140">
          <template #default="{ row }">
            {{ row.ma_holand?.length ? row.ma_holand.join(', ') : '—' }}
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Trạng thái" width="150" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
              {{ row.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="mo_ta" label="Mô tả" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.mo_ta || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Hình ảnh mô tả" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.hinh_anh_mo_ta || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="chi_tiet" label="Chi tiết" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ row.chi_tiet || '—' }}</template>
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
          <CustomEmpty description="Chưa có ngành đào tạo nào." />
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
    class="nganh-form-dialog"
    :title="editingId ? 'Cập nhật ngành' : 'Thêm ngành'"
    width="1400px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomRadioGroup v-if="!editingId" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!editingId && createMode === 'json'" class="json-panel">
      <div class="json-panel__head">
        <p>
          Dán một mảng JSON. Mỗi phần tử cần <code>ma_nhom_nganh</code>, <code>ten_nganh</code>,
          <code>ma_nganh</code>, <code>ten_tieng_anh</code> và <code>trinh_do</code>.
          <code>ma_holand</code> là mảng mã, ví dụ <code>["R", "I"]</code>.
          <code>hinh_anh_mo_ta</code>, <code>nhan_dan</code>, <code>thoi_gian_dao_tao</code> và
          <code>chi_tiet</code> có thể bỏ trống.
          <code>muc_luong_tham_khao</code> là mảng
          <code>{"name","min","max","unit","period"}</code>: min và max là số không âm, không giới hạn,
          unit thuộc VNĐ, USD hoặc EUR, period là buổi, ngày, tuần, tháng hoặc năm (mặc định tháng).
          <code>mo_ta_cong_viec</code> và <code>lo_trinh_phat_trien</code> là mảng
          <code>{"name","value","ghi_chu"}</code>, ghi chú có thể bỏ trống. Các mảng này có thể bỏ trống.
        </p>
        <CustomButton text type="primary" @click="fillJsonSample">Điền mẫu</CustomButton>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        placeholder="Dán mảng JSON vào đây"
      />
    </div>

    <CustomForm v-else ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Nhóm ngành" prop="ma_nhom_nganh">
            <CustomSelect
              v-model="form.ma_nhom_nganh"
              filterable
              placeholder="Chọn nhóm ngành"
              style="width: 100%"
              :disabled="!nhomOptions.length"
            >
              <CustomOption
                v-for="item in nhomOptions"
                :key="item.id"
                :label="parentLabel(item)"
                :value="item.ma_nhom_nganh"
              />
            </CustomSelect>
            <p v-if="!nhomOptions.length" class="field-hint">
              Chưa có nhóm ngành. Hãy thêm ở danh mục Nhóm ngành trước.
            </p>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Tên ngành" prop="ten_nganh">
            <CustomInput v-model="form.ten_nganh" maxlength="255" placeholder="Ví dụ: Công nghệ thông tin" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Mã ngành" prop="ma_nganh">
            <CustomInput v-model="form.ma_nganh" maxlength="20" placeholder="Ví dụ: 7480201" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Tên tiếng Anh" prop="ten_tieng_anh">
            <CustomInput
              v-model="form.ten_tieng_anh"
              maxlength="255"
              placeholder="Ví dụ: Information technology"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Trình độ" prop="trinh_do">
            <CustomSelect
              v-model="form.trinh_do"
              filterable
              allow-create
              default-first-option
              placeholder="Chọn hoặc nhập trình độ"
              style="width: 100%"
            >
              <CustomOption v-for="item in trinhDoOptions" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Mã Holland" prop="ma_holand">
            <CustomSelect
              v-model="form.ma_holand"
              multiple
              filterable
              clearable
              placeholder="Chọn mã, có thể bỏ trống"
              style="width: 100%"
              :disabled="!hollandSelectOptions.length"
            >
              <CustomOption
                v-for="item in hollandSelectOptions"
                :key="item.ma_nhom"
                :label="hollandLabel(item)"
                :value="item.ma_nhom"
              />
            </CustomSelect>
            <p v-if="!hollandOptions.length" class="field-hint">
              Chưa có nhóm Holland. Có thể để trống, hoặc thêm ở danh mục Nhóm Holland trước.
            </p>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" :clearable="false" style="width: 100%">
              <CustomOption label="Hoạt động" :value="1" />
              <CustomOption label="Ngừng sử dụng" :value="0" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Nhãn dán" prop="nhan_dan">
            <CustomInput v-model="form.nhan_dan" maxlength="100" placeholder="Ví dụ: Nhu cầu cao" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Thời gian đào tạo" prop="thoi_gian_dao_tao">
            <CustomInput v-model="form.thoi_gian_dao_tao" maxlength="100" placeholder="Ví dụ: 4 năm" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="4" :xs="12">
          <CustomFormItem label="Hình ảnh mô tả" prop="hinh_anh_mo_ta">
            <CustomInput
              v-model="form.hinh_anh_mo_ta"
              maxlength="500"
              placeholder="URL hình ảnh mô tả ngành"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
          <CustomFormItem label="Mô tả" prop="mo_ta">
            <CustomInput
              v-model="form.mo_ta"
              type="textarea"
              :rows="3"
              maxlength="5000"
              show-word-limit
              placeholder="Mô tả ngành (nếu có)"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="12">
          <CustomFormItem label="Chi tiết" prop="chi_tiet">
            <CustomInput
              v-model="form.chi_tiet"
              type="textarea"
              :rows="3"
              maxlength="10000"
              show-word-limit
              placeholder="Chi tiết ngành (nếu có)"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Mức lương tham khảo" prop="muc_luong_tham_khao">
            <BangMucLuong v-model="form.muc_luong_tham_khao" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Mô tả công việc" prop="mo_ta_cong_viec">
            <BangTenGiaTri
              v-model="form.mo_ta_cong_viec"
              name-label="Hạng mục"
              value-label="Mô tả"
              name-placeholder="Ví dụ: Nhiệm vụ chính"
              value-placeholder="Mô tả ngắn công việc"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Lộ trình phát triển" prop="lo_trinh_phat_trien">
            <BangTenGiaTri
              v-model="form.lo_trinh_phat_trien"
              name-label="Giai đoạn"
              value-label="Nội dung"
              name-placeholder="Ví dụ: Năm 1-2"
              value-placeholder="Ví dụ: Thực tập, lập trình viên mới"
            />
          </CustomFormItem>
        </CustomCol>
      </CustomRow>
    </CustomForm>
    <template #footer>
      <JsonImportDialogFooter
        :batch="jsonImport"
        :saving="saving"
        :show-progress="!editingId && createMode === 'json'"
        @cancel="dialogVisible = false"
        @save="onSubmit"
      >
        <CustomButton
          v-if="editingId || createMode === 'form'"
          :disabled="saving"
          @click="fillFormSample"
        >
          Điền dữ liệu mẫu
        </CustomButton>
      </JsonImportDialogFooter>
    </template>
  </CustomDialog>
</template>

<style scoped>
.catalog-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.catalog-card {
  border-radius: 12px;
}

.filters,
.toolbar__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar__title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.row-actions :deep(.el-icon) {
  font-size: 20px !important;
}

.row-actions :deep(.el-icon svg) {
  stroke: currentColor;
  stroke-width: 1.15;
  stroke-linejoin: round;
  paint-order: stroke fill;
}

.filter-search {
  width: 280px;
}

.filter-parent {
  width: 280px;
}

.create-mode {
  margin-bottom: 16px;
}

.json-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.json-panel__head p {
  margin: 0;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.json-input :deep(textarea) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: var(--app-font-size);
  font-weight: 400;
}

.field-hint {
  margin: 6px 0 0;
  color: var(--el-text-color-secondary);
  font-size: var(--app-font-size);
  font-weight: 400;
  line-height: 1.4;
}

.nganh-form-dialog {
  --el-dialog-content-font-size: var(--app-font-size);
  --el-dialog-title-font-size: var(--app-font-size);
  --el-font-weight-primary: 400;
  font-weight: 400;
}

.nganh-form-dialog :deep(.el-form-item) {
  --font-size: var(--app-font-size);
  --el-form-label-font-size: var(--app-font-size);
}

.nganh-form-dialog :deep(.el-dialog__title),
.nganh-form-dialog :deep(.el-dialog__body),
.nganh-form-dialog :deep(.el-form-item__label),
.nganh-form-dialog :deep(.el-form-item__content),
.nganh-form-dialog :deep(.el-input__wrapper),
.nganh-form-dialog :deep(.el-textarea__inner),
.nganh-form-dialog :deep(.el-select__wrapper),
.nganh-form-dialog :deep(.el-radio-button__inner),
.nganh-form-dialog :deep(.el-button),
.nganh-form-dialog :deep(.cap-table),
.nganh-form-dialog :deep(.cap-table th),
.nganh-form-dialog :deep(.cap-table__empty) {
  font-size: var(--app-font-size);
  font-weight: 400;
}

.filter-status {
  width: 170px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 640px) {
  .filter-search,
  .filter-parent,
  .filter-status {
    width: 100%;
  }
}
</style>
