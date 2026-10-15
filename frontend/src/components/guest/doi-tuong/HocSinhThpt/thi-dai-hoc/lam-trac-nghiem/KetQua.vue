<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchKetQua } from '@/api/phienKhaoSat'
import BuocLamBai from './BuocLamBai.vue'

defineOptions({ name: 'ThptKetQuaTracNghiem' })

const route = useRoute()
const ssid = computed(() => String(route.params.ssid || ''))
const dangTai = ref(false)
const loi = ref('')
const ketQua = ref(null)

const buoc = computed(() => [
  ...(ketQua.value?.buoc || []).map((item) => ({ ...item, xong: true })),
  { id: 'nganh-phu-hop', ten: 'Ngành phù hợp', xong: true },
  { id: 'ket-qua', ten: 'Kết quả', xong: false },
])
const diemCaoNhat = computed(() => Math.max(1, ...(ketQua.value?.nhom || []).map((item) => item.diem)))

async function taiKetQua(value) {
  ketQua.value = null
  loi.value = ''
  if (!value) {
    loi.value = 'Không có mã phiên khảo sát.'
    return
  }
  dangTai.value = true
  try {
    ketQua.value = await fetchKetQua(value)
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    loi.value = status === 404 && typeof detail === 'string' ? detail : 'Không tải được kết quả.'
  } finally {
    dangTai.value = false
  }
}

watch(ssid, taiKetQua, { immediate: true })
</script>

<template>
  <section class="quiz-flow py-4">
    <div class="container-fluid">
      <div class="holland-overview">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Kết quả trắc nghiệm Holland</h2>
          <p v-if="ketQua" class="holland-overview__lead">
            Đã trả lời {{ ketQua.so_da_tra_loi }}/{{ ketQua.so_cau_hoi }} câu.
          </p>
        </header>

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải kết quả…</p>

        <template v-else-if="ketQua">
          <BuocLamBai :ssid="ssid" :buoc="buoc" hien-tai="ket-qua" />

          <article class="holland-panel">
            <p class="holland-kicker">Mã nổi bật</p>
            <h3 class="holland-panel__title">{{ ketQua.ma_noi_bat || 'Chưa đủ đáp án' }}</h3>
            <p v-if="!ketQua.ma_noi_bat" class="quiz-note">
              Hãy hoàn thành các phần phía trước để hệ thống cộng điểm theo nhóm tính cách.
            </p>
            <ul class="quiz-scores">
              <li v-for="item in ketQua.nhom" :key="item.ma_nhom" class="quiz-score">
                <span class="quiz-score__code">{{ item.ma_nhom }}</span>
                <span class="quiz-score__body">
                  <span class="quiz-score__name">{{ item.ten_nhom }}</span>
                  <span class="quiz-score__track">
                    <span class="quiz-score__bar" :style="{ width: `${(item.diem / diemCaoNhat) * 100}%` }" />
                  </span>
                </span>
                <strong class="quiz-score__point">{{ item.diem }}</strong>
              </li>
            </ul>
          </article>
        </template>
      </div>
    </div>
  </section>
</template>

<style src="./quiz-type.scss"></style>

<style scoped>
.quiz-note {
  margin: 0 0 16px;
  color: #2c3a4d;
  font-weight: 400;
  line-height: 1.5;
}

.quiz-scores {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.quiz-score {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quiz-score__code {
  display: grid;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 8px;
  background: var(--guest-primary);
  color: #fff;
  font-weight: 500;
}

.quiz-score__body {
  flex: 1;
  min-width: 0;
}

.quiz-score__name {
  display: block;
  margin-bottom: 4px;
  color: #162033;
  font-weight: 400;
}

.quiz-score__track {
  display: block;
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #e6ece8;
}

.quiz-score__bar {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--guest-primary);
}

.quiz-score__point {
  flex: 0 0 2.5rem;
  color: #121a28;
  font-weight: 500;
  text-align: right;
}
</style>
