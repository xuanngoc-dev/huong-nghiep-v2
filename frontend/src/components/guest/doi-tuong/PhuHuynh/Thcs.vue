<template>
  <section class="py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="intro-card mb-3">
            <h1 class="ph-thcs__title">Con học THCS: cùng con chọn hướng đi sau lớp 9</h1>
            <p class="ph-thcs__lead mb-0">
              Hết lớp 9 con có nhiều con đường: học THPT, học nghề hay vừa học vừa làm. Hãy cùng con xem từng hướng đi,
              ưu nhược điểm và chi phí, hoặc cùng con trả lời vài câu hỏi ngắn để biết hướng nào hợp với con nhất.
            </p>
          </div>

          <DsHuongDi
            :tien-to="TIEN_TO_THCS"
            tieu-de="Sau khi học xong lớp 9, con có thể đi theo những hướng nào?"
            goi-y-ten="Chưa biết hướng nào hợp với con?"
            goi-y-mo-ta="Cùng con tự đánh giá học lực, sở thích, hoàn cảnh gia đình để nhận gợi ý hướng đi phù hợp."
          />

          <div class="d-flex flex-column gap-3 mt-3">
            <HoTroDinhHuong />
            <CauHoiThuongGap />
          </div>
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="chon-lai-giai-doan" class="h4 mb-3">Chọn lại giai đoạn của con</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-giai-doan">
              <button
                v-for="cap in capHocList"
                :key="cap.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': cap.code === 'thcs', 'is-locked': !cap.moTruyCap }"
                :disabled="!cap.moTruyCap"
                @click="chonGiaiDoan(cap.giaiDoan)"
              >
                <img class="switch-card__image" :src="cap.image" :alt="cap.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">
                    {{ cap.name }}
                    <span v-if="!cap.moTruyCap" class="sap-ra-mat sap-ra-mat--inline">Đang phát triển...</span>
                  </span>
                  <span class="switch-card__text">{{ cap.description }}</span>
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
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import DsHuongDi from '@/components/guest/doi-tuong/HocSinhThcs/DsHuongDi.vue'
import { capHocList } from './capHoc'
import { TIEN_TO_THCS } from './routes'
import { useGiaiDoanCon } from './useGiaiDoanCon'

// Phụ huynh đồng hành cùng con: dùng lại danh sách hướng đi, chi tiết và tự đánh giá của học sinh THCS.
defineOptions({ name: 'PhuHuynhThcs' })

const { chonGiaiDoan } = useGiaiDoanCon()
</script>

<style scoped>
.ph-thcs__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.35;
}

.ph-thcs__lead {
  color: #3a4742;
  line-height: 1.6;
}

@media (max-width: 575.98px) {
  .ph-thcs__title {
    font-size: 1.4rem;
  }

  .ph-thcs__lead {
    font-size: 0.9rem;
  }
}
</style>
