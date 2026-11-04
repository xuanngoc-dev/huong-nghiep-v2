<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchHoSo } from '@/api/hoSo'
import { fetchNganh } from '@/api/nganhDaoTao'
import { useAuthStore } from '@/stores/auth'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import { batDauPhienHolland } from '@/api/phienKhaoSat'
import { fetchTinhThanh } from '@/api/tinhThanh'
import { fetchTruongHoc } from '@/api/truongHoc'

defineOptions({ name: 'ThptThiDaiHocChonTruong' })

const KHU_VUC = ['Bắc', 'Trung', 'Nam']
const LOAI_CO_SO = ['Cao đẳng', 'Đại học', 'Học viện']
const SO_TRUONG_TOI_DA = 4

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const maNganh = computed(() => String(route.params.maNganh || ''))

const nganh = ref(null)
const holland = ref([])
const dangTaiNganh = ref(false)
const loiNganh = ref('')
const dangTaoPhien = ref(false)
const nganhCungNhom = ref([])
const dangTaiCungNhom = ref(false)
const loiCungNhom = ref('')

const danhSach = ref([])
const tinhTheoMa = ref(new Map())
const tinhTheoTen = ref(new Map())
const tinhTheoId = ref(new Map())
const hoSo = ref(null)
const dangTai = ref(false)
const loi = ref('')
const trang = ref(1)
const soMoiTrang = ref(12)
const truongDaChon = ref([])
const soSanhMo = ref(false)
const chiTietMo = ref(false)
const truongChiTiet = ref(null)
const introMo = ref(['nganh'])

const ten = ref('')
const khuVuc = ref('')
const loai = ref('')
const boLoc = ref({ ten: '', khuVuc: '', loai: '' })

function tachMoTa(value) {
  return (value || '')
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const tenNhom = computed(
  () => nganh.value?.ten_nhom_nganh || nganhCungNhom.value[0]?.ten_nhom_nganh || '',
)

const loiThe = computed(() => {
  const item = nganh.value
  if (!item) return []
  const lines = [...tachMoTa(item.mo_ta), ...tachMoTa(item.chi_tiet)]
  if (item.nhan_dan) lines.push(`Nhu cầu việc làm: ${item.nhan_dan}`)
  if (item.muc_luong_tham_khao) lines.push(`Mức lương tham khảo: ${item.muc_luong_tham_khao}`)
  if (item.thoi_gian_dao_tao) lines.push(`Thời gian đào tạo: ${item.thoi_gian_dao_tao}`)
  const theoMa = new Map(holland.value.map((nhom) => [nhom.ma_nhom, nhom]))
  for (const code of item.ma_holand || []) {
    const nhom = theoMa.get(code)
    const text = (nhom?.mo_ta || '').trim()
    if (text) lines.push(text)
  }
  return lines
})

function chuanHoa(value) {
  return (value || '')
    .toLowerCase()
    .normalize('NFC')
    .replace(/^(tỉnh|thành phố|tp\.?)\s+/, '')
    .trim()
}

function loaiCua(item) {
  if (item.loai_co_so) return item.loai_co_so
  const ten = (item.ten_truong || '').toLowerCase()
  if (ten.includes('học viện')) return 'Học viện'
  if (ten.includes('cao đẳng')) return 'Cao đẳng'
  if (ten.includes('đại học')) return 'Đại học'
  return ''
}

function khuVucCua(item) {
  if (item.vung_mien) return item.vung_mien
  const ma = (item.ma_tinh_thanh || '').trim()
  if (ma && tinhTheoMa.value.get(ma)) return tinhTheoMa.value.get(ma)
  const ten = chuanHoa(item.ten_tinh_thanh)
  if (!ten) return ''
  if (tinhTheoTen.value.get(ten)) return tinhTheoTen.value.get(ten)
  for (const [tenTinh, khuVuc] of tinhTheoTen.value) {
    if (tenTinh.endsWith(` ${ten}`)) return khuVuc
  }
  return ''
}

function diaDiem(item) {
  return [khuVucCua(item), item.ten_tinh_thanh].filter(Boolean).join(' · ') || 'Chưa rõ khu vực'
}

function diaChi(item) {
  return (item.dia_chi_tru_so || '').trim() || 'Chưa cập nhật'
}

function hrefWebsite(value) {
  const text = (value || '').trim()
  if (!text) return ''
  if (/^https?:\/\//i.test(text)) return text
  return `https://${text}`
}

function linhVucCua(item) {
  const nguon = [...(item.linh_vuc_dao_tao_chinh || []), ...(item.linh_vuc_dao_tao_khac || [])]
  const tags = []
  const daCo = new Set()
  for (const raw of nguon) {
    const text = String(raw || '').trim()
    if (!text || daCo.has(text)) continue
    daCo.add(text)
    tags.push(text)
  }
  return tags
}

const ketQua = computed(() => {
  const tuKhoa = boLoc.value.ten.toLowerCase()
  return danhSach.value.filter((item) => {
    if (boLoc.value.khuVuc && khuVucCua(item) !== boLoc.value.khuVuc) return false
    if (boLoc.value.loai && loaiCua(item) !== boLoc.value.loai) return false
    if (!tuKhoa) return true
    const haystack = [item.ten_truong, item.ten_tieng_anh, item.ten_viet_tat, item.ma_truong]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(tuKhoa)
  })
})

const truongTrang = computed(() => {
  const batDau = (trang.value - 1) * soMoiTrang.value
  return ketQua.value.slice(batDau, batDau + soMoiTrang.value)
})

watch(soMoiTrang, () => {
  trang.value = 1
})

const coTheSoSanh = computed(() => truongDaChon.value.length >= 2 && truongDaChon.value.length <= SO_TRUONG_TOI_DA)

const hangSoSanh = [
  { label: 'Loại cơ sở', lay: (item) => loaiCua(item) || '—' },
  { label: 'Khu vực', lay: (item) => khuVucCua(item) || '—' },
  { label: 'Tỉnh/thành', lay: (item) => item.ten_tinh_thanh || '—' },
  { label: 'Địa chỉ', lay: (item) => item.dia_chi_tru_so || '—' },
  { label: 'Website', lay: (item) => item.website || '', link: true },
  { label: 'Loại hình', lay: (item) => item.loai_hinh || '—' },
  { label: 'Tên tiếng Anh', lay: (item) => item.ten_tieng_anh || '—' },
]

function moChiTiet(item) {
  truongChiTiet.value = item
  chiTietMo.value = true
}

function daChon(item) {
  return truongDaChon.value.some((truong) => truong.id === item.id)
}

function doiChon(item) {
  const dangChon = daChon(item)
  const conLai = truongDaChon.value.filter((truong) => truong.id !== item.id)
  if (dangChon) {
    truongDaChon.value = conLai
    if (conLai.length < 2) soSanhMo.value = false
    return
  }
  if (conLai.length >= SO_TRUONG_TOI_DA) {
    ElMessage.warning('Chỉ chọn tối đa 3 trường để so sánh.')
    return
  }
  truongDaChon.value = [...conLai, item]
}

const tinhHoSo = computed(() => {
  const id = hoSo.value?.tinh_thanh_id
  if (!id) return null
  return tinhTheoId.value.get(id) || null
})

const goiYHoSo = computed(() => {
  const tinh = tinhHoSo.value
  if (tinh?.ten && tinh.khu_vuc) {
    return `Hồ sơ cá nhân bổ sung khu vực nơi bạn đang ở vào tìm kiếm trường. Hồ sơ đang ở ${tinh.ten}, khu vực ${tinh.khu_vuc}. Cập nhật tỉnh thành tại Hồ sơ của tôi.`
  }
  return 'Hồ sơ cá nhân bổ sung khu vực nơi bạn đang ở vào tìm kiếm trường. Cập nhật tỉnh thành tại Hồ sơ của tôi. Chưa có tài khoản thì đăng nhập hoặc tạo tài khoản.'
})

const biCatMap = ref({})

function khoaTran(id, field) {
  return `${id}:${field}`
}

function biCat(id, field) {
  return !!biCatMap.value[khoaTran(id, field)]
}

function datBiCat(key, value) {
  if (!!biCatMap.value[key] === value) return
  biCatMap.value = { ...biCatMap.value, [key]: value }
}

const vMotHang = {
  mounted(el, binding) {
    const doCapNhat = () => {
      datBiCat(binding.value, el.scrollWidth > el.clientWidth + 1)
    }
    el._roTran = new ResizeObserver(doCapNhat)
    el._roTran.observe(el)
    el._khoaTran = binding.value
    doCapNhat()
  },
  updated(el, binding) {
    el._khoaTran = binding.value
    datBiCat(binding.value, el.scrollWidth > el.clientWidth + 1)
  },
  unmounted(el) {
    el._roTran?.disconnect()
    const key = el._khoaTran
    if (!key || !(key in biCatMap.value)) return
    const next = { ...biCatMap.value }
    delete next[key]
    biCatMap.value = next
  },
}

function diHoSo() {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: '/member/tai-khoan/ho-so' } })
    return
  }
  router.push({ name: 'ho-so' })
}

function apDungKhuVucHoSo() {
  const khu = tinhHoSo.value?.khu_vuc
  if (!khu || !KHU_VUC.includes(khu) || boLoc.value.khuVuc || khuVuc.value) return
  khuVuc.value = khu
  boLoc.value = { ...boLoc.value, khuVuc: khu }
}

async function taiHoSo() {
  if (!auth.isAuthenticated) return
  try {
    hoSo.value = await fetchHoSo({ skipLoading: true })
  } catch {
    hoSo.value = null
  }
  apDungKhuVucHoSo()
}

function quayLai() {
  router.push({ name: 'thpt-thi-dai-hoc-da-co' })
}

async function thamGiaKhaoSat() {
  if (dangTaoPhien.value) return
  dangTaoPhien.value = true
  try {
    const phien = await batDauPhienHolland()
    router.push({
      name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
      params: { ssid: phien.ssid, loaiCauHoiId: phien.loai_cau_hoi_id },
    })
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Không tạo được phiên khảo sát.')
  } finally {
    dangTaoPhien.value = false
  }
}

let lanTaiNganh = 0

async function taiNganhCungNhom(maNhom, lan) {
  if (!maNhom) {
    nganhCungNhom.value = []
    loiCungNhom.value = ''
    return
  }
  dangTaiCungNhom.value = true
  loiCungNhom.value = ''
  nganhCungNhom.value = []
  try {
    const pageSize = 200
    let page = 1
    const items = []
    while (page <= 20) {
      const data = await fetchNganh(
        { page, page_size: pageSize, trang_thai: 1, ma_nhom_nganh: maNhom },
        { skipLoading: true },
      )
      if (lan !== lanTaiNganh) return
      items.push(...(data.items || []))
      if (items.length >= (data.total || 0) || !data.items?.length) break
      page += 1
    }
    if (lan !== lanTaiNganh) return
    items.sort((a, b) => a.ten_nganh.localeCompare(b.ten_nganh, 'vi'))
    nganhCungNhom.value = items
  } catch {
    if (lan !== lanTaiNganh) return
    loiCungNhom.value = 'Không tải được ngành cùng nhóm.'
  } finally {
    if (lan === lanTaiNganh) dangTaiCungNhom.value = false
  }
}

async function taiNganh() {
  const lan = ++lanTaiNganh
  dangTaiNganh.value = true
  loiNganh.value = ''
  nganh.value = null
  try {
    const [data, hollandData] = await Promise.all([
      fetchNganh({ q: maNganh.value, trang_thai: 1, page: 1, page_size: 20 }, { skipLoading: true }),
      fetchNhomHolland({ trang_thai: 1, page: 1, page_size: 20 }, { skipLoading: true }),
    ])
    if (lan !== lanTaiNganh) return
    holland.value = hollandData.items || []
    nganh.value = (data.items || []).find((item) => item.ma_nganh === maNganh.value) || null
    if (!nganh.value) {
      loiNganh.value = 'Không tìm thấy ngành đã chọn.'
      nganhCungNhom.value = []
      return
    }
    const maNhom = nganh.value.ma_nhom_nganh
    const daCoDanhSach = nganhCungNhom.value.some((item) => item.ma_nhom_nganh === maNhom)
    if (!daCoDanhSach) taiNganhCungNhom(maNhom, lan)
  } catch {
    if (lan !== lanTaiNganh) return
    loiNganh.value = 'Không tải được thông tin ngành.'
    nganhCungNhom.value = []
  } finally {
    if (lan === lanTaiNganh) dangTaiNganh.value = false
  }
}

function chonNganhKhac(item) {
  if (item.ma_nganh === maNganh.value) return
  router.push({
    name: 'thpt-thi-dai-hoc-chon-truong',
    params: { maNganh: item.ma_nganh },
  })
}

watch(maNganh, (ma, truoc) => {
  if (!ma || ma === truoc) return
  introMo.value = ['nganh']
  taiNganh()
})

async function taiHet(layTrang) {
  const pageSize = 500
  const items = []
  let page = 1
  while (page <= 6) {
    const data = await layTrang(page, pageSize)
    const batch = data.items || []
    items.push(...batch)
    if (!batch.length || items.length >= (data.total || 0)) break
    page += 1
  }
  return items
}

async function taiTruong() {
  dangTai.value = true
  loi.value = ''
  try {
    const [truongItems, tinhItems] = await Promise.all([
      taiHet((page, pageSize) => fetchTruongHoc({ page, page_size: pageSize }, { skipLoading: true })),
      taiHet((page, pageSize) =>
        fetchTinhThanh({ page, page_size: pageSize, trang_thai: 1 }, { skipLoading: true }),
      ),
    ])
    const truongData = { items: truongItems }
    const tinhData = { items: tinhItems }
    const theoMa = new Map()
    const theoTen = new Map()
    const theoId = new Map()
    for (const item of tinhData.items || []) {
      if (item.ma_tinh && item.khu_vuc) theoMa.set(item.ma_tinh, item.khu_vuc)
      const tenTinh = chuanHoa(item.ten_tinh)
      if (tenTinh && item.khu_vuc) theoTen.set(tenTinh, item.khu_vuc)
      if (item.id) theoId.set(item.id, { ten: item.ten_tinh, khu_vuc: item.khu_vuc || '' })
    }
    tinhTheoMa.value = theoMa
    tinhTheoTen.value = theoTen
    tinhTheoId.value = theoId
    danhSach.value = truongData.items || []
    apDungKhuVucHoSo()
  } catch {
    loi.value = 'Không tải được danh sách trường.'
    danhSach.value = []
  } finally {
    dangTai.value = false
  }
}

function timKiem() {
  boLoc.value = {
    ten: ten.value.trim(),
    khuVuc: khuVuc.value || '',
    loai: loai.value || '',
  }
  trang.value = 1
}

onMounted(() => {
  taiNganh()
  taiTruong()
  taiHoSo()
})
</script>

<template>
  <section class="chon-truong py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
      <CustomButton link type="primary" @click="quayLai">Quay lại ngành</CustomButton>

      <article class="intro-card mt-3">
        <p v-if="loiNganh" class="holland-note holland-note__text mb-0">{{ loiNganh }}</p>
        <p v-else-if="dangTaiNganh" class="holland-overview__lead mb-0">Đang tải ngành…</p>
        <template v-else-if="nganh">
          <p class="nhom-card__code">{{ nganh.ma_nganh }}</p>
          <el-collapse v-model="introMo" class="intro-collapse" expand-icon-position="left">
            <el-collapse-item name="nganh">
              <template #title>
                <div class="intro-collapse__title">
                  <p class="nhom-card__field">{{ nganh.trinh_do }}</p>
                  <h2 class="h2 mb-1">{{ nganh.ten_nganh }}</h2>
                  <p v-if="nganh.ten_tieng_anh" class="nhom-card__en">{{ nganh.ten_tieng_anh }}</p>
                </div>
              </template>
              <p class="loi-the">
                Bạn đã chọn ngành <span class="intro-card__emph">{{ nganh.ten_nganh }}</span>, trực thuộc nhóm ngành
                nghề <span class="intro-card__emph">{{ nganh.ten_nhom_nganh }}</span>. Ngành này có những lợi thế:
              </p>
              <ul v-if="loiThe.length" class="loi-the-list">
                <li v-for="(item, index) in loiThe" :key="index">{{ item }}</li>
              </ul>
              <p v-else class="loi-the">Danh mục chưa có mô tả lợi thế cho ngành này.</p>
              <p class="loi-the mb-0">
                Bạn có muốn tham gia khảo sát để chắc chắn thêm về điều đó, hoặc chọn lại ngành nghề khác?
              </p>
              <div class="intro-actions">
                <CustomButton type="primary" :disabled="dangTaoPhien" :loading="dangTaoPhien" @click="thamGiaKhaoSat">
                  Tham gia khảo sát
                </CustomButton>
                <CustomButton link type="primary" @click="quayLai">Chọn lại ngành</CustomButton>
              </div>
            </el-collapse-item>
          </el-collapse>
        </template>
      </article>

      <div class="stages-card holland-overview mt-3">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Trường đại học, cao đẳng</h2>
          <p class="holland-overview__lead">
            Dưới đây là danh sách các trường đại học, cao đẳng tuyển sinh ngành học mà bạn quan tâm.
          </p>
          <p class="holland-overview__lead">Lọc theo khu vực, tên trường và loại cơ sở.</p>
        </header>

        <form class="nhom-filter" @submit.prevent="timKiem">
          <div class="nhom-filter__field nhom-filter__field--ten">
            <label class="nhom-filter__label" for="loc-ten-truong">Tên</label>
            <CustomInput id="loc-ten-truong" v-model="ten" placeholder="Nhập tên trường" clearable />
          </div>
          <div class="nhom-filter__field nhom-filter__field--khu-vuc">
            <label class="nhom-filter__label" for="loc-khu-vuc">Khu vực</label>
            <CustomSelect id="loc-khu-vuc" v-model="khuVuc" class="nhom-filter__select" filterable clearable placeholder="Tất cả khu vực">
              <CustomOption v-for="item in KHU_VUC" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--loai">
            <label class="nhom-filter__label" for="loc-loai-co-so">Loại cơ sở</label>
            <CustomSelect id="loc-loai-co-so" v-model="loai" class="nhom-filter__select" filterable clearable placeholder="Tất cả loại">
              <CustomOption v-for="item in LOAI_CO_SO" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__actions">
            <CustomButton type="primary" native-type="submit">Tìm kiếm</CustomButton>
            <CustomTooltip
              content="Chọn từ 2 đến 3 trường để so sánh."
              placement="top"
              :disabled="coTheSoSanh"
            >
              <span class="nhom-filter__tooltip">
                <CustomBadge :value="truongDaChon.length" :max="SO_TRUONG_TOI_DA">
                  <CustomButton type="primary" :disabled="!coTheSoSanh" @click="soSanhMo = true">
                    So sánh
                  </CustomButton>
                </CustomBadge>
              </span>
            </CustomTooltip>
            <CustomTooltip :content="goiYHoSo" placement="top">
              <span class="nhom-filter__tooltip">
                <CustomButton @click="diHoSo">Hồ sơ của tôi</CustomButton>
              </span>
            </CustomTooltip>
          </div>
        </form>

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải trường…</p>
        <p v-else-if="!ketQua.length" class="holland-note holland-note__text">Không có trường khớp bộ lọc.</p>
        <div v-else class="row g-3">
          <div v-for="item in truongTrang" :key="item.id" class="col-12 col-md-6 col-lg-3">
            <article class="nhom-card h-100" :class="{ 'is-selected': daChon(item) }" @click="doiChon(item)">
              <p class="nhom-card__code">{{ item.ma_truong }}</p>
              <label class="nhom-card__check" @click.stop>
                <input
                  type="checkbox"
                  :checked="daChon(item)"
                  :disabled="!daChon(item) && truongDaChon.length >= SO_TRUONG_TOI_DA"
                  :aria-label="`Chọn ${item.ten_truong}`"
                  @change="doiChon(item)"
                />
                <span class="nhom-card__mark" aria-hidden="true"></span>
              </label>
              <div class="nhom-card__main">
                <CustomTooltip
                  :content="loaiCua(item) || 'Cơ sở đào tạo'"
                  placement="top"
                  :disabled="!biCat(item.id, 'loai')"
                >
                  <p v-mot-hang="khoaTran(item.id, 'loai')" class="nhom-card__line nhom-card__field">
                    {{ loaiCua(item) || 'Cơ sở đào tạo' }}
                  </p>
                </CustomTooltip>
                <!-- <div v-if="linhVucCua(item).length" class="nhom-card__tags">
                  <CustomTag v-for="tag in linhVucCua(item)" :key="tag" effect="plain">{{ tag }}</CustomTag>
                </div> -->
                <CustomTooltip :content="item.ten_truong" placement="top" :disabled="!biCat(item.id, 'ten')">
                  <h3 v-mot-hang="khoaTran(item.id, 'ten')" class="nhom-card__line nhom-card__name">
                    {{ item.ten_truong }}
                  </h3>
                </CustomTooltip>
                <CustomTooltip :content="diaChi(item)" placement="top" :disabled="!item.dia_chi_tru_so || !biCat(item.id, 'diachi')">
                  <p class="nhom-card__addr">
                    <CustomIcon class="nhom-card__pin" aria-hidden="true"><Location /></CustomIcon>
                    <span v-mot-hang="khoaTran(item.id, 'diachi')" class="nhom-card__line nhom-card__meta">
                      {{ diaChi(item) }}
                    </span>
                  </p>
                </CustomTooltip>
                <CustomTooltip
                  :content="item.website || 'Chưa cập nhật'"
                  placement="top"
                  :disabled="!item.website || !biCat(item.id, 'web')"
                >
                  <p class="nhom-card__addr">
                    <CustomIcon class="nhom-card__pin" aria-hidden="true"><Link /></CustomIcon>
                    <a
                      v-if="item.website"
                      v-mot-hang="khoaTran(item.id, 'web')"
                      class="nhom-card__line nhom-card__web"
                      :href="hrefWebsite(item.website)"
                      target="_blank"
                      rel="noopener noreferrer"
                      @click.stop
                    >
                      {{ item.website }}
                    </a>
                    <span v-else class="nhom-card__line nhom-card__meta">Chưa cập nhật</span>
                  </p>
                </CustomTooltip>
                <!-- <CustomTooltip :content="diaDiem(item)" placement="top" :disabled="!biCat(item.id, 'dia')">
                  <p v-mot-hang="khoaTran(item.id, 'dia')" class="nhom-card__line nhom-card__meta">
                    {{ diaDiem(item) }}
                  </p>
                </CustomTooltip> -->
                <CustomTooltip
                  v-if="item.gioi_thieu_ngan"
                  :content="item.gioi_thieu_ngan"
                  placement="top"
                  :disabled="!biCat(item.id, 'gioi')"
                >
                  <!-- <p v-mot-hang="khoaTran(item.id, 'gioi')" class="nhom-card__line nhom-card__text">
                    {{ item.gioi_thieu_ngan }}
                  </p> -->
                </CustomTooltip>
                <!-- <div class="nhom-card__detail">
                  <CustomButton plain type="primary" @click.stop="moChiTiet(item)">Chi tiết</CustomButton>
                </div> -->
              </div>
            </article>
          </div>
        </div>
        <div v-if="!dangTai && !loi && ketQua.length" class="nhom-pager">
          <CustomPagination
            v-model:current-page="trang"
            v-model:page-size="soMoiTrang"
            :total="ketQua.length"
            layout="total, sizes, prev, pager, next"
            background
          />
        </div>
      </div>
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="nganh-cung-nhom" class="h4 mb-2">Ngành cùng nhóm</h2>
            <p v-if="tenNhom" class="side-lead">{{ tenNhom }}</p>
            <p v-if="loiCungNhom" class="holland-note holland-note__text mb-0">{{ loiCungNhom }}</p>
            <p v-else-if="dangTaiCungNhom || (dangTaiNganh && !nganhCungNhom.length)" class="side-lead mb-0">
              Đang tải ngành…
            </p>
            <p v-else-if="!nganhCungNhom.length" class="side-lead mb-0">Chưa có ngành trong nhóm này.</p>
            <div v-else class="d-flex flex-column gap-2" aria-labelledby="nganh-cung-nhom">
              <button
                v-for="item in nganhCungNhom"
                :key="item.id"
                type="button"
                class="switch-card side-nganh"
                :class="{ 'is-selected': item.ma_nganh === maNganh }"
                @click="chonNganhKhac(item)"
              >
                <span class="side-nganh__code">{{ item.ma_nganh }}</span>
                <span class="switch-card__body">
                  <span class="switch-card__name">{{ item.ten_nganh }}</span>
                  <span v-if="item.ten_tieng_anh" class="switch-card__text">{{ item.ten_tieng_anh }}</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <CustomDialog v-model="chiTietMo" :title="truongChiTiet?.ten_truong || 'Chi tiết trường'" :width="720" :height="420">
      <div v-if="truongChiTiet" class="chi-tiet">
        <p class="nhom-card__field">{{ loaiCua(truongChiTiet) || 'Cơ sở đào tạo' }}</p>
        <div v-if="linhVucCua(truongChiTiet).length" class="nhom-card__tags">
          <CustomTag v-for="tag in linhVucCua(truongChiTiet)" :key="tag" effect="plain">{{ tag }}</CustomTag>
        </div>
        <p class="chi-tiet__addr">
          <CustomIcon class="nhom-card__pin" aria-hidden="true"><Location /></CustomIcon>
          <span>{{ diaChi(truongChiTiet) }}</span>
        </p>
        <p class="chi-tiet__row">
          <CustomIcon class="nhom-card__pin" aria-hidden="true"><Link /></CustomIcon>
          <a
            v-if="truongChiTiet.website"
            class="nhom-card__web"
            :href="hrefWebsite(truongChiTiet.website)"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ truongChiTiet.website }}
          </a>
          <span v-else>Chưa cập nhật website</span>
        </p>
        <p class="chi-tiet__label">{{ diaDiem(truongChiTiet) }}</p>
        <p v-if="truongChiTiet.gioi_thieu_ngan" class="chi-tiet__text">{{ truongChiTiet.gioi_thieu_ngan }}</p>
        <p v-if="truongChiTiet.gioi_thieu_chi_tiet" class="chi-tiet__text">{{ truongChiTiet.gioi_thieu_chi_tiet }}</p>
      </div>
    </CustomDialog>

    <CustomDialog v-model="soSanhMo" title="So sánh trường" :width="960" height="70vh">
      <div class="so-sanh-wrap">
        <table class="so-sanh">
          <thead>
            <tr>
              <th>Thông tin</th>
              <th v-for="item in truongDaChon" :key="item.id">{{ item.ten_truong }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hang in hangSoSanh" :key="hang.label">
              <th>{{ hang.label }}</th>
              <td v-for="item in truongDaChon" :key="item.id">
                <a
                  v-if="hang.link && hang.lay(item)"
                  :href="hang.lay(item)"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ hang.lay(item) }}
                </a>
                <template v-else>{{ hang.lay(item) || '—' }}</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </CustomDialog>
  </section>
</template>

<style scoped>
.chon-truong :is(.h2, .h4, .holland-overview__title, .nhom-card__name, .switch-card__name) {
  font-weight: 400;
}

.side-lead {
  margin: 0 0 12px;
  color: #5c6b62;
  font-size: 0.85rem;
  font-weight: 400;
  line-height: 1.45;
}

.side-nganh {
  align-items: center;
}

.side-nganh__code {
  flex: 0 0 auto;
  min-width: 52px;
  padding: 4px 6px;
  border-radius: 8px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 400;
  letter-spacing: 0.03em;
  line-height: 1.2;
  text-align: center;
}

.chon-truong :deep(.el-button) {
  font-weight: 400;
}

.intro-card {
  position: relative;
  overflow: hidden;
  padding: 20px 20px 16px;
  border: 2px solid #7eae8c;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(31, 122, 77, 0.16);
}

.loi-the {
  margin-top: 10px;
  color: #3a4742;
  font-weight: 400;
  line-height: 1.55;
}

.loi-the-list {
  margin: 8px 0 0;
  padding-left: 1.15rem;
  color: #3a4742;
  font-weight: 400;
  line-height: 1.55;
}

.loi-the-list li + li {
  margin-top: 6px;
}

.intro-card__emph {
  color: var(--guest-primary);
  font-weight: 400;
}

.intro-collapse {
  border-top: 0;
  border-bottom: 0;
}

.intro-collapse :deep(.el-collapse-item__header) {
  height: auto;
  align-items: flex-start;
  padding: 0 72px 0 0;
  border-bottom: 0;
  background: transparent;
  line-height: 1.35;
  font-weight: 400;
}

.intro-collapse :deep(.el-collapse-item__arrow) {
  margin-top: 4px;
}

.intro-collapse :deep(.el-collapse-item__wrap) {
  border-bottom: 0;
  background: transparent;
}

.intro-collapse :deep(.el-collapse-item__content) {
  padding-bottom: 0;
  color: inherit;
  font-size: inherit;
  font-weight: 400;
}

.intro-collapse__title {
  padding: 2px 0 8px;
  text-align: left;
}

.intro-collapse__title .h2 {
  font-weight: 400;
}

.intro-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-top: 14px;
}

.nhom-filter__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  max-width: 100%;
}

@media (max-width: 767.98px) {
  .nhom-filter__actions {
    flex: 1 1 100%;
  }
}

.nhom-filter__tooltip {
  display: inline-flex;
}

.nhom-filter {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 8px;
}

.nhom-filter__field--ten {
  flex: 1 1 180px;
  max-width: 240px;
}

.nhom-filter__field--khu-vuc,
.nhom-filter__field--loai {
  flex: 1 1 150px;
  max-width: 200px;
}

.nhom-filter__label {
  display: block;
  margin-bottom: 4px;
  color: #3a4742;
  font-size: 0.8125rem;
  font-weight: 400;
}

.nhom-filter__select {
  width: 100%;
}

.nhom-card {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  margin: 0;
  padding: 16px;
  overflow: hidden;
  border: 2px solid #7eae8c;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(31, 122, 77, 0.16);
  cursor: pointer;
}

.nhom-card.is-selected {
  border: 3px solid #2d7a34;
  background: #e5f6ea;
}

.nhom-filter__tooltip :deep(.el-badge__content) {
  border: 0;
  font-weight: 400;
}

.nhom-card__main {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-self: stretch;
  gap: 4px;
  min-width: 0;
}

.nhom-card__main :deep(.el-tooltip__trigger) {
  display: block;
  max-width: 100%;
  min-width: 0;
}

.nhom-card__line {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nhom-card__check {
  position: relative;
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  align-self: center;
  cursor: pointer;
}

.nhom-card__addr,
.chi-tiet__addr {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
  max-width: 100%;
  margin: 0;
}

.nhom-card__main :deep(.nhom-card__addr.el-tooltip__trigger) {
  display: flex;
}

.nhom-card__pin {
  flex: 0 0 auto;
  color: var(--guest-primary);
  font-size: 1rem;
}

.nhom-card__addr .nhom-card__line {
  flex: 1;
  min-width: 0;
}

.nhom-card__web {
  display: block;
  color: var(--guest-primary);
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.45;
  text-decoration: none;
}

.nhom-card__web:hover {
  text-decoration: underline;
}

.nhom-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.nhom-card__tags :deep(.el-tag) {
  height: auto;
  border-color: #7eae8c;
  background: #f3faf6;
  color: #1f6b45;
  font-weight: 400;
  line-height: 1.35;
  white-space: normal;
}

.nhom-card__detail {
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
  padding-top: 8px;
}

.chi-tiet {
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #3a4742;
  font-weight: 400;
}

.chi-tiet__row,
.chi-tiet__label,
.chi-tiet__text {
  margin: 0;
  font-weight: 400;
  line-height: 1.5;
}

.chi-tiet__row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.chi-tiet__text {
  white-space: pre-line;
}

.nhom-card__check input {
  position: absolute;
  width: 22px;
  height: 22px;
  margin: 0;
  opacity: 0;
  cursor: pointer;
}

.nhom-card__mark {
  width: 22px;
  height: 22px;
  border: 2px solid #7eae8c;
  border-radius: 50%;
  background: #fff;
  display: grid;
  place-content: center;
}

.nhom-card__mark::after {
  content: "";
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--guest-primary);
  transform: scale(0);
}

.nhom-card__check input:checked + .nhom-card__mark {
  border-color: var(--guest-primary);
}

.nhom-card__check input:checked + .nhom-card__mark::after {
  transform: scale(1);
}

.nhom-card__check input:focus-visible + .nhom-card__mark {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

.nhom-card__check input:disabled {
  cursor: not-allowed;
}

.nhom-card__check input:disabled + .nhom-card__mark {
  opacity: 0.45;
  cursor: not-allowed;
}

.so-sanh-wrap {
  overflow-x: auto;
}

.so-sanh {
  width: 100%;
  border-collapse: collapse;
  color: #1c2b23;
  font-weight: 400;
}

.so-sanh th,
.so-sanh td {
  padding: 10px 12px;
  border-bottom: 1px solid #e4efe8;
  font-weight: 400;
  text-align: left;
  vertical-align: top;
}

.so-sanh thead th {
  color: var(--guest-primary);
}

.so-sanh tbody th {
  width: 140px;
  color: #3a4742;
  white-space: nowrap;
}

.so-sanh a {
  color: var(--guest-primary);
  word-break: break-all;
}

.nhom-card__code {
  position: absolute;
  top: 5px;
  right: -45px;
  z-index: 1;
  width: 118px;
  margin: 0;
  padding: 4px 0;
  background: var(--guest-primary);
  box-shadow: 0 2px 6px rgba(28, 43, 35, 0.2);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 400;
  letter-spacing: 0.04em;
  line-height: 1.2;
  text-align: center;
  transform: rotate(45deg);
}

.nhom-card__field {
  margin: 0;
  padding-right: 48px;
  color: var(--guest-primary);
  font-size: 0.78rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  line-height: 1.35;
  text-transform: uppercase;
}

.nhom-card__name {
  margin: 0;
  color: #1c2b23;
  font-size: 1.05rem;
  line-height: 1.35;
}

.nhom-card__en,
.nhom-card__meta,
.nhom-card__text {
  margin: 0;
  color: #5c6b64;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.45;
}

.nhom-pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.nhom-pager :deep(.el-pagination) {
  font-weight: 400;
}

.intro-card :deep(.nhom-card__code) {
  position: absolute;
}
</style>
