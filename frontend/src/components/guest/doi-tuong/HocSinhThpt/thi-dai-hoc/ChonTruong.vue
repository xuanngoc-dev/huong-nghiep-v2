<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchHoSo } from '@/api/hoSo'
import { fetchNganh } from '@/api/nganhDaoTao'
import { useAuthStore } from '@/stores/auth'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import { fetchTinhThanh } from '@/api/tinhThanh'
import { fetchTruongHoc } from '@/api/truongHoc'
import { noiMucLuong } from '@/utils/capTenGiaTri'

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
const introMo = ref([])

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

const moTaNgan = computed(() => {
  const item = nganh.value
  if (!item) return ''
  return tachMoTa(item.mo_ta)[0] || `Thuộc nhóm ngành ${item.ten_nhom_nganh || '—'}.`
})

const loiThe = computed(() => {
  const item = nganh.value
  if (!item) return []
  const lines = [...tachMoTa(item.mo_ta), ...tachMoTa(item.chi_tiet)]
  if (item.nhan_dan) lines.push(`Nhu cầu việc làm: ${item.nhan_dan}`)
  const luong = noiMucLuong(item.muc_luong_tham_khao, '; ')
  if (luong) lines.push(`Mức lương tham khảo: ${luong}`)
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

function diaChi(item) {
  return (item.dia_chi_tru_so || '').trim() || 'Chưa cập nhật'
}

function hrefWebsite(value) {
  const text = (value || '').trim()
  if (!text) return ''
  if (/^https?:\/\//i.test(text)) return text
  return `https://${text}`
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

function diTruongPhuHop() {
  const ma = maNganh.value.trim()
  if (!ma) return
  router.push({
    name: 'thpt-thi-dai-hoc-truong-phu-hop',
    params: { maNganh: ma },
  })
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
  introMo.value = []
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
                  <h2 class="intro-collapse__name">{{ nganh.ten_nganh }}</h2>
                  <p class="intro-collapse__desc">{{ moTaNgan }}</p>
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
            <CustomButton type="success" @click="diTruongPhuHop">Trường phù hợp</CustomButton>
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

    <CustomDialog class="chon-truong-dialog" v-model="soSanhMo" title="So sánh trường" :width="960" height="70vh">
      <div class="so-sanh-wrap">
        <table class="so-sanh so-sanh--truong">
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

