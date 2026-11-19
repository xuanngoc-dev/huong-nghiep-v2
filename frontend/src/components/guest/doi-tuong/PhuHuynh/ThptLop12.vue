<template>
  <section class="py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="intro-card mb-3">
            <h1 class="h2 mb-2">Con đang học lớp 12</h1>
            <p class="text-secondary mb-0">
              Giai đoạn nước rút: cùng con chọn hướng đi sau tốt nghiệp, làm bài trắc nghiệm và tìm ngành, trường phù hợp.
            </p>
          </div>

          <div class="directions-card">
            <h2 class="directions-heading">Sau khi tốt nghiệp THPT, con định hướng làm gì?</h2>
            <div class="row g-3">
              <div v-for="direction in directions" :key="direction.code" class="col-md-6 col-xl-4">
                <article class="stage-card h-100" :class="{ 'is-selected': selectedDirection === direction.code }">
                  <div class="stage-card__media">
                    <img class="stage-card__image" :src="direction.image" :alt="direction.name" />
                    <button type="button" class="stage-card__button" @click="chonDinhHuong(direction)">
                      Bắt đầu
                    </button>
                  </div>
                  <h3 class="stage-card__title">{{ direction.name }}</h3>
                  <p class="stage-card__text">{{ direction.description }}</p>
                </article>
              </div>
            </div>
          </div>

          <div class="d-flex flex-column gap-3 mt-3">
            <DinhHuongTuongLai />
            <HoTroDinhHuong />
            <CauHoiThuongGap />
          </div>
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="chon-lai-giai-doan" class="h4 mb-3">Chọn lại giai đoạn của con</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-giai-doan">
              <button
                v-for="item in giaiDoanList"
                :key="item.giaiDoan"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': item.giaiDoan === 'thpt-12' }"
                @click="chonGiaiDoan(item.giaiDoan)"
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { routeNameDinhHuongThpt } from '@/components/guest/doi-tuong/HocSinhThpt/routes'
import { DINH_HUONG_THPT_KEY, dinhHuongThptList } from '@/components/guest/doi-tuong/HocSinhThpt/dinhHuong'
import DinhHuongTuongLai from '@/components/guest/chung/DinhHuongTuongLai.vue'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { capHocList } from './capHoc'
import { TIEN_TO_LOP_12 } from './routes'
import { useGiaiDoanCon } from './useGiaiDoanCon'

defineOptions({ name: 'PhuHuynhThptLop12' })

const directions = dinhHuongThptList

// Các lớp của THPT tách thành từng giai đoạn riêng để chọn lại nhanh.
const giaiDoanList = capHocList.flatMap((cap) => cap.lop || [cap])

const selectedDirection = ref(sessionStorage.getItem(DINH_HUONG_THPT_KEY) || '')
const router = useRouter()
const { chonGiaiDoan } = useGiaiDoanCon()

function chonDinhHuong(direction) {
  selectedDirection.value = direction.code
  sessionStorage.setItem(DINH_HUONG_THPT_KEY, direction.code)
  const name = routeNameDinhHuongThpt(direction.code, TIEN_TO_LOP_12)
  if (name) router.push({ name })
}
</script>
