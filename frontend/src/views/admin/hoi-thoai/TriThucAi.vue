<template>
  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Tri thức &amp; AI</h2>
    </div>
    <CustomEmpty description="Chức năng đang được phát triển.">
      <ul class="du-kien">
        <li>Quản lý nguồn tri thức trợ lý dùng để trả lời (tài liệu, câu hỏi thường gặp).</li>
        <li>Cấu hình model AI, lời nhắc hệ thống và giới hạn sử dụng.</li>
        <li>Thống kê câu hỏi, token sử dụng và tỷ lệ câu trả lời được đánh giá hữu ích.</li>
      </ul>
    </CustomEmpty>
  </CustomCard>
</template>

<script setup>
// Giao diện chờ cho nhóm menu Hội thoại.
</script>

<style scoped>
.du-kien {
  max-width: 560px;
  margin: 0 auto;
  padding-left: 20px;
  color: var(--el-text-color-secondary);
  line-height: 1.7;
  text-align: left;
}
</style>
