<template>
  <el-card shadow="never" class="placeholder-card">
    <template #header>
      <h1 class="placeholder-card__title">Cấu hình hội thoại</h1>
    </template>
    <el-empty description="Chức năng đang được phát triển.">
      <ul class="du-kien">
        <li>Chọn mô hình AI mặc định khi bắt đầu hội thoại mới.</li>
        <li>Bật / tắt dùng hồ sơ năng lực và hồ sơ xét tuyển để cá nhân hóa câu trả lời.</li>
        <li>Tùy chọn lưu lịch sử hội thoại và số lượt hỏi đáp còn lại của gói.</li>
      </ul>
    </el-empty>
  </el-card>
</template>

<script setup>
// Giao diện chờ cho nhóm menu Hội thoại của thành viên.
</script>

<style scoped>
.placeholder-card {
  border-radius: 12px;
}

.placeholder-card__title {
  margin: 0;
  font-size: 18px;
}

.du-kien {
  max-width: 560px;
  margin: 0 auto;
  padding-left: 20px;
  color: var(--el-text-color-secondary);
  line-height: 1.7;
  text-align: left;
}
</style>
