<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import Carousel from 'bootstrap/js/dist/carousel'

const sliderEl = ref(null)
let slider = null

const slides = [
  {
    kicker: 'Tính cách',
    title: 'Nhóm Holland R, I, A, S, E, C',
    text: 'Mỗi câu trả lời góp vào nhóm tính cách thực tế, nghiên cứu, nghệ thuật, xã hội, doanh nhân hoặc quy tắc.',
    background: 'linear-gradient(135deg, #1f7a4d, #3e9b68)',
  },
  {
    kicker: 'Ngành học',
    title: 'Gợi ý ngành và chuyên ngành',
    text: 'Sau bài trắc nghiệm, bạn xem các lĩnh vực đào tạo gần với điểm mạnh của mình.',
    background: 'linear-gradient(135deg, #145536, #1f7a4d)',
  },
  {
    kicker: 'Lộ trình',
    title: 'Lưu lại kết quả để xem lại',
    text: 'Đăng ký tài khoản để giữ lịch sử làm bài và đối chiếu khi chọn tổ hợp môn.',
    background: 'linear-gradient(135deg, #0f3d28, #1f7a4d)',
  },
]

const steps = [
  { title: 'Đăng ký', text: 'Tạo tài khoản miễn phí để lưu bài làm và hồ sơ.' },
  { title: 'Làm trắc nghiệm', text: 'Trả lời các câu hỏi theo nhóm tính cách Holland.' },
  { title: 'Xem gợi ý', text: 'Đối chiếu kết quả với ngành học và hướng nghề.' },
]

const groups = [
  { code: 'R', name: 'Thực tế', text: 'Thích làm việc cụ thể, máy móc và kỹ thuật.' },
  { code: 'I', name: 'Nghiên cứu', text: 'Thích phân tích, tìm hiểu và giải quyết vấn đề.' },
  { code: 'A', name: 'Nghệ thuật', text: 'Thích sáng tạo, thiết kế và thể hiện ý tưởng.' },
  { code: 'S', name: 'Xã hội', text: 'Thích hỗ trợ, giảng dạy và làm việc với người khác.' },
  { code: 'E', name: 'Doanh nhân', text: 'Thích thuyết phục, dẫn dắt và tổ chức.' },
  { code: 'C', name: 'Quy tắc', text: 'Thích sắp xếp, số liệu và quy trình rõ ràng.' },
]

onMounted(() => {
  if (!sliderEl.value) return
  slider = new Carousel(sliderEl.value, {
    interval: 5500,
    ride: 'carousel',
    pause: 'hover',
    touch: true,
    wrap: true,
  })
})

onUnmounted(() => {
  slider?.dispose()
  slider = null
})
</script>

<template>
  <div>
    <section class="guest-banner">
      <div class="container-fluid">
        <div class="row align-items-center gy-4">
          <div class="col-lg-7">
            <p class="guest-banner__kicker">Trắc nghiệm hướng nghiệp</p>
            <h1>Tìm ngành học và nghề phù hợp với bạn</h1>
            <p class="lead mb-4">
              Làm bài theo nhóm tính cách Holland, xem điểm mạnh và nhận gợi ý ngành, chuyên ngành.
            </p>
            <div class="d-flex flex-wrap gap-2">
              <RouterLink class="btn btn-light btn-lg" to="/chon-doi-tuong">Bắt đầu ngay</RouterLink>
              <RouterLink class="btn btn-outline-light btn-lg" to="/register">Đăng ký tài khoản</RouterLink>
            </div>
          </div>
          <div class="col-lg-5">
            <div class="guest-banner__panel">
              <p class="mb-2 fw-semibold">Sáu nhóm tính cách</p>
              <div class="d-flex flex-wrap gap-2">
                <span v-for="group in groups" :key="group.code" class="guest-banner__chip">
                  {{ group.code }} · {{ group.name }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5">
      <div class="container-fluid">
        <div class="mb-4">
          <h2 class="h3 mb-1">Bắt đầu từ đây</h2>
          <p class="text-secondary mb-0">Ba hướng để hiểu mình trước khi chọn ngành.</p>
        </div>

        <div id="guest-slider" ref="sliderEl" class="carousel slide guest-slider">
          <div class="carousel-indicators">
            <button
              v-for="(slide, index) in slides"
              :key="slide.title"
              type="button"
              data-bs-target="#guest-slider"
              :data-bs-slide-to="index"
              :class="{ active: index === 0 }"
              :aria-current="index === 0 ? 'true' : undefined"
              :aria-label="`Slide ${index + 1}`"
            ></button>
          </div>
          <div class="carousel-inner rounded-4">
            <div
              v-for="(slide, index) in slides"
              :key="slide.title"
              class="carousel-item"
              :class="{ active: index === 0 }"
            >
              <div class="guest-slide" :style="{ background: slide.background }">
                <p class="guest-slide__kicker">{{ slide.kicker }}</p>
                <h3 class="h2">{{ slide.title }}</h3>
                <p class="mb-0 col-lg-8">{{ slide.text }}</p>
              </div>
            </div>
          </div>
          <button class="carousel-control-prev" type="button" data-bs-target="#guest-slider" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Trước</span>
          </button>
          <button class="carousel-control-next" type="button" data-bs-target="#guest-slider" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Sau</span>
          </button>
        </div>
      </div>
    </section>

    <section class="py-5 bg-white border-top border-bottom">
      <div class="container-fluid">
        <h2 class="h3 text-center mb-4">Ba bước</h2>
        <div class="row g-4">
          <div v-for="(step, index) in steps" :key="step.title" class="col-md-4">
            <article class="h-100 p-4 border rounded-4">
              <span class="guest-step">{{ index + 1 }}</span>
              <h3 class="h5 mt-3">{{ step.title }}</h3>
              <p class="text-secondary mb-0">{{ step.text }}</p>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5">
      <div class="container-fluid">
        <h2 class="h3 mb-4">Nhóm tính cách Holland</h2>
        <div class="row g-3">
          <div v-for="group in groups" :key="group.code" class="col-md-6 col-lg-4">
            <article class="h-100 p-4 bg-white border rounded-4">
              <span class="guest-code">{{ group.code }}</span>
              <h3 class="h5 mt-3">{{ group.name }}</h3>
              <p class="text-secondary mb-0">{{ group.text }}</p>
            </article>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
