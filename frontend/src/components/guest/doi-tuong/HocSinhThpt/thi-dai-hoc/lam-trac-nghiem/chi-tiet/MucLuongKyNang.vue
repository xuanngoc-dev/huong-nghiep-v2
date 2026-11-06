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
  <div v-if="coDuLieu" class="luong" :class="{ 'luong--hai-cot': luong.length && kyNang.length }">
    <section v-if="luong.length" class="luong__so">
      <p>Mức lương tham khảo</p>
      <dl v-if="luong.length > 1 || luong[0].name" class="luong__muc">
        <div v-for="(item, index) in luong" :key="`${index}-${item.name}`">
          <dt>{{ item.name || 'Tham khảo' }}</dt>
          <dd>{{ hienMucLuong(item) }}</dd>
        </div>
      </dl>
      <strong v-else>{{ hienMucLuong(luong[0]) }}</strong>
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
  display: grid;
  gap: 16px;
}

.luong__so {
  margin: 0;
  padding: 16px;
  border-radius: 12px;
  background: #f6faf7;
}

.luong__so p {
  margin: 0;
  color: #31483d;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.luong__so strong {
  display: block;
  margin-top: 6px;
  color: #0c5c34;
  font-size: 1.35rem;
  line-height: 1.35;
  white-space: pre-line;
}

.luong__muc {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 8px 0 0;
}

.luong__muc div {
  display: grid;
  gap: 2px;
}

.luong__muc dt,
.luong__muc dd {
  margin: 0;
}

.luong__muc dt {
  color: #31483d;
  font-size: 0.85rem;
  font-weight: 600;
}

.luong__muc dd {
  color: #0c5c34;
  font-size: 1.05rem;
  font-weight: 700;
}

.luong h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.05rem;
  font-weight: 700;
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
  border-radius: 999px;
  background: #e7f5ec;
  color: #0c5c34;
  font-weight: 600;
}

@media (min-width: 768px) {
  .luong--hai-cot {
    grid-template-columns: minmax(200px, 280px) minmax(0, 1fr);
    align-items: start;
  }
}
</style>
