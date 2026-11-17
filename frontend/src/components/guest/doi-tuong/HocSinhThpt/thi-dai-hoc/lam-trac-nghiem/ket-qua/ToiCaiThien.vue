<template>
  <div class="kq-tab">
    <div class="row g-3">
      <div class="col-12 col-lg-6">
        <article class="kq-card">
          <h3 class="kq-card__title kq-mb">Kỹ năng cần phát triển</h3>
          <ul v-if="top.length" class="kq-list">
            <li v-for="(x, i) in gopNoiDung(top, 'ky_nang')" :key="i"><span class="kq-tag">{{ x.ma_nhom }}</span>{{ x.noi_dung }}</li>
          </ul>
          <p v-else class="kq-muted">Hoàn thành trắc nghiệm để nhận gợi ý kỹ năng.</p>
        </article>
      </div>
      <div class="col-12 col-lg-6">
        <article class="kq-card kq-card--nhac">
          <h3 class="kq-card__title kq-mb">Những điểm cần khám phá thêm</h3>
          <ul class="kq-list">
            <li v-for="item in top" :key="item.ma_nhom">
              <span class="kq-tag">{{ item.ma_nhom }}</span>{{ NOI_DUNG_NHOM[item.ma_nhom]?.can_nhac }}
            </li>
            <li v-if="itQuanTam.length">
              <span class="kq-tag">?</span>
              Bạn ít quan tâm đến nhóm {{ itQuanTam.map((item) => `${item.ten_nhom} (${item.ma_nhom})`).join(', ') }}.
              Có thể do bạn chưa có dịp trải nghiệm; hãy thử một hoạt động nhỏ thuộc nhóm này trước khi loại bỏ.
            </li>
            <li>
              <span class="kq-tag">!</span>
              Sở thích chưa phải là năng lực. Hãy đối chiếu với kết quả học tập, môn mạnh và trải nghiệm thực tế.
            </li>
          </ul>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { NOI_DUNG_NHOM, gopNoiDung, theoThuTuRiasec } from '@/utils/ketQuaHolland'

const props = defineProps({
  nhom: { type: Array, default: () => [] },
  top: { type: Array, default: () => [] },
})

// Nhóm điểm thấp nhất (ngoài nhóm nổi bật), tối đa 2 nhóm.
const itQuanTam = computed(() => {
  const maTop = new Set(props.top.map((item) => item.ma_nhom))
  const ds = theoThuTuRiasec(props.nhom).filter((item) => !maTop.has(item.ma_nhom))
  if (!ds.length) return []
  const thap = Math.min(...ds.map((item) => Number(item.diem) || 0))
  return ds.filter((item) => (Number(item.diem) || 0) === thap).slice(0, 2)
})
</script>

<style scoped src="./ket-qua.css"></style>
