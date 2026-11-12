<template>
  <div class="truong-dao-tao">
    <form class="nhom-filter" @submit.prevent="timKiem">
      <div class="nhom-filter__field nhom-filter__field--ten">
        <label class="nhom-filter__label" for="loc-tu-khoa-truong">Từ khóa</label>
        <CustomInput id="loc-tu-khoa-truong" v-model="tuKhoa" placeholder="Tên hoặc mã trường" clearable />
      </div>
      <div class="nhom-filter__field nhom-filter__field--khu-vuc">
        <label class="nhom-filter__label" for="loc-khu-vuc-truong">Khu vực</label>
        <CustomSelect id="loc-khu-vuc-truong" v-model="khuVuc" class="nhom-filter__select" clearable placeholder="Tất cả khu vực">
          <CustomOption v-for="item in KHU_VUC" :key="item" :label="item" :value="item" />
        </CustomSelect>
      </div>
      <div class="nhom-filter__field nhom-filter__field--nam">
        <label class="nhom-filter__label" for="loc-nam-hoc-truong">Năm học</label>
        <CustomSelect id="loc-nam-hoc-truong" v-model="namHoc" class="nhom-filter__select" placeholder="Năm học">
          <CustomOption v-for="nam in namOptions" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
        </CustomSelect>
      </div>
      <div class="nhom-filter__field nhom-filter__field--loai">
        <label class="nhom-filter__label" for="loc-loai-truong">Loại cơ sở</label>
        <CustomSelect id="loc-loai-truong" v-model="loai" class="nhom-filter__select" clearable placeholder="Tất cả loại">
          <CustomOption v-for="item in LOAI_CO_SO" :key="item" :label="item" :value="item" />
        </CustomSelect>
      </div>
      <div class="nhom-filter__field nhom-filter__field--tinh">
        <label class="nhom-filter__label" for="loc-tinh-truong">Tỉnh/thành</label>
        <CustomSelect id="loc-tinh-truong" v-model="tinh" class="nhom-filter__select" filterable clearable placeholder="Tất cả tỉnh/thành">
          <CustomOption v-for="item in tinhOptions" :key="item.id" :label="item.ten_tinh" :value="item.ten_tinh" />
        </CustomSelect>
      </div>
      <div class="nhom-filter__actions">
        <CustomButton type="primary" native-type="submit">Tìm kiếm</CustomButton>
        <CustomButton native-type="button" type="success" @click="diChonTruong">Trường phù hợp</CustomButton>
      </div>
    </form>

    <p v-if="loi" class="truong-dao-tao__status">{{ loi }}</p>
    <p v-else-if="dangTai" class="truong-dao-tao__status">Đang tải trường đào tạo…</p>
    <KhongCoDuLieu v-else-if="!danhSach.length" text="Chưa có trường đào tạo cho ngành này." />
    <div v-else class="row g-3 truong">
      <div v-for="item in danhSach" :key="item.ma_truong" class="col-12 col-md-6 col-lg-4">
        <article class="truong__item" :class="{ 'truong__item--co-anh': anhNen(item) }">
          <span v-if="anhNen(item)" class="truong__bg" :style="styleNen(item)" aria-hidden="true" />
          <p class="truong__code">{{ item.ma_truong }}</p>
          <div class="truong__main">
            <h3>{{ item.ten_truong }}</h3>
            <p v-if="item.ten_viet_tat" class="truong__meta">{{ item.ten_viet_tat }}</p>
            <dl class="truong__info">
              <div v-for="dong in thongTin(item)" :key="dong.nhan" class="truong__info-row">
                <dt>{{ dong.nhan }}</dt>
                <dd>
                  <a v-if="dong.link" :href="dong.link" target="_blank" rel="noopener noreferrer">{{ dong.giaTri }}</a>
                  <template v-else>{{ dong.giaTri }}</template>
                </dd>
              </div>
            </dl>
            <div class="truong__actions">
              <CustomButton plain size="small" type="success" @click="diChiTiet(item)">Chi tiết</CustomButton>
            </div>
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
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchTruongTheoNganh } from '@/api/nganhHocTheoTruong'
import { fetchTinhThanh } from '@/api/tinhThanh'
import { danhSachNamHoc, nhanNamHoc } from '@/constants/namHoc'
import anhThpt from '@/assets/guest/thpt.jpg'
import anhSinhVien from '@/assets/guest/sinh-vien.jpg'
import anhThcs from '@/assets/guest/thcs.jpg'
import anhThanhNien from '@/assets/guest/thanh-nien.jpg'
import anhPhuHuynh from '@/assets/guest/phu-huynh.jpg'
import anhNhaTruong from '@/assets/guest/nha-truong.jpg'
import anhNhaTuyenDung from '@/assets/guest/nha-tuyen-dung.jpg'

defineOptions({ name: 'ChiTietTruongDaoTao' })

const route = useRoute()
const router = useRouter()

const KHU_VUC = ['Bắc', 'Trung', 'Nam']
const LOAI_CO_SO = ['Cao đẳng', 'Đại học', 'Học viện']
const NAM_HIEN_TAI = new Date().getFullYear()
const ANH_DU_PHONG = [
  anhThpt,
  anhSinhVien,
  anhThcs,
  anhThanhNien,
  anhPhuHuynh,
  anhNhaTruong,
  anhNhaTuyenDung,
]

const props = defineProps({
  nganh: { type: Object, required: true },
  chiTiet: { type: Object, default: null },
  vanBan: { type: String, default: '' },
})

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
const tinhOptions = ref([])
const danhSach = ref([])
const total = ref(0)
const trang = ref(1)
const soMoiTrang = ref(12)
const dangTai = ref(false)
const loi = ref('')
let lanTai = 0

function hrefWebsite(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  if (/^https?:\/\//i.test(text)) return text
  return `https://${text}`
}

function thongTin(item) {
  const website = item.website_tuyen_sinh || item.website
  return [
    { nhan: 'Loại', giaTri: [item.loai_co_so, item.loai_hinh].filter(Boolean).join(' · ') },
    // { nhan: 'Khu vực', giaTri: [item.ten_tinh_thanh, item.vung_mien].filter(Boolean).join(' · ') },
    { nhan: 'Địa chỉ', giaTri: item.dia_chi_tru_so },
    { nhan: 'Chương trình', giaTri: item.so_chuong_trinh ? `${item.so_chuong_trinh} chương trình` : '' },
    { nhan: 'Website', giaTri: website, link: hrefWebsite(website) },
  ].filter((dong) => dong.giaTri)
}

function anhNen(item) {
  const url = String(item?.anh_dai_dien_url || '').trim()
  if (url) return url
  if (!ANH_DU_PHONG.length) return ''
  return ANH_DU_PHONG[bamMa(item?.ma_truong) % ANH_DU_PHONG.length]
}

function bamMa(ma) {
  let hash = 2166136261
  const khoa = String(ma || '')
  for (let i = 0; i < khoa.length; i += 1) {
    hash ^= khoa.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function matSong(hash) {
  const truc = 34 + (hash % 8)
  const bienDo = 2.5 + ((hash >>> 4) % 6)
  const soSong = 1 + ((hash >>> 8) % 3)
  const lech = ((hash >>> 11) % 9) - 4
  const phase = ((hash >>> 16) % 628) / 100
  const beRong = 1.15 + ((hash >>> 6) % 3) * 0.35
  const soLop = 14
  const ys = []
  for (let y = -20; y <= 120; y += 10) ys.push(y)

  function xTai(y, shift) {
    const ty = (y + 20) / 140
    const x = truc + shift + lech * ty + Math.sin(phase + ty * Math.PI * 2 * soSong) * bienDo
    return 100 - x
  }

  function vien(shift) {
    return ys.map((y) => `${xTai(y, shift).toFixed(2)},${y}`).join(' L')
  }

  let shapes = `<path d='M130,-20 L${vien(0)} L130,120 Z' fill='white'/>`
  for (let i = 0; i < soLop; i += 1) {
    const mo = ((1 - (i + 1) / soLop) ** 1.35).toFixed(3)
    const a = vien(i * beRong).split(' L')
    const b = vien((i + 1) * beRong).split(' L')
    shapes += `<path d='M${a.join(' L')} L${b.reverse().join(' L')} Z' fill='white' fill-opacity='${mo}'/>`
  }

  const svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'>${shapes}</svg>`
  return `url("data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}")`
}

function matTiepGiap(hash) {
  const kieu = hash % 6
  const neo = 36 + (hash % 8)
  const het = neo + 16 + ((hash >>> 5) % 12)
  const goc = 76 + ((hash >>> 9) % 29)
  if (kieu === 0) return `linear-gradient(${goc + 180}deg, #000 ${neo}%, transparent ${het}%)`
  if (kieu === 1) return `linear-gradient(${360 - goc}deg, #000 ${neo}%, transparent ${het}%)`
  if (kieu === 2) {
    const y = (hash >>> 12) % 101
    return `radial-gradient(145% 180% at 106% ${y}%, #000 ${neo}%, transparent ${het}%)`
  }
  if (kieu === 3) {
    const giua = neo + Math.round((het - neo) * 0.45)
    return `linear-gradient(${goc + 180}deg, #000 ${neo}%, rgba(0,0,0,.62) ${giua}%, transparent ${het}%)`
  }
  return matSong(hash)
}

function styleNen(item) {
  const url = anhNen(item).replace(/["\\\n\r\f]/g, '')
  if (!url) return undefined
  return {
    backgroundImage: `url("${url}")`,
    WebkitMaskImage: matTiepGiap(bamMa(item.ma_truong)),
    maskImage: matTiepGiap(bamMa(item.ma_truong)),
  }
}

async function taiTinh() {
  try {
    const data = await fetchTinhThanh({ page: 1, page_size: 200, trang_thai: 1 }, { skipLoading: true })
    const items = [...(data.items || [])]
    items.sort((a, b) => String(a.ten_tinh || '').localeCompare(String(b.ten_tinh || ''), 'vi'))
    tinhOptions.value = items
  } catch {
    tinhOptions.value = []
  }
}

async function tai() {
  const ma = String(props.nganh?.ma_nganh || '').trim()
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
    const data = await fetchTruongTheoNganh(params, { skipLoading: true })
    if (lan !== lanTai) return
    danhSach.value = data.items || []
    total.value = data.total || 0
  } catch {
    if (lan !== lanTai) return
    loi.value = 'Không tải được trường đào tạo.'
  } finally {
    if (lan === lanTai) dangTai.value = false
  }
}

function diChonTruong() {
  const ma = String(props.nganh?.ma_nganh || '').trim()
  if (!ma) return
  router.push({
    name: 'thpt-thi-dai-hoc-chon-truong',
    params: { maNganh: ma },
  })
}

function diChiTiet(item) {
  const maTruong = String(item?.ma_truong || '').trim()
  const ssid = String(route.params.ssid || '').trim()
  if (!maTruong || !ssid) return
  const query = {}
  const maNganh = String(props.nganh?.ma_nganh || '').trim()
  if (maNganh) query.ma_nganh = maNganh
  if (boLoc.value.namHoc) query.nam = String(boLoc.value.namHoc)
  router.push({
    name: 'thpt-thi-dai-hoc-chi-tiet-truong',
    params: { ssid, maTruong },
    query,
  })
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

watch(
  () => props.nganh?.ma_nganh,
  () => {
    if (trang.value !== 1) trang.value = 1
    else tai()
  },
)

watch(trang, tai)
watch(soMoiTrang, () => {
  if (trang.value !== 1) trang.value = 1
  else tai()
})

onMounted(() => {
  taiTinh()
  tai()
})
</script>

<style scoped>
.truong-dao-tao {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.nhom-filter__field--nam,
.nhom-filter__field--tinh {
  flex: 1 1 160px;
  max-width: 220px;
}

.nhom-filter__label {
  color: #3a4742;
  font-size: 0.8125rem;
}

.truong-dao-tao__status {
  margin: 0;
  color: #3d5c4c;
  line-height: 1.5;
}

.truong__item {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
  margin: 0;
  padding: 12px;
  overflow: hidden;
  border: 1px solid #c5d5cc;
  border-radius: 10px;
  background: #f6faf7;
}

.truong__bg {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  width: 100%;
  background-position: right center;
  background-repeat: no-repeat;
  background-size: cover;
  pointer-events: none;
  -webkit-mask-position: right center;
  mask-position: right center;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
}

.truong__main {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
  padding-right: 28px;
}

.truong__item--co-anh :is(h3, .truong__meta, .truong__info) {
  width: fit-content;
  max-width: 100%;
  text-shadow: 0 0 10px #fff, 0 0 5px #fff;
}

.truong__code {
  position: absolute;
  top: 5px;
  right: -45px;
  z-index: 2;
  width: 118px;
  margin: 0;
  padding: 3px 0;
  background: var(--guest-primary, #0c5c34);
  box-shadow: 0 2px 6px rgba(28, 43, 35, 0.2);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 400;
  letter-spacing: 0.04em;
  line-height: 1.2;
  text-align: center;
  transform: rotate(45deg);
}

.truong__item h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.08rem;
  font-weight: 700;
  line-height: 1.4;
}

.truong__meta {
  margin: 4px 0 0;
  color: #3d5c4c;
  font-size: 0.9375rem;
  line-height: 1.45;
}

.truong__info {
  display: grid;
  gap: 5px;
  margin: 10px 0 0;
  font-size: 0.9375rem;
  line-height: 1.5;
}

.truong__info-row {
  display: grid;
  grid-template-columns: 104px minmax(0, 1fr);
  gap: 10px;
}

.truong__info dt {
  color: #5a6e63;
  font-weight: 400;
}

.truong__info dd {
  margin: 0;
  color: #1c2836;
  overflow-wrap: anywhere;
}

.truong__info a {
  color: #0c5c34;
}

/* Bù lại khoảng đệm phải của .truong__main để nút sát góc phải dưới thẻ. */
.truong__actions {
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
  margin-right: -28px;
  padding-top: 12px;
}

@media (max-width: 767.98px) {
  .nhom-filter__field--ten,
  .nhom-filter__field--khu-vuc,
  .nhom-filter__field--nam,
  .nhom-filter__field--loai,
  .nhom-filter__field--tinh,
  .nhom-filter__actions {
    flex: 1 1 100%;
    max-width: none;
  }
}
</style>
