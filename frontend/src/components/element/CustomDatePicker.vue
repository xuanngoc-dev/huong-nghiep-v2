<script setup>
/**
 * CustomDatePicker — wrapper el-date-picker.
 * Locale tiếng Việt: "Năm 2026", "Tháng 5" (thay vì "2026 Năm", "Th.5").
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 */
import { computed, nextTick, onBeforeUnmount, ref, useAttrs, useSlots } from 'vue'
import vi from 'element-plus/es/locale/lang/vi'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomDatePicker', inheritAttrs: false })

const datepickerLocale = {
  ...vi,
  el: {
    ...vi.el,
    datepicker: {
      ...vi.el.datepicker,
      months: {
        jan: 'Tháng 1',
        feb: 'Tháng 2',
        mar: 'Tháng 3',
        apr: 'Tháng 4',
        may: 'Tháng 5',
        jun: 'Tháng 6',
        jul: 'Tháng 7',
        aug: 'Tháng 8',
        sep: 'Tháng 9',
        oct: 'Tháng 10',
        nov: 'Tháng 11',
        dec: 'Tháng 12',
      },
    },
  },
}

const model = defineModel({ default: undefined })
const pickerRef = ref(null)
const slots = useSlots()
const attrs = useAttrs()
const { resolvedSize } = useResponsiveComponentSize()
const instancePopperClass = `custom-date-picker-popper-${Math.random().toString(36).slice(2, 9)}`

let yearLabelObserver = null

const pickerAttrs = computed(() => {
  const {
    popperClass,
    'popper-class': _popperClassKebab,
    onVisibleChange: _onVisibleChange,
    ...rest
  } = attrs
  return rest
})

const mergedPopperClass = computed(() => {
  const existing = attrs.popperClass ?? attrs['popper-class'] ?? ''
  return ['custom-date-picker-popper', instancePopperClass, existing]
    .filter(Boolean)
    .join(' ')
})

function rewriteYearLabels(root) {
  if (!root) return
  root.querySelectorAll('.el-date-picker__header-label').forEach((el) => {
    const text = (el.textContent || '').trim()
    if (!text) return

    // "2020 Năm - 2029 Năm" → "Năm 2020 - Năm 2029"
    let next = text.replace(
      /^(\d{4})\s+Năm\s+-\s+(\d{4})\s+Năm$/,
      'Năm $1 - Năm $2',
    )
    // "2026 Năm" → "Năm 2026"
    next = next.replace(/^(\d{4})\s+Năm$/, 'Năm $1')

    if (next !== text) el.textContent = next
  })
}

function findPopperRoot() {
  return document.querySelector(`.${instancePopperClass}`)
}

function stopObservingYearLabels() {
  yearLabelObserver?.disconnect()
  yearLabelObserver = null
}

async function startObservingYearLabels() {
  stopObservingYearLabels()
  await nextTick()
  const root = findPopperRoot()
  if (!root) return

  rewriteYearLabels(root)
  yearLabelObserver = new MutationObserver(() => {
    rewriteYearLabels(root)
  })
  yearLabelObserver.observe(root, {
    characterData: true,
    childList: true,
    subtree: true,
  })
}

function onVisibleChange(visible) {
  const listener = attrs.onVisibleChange
  if (typeof listener === 'function') listener(visible)

  if (visible) {
    startObservingYearLabels()
  } else {
    stopObservingYearLabels()
  }
}

onBeforeUnmount(stopObservingYearLabels)

defineExpose({
  focus: (...args) => pickerRef.value?.focus?.(...args),
  blur: (...args) => pickerRef.value?.blur?.(...args),
  handleOpen: (...args) => pickerRef.value?.handleOpen?.(...args),
  handleClose: (...args) => pickerRef.value?.handleClose?.(...args),
})
</script>

<template>
  <el-config-provider :locale="datepickerLocale">
    <el-date-picker
      ref="pickerRef"
      v-model="model"
      v-bind="pickerAttrs"
      :size="resolvedSize"
      :popper-class="mergedPopperClass"
      @visible-change="onVisibleChange"
    >
      <template v-for="(_, name) in slots" #[name]="slotData">
        <slot :name="name" v-bind="slotData || {}" />
      </template>
    </el-date-picker>
  </el-config-provider>
</template>
