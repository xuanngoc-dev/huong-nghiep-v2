<script setup>
import { nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useLandingReveal } from '@/composables/useLandingReveal'
import LandingHero from '@/components/guest/landing/LandingHero.vue'
import LandingAudiences from '@/components/guest/landing/LandingAudiences.vue'
import LandingFeatures from '@/components/guest/landing/LandingFeatures.vue'
import LandingHowItWorks from '@/components/guest/landing/LandingHowItWorks.vue'
import LandingHolland from '@/components/guest/landing/LandingHolland.vue'
import LandingExplore from '@/components/guest/landing/LandingExplore.vue'
import LandingAiAdvisor from '@/components/guest/landing/LandingAiAdvisor.vue'
import LandingInstitutions from '@/components/guest/landing/LandingInstitutions.vue'
import LandingTestimonials from '@/components/guest/landing/LandingTestimonials.vue'
import LandingStudyPaths from '@/components/guest/landing/LandingStudyPaths.vue'
import LandingFaq from '@/components/guest/landing/LandingFaq.vue'
import LandingResources from '@/components/guest/landing/LandingResources.vue'
import LandingFinalCta from '@/components/guest/landing/LandingFinalCta.vue'
import '@/components/guest/landing/landing.css'

const route = useRoute()
useLandingReveal()

const DESCRIPTION =
  'Nền tảng định hướng nghề nghiệp giúp học sinh, sinh viên, phụ huynh và tổ chức khám phá bản thân, chọn ngành học và xây dựng lộ trình sự nghiệp.'

let metaDescription = null
let previousDescription = ''

function ensureMetaDescription() {
  metaDescription = document.querySelector('meta[name="description"]')
  if (!metaDescription) {
    metaDescription = document.createElement('meta')
    metaDescription.setAttribute('name', 'description')
    document.head.appendChild(metaDescription)
    previousDescription = ''
  } else {
    previousDescription = metaDescription.getAttribute('content') || ''
  }
  metaDescription.setAttribute('content', DESCRIPTION)
}

function scrollToHash() {
  if (!route.hash) return
  const id = route.hash.replace(/^#/, '')
  const el = document.getElementById(id)
  if (!el) return
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(async () => {
  ensureMetaDescription()
  document.title = 'Trang chủ | Định hướng nghề'
  await nextTick()
  scrollToHash()
})

watch(
  () => route.hash,
  async () => {
    await nextTick()
    scrollToHash()
  },
)

onUnmounted(() => {
  if (!metaDescription) return
  if (previousDescription) metaDescription.setAttribute('content', previousDescription)
  else metaDescription.remove()
})
</script>

<template>
  <div class="landing">
    <LandingHero />
    <LandingAudiences />
    <LandingFeatures />
    <LandingExplore />
    <LandingHolland />
    <LandingStudyPaths />
    <LandingAiAdvisor />
    <LandingInstitutions />
    <LandingHowItWorks />
    <LandingTestimonials />
    <LandingResources />
    <LandingFaq />
    <LandingFinalCta />
  </div>
</template>
