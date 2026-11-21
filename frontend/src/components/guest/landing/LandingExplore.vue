<template>
  <section id="kham-pha" class="landing__section landing__section--alt" aria-labelledby="explore-title">
    <div class="container-fluid">
      <div class="landing__head row g-lp align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Khám phá nghề & trường</p>
          <h2 id="explore-title" class="landing__title">Tìm ngành nghề, trường học và lộ trình phù hợp</h2>
        </div>
        <!-- <p class="landing__lead col-lg-5">
          Duyệt các lĩnh vực phổ biến, xem trước bộ lọc tìm kiếm và bắt đầu hành trình khám phá ngay
          trên nền tảng.
        </p> -->
      </div>

      <div class="landing-explore__panel" data-reveal>
        <div class="landing-explore__filters flex-nowrap flex-md-wrap overflow-x-auto" role="group" aria-label="Loại tra cứu">
          <button
            v-for="tab in LOAI_TRA_CUU"
            :key="tab.id"
            type="button"
            class="landing-explore__chip"
            :class="{ 'is-active': tab.id === activeTab }"
            :aria-pressed="tab.id === activeTab"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <form class="landing-explore__search mb-0" role="search" @submit.prevent="traCuu()">
          <el-icon aria-hidden="true"><Search /></el-icon>
          <input
            v-model="query"
            type="search"
            :placeholder="loai.placeholder"
            :aria-label="`Tìm ${loai.label}`"
          />
          <button type="submit" class="landing__btn landing__btn--soft">Tra cứu</button>
        </form>
      </div>

      <div class="landing-explore__cats" data-reveal>
        <h3 class="landing__subtitle">Lĩnh vực nghề nghiệp nổi bật</h3>
        <LandingCarousel
          :items="careerCategories"
          label="Lĩnh vực nghề nghiệp nổi bật"
          :per-view="{ base: 1.15, sm: 2, lg: 3, xl: 4, xxl: 5 }"
          :autoplay="5000"
        >
          <template #default="{ item }">
            <RouterLink :to="{ name: 'chon-doi-tuong' }" class="lp-media-card lp-media-card--overlay">
              <LandingImage :src="item.image" :fallback="item.fallback" :alt="item.alt" ratio="4 / 5" />
              <div class="lp-media-card__overlay">
                <span class="lp-tag">{{ item.tag }}</span>
                <h4>{{ item.title }}</h4>
                <p>{{ item.meta }}</p>
                <span class="lp-link lp-link--light">Khám phá lĩnh vực <el-icon aria-hidden="true"><Right /></el-icon></span>
              </div>
            </RouterLink>
          </template>
        </LandingCarousel>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { careerCategories } from '@/data/landing'
import { LOAI_TRA_CUU, timLoaiTraCuu } from '@/components/guest/tra-cuu/loaiTraCuu'
import LandingCarousel from './LandingCarousel.vue'
import LandingImage from './LandingImage.vue'

const router = useRouter()
const activeTab = ref(LOAI_TRA_CUU[0].id)
const query = ref('')
const loai = computed(() => timLoaiTraCuu(activeTab.value))

// Trang chủ chỉ chọn loại + nhập từ khóa; kết quả hiện ở trang /tra-cuu.
function traCuu() {
  const q = query.value.trim()
  router.push({ name: 'tra-cuu', query: { loai: activeTab.value, ...(q ? { q } : {}) } })
}
</script>
