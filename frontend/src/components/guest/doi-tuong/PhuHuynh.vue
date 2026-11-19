<template>
  <section class="phu-huynh py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="ph-banner mb-3">
            <img class="ph-banner__image" :src="phuHuynhImage" alt="" aria-hidden="true" />
            <div class="ph-banner__body">
              <p class="ph-banner__kicker">Dành cho phụ huynh</p>
              <h1 class="ph-banner__title">Đồng hành cùng con trên hành trình chọn nghề</h1>
              <p class="ph-banner__text">
                Hiểu con hơn, lắng nghe nhiều hơn và cùng con đưa ra lựa chọn ngành học, trường học phù hợp
                với năng lực và đam mê.
              </p>
            </div>
          </div>

          <div class="stages-card">
            <h2 class="stages-heading">Con của bạn đang học ở cấp nào?</h2>
            <div class="row g-3">
              <div v-for="cap in capHocList" :key="cap.code" class="col-md-6 col-xl-4">
                <article class="stage-card h-100" :class="{ 'is-selected': laCapDangChon(cap) }">
                  <div class="stage-card__media">
                    <img class="stage-card__image" :src="cap.image" :alt="cap.name" />
                    <span class="ph-tag">{{ cap.nhan }}</span>
                    <button type="button" class="stage-card__button" @click="chonGiaiDoan(cap.giaiDoan)">Bắt đầu</button>
                  </div>
                  <h3 class="stage-card__title">{{ cap.name }}</h3>
                  <p class="stage-card__text">{{ cap.description }}</p>
                </article>
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
                :class="{ 'is-selected': selectedCode === item.code }"
                @click="chonDoiTuong(item)"
              >
                <img class="switch-card__image" :src="item.image" :alt="item.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">{{ item.name }}</span>
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
import { capHocList } from '@/components/guest/doi-tuong/PhuHuynh/capHoc'
import { useGiaiDoanCon } from '@/components/guest/doi-tuong/PhuHuynh/useGiaiDoanCon'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import phuHuynhImage from '@/assets/guest/phu-huynh.jpg'

defineOptions({ name: 'PhuHuynh' })

defineProps({
  audience: { type: Object, required: true },
})

const { audiences, selectedCode, chonDoiTuong } = useDoiTuongAudiences()
const { chonGiaiDoan, laCapDangChon } = useGiaiDoanCon()
</script>

<style scoped>
.ph-banner {
  position: relative;
  display: flex;
  align-items: center;
  min-height: 260px;
  overflow: hidden;
  border-radius: var(--guest-radius);
  color: #fff;
}

.ph-banner__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ph-banner::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(20, 85, 54, 0.92) 0%, rgba(31, 122, 77, 0.78) 45%, rgba(31, 122, 77, 0.15) 100%);
}

.ph-banner__body {
  position: relative;
  z-index: 1;
  max-width: 560px;
  padding: 32px;
}

.ph-banner__kicker {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.9;
}

.ph-banner__title {
  margin: 0 0 12px;
  color: #fff;
  font-size: clamp(26px, 3.4vw, 40px);
  font-weight: 700;
  line-height: 1.2;
}

.ph-banner__text {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.55;
  opacity: 0.95;
}

.ph-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 10px;
  border-radius: var(--guest-radius-sm);
  background: rgba(255, 255, 255, 0.92);
  color: var(--guest-primary);
  font-size: 0.85rem;
  font-weight: 600;
}

@media (max-width: 767px) {
  .ph-banner {
    min-height: 220px;
  }

  .ph-banner::after {
    background: linear-gradient(180deg, rgba(20, 85, 54, 0.55) 0%, rgba(20, 85, 54, 0.9) 100%);
  }

  .ph-banner__body {
    padding: 24px 16px;
  }
}
</style>
