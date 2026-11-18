<template>
  <ul v-if="ds.length" class="goi-y-lenh" role="listbox" aria-label="Lệnh trong khung chat">
    <li v-for="(lenh, i) in ds" :key="lenh.ten" role="option" :aria-selected="i === 0">
      <!-- mousedown.prevent: giữ focus ở ô nhập khi bấm chọn. -->
      <button type="button" :class="{ 'is-dau': i === 0 }" @mousedown.prevent @click="$emit('chon', lenh)">
        <code>{{ cuPhap(lenh) }}</code>
        <span>{{ lenh.moTa }}</span>
      </button>
    </li>
    <li class="goi-y-lenh__meo" aria-hidden="true">Tab để chọn lệnh đầu · Enter để chạy</li>
  </ul>
</template>

<script setup>
/** Gợi ý lệnh "/..." khi người dùng bắt đầu gõ "/" trong ô nhập của khung chat. Đặt trong khung có position: relative. */
import { computed } from 'vue'
import { cuPhap, goiYLenh } from '@/utils/chatLenh'

defineOptions({ name: 'GoiYLenh' })
const props = defineProps({ text: { type: String, default: '' } })
defineEmits(['chon'])

const ds = computed(() => goiYLenh(props.text))
</script>

<style scoped>
.goi-y-lenh {
  position: absolute;
  right: 0;
  bottom: calc(100% + 6px);
  left: 0;
  z-index: 5;
  max-height: 260px;
  margin: 0;
  padding: 6px;
  overflow-y: auto;
  border: 1px solid var(--el-border-color-lighter, #e2ece5);
  border-radius: 10px;
  background: var(--el-bg-color, #fff);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  list-style: none;
}

.goi-y-lenh button {
  display: flex;
  align-items: baseline;
  gap: 10px;
  width: 100%;
  padding: 7px 10px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--el-text-color-primary, #1c2b23);
  font: inherit;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
}

.goi-y-lenh button:hover,
.goi-y-lenh button.is-dau {
  background: var(--el-fill-color-light, #f2f7f4);
}

.goi-y-lenh code {
  flex: 0 0 auto;
  color: var(--el-color-primary, #237b51);
  font-weight: 600;
}

.goi-y-lenh span {
  color: var(--el-text-color-secondary, #607169);
}

.goi-y-lenh__meo {
  padding: 4px 10px 0;
  color: var(--el-text-color-placeholder, #8a9a91);
  font-size: 11px;
}
</style>
