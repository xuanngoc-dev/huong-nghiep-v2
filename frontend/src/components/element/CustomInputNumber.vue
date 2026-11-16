<template>
  <el-input-number v-model="model" v-bind="numberAttrs" :size="resolvedSize">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-input-number>
</template>

<script setup>
/**
 * CustomInputNumber — wrapper el-input-number.
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 *
 * Mặc định phân tách hàng nghìn ngay khi gõ (10000 → 10.000, thập phân dùng dấu phẩy: 1.234,5); model vẫn là số.
 * Ô năm, mã/id truyền `:phan-tach-hang-nghin="false"`. Truyền `formatter`/`parser` riêng thì dùng của nơi gọi.
 */
import { computed, useAttrs, useSlots } from 'vue'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'
import { formatSoNhap, parseSoNhap } from '@/utils/number'

defineOptions({ name: 'CustomInputNumber', inheritAttrs: false })

const props = defineProps({
  phanTachHangNghin: { type: Boolean, default: true },
})

const model = defineModel({ default: undefined })
const attrs = useAttrs()
const slots = useSlots()
const { resolvedSize } = useResponsiveComponentSize()

const numberAttrs = computed(() => {
  if (!props.phanTachHangNghin || attrs.formatter || attrs.parser) return attrs
  return { formatter: formatSoNhap, parser: parseSoNhap, inputmode: 'decimal', ...attrs }
})
</script>
