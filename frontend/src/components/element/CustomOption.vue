<script setup>
/**
 * CustomOption — wrapper el-option.
 * Đăng ký value với CustomSelect (phục vụ chọn tất cả khi multiple).
 */
import {
  getCurrentInstance,
  inject,
  onBeforeUnmount,
  onMounted,
  useAttrs,
  useSlots,
  watch,
} from 'vue'

defineOptions({ name: 'CustomOption', inheritAttrs: false })

const attrs = useAttrs()
const slots = useSlots()
const registry = inject('customSelectOptions', null)
const uid = getCurrentInstance()?.uid

function syncRegister() {
  if (!registry || uid == null) return
  registry.register(uid, attrs.value)
}

onMounted(syncRegister)
watch(() => attrs.value, syncRegister)
onBeforeUnmount(() => {
  registry?.unregister?.(uid)
})
</script>

<template>
  <el-option v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-option>
</template>
