<script setup>
import { computed } from 'vue'
import { layChiTiet, thanhTruong } from './chiTiet'

defineOptions({ name: 'ChiTietTruongDaoTao' })

const props = defineProps({
  nganh: { type: Object, required: true },
  chiTiet: { type: Object, default: null },
  vanBan: { type: String, default: '' },
})

const truong = computed(() => thanhTruong(layChiTiet(props.chiTiet, ['truong_dao_tao'])))
</script>

<template>
  <ul v-if="truong.length" class="truong">
    <li v-for="item in truong" :key="item.ten" class="truong__item">
      <h3>{{ item.ten }}</h3>
      <p v-if="item.phu">{{ item.phu }}</p>
    </li>
  </ul>
  <KhongCoDuLieu v-else text="Chưa có trường đào tạo cho ngành này." />
</template>

<style scoped>
.truong {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.truong__item {
  margin: 0;
  padding: 12px 14px;
  border: 1px solid #c5d5cc;
  border-radius: 10px;
  background: #f6faf7;
}

.truong__item h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.4;
}

.truong__item p {
  margin: 4px 0 0;
  color: #1c2836;
  line-height: 1.5;
}
</style>
