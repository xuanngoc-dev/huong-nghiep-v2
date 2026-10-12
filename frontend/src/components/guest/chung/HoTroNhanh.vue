<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

defineOptions({ name: 'HoTroNhanh' })

const channels = [
  {
    name: 'Zalo',
    text: 'Nhắn tin qua Zalo',
    href: 'https://zalo.me',
    icon: 'https://cdn.simpleicons.org/zalo/0068FF',
    external: true,
  },
  {
    name: 'Facebook',
    text: 'Nhắn tin qua Facebook',
    href: 'https://www.facebook.com',
    icon: 'https://cdn.simpleicons.org/facebook/1877F2',
    external: true,
  },
  {
    name: 'Hotline',
    text: '1900 0000',
    href: 'tel:19000000',
    icon: 'https://api.iconify.design/mdi/phone.svg?color=%233f9643',
    external: false,
  },
]

const open = ref(false)
const rootEl = ref(null)

function toggle() {
  open.value = !open.value
}

function onDocumentClick(event) {
  if (!open.value || rootEl.value?.contains(event.target)) return
  open.value = false
}

function onKeydown(event) {
  if (event.key === 'Escape') open.value = false
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div ref="rootEl" class="quick-support">
    <div v-if="open" id="quick-support-panel" class="quick-support__panel">
      <p class="quick-support__title">Kênh hỗ trợ</p>
      <a
        v-for="channel in channels"
        :key="channel.name"
        class="quick-support__link"
        :href="channel.href"
        :target="channel.external ? '_blank' : undefined"
        :rel="channel.external ? 'noopener noreferrer' : undefined"
      >
        <span class="quick-support__mark">
          <img :src="channel.icon" alt="" width="24" height="24" />
        </span>
        <span>
          <strong>{{ channel.name }}</strong>
          <small>{{ channel.text }}</small>
        </span>
      </a>
    </div>
    <button
      type="button"
      class="guest-fab quick-support__fab"
      aria-label="Kênh hỗ trợ"
      aria-controls="quick-support-panel"
      :aria-expanded="open"
      @click="toggle"
    >
      <span class="quick-support__waves" aria-hidden="true">
        <span></span>
        <span></span>
      </span>
      <el-icon :size="22"><Service /></el-icon>
    </button>
  </div>
</template>
