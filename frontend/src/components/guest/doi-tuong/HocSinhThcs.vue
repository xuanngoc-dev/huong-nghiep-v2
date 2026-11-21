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

          <DsHuongDi
            tieu-de="Là học sinh THCS, bạn định hướng gì sau khi học xong lớp 9"
            goi-y-ten="Chưa biết chọn hướng nào?"
            goi-y-mo-ta="Tự đánh giá học lực, sở thích, hoàn cảnh gia đình để nhận gợi ý hướng đi phù hợp."
          />

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
import { useDoiTuongAudiences } from '@/composables/useDoiTuongAudiences'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import DsHuongDi from './HocSinhThcs/DsHuongDi.vue'

defineOptions({ name: 'HocSinhThcs' })

defineProps({
  audience: { type: Object, required: true },
})

const { audiences, selectedCode, chonDoiTuong } = useDoiTuongAudiences()
</script>

<style scoped>
.thcs__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.35;
}

.thcs__lead {
  color: #3a4742;
  line-height: 1.6;
}

@media (max-width: 575.98px) {
  .thcs__title {
    font-size: 1.4rem;
  }

  .thcs__lead {
    font-size: 0.9rem;
  }
}
</style>
