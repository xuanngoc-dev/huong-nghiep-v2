<template>
  <!-- Xem Chính sách bảo mật / Điều khoản sử dụng ngay trong form đăng ký, không rời trang. -->
  <CustomDialog
    :model-value="modelValue"
    :title="vanBan?.tieuDe || ''"
    :width="760"
    height="75vh"
    class="dialog-van-ban"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template v-if="vanBan">
      <p class="dialog-van-ban__cap-nhat">Cập nhật lần cuối: {{ dinhDangNgay(vanBan.capNhat) }}</p>
      <NoiDungVanBan :van-ban="vanBan" />
    </template>
    <template #footer>
      <CustomButton @click="emit('update:modelValue', false)">Đóng</CustomButton>
      <CustomButton type="primary" @click="dongY">Tôi đồng ý</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import { dinhDangNgay } from '@/utils/thoiGian'
import NoiDungVanBan from './NoiDungVanBan.vue'

defineOptions({ name: 'DialogVanBan' })

defineProps({
  modelValue: { type: Boolean, default: false },
  // Một văn bản trong data/vanBanPhapLy.js.
  vanBan: { type: Object, default: null },
})

// dong-y: người dùng bấm "Tôi đồng ý" (form đăng ký tự đánh dấu ô đồng ý).
const emit = defineEmits(['update:modelValue', 'dong-y'])

function dongY() {
  emit('dong-y')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.dialog-van-ban__cap-nhat {
  margin: 0 0 16px;
  color: #64748b;
  font-size: 0.875rem;
}
</style>
