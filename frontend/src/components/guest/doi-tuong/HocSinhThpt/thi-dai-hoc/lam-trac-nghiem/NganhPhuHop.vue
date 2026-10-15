<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchNganhPhuHop } from '@/api/phienKhaoSat'
import BieuDoRadar from '@/components/guest/BieuDoRadar.vue'
import CardMajor from './CardMajor.vue'
import anhA from '@/assets/guest/holland/a.svg'
import anhC from '@/assets/guest/holland/c.svg'
import anhE from '@/assets/guest/holland/e.svg'
import anhI from '@/assets/guest/holland/i.svg'
import anhR from '@/assets/guest/holland/r.svg'
import anhS from '@/assets/guest/holland/s.svg'
import BuocLamBai from './BuocLamBai.vue'

const ANH_NHOM = { R: anhR, I: anhI, A: anhA, S: anhS, E: anhE, C: anhC }
const SO_NGANH_HIEN = 4
const SO_SANH_TOI_DA = 3
const TIEU_CHI_SO_SANH = [
  { id: 'mo_ta', ten: 'Mô tả/ngành học' },
  { id: 'ky_nang_phu_hop', ten: 'Kỹ năng phù hợp' },
  { id: 'mon_hoc_tieu_bieu', ten: 'Môn học tiêu biểu' },
  { id: 'co_hoi_nghe_nghiep', ten: 'Cơ hội nghề nghiệp' },
  { id: 'muc_luong', ten: 'Mức lương (tham khảo)' },
  { id: 'cong_cu', ten: 'Công cụ thường dùng' },
  { id: 'do_phu_hop', ten: 'Độ phù hợp với bản thân' },
  { id: 'diem_can_nhac', ten: 'Điểm cân nhắc' },
  { id: 'truong_dao_tao', ten: 'Các trường đào tạo' },
]

defineOptions({ name: 'ThptNganhPhuHop' })

const route = useRoute()
const router = useRouter()
const ssid = computed(() => String(route.params.ssid || ''))
const dangTai = ref(false)
const loi = ref('')
const duLieu = ref(null)
const maDangXem = ref('')
const nhomDaMo = ref({})
const nganhDaChon = ref({})
const soSanhMo = ref(false)
const nganhSoSanh = ref([])
const bang = ref(null)
const biCat = ref({})
const theMoTa = new Map()
let quanSatBang = null

const buoc = computed(() => {
  const daXong = !!duLieu.value?.da_xong
  return [
    ...(duLieu.value?.buoc || []).map((item) => ({ ...item, xong: daXong })),
    { id: 'nganh-phu-hop', ten: 'Ngành phù hợp', xong: false },
    { id: 'ket-qua', ten: 'Kết quả', xong: false },
  ]
})
const buocTruoc = computed(() => {
  const questions = duLieu.value?.buoc || []
  return questions[questions.length - 1] || null
})
const nhomTheoDiem = computed(() =>
  [...(duLieu.value?.nhom || [])].sort((a, b) => b.diem - a.diem || a.ma_nhom.localeCompare(b.ma_nhom)),
)
const nhomCaoNhat = computed(() => nhomTheoDiem.value[0] || null)
const maDangChon = computed(() => maDangXem.value || nhomCaoNhat.value?.ma_nhom || '')
const nhomNganhHienThi = computed(() => {
  const ma = maDangChon.value
  if (!ma) return []
  const groups = new Map()
  for (const item of duLieu.value?.nganh || []) {
    if (!item.ma_holand?.includes(ma)) continue
    const key = item.ma_nhom_nganh || item.ten_nhom_nganh
    if (!groups.has(key)) {
      groups.set(key, { ma: key, ten: item.ten_nhom_nganh, nganh: [] })
    }
    groups.get(key).nganh.push(item)
  }
  return [...groups.values()].map((group) => ({
    ...group,
    nganh: [...group.nganh].sort((a, b) => {
      const uuA = a.ma_holand?.[0] === ma ? 0 : 1
      const uuB = b.ma_holand?.[0] === ma ? 0 : 1
      return uuA - uuB || a.ten_nganh.localeCompare(b.ten_nganh, 'vi')
    }),
  }))
})

function nganhDangXem(nhom) {
  if (nhomDaMo.value[nhom.ma]) return nhom.nganh
  return nhom.nganh.slice(0, SO_NGANH_HIEN)
}

function doiMoNhom(ma) {
  nhomDaMo.value = { ...nhomDaMo.value, [ma]: !nhomDaMo.value[ma] }
}

function maNganhDaChon(nhom) {
  return nganhDaChon.value[nhom.ma] || []
}

function daChonNganh(nhom, nganh) {
  return maNganhDaChon(nhom).includes(nganh.ma_nganh)
}

function chonNganh(nhom, nganh) {
  const daChon = [...maNganhDaChon(nhom)]
  const index = daChon.indexOf(nganh.ma_nganh)
  if (index >= 0) {
    daChon.splice(index, 1)
  } else if (daChon.length >= SO_SANH_TOI_DA) {
    ElMessage.warning('Chỉ so sánh tối đa 3 ngành.')
    return
  } else {
    daChon.push(nganh.ma_nganh)
  }
  nganhDaChon.value = { ...nganhDaChon.value, [nhom.ma]: daChon }
}

function moSoSanh(nhom) {
  const ma = maNganhDaChon(nhom)
  if (ma.length < 2) {
    ElMessage.warning('Hãy chọn từ 2 đến 3 ngành để so sánh.')
    return
  }
  nganhSoSanh.value = ma
    .map((code) => nhom.nganh.find((item) => item.ma_nganh === code))
    .filter(Boolean)
  soSanhMo.value = true
}

function noiChiTiet(value) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean).join('\n')
  }
  if (value == null) return ''
  return String(value).trim()
}

function chiTietNganh(nganh) {
  const text = String(nganh.chi_tiet || '').trim()
  if (!text.startsWith('{')) return {}
  try {
    const data = JSON.parse(text)
    return data && typeof data === 'object' && !Array.isArray(data) ? data : {}
  } catch {
    return {}
  }
}

function doPhuHop(nganh) {
  const khop = nhomTheoDiem.value.filter(
    (nhom) => nhom.diem > 0 && nganh.ma_holand?.includes(nhom.ma_nhom),
  )
  if (!khop.length) return ''
  return khop.map((nhom) => `${nhom.ma_nhom} · ${nhom.ten_nhom} (${nhom.diem} điểm)`).join('\n')
}

function giaTriTieuChi(nganh, id) {
  const chiTiet = chiTietNganh(nganh)
  if (id === 'mo_ta') return nganh.mo_ta || noiChiTiet(chiTiet.mo_ta) || '—'
  if (id === 'muc_luong') return nganh.muc_luong_tham_khao || noiChiTiet(chiTiet.muc_luong_tham_khao) || '—'
  if (id === 'do_phu_hop') return noiChiTiet(chiTiet.do_phu_hop) || doPhuHop(nganh) || '—'
  return noiChiTiet(chiTiet[id]) || '—'
}

function xemNganh(ma) {
  maDangXem.value = ma
  nhomDaMo.value = {}
  nganhDaChon.value = {}
}

function ganMoTa(ma, el) {
  if (el) theMoTa.set(ma, el)
  else theMoTa.delete(ma)
}

function doMoTa() {
  const next = {}
  for (const [ma, el] of theMoTa) {
    next[ma] = el.scrollHeight > el.clientHeight + 1
  }
  biCat.value = next
}

async function taiNganh(value) {
  duLieu.value = null
  maDangXem.value = ''
  nhomDaMo.value = {}
  nganhDaChon.value = {}
  soSanhMo.value = false
  nganhSoSanh.value = []
  loi.value = ''
  if (!value) {
    loi.value = 'Không có mã phiên khảo sát.'
    return
  }
  dangTai.value = true
  try {
    duLieu.value = await fetchNganhPhuHop(value)
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    loi.value = status === 404 && typeof detail === 'string' ? detail : 'Không tải được ngành phù hợp.'
  } finally {
    dangTai.value = false
  }
}

function lui() {
  if (!buocTruoc.value) return
  router.push({
    name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    params: { ssid: ssid.value, loaiCauHoiId: buocTruoc.value.id },
  })
}

function tiep() {
  if (!duLieu.value?.da_xong) {
    ElMessage.error('Vui lòng hoàn thành các phần trước khi xem kết quả.')
    return
  }
  router.push({ name: 'thpt-thi-dai-hoc-ket-qua', params: { ssid: ssid.value } })
}

watch(ssid, taiNganh, { immediate: true })
watch(nhomTheoDiem, () => nextTick(doMoTa))
watch(bang, (el) => {
  if (!quanSatBang) quanSatBang = new ResizeObserver(() => doMoTa())
  quanSatBang.disconnect()
  if (el) quanSatBang.observe(el)
})

onMounted(() => {
  if (!quanSatBang) quanSatBang = new ResizeObserver(() => doMoTa())
  if (bang.value) quanSatBang.observe(bang.value)
})

onBeforeUnmount(() => {
  quanSatBang?.disconnect()
  quanSatBang = null
})
</script>

<template>
  <section class="quiz-flow py-4">
    <div class="container-fluid">
      <div class="holland-overview">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Ngành phù hợp</h2>
          <p v-if="duLieu?.ma_noi_bat" class="holland-overview__lead">
            Gợi ý theo nhóm tính cách nổi bật {{ duLieu.ma_noi_bat }}.
          </p>
          <p v-else class="holland-overview__lead">Ngành đào tạo gần với kết quả trắc nghiệm Holland của bạn.</p>
        </header>

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải ngành phù hợp…</p>

        <template v-else-if="duLieu">
          <BuocLamBai :ssid="ssid" :buoc="buoc" hien-tai="nganh-phu-hop" />

          <article v-if="nhomCaoNhat" class="top-group">
            <img
              class="top-group__icon"
              :src="ANH_NHOM[nhomCaoNhat.ma_nhom]"
              :alt="`Biểu tượng nhóm ${nhomCaoNhat.ten_nhom}`"
            />
            <div class="top-group__body">
              <p class="top-group__kicker">Nhóm điểm cao nhất</p>
              <h3 class="top-group__name">[{{ nhomCaoNhat.ma_nhom }}]-{{ nhomCaoNhat.ten_nhom }}</h3>
              <p class="top-group__text">{{ nhomCaoNhat.mo_ta || 'Chưa có mô tả cho nhóm này.' }}</p>
            </div>
            <p class="top-group__score">{{ nhomCaoNhat.diem }} điểm</p>
          </article>

          <div v-if="nhomTheoDiem.length" class="row g-3 profile">
            <div class="col-12 col-md-4">
              <article class="card h-100 profile__chart-card">
                <header class="card-header">Điểm Holland</header>
                <div class="card-body d-flex align-items-center justify-content-center">
                  <BieuDoRadar
                    :height="320"
                    :categories="nhomTheoDiem.map((item) => item.ten_nhom)"
                    :values="nhomTheoDiem.map((item) => item.diem)"
                    series-name="Điểm Holland"
                  />
                </div>
              </article>
            </div>
            <div class="col-12 col-md-8">
              <article ref="bang" class="card h-100 profile__table">
              <table>
                <colgroup>
                  <col class="col-stt" />
                  <col class="col-name" />
                  <col />
                  <col class="col-score" />
                  <col class="col-action" />
                </colgroup>
                <thead>
                  <tr>
                    <th>STT</th>
                    <th>Tên nhóm</th>
                    <th>Mô tả</th>
                    <th class="profile__score">Số điểm</th>
                    <th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in nhomTheoDiem" :key="item.ma_nhom">
                    <td>{{ index + 1 }}</td>
                    <td>[{{ item.ma_nhom }}]-{{ item.ten_nhom }}</td>
                    <td>
                      <el-tooltip
                        :content="item.mo_ta || ''"
                        placement="top"
                        :disabled="!biCat[item.ma_nhom]"
                        :show-after="200"
                        popper-class="profile-desc-tip"
                      >
                        <p :ref="(el) => ganMoTa(item.ma_nhom, el)" class="profile__desc">
                          {{ item.mo_ta || '—' }}
                        </p>
                      </el-tooltip>
                    </td>
                    <td class="profile__score">{{ item.diem }}</td>
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm"
                        :class="maDangChon === item.ma_nhom ? 'btn-success' : 'btn-outline-success'"
                        @click="xemNganh(item.ma_nhom)"
                      >
                        {{ maDangChon === item.ma_nhom ? 'Đang xem' : 'Xem ngành' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              </article>
            </div>
          </div>

          <p v-if="!duLieu.da_xong" class="holland-note holland-note__text">
            Hãy hoàn thành các phần trắc nghiệm để xem ngành phù hợp.
          </p>
          <p v-else-if="!duLieu.nganh.length" class="holland-note holland-note__text">
            Chưa có ngành đào tạo khớp với nhóm tính cách này.
          </p>
          <p v-else-if="!nhomNganhHienThi.length" class="holland-note holland-note__text">
            Không có nhóm ngành khớp mã {{ maDangChon }}.
          </p>
          <ul v-else class="major-list">
            <li v-for="nhom in nhomNganhHienThi" :key="nhom.ma" class="card major-card">
              <div class="card-body">
                <div class="major-card__title">
                  <h3>
                    {{ nhom.ten }}
                    <el-tooltip
                      :content="`Nhóm này có ${nhom.nganh.length} ngành`"
                      placement="top"
                      :show-after="200"
                    >
                      <span class="major-card__count">[{{ nhom.nganh.length }}]</span>
                    </el-tooltip>
                  </h3>
                  <div class="major-card__tools">
                    <button type="button" class="major-card__compare" @click="moSoSanh(nhom)">
                      So sánh
                      <span v-if="maNganhDaChon(nhom).length">({{ maNganhDaChon(nhom).length }}/3)</span>
                    </button>
                  <el-icon
                    v-if="nhom.nganh.length > SO_NGANH_HIEN"
                    class="major-card__more"
                    :size="22"
                    role="button"
                    tabindex="0"
                    :aria-expanded="!!nhomDaMo[nhom.ma]"
                    :aria-label="
                      nhomDaMo[nhom.ma]
                        ? 'Thu gọn'
                        : `Xem thêm ${nhom.nganh.length - SO_NGANH_HIEN} ngành`
                    "
                    @click="doiMoNhom(nhom.ma)"
                    @keydown.enter.prevent="doiMoNhom(nhom.ma)"
                    @keydown.space.prevent="doiMoNhom(nhom.ma)"
                  >
                    <ArrowUp v-if="nhomDaMo[nhom.ma]" />
                    <ArrowDown v-else />
                  </el-icon>
                  </div>
                </div>
                <div class="row g-2">
                  <div
                    v-for="nganh in nganhDangXem(nhom)"
                    :key="nganh.ma_nganh"
                    class="col-12 col-md-6 col-lg-3"
                  >
                    <CardMajor
                      :ten="nganh.ten_nganh"
                      :mo-ta="nganh.mo_ta || ''"
                      :muc-luong="nganh.muc_luong_tham_khao || ''"
                      :thoi-gian="nganh.thoi_gian_dao_tao || ''"
                      :hinh-anh="nganh.hinh_anh_mo_ta || ''"
                      :chon="daChonNganh(nhom, nganh)"
                      @chon="chonNganh(nhom, nganh)"
                    />
                  </div>
                </div>
              </div>
            </li>
          </ul>

          <el-dialog
            v-model="soSanhMo"
            title="So sánh ngành"
            width="min(1100px, 94vw)"
            append-to-body
            class="major-compare-dialog"
          >
            <div class="compare-wrap">
              <table class="compare-table">
                <thead>
                  <tr>
                    <th>Tiêu chí</th>
                    <th v-for="nganh in nganhSoSanh" :key="nganh.ma_nganh">{{ nganh.ten_nganh }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="tieuChi in TIEU_CHI_SO_SANH" :key="tieuChi.id">
                    <th>{{ tieuChi.ten }}</th>
                    <td v-for="nganh in nganhSoSanh" :key="nganh.ma_nganh">
                      {{ giaTriTieuChi(nganh, tieuChi.id) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </el-dialog>

          <div class="major-nav d-flex flex-wrap justify-content-between gap-2">
            <button type="button" class="btn btn-outline-success" :disabled="!buocTruoc" @click="lui">
              Phần trước
            </button>
            <button type="button" class="btn btn-success" @click="tiep">Xem kết quả</button>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<style src="./quiz-type.scss"></style>

<style scoped>
.top-group {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 28px;
  padding: 10px 14px;
  border: 1px solid #e3ebe6;
  border-radius: 12px;
  background: #f6faf7;
  box-shadow: 0 8px 22px rgba(28, 43, 35, 0.08);
}

.top-group__icon {
  flex: 0 0 48px;
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 10px;
  background: #e7edf2;
}

.top-group__body {
  flex: 1;
  min-width: 0;
}

.top-group__kicker {
  margin: 0 0 2px;
  color: #5c6b7a;
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  line-height: 1.3;
  text-transform: uppercase;
}

.top-group__name {
  margin: 0;
  color: #243044;
  font-size: 1rem;
  font-weight: 500;
}

.top-group__text {
  display: -webkit-box;
  margin: 2px 0 0;
  overflow: hidden;
  color: #4a5568;
  font-size: 0.9rem;
  font-weight: 400;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.top-group__score {
  flex: 0 0 auto;
  margin: 0;
  color: #3a4a5e;
  font-weight: 500;
  white-space: nowrap;
}

.profile {
  margin-top: 28px;
}

.profile__chart-card,
.profile__table {
  border-color: #e3ebe6;
  background: #f6faf7;
  box-shadow: 0 8px 22px rgba(28, 43, 35, 0.08);
}

.profile__chart-card .card-header {
  color: #121a28;
  font-weight: 500;
  background: #f4f7fb;
  border-bottom-color: #d5dee8;
}

.profile__table {
  min-width: 0;
  overflow-x: auto;
}

.profile__table table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  color: #162033;
  font-weight: 400;
}

.col-stt { width: 44px; }
.col-name { width: 22%; }
.col-score { width: 72px; }
.col-action { width: 108px; }

.profile__table th,
.profile__table td {
  padding: 10px 12px;
  border-bottom: 1px solid #d5dee8;
  text-align: left;
  vertical-align: top;
}

.profile__table th {
  color: #121a28;
  font-weight: 500;
  background: #f4f7fb;
}

.profile__table td:first-child,
.profile__table th:first-child,
.profile__score {
  text-align: center;
  white-space: nowrap;
}

.profile__table th:nth-child(4),
.profile__table th:last-child {
  text-align: center;
}

.profile__table td:last-child {
  text-align: center;
}

.profile__table .btn {
  padding: 2px 8px;
  font-size: 12px;
  white-space: nowrap;
}

.profile__desc {
  display: -webkit-box;
  width: 100%;
  margin: 0;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-height: 1.45;
}

.major-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin: 28px 0 0;
  padding: 0;
  list-style: none;
}

.major-card {
  margin: 0;
  border-color: #b7d0c2;
  background: #e5f2ea;
  box-shadow: 0 8px 22px rgba(28, 43, 35, 0.08);
}

.major-card__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0 0 12px;
}

.major-card__title h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.3;
}

.major-card__count {
  margin-left: 6px;
  cursor: help;
  font-weight: 700;
}

.major-card__tools {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 10px;
}

.major-card__compare {
  padding: 4px 12px;
  border: 1px solid #0c5c34;
  border-radius: 8px;
  background: #fff;
  color: #0c5c34;
  font-size: 0.92rem;
  font-weight: 600;
  line-height: 1.4;
}

.major-card__compare:hover {
  background: #0c5c34;
  color: #fff;
}

.major-card__more {
  flex: 0 0 auto;
  color: #0c5c34;
  cursor: pointer;
}

.major-card__more:hover {
  color: #084422;
}

.major-nav {
  margin-top: 28px;
}
</style>

<style>
.profile-desc-tip {
  max-width: 360px;
  line-height: 1.45;
}

.compare-wrap {
  overflow-x: auto;
}

.compare-table {
  width: 100%;
  border-collapse: collapse;
  color: #121a28;
  font-size: 0.95rem;
  line-height: 1.45;
}

.compare-table th,
.compare-table td {
  padding: 10px 12px;
  border: 1px solid #c5d5cc;
  vertical-align: top;
  white-space: pre-line;
}

.compare-table thead th {
  background: #0c5c34;
  color: #fff;
  font-weight: 600;
}

.compare-table tbody th {
  width: 180px;
  background: #e5f2ea;
  color: #0c5c34;
  font-weight: 700;
  text-align: left;
}

.compare-table td {
  background: #fff;
  min-width: 180px;
}
</style>
