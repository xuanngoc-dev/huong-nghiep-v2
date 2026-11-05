<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchTruongHoc } from '@/api/truongHoc'
import { GIAI_DOAN_THI_DAI_HOC_KEY, giaiDoanThiDaiHocList } from './giaiDoan'
import { routeNameGiaiDoanThiDaiHoc } from '../routes'
import CardNganhDaoTao from './CardNganhDaoTao.vue'

defineOptions({ name: 'ThptThiDaiHocChuaCo' })

const MA_NGANH_NOI_BAT = ['480201', '480107', '480208', '480103', '340101', '220201', '720101', '380101']
const MA_TRUONG_NOI_BAT = ['BKA', 'QSB', 'QSC', 'KHA', 'NTH', 'YHB', 'LPH', 'SPH']

const stages = giaiDoanThiDaiHocList
const route = useRoute()
const router = useRouter()
const currentStage = computed(() => route.meta.giaiDoan || '')
const nganhNoiBat = ref([])
const truongNoiBat = ref([])
const dangTaiNganh = ref(false)
const dangTaiTruong = ref(false)
const loiNganh = ref('')
const loiTruong = ref('')

function chonGiaiDoan(stage) {
  sessionStorage.setItem(GIAI_DOAN_THI_DAI_HOC_KEY, stage.code)
  const name = routeNameGiaiDoanThiDaiHoc(stage.code)
  if (name && name !== route.name) {
    router.push({ name })
    return
  }
  if (!name) router.push({ name: 'thpt-thi-dai-hoc' })
}

function moHuongDan() {
  router.push({ name: 'thpt-thi-dai-hoc-huong-dan-khao-sat' })
}

async function layTheoMa(fetchFn, codes, key, params = {}) {
  let coLoiMang = true
  const items = await Promise.all(codes.map(async (code) => {
    try {
      const data = await fetchFn(
        { page: 1, page_size: 20, q: code, ...params },
        { skipLoading: true },
      )
      coLoiMang = false
      return (data.items || []).find((item) => String(item[key] || '').toUpperCase() === code) || null
    } catch {
      return null
    }
  }))
  return { items: items.filter(Boolean), coLoiMang }
}

function moTaNganh(item) {
  if (item.mo_ta) return item.mo_ta
  if (item.ten_nhom_nganh && item.ten_nhom_nganh !== item.ten_nganh) return item.ten_nhom_nganh
  return ''
}

function moTaTruong(item) {
  return [item.ten_tinh_thanh, item.loai_co_so].filter(Boolean).join(' · ')
}

async function taiNganhNoiBat() {
  dangTaiNganh.value = true
  loiNganh.value = ''
  try {
    const { items, coLoiMang } = await layTheoMa(fetchNganh, MA_NGANH_NOI_BAT, 'ma_nganh', { trang_thai: 1 })
    nganhNoiBat.value = items
    if (!items.length && coLoiMang) loiNganh.value = 'Không tải được ngành nổi bật.'
  } finally {
    dangTaiNganh.value = false
  }
}

async function taiTruongNoiBat() {
  dangTaiTruong.value = true
  loiTruong.value = ''
  try {
    const { items, coLoiMang } = await layTheoMa(fetchTruongHoc, MA_TRUONG_NOI_BAT, 'ma_truong')
    truongNoiBat.value = items
    if (!items.length && coLoiMang) loiTruong.value = 'Không tải được trường nổi bật.'
  } finally {
    dangTaiTruong.value = false
  }
}

onMounted(() => {
  taiNganhNoiBat()
  taiTruongNoiBat()
})
</script>

<template>
  <section class="chua-co py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <article class="intro-card">
            <h2 class="h2 mb-2">Bạn chưa rõ mình phù hợp với ngành nghề nào?</h2>
            <p class="text-secondary mb-0">
              Làm khảo sát để hệ thống gợi ý ngành đào tạo gần với sở thích và năng lực của bạn.
            </p>
          </article>

          <article class="stages-card holland-overview mt-3">
            <h2 class="h4 mb-2">Bắt đầu từ khảo sát</h2>
            <p class="text-secondary mb-3">
              Bài trắc nghiệm Holland giúp bạn hiểu nhóm tính cách nổi bật, rồi đối chiếu với các ngành đào tạo.
              Xem hướng dẫn trước khi làm bài.
            </p>
            <button type="button" class="btn btn-success" @click="moHuongDan">
              Bắt đầu khảo sát
            </button>
          </article>

          <article class="stages-card mt-3">
            <h2 class="h4 mb-2">Ngành nổi bật</h2>
            <p class="text-secondary mb-3">Một số ngành nhiều thí sinh đang tìm hiểu, để bạn tham khảo trước khi làm khảo sát.</p>
            <p v-if="loiNganh" class="holland-note holland-note__text mb-0">{{ loiNganh }}</p>
            <p v-else-if="dangTaiNganh" class="text-secondary mb-0">Đang tải ngành…</p>
            <KhongCoDuLieu v-else-if="!nganhNoiBat.length" text="Chưa có ngành nổi bật." />
            <div v-else class="row g-3">
              <div v-for="item in nganhNoiBat" :key="item.id" class="col-12 col-md-6 col-lg-4">
                <CardNganhDaoTao
                  :ma="item.ma_nganh"
                  :ten="item.ten_nganh"
                  :ten-tieng-anh="item.ten_tieng_anh"
                  :mo-ta="moTaNganh(item)"
                  :hinh-anh="item.hinh_anh_mo_ta || ''"
                  :khoa="item.id"
                />
              </div>
            </div>
          </article>

          <article class="stages-card mt-3">
            <h2 class="h4 mb-2">Trường nổi bật</h2>
            <p class="text-secondary mb-3">Một số cơ sở đào tạo để bạn xem thêm khi đang tìm hướng đi.</p>
            <p v-if="loiTruong" class="holland-note holland-note__text mb-0">{{ loiTruong }}</p>
            <p v-else-if="dangTaiTruong" class="text-secondary mb-0">Đang tải trường…</p>
            <KhongCoDuLieu v-else-if="!truongNoiBat.length" text="Chưa có trường nổi bật." />
            <div v-else class="row g-3">
              <div v-for="item in truongNoiBat" :key="item.id" class="col-12 col-md-6 col-lg-4">
                <CardNganhDaoTao
                  :ma="item.ma_truong"
                  :ten="item.ten_truong"
                  :ten-tieng-anh="item.ten_tieng_anh || ''"
                  :mo-ta="item.gioi_thieu_ngan || moTaTruong(item)"
                  :hinh-anh="item.anh_dai_dien_url || item.logo_url || ''"
                  :khoa="item.id"
                />
              </div>
            </div>
          </article>

          <HoTroDinhHuong class="mt-3" />
          <CauHoiThuongGap class="mt-3" />
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="chon-lai-giai-doan" class="h4 mb-3">Chọn lại giai đoạn</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-giai-doan">
              <button
                v-for="stage in stages"
                :key="stage.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': currentStage === stage.code }"
                @click="chonGiaiDoan(stage)"
              >
                <img class="switch-card__image" :src="stage.image" :alt="stage.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">{{ stage.name }}</span>
                  <span class="switch-card__text">{{ stage.description }}</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.chua-co :is(.h2, .h4, .switch-card__name) {
  font-weight: 400;
}
</style>
