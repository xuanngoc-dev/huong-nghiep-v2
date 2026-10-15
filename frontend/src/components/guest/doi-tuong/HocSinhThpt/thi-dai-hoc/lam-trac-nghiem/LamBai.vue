<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchNganhPhuHop, fetchPhienLamBai, luuTraLoi } from '@/api/phienKhaoSat'
import LoadingSuyNghi from '@/components/guest/LoadingSuyNghi.vue'
import BuocLamBai from './BuocLamBai.vue'

defineOptions({ name: 'ThptLamTracNghiem' })

const route = useRoute()
const router = useRouter()
const ssid = computed(() => String(route.params.ssid || ''))
const loaiCauHoiId = computed(() => Number(route.params.loaiCauHoiId))
const dangTai = ref(false)
const dangPhanTich = ref(false)
const CHO_PHAN_TICH_MS = 5000
let huyPhanTich = false
let henPhanTich = 0
const loi = ref('')
const phien = ref(null)
const daChon = ref({})
const chiSo = ref(0)
const theCau = ref([])

const cauHoi = computed(() => phien.value?.cau_hoi || [])
const cauHoiLoai = ref([])

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

function phimDangNhap(event) {
  const tag = event.target?.tagName
  if (tag === 'TEXTAREA' || event.target?.isContentEditable) return true
  if (tag === 'INPUT' && event.target.type !== 'radio') return true
  return false
}

function xuLyPhim(event) {
  if (!cauHoiLoai.value.length || phimDangNhap(event) || event.altKey || event.ctrlKey || event.metaKey) return
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
  if (!/^[1-5]$/.test(event.key) || !cauDangChon.value) return
  const answer = cauDangChon.value.cau_tra_loi[Number(event.key) - 1]
  if (!answer) return
  event.preventDefault()
  chonDapAn(cauDangChon.value, answer.id)
}

onMounted(() => window.addEventListener('keydown', xuLyPhim))
onBeforeUnmount(() => {
  huyPhanTich = true
  window.clearTimeout(henPhanTich)
  window.removeEventListener('keydown', xuLyPhim)
})

function moLoai(id, thayThe = false) {
  const location = {
    name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    params: { ssid: ssid.value, loaiCauHoiId: id },
  }
  if (thayThe) router.replace(location)
  else router.push(location)
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
    await router.push({ name: 'thpt-thi-dai-hoc-nganh-phu-hop', params: { ssid: ssid.value } })
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
  if (prev) moLoai(prev.id)
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
    moLoai(next.id)
    return
  }
  const chua = buoc.value.find((item) => item.id !== 'nganh-phu-hop' && item.id !== 'ket-qua' && !item.xong)
  if (chua) {
    ElMessage.error('Vui lòng hoàn thành các phần trước khi xem ngành phù hợp.')
    moLoai(chua.id)
    return
  }
  moNganhPhuHop()
}

async function chonDapAn(cau, answerId) {
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
    const data = await fetchPhienLamBai(value)
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

<template>
  <section class="quiz-flow py-4">
    <div class="container-fluid">
      <div class="holland-overview">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Làm trắc nghiệm Holland</h2>
          <p class="holland-overview__lead">Chọn mức độ phù hợp với bạn theo cảm nhận đầu tiên.</p>
        </header>

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>

        <template v-else-if="cauHoiLoai.length">
          <BuocLamBai :ssid="ssid" :buoc="buoc" :hien-tai="loaiCauHoiId" />
          <div class="quiz-list">
            <article
              v-for="(cau, cauIndex) in cauHoiLoai"
              :key="cau.id"
              :ref="(el) => ganTheCau(cauIndex, el)"
              class="holland-panel quiz-question"
              :class="{ 'is-active': cauIndex === chiSo }"
              tabindex="-1"
              @click="chonCau(cauIndex, false)"
            >
              <h3 class="holland-panel__title">Câu {{ cauIndex + 1 }}. {{ cau.noi_dung_cau_hoi }}</h3>
              <div class="quiz-choices" role="radiogroup" :aria-label="`Câu ${cauIndex + 1}`">
                <label
                  v-for="(answer, index) in cau.cau_tra_loi"
                  :key="answer.id"
                  class="quiz-choice"
                  :class="{ 'is-selected': daChon[cau.id] === answer.id }"
                >
                  <input
                    class="quiz-choice__radio"
                    type="radio"
                    :name="`cau-${cau.id}`"
                    :value="answer.id"
                    :checked="daChon[cau.id] === answer.id"
                    @change="chonDapAn(cau, answer.id)"
                  />
                  <span class="quiz-choice__num">{{ index + 1 }}</span>
                  <span class="quiz-choice__text">{{ answer.noi_dung_cau_tra_loi }}</span>
                </label>
              </div>
            </article>
          </div>

          <div class="quiz-nav d-flex flex-wrap justify-content-between gap-2">
            <button type="button" class="btn btn-outline-success" :disabled="viTriLoai <= 0" @click="lui">
              Phần trước
            </button>
            <span class="quiz-progress">Đã chọn {{ daTraLoi }}/{{ cauHoiLoai.length }}</span>
            <button type="button" class="btn btn-success" :disabled="dangPhanTich" @click="tiep">{{ nutTiep }}</button>
          </div>
        </template>

        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải bài làm…</p>
      </div>
    </div>
    <LoadingSuyNghi :visible="dangPhanTich" />
  </section>
</template>

<style src="./quiz-type.scss"></style>

<style scoped>
.quiz-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  align-items: start;
  margin-top: 28px;
}

.quiz-nav {
  margin-top: 28px;
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

@media (min-width: 768px) {
  .quiz-list {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
