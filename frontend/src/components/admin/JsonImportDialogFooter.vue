<script setup>
import { computed } from 'vue'

const props = defineProps({
  batch: {
    type: Object,
    required: true,
  },
  saving: {
    type: Boolean,
    default: false,
  },
  showProgress: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['cancel', 'save'])

const percent = computed(() => {
  const { done, total } = props.batch.progress
  if (!total) return 0
  return Math.min(100, Math.round((done / total) * 100))
})

const status = computed(() => {
  const { failed, done, total } = props.batch.progress
  if (failed) return 'exception'
  if (total > 0 && done >= total) return 'success'
  return ''
})

const text = computed(() => {
  const { done, total, active } = props.batch.progress
  const { label, batchSize } = props.batch
  if (active) {
    const from = done + 1
    const to = Math.min(done + batchSize, total)
    return `Đang lưu ${label} ${from}–${to} / ${total}`
  }
  return `Đã lưu ${done} / ${total} ${label}`
})
</script>

<template>
  <div class="dialog-footer">
    <div v-if="showProgress && batch.progress.total > 1" class="json-progress">
      <el-progress
        :percentage="percent"
        :status="status || undefined"
        :stroke-width="14"
        :striped="batch.progress.active"
        striped-flow
      />
      <p class="json-progress__text">{{ text }}</p>
    </div>
    <div class="dialog-footer__actions">
      <CustomButton :disabled="saving" @click="$emit('cancel')">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" @click="$emit('save')">Lưu</CustomButton>
    </div>
  </div>
</template>

<style scoped>
.dialog-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dialog-footer__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.json-progress__text {
  margin: 6px 0 0;
  text-align: left;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.4;
}
</style>
