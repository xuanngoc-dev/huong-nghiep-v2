<script setup>
import { computed } from 'vue'
import { danhSachMucLuong, hienMucLuong } from '@/utils/capTenGiaTri'
import { layChiTiet, noiGiaTri, tachDong } from './chiTiet'

defineOptions({ name: 'ChiTietMucLuongKyNang' })

const props = defineProps({
  nganh: { type: Object, required: true },
  chiTiet: { type: Object, default: null },
  vanBan: { type: String, default: '' },
})

const luong = computed(() => {
  const tuCot = danhSachMucLuong(props.nganh?.muc_luong_tham_khao)
  if (tuCot.length) return tuCot
  const text = noiGiaTri(layChiTiet(props.chiTiet, ['muc_luong_tham_khao', 'muc_luong']))
  return text ? [{ name: '', value: text }] : []
})
const kyNang = computed(() => tachDong(layChiTiet(props.chiTiet, ['ky_nang_phu_hop', 'ky_nang'])))
const coDuLieu = computed(() => luong.value.length > 0 || kyNang.value.length > 0)
</script>

<template>
  <div v-if="coDuLieu" class="luong">
    <section v-if="luong.length">
      <h3>Mức lương tham khảo</h3>
      <div class="luong__cards">
        <article v-for="(item, index) in luong" :key="`${index}-${item.name}`" class="luong__card">
          <p class="luong__ten">{{ item.name || 'Tham khảo' }}</p>
          <p class="luong__gia">{{ hienMucLuong(item) }}</p>
        </article>
      </div>
    </section>
    <section v-if="kyNang.length">
      <h3>Kỹ năng phù hợp</h3>
      <ul class="luong__chip">
        <li v-for="item in kyNang" :key="item">{{ item }}</li>
      </ul>
    </section>
  </div>
  <KhongCoDuLieu v-else text="Chưa có mức lương và kỹ năng cho ngành này." />
</template>

<style scoped>
.luong {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.luong h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.05rem;
  font-weight: 700;
}

.luong__cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.luong__card {
  margin: 0;
  padding: 14px 16px;
  border: 1px solid #c5d5cc;
  border-radius: 12px;
  background: #f6faf7;
}

.luong__ten {
  margin: 0;
  color: #31483d;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.luong__gia {
  margin: 6px 0 0;
  color: #0c5c34;
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.35;
  white-space: pre-line;
}

.luong__chip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}

.luong__chip li {
  padding: 6px 12px;
  border-radius: 0.375rem;
  background: #e7f5ec;
  color: #0c5c34;
  font-weight: 600;
}
</style>
