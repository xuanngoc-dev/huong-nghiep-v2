<template>
  <div class="kq-tong-quan">
    <div class="row g-3">
      <div class="col-12 col-lg-5">
        <article class="kq-card kq-ma">
          <p class="kq-kicker">Mã Holland của bạn</p>
          <p class="kq-ma__code">{{ maNoiBat || '—' }}</p>
          <ol v-if="top.length" class="kq-ma__list">
            <li v-for="(item, index) in top" :key="item.ma_nhom" class="kq-ma__item">
              <span class="kq-ma__badge" :class="`kq-ma__badge--${index + 1}`">{{ item.ma_nhom }}</span>
              <span class="kq-ma__name">
                {{ item.ten_nhom }}
                <span v-if="item.mo_ta" class="kq-ma__desc">{{ item.mo_ta }}</span>
              </span>
              <span class="kq-ma__point">{{ item.diem }} điểm</span>
            </li>
          </ol>
          <p v-else class="kq-muted">Chưa đủ câu trả lời để xác định nhóm sở thích nổi bật.</p>
        </article>
      </div>
      <div class="col-12 col-lg-7">
        <article class="kq-card">
          <header class="kq-card__head">
            <h3 class="kq-card__title">Điểm 6 nhóm RIASEC</h3>
            <p class="kq-card__sub">3 nhóm nổi bật được tô đậm</p>
          </header>
          <BieuDoRadar
            :height="300"
            :categories="sauNhom.map((item) => `${item.ten_nhom} (${item.ma_nhom})`)"
            :values="sauNhom.map((item) => item.diem)"
            :noi-bat="viTriNoiBat"
            series-name="Điểm Holland"
          />
          <table class="kq-bang">
            <caption class="visually-hidden">Điểm từng nhóm Holland</caption>
            <tbody>
              <tr v-for="item in sauNhom" :key="item.ma_nhom">
                <th scope="row">{{ item.ma_nhom }} · {{ item.ten_nhom }}</th>
                <td>
                  <span class="kq-bang__track"><span :style="{ width: `${tyLe(item)}%` }" /></span>
                </td>
                <td class="kq-bang__point">{{ item.diem }}</td>
              </tr>
            </tbody>
          </table>
        </article>
      </div>
    </div>

    <article class="kq-card kq-nhan-xet">
      <h3 class="kq-card__title">Nhận xét tổng quan</h3>
      <p v-for="(doan, index) in nhanXet" :key="index" :class="{ 'kq-nhan-xet__luu-y': index === nhanXet.length - 1 }">
        {{ doan }}
      </p>
    </article>

    <template v-if="top.length">
      <h3 class="kq-section-title">Khám phá bản thân</h3>
      <div class="row g-3">
        <div class="col-12 col-md-6 col-xl-4">
          <article class="kq-card kq-y">
            <h4 class="kq-y__title">Đặc điểm và sở thích nổi bật</h4>
            <ul class="kq-list">
              <li v-for="(x, i) in gop('dac_diem')" :key="i"><span class="kq-tag">{{ x.ma_nhom }}</span>{{ x.noi_dung }}</li>
            </ul>
          </article>
        </div>
        <div class="col-12 col-md-6 col-xl-4">
          <article class="kq-card kq-y">
            <h4 class="kq-y__title">Hoạt động có thể yêu thích</h4>
            <ul class="kq-list">
              <li v-for="(x, i) in gop('hoat_dong')" :key="i"><span class="kq-tag">{{ x.ma_nhom }}</span>{{ x.noi_dung }}</li>
            </ul>
          </article>
        </div>
        <div class="col-12 col-md-6 col-xl-4">
          <article class="kq-card kq-y">
            <h4 class="kq-y__title">Phong cách và môi trường làm việc phù hợp</h4>
            <ul class="kq-list">
              <li v-for="item in top" :key="item.ma_nhom">
                <span class="kq-tag">{{ item.ma_nhom }}</span>{{ NOI_DUNG_NHOM[item.ma_nhom]?.moi_truong }}
              </li>
            </ul>
          </article>
        </div>
        <div class="col-12 col-md-6 col-xl-6">
          <article class="kq-card kq-y">
            <h4 class="kq-y__title">Kỹ năng nên phát triển</h4>
            <ul class="kq-list">
              <li v-for="(x, i) in gop('ky_nang')" :key="i"><span class="kq-tag">{{ x.ma_nhom }}</span>{{ x.noi_dung }}</li>
            </ul>
          </article>
        </div>
        <div class="col-12 col-xl-6">
          <article class="kq-card kq-y kq-y--can-nhac">
            <h4 class="kq-y__title">Những điều cần cân nhắc khi chọn nghề</h4>
            <ul class="kq-list">
              <li v-for="item in top" :key="item.ma_nhom">
                <span class="kq-tag">{{ item.ma_nhom }}</span>{{ NOI_DUNG_NHOM[item.ma_nhom]?.can_nhac }}
              </li>
              <li>
                <span class="kq-tag">!</span>Sở thích có thể thay đổi theo thời gian và trải nghiệm. Hãy xem kết quả là gợi ý để
                tìm hiểu, không phải quyết định cuối cùng.
              </li>
            </ul>
          </article>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BieuDoRadar from '@/components/guest/BieuDoRadar.vue'
import { NOI_DUNG_NHOM, gopNoiDung, nhanXetTongQuan, theoThuTuRiasec } from '@/utils/ketQuaHolland'

const props = defineProps({
  nhom: { type: Array, default: () => [] },
  top: { type: Array, default: () => [] },
  maNoiBat: { type: String, default: '' },
})

const sauNhom = computed(() => theoThuTuRiasec(props.nhom))
const viTriNoiBat = computed(() => {
  const ma = new Set(props.top.map((item) => item.ma_nhom))
  return sauNhom.value.flatMap((item, index) => (ma.has(item.ma_nhom) ? [index] : []))
})
const diemCao = computed(() => Math.max(1, ...sauNhom.value.map((item) => item.diem)))
const nhanXet = computed(() => nhanXetTongQuan(props.nhom))

function tyLe(item) {
  return Math.round((item.diem / diemCao.value) * 100)
}

function gop(khoa) {
  return gopNoiDung(props.top, khoa)
}
</script>

<style scoped src="./ket-qua.css"></style>
