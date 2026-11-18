<template>
  <p class="dang-soan" role="status">
    <!-- Trình đọc màn hình chỉ đọc một câu cố định, không đọc lại mỗi lần đổi chữ. -->
    <span class="dang-soan__an">Trợ lý đang soạn câu trả lời</span>
    <span class="dang-soan__cham" aria-hidden="true"><i /><i /><i /></span>
    <Transition name="dang-soan" mode="out-in">
      <span :key="buoc" class="dang-soan__chu" aria-hidden="true">
        <span
          v-for="(kyTu, i) in CAC_BUOC[buoc]"
          :key="i"
          class="dang-soan__ky-tu"
          :style="{ animationDelay: `${i * 0.05}s` }"
          >{{ kyTu }}</span
        >…
      </span>
    </Transition>
  </p>
</template>

<script setup>
/** Hiệu ứng chờ trợ lý trả lời: chữ lượn sóng, câu mô tả đổi dần theo các bước xử lý (dừng ở bước cuối). */
import { onBeforeUnmount, onMounted, ref } from 'vue'

defineOptions({ name: 'DangSoanTraLoi' })

const CAC_BUOC = [
  'Đang phân tích câu hỏi',
  'Đang tra cứu dữ liệu tuyển sinh',
  'Đang tổng hợp dữ liệu',
  'Đang đối chiếu nguồn tham khảo',
  'Đang soạn câu trả lời',
]
const THOI_GIAN_MOI_BUOC = 2200

const buoc = ref(0)
let hen = null

onMounted(() => {
  hen = setInterval(() => {
    if (buoc.value < CAC_BUOC.length - 1) buoc.value += 1
    else clearInterval(hen)
  }, THOI_GIAN_MOI_BUOC)
})

onBeforeUnmount(() => clearInterval(hen))
</script>

<style scoped>
.dang-soan {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: var(--el-text-color-secondary, #607169);
}

.dang-soan__an {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.dang-soan__chu {
  white-space: pre-wrap;
}

/* Chữ lượn sóng: từng ký tự nhô lên và sáng màu lần lượt. */
.dang-soan__ky-tu {
  display: inline-block;
  white-space: pre;
  animation: dang-soan-song 1.6s ease-in-out infinite;
}

@keyframes dang-soan-song {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.65;
  }
  25% {
    transform: translateY(-3px);
    opacity: 1;
    color: var(--el-color-primary, #237b51);
  }
}

/* Ba chấm nhún nhảy phía trước. */
.dang-soan__cham {
  display: inline-flex;
  gap: 3px;
}

.dang-soan__cham i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--el-color-primary, #237b51);
  animation: dang-soan-cham 1s ease-in-out infinite;
}

.dang-soan__cham i:nth-child(2) {
  animation-delay: 0.15s;
}

.dang-soan__cham i:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes dang-soan-cham {
  0%,
  80%,
  100% {
    transform: scale(0.6);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Đổi câu: mờ dần và trượt nhẹ. */
.dang-soan-enter-active,
.dang-soan-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.dang-soan-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.dang-soan-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (prefers-reduced-motion: reduce) {
  .dang-soan__ky-tu,
  .dang-soan__cham i {
    animation: none;
  }

  .dang-soan-enter-active,
  .dang-soan-leave-active {
    transition: none;
  }
}
</style>
