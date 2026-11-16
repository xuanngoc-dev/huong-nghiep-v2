<template>
  <el-dialog
    :model-value="modelValue"
    width="520px"
    align-center
    append-to-body
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="tien-trinh-dialog"
    aria-label="Đang xử lý yêu cầu"
  >
    <div class="tien-trinh" role="status" aria-live="polite">
      <div class="tien-trinh__dau">
        <span class="tien-trinh__icon" :class="{ 'is-xong': daXong }" aria-hidden="true">
          <el-icon><CircleCheck v-if="daXong" /><MagicStick v-else /></el-icon>
        </span>
        <div class="tien-trinh__chu">
          <!-- key theo bước để chữ mờ dần khi đổi bước. -->
          <Transition name="tien-trinh-chu" mode="out-in">
            <p :key="buocHienTai" class="tien-trinh__tieu-de">{{ buoc?.text }}</p>
          </Transition>
          <p class="tien-trinh__phu">
            <template v-if="daXong">
              Bước {{ buocs.length }}/{{ buocs.length }} · Tự đóng sau {{ giayConLai }} giây
            </template>
            <template v-else>Bước {{ buocHienTai }}/{{ buocs.length }} · Vui lòng chờ trong giây lát</template>
          </p>
        </div>
        <el-icon v-if="!daXong" class="tien-trinh__quay" aria-hidden="true"><Loading /></el-icon>
      </div>
      <div class="tien-trinh__thanh" aria-hidden="true">
        <span
          v-for="item in buocs"
          :key="item.step"
          class="tien-trinh__doan"
          :class="{ 'is-xong': item.step <= buocHienTai }"
        />
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
/**
 * Dialog tiến trình xử lý: icon, tiêu đề theo từng bước và thanh tiến trình chia đoạn (mỗi bước một đoạn).
 * Nơi gọi tự điều khiển `buoc-hien-tai`; bước cuối cùng được coi là hoàn tất.
 */
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { CircleCheck, Loading, MagicStick } from '@element-plus/icons-vue'
import { BUOC_TIEN_TRINH, THOI_GIAN_HOAN_TAT } from '@/data/tienTrinhXuLy'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  // Số thứ tự bước đang chạy (bắt đầu từ 1).
  buocHienTai: { type: Number, default: 1 },
  buocs: { type: Array, default: () => BUOC_TIEN_TRINH },
  // Thời gian đếm ngược ở bước hoàn tất (ms); nơi gọi đóng dialog sau đúng khoảng này.
  thoiGianHoanTat: { type: Number, default: THOI_GIAN_HOAN_TAT },
})

const buoc = computed(() => props.buocs.find((item) => item.step === props.buocHienTai) || props.buocs[0])
const daXong = computed(() => props.buocHienTai >= props.buocs.length)

// Đếm ngược "Tự đóng sau n giây" khi tới bước hoàn tất.
const giayConLai = ref(0)
let henGio = null

function dungDem() {
  clearInterval(henGio)
  henGio = null
}

watch(
  () => props.modelValue && daXong.value,
  (dangHoanTat) => {
    dungDem()
    if (!dangHoanTat) return
    giayConLai.value = Math.ceil(props.thoiGianHoanTat / 1000)
    henGio = setInterval(() => {
      giayConLai.value = Math.max(giayConLai.value - 1, 0)
      if (giayConLai.value === 0) dungDem()
    }, 1000)
  },
  { immediate: true },
)

onBeforeUnmount(dungDem)
</script>

<style scoped>
.tien-trinh {
  display: grid;
  gap: 18px;
}

.tien-trinh__dau {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tien-trinh__icon {
  display: grid;
  flex-shrink: 0;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: #eef6f1;
  color: #0c5c34;
  font-size: 24px;
  transition:
    background 0.3s ease,
    color 0.3s ease;
}

.tien-trinh__icon .el-icon {
  animation: tien-trinh-nhip 1.6s ease-in-out infinite;
}

.tien-trinh__icon.is-xong {
  background: #0c5c34;
  color: #fff;
}

.tien-trinh__icon.is-xong .el-icon {
  animation: none;
}

.tien-trinh__chu {
  flex: 1;
  min-width: 0;
}

.tien-trinh__quay {
  flex-shrink: 0;
  color: #3f9466;
  font-size: 22px;
  animation: tien-trinh-quay 1s linear infinite;
}

.tien-trinh__tieu-de {
  margin: 0 0 4px;
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.4;
}

.tien-trinh__phu {
  margin: 0;
  color: #5f6f66;
  font-size: 0.875rem;
}

.tien-trinh__thanh {
  display: flex;
  gap: 6px;
}

.tien-trinh__doan {
  flex: 1;
  height: 6px;
  border-radius: 999px;
  background: #e3ebe6;
  transition: background 0.4s ease;
}

.tien-trinh__doan.is-xong {
  background: #3f9466;
}

.tien-trinh-chu-enter-active,
.tien-trinh-chu-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.tien-trinh-chu-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.tien-trinh-chu-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@keyframes tien-trinh-quay {
  to {
    transform: rotate(360deg);
  }
}

@keyframes tien-trinh-nhip {
  50% {
    transform: scale(1.15) rotate(8deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .tien-trinh__icon .el-icon {
    animation: none;
  }

  .tien-trinh__quay {
    animation-duration: 3s;
  }

  .tien-trinh__doan,
  .tien-trinh-chu-enter-active,
  .tien-trinh-chu-leave-active {
    transition: none;
  }
}
</style>

<!-- el-dialog teleport ra body nên không dùng scoped. -->
<style>
.tien-trinh-dialog {
  max-width: calc(100vw - 32px);
  border-radius: 16px;
}

.tien-trinh-dialog .el-dialog__header {
  display: none;
}

.tien-trinh-dialog .el-dialog__body {
  padding: 24px;
}
</style>
