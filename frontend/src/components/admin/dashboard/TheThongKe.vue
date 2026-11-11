<script setup>
/**
 * TheThongKe — thẻ chỉ số tổng quan trên dashboard.
 * trend: % thay đổi so với kỳ trước (dương = tăng, âm = giảm).
 * xuHuong: mảng số liệu vẽ sparkline phía dưới (tùy chọn).
 */
import { computed } from 'vue'
import BieuDoDuong from '@/components/admin/charts/BieuDoDuong.vue'

const props = defineProps({
  title: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  donVi: { type: String, default: '' },
  icon: { type: String, default: 'DataLine' },
  color: { type: String, default: '#1f7a4d' },
  trend: { type: Number, default: null },
  trendLabel: { type: String, default: 'so với tháng trước' },
  xuHuong: { type: Array, default: () => [] },
})

const giaTri = computed(() =>
  typeof props.value === 'number' ? props.value.toLocaleString('vi-VN') : props.value,
)
const tang = computed(() => (props.trend ?? 0) >= 0)
const sparkSeries = computed(() => [{ name: props.title, data: props.xuHuong }])
</script>

<template>
  <el-card shadow="never" class="the-thong-ke" :style="{ '--mau': color }">
    <div class="the-thong-ke__head">
      <span class="the-thong-ke__title">{{ title }}</span>
      <span class="the-thong-ke__icon">
        <el-icon><component :is="icon" /></el-icon>
      </span>
    </div>

    <div class="the-thong-ke__value">
      {{ giaTri }}<small v-if="donVi">{{ donVi }}</small>
    </div>

    <div v-if="trend !== null" class="the-thong-ke__trend">
      <span :class="tang ? 'is-up' : 'is-down'">
        <el-icon><component :is="tang ? 'Top' : 'Bottom'" /></el-icon>
        {{ Math.abs(trend).toLocaleString('vi-VN') }}%
      </span>
      <span class="the-thong-ke__trend-label">{{ trendLabel }}</span>
    </div>

    <BieuDoDuong
      v-if="xuHuong.length"
      class="the-thong-ke__spark"
      sparkline
      :height="48"
      :series="sparkSeries"
      :colors="[color]"
    />
  </el-card>
</template>

<style scoped>
.the-thong-ke {
  height: 100%;
  border-radius: 12px;
}

.the-thong-ke :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 20px 12px;
}

.the-thong-ke__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.the-thong-ke__title {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.the-thong-ke__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  font-size: 20px;
  color: var(--mau);
  background: color-mix(in srgb, var(--mau) 12%, transparent);
}

.the-thong-ke__value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.01em;
  color: var(--el-text-color-primary);
}

.the-thong-ke__value small {
  margin-left: 4px;
  font-size: 15px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
}

.the-thong-ke__trend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.the-thong-ke__trend .is-up,
.the-thong-ke__trend .is-down {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-weight: 600;
}

.the-thong-ke__trend .is-up {
  color: var(--el-color-success);
}

.the-thong-ke__trend .is-down {
  color: var(--el-color-danger);
}

.the-thong-ke__trend-label {
  color: var(--el-text-color-secondary);
}

.the-thong-ke__spark {
  margin: 0 -4px;
}
</style>
