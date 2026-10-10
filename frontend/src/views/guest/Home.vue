<script setup>
import { onMounted, ref } from 'vue'
import { getHealth } from '@/api/health'

const loading = ref(true)
const connected = ref(false)
const appName = ref('')
const message = ref('')

onMounted(async () => {
  try {
    const data = await getHealth()
    connected.value = data.status === 'ok'
    appName.value = data.app_name
    message.value = connected.value
      ? 'Frontend đã gọi được API backend.'
      : 'Backend phản hồi nhưng trạng thái không hợp lệ.'
  } catch {
    connected.value = false
    message.value = 'Không kết nối được backend. Hãy chạy API: make be (port 3060).'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <el-card class="home-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Khung dự án</span>
        <el-tag v-if="loading" type="info">Đang kiểm tra…</el-tag>
        <el-tag v-else-if="connected" type="success">Đã kết nối</el-tag>
        <el-tag v-else type="danger">Chưa kết nối</el-tag>
      </div>
    </template>

    <h1>Định hướng nghề</h1>
    <p class="lead">
      Vue + Element Plus gọi REST API FastAPI. Thêm endpoint ở
      <code>backend/app/api/v1/endpoints</code>, rồi gọi từ
      <code>frontend/src/api</code>.
    </p>

    <el-alert
      class="status-alert"
      :title="loading ? 'Đang kiểm tra API…' : connected ? `Đã kết nối ${appName}` : 'Chưa kết nối backend'"
      :description="message"
      :type="loading ? 'info' : connected ? 'success' : 'error'"
      :closable="false"
      show-icon
    />
  </el-card>
</template>

<style scoped>
.home-card {
  border-radius: 12px;
  max-width: 760px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

h1 {
  margin: 0 0 12px;
  font-size: 32px;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.lead {
  margin: 0;
  max-width: 58ch;
  color: var(--el-text-color-regular);
}

.status-alert {
  margin-top: 20px;
}
</style>
