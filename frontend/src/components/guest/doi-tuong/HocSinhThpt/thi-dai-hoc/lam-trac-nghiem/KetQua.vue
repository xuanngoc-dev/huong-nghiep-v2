<template>
  <section class="quiz-flow">
    <div class="container-fluid">
      <div class="holland-overview">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Kết quả trắc nghiệm Holland</h2>
          <p v-if="ketQua" class="holland-overview__lead">
            Đã trả lời {{ ketQua.so_da_tra_loi }}/{{ ketQua.so_cau_hoi }} câu. Kết quả cho biết xu hướng sở thích nghề
            nghiệp của bạn, dùng để định hướng tìm hiểu.
          </p>
        </header>

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải kết quả…</p>

        <template v-else-if="ketQua">
          <BuocLamBai :ssid="ssid" :buoc="buoc" hien-tai="ket-qua" />

          <div class="major-tabs">
            <div class="major-tabs__bar" role="tablist" aria-label="Kết quả trắc nghiệm Holland">
              <button
                v-for="tab in TABS"
                :id="idTab(tab.id)"
                :key="tab.id"
                type="button"
                role="tab"
                class="major-tabs__pill"
                :class="{ 'is-active': tabDangChon === tab.id }"
                :aria-selected="tabDangChon === tab.id"
                :aria-controls="`ket-qua-panel-${tab.id}`"
                :tabindex="tabDangChon === tab.id ? 0 : -1"
                @click="chonTab(tab.id)"
                @keydown="dieuHuongTab"
              >
                {{ tab.nhan }}
              </button>
            </div>
            <div
              :id="`ket-qua-panel-${tabDangChon}`"
              class="major-tabs__panel"
              role="tabpanel"
              :aria-labelledby="idTab(tabDangChon)"
            >
              <TongQuanKetQua
                v-if="tabDangChon === 'tong-quan'"
                :nhom="ketQua.nhom"
                :top="top"
                :ma-noi-bat="ketQua.ma_noi_bat"
              />
              <NgheNghiepDaoTao
                v-else-if="tabDangChon === 'nghe-nghiep'"
                :ssid="ssid"
                :top="top"
                :ma-noi-bat="ketQua.ma_noi_bat"
                :danh-muc-nhom="danhMucNhom"
                :nganh="nganh"
                :dang-tai-nganh="dangTaiNganh"
                :loi-nganh="loiNganh"
                :quan-tam="quanTam"
                :route-query="queryGiuLai"
                @doi-quan-tam="doiQuanTam"
              />
              <LoTrinhTiepTheo
                v-else
                :ssid="ssid"
                :top="top"
                :ma-noi-bat="ketQua.ma_noi_bat"
                :nganh="nganh"
                :quan-tam="quanTam"
                :route-query="queryGiuLai"
                @doi-quan-tam="doiQuanTam"
                @chuyen-tab="chonTab"
              />
            </div>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup>
/**
 * Kết quả trắc nghiệm Holland theo 3 tab: Tổng quan (mã Holland, biểu đồ, nhận xét, khám phá bản thân),
 * Nghề nghiệp & đào tạo (nghề, ngành, trường), Lộ trình tiếp theo (các bước, trải nghiệm, hành động).
 */
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import { fetchKetQua, fetchNganhPhuHop } from '@/api/phienKhaoSat'
import { docQuanTam, ghiQuanTam, xepHang } from '@/utils/ketQuaHolland'
import BuocLamBai from './BuocLamBai.vue'
import LoTrinhTiepTheo from './ket-qua/LoTrinhTiepTheo.vue'
import NgheNghiepDaoTao from './ket-qua/NgheNghiepDaoTao.vue'
import TongQuanKetQua from './ket-qua/TongQuanKetQua.vue'

defineOptions({ name: 'ThptKetQuaTracNghiem' })

const TABS = [
  { id: 'tong-quan', nhan: 'Tổng quan' },
  { id: 'nghe-nghiep', nhan: 'Nghề nghiệp & đào tạo' },
  { id: 'lo-trinh', nhan: 'Lộ trình tiếp theo' },
]

const route = useRoute()
const router = useRouter()
const ssid = computed(() => String(route.params.ssid || ''))
const dangTai = ref(false)
const loi = ref('')
const ketQua = ref(null)
const danhMucNhom = ref([])
const nganh = ref([])
const dangTaiNganh = ref(false)
const loiNganh = ref('')
const quanTam = reactive({ nganh: [], truong: [] })

const tabDangChon = computed(() => (TABS.some((tab) => tab.id === route.query.tab) ? route.query.tab : 'tong-quan'))
// Giữ ma_nganh của luồng làm bài khi sang trang chi tiết ngành / trường.
const queryGiuLai = computed(() => (route.query.ma_nganh ? { ma_nganh: route.query.ma_nganh } : {}))
const top = computed(() => xepHang(ketQua.value?.nhom).slice(0, 3))

const buoc = computed(() => [
  ...(ketQua.value?.buoc || []).map((item) => ({ ...item, xong: true })),
  { id: 'nganh-phu-hop', ten: 'Ngành phù hợp', xong: true },
  { id: 'ket-qua', ten: 'Kết quả', xong: false },
])

function idTab(id) {
  return `ket-qua-tab-${id}`
}

function chonTab(id) {
  router.replace({ query: { ...route.query, tab: id === 'tong-quan' ? undefined : id } })
}

function dieuHuongTab(event) {
  const huong = { ArrowRight: 1, ArrowLeft: -1, Home: 'dau', End: 'cuoi' }[event.key]
  if (!huong) return
  event.preventDefault()
  const index = TABS.findIndex((tab) => tab.id === tabDangChon.value)
  const ke = huong === 'dau' ? 0 : huong === 'cuoi' ? TABS.length - 1 : (index + huong + TABS.length) % TABS.length
  chonTab(TABS[ke].id)
  nextTick(() => document.getElementById(idTab(TABS[ke].id))?.focus())
}

function doiQuanTam(loai, item) {
  const khoa = loai === 'nganh' ? 'ma_nganh' : 'ma_truong'
  const ds = quanTam[loai]
  const index = ds.findIndex((x) => x[khoa] === item[khoa])
  if (index >= 0) ds.splice(index, 1)
  else ds.push(item)
  ghiQuanTam(globalThis.localStorage, ssid.value, { nganh: quanTam.nganh, truong: quanTam.truong })
}

async function taiNganh(value) {
  nganh.value = []
  loiNganh.value = ''
  dangTaiNganh.value = true
  try {
    nganh.value = (await fetchNganhPhuHop(value)).nganh || []
  } catch {
    loiNganh.value = 'Không tải được ngành phù hợp.'
  } finally {
    dangTaiNganh.value = false
  }
}

async function taiKetQua(value) {
  ketQua.value = null
  loi.value = ''
  Object.assign(quanTam, docQuanTam(globalThis.localStorage, value))
  if (!value) {
    loi.value = 'Không có mã phiên khảo sát.'
    return
  }
  dangTai.value = true
  try {
    ketQua.value = await fetchKetQua(value)
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    loi.value = status === 400 && typeof detail === 'string' ? detail : 'Không tải được kết quả.'
    return
  } finally {
    dangTai.value = false
  }
  taiNganh(value)
}

async function taiDanhMucNhom() {
  try {
    const data = await fetchNhomHolland({ trang_thai: 1, page: 1, page_size: 20 }, { skipLoading: true })
    danhMucNhom.value = data.items || []
  } catch {
    danhMucNhom.value = []
  }
}

watch(ssid, taiKetQua, { immediate: true })
taiDanhMucNhom()
</script>

<style src="./quiz-type.scss"></style>
