<template>
  <el-card shadow="never" class="placeholder-card">
    <template #header>
      <h1 class="placeholder-card__title">Danh sách hội thoại</h1>
    </template>
    <el-empty description="Chức năng đang được phát triển.">
      <ul class="du-kien">
        <li>Xem lại các cuộc hội thoại đã có với trợ lý, mới nhất trước.</li>
        <li>Tìm theo nội dung, lọc theo trạng thái (đang hoạt động, đã kết thúc).</li>
        <li>Mở lại cuộc hội thoại đang hoạt động để hỏi tiếp, đổi tên hoặc xóa cuộc hội thoại.</li>
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
