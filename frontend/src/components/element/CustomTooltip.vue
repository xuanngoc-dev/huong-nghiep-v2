<template>
  <el-tooltip v-bind="$attrs" :disabled="tatTooltip">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-tooltip>
</template>

<script setup>
/**
 * CustomTooltip — wrapper el-tooltip. Tự tắt trên mobile và thiết bị cảm ứng không có hover
 * (chạm vào nút sẽ bật tooltip đè lên thao tác); desktop vẫn hiện. Truyền `disabled` để tắt thêm theo điều kiện riêng.
 */
import { computed, useAttrs, useSlots } from 'vue'
import { COMPONENT_MOBILE_MQ, useIsMobile } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomTooltip', inheritAttrs: false })

const slots = useSlots()
const attrs = useAttrs()
const khongHover = useIsMobile(`${COMPONENT_MOBILE_MQ}, (hover: none)`)

const tatTooltip = computed(() => {
  const disabled = attrs.disabled
  return khongHover.value || (disabled !== undefined && disabled !== false)
})
</script>
