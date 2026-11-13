<template>
  <section ref="khuVucBai" class="quiz-flow" :aria-busy="dangDoiPhan">
    <div class="container-fluid">
      <div class="holland-overview">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Làm trắc nghiệm Holland</h2>
          <p class="holland-overview__lead">Chọn mức độ phù hợp với bạn theo cảm nhận đầu tiên.</p>
        </header>

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>

        <template v-else-if="cauHoiLoai.length">
          <BuocLamBai :ssid="ssid" :buoc="buoc" :hien-tai="loaiCauHoiId" />
          <div v-if="laDiemSo" class="quiz-scale" :class="{ 'is-switching': dangDoiPhan }">
            <table class="quiz-scale__table">
              <thead>
                <tr>
                  <th rowspan="2" class="quiz-scale__stt">STT</th>
                  <th rowspan="2" class="quiz-scale__question">Câu hỏi</th>
                  <th :colspan="MUC_DIEM.length">Câu trả lời</th>
                </tr>
                <tr>
                  <th v-for="muc in MUC_DIEM" :key="muc.diem" class="quiz-scale__level">{{ muc.ten }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(cau, cauIndex) in cauHoiLoai"
                  :key="cau.id"
                  :ref="(el) => ganTheCau(cauIndex, el)"
                  class="quiz-scale__row"
                  :class="{ 'is-active': cauIndex === chiSo, 'is-done': daChon[cau.id] }"
                  tabindex="-1"
                  role="radiogroup"
                  :aria-label="`Câu ${cauIndex + 1}. ${cau.noi_dung_cau_hoi}`"
                  :aria-disabled="khoaTraLoi"
                  @click="bamCau(cauIndex)"
                >
                  <td class="quiz-scale__stt">{{ cauIndex + 1 }}</td>
                  <td class="quiz-scale__question" :data-stt="cauIndex + 1">{{ cau.noi_dung_cau_hoi }}</td>
                  <td v-for="muc in MUC_DIEM" :key="muc.diem" class="quiz-scale__cell">
                    <label
                      v-if="dapAnTheoDiem(cau, muc.diem)"
                      class="quiz-scale__choice"
                      :class="{
                        'is-selected': daChon[cau.id] === dapAnTheoDiem(cau, muc.diem).id,
                        'is-locked': khoaTraLoi,
                      }"
                      @pointerup="chamDapAn($event, cauIndex, cau, dapAnTheoDiem(cau, muc.diem).id)"
                    >
                      <input
                        class="quiz-choice__radio"
                        type="radio"
                        :name="`cau-${cau.id}`"
                        :value="dapAnTheoDiem(cau, muc.diem).id"
                        :checked="daChon[cau.id] === dapAnTheoDiem(cau, muc.diem).id"
                        :disabled="khoaTraLoi"
                        :aria-label="muc.ten"
                        @change="chonDapAn(cau, dapAnTheoDiem(cau, muc.diem).id)"
                      />
                      <span class="quiz-scale__choice-text">{{ muc.ten }}</span>
                    </label>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="quiz-list" :class="{ 'is-switching': dangDoiPhan }">
            <article
              v-for="(cau, cauIndex) in cauHoiLoai"
              :key="cau.id"
              :ref="(el) => ganTheCau(cauIndex, el)"
              class="holland-panel quiz-question"
              :class="{ 'is-active': cauIndex === chiSo }"
              tabindex="-1"
              @click="bamCau(cauIndex)"
            >
              <h3 class="holland-panel__title">Câu {{ cauIndex + 1 }}. {{ cau.noi_dung_cau_hoi }}</h3>
              <div
                class="quiz-choices"
                role="radiogroup"
                :aria-label="`Câu ${cauIndex + 1}`"
                :aria-disabled="khoaTraLoi"
              >
                <label
                  v-for="(answer, index) in cau.cau_tra_loi"
                  :key="answer.id"
                  class="quiz-choice"
                  :class="{ 'is-selected': daChon[cau.id] === answer.id, 'is-locked': khoaTraLoi }"
                  @pointerup="chamDapAn($event, cauIndex, cau, answer.id)"
                >
                  <input
                    class="quiz-choice__radio"
                    type="radio"
                    :name="`cau-${cau.id}`"
                    :value="answer.id"
                    :checked="daChon[cau.id] === answer.id"
                    :disabled="khoaTraLoi"
                    @change="chonDapAn(cau, answer.id)"
                  />
                  <span class="quiz-choice__num">{{ index + 1 }}</span>
                  <span class="quiz-choice__text">{{ answer.noi_dung_cau_tra_loi }}</span>
                </label>
              </div>
            </article>
          </div>

          <p class="quiz-tip">Mẹo: chạm 2 lần vào đáp án để chọn và chuyển ngay sang câu tiếp theo.</p>
          <div ref="thanhDieuHuong" class="quiz-nav">
            <CustomButton
              class="quiz-nav__btn"
              plain
              type="primary"
              :disabled="viTriLoai <= 0 || dangDoiPhan || dangPhanTich"
              :loading="nutDangCho === 'lui'"
              @click="lui"
            >
              Phần trước
            </CustomButton>
            <span class="quiz-progress">Đã trả lời {{ daTraLoi }}/{{ cauHoiLoai.length }}</span>
            <CustomButton
              class="quiz-nav__btn"
              type="primary"
              :disabled="dangPhanTich || dangDoiPhan"
              :loading="dangPhanTich || nutDangCho === 'tiep'"
              @click="tiep"
            >
              {{ nutTiep }}
            </CustomButton>
          </div>
        </template>

        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải bài làm…</p>
      </div>
    </div>
    <LoadingSuyNghi :visible="dangPhanTich" />
    <Transition name="quiz-switch">
      <div
        v-if="dangDoiPhan"
        class="quiz-switch"
        role="status"
        aria-live="polite"
        aria-label="Đang chuyển phần"
      >
        <span class="quiz-switch__spin" />
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchNganhPhuHop, fetchPhienLamBai, luuTraLoi } from '@/api/phienKhaoSat'
import { fetchCauHinhEnduserDangApDung } from '@/api/cauHinhEnduser'
import LoadingSuyNghi from '@/components/guest/LoadingSuyNghi.vue'
import BuocLamBai from './BuocLamBai.vue'

defineOptions({ name: 'ThptLamTracNghiem' })

const route = useRoute()
const router = useRouter()
const ssid = computed(() => String(route.params.ssid || ''))
const loaiCauHoiId = computed(() => Number(route.params.loaiCauHoiId))
const dangTai = ref(false)
const dangPhanTich = ref(false)
const dangDoiPhan = ref(false)
const nutDangCho = ref('')
const khuVucBai = ref(null)
const CHO_PHAN_TICH_MS = 5000
const CHO_DOI_PHAN_MS = 480
let huyPhanTich = false
let henPhanTich = 0
let huyDoiPhan = false
let henDoiPhan = 0
const loi = ref('')
const phien = ref(null)
const daChon = ref({})
const chiSo = ref(0)
const theCau = ref([])
const thanhDieuHuong = ref(null)

// Các mức của kiểu trả lời điểm số, điểm 1–5 ứng với đáp án có cùng `diem` của từng câu.
const MUC_DIEM = [
  { diem: 1, ten: 'Rất không thích' },
  { diem: 2, ten: 'Không thích' },
  { diem: 3, ten: 'Bình thường' },
  { diem: 4, ten: 'Thích' },
  { diem: 5, ten: 'Rất thích' },
]
// Kiểu trả lời lấy từ cấu hình EndUser đang áp dụng; lỗi thì giữ cách hiển thị tình huống.
const kieuTraLoi = ref('tinh_huong')
const laDiemSo = computed(() => kieuTraLoi.value === 'diem_so')

const cauHoi = computed(() => phien.value?.cau_hoi || [])
const cauHoiLoai = ref([])

function dapAnTheoDiem(cau, diem) {
  return cau.cau_tra_loi.find((answer) => answer.diem === diem) || null
}

async function taiCauHinh() {
  try {
    const data = await fetchCauHinhEnduserDangApDung()
    kieuTraLoi.value = data.kieu_tra_loi === 'diem_so' ? 'diem_so' : 'tinh_huong'
  } catch {
    kieuTraLoi.value = 'tinh_huong'
  }
}

function xaoTron(list) {
  const next = [...list]
  for (let i = next.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    const item = next[i]
    next[i] = next[j]
    next[j] = item
  }
  return next
}

function sapXepNgauNhien() {
  const items = cauHoi.value.filter((item) => item.loai_cau_hoi_id === loaiCauHoiId.value)
  cauHoiLoai.value = xaoTron(items).map((item) => ({
    ...item,
    cau_tra_loi: xaoTron(item.cau_tra_loi || []),
  }))
  chiSo.value = 0
  theCau.value = []
}

const nhom = computed(() => {
  const groups = []
  for (const item of cauHoi.value) {
    const last = groups[groups.length - 1]
    if (!last || last.id !== item.loai_cau_hoi_id) {
      groups.push({ id: item.loai_cau_hoi_id, ten: item.ten_loai_cau_hoi })
    }
  }
  return groups
})

const tenLoai = computed(() => nhom.value.find((item) => item.id === loaiCauHoiId.value)?.ten || '')
const buoc = computed(() => {
  const steps = nhom.value.map((group) => {
    const items = cauHoi.value.filter((item) => item.loai_cau_hoi_id === group.id)
    const xong = items.length > 0 && items.every((item) => daChon.value[item.id])
    return { ...group, xong }
  })
  return [
    ...steps,
    { id: 'nganh-phu-hop', ten: 'Ngành phù hợp', xong: false },
    { id: 'ket-qua', ten: 'Kết quả', xong: false },
  ]
})
const viTriLoai = computed(() => nhom.value.findIndex((item) => item.id === loaiCauHoiId.value))
const laBuocCuoi = computed(() => viTriLoai.value >= 0 && viTriLoai.value === nhom.value.length - 1)
const nutTiep = computed(() => (laBuocCuoi.value ? 'Phân tích kết quả' : 'Phần tiếp theo'))
const daTraLoi = computed(() => cauHoiLoai.value.filter((item) => daChon.value[item.id]).length)
const khoaTraLoi = computed(
  () => cauHoi.value.length > 0 && cauHoi.value.every((item) => daChon.value[item.id]),
)
const cauDangChon = computed(() => cauHoiLoai.value[chiSo.value] || null)

function ganTheCau(index, el) {
  if (el) theCau.value[index] = el
  else delete theCau.value[index]
}

function chonCau(index, cuon = true, focus = false) {
  const max = cauHoiLoai.value.length - 1
  if (max < 0) return
  chiSo.value = Math.min(Math.max(index, 0), max)
  if (!cuon && !focus) return
  nextTick(() => {
    const el = theCau.value[chiSo.value]
    if (!el) return
    if (cuon) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    if (focus) el.focus({ preventScroll: true })
  })
}

// Chạm 2 lần (thiết bị cảm ứng) vào một đáp án: chọn đáp án đó rồi cuộn sang câu tiếp theo.
// Tự nhận diện qua pointerup vì dblclick trên di động không ổn định (trình duyệt dùng để phóng to).
const CHAM_DUP_MS = 350
let chamTruoc = { id: null, luc: 0 }
let boQuaBamCauDen = 0

function chamDapAn(event, cauIndex, cau, answerId) {
  if (event.pointerType !== 'touch' || khoaTraLoi.value || dangDoiPhan.value) return
  const dup = chamTruoc.id === answerId && event.timeStamp - chamTruoc.luc < CHAM_DUP_MS
  chamTruoc = dup ? { id: null, luc: 0 } : { id: answerId, luc: event.timeStamp }
  if (!dup) return
  if (daChon.value[cau.id] !== answerId) chonDapAn(cau, answerId)
  sangCauTiep(cauIndex)
}

function sangCauTiep(cauIndex) {
  // Sự kiện click của thẻ câu hỏi đến ngay sau pointerup và sẽ chọn lại câu vừa chạm, nên bỏ qua nó.
  boQuaBamCauDen = Date.now() + 500
  if (cauIndex < cauHoiLoai.value.length - 1) {
    chonCau(cauIndex + 1)
    return
  }
  // Câu cuối của phần: cuộn tới nút chuyển phần.
  nextTick(() => thanhDieuHuong.value?.scrollIntoView({ behavior: 'smooth', block: 'center' }))
}

function bamCau(cauIndex) {
  if (Date.now() < boQuaBamCauDen) return
  chonCau(cauIndex, false)
}

function phimDangNhap(event) {
  const tag = event.target?.tagName
  if (tag === 'TEXTAREA' || event.target?.isContentEditable) return true
  if (tag === 'INPUT' && event.target.type !== 'radio') return true
  return false
}

function xuLyPhim(event) {
  if (
    dangDoiPhan.value ||
    !cauHoiLoai.value.length ||
    phimDangNhap(event) ||
    event.altKey ||
    event.ctrlKey ||
    event.metaKey
  ) {
    return
  }
  if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
    event.preventDefault()
    chonCau(chiSo.value + 1)
    return
  }
  if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
    event.preventDefault()
    chonCau(chiSo.value - 1)
    return
  }
  if (khoaTraLoi.value || !/^[1-5]$/.test(event.key) || !cauDangChon.value) return
  // Điểm số: phím 1–5 là đúng mức điểm; tình huống: thứ tự đáp án đang hiển thị.
  const answer = laDiemSo.value
    ? dapAnTheoDiem(cauDangChon.value, Number(event.key))
    : cauDangChon.value.cau_tra_loi[Number(event.key) - 1]
  if (!answer) return
  event.preventDefault()
  chonDapAn(cauDangChon.value, answer.id)
}

onMounted(() => window.addEventListener('keydown', xuLyPhim))
onBeforeUnmount(() => {
  huyPhanTich = true
  huyDoiPhan = true
  window.clearTimeout(henPhanTich)
  window.clearTimeout(henDoiPhan)
  window.removeEventListener('keydown', xuLyPhim)
})

function queryMaNganh() {
  const ma = route.query.ma_nganh
  return ma ? { ma_nganh: ma } : {}
}

function moLoai(id, thayThe = false) {
  const location = {
    name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    params: { ssid: ssid.value, loaiCauHoiId: id },
    query: queryMaNganh(),
  }
  return thayThe ? router.replace(location) : router.push(location)
}

function choDoiPhan(ms) {
  return new Promise((resolve) => {
    henDoiPhan = window.setTimeout(resolve, ms)
  })
}

async function chuyenPhan(id, nut) {
  if (dangDoiPhan.value || dangPhanTich.value || id == null) return
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    await moLoai(id).catch(() => {})
    return
  }
  nutDangCho.value = nut
  dangDoiPhan.value = true
  try {
    await choDoiPhan(CHO_DOI_PHAN_MS)
    if (huyDoiPhan) return
    await moLoai(id).catch(() => {})
    if (huyDoiPhan) return
    await nextTick()
    khuVucBai.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } finally {
    dangDoiPhan.value = false
    nutDangCho.value = ''
  }
}

function doi(ms) {
  return new Promise((resolve) => {
    henPhanTich = window.setTimeout(resolve, ms)
  })
}

async function moNganhPhuHop() {
  if (dangPhanTich.value) return
  dangPhanTich.value = true
  try {
    await fetchNganhPhuHop(ssid.value)
    await doi(CHO_PHAN_TICH_MS)
    if (huyPhanTich) return
    await router.push({
      name: 'thpt-thi-dai-hoc-nganh-phu-hop',
      params: { ssid: ssid.value },
      query: queryMaNganh(),
    })
  } catch {
    dangPhanTich.value = false
    if (!huyPhanTich) ElMessage.error('Không phân tích được kết quả. Bạn thử lại giúp mình nhé.')
  }
}

function chuanHoaLoai() {
  if (!nhom.value.length) return
  if (nhom.value.some((item) => item.id === loaiCauHoiId.value)) return
  moLoai(nhom.value[0].id, true)
}

function lui() {
  const prev = nhom.value[viTriLoai.value - 1]
  if (prev) chuyenPhan(prev.id, 'lui')
}

function tiep() {
  const thieu = cauHoiLoai.value.findIndex((item) => !daChon.value[item.id])
  if (thieu >= 0) {
    //Bổ sung message thông báo
    ElMessage.error(
      laBuocCuoi.value
        ? 'Vui lòng hoàn thành câu hỏi trước khi phân tích kết quả.'
        : 'Vui lòng hoàn thành câu hỏi trước khi chuyển sang phần tiếp theo.',
    )
    chonCau(thieu, true, true)
    return
  }
  const next = nhom.value[viTriLoai.value + 1]
  if (next) {
    chuyenPhan(next.id, 'tiep')
    return
  }
  const chua = buoc.value.find((item) => item.id !== 'nganh-phu-hop' && item.id !== 'ket-qua' && !item.xong)
  if (chua) {
    ElMessage.error('Vui lòng hoàn thành các phần trước khi xem ngành phù hợp.')
    chuyenPhan(chua.id, 'tiep')
    return
  }
  moNganhPhuHop()
}

async function chonDapAn(cau, answerId) {
  if (khoaTraLoi.value || dangDoiPhan.value) return
  const truoc = daChon.value[cau.id]
  daChon.value = { ...daChon.value, [cau.id]: answerId }
  try {
    await luuTraLoi(ssid.value, cau.id, answerId)
  } catch (error) {
    const next = { ...daChon.value }
    if (truoc) next[cau.id] = truoc
    else delete next[cau.id]
    daChon.value = next
    const detail = error.response?.data?.detail
    if (error.response?.status === 400) {
      ElMessage.error(typeof detail === 'string' ? detail : 'Không lưu được đáp án.')
    }
  }
}

async function taiDeBai(value) {
  phien.value = null
  loi.value = ''
  daChon.value = {}
  if (!value) {
    loi.value = 'Không có mã phiên khảo sát.'
    return
  }
  dangTai.value = true
  try {
    const [data] = await Promise.all([fetchPhienLamBai(value), taiCauHinh()])
    phien.value = data
    const selected = {}
    for (const item of data.cau_hoi || []) {
      if (item.cau_tra_loi_id) selected[item.id] = item.cau_tra_loi_id
    }
    daChon.value = selected
    if (!data.cau_hoi?.length) loi.value = 'Phiên này chưa có câu hỏi.'
    chuanHoaLoai()
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    loi.value = status === 404 && typeof detail === 'string' ? detail : 'Không tải được bài trắc nghiệm.'
  } finally {
    dangTai.value = false
  }
}

watch(ssid, taiDeBai, { immediate: true })
watch([phien, loaiCauHoiId], sapXepNgauNhien)
</script>

<style src="./quiz-type.scss"></style>

<style scoped>
.quiz-flow {
  scroll-margin-top: 16px;
}

.quiz-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  align-items: start;
  margin-top: 28px;
  transition: opacity 0.2s ease;
}

.quiz-list.is-switching,
.quiz-scale.is-switching {
  opacity: 0.4;
  pointer-events: none;
}

.quiz-scale {
  margin-top: 28px;
  overflow: hidden;
  border: 1px solid #d7ebe0;
  border-radius: 12px;
  background: #fff;
  transition: opacity 0.2s ease;
}

.quiz-scale__table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.quiz-scale__table th {
  padding: 10px 8px;
  border: 1px solid #d7ebe0;
  background: #edf7f0;
  color: #1d6b28;
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.35;
  text-align: center;
  vertical-align: middle;
}

.quiz-scale__table tr > :first-child {
  border-left: 0;
}

.quiz-scale__table tr > :last-child {
  border-right: 0;
}

.quiz-scale__table thead tr:first-child th {
  border-top: 0;
}

.quiz-scale__table tbody tr:last-child td {
  border-bottom: 0;
}

.quiz-scale__table td {
  padding: 10px 8px;
  border: 1px solid #e6ece8;
  color: #162033;
  line-height: 1.45;
  vertical-align: middle;
}

th.quiz-scale__stt {
  width: 64px;
}

th.quiz-scale__question {
  width: 40%;
}

td.quiz-scale__stt {
  color: #1d6b28;
  font-weight: 500;
  text-align: center;
}

.quiz-scale__row {
  cursor: pointer;
  scroll-margin: 24px;
  transition: background-color 0.2s ease;
}

.quiz-scale__row:focus {
  outline: none;
}

.quiz-scale__row:hover,
.quiz-scale__row.is-done {
  background: #f6fbf7;
}

.quiz-scale__row.is-active {
  background: #edfff0;
  box-shadow: inset 3px 0 0 var(--guest-primary);
}

.quiz-scale__cell {
  text-align: center;
}

.quiz-scale__choice {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 36px;
  margin: 0;
  border-radius: 8px;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

.quiz-scale__choice .quiz-choice__radio {
  width: 18px;
  height: 18px;
  margin: 0;
}

.quiz-scale__choice.is-selected {
  background: #d9f3dc;
}

.quiz-scale__choice.is-locked,
.quiz-scale__choice.is-locked .quiz-choice__radio {
  cursor: default;
}

/* Tên mức đã có ở tiêu đề cột trên màn rộng, chỉ hiện trong ô khi chuyển sang dạng thẻ. */
.quiz-scale__choice-text {
  display: none;
}

@media (max-width: 767px) {
  .quiz-scale {
    border: 0;
    background: transparent;
  }

  .quiz-scale__table {
    display: block;
  }

  .quiz-scale__table thead {
    display: none;
  }

  .quiz-scale__table tbody {
    display: grid;
    gap: 12px;
  }

  .quiz-scale__row {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 6px;
    padding: 12px;
    border: 1px solid #d7ebe0;
    border-radius: 12px;
    background: #f3faf5;
  }

  .quiz-scale__row.is-active {
    border-color: var(--guest-primary);
    box-shadow: 0 10px 28px rgba(var(--guest-primary-rgb), 0.16);
  }

  .quiz-scale__table td {
    padding: 0;
    border: 0;
  }

  td.quiz-scale__stt {
    display: none;
  }

  td.quiz-scale__question {
    grid-column: 1 / -1;
    margin-bottom: 4px;
    font-weight: 500;
  }

  td.quiz-scale__question::before {
    content: 'Câu ' attr(data-stt) '. ';
    color: #1d6b28;
  }

  .quiz-scale__choice {
    flex-direction: column;
    gap: 4px;
    min-height: 0;
    padding: 6px 2px;
    border: 1px solid #e6ece8;
    background: #fff;
  }

  .quiz-scale__choice.is-selected {
    border-color: #8ecf93;
  }

  .quiz-scale__choice-text {
    display: block;
    color: #2c3a4d;
    font-size: 0.75rem;
    line-height: 1.25;
  }
}

.quiz-switch {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: grid;
  place-items: center;
  background: color-mix(in srgb, #f6fbf7 72%, transparent);
  backdrop-filter: blur(1px);
}

.quiz-switch__spin {
  width: 28px;
  height: 28px;
  border: 3px solid color-mix(in srgb, var(--guest-primary, #3f9643) 24%, transparent);
  border-top-color: var(--guest-primary, #3f9643);
  border-radius: 50%;
  animation: quiz-switch-spin 0.7s linear infinite;
}

.quiz-switch-enter-active,
.quiz-switch-leave-active {
  transition: opacity 0.16s ease;
}

.quiz-switch-enter-from,
.quiz-switch-leave-to {
  opacity: 0;
}

@keyframes quiz-switch-spin {
  to {
    transform: rotate(360deg);
  }
}

.quiz-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 12px 20px;
  margin-top: 28px;
  padding-bottom: 28px;
}

.quiz-nav__btn {
  height: 42px;
  margin: 0;
  padding: 0 22px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
}

.quiz-hint {
  margin: -4px 0 0;
  color: #2c3a4d;
  font-size: 0.92rem;
  font-weight: 400;
}

.quiz-question.holland-panel {
  width: 100%;
  border-color: #d7ebe0;
  background: #f3faf5;
  box-shadow: none;
  cursor: pointer;
  scroll-margin: 24px;
  transition:
    background-color 0.25s ease,
    border-color 0.25s ease,
    box-shadow 0.25s ease;
}

.quiz-question.holland-panel:focus {
  outline: none;
}

.quiz-question.holland-panel.is-active {
  border-color: var(--guest-primary);
  background: #edfff0;
  box-shadow: 0 10px 28px rgba(var(--guest-primary-rgb), 0.16);
}

.quiz-choices {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.quiz-choice {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 0;
  padding: 10px 12px;
  border: 1px solid #e6ece8;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  /* Tắt phóng to khi chạm 2 lần để dùng cử chỉ này chọn đáp án và sang câu tiếp. */
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

.quiz-tip {
  display: none;
  margin: 12px 0 0;
  color: #5a6e63;
  font-size: 0.875rem;
  line-height: 1.5;
  text-align: center;
}

/* Chỉ thiết bị cảm ứng mới có cử chỉ chạm 2 lần. */
@media (hover: none) and (pointer: coarse) {
  .quiz-tip {
    display: block;
  }
}

.quiz-choice.is-selected {
  border-color: #8ecf93;
  background: #d9f3dc;
}

.quiz-choice.is-selected .quiz-choice__num,
.quiz-choice.is-selected .quiz-choice__text {
  color: #121a28;
}

.quiz-choice.is-selected .quiz-choice__radio {
  accent-color: var(--guest-primary);
}

.quiz-choice.is-locked {
  cursor: default;
}

.quiz-choice.is-locked .quiz-choice__radio {
  cursor: default;
}

.quiz-choice__radio {
  flex: 0 0 auto;
  margin-top: 0.2rem;
  accent-color: var(--guest-primary);
}

.quiz-choice__num {
  flex: 0 0 auto;
  color: #1d6b28;
  font-weight: 500;
  line-height: 1.45;
}

.quiz-choice__text {
  flex: 1;
  min-width: 0;
  color: #162033;
  font-weight: 400;
  line-height: 1.45;
}

.quiz-progress {
  align-self: center;
  color: #2c3a4d;
  font-size: 0.92rem;
  font-weight: 400;
}

@media (max-width: 767px) {
  .quiz-progress {
    order: -1;
    flex-basis: 100%;
    text-align: center;
  }

  .quiz-nav__btn {
    flex: 1 1 0;
    height: 48px;
    font-size: 1rem;
  }
}

@media (min-width: 768px) {
  .quiz-list {
    grid-template-columns: 1fr 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .quiz-list,
  .quiz-scale,
  .quiz-scale__row,
  .quiz-switch__spin,
  .quiz-switch-enter-active,
  .quiz-switch-leave-active {
    transition: none;
    animation: none;
  }
}
</style>
