<script setup>
/**
 * CustomDropdown — wrapper el-dropdown.
 * Hỗ trợ slot mặc định (trigger) + slot dropdown, hoặc prop `items` để render menu nhanh.
 *
 * items: Array<{
 *   command?: string | number | object
 *   label: string
 *   icon?: import('vue').Component | string
 *   disabled?: boolean
 *   divided?: boolean
 *   type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
 *   class?: string
 * }>
 *
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 */
import { computed, ref, useAttrs, useSlots } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomDropdown', inheritAttrs: false })

const props = defineProps({
  /** Danh sách item — nếu có thì tự render el-dropdown-menu (bỏ qua slot dropdown nếu không truyền). */
  items: { type: Array, default: null },
  /** Text nút trigger mặc định khi không có default slot. */
  triggerText: { type: String, default: 'Thao tác' },
  /** Hiện icon mũi tên trên trigger mặc định. */
  showArrow: { type: Boolean, default: true },
})

const emit = defineEmits(['command', 'visible-change', 'click'])

const slots = useSlots()
const attrs = useAttrs()
const dropdownRef = ref(null)
const { resolvedSize } = useResponsiveComponentSize()

const hasItems = computed(() => Array.isArray(props.items) && props.items.length > 0)
const useItemsMenu = computed(() => hasItems.value && !slots.dropdown)

/** Menu teleported ra body → cần popper-class để style type màu. */
const popperClass = computed(() => {
  const extra = attrs.popperClass ?? attrs['popper-class']
  return ['custom-dropdown-popper', extra].filter(Boolean).join(' ')
})

function itemClass(item) {
  const classes = []
  if (item?.type) classes.push(`custom-dropdown-item--${item.type}`)
  if (item?.class) classes.push(item.class)
  return classes
}

function onCommand(command) {
  emit('command', command)
}

function onVisibleChange(visible) {
  emit('visible-change', visible)
}

function onClick(...args) {
  emit('click', ...args)
}

defineExpose({
  handleOpen: (...args) => dropdownRef.value?.handleOpen?.(...args),
  handleClose: (...args) => dropdownRef.value?.handleClose?.(...args),
})
</script>

<template>
  <el-dropdown
    ref="dropdownRef"
    v-bind="$attrs"
    :size="resolvedSize"
    :popper-class="popperClass"
    @command="onCommand"
    @visible-change="onVisibleChange"
    @click="onClick"
  >
    <slot>
      <span class="custom-dropdown__trigger el-dropdown-link">
        {{ triggerText }}
        <el-icon v-if="showArrow" class="el-icon--right">
          <ArrowDown />
        </el-icon>
      </span>
    </slot>

    <template v-if="useItemsMenu" #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="(item, index) in items"
          :key="item.command ?? item.label ?? index"
          :command="item.command"
          :disabled="item.disabled"
          :divided="item.divided"
          :icon="item.icon"
          :class="itemClass(item)"
        >
          {{ item.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
    <template v-else-if="slots.dropdown" #dropdown="slotData">
      <slot name="dropdown" v-bind="slotData || {}" />
    </template>
  </el-dropdown>
</template>

<style scoped lang="scss">
.custom-dropdown__trigger {
  cursor: pointer;
  color: var(--el-color-primary);
  display: inline-flex;
  align-items: center;
  outline: none;
}
</style>

<!-- Teleported menu — không dùng scoped -->
<style lang="scss">
.custom-dropdown-popper {
  .custom-dropdown-item--primary {
    color: var(--el-color-primary);
  }

  .custom-dropdown-item--success {
    color: var(--el-color-success);
  }

  .custom-dropdown-item--warning {
    color: var(--el-color-warning);
  }

  .custom-dropdown-item--danger {
    color: var(--el-color-danger);
  }

  .custom-dropdown-item--info {
    color: var(--el-color-info);
  }
}
</style>
