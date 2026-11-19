<template>
  <el-card shadow="never" class="the-thong-ke" :style="{ '--mau': color }">
    <div class="the-thong-ke__head">
      <span class="the-thong-ke__icon" aria-hidden="true">
        <el-icon><component :is="icon" /></el-icon>
      </span>
      <span class="the-thong-ke__title" :title="title">{{ title }}</span>
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
      :height="36"
      :series="sparkSeries"
      :colors="[color]"
    />
  </el-card>
</template>

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

<style scoped>
/* Thẻ là container: khi thẻ hẹp (2 thẻ/hàng trên điện thoại) nội dung bên trong tự thu gọn. */
.the-thong-ke {
  container-type: inline-size;
  height: 100%;
  border-radius: 12px;
}

.the-thong-ke :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px 8px;
}

.the-thong-ke__head {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.the-thong-ke__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  font-size: 15px;
  color: var(--mau);
  background: color-mix(in srgb, var(--mau) 12%, transparent);
}

.the-thong-ke__title {
  min-width: 0;
  overflow: hidden;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.the-thong-ke__value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.01em;
  color: var(--el-text-color-primary);
  font-variant-numeric: tabular-nums;
}

.the-thong-ke__value small {
  margin-left: 2px;
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
}

.the-thong-ke__trend {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  font-size: 12px;
}

.the-thong-ke__trend .is-up,
.the-thong-ke__trend .is-down {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  gap: 2px;
  font-weight: 500;
}

.the-thong-ke__trend .is-up {
  color: var(--el-color-success);
}

.the-thong-ke__trend .is-down {
  color: var(--el-color-danger);
}

.the-thong-ke__trend-label {
  min-width: 0;
  overflow: hidden;
  color: var(--el-text-color-secondary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.the-thong-ke__spark {
  margin: 0 -4px;
  opacity: 0.85;
}

@container (max-width: 220px) {
  .the-thong-ke :deep(.el-card__body) {
    gap: 4px;
    padding: 12px 12px 6px;
  }

  /* Nhường chỗ cho tiêu đề; màu sparkline vẫn phân biệt được từng thẻ. */
  .the-thong-ke__icon {
    display: none;
  }

  .the-thong-ke__title {
    font-size: 12px;
  }

  .the-thong-ke__value {
    font-size: 20px;
  }

  .the-thong-ke__value small {
    font-size: 12px;
  }

  /* Thẻ hẹp: chỉ giữ mức tăng/giảm, bỏ nhãn so sánh. */
  .the-thong-ke__trend-label {
    display: none;
  }
}
</style>
