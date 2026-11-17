<template>
  <div class="kq-tab">
    <div class="row g-3">
      <div class="col-12 col-lg-6">
        <article class="kq-card">
          <h3 class="kq-card__title kq-mb">Sở thích nghề nghiệp <span class="kq-muted">· điểm 6 nhóm RIASEC</span></h3>
          <BieuDoRadar
            :height="300"
            :categories="sauNhom.map((item) => `${item.ten_nhom} (${item.ma_nhom})`)"
            :values="sauNhom.map((item) => item.diem)"
            :noi-bat="viTriNoiBat"
            series-name="Điểm Holland"
          />
        </article>
      </div>
      <div class="col-12 col-lg-6">
        <article class="kq-card kq-nhan-xet">
          <h3 class="kq-card__title">Nhận xét</h3>
          <p v-for="(doan, index) in nhanXet" :key="index" :class="{ 'kq-nhan-xet__luu-y': index === nhanXet.length - 1 }">
            {{ doan }}
          </p>
        </article>
      </div>
    </div>

    <div v-if="top.length" class="row g-3">
      <div class="col-12 col-md-6 col-xl-4">
        <article class="kq-card">
          <h4 class="kq-y__title">Hoạt động bạn có thể yêu thích</h4>
          <ul class="kq-list">
            <li v-for="(x, i) in gopNoiDung(top, 'hoat_dong')" :key="i"><span class="kq-tag">{{ x.ma_nhom }}</span>{{ x.noi_dung }}</li>
          </ul>
        </article>
      </div>
      <div class="col-12 col-md-6 col-xl-4">
        <article class="kq-card">
          <h4 class="kq-y__title">Xu hướng làm việc</h4>
          <ul class="kq-list">
            <li v-for="item in top" :key="item.ma_nhom">
              <span class="kq-tag">{{ item.ma_nhom }}</span>{{ NOI_DUNG_NHOM[item.ma_nhom]?.xu_huong }}
            </li>
          </ul>
        </article>
      </div>
      <div class="col-12 col-xl-4">
        <article class="kq-card">
          <h4 class="kq-y__title">Đặc điểm nổi bật</h4>
          <ul class="kq-list">
            <li v-for="(x, i) in gopNoiDung(top, 'dac_diem')" :key="i"><span class="kq-tag">{{ x.ma_nhom }}</span>{{ x.noi_dung }}</li>
          </ul>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BieuDoRadar from '@/components/guest/BieuDoRadar.vue'
import { NOI_DUNG_NHOM, gopNoiDung, nhanXetTongQuan, theoThuTuRiasec } from '@/utils/ketQuaHolland'

const props = defineProps({
  nhom: { type: Array, default: () => [] },
  top: { type: Array, default: () => [] },
})

const sauNhom = computed(() => theoThuTuRiasec(props.nhom))
const viTriNoiBat = computed(() => {
  const ma = new Set(props.top.map((item) => item.ma_nhom))
  return sauNhom.value.flatMap((item, index) => (ma.has(item.ma_nhom) ? [index] : []))
})
const nhanXet = computed(() => nhanXetTongQuan(props.nhom))
</script>

<style scoped src="./ket-qua.css"></style>
