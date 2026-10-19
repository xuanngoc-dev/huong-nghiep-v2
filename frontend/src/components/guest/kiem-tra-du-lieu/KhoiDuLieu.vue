<script setup>
import { computed } from 'vue'
import { nhan } from './nhanDuLieu'

defineOptions({ name: 'KhoiDuLieu' })

const props = defineProps({
  value: { default: null },
  depth: { type: Number, default: 0 },
})

const dang = computed(() => {
  const value = props.value
  if (value == null || value === '') return 'trong'
  if (Array.isArray(value)) {
    if (!value.length) return 'trong'
    if (value.every((item) => item == null || ['string', 'number', 'boolean'].includes(typeof item))) return 'chu-list'
    return 'danh-sach'
  }
  if (typeof value === 'object') return 'doi-tuong'
  return 'chu'
})

const muc = computed(() => {
  if (dang.value !== 'danh-sach') return []
  return props.value.map((item, index) => ({
    key: index,
    title: tieuDe(item, index),
    value: item,
  }))
})

const truong = computed(() => {
  if (dang.value !== 'doi-tuong') return []
  return Object.keys(props.value).map((key) => ({ key, label: nhan(key), value: props.value[key] }))
})

function tieuDe(item, index) {
  if (item && typeof item === 'object' && !Array.isArray(item)) {
    const loai = item.loai || item.ten_phuong_thuc || item.ten_to_hap || item.ma_to_hap
    if (loai) return String(loai).replaceAll('_', ' ')
  }
  return `Mục ${index + 1}`
}

function chu(value) {
  if (typeof value === 'boolean') return value ? 'Có' : 'Không'
  return String(value)
}
</script>

<template>
  <p v-if="dang === 'trong'" class="khoi-trong">Không có</p>
  <p v-else-if="dang === 'chu'" class="khoi-chu">{{ chu(value) }}</p>
  <p v-else-if="dang === 'chu-list'" class="khoi-chu">{{ value.map((item) => chu(item)).join(', ') }}</p>
  <dl v-else-if="dang === 'doi-tuong'" class="khoi-dl">
    <div v-for="field in truong" :key="field.key" class="khoi-row">
      <dt>{{ field.label }}</dt>
      <dd><KhoiDuLieu :value="field.value" :depth="depth + 1" /></dd>
    </div>
  </dl>
  <div v-else class="khoi-list">
    <article v-for="item in muc" :key="item.key" class="khoi-card" :class="{ 'is-nested': depth > 0 }">
      <template v-if="item.value && typeof item.value === 'object'">
        <h4>{{ item.title }}</h4>
        <KhoiDuLieu :value="item.value" :depth="depth + 1" />
      </template>
      <p v-else class="khoi-chu">{{ chu(item.value) }}</p>
    </article>
  </div>
</template>

<style scoped>
.khoi-trong {
  margin: 0;
  color: #8a978e;
}

.khoi-chu {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.khoi-dl {
  display: grid;
  gap: 8px;
  margin: 0;
}

.khoi-row {
  display: grid;
  grid-template-columns: minmax(148px, 220px) minmax(0, 1fr);
  gap: 4px 12px;
  align-items: start;
}

.khoi-row dt {
  margin: 0;
  color: #5c6b62;
  font-size: 13px;
  line-height: 1.45;
}

.khoi-row dd {
  margin: 0;
  min-width: 0;
}

.khoi-list {
  display: grid;
  gap: 8px;
}

.khoi-card {
  border: 1px solid #e4eee6;
  border-radius: 8px;
  padding: 10px 12px;
  background: #fff;
}

.khoi-card.is-nested {
  background: #f7fbf8;
}

.khoi-card h4 {
  margin: 0 0 8px;
  font-size: 14px;
  line-height: 1.4;
}

@media (max-width: 720px) {
  .khoi-row {
    grid-template-columns: 1fr;
  }
}
</style>
