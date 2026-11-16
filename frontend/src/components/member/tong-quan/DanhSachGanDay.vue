<template>
  <el-card shadow="never" class="gan-day">
    <template #header>
      <div class="gan-day__dau">
        <h2 class="gan-day__tieu-de">
          <CustomIcon><component :is="icon" /></CustomIcon>
          {{ tieuDe }}
        </h2>
        <RouterLink v-if="xemTatCa" class="gan-day__xem" :to="xemTatCa">Xem tất cả</RouterLink>
      </div>
    </template>

    <p v-if="loi" class="gan-day__trong">{{ loi }}</p>
    <p v-else-if="dangTai" class="gan-day__trong">Đang tải…</p>
    <p v-else-if="!items.length" class="gan-day__trong">{{ trong }}</p>
    <ul v-else class="gan-day__ds">
      <li v-for="item in items" :key="item.key" class="gan-day__dong">
        <div class="gan-day__noi-dung">
          <span class="gan-day__ten">{{ item.ten }}</span>
          <span class="gan-day__phu">{{ item.phu }}</span>
        </div>
        <div class="gan-day__ben">
          <CustomTag v-if="item.nhan" :type="item.nhanLoai || 'info'" size="small">{{ item.nhan }}</CustomTag>
          <span class="gan-day__thoi-gian">{{ item.thoiGian }}</span>
        </div>
      </li>
    </ul>
  </el-card>
</template>

<script setup>
/**
 * Thẻ danh sách hoạt động gần đây dùng chung cho trang tổng quan.
 * items: Array<{ key, ten, phu?, nhan?, nhanLoai?, thoiGian }>
 */
defineProps({
  tieuDe: { type: String, required: true },
  icon: { type: [Object, Function], required: true },
  items: { type: Array, default: () => [] },
  // Route "Xem tất cả" (tùy chọn).
  xemTatCa: { type: [String, Object], default: null },
  trong: { type: String, default: 'Chưa có hoạt động nào.' },
  dangTai: { type: Boolean, default: false },
  loi: { type: String, default: '' },
})
</script>

<style scoped>
.gan-day {
  height: 100%;
  border-radius: 12px;
}

.gan-day__dau {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.gan-day__tieu-de {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 15px;
}

.gan-day__xem {
  color: var(--el-color-primary);
  font-size: 13px;
  text-decoration: none;
  white-space: nowrap;
}

.gan-day__xem:hover {
  text-decoration: underline;
}

.gan-day__trong {
  margin: 0;
  padding: 16px 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  text-align: center;
}

.gan-day__ds {
  margin: 0;
  padding: 0;
  list-style: none;
}

.gan-day__dong {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.gan-day__dong:last-child {
  border-bottom: 0;
}

.gan-day__noi-dung,
.gan-day__ben {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.gan-day__ben {
  flex-shrink: 0;
  align-items: flex-end;
  gap: 4px;
}

.gan-day__ten {
  overflow: hidden;
  color: var(--el-text-color-primary);
  font-size: 14px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gan-day__phu,
.gan-day__thoi-gian {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
