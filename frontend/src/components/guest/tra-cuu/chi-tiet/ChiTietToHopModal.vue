<template>
  <KhungChiTiet v-model="visible" tieu-de="Chi tiết tổ hợp môn">
    <template v-if="t" #dau>
      <DauChiTiet :tieu-de="t.ten_to_hop" icon="Collection" :ma="t.ma_to_hop || ''" :nhan="locNhan([soMon])" />
    </template>

    <template v-if="t">
      <CardThongTin tieu-de="Các môn trong tổ hợp" icon="Collection" :nhan="dsMon" rong />
      <CardThongTin tieu-de="Ghi chú" icon="Document" :doan="t.ghi_chu" rong />
    </template>
  </KhungChiTiet>
</template>

<script setup>
/** Modal chi tiết tổ hợp môn ở trang Tra cứu (khách). Dữ liệu lấy từ danh sách đã tải, không gọi thêm API. */
import { computed } from 'vue'
import KhungChiTiet from './KhungChiTiet.vue'
import DauChiTiet from './DauChiTiet.vue'
import CardThongTin from './CardThongTin.vue'
import { locNhan } from './phanChiTiet'

defineOptions({ name: 'ChiTietToHopModal' })

const props = defineProps({
  item: { type: Object, default: null },
})
const visible = defineModel({ type: Boolean, default: false })

const t = computed(() => props.item)

// Tên tổ hợp dạng "Toán, Vật lý, Hóa học" → từng môn. ds_mon_hoc là mã môn (TOAN, LY…) nên không dùng để hiện.
const dsMon = computed(() => locNhan(String(t.value.ten_to_hop || '').split(/[,;]/).map((mon) => mon.trim())))
const soMon = computed(() => (dsMon.value.length > 1 ? `${dsMon.value.length} môn` : ''))
</script>
