<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  text: { type: String, default: 'Đang phân tích kết quả…' },
})
</script>

<template>
  <Teleport to="body">
    <Transition name="think-loading">
      <div v-if="visible" class="think-loading" role="status" aria-live="polite" :aria-label="text">
        <div class="think-loading__stage">
          <div class="think-bubbles" aria-hidden="true">
            <span class="think-bubbles__dot" />
            <span class="think-bubbles__dot think-bubbles__dot--mid" />
            <span class="think-bubbles__cloud">?</span>
          </div>
          <div class="think-face" aria-hidden="true">
            <span class="think-face__blush think-face__blush--left" />
            <span class="think-face__blush think-face__blush--right" />
            <span class="think-face__eye think-face__eye--left"><i /></span>
            <span class="think-face__eye think-face__eye--right"><i /></span>
            <span class="think-face__mouth" />
          </div>
          <p class="think-loading__text">{{ text }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.think-loading {
  position: fixed;
  inset: 0;
  z-index: 4000;
  display: grid;
  place-items: center;
  background: rgba(246, 251, 247, 0.94);
  backdrop-filter: blur(3px);
}

.think-loading__stage {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.think-bubbles {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 72px;
  margin-bottom: 8px;
  margin-left: 88px;
}

.think-bubbles__dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 4px 10px rgba(63, 150, 67, 0.16);
  animation: think-pop 1.6s ease-in-out infinite;
}

.think-bubbles__dot--mid {
  width: 18px;
  height: 18px;
  animation-delay: 0.2s;
}

.think-bubbles__cloud {
  display: grid;
  width: 54px;
  height: 54px;
  place-items: center;
  border-radius: 50%;
  background: #fff;
  color: var(--guest-primary, #3f9643);
  font-size: 1.55rem;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(63, 150, 67, 0.16);
  animation: think-pop 1.6s ease-in-out infinite;
  animation-delay: 0.4s;
}

.think-face {
  position: relative;
  width: 148px;
  height: 132px;
  border-radius: 58% 58% 50% 50%;
  background: #7dca78;
  box-shadow:
    inset 0 -12px 0 rgba(47, 122, 58, 0.12),
    0 16px 30px rgba(63, 150, 67, 0.22);
  animation: think-bob 1.6s ease-in-out infinite;
}

.think-face__eye {
  position: absolute;
  top: 46px;
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 50%;
  background: #fff;
}

.think-face__eye--left {
  left: 34px;
}

.think-face__eye--right {
  right: 34px;
}

.think-face__eye i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #1c2b23;
  transform: translate(2px, -3px);
  animation: think-look 1.6s ease-in-out infinite;
}

.think-face__blush {
  position: absolute;
  top: 78px;
  width: 16px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 138, 158, 0.55);
}

.think-face__blush--left {
  left: 22px;
}

.think-face__blush--right {
  right: 22px;
}

.think-face__mouth {
  position: absolute;
  bottom: 28px;
  left: 50%;
  width: 22px;
  height: 10px;
  border-bottom: 3px solid #1c2b23;
  border-radius: 0 0 16px 16px;
  transform: translateX(-50%);
}

.think-loading__text {
  margin: 22px 0 0;
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 700;
}

.think-loading-enter-active,
.think-loading-leave-active {
  transition: opacity 0.2s ease;
}

.think-loading-enter-from,
.think-loading-leave-to {
  opacity: 0;
}

@keyframes think-bob {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-8px);
  }
}

@keyframes think-pop {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }

  50% {
    transform: translateY(-6px) scale(1.08);
  }
}

@keyframes think-look {
  0%,
  100% {
    transform: translate(2px, -3px);
  }

  50% {
    transform: translate(4px, -6px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .think-face,
  .think-bubbles__dot,
  .think-bubbles__cloud,
  .think-face__eye i {
    animation: none;
  }
}
</style>
