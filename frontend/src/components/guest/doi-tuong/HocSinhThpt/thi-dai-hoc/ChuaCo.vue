<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { GIAI_DOAN_THI_DAI_HOC_KEY, giaiDoanThiDaiHocList } from './giaiDoan'
import { routeNameGiaiDoanThiDaiHoc } from '../routes'

defineOptions({ name: 'ThptThiDaiHocChuaCo' })

const stages = giaiDoanThiDaiHocList
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const currentStage = computed(() => route.meta.giaiDoan || '')

const pathSteps = [
  { label: 'Bắt đầu', current: true },
  { label: 'Sở thích & đam mê' },
  { label: 'Kỹ năng & khả năng' },
  { label: 'Môi trường làm việc' },
  { label: 'Phong cách làm việc' },
  { label: 'Ngành phù hợp' },
  { label: 'Kết quả' },
]

const beforeTips = [
  'Dành khoảng 5 phút để thư giãn và tập trung.',
  'Nhập thông tin của bản thân để hệ thống giúp phân tích kết quả 1 cách chuẩn xác nhất.',
  'Hiểu rằng trắc nghiệm này nhằm giúp bạn hiểu mình hơn, không phải để tạo hình ảnh “hoàn hảo” cho người khác.',
  'Trung thực với bản thân, không khen hoặc chê quá mức.',
  'Hoàn thành bài trong khoảng 20 phút để kết quả phản ánh đúng nhất.',
]

const duringTips = [
  'Trả lời nhanh, tự nhiên, theo cảm nhận đầu tiên — đừng suy nghĩ quá nhiều.',
  'Với mỗi mô tả, hãy chọn mức độ phù hợp với bạn theo 5 mức:',
]

const scores = [
  { code: 'A', point: 5, tone: 'a' },
  { code: 'B', point: 4, tone: 'b' },
  { code: 'C', point: 3, tone: 'c' },
  { code: 'D', point: 2, tone: 'd' },
  { code: 'E', point: 1, tone: 'e' },
]

function chonGiaiDoan(stage) {
  sessionStorage.setItem(GIAI_DOAN_THI_DAI_HOC_KEY, stage.code)
  const name = routeNameGiaiDoanThiDaiHoc(stage.code)
  if (name && name !== route.name) {
    router.push({ name })
    return
  }
  if (!name) router.push({ name: 'thpt-thi-dai-hoc' })
}

function batDauHolland() {
  router.push({ name: 'danh-gia' })
}
</script>

<template>
  <section class="py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <article class="intro-card">
            <h2 class="h2 mb-2">Bạn chưa rõ mình phù hợp với ngành nghề nào?</h2>
            <p class="text-secondary mb-3">Đừng lo, đã có cẩm nang định hướng nghề.</p>
          </article>

          <div class="stages-card holland-overview mt-3">
            <header class="holland-overview__header">
              <h2 class="holland-overview__title">Tổng quan về trắc nghiệm Holland</h2>
              <p class="holland-overview__lead">
                Khám phá các nhóm ngành nghề được gợi ý sau khi hoàn thành bài trắc nghiệm.
              </p>
            </header>

            <article class="holland-intro">
              <div class="holland-intro__body">
                <!-- <span class="holland-intro__badge">Khám phá bản thân</span> -->
                <h3 class="holland-intro__title">Giới thiệu trắc nghiệm hướng nghiệp</h3>
                <p class="holland-intro__text">
                  Mô hình Holland Test được xây dựng trên nền tảng tâm lý học nghề nghiệp, dựa vào giả
                  thuyết rằng con người có thể được phân loại vào 6 nhóm tính cách nghề nghiệp RIASEC, và
                  mức độ phù hợp giữa tính cách với môi trường làm việc quyết định sự hài lòng, hiệu suất
                  và khả năng gắn bó lâu dài. Nhiều nghiên cứu đã chứng minh, khi làm việc trong môi
                  trường phù hợp với mã Holland, cá nhân có xu hướng giảm căng thẳng, tăng động lực và
                  phát triển bền vững hơn.
                </p>
              </div>
              <aside class="holland-duration">
                <span class="holland-kicker">Thời lượng dự kiến</span>
                <strong class="holland-duration__time">20 phút</strong>
                <p class="holland-duration__text">
                  Chọn nơi yên tĩnh và trả lời theo cảm nhận đầu tiên.
                </p>
              </aside>
            </article>

            <article class="holland-panel">
              <p class="holland-kicker">Lộ trình trắc nghiệm</p>
              <ol class="holland-path">
                <li
                  v-for="(step, index) in pathSteps"
                  :key="step.label"
                  class="holland-path__item"
                  :class="{ 'is-current': step.current }"
                >
                  <span class="holland-path__index">{{ index + 1 }}</span>
                  <span class="holland-path__label">{{ step.label }}</span>
                </li>
              </ol>
            </article>

            <div class="row g-3">
              <div class="col-md-6">
                <article class="holland-panel h-100">
                  <h3 class="holland-panel__title">Trước khi bắt đầu, bạn cần:</h3>
                  <ul class="holland-list">
                    <li v-for="tip in beforeTips" :key="tip">{{ tip }}</li>
                  </ul>
                </article>
              </div>
              <div class="col-md-6">
                <article class="holland-panel h-100">
                  <h3 class="holland-panel__title">Trong quá trình làm bài, bạn cần:</h3>
                  <ul class="holland-list">
                    <li v-for="tip in duringTips" :key="tip">{{ tip }}</li>
                  </ul>
                  <ul class="holland-scores">
                    <li v-for="score in scores" :key="score.code" class="holland-score">
                      <span class="holland-score__mark" :class="`is-${score.tone}`">{{ score.code }}</span>
                      <span class="holland-score__point" :class="`is-${score.tone}`">{{ score.point }} điểm</span>
                    </li>
                  </ul>
                </article>
              </div>
            </div>
            <div class="d-flex flex-wrap gap-2">
              <button type="button" class="btn btn-success" @click="batDauHolland">
                Bắt đầu trắc nghiệm Holland
              </button>
              <RouterLink v-if="!auth.isAuthenticated" class="btn btn-outline-success" :to="{ name: 'register' }">
                Đăng ký tài khoản
              </RouterLink>
            </div>
            <article class="holland-note">
              <h3 class="holland-note__title">Lưu ý:</h3>
              <p class="holland-note__text">
                Kết quả trắc nghiệm chỉ mang tính tham khảo, hỗ trợ định hướng ban đầu và không thay thế
                tư vấn hướng nghiệp chuyên sâu từ chuyên gia.
              </p>
              <p v-if="!auth.isAuthenticated" class="holland-note__text">
                Bạn có thể đăng ký tài khoản để lưu bài làm và tối ưu hóa việc khảo sát.
              </p>
            </article>
          </div>
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
