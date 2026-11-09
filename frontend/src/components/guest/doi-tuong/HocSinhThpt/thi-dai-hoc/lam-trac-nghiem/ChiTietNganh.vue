<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import anhMacDinh from '@/assets/guest/sinh-vien.jpg'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { noiMucLuong } from '@/utils/capTenGiaTri'
import { docChiTiet, noiGiaTri } from './chi-tiet/chiTiet'
import CardNganhDaoTao from '../CardNganhDaoTao.vue'
import TongQuan from './chi-tiet/TongQuan.vue'
import MoTaCongViec from './chi-tiet/MoTaCongViec.vue'
import LoTrinhPhatTrien from './chi-tiet/LoTrinhPhatTrien.vue'
import MucLuongKyNang from './chi-tiet/MucLuongKyNang.vue'
import TruongDaoTao from './chi-tiet/TruongDaoTao.vue'

defineOptions({ name: 'ThptChiTietNganh' })

const SO_NGANH_CUNG_NHOM = 4

const TABS = [
  { id: 'tong-quan', nhan: 'Tổng quan', component: TongQuan },
  { id: 'mo-ta-cong-viec', nhan: 'Mô tả công việc', component: MoTaCongViec },
  { id: 'lo-trinh', nhan: 'Lộ trình phát triển', component: LoTrinhPhatTrien },
  { id: 'muc-luong', nhan: 'Mức lương & Kỹ năng', component: MucLuongKyNang },
  { id: 'truong', nhan: 'Trường đào tạo', component: TruongDaoTao },
]

const route = useRoute()
const router = useRouter()
const ssid = computed(() => String(route.params.ssid || ''))
const maNganh = computed(() => String(route.params.maNganh || '').trim())
const dangTai = ref(false)
const loi = ref('')
const nganh = ref(null)
const anhHong = ref(false)
const tabDangChon = ref(TABS[0].id)
const nganhCungNhom = ref([])
const dangTaiCungNhom = ref(false)
const loiCungNhom = ref('')
const nhomHolland = ref([])

const anh = computed(() => {
  const url = String(nganh.value?.hinh_anh_mo_ta || '').trim()
  if (url && !anhHong.value) return url
  return anhMacDinh
})

function queryMaNganh() {
  const ma = route.query.ma_nganh
  return ma ? { ma_nganh: ma } : {}
}

const chiTiet = computed(() => (nganh.value ? docChiTiet(nganh.value) : { vanBan: '', json: null }))
const thanhPhanTab = computed(() => TABS.find((tab) => tab.id === tabDangChon.value)?.component || TongQuan)
const tenNhom = computed(() =>
  [nganh.value?.ma_nhom_nganh, nganh.value?.ten_nhom_nganh].filter(Boolean).join(' · '),
)

const moTa = computed(() => {
  if (!nganh.value) return ''
  const { vanBan, json } = chiTiet.value
  return nganh.value.mo_ta || noiGiaTri(json?.mo_ta) || vanBan
})

function maHollandCua(item) {
  const value = item?.ma_holand
  if (Array.isArray(value)) return value.map((code) => String(code).trim()).filter(Boolean)
  if (typeof value === 'string' && value.trim()) return [value.trim()]
  return []
}

const tomTat = computed(() => {
  if (!nganh.value) return []
  const { json } = chiTiet.value
  const theoMa = new Map(
    nhomHolland.value.map((nhom) => [String(nhom.ma_nhom).toUpperCase(), nhom.ten_nhom]),
  )
  const holand = maHollandCua(nganh.value)
    .map((code) => theoMa.get(code.toUpperCase()) || code)
    .join(', ')
  return [
    { nhan: 'Mã ngành', giaTri: nganh.value.ma_nganh },
    { nhan: 'Nhóm ngành', giaTri: [nganh.value.ma_nhom_nganh, nganh.value.ten_nhom_nganh].filter(Boolean).join(' · ') },
    { nhan: 'Trình độ', giaTri: nganh.value.trinh_do },
    { nhan: 'Thời gian đào tạo', giaTri: nganh.value.thoi_gian_dao_tao || noiGiaTri(json?.thoi_gian_dao_tao) },
    // { nhan: 'Mức lương tham khảo', giaTri: noiMucLuong(nganh.value.muc_luong_tham_khao) || noiGiaTri(json?.muc_luong_tham_khao || json?.muc_luong) },
    { nhan: 'Nhu cầu việc làm', giaTri: nganh.value.nhan_dan },
    { nhan: 'Nhóm Holland', giaTri: holand },
  ].filter((item) => item.giaTri)
})

function idTab(id) {
  return `major-tab-${maNganh.value}-${id}`
}

function dieuHuongTab(event) {
  const huong = { ArrowRight: 1, ArrowLeft: -1, Home: 'dau', End: 'cuoi' }[event.key]
  if (!huong) return
  event.preventDefault()
  const index = TABS.findIndex((tab) => tab.id === tabDangChon.value)
  const ke = huong === 'dau' ? 0 : huong === 'cuoi' ? TABS.length - 1 : (index + huong + TABS.length) % TABS.length
  tabDangChon.value = TABS[ke].id
  nextTick(() => document.getElementById(idTab(tabDangChon.value))?.focus())
}

function xemNganh(ma) {
  const code = String(ma || '').trim()
  if (!code || code.toUpperCase() === maNganh.value.toUpperCase()) return
  router.push({
    name: 'thpt-thi-dai-hoc-chi-tiet-nganh',
    params: { ssid: ssid.value, maNganh: code },
    query: queryMaNganh(),
  })
}

function quayLai() {
  if (!ssid.value) {
    router.push({ name: 'thpt-thi-dai-hoc' })
    return
  }
  router.push({
    name: 'thpt-thi-dai-hoc-nganh-phu-hop',
    params: { ssid: ssid.value },
    query: queryMaNganh(),
  })
}

let lanTai = 0
let taiHolland = null

function taiNhomHolland() {
  if (!taiHolland) {
    taiHolland = fetchNhomHolland({ trang_thai: 1, page: 1, page_size: 20 }, { skipLoading: true })
      .then((data) => {
        nhomHolland.value = data.items || []
      })
      .catch(() => {
        taiHolland = null
      })
  }
  return taiHolland
}

async function taiNganhCungNhom(maNhom, maHienTai, lan) {
  nganhCungNhom.value = []
  loiCungNhom.value = ''
  if (!maNhom) return
  dangTaiCungNhom.value = true
  try {
    const data = await fetchNganh(
      { ma_nhom_nganh: maNhom, trang_thai: 1, page: 1, page_size: 24 },
      { skipLoading: true },
    )
    if (lan !== lanTai) return
    const items = (data.items || []).filter(
      (item) => String(item.ma_nganh).toUpperCase() !== String(maHienTai).toUpperCase(),
    )
    items.sort((a, b) => String(a.ten_nganh || '').localeCompare(String(b.ten_nganh || ''), 'vi'))
    nganhCungNhom.value = items.slice(0, SO_NGANH_CUNG_NHOM)
  } catch {
    if (lan !== lanTai) return
    loiCungNhom.value = 'Không tải được ngành cùng nhóm.'
  } finally {
    if (lan === lanTai) dangTaiCungNhom.value = false
  }
}

async function taiNganh(ma) {
  const lan = ++lanTai
  nganh.value = null
  nganhCungNhom.value = []
  loiCungNhom.value = ''
  anhHong.value = false
  loi.value = ''
  tabDangChon.value = TABS[0].id
  if (!ma) {
    loi.value = 'Không có mã ngành.'
    return
  }
  dangTai.value = true
  try {
    const [data] = await Promise.all([
      fetchNganh({ q: ma, trang_thai: 1, page: 1, page_size: 20 }, { skipLoading: true }),
      taiNhomHolland(),
    ])
    if (lan !== lanTai) return
    const found = (data.items || []).find((item) => String(item.ma_nganh).toUpperCase() === ma.toUpperCase())
    if (!found) {
      loi.value = 'Không tìm thấy ngành này.'
      return
    }
    nganh.value = found
    taiNganhCungNhom(found.ma_nhom_nganh, ma, lan)
  } catch {
    if (lan !== lanTai) return
    loi.value = 'Không tải được thông tin ngành.'
  } finally {
    if (lan === lanTai) dangTai.value = false
  }
}

watch(maNganh, taiNganh, { immediate: true })
</script>

<template>
  <section class="quiz-flow">
    <div class="container-fluid">
      <div class="holland-overview">
        <!-- <header class="holland-overview__header">
          <h2 class="holland-overview__title">Chi tiết ngành</h2>
          <p v-if="nganh" class="holland-overview__lead">
            {{ [nganh.ma_nhom_nganh, nganh.ten_nhom_nganh].filter(Boolean).join(' · ') || nganh.ten_nganh }}
          </p>
          <p v-else class="holland-overview__lead">Thông tin đào tạo theo mã ngành trên đường dẫn.</p>
        </header> -->

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải thông tin ngành…</p>

        <template v-else-if="nganh">
          <article class="major-detail">
            <div class="major-detail__head">
              <img class="major-detail__image" :src="anh" :alt="`Hình minh họa ngành ${nganh.ten_nganh}`" @error="anhHong = true" />
              <div class="major-detail__intro">
                <p class="major-detail__code">{{ nganh.ma_nganh }}</p>
                <h3 class="major-detail__name">{{ nganh.ten_nganh }}</h3>
                <p v-if="nganh.ten_tieng_anh" class="major-detail__en">{{ nganh.ten_tieng_anh }}</p>
                <p class="major-detail__text">{{ moTa || 'Chưa có mô tả cho ngành này.' }}</p>
                <dl v-if="tomTat.length" class="major-facts">
                  <div v-for="item in tomTat" :key="item.nhan" class="major-facts__item">
                    <dt>{{ item.nhan }}</dt>
                    <dd>{{ item.giaTri }}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </article>

          <div class="major-tabs">
            <div class="major-tabs__bar" role="tablist" aria-label="Nội dung chi tiết ngành">
              <button
                v-for="tab in TABS"
                :id="idTab(tab.id)"
                :key="tab.id"
                type="button"
                role="tab"
                class="major-tabs__pill"
                :class="{ 'is-active': tabDangChon === tab.id }"
                :aria-selected="tabDangChon === tab.id"
                :aria-controls="`major-panel-${maNganh}-${tab.id}`"
                :tabindex="tabDangChon === tab.id ? 0 : -1"
                @click="tabDangChon = tab.id"
                @keydown="dieuHuongTab"
              >
                {{ tab.nhan }}
              </button>
            </div>
            <div
              :id="`major-panel-${maNganh}-${tabDangChon}`"
              class="major-tabs__panel"
              role="tabpanel"
              :aria-labelledby="idTab(tabDangChon)"
            >
              <component :is="thanhPhanTab" :nganh="nganh" :chi-tiet="chiTiet.json" :van-ban="chiTiet.vanBan" />
            </div>
          </div>

          <section class="major-peers" aria-labelledby="nganh-cung-nhom-title">
            <h2 id="nganh-cung-nhom-title" class="major-peers__title">Một số ngành học cùng nhóm</h2>
            <p v-if="tenNhom" class="major-peers__lead">{{ tenNhom }}</p>
            <p v-if="loiCungNhom" class="holland-note holland-note__text">{{ loiCungNhom }}</p>
            <p v-else-if="dangTaiCungNhom" class="major-peers__lead">Đang tải ngành cùng nhóm…</p>
            <p v-else-if="!nganhCungNhom.length" class="major-peers__lead">Chưa có ngành khác trong nhóm này.</p>
            <div v-else class="row g-3">
              <div v-for="item in nganhCungNhom" :key="item.ma_nganh" class="col-12 col-md-6 col-xl-3">
                <CardNganhDaoTao
                  class="h-100"
                  :ma="item.ma_nganh"
                  :ten="item.ten_nganh"
                  :ten-tieng-anh="item.ten_tieng_anh"
                  :mo-ta="item.mo_ta || ''"
                  :hinh-anh="item.hinh_anh_mo_ta || ''"
                  :khoa="item.id || item.ma_nganh"
                  hanh-dong="Xem chi tiết"
                  @chon="xemNganh(item.ma_nganh)"
                />
              </div>
            </div>
          </section>

          <HoTroDinhHuong class="mt-3" />
          <CauHoiThuongGap class="mt-3" />
        </template>

        <div class="major-nav">
          <button type="button" class="btn btn-outline-success" @click="quayLai">Quay lại ngành phù hợp</button>
        </div>
      </div>
    </div>
  </section>
</template>

<style src="./quiz-type.scss"></style>
