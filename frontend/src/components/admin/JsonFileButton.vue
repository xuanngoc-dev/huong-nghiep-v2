<template>
  <CustomButton type="primary" plain :disabled="disabled" @click="open">
    <CustomIcon><Upload /></CustomIcon>
    <span>Chọn file</span>
  </CustomButton>
  <input ref="inputRef" type="file" accept=".json,application/json" hidden @change="onChange" />
</template>

<script setup>
/**
 * JsonFileButton — nút "Chọn file" đọc file .json vào ô JSON (v-model).
 */
import { ref } from 'vue'
import { docFileJson, JSON_FILE_MAX_MB } from '@/utils/jsonFile'

const props = defineProps({
  disabled: { type: Boolean, default: false },
  maxMb: { type: Number, default: JSON_FILE_MAX_MB },
})

const emit = defineEmits(['loaded'])
const model = defineModel({ type: String, default: '' })
const inputRef = ref()

function open() {
  inputRef.value?.click()
}

async function onChange(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  const text = await docFileJson(file, props.maxMb)
  if (text === null) return
  model.value = text
  emit('loaded', text)
}
</script>
