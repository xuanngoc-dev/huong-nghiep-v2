<template>
  <KhungChiTiet v-model="visible" tieu-de="Chi tiết phương thức tuyển sinh">
    <template v-if="p" #dau>
      <DauChiTiet
        :tieu-de="p.ten_phuong_thuc"
        icon="Tickets"
        :ma="p.ma_phuong_thuc || ''"
      />
    </template>

    <template v-if="p">
      <CardThongTin tieu-de="Phương thức này là gì?" icon="QuestionFilled" :doan="p.giai_thich" rong />
      <CardThongTin tieu-de="Áp dụng như thế nào?" icon="Guide" :doan="p.truong_hop_cu_the" />
      <CardThongTin tieu-de="Lưu ý" icon="WarningFilled" :doan="p.luu_y" luu-y />
    </template>
  </KhungChiTiet>
</template>

<script setup>
/** Modal chi tiết phương thức tuyển sinh ở trang Tra cứu (khách). Dữ liệu lấy từ danh sách đã tải, không gọi thêm API. */
import { computed } from 'vue'
import KhungChiTiet from './KhungChiTiet.vue'
import DauChiTiet from './DauChiTiet.vue'
import CardThongTin from './CardThongTin.vue'

defineOptions({ name: 'ChiTietPhuongThucModal' })

const props = defineProps({
  item: { type: Object, default: null },
})
const visible = defineModel({ type: Boolean, default: false })

const p = computed(() => props.item)
</script>
