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
.demo-chat { width: 100%; height: 100%; min-height: 0; }
.demo-chat__shell { width: 100%; height: 100%; max-width: none; min-height: 0; display: flex; flex-direction: column; }
</style>
