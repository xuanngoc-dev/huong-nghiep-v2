<template>
  <ol v-if="buoc.length" class="lo-trinh">
    <li v-for="(item, index) in buoc" :key="`${index}-${item.tieuDe}`" class="lo-trinh__item">
      <span class="lo-trinh__index">{{ index + 1 }}</span>
      <h3>{{ item.tieuDe }}</h3>
      <p v-if="item.noiDung">{{ item.noiDung }}</p>
      <p v-if="item.ghiChu" class="lo-trinh__note">{{ item.ghiChu }}</p>
    </li>
  </ol>
  <KhongCoDuLieu v-else text="Chưa có lộ trình phát triển cho ngành này." />
</template>

<script setup>
import { computed } from 'vue'
import { danhSachCap } from '@/utils/capTenGiaTri'
import { layChiTiet, thanhBuoc } from './chiTiet'

defineOptions({ name: 'ChiTietLoTrinhPhatTrien' })

const props = defineProps({
  nganh: { type: Object, required: true },
  chiTiet: { type: Object, default: null },
  vanBan: { type: String, default: '' },
})

const buoc = computed(() => {
  const tuCot = danhSachCap(props.nganh?.lo_trinh_phat_trien)
  if (tuCot.length) {
    return thanhBuoc(tuCot.map((item) => ({
      ten: item.name || 'Bước',
      mo_ta: item.value,
      ghi_chu: item.ghi_chu,
    })))
  }
  return thanhBuoc(layChiTiet(props.chiTiet, ['lo_trinh_phat_trien', 'lo_trinh', 'lo_trinh_nghe_nghiep']))
})
</script>

<style scoped>
.lo-trinh {
  margin: 0;
  padding: 0;
  list-style: none;
}

.lo-trinh__item {
  position: relative;
  padding: 0 0 18px 36px;
}

.lo-trinh__item:last-child {
  padding-bottom: 0;
}

.lo-trinh__item::before {
  content: '';
  position: absolute;
  top: 24px;
  bottom: 0;
  left: 11px;
  width: 2px;
  background: #c5d5cc;
}

.lo-trinh__item:last-child::before {
  display: none;
}

.lo-trinh__index {
  position: absolute;
  top: 0;
  left: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #0c5c34;
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  line-height: 24px;
  text-align: center;
}

.lo-trinh__item h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 24px;
}

.lo-trinh__item p {
  margin: 4px 0 0;
  color: #1c2836;
  line-height: 1.55;
  white-space: pre-line;
}

.lo-trinh__note {
  color: #5c6b63;
  font-size: 0.92rem;
}
</style>
