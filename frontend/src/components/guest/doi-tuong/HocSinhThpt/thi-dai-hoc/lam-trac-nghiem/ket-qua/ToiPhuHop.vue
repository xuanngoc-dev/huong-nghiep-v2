<template>
  <div class="kq-tab">
    <section class="kq-section">
      <h3 class="kq-section-title">Nghề nghiệp</h3>
      <div v-if="ngheTheoNhom.length" class="row g-3">
        <div v-for="nhom in ngheTheoNhom" :key="nhom.ma_nhom" class="col-12 col-lg-4">
          <article class="kq-card">
            <h4 class="kq-y__title"><span class="kq-tag">{{ nhom.ma_nhom }}</span>{{ nhom.ten_nhom }}</h4>
            <p class="kq-muted kq-mb">{{ nhom.mo_ta }}</p>
            <ul class="kq-chips">
              <li v-for="ten in nhom.nghe" :key="ten" class="kq-chip">{{ ten }}</li>
            </ul>
          </article>
        </div>
      </div>
      <p v-else class="kq-muted">Chưa có ví dụ nghề cho các nhóm này.</p>
    </section>

    <section class="kq-section">
      <header class="kq-section-head">
        <h3 class="kq-section-title">Ngành đào tạo</h3>
        <RouterLink class="kq-link" :to="{ name: 'thpt-thi-dai-hoc-nganh-phu-hop', params: { ssid }, query: routeQuery }">
          Xem tất cả {{ nganh.length }} ngành và so sánh
        </RouterLink>
      </header>
      <p v-if="loiNganh" class="kq-muted">{{ loiNganh }}</p>
      <p v-else-if="dangTaiNganh" class="kq-muted">Đang tải ngành phù hợp…</p>
      <p v-else-if="!nganh.length" class="kq-muted">Chưa có ngành đào tạo khớp kết quả của bạn.</p>
      <div v-else class="row g-3">
        <div v-for="item in nganh.slice(0, SO_NGANH)" :key="item.ma_nganh" class="col-12 col-md-6 col-xl-4">
          <RouterLink
            class="kq-card kq-nganh"
            :to="{ name: 'thpt-thi-dai-hoc-chi-tiet-nganh', params: { ssid, maNganh: item.ma_nganh }, query: routeQuery }"
          >
            <span class="kq-nganh__ma">{{ item.ma_nganh }} · {{ item.ten_nhom_nganh }}</span>
            <strong class="kq-nganh__ten">{{ item.ten_nganh }}</strong>
            <span>
              <span v-for="ma in item.ma_holand" :key="ma" class="kq-tag" :class="{ 'kq-tag--muted': !maTop.has(ma) }">{{ ma }}</span>
            </span>
          </RouterLink>
        </div>
      </div>
    </section>

    <section v-if="top.length" class="kq-section">
      <h3 class="kq-section-title">Môi trường làm việc</h3>
      <article class="kq-card">
        <ul class="kq-list">
          <li v-for="item in top" :key="item.ma_nhom">
            <span class="kq-tag">{{ item.ma_nhom }}</span>{{ NOI_DUNG_NHOM[item.ma_nhom]?.moi_truong }}
          </li>
        </ul>
      </article>
    </section>

    <p class="kq-muted">Mức phù hợp thực tế còn tùy năng lực, sức khỏe và điều kiện của bạn, không chỉ ở sở thích.</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { NOI_DUNG_NHOM, ngheGoiY } from '@/utils/ketQuaHolland'

const props = defineProps({
  ssid: { type: String, required: true },
  top: { type: Array, default: () => [] },
  danhMucNhom: { type: Array, default: () => [] },
  nganh: { type: Array, default: () => [] },
  dangTaiNganh: { type: Boolean, default: false },
  loiNganh: { type: String, default: '' },
  routeQuery: { type: Object, default: () => ({}) },
})

const SO_NGANH = 6

// Nghề gộp theo nhóm sở thích: mỗi nhóm một thẻ có mô tả chung và các nghề ví dụ.
const ngheTheoNhom = computed(() => {
  const nghe = ngheGoiY(props.top, props.danhMucNhom, 6)
  return props.top
    .map((item) => {
      const cuaNhom = nghe.filter((x) => x.ma_nhom === item.ma_nhom)
      return { ma_nhom: item.ma_nhom, ten_nhom: item.ten_nhom, mo_ta: cuaNhom[0]?.mo_ta || '', nghe: cuaNhom.map((x) => x.ten) }
    })
    .filter((nhom) => nhom.nghe.length)
})
const maTop = computed(() => new Set(props.top.map((item) => item.ma_nhom)))
</script>

<style scoped src="./ket-qua.css"></style>
