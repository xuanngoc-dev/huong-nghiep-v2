<template>
  <section class="quiz-flow">
    <div class="container-fluid mb-3">
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

          <div class="kq">
            <div v-if="top.length" class="row g-3 mt-2">
              <div v-for="(item, index) in top" :key="item.ma_nhom" class="col-12 col-md-4">
                <article class="kq-card kq-nhom">
                  <div class="kq-nhom__head">
                    <span class="kq-ma__badge" :class="`kq-ma__badge--${index + 1}`">{{ item.ma_nhom }}</span>
                    <div class="kq-nhom__ten">
                      <p class="kq-kicker">Nhóm nổi bật {{ index + 1 }}</p>
                      <h3>{{ item.ten_nhom }}</h3>
                    </div>
                    <span class="kq-nhom__diem">{{ item.diem }} điểm</span>
                  </div>
                  <!-- <p class="kq-nhom__mo-ta">{{ NOI_DUNG_NHOM[item.ma_nhom]?.xu_huong || item.mo_ta }}</p> -->
                  <RouterLink
                    class="kq-nhom__dem"
                    :to="{ name: 'thpt-thi-dai-hoc-nganh-phu-hop', params: { ssid }, query: queryGiuLai }"
                  >
                    <strong>{{ dangTaiNganh ? '…' : soNganh[item.ma_nhom] || 0 }}</strong>
                    <span>ngành đào tạo liên quan</span>
                  </RouterLink>
                </article>
              </div>
            </div>
            <p v-else class="kq-card kq-muted">Chưa đủ câu trả lời để xác định nhóm sở thích nổi bật.</p>

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
                <ToiLaAi v-if="tabDangChon === 'toi-la-ai'" :nhom="ketQua.nhom" :top="top" />
                <ToiPhuHop
                  v-else-if="tabDangChon === 'phu-hop'"
                  :ssid="ssid"
                  :top="top"
                  :danh-muc-nhom="danhMucNhom"
                  :nganh="nganh"
                  :dang-tai-nganh="dangTaiNganh"
                  :loi-nganh="loiNganh"
                  :route-query="queryGiuLai"
                />
                <ToiCaiThien v-else-if="tabDangChon === 'cai-thien'" :nhom="ketQua.nhom" :top="top" />
                <ToiLamGiTiep v-else :ssid="ssid" :top="top" :route-query="queryGiuLai" @chuyen-tab="chonTab" />
              </div>
            </div>

            <article class="kq-card kq-cta" v-if="false">
              <div>
                <h3 class="kq-card__title">Tìm trường phù hợp</h3>
                <p class="kq-muted">Chọn ngành để xem trường đào tạo và khả năng trúng tuyển theo điểm của bạn.</p>
              </div>
              <div class="kq-cta__form">
                <CustomSelect
                  v-model="maNganhTimTruong"
                  class="kq-select"
                  filterable
                  :loading="dangTaiNganh"
                  placeholder="Chọn ngành"
                >
                  <CustomOption
                    v-for="item in nganh.slice(0, 30)"
                    :key="item.ma_nganh"
                    :label="`${item.ma_nganh} — ${item.ten_nganh}`"
                    :value="item.ma_nganh"
                  />
                </CustomSelect>
                <RouterLink
                  v-if="maNganhTimTruong"
                  class="btn btn-success"
                  :to="{ name: 'thpt-thi-dai-hoc-truong-phu-hop', params: { maNganh: maNganhTimTruong } }"
                >
                  Tìm trường phù hợp
                </RouterLink>
                <button v-else type="button" class="btn btn-success" disabled>Tìm trường phù hợp</button>
              </div>
            </article>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup>
/**
 * Kết quả trắc nghiệm Holland: 3 thẻ nhóm nổi bật (kèm số ngành liên quan), 4 tab câu hỏi định hướng
 * (Tôi là ai? / phù hợp / cần cải thiện / làm gì tiếp theo) và hành động "Tìm trường phù hợp" ở cuối.
 */
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import { fetchKetQua, fetchNganhPhuHop } from '@/api/phienKhaoSat'
import { demNganhTheoNhom, xepHang } from '@/utils/ketQuaHolland'
import BuocLamBai from './BuocLamBai.vue'
import ToiCaiThien from './ket-qua/ToiCaiThien.vue'
import ToiLaAi from './ket-qua/ToiLaAi.vue'
import ToiLamGiTiep from './ket-qua/ToiLamGiTiep.vue'
import ToiPhuHop from './ket-qua/ToiPhuHop.vue'

defineOptions({ name: 'ThptKetQuaTracNghiem' })

const TABS = [
  { id: 'toi-la-ai', nhan: 'Tôi là ai?' },
  { id: 'phu-hop', nhan: 'Tôi phù hợp với điều gì?' },
  { id: 'cai-thien', nhan: 'Tôi cần cải thiện điều gì?' },
  { id: 'tiep-theo', nhan: 'Tôi nên làm gì tiếp theo?' },
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
const maNganhTimTruong = ref('')

const tabDangChon = computed(() => (TABS.some((tab) => tab.id === route.query.tab) ? route.query.tab : TABS[0].id))
// Giữ ma_nganh của luồng làm bài khi sang trang chi tiết ngành / trường.
const queryGiuLai = computed(() => (route.query.ma_nganh ? { ma_nganh: route.query.ma_nganh } : {}))
const top = computed(() => xepHang(ketQua.value?.nhom).slice(0, 3))
const soNganh = computed(() => demNganhTheoNhom(nganh.value))

const buoc = computed(() => [
  ...(ketQua.value?.buoc || []).map((item) => ({ ...item, xong: true })),
  { id: 'nganh-phu-hop', ten: 'Ngành phù hợp', xong: true },
  { id: 'ket-qua', ten: 'Kết quả', xong: false },
])

function idTab(id) {
  return `ket-qua-tab-${id}`
}

function chonTab(id) {
  router.replace({ query: { ...route.query, tab: id === TABS[0].id ? undefined : id } })
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
  // Mặc định tìm trường theo ngành của luồng làm bài, không có thì ngành phù hợp nhất.
  const maTuLuong = String(route.query.ma_nganh || '')
  maNganhTimTruong.value = nganh.value.some((item) => item.ma_nganh === maTuLuong)
    ? maTuLuong
    : nganh.value[0]?.ma_nganh || ''
}

async function taiKetQua(value) {
  ketQua.value = null
  loi.value = ''
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
<style scoped src="./ket-qua/ket-qua.css"></style>
