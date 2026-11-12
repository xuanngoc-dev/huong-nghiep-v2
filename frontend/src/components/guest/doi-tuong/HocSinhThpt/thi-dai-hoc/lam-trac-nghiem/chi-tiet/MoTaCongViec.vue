<script setup>
import { computed } from 'vue'
import { danhSachCap } from '@/utils/capTenGiaTri'
import { layChiTiet, tachDong } from './chiTiet'

defineOptions({ name: 'ChiTietMoTaCongViec' })

const props = defineProps({
  nganh: { type: Object, required: true },
  chiTiet: { type: Object, default: null },
  vanBan: { type: String, default: '' },
})

const tuCot = computed(() => danhSachCap(props.nganh?.mo_ta_cong_viec))
const moTa = computed(() => (
  tuCot.value.length ? [] : tachDong(layChiTiet(props.chiTiet, ['mo_ta_cong_viec', 'cong_viec', 'nhiem_vu']))
))
const coHoi = computed(() => tachDong(layChiTiet(props.chiTiet, ['co_hoi_nghe_nghiep'])))
const congCu = computed(() => tachDong(layChiTiet(props.chiTiet, ['cong_cu'])))
const coDuLieu = computed(() => tuCot.value.length || moTa.value.length || coHoi.value.length || congCu.value.length)
</script>

<template>
  <div v-if="coDuLieu" class="cong-viec">
    <section v-for="(item, index) in tuCot" :key="`${index}-${item.name}`">
      <h3>{{ item.name || 'Công việc' }}</h3>
      <p class="cong-viec__lead">{{ item.value }}</p>
      <p v-if="item.ghi_chu" class="cong-viec__note">{{ item.ghi_chu }}</p>
    </section>
    <p v-if="moTa.length" class="cong-viec__lead">{{ moTa.join('\n') }}</p>
    <section v-if="coHoi.length">
      <h3>Cơ hội nghề nghiệp</h3>
      <ul class="cong-viec__viec">
        <li v-for="item in coHoi" :key="item">{{ item }}</li>
      </ul>
    </section>
    <section v-if="congCu.length">
      <h3>Công cụ thường dùng</h3>
      <ul class="cong-viec__chip">
        <li v-for="item in congCu" :key="item">{{ item }}</li>
      </ul>
    </section>
  </div>
  <KhongCoDuLieu v-else text="Chưa có mô tả công việc cho ngành này." />
</template>

<style scoped>
.cong-viec {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cong-viec__lead {
  margin: 0;
  color: #1c2836;
  font-size: 1rem;
  line-height: 1.55;
  white-space: pre-line;
}

.cong-viec section .cong-viec__lead {
  margin-top: 6px;
}

.cong-viec__note {
  margin: 4px 0 0;
  color: #5c6b63;
  font-size: 0.92rem;
  line-height: 1.5;
  white-space: pre-line;
}

.cong-viec h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.05rem;
  font-weight: 700;
}

.cong-viec__viec {
  margin: 8px 0 0;
  padding-left: 1.2rem;
  color: #1c2836;
  line-height: 1.55;
}

.cong-viec__viec li + li {
  margin-top: 4px;
}

.cong-viec__chip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}

.cong-viec__chip li {
  padding: 6px 12px;
  border-radius: 0.375rem;
  background: #e7f5ec;
  color: #0c5c34;
  font-weight: 400;
}
</style>
