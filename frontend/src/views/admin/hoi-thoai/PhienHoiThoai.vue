<template>
  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Phiên hội thoại</h2>
    </div>
    <CustomEmpty description="Chức năng đang được phát triển.">
      <ul class="du-kien">
        <li>Danh sách phiên trò chuyện của thành viên và khách vãng lai, lọc theo người dùng, trạng thái, thời gian.</li>
        <li>Xem lại toàn bộ tin nhắn của một phiên, nguồn tham khảo và đánh giá của người dùng.</li>
        <li>Đóng / lưu trữ / xóa phiên hội thoại.</li>
      </ul>
    </CustomEmpty>
  </CustomCard>
</template>

<script setup>
// Giao diện chờ: dữ liệu lấy từ bảng chat_conversations / chat_messages khi có API.
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
