<template>
  <section class="thcs py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="intro-card mb-3">
            <h1 class="thcs__title">Học sinh THCS: chọn hướng đi sau lớp 9</h1>
            <p class="thcs__lead mb-0">
              Hết lớp 9 bạn có nhiều con đường: học THPT, học nghề hay vừa học vừa làm. Hãy xem từng hướng đi, ưu nhược
              điểm và chi phí, hoặc trả lời vài câu hỏi ngắn để biết hướng nào hợp với bạn nhất.
            </p>
          </div>

          <RouterLink class="goi-y-card mb-3" :to="{ name: 'hs-thcs-tu-danh-gia' }">
            <span class="goi-y-card__icon" aria-hidden="true">
              <el-icon><Compass /></el-icon>
            </span>
            <span class="goi-y-card__body">
              <span class="goi-y-card__ten">Chưa biết chọn hướng nào?</span>
              <span class="goi-y-card__mo-ta">
                Tự đánh giá học lực, sở thích, hoàn cảnh gia đình để nhận gợi ý hướng đi phù hợp.
              </span>
            </span>
            <span class="goi-y-card__nut">Tìm hướng đi phù hợp →</span>
          </RouterLink>

          <div class="directions-card">
            <h2 class="directions-heading">Là học sinh THCS, bạn định hướng gì sau khi học xong lớp 9</h2>

            <div v-if="dangTai" class="thcs__trang-thai" role="status">Đang tải các hướng đi…</div>
            <div v-else-if="loi" class="thcs__trang-thai">
              {{ loi }}
              <button type="button" class="thcs__thu-lai" @click="taiHuongDi">Thử lại</button>
            </div>
            <div v-else-if="!dsHuong.length" class="thcs__trang-thai">Chưa có dữ liệu hướng đi sau THCS.</div>

            <div v-else class="row g-3">
              <div v-for="huong in dsHuong" :key="huong.id" class="col-12 col-xl-6">
                <HuongDiCard
                  :image="anhHuongDi(huong)"
                  :title="huong.ten_huong"
                  :description="huong.mo_ta_tong_quan"
                  :note="chiPhi(huong)"
                  :to="{ name: 'hs-thcs-huong-di', params: { maHuong: huong.ma_huong } }"
                />
              </div>
            </div>
          </div>

          <div class="d-flex flex-column gap-3 mt-3">
            <HoTroDinhHuong />
            <CauHoiThuongGap />
          </div>
        </div>

        <div class="col-lg-3">
          <div class="audiences-card">
            <h2 id="chon-lai-doi-tuong" class="h4 mb-3">Chọn lại đối tượng</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-doi-tuong">
              <button
                v-for="item in audiences"
                :key="item.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': selectedCode === item.code, 'is-locked': !item.moTruyCap }"
                :disabled="!item.moTruyCap"
                @click="chonDoiTuong(item)"
              >
                <img class="switch-card__image" :src="item.image" :alt="item.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">
                    {{ item.name }}
                    <span v-if="!item.moTruyCap" class="sap-ra-mat sap-ra-mat--inline">Sắp ra mắt</span>
                  </span>
                  <span class="switch-card__text">{{ item.description }}</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from 'vue'
import { Compass } from '@element-plus/icons-vue'
import { useDoiTuongAudiences } from '@/composables/useDoiTuongAudiences'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import HuongDiCard from '@/components/guest/chung/HuongDiCard.vue'
import { anhHuongDi, chiPhi, useDsHuongDiThcs } from './HocSinhThcs/thcs'

defineOptions({ name: 'HocSinhThcs' })

defineProps({
  audience: { type: Object, required: true },
})

const { audiences, selectedCode, chonDoiTuong } = useDoiTuongAudiences()
const { dsHuong, dangTai, loi, taiHuongDi } = useDsHuongDiThcs()

onMounted(taiHuongDi)
</script>

<style scoped>
.thcs__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.35;
}

.thcs__lead {
  color: #3a4742;
  line-height: 1.6;
}

.thcs__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.thcs__thu-lai {
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
  font-weight: 700;
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
.thcs__thu-lai:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

@media (max-width: 575.98px) {
  .thcs__title {
    font-size: 1.4rem;
  }

  .thcs__lead {
    font-size: 0.9rem;
  }

  .goi-y-card__nut {
    width: 100%;
    text-align: center;
  }
}
</style>
