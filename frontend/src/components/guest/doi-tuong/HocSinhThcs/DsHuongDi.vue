<template>
  <div>
    <RouterLink class="goi-y-card mb-3" :to="{ name: tenRoute('hs-thcs-tu-danh-gia') }">
      <span class="goi-y-card__icon" aria-hidden="true">
        <el-icon><Compass /></el-icon>
      </span>
      <span class="goi-y-card__body">
        <span class="goi-y-card__ten">{{ goiYTen }}</span>
        <span class="goi-y-card__mo-ta">{{ goiYMoTa }}</span>
      </span>
      <span class="goi-y-card__nut">Tìm hướng đi phù hợp →</span>
    </RouterLink>

    <div class="directions-card">
      <h2 class="directions-heading">{{ tieuDe }}</h2>

      <div v-if="dangTai" class="ds-huong__trang-thai" role="status">Đang tải các hướng đi…</div>
      <div v-else-if="loi" class="ds-huong__trang-thai">
        {{ loi }}
        <button type="button" class="ds-huong__thu-lai" @click="taiHuongDi">Thử lại</button>
      </div>
      <div v-else-if="!dsHuong.length" class="ds-huong__trang-thai">Chưa có dữ liệu hướng đi sau THCS.</div>

      <div v-else class="row g-3">
        <div v-for="huong in dsHuong" :key="huong.id" class="col-12 col-xl-6">
          <HuongDiCard
            :image="anhHuongDi(huong)"
            :title="huong.ten_huong"
            :description="huong.mo_ta_tong_quan"
            :note="chiPhi(huong)"
            :to="{ name: tenRoute('hs-thcs-huong-di'), params: { maHuong: huong.ma_huong } }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Compass } from '@element-plus/icons-vue'
import HuongDiCard from '@/components/guest/chung/HuongDiCard.vue'
import { anhHuongDi, chiPhi, useDsHuongDiThcs } from './thcs'
import { useTenRouteThcs } from './useTenRouteThcs'

// Thẻ gợi ý tự đánh giá và danh sách hướng đi sau THCS; dùng chung cho trang học sinh THCS và phụ huynh có con học THCS.
defineOptions({ name: 'ThcsDsHuongDi' })

const props = defineProps({
  tieuDe: { type: String, required: true },
  goiYTen: { type: String, required: true },
  goiYMoTa: { type: String, required: true },
  // Tiền tố tên route của nhánh (vd. `ph-thcs`); bỏ trống là nhánh học sinh.
  tienTo: { type: String, default: '' },
})

const { tenRoute } = useTenRouteThcs(props.tienTo)
const { dsHuong, dangTai, loi, taiHuongDi } = useDsHuongDiThcs()

onMounted(taiHuongDi)
</script>

<style scoped>
.ds-huong__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.ds-huong__thu-lai {
  margin-left: 8px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.goi-y-card {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  padding: 16px 20px;
  border: 1px solid rgba(var(--guest-primary-rgb), 0.3);
  border-radius: var(--guest-radius);
  background: linear-gradient(120deg, rgba(var(--guest-primary-rgb), 0.1), #fff 70%);
  color: inherit;
  text-decoration: none;
  transition: box-shadow 0.3s ease;
}

.goi-y-card:hover {
  box-shadow: 0 12px 24px rgba(31, 122, 77, 0.12);
}

.goi-y-card__icon {
  display: inline-flex;
  flex: 0 0 44px;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--guest-primary);
  color: #fff;
  font-size: 1.4rem;
}

.goi-y-card__body {
  display: flex;
  flex: 1 1 240px;
  flex-direction: column;
  gap: 2px;
}

.goi-y-card__ten {
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 600;
}

.goi-y-card__mo-ta {
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
}

.goi-y-card__nut {
  border-radius: 999px;
  padding: 8px 16px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
}

.goi-y-card:focus-visible,
.ds-huong__thu-lai:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

@media (max-width: 575.98px) {
  .goi-y-card__nut {
    width: 100%;
    text-align: center;
  }
}
</style>
