<template>
  <section class="quiz-flow">
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
              class="top-group__image"
              :src="anhNhomCao"
              :alt="`Hình minh họa nhóm ${nhomCaoNhat.ten_nhom}`"
              @error="anhNhomHong = true"
            />
            <div class="top-group__body">
              <p class="top-group__kicker">Nhóm điểm cao nhất</p>
              <div class="top-group__heading">
                <h3 class="top-group__name">[{{ nhomCaoNhat.ma_nhom }}]-{{ nhomCaoNhat.ten_nhom }}</h3>
                <p class="top-group__score">{{ nhomCaoNhat.diem }} điểm</p>
              </div>
              <p class="top-group__text">{{ nhomCaoNhat.mo_ta || 'Chưa có mô tả cho nhóm này.' }}</p>
            </div>
          </article>

          <div v-if="nhomTop.length" class="row g-3 profile">
            <div class="col-12 col-lg-5">
              <article class="profile__panel profile__chart-card">
                <header class="profile__head">
                  <h3 class="profile__title">Biểu đồ Holland</h3>
                  <p class="profile__sub">Đủ 6 nhóm, điểm đậm là 3 nhóm nổi bật</p>
                </header>
                <div class="profile__chart">
                  <BieuDoRadar
                    :height="380"
                    :categories="nhomBieuDo.map((item) => item.ten_nhom)"
                    :values="nhomBieuDo.map((item) => item.diem)"
                    :noi-bat="viTriNoiBat"
                    series-name="Điểm Holland"
                  />
                </div>
              </article>
            </div>
            <div class="col-12 col-lg-7">
              <article ref="bang" class="profile__panel">
                <header class="profile__head">
                  <h3 class="profile__title">Top {{ nhomTop.length }} nhóm nổi bật</h3>
                  <p class="profile__sub">Chọn một nhóm để xem các ngành phù hợp</p>
                </header>
                <ol class="rank-list">
                  <li
                    v-for="(item, index) in nhomTop"
                    :key="item.ma_nhom"
                    class="rank-item"
                    :class="[`rank-item--${index + 1}`, { 'is-active': maDangChon === item.ma_nhom }]"
                  >
                    <span class="rank-item__no" aria-hidden="true">{{ index + 1 }}</span>
                    <div class="rank-item__main">
                      <div class="rank-item__heading">
                        <span class="rank-item__code">{{ item.ma_nhom }}</span>
                        <h4 class="rank-item__name">{{ item.ten_nhom }}</h4>
                        <span class="rank-item__score">{{ item.diem }} điểm</span>
                      </div>
                      <div
                        class="rank-item__bar"
                        role="progressbar"
                        :aria-valuenow="item.diem"
                        aria-valuemin="0"
                        :aria-valuemax="nhomCaoNhat?.diem || 0"
                        :aria-label="`Điểm nhóm ${item.ten_nhom}`"
                      >
                        <span :style="{ width: `${tyLeDiem(item)}%` }" />
                      </div>
                      <el-tooltip
                        :content="item.mo_ta || ''"
                        placement="top"
                        :disabled="!biCat[item.ma_nhom]"
                        :show-after="200"
                        popper-class="profile-desc-tip"
                      >
                        <p :ref="(el) => ganMoTa(item.ma_nhom, el)" class="rank-item__desc">
                          {{ item.mo_ta || 'Chưa có mô tả cho nhóm này.' }}
                        </p>
                      </el-tooltip>
                    </div>
                    <button
                      type="button"
                      class="rank-item__action"
                      :aria-pressed="maDangChon === item.ma_nhom"
                      @click="xemNganh(item.ma_nhom)"
                    >
                      {{ maDangChon === item.ma_nhom ? 'Đang xem' : 'Xem ngành' }}
                    </button>
                  </li>
                </ol>
              </article>
            </div>
          </div>

          <p v-if="!duLieu.da_xong" class="holland-note holland-note__text">
            Hãy hoàn thành các phần trắc nghiệm để xem ngành phù hợp.
          </p>
          <p v-else-if="loiNganh" class="holland-note holland-note__text">{{ loiNganh }}</p>
          <p v-else-if="dangTaiNganh" class="holland-overview__lead text-center">Đang tải ngành…</p>
          <p v-else-if="!nhomNganhHienThi.length" class="holland-note holland-note__text">
            Chưa có ngành đào tạo khớp mã {{ maDangChon }}.
          </p>
          <template v-else>
            <ul class="major-list">
              <li v-for="nhom in nhomNganhDangXem" :key="nhom.ma" class="card major-card">
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
                  </div>
                </div>
                <el-collapse-transition v-for="phan in phanNganh(nhom)" :key="phan.id">
                  <div v-show="phan.hien" :class="{ 'major-card__extra': phan.id === 'them' }">
                    <div class="row g-2">
                      <div
                        v-for="(nganh, index) in phan.nganh"
                        :key="nganh.ma_nganh"
                        class="col-12 col-md-6 col-lg-3 major-card__item"
                        :style="{ '--delay': `${Math.min(index, 7) * 40}ms` }"
                      >
                        <CardMajor
                          :ten="nganh.ten_nganh"
                          :mo-ta="nganh.mo_ta || ''"
                          :muc-luong="noiMucLuong(nganh.muc_luong_tham_khao, ' · ')"
                          :thoi-gian="nganh.thoi_gian_dao_tao || ''"
                          :hinh-anh="nganh.hinh_anh_mo_ta || ''"
                          :chon="daChonNganh(nhom, nganh)"
                          @chon="chonNganh(nhom, nganh)"
                          @kham-pha="khamPhaNganh(nganh.ma_nganh)"
                        />
                      </div>
                    </div>
                  </div>
                </el-collapse-transition>
                <button
                  v-if="nhom.nganh.length > SO_NGANH_HIEN"
                  type="button"
                  class="major-card__more"
                  :aria-expanded="!!nhomDaMo[nhom.ma]"
                  @click="doiMoNhom(nhom.ma, $event)"
                >
                  {{ nhomDaMo[nhom.ma] ? 'Thu gọn' : `Xem thêm ${nhom.nganh.length - SO_NGANH_HIEN} ngành` }}
                  <el-icon class="major-card__more-icon" :class="{ 'is-open': nhomDaMo[nhom.ma] }"><ArrowDown /></el-icon>
                </button>
              </div>
            </li>
            </ul>
            <button
              v-if="conNhom"
              type="button"
              class="major-list__more"
              :disabled="dangTaiThem"
              :aria-busy="dangTaiThem"
              @click="taiThemNhom"
            >
              <el-icon v-if="dangTaiThem" class="is-loading"><Loading /></el-icon>
              {{ dangTaiThem ? 'Đang tải…' : 'Xem thêm' }}
            </button>
          </template>

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

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchNganhPhuHop, fetchPhienLamBai } from '@/api/phienKhaoSat'
import BieuDoRadar from '@/components/guest/BieuDoRadar.vue'
import CardMajor from './CardMajor.vue'
import anhA from '@/assets/guest/holland/a.svg'
import anhC from '@/assets/guest/holland/c.svg'
import anhE from '@/assets/guest/holland/e.svg'
import anhI from '@/assets/guest/holland/i.svg'
import anhR from '@/assets/guest/holland/r.svg'
import anhS from '@/assets/guest/holland/s.svg'
import anhMacDinh from '@/assets/guest/sinh-vien.jpg'
import BuocLamBai from './BuocLamBai.vue'
import { noiMucLuong } from '@/utils/capTenGiaTri'

const ANH_NHOM = { R: anhR, I: anhI, A: anhA, S: anhS, E: anhE, C: anhC }
const SO_NHOM_HIEN = 3
const SO_NGANH_HIEN = 4
const SO_NHOM_TOP = 3
// Thứ tự lục giác Holland, giữ cố định trên biểu đồ radar.
const THU_TU_HOLLAND = 'RIASEC'
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
const soNhomHien = ref(SO_NHOM_HIEN)
const dangTaiThem = ref(false)
const nganhDaChon = ref({})
const nhomDaMo = ref({})
const soSanhMo = ref(false)
const nganhSoSanh = ref([])
const bang = ref(null)
const biCat = ref({})
const theMoTa = new Map()
let quanSatBang = null
let henTaiThem = 0

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
const nhomTop = computed(() => nhomTheoDiem.value.slice(0, SO_NHOM_TOP))
const nhomBieuDo = computed(() =>
  [...(duLieu.value?.nhom || [])].sort((a, b) => {
    const viTri = (ma) => {
      const index = THU_TU_HOLLAND.indexOf(ma)
      return index < 0 ? THU_TU_HOLLAND.length : index
    }
    return viTri(a.ma_nhom) - viTri(b.ma_nhom) || a.ma_nhom.localeCompare(b.ma_nhom)
  }),
)
const viTriNoiBat = computed(() => {
  const maTop = nhomTop.value.map((item) => item.ma_nhom)
  return nhomBieuDo.value.flatMap((item, index) => (maTop.includes(item.ma_nhom) ? [index] : []))
})

function tyLeDiem(nhom) {
  const caoNhat = nhomCaoNhat.value?.diem || 0
  if (caoNhat <= 0) return 0
  return Math.round((nhom.diem / caoNhat) * 100)
}
const anhNhomHong = ref(false)
const anhNhomCao = computed(() => {
  const ma = nhomCaoNhat.value?.ma_nhom
  if (!ma || anhNhomHong.value) return anhMacDinh
  return ANH_NHOM[ma] || anhMacDinh
})
const maDangChon = computed(() => maDangXem.value || nhomCaoNhat.value?.ma_nhom || '')
const nganhTheoMa = ref({})
const dangTaiNganh = ref(false)
const loiNganh = ref('')
let lanTaiNganh = 0

function maHollandCua(nganh) {
  return (nganh.ma_holand || []).map((ma) => String(ma).toUpperCase())
}

// Điểm của ngành theo kết quả trắc nghiệm: cộng điểm các nhóm Holland mà ngành có.
function diemNganh(nganh) {
  const diemTheoMa = new Map(nhomTheoDiem.value.map((nhom) => [nhom.ma_nhom, nhom.diem]))
  return maHollandCua(nganh).reduce((tong, ma) => tong + (diemTheoMa.get(ma) || 0), 0)
}

// Ngành có mã Holland đang xem, gom các ngành cùng nhóm ngành vào một card.
const nhomNganhHienThi = computed(() => {
  const ma = maDangChon.value
  const danhSach = nganhTheoMa.value[ma]
  if (!ma || !danhSach) return []
  const groups = new Map()
  for (const item of danhSach) {
    const key = item.ma_nhom_nganh || item.ten_nhom_nganh
    if (!groups.has(key)) {
      groups.set(key, { ma: key, ten: item.ten_nhom_nganh, nganh: [], diem: 0 })
    }
    const group = groups.get(key)
    group.nganh.push(item)
    group.diem = Math.max(group.diem, diemNganh(item))
  }
  return [...groups.values()]
    .map((group) => ({
      ...group,
      nganh: [...group.nganh].sort((a, b) => {
        const uuA = maHollandCua(a)[0] === ma ? 0 : 1
        const uuB = maHollandCua(b)[0] === ma ? 0 : 1
        return uuA - uuB || diemNganh(b) - diemNganh(a) || a.ten_nganh.localeCompare(b.ten_nganh, 'vi')
      }),
    }))
    .sort((a, b) => b.diem - a.diem || b.nganh.length - a.nganh.length || a.ten.localeCompare(b.ten, 'vi'))
})

async function taiNganhTheoMa(ma) {
  if (!ma || nganhTheoMa.value[ma]) return
  const lan = ++lanTaiNganh
  dangTaiNganh.value = true
  loiNganh.value = ''
  try {
    const data = await fetchNganh(
      { ma_holand: ma, trang_thai: 1, page: 1, page_size: 1000 },
      { skipLoading: true },
    )
    nganhTheoMa.value = { ...nganhTheoMa.value, [ma]: data.items || [] }
  } catch {
    if (lan === lanTaiNganh) loiNganh.value = 'Không tải được ngành đào tạo.'
  } finally {
    if (lan === lanTaiNganh) dangTaiNganh.value = false
  }
}
const nhomNganhDangXem = computed(() => nhomNganhHienThi.value.slice(0, soNhomHien.value))
const conNhom = computed(() => Math.max(nhomNganhHienThi.value.length - soNhomHien.value, 0))

function huyTaiThem() {
  if (!henTaiThem) return
  clearTimeout(henTaiThem)
  henTaiThem = 0
  dangTaiThem.value = false
}

function taiThemNhom() {
  if (dangTaiThem.value || !conNhom.value) return
  dangTaiThem.value = true
  henTaiThem = window.setTimeout(() => {
    soNhomHien.value += SO_NHOM_HIEN
    dangTaiThem.value = false
    henTaiThem = 0
  }, 1000)
}

// Tách 4 ngành đầu và phần còn lại, phần còn lại mở/thu gọn có hiệu ứng.
function phanNganh(nhom) {
  const phan = [{ id: 'dau', nganh: nhom.nganh.slice(0, SO_NGANH_HIEN), hien: true }]
  if (nhom.nganh.length > SO_NGANH_HIEN) {
    phan.push({ id: 'them', nganh: nhom.nganh.slice(SO_NGANH_HIEN), hien: !!nhomDaMo.value[nhom.ma] })
  }
  return phan
}

function doiMoNhom(ma, event) {
  const dangMo = !!nhomDaMo.value[ma]
  nhomDaMo.value = { ...nhomDaMo.value, [ma]: !dangMo }
  if (!dangMo) return
  // Thu gọn nhóm dài thì cuộn lại đầu card nếu đầu card đã trôi khỏi màn hình.
  const card = event?.currentTarget?.closest('.major-card')
  window.setTimeout(() => {
    if (card && card.getBoundingClientRect().top < 0) card.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 320)
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
  if (id === 'muc_luong') return noiMucLuong(nganh.muc_luong_tham_khao) || noiChiTiet(chiTiet.muc_luong_tham_khao) || '—'
  if (id === 'do_phu_hop') return noiChiTiet(chiTiet.do_phu_hop) || doPhuHop(nganh) || '—'
  return noiChiTiet(chiTiet[id]) || '—'
}

function khamPhaNganh(ma) {
  const code = String(ma || '').trim()
  if (!code || !ssid.value) return
  router.push({
    name: 'thpt-thi-dai-hoc-chi-tiet-nganh',
    params: { ssid: ssid.value, maNganh: code },
    query: queryMaNganh(),
  })
}

function xemNganh(ma) {
  huyTaiThem()
  maDangXem.value = ma
  soNhomHien.value = SO_NHOM_HIEN
  nganhDaChon.value = {}
  nhomDaMo.value = {}
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

function queryMaNganh() {
  const ma = route.query.ma_nganh
  return ma ? { ma_nganh: ma } : {}
}

async function chuyenVeLamBai(value) {
  const phien = await fetchPhienLamBai(value)
  const cau = phien.cau_hoi || []
  const thieu = cau.find((item) => !item.cau_tra_loi_id) || cau[0]
  if (!thieu) return false
  ElMessage.error('Vui lòng hoàn thành các câu hỏi trước khi xem ngành phù hợp.')
  await router.replace({
    name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    params: { ssid: value, loaiCauHoiId: thieu.loai_cau_hoi_id },
    query: queryMaNganh(),
  })
  return true
}

async function taiNganh(value) {
  huyTaiThem()
  duLieu.value = null
  maDangXem.value = ''
  soNhomHien.value = SO_NHOM_HIEN
  nganhDaChon.value = {}
  nhomDaMo.value = {}
  soSanhMo.value = false
  nganhSoSanh.value = []
  loi.value = ''
  if (!value) {
    loi.value = 'Không có mã phiên khảo sát.'
    return
  }
  dangTai.value = true
  let roiTrang = false
  try {
    const data = await fetchNganhPhuHop(value)
    if (!data.da_xong) {
      roiTrang = await chuyenVeLamBai(value)
      if (roiTrang) return
    }
    duLieu.value = data
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    loi.value = status === 404 && typeof detail === 'string' ? detail : 'Không tải được ngành phù hợp.'
  } finally {
    if (!roiTrang) dangTai.value = false
  }
}

function lui() {
  if (!buocTruoc.value) return
  router.push({
    name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    params: { ssid: ssid.value, loaiCauHoiId: buocTruoc.value.id },
    query: queryMaNganh(),
  })
}

function tiep() {
  if (!duLieu.value?.da_xong) {
    ElMessage.error('Vui lòng hoàn thành các phần trước khi xem kết quả.')
    return
  }
  router.push({ name: 'thpt-thi-dai-hoc-ket-qua', params: { ssid: ssid.value }, query: queryMaNganh() })
}

watch(ssid, taiNganh, { immediate: true })
watch(maDangChon, taiNganhTheoMa, { immediate: true })
watch(nhomCaoNhat, () => {
  anhNhomHong.value = false
})
watch(nhomTop, () => nextTick(doMoTa))
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
  huyTaiThem()
  quanSatBang?.disconnect()
  quanSatBang = null
})
</script>

<style src="./quiz-type.scss"></style>

<style scoped>
.top-group {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 28px;
  min-height: 128px;
  padding: 16px 18px;
  border: 1px solid #e3ebe6;
  border-radius: 12px;
  background: #f6faf7;
  box-shadow: 0 8px 22px rgba(28, 43, 35, 0.08);
}

.top-group__image {
  flex: 0 0 168px;
  width: 168px;
  height: 108px;
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

.top-group__heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.top-group__name {
  margin: 0;
  color: #243044;
  font-size: 1.05rem;
  font-weight: 500;
}

.top-group__text {
  display: -webkit-box;
  margin: 6px 0 0;
  overflow: hidden;
  color: #4a5568;
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.top-group__score {
  flex: 0 0 auto;
  margin: 0;
  padding: 2px 10px;
  border-radius: 0.375rem;
  background: #e7f5ea;
  color: #0c5c34;
  font-weight: 400;
  white-space: nowrap;
}

@media (max-width: 575.98px) {
  .top-group {
    align-items: stretch;
    flex-direction: column;
  }

  .top-group__image {
    flex-basis: auto;
    width: 100%;
    height: 140px;
  }
}

.profile {
  --pf-primary: #1f7a4d;
  --pf-primary-deep: #145c38;
  --pf-soft: #eaf5ef;
  --pf-border: #dfeae3;
  --pf-text: #1f2d26;
  --pf-muted: #5f7268;

  margin-top: 28px;
}

.profile__panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 18px 20px;
  border: 1px solid var(--pf-border);
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 6px 18px rgba(20, 70, 45, 0.06);
}

.profile__head {
  margin-bottom: 12px;
}

.profile__title {
  margin: 0;
  color: var(--pf-text);
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.4;
}

.profile__sub {
  margin: 2px 0 0;
  color: var(--pf-muted);
  font-size: 0.85rem;
  line-height: 1.4;
}

.profile__chart {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
}

.rank-list {
  display: grid;
  flex: 1;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.rank-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border: 1px solid var(--pf-border);
  border-radius: 12px;
  background: #fbfdfc;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    box-shadow 0.2s ease;
}

.rank-item:hover {
  border-color: color-mix(in srgb, var(--pf-primary) 35%, var(--pf-border));
  box-shadow: 0 4px 12px rgba(20, 70, 45, 0.08);
}

.rank-item.is-active {
  border-color: var(--pf-primary);
  background: var(--pf-soft);
}

.rank-item__no {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #eef2f0;
  color: var(--pf-muted);
  font-size: 0.95rem;
  font-weight: 700;
}

.rank-item--1 .rank-item__no {
  background: var(--pf-primary);
  color: #fff;
}

.rank-item--2 .rank-item__no {
  background: #cfe7d9;
  color: var(--pf-primary-deep);
}

.rank-item--3 .rank-item__no {
  background: #e3f0e8;
  color: var(--pf-primary-deep);
}

.rank-item__main {
  min-width: 0;
}

.rank-item__heading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rank-item__code {
  flex: 0 0 auto;
  padding: 1px 8px;
  border-radius: 6px;
  background: var(--pf-soft);
  color: var(--pf-primary-deep);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.rank-item.is-active .rank-item__code {
  background: #fff;
}

.rank-item__name {
  flex: 1;
  min-width: 0;
  margin: 0;
  overflow: hidden;
  color: var(--pf-text);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-item__score {
  flex: 0 0 auto;
  color: var(--pf-primary-deep);
  font-size: 0.9rem;
  font-weight: 700;
  white-space: nowrap;
}

.rank-item__bar {
  height: 6px;
  margin-top: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #e8efeb;
}

.rank-item__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #4fa877, var(--pf-primary));
  transition: width 0.5s ease;
}

.rank-item__desc {
  display: -webkit-box;
  margin: 8px 0 0;
  overflow: hidden;
  color: var(--pf-muted);
  font-size: 0.88rem;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.rank-item__action {
  padding: 6px 12px;
  border: 1px solid var(--pf-primary);
  border-radius: 8px;
  background: #fff;
  color: var(--pf-primary);
  font-size: 0.85rem;
  font-weight: 400;
  line-height: 1.3;
  white-space: nowrap;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
}

.rank-item__action:hover,
.rank-item.is-active .rank-item__action {
  background: var(--pf-primary);
  color: #fff;
}

.rank-item__action:focus-visible {
  outline: 2px solid color-mix(in srgb, var(--pf-primary) 40%, transparent);
  outline-offset: 2px;
}

@media (max-width: 575.98px) {
  .profile__panel {
    padding: 14px;
  }

  .rank-item {
    grid-template-columns: auto minmax(0, 1fr);
    gap: 10px 12px;
  }

  .rank-item__action {
    grid-column: 1 / -1;
    width: 100%;
  }
}

.major-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin: 28px 0 0;
  padding: 0;
  list-style: none;
}

.major-list__more {
  display: flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  margin: 16px auto 0;
  padding: 8px 18px;
  border: 1px solid #0c5c34;
  border-radius: 8px;
  background: #fff;
  color: #0c5c34;
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.4;
  cursor: pointer;
}

.major-list__more:hover:not(:disabled) {
  background: #0c5c34;
  color: #fff;
}

.major-list__more:disabled {
  opacity: 0.65;
  cursor: wait;
}

.major-card__more {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 12px auto 0;
  padding: 6px 16px;
  border: 1px solid #0c5c34;
  border-radius: 8px;
  background: #fff;
  color: #0c5c34;
  font-size: 0.95rem;
  line-height: 1.4;
}

.major-card__more:hover {
  background: #0c5c34;
  color: #fff;
}

.major-card__more-icon {
  transition: transform 0.3s ease;
}

.major-card__more-icon.is-open {
  transform: rotate(180deg);
}

/* Hàng tiếp nối lưới 4 ngành đầu, giữ khoảng cách bằng gutter của .row. */
.major-card__extra {
  padding-top: 0.5rem;
}

.major-card__extra .major-card__item {
  animation: major-hien 0.35s ease both;
  animation-delay: var(--delay, 0ms);
}

@keyframes major-hien {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .major-card__more-icon,
  .major-card__extra .major-card__item {
    animation: none;
    transition: none;
  }
}

.major-card {
  margin: 0;
  border-color: #b7d0c2;
  background: #ffffff;
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
  font-weight: 400;
  line-height: 1.4;
}

.major-card__compare:hover {
  background: #0c5c34;
  color: #fff;
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
  font-weight: 400;
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
