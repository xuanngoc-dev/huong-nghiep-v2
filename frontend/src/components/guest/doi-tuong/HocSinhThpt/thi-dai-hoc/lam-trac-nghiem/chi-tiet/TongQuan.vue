<template>
  <div v-if="muc.length" class="tong-quan">
    <section v-for="item in muc" :key="item.id" class="tong-quan__muc">
      <h3>{{ item.nhan }}</h3>
      <ul v-if="item.dong.length > 1">
        <li v-for="dong in item.dong" :key="dong">{{ dong }}</li>
      </ul>
      <p v-else>{{ item.dong[0] }}</p>
    </section>
  </div>
  <KhongCoDuLieu v-else text="Chưa có thông tin tổng quan cho ngành này." />
</template>

<script setup>
import { computed } from 'vue'
import { layChiTiet, tachDong } from './chiTiet'

defineOptions({ name: 'ChiTietTongQuan' })

const props = defineProps({
  nganh: { type: Object, required: true },
  chiTiet: { type: Object, default: null },
  vanBan: { type: String, default: '' },
})

const muc = computed(() => {
  const items = [
    { id: 'tong-quan', nhan: 'Tổng quan', keys: ['tong_quan'] },
    { id: 'mon-hoc', nhan: 'Môn học tiêu biểu', keys: ['mon_hoc_tieu_bieu'] },
    { id: 'phu-hop', nhan: 'Độ phù hợp', keys: ['do_phu_hop'] },
    { id: 'can-nhac', nhan: 'Điểm cân nhắc', keys: ['diem_can_nhac'] },
  ]
    .map((item) => ({ id: item.id, nhan: item.nhan, dong: tachDong(layChiTiet(props.chiTiet, item.keys)) }))
    .filter((item) => item.dong.length)
  const extra = String(props.vanBan || '').trim()
  const moTa = String(props.nganh?.mo_ta || '').trim()
  if (extra && extra !== moTa) items.push({ id: 'van-ban', nhan: 'Chi tiết', dong: tachDong(extra) })
  return items
})
</script>

<style scoped>
.tong-quan {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tong-quan__muc h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.05rem;
  font-weight: 700;
}

.tong-quan__muc p,
.tong-quan__muc li {
  color: #1c2836;
  font-size: 1rem;
  line-height: 1.55;
}

.tong-quan__muc p {
  margin: 8px 0 0;
  white-space: pre-line;
}

.tong-quan__muc ul {
  margin: 8px 0 0;
  padding-left: 1.2rem;
}

.tong-quan__muc li + li {
  margin-top: 4px;
}
</style>
