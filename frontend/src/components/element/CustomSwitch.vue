<script setup>
/**
 * CustomSwitch — wrapper el-switch.
 * Mặc định đưa active-text / inactive-text ra ngoài, chỉ hiện nhãn của trạng thái hiện tại.
 * inline-prompt: giữ chữ bên trong công tắc (header, cài đặt giao diện).
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 */
import { computed, useAttrs, useSlots } from 'vue'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomSwitch', inheritAttrs: false })

const props = defineProps({
  modelValue: { type: [Boolean, String, Number], default: false },
  activeValue: { type: [Boolean, String, Number], default: true },
  inactiveValue: { type: [Boolean, String, Number], default: false },
  activeText: { type: String, default: 'Bật' },
  inactiveText: { type: String, default: 'Tắt' },
  inlinePrompt: { type: Boolean, default: false },
})

const attrs = useAttrs()
const slots = useSlots()
const { resolvedSize } = useResponsiveComponentSize()

const isOn = computed(() => props.modelValue === props.activeValue)
const label = computed(() => (isOn.value ? props.activeText : props.inactiveText))
</script>

<template>
  <span class="custom-switch">
    <el-switch
      v-bind="attrs"
      :model-value="modelValue"
      :active-value="activeValue"
      :inactive-value="inactiveValue"
      :size="resolvedSize"
      :inline-prompt="inlinePrompt"
      :active-text="inlinePrompt ? activeText : undefined"
      :inactive-text="inlinePrompt ? inactiveText : undefined"
    >
      <template v-for="(_, name) in slots" #[name]="slotData">
        <slot :name="name" v-bind="slotData || {}" />
      </template>
    </el-switch>
    <span
      v-if="!inlinePrompt && label"
      class="custom-switch__label"
      :class="isOn ? 'is-on' : 'is-off'"
    >
      {{ label }}
    </span>
  </span>
</template>

<style scoped>
.custom-switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 100%;
  vertical-align: middle;
}

.custom-switch__label {
  font-size: 13px;
  line-height: 1.2;
  white-space: nowrap;
}

.custom-switch__label.is-on {
  color: var(--el-color-success);
}

.custom-switch__label.is-off {
  color: var(--el-text-color-secondary);
}
</style>
