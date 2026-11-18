<template>
  <el-card shadow="never" class="placeholder-card">
    <template #header>
      <h1 class="placeholder-card__title">Cuộc hội thoại mới</h1>
    </template>
    <el-empty description="Chức năng đang được phát triển.">
      <ul class="du-kien">
        <li>Bắt đầu cuộc trò chuyện mới với trợ lý tư vấn tuyển sinh, hướng nghiệp.</li>
        <li>Chọn mô hình AI và chủ đề (trường, ngành, điểm chuẩn, tổ hợp…) trước khi hỏi.</li>
        <li>Trợ lý dùng hồ sơ của bạn để cá nhân hóa câu trả lời.</li>
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
