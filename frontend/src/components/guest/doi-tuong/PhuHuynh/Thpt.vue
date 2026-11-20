<template>
  <section class="py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="intro-card mb-3">
            <h1 class="h2 mb-2">Con đang học Trung học phổ thông</h1>
            <p class="text-secondary mb-0">
              Mỗi năm học ở THPT có mối quan tâm khác nhau. Chọn lớp của con để xem gợi ý phù hợp với giai đoạn này.
            </p>
          </div>

          <div class="stages-card">
            <h2 class="stages-heading">Con đang học lớp mấy?</h2>
            <div class="row g-3">
              <div v-for="lop in thpt.lop" :key="lop.code" class="col-12 col-md-6">
                <DoiTuongCard
                  :image="lop.image"
                  :name="lop.name"
                  :description="lop.description"
                  :selected="giaiDoanDaChon === lop.giaiDoan"
                  @select="chonGiaiDoan(lop.giaiDoan)"
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
          <div class="paths-card">
            <h2 id="chon-lai-giai-doan" class="h4 mb-3">Chọn lại giai đoạn của con</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-giai-doan">
              <button
                v-for="cap in capHocList"
                :key="cap.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': cap.code === thpt.code }"
                @click="chonGiaiDoan(cap.giaiDoan)"
              >
                <img class="switch-card__image" :src="cap.image" :alt="cap.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">{{ cap.name }}</span>
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
import DoiTuongCard from '@/components/guest/chung/DoiTuongCard.vue'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { capHocList } from './capHoc'
import { useGiaiDoanCon } from './useGiaiDoanCon'

defineOptions({ name: 'PhuHuynhThpt' })

const thpt = capHocList.find((item) => item.code === 'thpt')
const { giaiDoanDaChon, chonGiaiDoan } = useGiaiDoanCon()
</script>
