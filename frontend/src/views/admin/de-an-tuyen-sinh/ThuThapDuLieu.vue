<template>
  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Thu thập dữ liệu</h2>
    </div>
    <CustomEmpty description="Chức năng đang được phát triển.">
      <ul class="du-kien">
        <li>Thu thập đề án tuyển sinh từ website trường hoặc file tải lên (PDF, Word, Excel).</li>
        <li>Trích xuất chương trình, phương thức, tổ hợp, chỉ tiêu, điểm chuẩn và học phí về đúng cấu trúc đề án.</li>
        <li>Kiểm tra, đối chiếu và duyệt dữ liệu trước khi nhập vào danh sách đề án tuyển sinh.</li>
        <li>Theo dõi lịch sử và trạng thái các lần thu thập.</li>
      </ul>
    </CustomEmpty>
  </CustomCard>
</template>

<script setup>
// Giao diện chờ cho menu Thu thập dữ liệu (nhóm Đề án tuyển sinh).
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
