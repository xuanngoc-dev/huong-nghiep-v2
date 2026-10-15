<script setup>
import ChatPanel from '@/components/guest/chung/ChatPanel.vue'
defineOptions({ name: 'DemoChat' })
</script>

<template>
  <section class="demo-chat">
    <div class="demo-chat__shell">
      <header class="demo-chat__header">
        <div class="demo-chat__identity">
          <span class="demo-chat__avatar" aria-hidden="true"><el-icon :size="22"><ChatDotRound /></el-icon></span>
          <div>
            <h1>Trợ lý tư vấn tuyển sinh & định hướng</h1>
            <p>Tra cứu, so sánh thông tin tuyển sinh và kiểm tra nguồn tham khảo</p>
          </div>
        </div>
      </header>
      <ChatPanel />
    </div>
  </section>
</template>

<style scoped>
.demo-chat__shell { height: min(850px, calc(100dvh - 180px)); min-height: 480px; display: flex; flex-direction: column; }
@media (max-width: 600px) { .demo-chat__shell { height: calc(100dvh - 130px); min-height: 400px; } }
</style>
