<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  fallback: { type: String, default: '' },
  alt: { type: String, default: '' },
  ratio: { type: String, default: '16 / 10' },
  eager: { type: Boolean, default: false },
})

const current = ref(props.src)
const loaded = ref(false)

watch(
  () => props.src,
  (value) => {
    current.value = value
    loaded.value = false
  },
)

function onError() {
  if (props.fallback && current.value !== props.fallback) {
    current.value = props.fallback
    return
  }
  loaded.value = true
}
</script>

<template>
  <div class="lp-image" :class="{ 'is-loaded': loaded }" :style="{ aspectRatio: ratio }">
    <img
      :src="current"
      :alt="alt"
      :loading="eager ? 'eager' : 'lazy'"
      decoding="async"
      @load="loaded = true"
      @error="onError"
    />
    <slot />
  </div>
</template>
