<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import Carousel from 'bootstrap/js/dist/carousel'
import khamPhaImage from '@/assets/guest/thpt.jpg'
import chonHuongImage from '@/assets/guest/nha-truong.jpg'
import dongHanhImage from '@/assets/guest/thanh-nien.jpg'

defineOptions({ name: 'DinhHuongTuongLai' })

const SLIDER_ID = 'dinh-huong-tuong-lai'

const slides = [
  {
    title: 'Khám phá điểm mạnh',
    text: 'Hiểu nhóm tính cách và môn học thế mạnh trước khi chọn hướng sau tốt nghiệp.',
    image: khamPhaImage,
  },
  {
    title: 'Chọn hướng phù hợp',
    text: 'Đối chiếu đi làm, học tiếp, du học hoặc khởi nghiệp với năng lực của bạn.',
    image: chonHuongImage,
  },
  {
    title: 'Đồng hành từng bước',
    text: 'Giữ lựa chọn đã chọn và nhận gợi ý khi bạn cần làm rõ bước tiếp theo.',
    image: dongHanhImage,
  },
]

const sliderEl = ref(null)
let slider = null

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
  <section class="future-card" aria-labelledby="dinh-huong-tuong-lai-title">
    <h2 id="dinh-huong-tuong-lai-title" class="future-card__title">Định hướng tương lai cùng chúng tôi</h2>
    <p class="future-card__lead">Một vài bước để bạn hình dung hướng đi sau khi tốt nghiệp THPT.</p>

    <div :id="SLIDER_ID" ref="sliderEl" class="carousel slide">
      <div class="carousel-indicators">
        <button
          v-for="(slide, index) in slides"
          :key="slide.title"
          type="button"
          :data-bs-target="`#${SLIDER_ID}`"
          :data-bs-slide-to="index"
          :class="{ active: index === 0 }"
          :aria-current="index === 0 ? 'true' : undefined"
          :aria-label="`Slide ${index + 1}`"
        ></button>
      </div>
      <div class="carousel-inner">
        <div
          v-for="(slide, index) in slides"
          :key="slide.title"
          class="carousel-item"
          :class="{ active: index === 0 }"
        >
          <article class="future-slide">
            <img class="future-slide__image" :src="slide.image" :alt="slide.title" />
            <div class="future-slide__caption">
              <h3>{{ slide.title }}</h3>
              <p>{{ slide.text }}</p>
            </div>
          </article>
        </div>
      </div>
      <button class="carousel-control-prev" type="button" :data-bs-target="`#${SLIDER_ID}`" data-bs-slide="prev">
        <span class="future-card__arrow" aria-hidden="true">‹</span>
        <span class="visually-hidden">Trước</span>
      </button>
      <button class="carousel-control-next" type="button" :data-bs-target="`#${SLIDER_ID}`" data-bs-slide="next">
        <span class="future-card__arrow" aria-hidden="true">›</span>
        <span class="visually-hidden">Sau</span>
      </button>
    </div>
  </section>
</template>
