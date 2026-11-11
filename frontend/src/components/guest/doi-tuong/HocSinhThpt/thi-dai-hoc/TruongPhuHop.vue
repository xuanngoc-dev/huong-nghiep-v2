<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchTruongDaoTao } from '@/api/deAnTuyenSinh'
import { fetchDoiTuongUuTien } from '@/api/doiTuongUuTien'
import { fetchHoSo } from '@/api/hoSo'
import { fetchKhuVucUuTien } from '@/api/khuVucUuTien'
import { fetchMonHoc } from '@/api/monHoc'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchTinhThanh } from '@/api/tinhThanh'
import { fetchToHopMonHoc } from '@/api/toHopMonHoc'
import { danhSachNamHoc, nhanNamHoc } from '@/constants/namHoc'
import { useAuthStore } from '@/stores/auth'
import HoSo from '@/views/member/HoSo.vue'

defineOptions({ name: 'ThptThiDaiHocTruongPhuHop' })

const KHU_VUC = ['Bắc', 'Trung', 'Nam']
const LOAI_CO_SO = ['Đại học', 'Cao đẳng', 'Học viện']
const SAP_XEP = [
  { value: 'gan_toi', label: 'Gần nơi ở nhất', canHoSo: true },
  { value: 'ten_asc', label: 'Tên trường A → Z' },
  { value: 'ten_desc', label: 'Tên trường Z → A' },
  { value: 'chi_tieu_desc', label: 'Chỉ tiêu nhiều nhất' },
  { value: 'chuong_trinh_desc', label: 'Nhiều chương trình nhất' },
]
const NAM_HIEN_TAI = new Date().getFullYear()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const maNganh = computed(() => String(route.params.maNganh || '').trim())

const nganh = ref(null)
const hoSo = ref(null)
const tinhHoSo = ref(null)
const daDangNhap = ref(false)
const tinhOptions = ref([])
const danhMuc = ref({ monHoc: [], toHop: [], khuVucUuTien: [], doiTuongUuTien: [] })
const hoSoMo = ref(false)
const tuKhoa = ref('')
const khuVuc = ref('')
const namHoc = ref(NAM_HIEN_TAI)
const loai = ref('')
const tinh = ref('')
const sapXep = ref('ten_asc')
const boLoc = ref({
  tuKhoa: '',
  khuVuc: '',
  namHoc: NAM_HIEN_TAI,
  loai: '',
  tinh: '',
  sapXep: 'ten_asc',
})
const namOptions = danhSachNamHoc(NAM_HIEN_TAI)
const danhSach = ref([])
const total = ref(0)
const trang = ref(1)
const soMoiTrang = ref(12)
const dangTai = ref(false)
const loi = ref('')
const sanSang = ref(false)
let lanTai = 0

const tenNganh = computed(() => nganh.value?.ten_nganh || maNganh.value)
const sapXepOptions = computed(() => SAP_XEP.filter((item) => !item.canHoSo || tinhHoSo.value))

const moTaHoSo = computed(() => {
  if (!daDangNhap.value) {
    return 'Đăng nhập để lọc trường theo tỉnh thành trong hồ sơ. Hiện danh sách gồm trường có đào tạo ngành này.'
  }
  if (tinhHoSo.value) {
    return 'Bộ lọc và thứ tự gợi ý dựa trên các thông tin chính trong hồ sơ của bạn.'
  }
  return 'Hồ sơ chưa có tỉnh thành. Cập nhật hồ sơ để lọc trường theo nơi bạn đang ở.'
})

const diemThiThu = computed(() => {
  const duKien = hoSo.value?.trinh_do_hoc_van?.diem_thi_thpt_quoc_gia?.du_kien || {}
  const diem = {}
  for (const [ma, value] of Object.entries(duKien)) {
    const so = Number(value)
    if (value !== null && value !== '' && Number.isFinite(so)) diem[ma] = so
  }
  return diem
})

// Tổ hợp có tổng điểm thi thử cao nhất (thang 30). Chỉ xét tổ hợp đúng 3 môn và đủ điểm cả 3:
// danh mục có vài tổ hợp đặc biệt lưu nhiều môn hơn (ví dụ K01 "1 trong 4 môn") nên cộng sẽ sai.
const toHopManh = computed(() => {
  const diem = diemThiThu.value
  if (!Object.keys(diem).length) return []
  return danhMuc.value.toHop
    .filter((item) => item.trang_thai === 1 && item.ds_mon_hoc?.length === 3)
    .filter((item) => item.ds_mon_hoc.every((ma) => ma in diem))
    .map((item) => ({
      ma: item.ma_to_hop,
      tong: Math.round(item.ds_mon_hoc.reduce((sum, ma) => sum + diem[ma], 0) * 100) / 100,
      mon: item.ds_mon_hoc,
    }))
    .sort((a, b) => b.tong - a.tong || a.ma.localeCompare(b.ma))
    .slice(0, 3)
})

const tenMon = computed(() => new Map(danhMuc.value.monHoc.map((item) => [item.ma_mon_hoc, item.ten_mon_hoc])))

const thongTinHoSo = computed(() => {
  if (!hoSo.value) return []
  const hocVan = hoSo.value.trinh_do_hoc_van || {}
  const khuVucUt = danhMuc.value.khuVucUuTien.find((item) => item.id === hoSo.value.khu_vuc_uu_tien_id)
  const doiTuongUt = danhMuc.value.doiTuongUuTien.find((item) => item.id === hoSo.value.doi_tuong_uu_tien_id)
  const hocLuc12 = hocVan.hoc_luc_trung_binh?.['12']
  const soMon = Object.keys(diemThiThu.value).length
  const toHop = toHopManh.value[0]
  const chungChi = [
    ...(hocVan.chung_chi_ngoai_ngu || []),
    ...(hocVan.bai_thi_danh_gia_nang_luc || []),
  ].length
  return [
    {
      id: 'noi-o',
      icon: 'Location',
      nhan: 'Nơi ở',
      giaTri: tinhHoSo.value
        ? [tinhHoSo.value.ten, tinhHoSo.value.khu_vuc && `miền ${tinhHoSo.value.khu_vuc}`].filter(Boolean).join(' · ')
        : '',
    },
    {
      id: 'diem-thi',
      icon: 'Medal',
      nhan: 'Điểm thi thử THPT',
      giaTri: toHop ? `${toHop.ma}: ${toHop.tong} điểm` : soMon ? `${soMon} môn đã nhập` : '',
      goiY: toHop ? `Tổ hợp cao nhất · ${toHop.mon.map((ma) => tenMon.value.get(ma) || ma).join(', ')}` : '',
    },
    {
      id: 'hoc-luc',
      icon: 'Reading',
      nhan: 'Học lực lớp 12',
      giaTri: hocLuc12 != null && hocLuc12 !== '' ? `${hocLuc12} điểm` : '',
    },
    {
      id: 'uu-tien',
      icon: 'Flag',
      nhan: 'Ưu tiên tuyển sinh',
      giaTri: [khuVucUt?.ma_khu_vuc, doiTuongUt?.ma_doi_tuong].filter(Boolean).join(' · '),
      goiY: [khuVucUt?.ten_khu_vuc, doiTuongUt?.ten_doi_tuong].filter(Boolean).join(' · '),
    },
    {
      id: 'chung-chi',
      icon: 'Tickets',
      nhan: 'Chứng chỉ, bài thi ĐGNL',
      giaTri: chungChi ? `${chungChi} mục` : '',
    },
  ]
})

const soMucThieu = computed(() => thongTinHoSo.value.filter((item) => !item.giaTri).length)

const dangLocTheoHoSo = computed(
  () => !!tinhHoSo.value && (boLoc.value.tinh === tinhHoSo.value.ten || boLoc.value.khuVuc === tinhHoSo.value.khu_vuc),
)

const thongBaoTrong = computed(() => {
  if (boLoc.value.tinh || boLoc.value.khuVuc || boLoc.value.tuKhoa || boLoc.value.loai) {
    return 'Không có trường đào tạo ngành này khớp bộ lọc.'
  }
  return 'Chưa có trường đào tạo cho ngành này.'
})

function hrefWebsite(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  if (/^https?:\/\//i.test(text)) return text
  return `https://${text}`
}

function diaDiem(item) {
  return [item.loai_co_so, item.vung_mien, item.ten_tinh_thanh].filter(Boolean).join(' · ')
}

function chiTieu(value) {
  if (value == null || value === '') return ''
  return Number(value).toLocaleString('vi-VN')
}

function quayLai() {
  router.push({
    name: 'thpt-thi-dai-hoc-chon-truong',
    params: { maNganh: maNganh.value },
  })
}

function diDangNhap() {
  router.push({ name: 'login', query: { redirect: route.fullPath } })
}

function diDangKy() {
  router.push({ name: 'register', query: { redirect: route.fullPath } })
}

async function taiNganh(ma) {
  nganh.value = null
  if (!ma) return
  try {
    const data = await fetchNganh({ q: ma, trang_thai: 1, page: 1, page_size: 20 }, { skipLoading: true })
    nganh.value = (data.items || []).find((item) => String(item.ma_nganh).toUpperCase() === ma.toUpperCase()) || null
  } catch {
    nganh.value = null
  }
}

async function taiDanhMucHoSo() {
  const lay = (fetchFn) =>
    fetchFn({ page: 1, page_size: 1000 })
      .then((data) => data.items || [])
      .catch(() => [])
  const [monHoc, toHop, khuVucUuTien, doiTuongUuTien] = await Promise.all([
    lay(fetchMonHoc),
    lay(fetchToHopMonHoc),
    lay(fetchKhuVucUuTien),
    lay(fetchDoiTuongUuTien),
  ])
  danhMuc.value = { monHoc, toHop, khuVucUuTien, doiTuongUuTien }
}

// Lấy tỉnh/khu vực trong hồ sơ và đặt làm bộ lọc, thứ tự mặc định.
function apDungHoSo() {
  const tinhTim = tinhOptions.value.find((item) => item.id === hoSo.value?.tinh_thanh_id) || null
  if (!tinhTim) {
    tinhHoSo.value = null
    if (sapXep.value === 'gan_toi') sapXep.value = 'ten_asc'
    return
  }
  const khu = KHU_VUC.includes(tinhTim.khu_vuc) ? tinhTim.khu_vuc : ''
  tinhHoSo.value = { ten: tinhTim.ten_tinh, khu_vuc: khu }
  tinh.value = tinhTim.ten_tinh
  khuVuc.value = khu
  sapXep.value = 'gan_toi'
}

async function chuanBiHoSo() {
  daDangNhap.value = auth.isAuthenticated
  tinhHoSo.value = null
  hoSo.value = null
  let tinhItems = []
  try {
    const data = await fetchTinhThanh({ page: 1, page_size: 200, trang_thai: 1 }, { skipLoading: true })
    tinhItems = [...(data.items || [])]
    tinhItems.sort((a, b) => String(a.ten_tinh || '').localeCompare(String(b.ten_tinh || ''), 'vi'))
  } catch {
    tinhItems = []
  }
  tinhOptions.value = tinhItems
  if (!auth.isAuthenticated) return
  try {
    const [data] = await Promise.all([fetchHoSo({ skipLoading: true }), taiDanhMucHoSo()])
    hoSo.value = data
    daDangNhap.value = true
  } catch {
    hoSo.value = null
    daDangNhap.value = false
    return
  }
  apDungHoSo()
  boLoc.value = { ...boLoc.value, tinh: tinh.value, khuVuc: khuVuc.value, sapXep: sapXep.value }
}

async function tai() {
  const ma = maNganh.value
  const lan = ++lanTai
  danhSach.value = []
  total.value = 0
  if (!ma) {
    loi.value = 'Không có mã ngành.'
    return
  }
  dangTai.value = true
  loi.value = ''
  try {
    const params = {
      ma_nganh: ma,
      nam_tuyen_sinh: boLoc.value.namHoc || NAM_HIEN_TAI,
      sap_xep: boLoc.value.sapXep,
      page: trang.value,
      page_size: soMoiTrang.value,
    }
    if (boLoc.value.tuKhoa) params.q = boLoc.value.tuKhoa
    if (boLoc.value.khuVuc) params.vung_mien = boLoc.value.khuVuc
    if (boLoc.value.loai) params.loai_co_so = boLoc.value.loai
    if (boLoc.value.tinh) params.ten_tinh_thanh = boLoc.value.tinh
    if (boLoc.value.sapXep === 'gan_toi' && tinhHoSo.value) {
      params.uu_tien_tinh = tinhHoSo.value.ten
      if (tinhHoSo.value.khu_vuc) params.uu_tien_khu_vuc = tinhHoSo.value.khu_vuc
    }
    const data = await fetchTruongDaoTao(params, { skipLoading: true })
    if (lan !== lanTai) return
    danhSach.value = data.items || []
    total.value = data.total || 0
  } catch {
    if (lan !== lanTai) return
    loi.value = 'Không tải được trường phù hợp.'
  } finally {
    if (lan === lanTai) dangTai.value = false
  }
}

function timKiem() {
  const nam = Number(namHoc.value)
  boLoc.value = {
    tuKhoa: tuKhoa.value.trim(),
    khuVuc: khuVuc.value || '',
    namHoc: Number.isInteger(nam) ? nam : NAM_HIEN_TAI,
    loai: loai.value || '',
    tinh: tinh.value || '',
    sapXep: sapXep.value || 'ten_asc',
  }
  if (trang.value !== 1) trang.value = 1
  else tai()
}

function chonLoai(value) {
  loai.value = value
  timKiem()
}

function boLocHoSo() {
  khuVuc.value = ''
  tinh.value = ''
  timKiem()
}

function locTheoHoSo() {
  if (!tinhHoSo.value) return
  tinh.value = tinhHoSo.value.ten
  khuVuc.value = tinhHoSo.value.khu_vuc
  timKiem()
}

function daLuuHoSo(data) {
  hoSo.value = data
  hoSoMo.value = false
  apDungHoSo()
  timKiem()
}

watch(maNganh, (ma, truoc) => {
  if (!sanSang.value || !ma || ma === truoc) return
  taiNganh(ma)
  if (trang.value !== 1) trang.value = 1
  else tai()
})

watch(trang, () => {
  if (sanSang.value) tai()
})

watch(soMoiTrang, () => {
  if (!sanSang.value) return
  if (trang.value !== 1) trang.value = 1
  else tai()
})

onMounted(async () => {
  await Promise.all([taiNganh(maNganh.value), chuanBiHoSo()])
  sanSang.value = true
  tai()
})
</script>

<template>
  <section class="truong-phu-hop py-4">
    <div class="container-fluid">

      <div class="stages-card holland-overview mt-3">
        <header class="holland-overview__header truong-phu-hop__header">
          <h2 class="holland-overview__title">Trường phù hợp</h2>
          <CustomButton link type="primary" @click="quayLai">Quay lại</CustomButton>
        </header>

        <article class="truong-phu-hop__hero">
          <div class="truong-phu-hop__info">
            <p class="holland-overview__lead">
              Trường có đào tạo ngành <strong>{{ tenNganh }}</strong>
              <span v-if="maNganh"> ({{ maNganh }})</span>.
            </p>
            <p class="holland-overview__lead">{{ moTaHoSo }}</p>
          </div>
          <aside v-if="!daDangNhap" class="truong-phu-hop__auth">
            <p class="holland-note__text">
              Cung cấp hồ sơ năng lực cũng như bằng cấp, chứng chỉ để tìm ra trường phù hợp với bạn.
            </p>
            <div class="truong-phu-hop__links">
              <CustomButton type="primary" @click="diDangNhap">Đăng nhập</CustomButton>
              <CustomButton @click="diDangKy">Đăng ký</CustomButton>
            </div>
          </aside>
        </article>

        <article v-if="daDangNhap && hoSo" class="ho-so-tom-tat">
          <header class="ho-so-tom-tat__head">
            <div>
              <h3 class="ho-so-tom-tat__title">Thông tin của bạn</h3>
              <p class="ho-so-tom-tat__sub">
                {{ hoSo.ho_ten }}
                <span v-if="soMucThieu"> · còn {{ soMucThieu }} mục chưa cập nhật</span>
              </p>
            </div>
            <CustomButton type="primary" plain @click="hoSoMo = true">
              <CustomIcon><User /></CustomIcon>
              <span>Xem & cập nhật hồ sơ</span>
            </CustomButton>
          </header>
          <ul class="ho-so-tom-tat__list">
            <li
              v-for="item in thongTinHoSo"
              :key="item.id"
              class="ho-so-chip"
              :class="{ 'ho-so-chip--trong': !item.giaTri }"
            >
              <CustomIcon class="ho-so-chip__icon"><component :is="item.icon" /></CustomIcon>
              <div class="ho-so-chip__body">
                <span class="ho-so-chip__label">{{ item.nhan }}</span>
                <CustomTooltip :content="item.goiY" placement="top" :disabled="!item.goiY">
                  <span class="ho-so-chip__value">{{ item.giaTri || 'Chưa cập nhật' }}</span>
                </CustomTooltip>
              </div>
            </li>
          </ul>
        </article>

        <div class="loai-co-so" role="group" aria-label="Loại cơ sở đào tạo">
          <button
            type="button"
            class="loai-co-so__chip"
            :class="{ 'is-active': !boLoc.loai }"
            :aria-pressed="!boLoc.loai"
            @click="chonLoai('')"
          >
            Tất cả
          </button>
          <button
            v-for="item in LOAI_CO_SO"
            :key="item"
            type="button"
            class="loai-co-so__chip"
            :class="{ 'is-active': boLoc.loai === item }"
            :aria-pressed="boLoc.loai === item"
            @click="chonLoai(item)"
          >
            {{ item }}
          </button>
        </div>

        <form class="nhom-filter" @submit.prevent="timKiem">
          <div class="nhom-filter__field nhom-filter__field--ten">
            <label class="nhom-filter__label" for="phu-hop-tu-khoa">Từ khóa</label>
            <CustomInput id="phu-hop-tu-khoa" v-model="tuKhoa" placeholder="Tên hoặc mã trường" clearable />
          </div>
          <div class="nhom-filter__field nhom-filter__field--khu-vuc">
            <label class="nhom-filter__label" for="phu-hop-khu-vuc">Khu vực</label>
            <CustomSelect id="phu-hop-khu-vuc" v-model="khuVuc" class="nhom-filter__select" clearable placeholder="Tất cả khu vực">
              <CustomOption v-for="item in KHU_VUC" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--tinh">
            <label class="nhom-filter__label" for="phu-hop-tinh">Tỉnh/thành</label>
            <CustomSelect id="phu-hop-tinh" v-model="tinh" class="nhom-filter__select" filterable clearable placeholder="Tất cả tỉnh/thành">
              <CustomOption v-for="item in tinhOptions" :key="item.id" :label="item.ten_tinh" :value="item.ten_tinh" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--nam">
            <label class="nhom-filter__label" for="phu-hop-nam">Năm học</label>
            <CustomSelect id="phu-hop-nam" v-model="namHoc" class="nhom-filter__select" placeholder="Năm học">
              <CustomOption v-for="nam in namOptions" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--sap-xep">
            <label class="nhom-filter__label" for="phu-hop-sap-xep">Sắp xếp</label>
            <CustomSelect id="phu-hop-sap-xep" v-model="sapXep" class="nhom-filter__select" @change="timKiem">
              <CustomOption v-for="item in sapXepOptions" :key="item.value" :label="item.label" :value="item.value" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__actions">
            <CustomButton type="primary" native-type="submit">Tìm kiếm</CustomButton>
            <CustomButton v-if="dangLocTheoHoSo" native-type="button" @click="boLocHoSo">Bỏ lọc hồ sơ</CustomButton>
            <CustomButton v-else-if="tinhHoSo" native-type="button" @click="locTheoHoSo">Lọc theo hồ sơ</CustomButton>
          </div>
        </form>

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải trường phù hợp…</p>
        <KhongCoDuLieu v-else-if="!danhSach.length" :text="thongBaoTrong" />
        <div v-else class="row g-3">
          <div v-for="item in danhSach" :key="item.ma_truong" class="col-12 col-md-6 col-lg-3">
            <article class="nhom-card h-100">
              <p class="nhom-card__code">{{ item.ma_truong }}</p>
              <div class="nhom-card__main">
                <p class="nhom-card__field">{{ item.loai_co_so || 'Cơ sở đào tạo' }}</p>
                <h3 class="nhom-card__name">{{ item.ten_truong }}</h3>
                <p v-if="item.ten_tieng_anh" class="nhom-card__en">{{ item.ten_tieng_anh }}</p>
                <p v-if="diaDiem(item)" class="nhom-card__meta">{{ diaDiem(item) }}</p>
                <p v-if="item.dia_chi_tru_so" class="nhom-card__meta">{{ item.dia_chi_tru_so }}</p>
                <p v-if="item.so_chuong_trinh || chiTieu(item.chi_tieu)" class="nhom-card__meta">
                  <span v-if="item.so_chuong_trinh">{{ item.so_chuong_trinh }} chương trình</span>
                  <span v-if="item.so_chuong_trinh && chiTieu(item.chi_tieu)"> · </span>
                  <span v-if="chiTieu(item.chi_tieu)">Chỉ tiêu {{ chiTieu(item.chi_tieu) }}</span>
                </p>
                <p v-if="hrefWebsite(item.website_tuyen_sinh || item.website)" class="nhom-card__addr">
                  <a
                    class="nhom-card__web"
                    :href="hrefWebsite(item.website_tuyen_sinh || item.website)"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {{ item.website_tuyen_sinh || item.website }}
                  </a>
                </p>
              </div>
            </article>
          </div>
        </div>
        <div v-if="!dangTai && !loi && total > soMoiTrang" class="nhom-pager">
          <CustomPagination
            v-model:current-page="trang"
            v-model:page-size="soMoiTrang"
            :total="total"
            :page-sizes="[12, 24, 48]"
            layout="total, sizes, prev, pager, next"
            background
          />
        </div>
      </div>
    </div>

    <el-drawer
      v-model="hoSoMo"
      title="Hồ sơ của tôi"
      direction="rtl"
      size="min(960px, 100%)"
      append-to-body
      destroy-on-close
      class="ho-so-drawer"
    >
      <HoSo embedded @saved="daLuuHoSo" />
    </el-drawer>
  </section>
</template>

<style scoped>
/* Tiêu đề trái, nút quay lại phải. Thêm .truong-phu-hop để thắng rule căn giữa dùng chung. */
.truong-phu-hop .truong-phu-hop__header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 16px;
  text-align: left;
}

.truong-phu-hop .truong-phu-hop__header .holland-overview__title {
  margin: 0;
}

.truong-phu-hop__hero {
  display: flex;
  align-items: stretch;
  gap: 16px;
  padding: 18px;
  border: 1px solid #e3f0e6;
  border-radius: 12px;
  background: #f3faf4;
  text-align: left;
}

.truong-phu-hop__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  min-width: 0;
}

.truong-phu-hop__info :deep(strong) {
  color: #1c2b23;
}

.truong-phu-hop__auth {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e6ece8;
  border-radius: 12px;
  background: #fff;
}

.truong-phu-hop__links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ho-so-tom-tat {
  margin-top: 16px;
  padding: 16px 18px;
  border: 1px solid #dfeae3;
  border-radius: 12px;
  background: #fff;
  text-align: left;
}

.ho-so-tom-tat__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.ho-so-tom-tat__title {
  margin: 0;
  color: #1f2d26;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.4;
}

.ho-so-tom-tat__sub {
  margin: 2px 0 0;
  color: #5f7268;
  font-size: 0.875rem;
  line-height: 1.4;
}

.ho-so-tom-tat__list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.ho-so-chip {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid #e3eee7;
  border-radius: 10px;
  background: #f6fbf8;
}

.ho-so-chip__icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: #1f7a4d;
  font-size: 18px;
}

.ho-so-chip__body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.ho-so-chip__label {
  color: #5f7268;
  font-size: 0.78rem;
  line-height: 1.35;
}

.ho-so-chip__value {
  overflow: hidden;
  color: #1f2d26;
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ho-so-chip--trong {
  border-style: dashed;
  background: #fff;
}

.ho-so-chip--trong .ho-so-chip__icon,
.ho-so-chip--trong .ho-so-chip__value {
  color: #9aa8a0;
  font-weight: 400;
}

.loai-co-so {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.loai-co-so__chip {
  padding: 6px 16px;
  border: 1px solid #cfe1d6;
  border-radius: 999px;
  background: #fff;
  color: #31483d;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.loai-co-so__chip:hover {
  border-color: #1f7a4d;
  color: #1f7a4d;
}

.loai-co-so__chip.is-active {
  border-color: #1f7a4d;
  background: #1f7a4d;
  color: #fff;
}

.loai-co-so__chip:focus-visible {
  outline: 2px solid rgba(31, 122, 77, 0.4);
  outline-offset: 2px;
}

@media (max-width: 767px) {
  .truong-phu-hop__hero {
    flex-direction: column;
  }

  .truong-phu-hop__auth {
    flex-basis: auto;
  }

  .ho-so-tom-tat__head :deep(.el-button) {
    width: 100%;
  }
}

.nhom-filter__field--nam,
.nhom-filter__field--tinh,
.nhom-filter__field--sap-xep {
  flex: 1 1 160px;
  max-width: 220px;
}

.nhom-card__en,
.nhom-card__meta {
  margin: 0;
}
</style>
