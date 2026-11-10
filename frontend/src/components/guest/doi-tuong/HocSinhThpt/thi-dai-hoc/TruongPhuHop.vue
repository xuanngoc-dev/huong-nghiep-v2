<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchTruongDaoTao } from '@/api/deAnTuyenSinh'
import { fetchHoSo } from '@/api/hoSo'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchTinhThanh } from '@/api/tinhThanh'
import { danhSachNamHoc, nhanNamHoc } from '@/constants/namHoc'
import { useAuthStore } from '@/stores/auth'

defineOptions({ name: 'ThptThiDaiHocTruongPhuHop' })

const KHU_VUC = ['Bắc', 'Trung', 'Nam']
const LOAI_CO_SO = ['Cao đẳng', 'Đại học', 'Học viện']
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
const tuKhoa = ref('')
const khuVuc = ref('')
const namHoc = ref(NAM_HIEN_TAI)
const loai = ref('')
const tinh = ref('')
const boLoc = ref({
  tuKhoa: '',
  khuVuc: '',
  namHoc: NAM_HIEN_TAI,
  loai: '',
  tinh: '',
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

const moTaHoSo = computed(() => {
  if (!daDangNhap.value) {
    return 'Đăng nhập để lọc trường theo tỉnh thành trong hồ sơ. Hiện danh sách gồm trường có đào tạo ngành này.'
  }
  const tinhTen = tinhHoSo.value?.ten
  const khu = tinhHoSo.value?.khu_vuc
  if (tinhTen && khu) {
    return `Hồ sơ đang ở ${tinhTen}, khu vực ${khu}. Danh sách ưu tiên trường đào tạo ngành này tại đó.`
  }
  if (tinhTen) {
    return `Hồ sơ đang ở ${tinhTen}. Danh sách ưu tiên trường đào tạo ngành này tại tỉnh thành này.`
  }
  return 'Hồ sơ chưa có tỉnh thành. Cập nhật hồ sơ để lọc trường theo nơi bạn đang ở.'
})

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

function diHoSo() {
  router.push({ name: 'ho-so' })
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
    hoSo.value = await fetchHoSo({ skipLoading: true })
    daDangNhap.value = true
  } catch {
    hoSo.value = null
    daDangNhap.value = false
    return
  }
  const tinhTim = tinhItems.find((item) => item.id === hoSo.value?.tinh_thanh_id) || null
  if (!tinhTim) return
  const khu = KHU_VUC.includes(tinhTim.khu_vuc) ? tinhTim.khu_vuc : ''
  tinhHoSo.value = { ten: tinhTim.ten_tinh, khu_vuc: khu }
  tinh.value = tinhTim.ten_tinh
  khuVuc.value = khu
  boLoc.value = { ...boLoc.value, tinh: tinhTim.ten_tinh, khuVuc: khu }
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
      page: trang.value,
      page_size: soMoiTrang.value,
    }
    if (boLoc.value.tuKhoa) params.q = boLoc.value.tuKhoa
    if (boLoc.value.khuVuc) params.vung_mien = boLoc.value.khuVuc
    if (boLoc.value.loai) params.loai_co_so = boLoc.value.loai
    if (boLoc.value.tinh) params.ten_tinh_thanh = boLoc.value.tinh
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
  }
  if (trang.value !== 1) trang.value = 1
  else tai()
}

function boLocHoSo() {
  khuVuc.value = ''
  tinh.value = ''
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
      <CustomButton link type="primary" @click="quayLai">Quay lại chọn trường</CustomButton>

      <div class="stages-card holland-overview mt-3">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Trường phù hợp</h2>
          <p class="holland-overview__lead">
            Trường có đào tạo ngành <strong>{{ tenNganh }}</strong>
            <span v-if="maNganh"> ({{ maNganh }})</span>.
          </p>
          <p class="holland-overview__lead">{{ moTaHoSo }}</p>
          <div class="truong-phu-hop__links">
            <CustomButton v-if="!daDangNhap" link type="primary" @click="diDangNhap">Đăng nhập</CustomButton>
            <CustomButton v-else link type="primary" @click="diHoSo">Hồ sơ của tôi</CustomButton>
          </div>
        </header>

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
          <div class="nhom-filter__field nhom-filter__field--nam">
            <label class="nhom-filter__label" for="phu-hop-nam">Năm học</label>
            <CustomSelect id="phu-hop-nam" v-model="namHoc" class="nhom-filter__select" placeholder="Năm học">
              <CustomOption v-for="nam in namOptions" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--loai">
            <label class="nhom-filter__label" for="phu-hop-loai">Loại cơ sở</label>
            <CustomSelect id="phu-hop-loai" v-model="loai" class="nhom-filter__select" clearable placeholder="Tất cả loại">
              <CustomOption v-for="item in LOAI_CO_SO" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--tinh">
            <label class="nhom-filter__label" for="phu-hop-tinh">Tỉnh/thành</label>
            <CustomSelect id="phu-hop-tinh" v-model="tinh" class="nhom-filter__select" filterable clearable placeholder="Tất cả tỉnh/thành">
              <CustomOption v-for="item in tinhOptions" :key="item.id" :label="item.ten_tinh" :value="item.ten_tinh" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__actions">
            <CustomButton type="primary" native-type="submit">Tìm kiếm</CustomButton>
            <CustomButton v-if="boLoc.tinh || boLoc.khuVuc" native-type="button" @click="boLocHoSo">Bỏ lọc hồ sơ</CustomButton>
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
  </section>
</template>

<style scoped>
.truong-phu-hop__links {
  margin-top: 4px;
}

.nhom-filter__field--nam,
.nhom-filter__field--tinh {
  flex: 1 1 160px;
  max-width: 220px;
}

.nhom-card__en,
.nhom-card__meta {
  margin: 0;
}
</style>
