<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchBaiThiDanhGiaNangLuc } from '@/api/baiThiDanhGiaNangLuc'
import { fetchChungChiNgoaiNgu } from '@/api/chungChiNgoaiNgu'
import { fetchDanToc } from '@/api/danToc'
import { fetchDoiTuongUuTien } from '@/api/doiTuongUuTien'
import { fetchHoSo, updateHoSo } from '@/api/hoSo'
import { storeHoSo } from '@/utils/hoSoCache'
import { fetchKhuVucUuTien } from '@/api/khuVucUuTien'
import { fetchMonHoc } from '@/api/monHoc'
import { fetchThanhTichHocTapNghienCuu } from '@/api/thanhTichHocTapNghienCuu'
import { fetchTinhThanh } from '@/api/tinhThanh'
import { fetchTonGiao } from '@/api/tonGiao'
import { useAuthStore } from '@/stores/auth'

const GRADES = ['10', '11', '12']
const HANH_KIEM = ['Tốt', 'Khá', 'Trung bình', 'Yếu']
const GIOI_TINH = [
  { value: 1, label: 'Nam' },
  { value: 2, label: 'Nữ' },
  { value: 3, label: 'Khác' },
]
const RECORD_SECTIONS = [
  {
    key: 'chung_chi_ngoai_ngu',
    title: 'Chứng chỉ ngoại ngữ',
    lead: 'Chọn chứng chỉ trong danh mục, điểm đạt được và thời gian cấp.',
    maKey: 'ma_chung_chi',
    tenKey: 'ten_chung_chi',
  },
  {
    key: 'bai_thi_danh_gia_nang_luc',
    title: 'Bài thi đánh giá năng lực',
    lead: 'Chọn bài thi trong danh mục, điểm đạt được và thời gian cấp.',
    maKey: 'ma_bai_thi',
    tenKey: 'ten_bai_thi',
  },
  {
    key: 'thanh_tich_hoc_tap_nghien_cuu',
    title: 'Thành tích học tập, nghiên cứu',
    lead: 'Chọn thành tích trong danh mục, kết quả đạt được và thời gian cấp.',
    maKey: 'ma_thanh_tich',
    tenKey: 'ten_thanh_tich',
  },
]

const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)
const email = ref('')
const provinceOptions = ref([])
const ethnicOptions = ref([])
const religionOptions = ref([])
const khuVucRows = ref([])
const doiTuongRows = ref([])
const catalogRows = reactive({
  chung_chi_ngoai_ngu: [],
  bai_thi_danh_gia_nang_luc: [],
  thanh_tich_hoc_tap_nghien_cuu: [],
})
const subjects = ref([])
let recordSeq = 0

function blankRecord() {
  recordSeq += 1
  return {
    _key: recordSeq,
    ma: null,
    thanh_tich: '',
    thoi_gian_cap: '',
    editing: true,
  }
}

const recordGroups = reactive(
  Object.fromEntries(RECORD_SECTIONS.map((section) => [section.key, [blankRecord()]])),
)
const openSections = ref([
  'ca-nhan',
  'hoc-ba',
  'thi-thpt',
  'suc-khoe',
  ...RECORD_SECTIONS.map((section) => section.key),
])

const form = reactive({
  ho_ten: '',
  so_dien_thoai: '',
  gioi_tinh: null,
  ngay_sinh: '',
  dan_toc: null,
  ton_giao: null,
  tinh_thanh_id: null,
  khu_vuc_uu_tien_id: null,
  doi_tuong_uu_tien_id: null,
})
const hocBa = reactive({ 10: {}, 11: {}, 12: {} })
const hocLucTb = reactive({ 10: null, 11: null, 12: null })
const hanhKiem = reactive({ 10: null, 11: null, 12: null })
const diemDuKien = reactive({})
const sucKhoe = reactive({
  chieu_cao: null,
  can_nang: null,
  tien_su_benh: '',
})

const rules = {
  ho_ten: [
    { required: true, message: 'Vui lòng nhập họ tên', trigger: 'blur' },
    { min: 2, message: 'Họ tên phải có ít nhất 2 ký tự', trigger: 'blur' },
  ],
  so_dien_thoai: [
    {
      validator: (_rule, value, callback) => {
        if (!value) return callback()
        if (!/^[0-9+\-\s]{8,20}$/.test(value)) {
          return callback(new Error('Số điện thoại không hợp lệ'))
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
}

function withCurrent(options, current) {
  const value = String(current || '').trim()
  if (!value || options.includes(value)) return options
  return [value, ...options]
}

const ethnicSelectOptions = computed(() => withCurrent(ethnicOptions.value, form.dan_toc))
const religionSelectOptions = computed(() => withCurrent(religionOptions.value, form.ton_giao))
const khuVucSelectOptions = computed(() =>
  khuVucRows.value
    .filter((item) => item.trang_thai === 1 || item.id === form.khu_vuc_uu_tien_id)
    .sort((a, b) => a.ten_khu_vuc.localeCompare(b.ten_khu_vuc, 'vi'))
    .map((item) => ({ id: item.id, label: `${item.ten_khu_vuc} (${item.ma_khu_vuc})` })),
)
const doiTuongSelectOptions = computed(() =>
  doiTuongRows.value
    .filter((item) => item.trang_thai === 1 || item.id === form.doi_tuong_uu_tien_id)
    .sort((a, b) => a.ten_doi_tuong.localeCompare(b.ten_doi_tuong, 'vi'))
    .map((item) => ({ id: item.id, label: `${item.ten_doi_tuong} (${item.ma_doi_tuong})` })),
)
const recordSections = computed(() =>
  RECORD_SECTIONS.map((section) => {
    const rows = recordGroups[section.key]
    const selected = new Set(rows.map((row) => row.ma).filter(Boolean))
    const options = catalogRows[section.key]
      .filter((item) => item.trang_thai === 1 || selected.has(item[section.maKey]))
      .sort((a, b) => a[section.tenKey].localeCompare(b[section.tenKey], 'vi'))
      .map((item) => ({
        ma: item[section.maKey],
        label: `${item[section.tenKey]} (${item[section.maKey]})`,
      }))
    const known = new Set(options.map((item) => item.ma))
    for (const code of selected) {
      if (!known.has(code)) options.push({ ma: code, label: code })
    }
    return { ...section, options }
  }),
)

function blank(value) {
  const text = String(value ?? '').trim()
  return text || null
}

function lookupScale(sectionKey, ma) {
  if (!ma) return ''
  const section = RECORD_SECTIONS.find((item) => item.key === sectionKey)
  const row = catalogRows[sectionKey].find((item) => item[section.maKey] === ma)
  return String(row?.thang_diem || '').trim()
}

function exampleInRange(min, max) {
  const decimal = max <= 10
  const target = min + (max - min) * 0.75
  const value = decimal
    ? Math.min(max, Math.max(min, Math.round(target * 2) / 2))
    : Math.min(max, Math.max(min, Math.round(target)))
  return decimal ? value.toFixed(1) : String(value)
}

function hintFromScale(scale) {
  const range = scale.match(/(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)/)
  if (range) {
    const min = Number(range[1].replace(',', '.'))
    const max = Number(range[2].replace(',', '.'))
    if (Number.isFinite(min) && Number.isFinite(max) && max > min) {
      const note = scale.match(/\(([^)]+)\)/)
      const suffix = note && note[1].length <= 24 ? ` (${note[1]})` : ''
      return `Thang ${range[1].replace(',', '.')}–${range[2].replace(',', '.')}${suffix}, ví dụ ${exampleInRange(min, max)}`
    }
  }

  const parts = scale.split(/\s+[-–]\s+/).map((part) => part.trim()).filter(Boolean)
  if (parts.length > 1 && parts.every((part) => part.length <= 24)) {
    const list = parts.join(', ')
    return list.length <= 60 ? list : `Ví dụ: ${parts[0]}`
  }

  if (scale.length <= 28) return `Ví dụ: ${scale}`
  return scale
}

function scorePlaceholder(sectionKey, ma) {
  if (!ma) return 'Chọn nội dung trước'
  const scale = lookupScale(sectionKey, ma)
  if (!scale) return 'Điểm đạt được'
  const hint = hintFromScale(scale)
  return hint.length <= 60 ? hint : `${hint.slice(0, 57)}…`
}

function scoreTitle(sectionKey, ma) {
  return lookupScale(sectionKey, ma) || undefined
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function disableFutureDate(value) {
  const today = new Date()
  today.setHours(23, 59, 59, 999)
  return value.getTime() > today.getTime()
}

function readScore(value) {
  if (value == null || value === '') return null
  const score = Number(value)
  return Number.isFinite(score) ? score : null
}

function gradeScores(block) {
  if (!block || typeof block !== 'object') return {}
  if (block.hoc_luc && typeof block.hoc_luc === 'object') return block.hoc_luc
  return block
}

function readConduct(value) {
  const text = String(value ?? '').trim()
  return HANH_KIEM.includes(text) ? text : null
}

function collectSavedCodes(hocVan) {
  const codes = new Set()
  const hocBaSaved = hocVan?.diem_trung_binh_hoc_ba || {}
  for (const grade of GRADES) {
    Object.keys(gradeScores(hocBaSaved[grade])).forEach((code) => codes.add(code))
  }
  const exam = hocVan?.diem_thi_thpt_quoc_gia?.du_kien || {}
  Object.keys(exam).forEach((code) => codes.add(code))
  return codes
}

function mergeSubjects(catalog, hocVan) {
  const savedCodes = collectSavedCodes(hocVan)
  const map = new Map()
  for (const item of catalog) {
    if (item.trang_thai === 1 || savedCodes.has(item.ma_mon_hoc)) {
      map.set(item.ma_mon_hoc, item)
    }
  }
  for (const code of savedCodes) {
    if (!map.has(code)) {
      map.set(code, { ma_mon_hoc: code, ten_mon_hoc: code, trang_thai: 1 })
    }
  }
  return [...map.values()].sort((a, b) => a.ten_mon_hoc.localeCompare(b.ten_mon_hoc, 'vi'))
}

function resetScores() {
  for (const grade of GRADES) {
    hocBa[grade] = {}
    hocLucTb[grade] = null
    hanhKiem[grade] = null
  }
  for (const code of Object.keys(diemDuKien)) delete diemDuKien[code]
}

function applyScores(hocVan) {
  resetScores()
  const hocBaSaved = hocVan?.diem_trung_binh_hoc_ba || {}
  const averages = hocVan?.hoc_luc_trung_binh || {}
  const conduct = hocVan?.hanh_kiem || {}
  const exam = hocVan?.diem_thi_thpt_quoc_gia || {}
  const health = hocVan?.suc_khoe_the_chat || {}
  for (const grade of GRADES) {
    hocLucTb[grade] = readScore(averages[grade])
    hanhKiem[grade] = readConduct(conduct[grade])
  }
  for (const subject of subjects.value) {
    const code = subject.ma_mon_hoc
    for (const grade of GRADES) {
      hocBa[grade][code] = readScore(gradeScores(hocBaSaved[grade])[code])
    }
    diemDuKien[code] = readScore(exam.du_kien?.[code])
  }
  sucKhoe.chieu_cao = health.chieu_cao ?? null
  sucKhoe.can_nang = health.can_nang ?? null
  sucKhoe.tien_su_benh = health.tien_su_benh || ''
}

function applyRecordGroups(hocVan) {
  for (const section of RECORD_SECTIONS) {
    const saved = Array.isArray(hocVan?.[section.key]) ? hocVan[section.key] : []
    if (!saved.length) {
      recordGroups[section.key] = [blankRecord()]
      continue
    }
    recordGroups[section.key] = saved.map((item) => {
      const row = blankRecord()
      row.ma = item.ma || null
      row.thanh_tich = item.thanh_tich || ''
      row.thoi_gian_cap = item.thoi_gian_cap || ''
      row.editing = false
      return row
    })
  }
}

function addRecord(key) {
  recordGroups[key].push(blankRecord())
}

function removeRecord(key, index) {
  recordGroups[key].splice(index, 1)
  if (!recordGroups[key].length) recordGroups[key].push(blankRecord())
}

function canRemove(key, row) {
  if (recordGroups[key].length > 1) return true
  return Boolean(blank(row.ma) || blank(row.thanh_tich) || row.thoi_gian_cap)
}

function collectRecords() {
  const payload = {}
  for (const section of RECORD_SECTIONS) {
    const items = []
    for (const row of recordGroups[section.key]) {
      const ma = blank(row.ma)
      const thanhTich = blank(row.thanh_tich)
      const issued = row.thoi_gian_cap || null
      if (!ma && !thanhTich && !issued) continue
      if (!ma) return { error: `Chọn nội dung ở mục ${section.title}`, section: section.key }
      items.push({ ma: ma.toUpperCase(), thanh_tich: thanhTich, thoi_gian_cap: issued })
    }
    if (items.length) payload[section.key] = items
  }
  return { payload }
}

function scoreMap(source, codes) {
  const data = {}
  for (const code of codes) {
    const score = readScore(source[code])
    if (score == null) continue
    data[code] = score
  }
  return Object.keys(data).length ? data : null
}

function buildTrinhDoHocVan() {
  const codes = subjects.value.map((item) => item.ma_mon_hoc)
  const hocBaPayload = {}
  const averagePayload = {}
  const conductPayload = {}
  for (const grade of GRADES) {
    const scores = scoreMap(hocBa[grade], codes)
    if (scores) hocBaPayload[grade] = scores
    const average = readScore(hocLucTb[grade])
    if (average != null) averagePayload[grade] = average
    const conduct = readConduct(hanhKiem[grade])
    if (conduct) conductPayload[grade] = conduct
  }
  const duKien = scoreMap(diemDuKien, codes)
  const health = {}
  if (sucKhoe.chieu_cao != null && sucKhoe.chieu_cao !== '') health.chieu_cao = sucKhoe.chieu_cao
  if (sucKhoe.can_nang != null && sucKhoe.can_nang !== '') health.can_nang = sucKhoe.can_nang
  const tienSu = blank(sucKhoe.tien_su_benh)
  if (tienSu) health.tien_su_benh = tienSu

  const payload = {}
  if (Object.keys(hocBaPayload).length) payload.diem_trung_binh_hoc_ba = hocBaPayload
  if (Object.keys(averagePayload).length) payload.hoc_luc_trung_binh = averagePayload
  if (Object.keys(conductPayload).length) payload.hanh_kiem = conductPayload
  if (duKien) payload.diem_thi_thpt_quoc_gia = { du_kien: duKien }
  if (Object.keys(health).length) payload.suc_khoe_the_chat = health
  const records = collectRecords()
  if (records.error) return records
  Object.assign(payload, records.payload)
  return { payload: Object.keys(payload).length ? payload : null }
}

async function loadAll(fetchFn) {
  const size = 100
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchFn({ page: current, page_size: size })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  return items
}

function applyProfile(data) {
  email.value = data.email || ''
  form.ho_ten = data.ho_ten || ''
  form.so_dien_thoai = data.so_dien_thoai || ''
  form.gioi_tinh = data.gioi_tinh ?? null
  form.ngay_sinh = data.ngay_sinh || ''
  form.dan_toc = data.dan_toc || null
  form.ton_giao = data.ton_giao || null
  form.tinh_thanh_id = data.tinh_thanh_id ?? null
  form.khu_vuc_uu_tien_id = data.khu_vuc_uu_tien_id ?? null
  form.doi_tuong_uu_tien_id = data.doi_tuong_uu_tien_id ?? null
  applyScores(data.trinh_do_hoc_van)
  applyRecordGroups(data.trinh_do_hoc_van)
}

function syncAuthUser(data) {
  if (!auth.user) return
  auth.setUser({
    ...auth.user,
    ho_ten: data.ho_ten,
    so_dien_thoai: data.so_dien_thoai,
  })
}

async function load() {
  loading.value = true
  try {
    const [profile, provinces, ethnics, religions, subjectRows, areas, priorities, certificates, exams, achievements] =
      await Promise.all([
        fetchHoSo(),
        loadAll(fetchTinhThanh),
        loadAll(fetchDanToc),
        loadAll(fetchTonGiao),
        loadAll(fetchMonHoc),
        loadAll(fetchKhuVucUuTien),
        loadAll(fetchDoiTuongUuTien),
        loadAll(fetchChungChiNgoaiNgu),
        loadAll(fetchBaiThiDanhGiaNangLuc),
        loadAll(fetchThanhTichHocTapNghienCuu),
      ])
    subjects.value = mergeSubjects(subjectRows, profile.trinh_do_hoc_van)
    provinceOptions.value = provinces
      .filter((item) => item.trang_thai === 1 || item.id === profile.tinh_thanh_id)
      .sort((a, b) => a.ten_tinh.localeCompare(b.ten_tinh, 'vi'))
    ethnicOptions.value = ethnics
      .filter((item) => item.trang_thai === 1)
      .map((item) => item.ten_dan_toc)
      .sort((a, b) => a.localeCompare(b, 'vi'))
    religionOptions.value = religions
      .filter((item) => item.trang_thai === 1)
      .map((item) => item.ten_ton_giao)
      .sort((a, b) => a.localeCompare(b, 'vi'))
    khuVucRows.value = areas
    doiTuongRows.value = priorities
    catalogRows.chung_chi_ngoai_ngu = certificates
    catalogRows.bai_thi_danh_gia_nang_luc = exams
    catalogRows.thanh_tich_hoc_tap_nghien_cuu = achievements
    applyProfile(profile)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được hồ sơ'))
  } finally {
    loading.value = false
  }
}

function fillSample() {
  form.ho_ten = 'Nguyễn Văn An'
  form.so_dien_thoai = '0912345678'
  form.gioi_tinh = 2
  form.ngay_sinh = '2008-03-15'
  const province = provinceOptions.value.find((item) => item.ten_tinh === 'Hà Nội') || provinceOptions.value[0]
  form.tinh_thanh_id = province?.id ?? null
  form.dan_toc = ethnicOptions.value.includes('Kinh') ? 'Kinh' : ethnicOptions.value[0] || null
  form.ton_giao = religionOptions.value.find((item) => item.includes('Không')) || religionOptions.value[0] || null
  form.khu_vuc_uu_tien_id = khuVucSelectOptions.value[0]?.id ?? null
  form.doi_tuong_uu_tien_id = doiTuongSelectOptions.value[0]?.id ?? null

  GRADES.forEach((grade, gradeIndex) => {
    hocLucTb[grade] = Math.round((7.2 + gradeIndex * 0.3) * 10) / 10
    hanhKiem[grade] = HANH_KIEM[gradeIndex]
  })
  subjects.value.forEach((subject, index) => {
    const code = subject.ma_mon_hoc
    GRADES.forEach((grade, gradeIndex) => {
      hocBa[grade][code] = Math.round((6 + ((index * 2 + gradeIndex) % 9) * 0.4) * 10) / 10
    })
    diemDuKien[code] = Math.round((6.2 + (index % 8) * 0.4) * 10) / 10
  })
  sucKhoe.chieu_cao = 165
  sucKhoe.can_nang = 52
  sucKhoe.tien_su_benh = 'Không'
  for (const section of recordSections.value) {
    if (!section.options.length) {
      recordGroups[section.key] = [blankRecord()]
      continue
    }
    const row = blankRecord()
    row.ma = section.options[0].ma
    row.thanh_tich = section.key === 'thanh_tich_hoc_tap_nghien_cuu' ? 'Giải Nhất' : '8.0'
    row.thoi_gian_cap = '2025-06-15'
    recordGroups[section.key] = [row]
  }
  openSections.value = ['ca-nhan', 'hoc-ba', 'thi-thpt', 'suc-khoe', ...RECORD_SECTIONS.map((section) => section.key)]
  ElMessage.success('Đã điền dữ liệu mẫu')
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) {
    if (!openSections.value.includes('ca-nhan')) {
      openSections.value = [...openSections.value, 'ca-nhan']
    }
    return
  }

  const built = buildTrinhDoHocVan()
  if (built.error) {
    ElMessage.error(built.error)
    if (!openSections.value.includes(built.section)) {
      openSections.value = [...openSections.value, built.section]
    }
    return
  }

  saving.value = true
  try {
    const data = await updateHoSo({
      ho_ten: form.ho_ten.trim(),
      so_dien_thoai: blank(form.so_dien_thoai),
      gioi_tinh: form.gioi_tinh ?? null,
      ngay_sinh: form.ngay_sinh || null,
      dan_toc: blank(form.dan_toc),
      ton_giao: blank(form.ton_giao),
      tinh_thanh_id: form.tinh_thanh_id ?? null,
      khu_vuc_uu_tien_id: form.khu_vuc_uu_tien_id ?? null,
      doi_tuong_uu_tien_id: form.doi_tuong_uu_tien_id ?? null,
      trinh_do_hoc_van: built.payload,
    })
    subjects.value = mergeSubjects(
      subjects.value.map((item) => ({ ...item, trang_thai: item.trang_thai ?? 1 })),
      data.trinh_do_hoc_van,
    )
    applyProfile(data)
    syncAuthUser(data)
    if (auth.user?.id) storeHoSo(auth.user.id, data)
    ElMessage.success('Đã cập nhật thông tin cá nhân')
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được thông tin cá nhân'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <el-card v-loading="loading" shadow="never" class="profile-card">
    <template #header>
      <div>
        <h1 class="profile-card__title">Cập nhật thông tin cá nhân</h1>
        <p class="profile-card__lead">
          Thông tin này giúp hệ thống phân tích kết quả trắc nghiệm chính xác hơn.
        </p>
      </div>
    </template>

    <CustomForm ref="formRef" :model="form" :rules="rules" @submit.prevent="onSubmit">
      <el-collapse v-model="openSections" class="profile-collapse">
      <el-collapse-item name="ca-nhan" title="Thông tin cá nhân">
        <CustomRow :gutter="16">
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Họ tên" prop="ho_ten">
              <CustomInput v-model="form.ho_ten" maxlength="150" placeholder="Nguyễn Văn A" clearable />
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Email">
              <CustomInput :model-value="email" disabled />
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Số điện thoại" prop="so_dien_thoai">
              <CustomInput v-model="form.so_dien_thoai" maxlength="20" placeholder="Tùy chọn" clearable />
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Giới tính">
              <CustomSelect v-model="form.gioi_tinh" placeholder="Chọn" clearable>
                <CustomOption
                  v-for="item in GIOI_TINH"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </CustomSelect>
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Ngày sinh">
              <CustomDatePicker
                v-model="form.ngay_sinh"
                type="date"
                value-format="YYYY-MM-DD"
                format="DD/MM/YYYY"
                placeholder="Chọn ngày"
                clearable
                :disabled-date="disableFutureDate"
              />
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Tỉnh thành">
              <CustomSelect v-model="form.tinh_thanh_id" placeholder="Chọn" clearable filterable>
                <CustomOption
                  v-for="item in provinceOptions"
                  :key="item.id"
                  :label="item.ten_tinh"
                  :value="item.id"
                />
              </CustomSelect>
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Dân tộc">
              <CustomSelect
                v-model="form.dan_toc"
                placeholder="Chọn"
                clearable
                filterable
                allow-create
                default-first-option
              >
                <CustomOption v-for="item in ethnicSelectOptions" :key="item" :label="item" :value="item" />
              </CustomSelect>
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Tôn giáo">
              <CustomSelect
                v-model="form.ton_giao"
                placeholder="Chọn"
                clearable
                filterable
                allow-create
                default-first-option
              >
                <CustomOption v-for="item in religionSelectOptions" :key="item" :label="item" :value="item" />
              </CustomSelect>
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Khu vực ưu tiên">
              <CustomSelect v-model="form.khu_vuc_uu_tien_id" placeholder="Chọn" clearable filterable>
                <CustomOption
                  v-for="item in khuVucSelectOptions"
                  :key="item.id"
                  :label="item.label"
                  :value="item.id"
                />
              </CustomSelect>
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Đối tượng ưu tiên">
              <CustomSelect v-model="form.doi_tuong_uu_tien_id" placeholder="Chọn" clearable filterable>
                <CustomOption
                  v-for="item in doiTuongSelectOptions"
                  :key="item.id"
                  :label="item.label"
                  :value="item.id"
                />
              </CustomSelect>
            </CustomFormItem>
          </CustomCol>
        </CustomRow>
      </el-collapse-item>

      <el-collapse-item name="hoc-ba" title="Điểm trung bình học bạ">
        <p class="profile-section__lead">Học lực trung bình và hạnh kiểm của từng lớp. Học lực thang điểm 10.</p>
        <CustomRow :gutter="16">
          <CustomCol v-for="grade in GRADES" :key="`tb-${grade}`" :span="4" :xs="12">
            <CustomFormItem :label="`Học lực trung bình lớp ${grade}`">
              <CustomInputNumber
                v-model="hocLucTb[grade]"
                :min="0"
                :max="10"
                :step="0.1"
                :precision="2"
                :controls="false"
                :value-on-clear="null"
                placeholder="0–10"
              />
            </CustomFormItem>
          </CustomCol>
          <CustomCol v-for="grade in GRADES" :key="`hk-${grade}`" :span="4" :xs="12">
            <CustomFormItem :label="`Hạnh kiểm lớp ${grade}`">
              <CustomSelect v-model="hanhKiem[grade]" placeholder="Chọn">
                <CustomOption v-for="item in HANH_KIEM" :key="item" :label="item" :value="item" />
              </CustomSelect>
            </CustomFormItem>
          </CustomCol>
        </CustomRow>
        <p class="profile-section__lead">Điểm trung bình từng môn các lớp 10, 11 và 12, thang điểm 10.</p>
        <CustomTable v-if="openSections.includes('hoc-ba')" :data="subjects" row-key="ma_mon_hoc" class="score-table">
          <CustomTableColumn label="STT" width="72" align="center">
            <template #default="{ $index }">{{ $index + 1 }}</template>
          </CustomTableColumn>
          <CustomTableColumn prop="ma_mon_hoc" label="Mã môn" width="110" />
          <CustomTableColumn prop="ten_mon_hoc" label="Môn học" min-width="180" />
          <CustomTableColumn v-for="grade in GRADES" :key="grade" :label="`Lớp ${grade}`" min-width="120">
            <template #default="{ row }">
              <CustomInputNumber
                v-model="hocBa[grade][row.ma_mon_hoc]"
                :min="0"
                :max="10"
                :step="0.1"
                :precision="2"
                :controls="false"
                :value-on-clear="null"
                placeholder="0–10"
              />
            </template>
          </CustomTableColumn>
          <template #empty>Chưa có môn học trong danh mục.</template>
        </CustomTable>
      </el-collapse-item>

      <el-collapse-item name="thi-thpt" title="Điểm thi THPT Quốc gia">
        <p class="profile-section__lead">Điểm dự kiến theo từng môn, thang điểm 10.</p>
        <CustomTable v-if="openSections.includes('thi-thpt')" :data="subjects" row-key="ma_mon_hoc" class="score-table">
          <CustomTableColumn label="STT" width="72" align="center">
            <template #default="{ $index }">{{ $index + 1 }}</template>
          </CustomTableColumn>
          <CustomTableColumn prop="ma_mon_hoc" label="Mã môn" width="110" />
          <CustomTableColumn prop="ten_mon_hoc" label="Môn học" min-width="180" />
          <CustomTableColumn label="Điểm dự kiến" min-width="140">
            <template #default="{ row }">
              <CustomInputNumber
                v-model="diemDuKien[row.ma_mon_hoc]"
                :min="0"
                :max="10"
                :step="0.1"
                :precision="2"
                :controls="false"
                :value-on-clear="null"
                placeholder="0–10"
              />
            </template>
          </CustomTableColumn>
          <template #empty>Chưa có môn học trong danh mục.</template>
        </CustomTable>
      </el-collapse-item>

      <el-collapse-item name="suc-khoe" title="Sức khỏe thể chất">
        <CustomRow :gutter="16">
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Chiều cao (cm)">
              <CustomInputNumber
                v-model="sucKhoe.chieu_cao"
                :min="30"
                :max="250"
                :step="0.1"
                :precision="1"
                :controls="false"
                :value-on-clear="null"
                placeholder="cm"
              />
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="4" :xs="12">
            <CustomFormItem label="Cân nặng (kg)">
              <CustomInputNumber
                v-model="sucKhoe.can_nang"
                :min="5"
                :max="300"
                :step="0.1"
                :precision="1"
                :controls="false"
                :value-on-clear="null"
                placeholder="kg"
              />
            </CustomFormItem>
          </CustomCol>
          <CustomCol :span="16" :xs="24">
            <CustomFormItem label="Tiền sử bệnh">
              <CustomInput
                v-model="sucKhoe.tien_su_benh"
                maxlength="1000"
                show-word-limit
                placeholder="Bệnh mãn tính, dị ứng, khuyết tật hoặc ghi không có"
              />
            </CustomFormItem>
          </CustomCol>
        </CustomRow>
      </el-collapse-item>

      <el-collapse-item
        v-for="section in recordSections"
        :key="section.key"
        :name="section.key"
        :title="section.title"
      >
        <p class="profile-section__lead">{{ section.lead }}</p>
        <CustomTable
          v-if="openSections.includes(section.key)"
          :data="recordGroups[section.key]"
          row-key="_key"
          class="score-table record-table"
        >
          <CustomTableColumn label="STT" width="72" align="center">
            <template #default="{ $index }">{{ $index + 1 }}</template>
          </CustomTableColumn>
          <CustomTableColumn label="Nội dung" min-width="240">
            <template #default="{ row }">
              <CustomSelect
                v-model="row.ma"
                placeholder="Chọn"
                filterable
                :disabled="!row.editing"
              >
                <CustomOption
                  v-for="item in section.options"
                  :key="item.ma"
                  :label="item.label"
                  :value="item.ma"
                />
              </CustomSelect>
            </template>
          </CustomTableColumn>
          <CustomTableColumn label="Thành tích" min-width="260">
            <template #default="{ row }">
              <CustomInput
                v-model="row.thanh_tich"
                maxlength="100"
                :placeholder="scorePlaceholder(section.key, row.ma)"
                :title="scoreTitle(section.key, row.ma)"
                :disabled="!row.editing"
              />
            </template>
          </CustomTableColumn>
          <CustomTableColumn label="Thời gian cấp" min-width="170">
            <template #default="{ row }">
              <CustomDatePicker
                v-model="row.thoi_gian_cap"
                type="date"
                value-format="YYYY-MM-DD"
                format="DD/MM/YYYY"
                placeholder="Chọn ngày"
                clearable
                :disabled="!row.editing"
                :disabled-date="disableFutureDate"
              />
            </template>
          </CustomTableColumn>
          <CustomTableColumn label="Hành động" width="140" align="center">
            <template #default="{ row, $index }">
              <div class="row-actions">
                <CustomButton
                  v-if="!row.editing"
                  link
                  type="primary"
                  native-type="button"
                  @click="row.editing = true"
                >
                  Sửa
                </CustomButton>
                <CustomTooltip
                  v-if="$index === recordGroups[section.key].length - 1"
                  content="Thêm mới"
                  placement="top"
                >
                  <CustomButton
                    link
                    type="primary"
                    native-type="button"
                    aria-label="Thêm mới"
                    @click="addRecord(section.key)"
                  >
                    <CustomIcon><Plus /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
                <CustomTooltip v-if="canRemove(section.key, row)" content="Xóa" placement="top">
                  <CustomButton
                    link
                    type="danger"
                    native-type="button"
                    aria-label="Xóa"
                    @click="removeRecord(section.key, $index)"
                  >
                    <CustomIcon><Delete /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
              </div>
            </template>
          </CustomTableColumn>
          <template #empty>Chưa có mục trong danh mục.</template>
        </CustomTable>
      </el-collapse-item>
      </el-collapse>

      <div class="profile-actions">
        <CustomButton native-type="button" :disabled="loading" @click="fillSample">Điền dữ liệu mẫu</CustomButton>
        <CustomButton type="primary" :loading="saving" @click="onSubmit">Lưu thông tin</CustomButton>
      </div>
    </CustomForm>
  </el-card>
</template>

<style scoped>
.profile-card {
  border-radius: 12px;
}

.profile-card__title {
  margin: 0 0 4px;
  font-size: 20px;
  line-height: 1.4;
}

.profile-card__lead,
.profile-section__lead {
  margin: 0 0 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.4;
}

.profile-collapse {
  border-top: none;
  border-bottom: none;
}

.profile-collapse :deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: 600;
}

.profile-collapse :deep(.el-collapse-item__content) {
  padding-bottom: 8px;
}

.score-table {
  width: 100%;
}

.score-table :deep(.el-input-number),
.score-table :deep(.el-select),
.record-table :deep(.el-date-editor.el-input) {
  width: 100%;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.row-actions :deep(.el-icon) {
  font-size: 18px;
}

.row-actions :deep(.el-icon svg) {
  stroke: currentColor;
  stroke-width: 1.15;
  stroke-linejoin: round;
  paint-order: stroke fill;
}

.score-table.is-mobile-compact :deep(th.el-table__cell),
.score-table.is-mobile-compact :deep(td.el-table__cell) {
  padding: 6px 0;
}

.profile-card :deep(.el-input-number),
.profile-card :deep(.el-date-editor.el-input) {
  width: 100%;
}

.profile-actions {
  padding-top: 15px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
