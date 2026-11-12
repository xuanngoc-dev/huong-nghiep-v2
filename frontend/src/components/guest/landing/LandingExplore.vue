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
        <div class="landing-explore__filters flex-nowrap flex-md-wrap overflow-x-auto" role="tablist" aria-label="Bộ lọc khám phá">
          <button
            v-for="tab in exploreTabs"
            :key="tab.id"
            type="button"
            class="landing-explore__chip"
            :class="{ 'is-active': tab.id === activeTab }"
            role="tab"
            :aria-selected="tab.id === activeTab"
            aria-controls="explore-preview"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="landing-explore__search" role="search">
          <el-icon aria-hidden="true"><Search /></el-icon>
          <input
            v-model="query"
            type="search"
            placeholder="Tìm ngành nghề, trường học hoặc kỹ năng..."
            aria-label="Tìm kiếm khám phá"
          />
          <RouterLink class="landing__btn landing__btn--soft" :to="{ name: 'thpt-thi-dai-hoc' }">
            Tra cứu
          </RouterLink>
        </div>

        <div id="explore-preview" class="landing-explore__preview" role="tabpanel" aria-live="polite">
          <template v-if="previewItems.length">
            <span v-for="item in previewItems" :key="item" class="landing-explore__pill">{{ item }}</span>
          </template>
          <p v-else class="mb-0 text-secondary">Không có kết quả phù hợp với từ khóa hiện tại.</p>
        </div>
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
import { careerCategories, explorePreview, exploreTabs } from '@/data/landing'
import LandingCarousel from './LandingCarousel.vue'
import LandingImage from './LandingImage.vue'

const activeTab = ref(exploreTabs[0].id)
const query = ref('')

const previewItems = computed(() => {
  const items = explorePreview[activeTab.value] || []
  const q = query.value.trim().toLowerCase()
  if (!q) return items
  return items.filter((item) => item.toLowerCase().includes(q))
})
</script>
