<template>
  <div class="guest-layout">
    <header class="guest-header">
      <RouterLink to="/" class="guest-brand">
        <el-icon :size="22"><Monitor /></el-icon>
        <span>Định hướng nghề</span>
      </RouterLink>

      <div class="guest-actions">
        <el-switch
          v-model="isDark"
          inline-prompt
          active-text="🌙"
          inactive-text="☀️"
          aria-label="Đổi giao diện"
          @change="toggleDark"
        />
        <el-button @click="router.push('/login')">Đăng nhập</el-button>
        <el-button type="primary" @click="router.push('/register')">Đăng ký</el-button>
      </div>
    </header>

    <main class="guest-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor } from '@element-plus/icons-vue'

const router = useRouter()

const isDark = ref(document.documentElement.classList.contains('dark'))

function toggleDark(val) {
  document.documentElement.classList.toggle('dark', val)
  localStorage.setItem('darkMode', val ? '1' : '0')
}

onMounted(() => {
  const saved = localStorage.getItem('darkMode')
  if (saved === '1') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})
</script>

<style scoped lang="scss">
.guest-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
  color: var(--el-text-color-primary);
  font-size: var(--app-font-size);
}

.guest-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 64px;
  padding: 12px 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.guest-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--el-color-primary);
  font-weight: 700;
  font-size: calc(var(--app-font-size) + 1px);
  white-space: nowrap;
}

.guest-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.guest-main {
  flex: 1;
  padding: 24px;
}

@media (max-width: 640px) {
  .guest-header {
    padding: 12px 16px;
  }

  .guest-brand span {
    display: none;
  }

  .guest-main {
    padding: 16px;
  }
}
</style>
