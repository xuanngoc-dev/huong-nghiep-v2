<template>
  <div class="landing">
    <section class="landing__section" aria-labelledby="cam-nang-title">
      <div class="container-fluid">
        <div class="landing__head">
          <p class="landing__eyebrow">Cẩm nang hướng nghiệp</p>
          <h1 id="cam-nang-title" class="landing__title">Bài viết và tài nguyên hữu ích</h1>
          <p class="landing__lead">
            Kiến thức về hướng nghiệp, tuyển sinh, phát triển nghề nghiệp và xu hướng thị trường lao động.
          </p>
        </div>

        <div class="landing-explore__panel">
          <div class="landing-explore__filters flex-nowrap flex-md-wrap overflow-x-auto" role="group" aria-label="Chủ đề">
            <button
              v-for="item in chuDe"
              :key="item"
              type="button"
              class="landing-explore__chip"
              :class="{ 'is-active': item === chuDeDangChon }"
              :aria-pressed="item === chuDeDangChon"
              @click="chonChuDe(item)"
            >
              {{ item }}
            </button>
          </div>

          <form class="landing-explore__search" role="search" @submit.prevent>
            <label class="landing-explore__o-nhap">
              <el-icon aria-hidden="true"><Search /></el-icon>
              <input v-model="tuKhoa" type="search" placeholder="Tìm bài viết" aria-label="Tìm bài viết" />
            </label>
          </form>

          <p v-if="ketQua.length" class="cam-nang__dem">{{ ketQua.length }} bài viết</p>
          <div v-if="ketQua.length" class="row g-3">
            <div v-for="item in ketQua" :key="item.id" class="col-12 col-lg-6">
              <TheBaiViet :bai="item" />
            </div>
          </div>
          <KhongCoDuLieu v-else :text="tuKhoa ? `Không có bài viết nào khớp “${tuKhoa}”.` : 'Chưa có bài viết.'" />
        </div>

        <HoTroDinhHuong class="cam-nang__ho-tro" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { articles } from '@/data/landing'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import KhongCoDuLieu from '@/components/guest/chung/KhongCoDuLieu.vue'
import TheBaiViet from '@/components/guest/cam-nang/TheBaiViet.vue'
import { locBaiViet } from '@/components/guest/cam-nang/locBaiViet'
import '@/components/guest/landing/landing.css'

defineOptions({ name: 'CamNang' })

const TAT_CA = 'Tất cả'

const route = useRoute()
const router = useRouter()

// Bài viết hiện là dữ liệu tĩnh (data/landing.js), lọc ngay trên trình duyệt.
const chuDe = [TAT_CA, ...new Set(articles.map((item) => item.category))]
// Chủ đề lưu trên query ?chu-de= để chia sẻ link được.
const chuDeDangChon = computed(() => (chuDe.includes(route.query['chu-de']) ? route.query['chu-de'] : TAT_CA))
const tuKhoa = ref(route.query.q || '')

const ketQua = computed(() =>
  locBaiViet(articles, { chuDe: chuDeDangChon.value === TAT_CA ? '' : chuDeDangChon.value, tuKhoa: tuKhoa.value }),
)

function chonChuDe(item) {
  const query = { ...route.query, 'chu-de': item === TAT_CA ? undefined : item }
  router.replace({ name: 'cam-nang', query })
}

watch(tuKhoa, (value) => {
  router.replace({ name: 'cam-nang', query: { ...route.query, q: value.trim() || undefined } })
})
</script>

<style scoped>
.cam-nang__dem {
  margin: 0 0 var(--lp-gap-sm);
  color: var(--lp-muted);
}

.cam-nang__ho-tro {
  margin-top: calc(var(--lp-gap) * 2);
}
</style>
