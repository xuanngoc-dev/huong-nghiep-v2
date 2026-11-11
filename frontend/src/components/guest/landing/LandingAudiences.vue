<script setup>
import { computed, nextTick, ref } from 'vue'
import { audiences } from '@/data/landing'

const activeId = ref(audiences[0].id)
const active = computed(() => audiences.find((item) => item.id === activeId.value) || audiences[0])
const tabRefs = ref([])

function selectAudience(id) {
  activeId.value = id
}

async function onTabKeydown(event, index) {
  const keys = { ArrowRight: 1, ArrowLeft: -1 }
  let target = null
  if (event.key in keys) target = (index + keys[event.key] + audiences.length) % audiences.length
  else if (event.key === 'Home') target = 0
  else if (event.key === 'End') target = audiences.length - 1
  if (target === null) return
  event.preventDefault()
  selectAudience(audiences[target].id)
  await nextTick()
  tabRefs.value[target]?.focus()
}
</script>

<template>
  <section id="doi-tuong" class="landing__section landing__section--alt" aria-labelledby="audiences-title">
    <div class="container-fluid">
      <div class="landing__head row g-lp align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Giải pháp theo đối tượng</p>
          <h3 id="audiences-title" class="landing__title">Dù bạn là ai, chúng tôi cũng có giải pháp phù hợp cho bạn</h3>
        </div>
        <!-- <p class="landing__lead col-lg-5">
          Chọn đối tượng của bạn để xem lợi ích và dịch vụ phù hợp nhất.
        </p> -->
      </div>

      <div class="landing-audiences row g-lp align-items-start" data-reveal>
        <div class="col-12">
          <div
            class="landing-audiences__tabs nav nav-pills flex-nowrap flex-md-wrap overflow-x-auto"
            role="tablist"
            aria-label="Chọn đối tượng"
          >
            <button
              v-for="(item, index) in audiences"
              :id="`audience-tab-${item.id}`"
              :key="item.id"
              :ref="(el) => (tabRefs[index] = el)"
              type="button"
              role="tab"
              class="landing-audiences__tab nav-link"
              :class="{ active: item.id === activeId }"
              :aria-selected="item.id === activeId"
              :aria-controls="`audience-panel-${item.id}`"
              :tabindex="item.id === activeId ? 0 : -1"
              @click="selectAudience(item.id)"
              @keydown="onTabKeydown($event, index)"
            >
              <img :src="item.image" alt="" loading="lazy" decoding="async" />
              {{ item.name }}
            </button>
          </div>
        </div>

        <div class="col-12">
          <Transition name="lp-fade" mode="out-in">
            <div
              :id="`audience-panel-${active.id}`"
              :key="active.id"
              class="landing-audiences__panel row g-0"
              role="tabpanel"
              :aria-labelledby="`audience-tab-${active.id}`"
            >
              <div class="landing-audiences__media col-lg-6">
                <img :src="active.image" :alt="`Hình minh họa cho ${active.name}`" loading="lazy" decoding="async" />
                <span class="lp-tag lp-tag--float">{{ active.name }}</span>
              </div>
              <div class="landing-audiences__body col-lg-6">
                <h3>{{ active.description }}</h3>
                <ul class="landing-audiences__list">
                  <li v-for="benefit in active.benefits" :key="benefit">
                    <el-icon aria-hidden="true"><CircleCheckFilled /></el-icon>
                    {{ benefit }}
                  </li>
                </ul>
                <RouterLink class="landing__btn landing__btn--primary" :to="{ name: active.route }">
                  {{ active.cta }}
                  <el-icon aria-hidden="true"><Right /></el-icon>
                </RouterLink>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </section>
</template>
