<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDoiTuongAudiences } from '@/composables/useDoiTuongAudiences'
import { routeNameDinhHuongThpt } from '@/components/guest/doi-tuong/HocSinhThpt/routes'
import { DINH_HUONG_THPT_KEY, dinhHuongThptList } from '@/components/guest/doi-tuong/HocSinhThpt/dinhHuong'
import DinhHuongTuongLai from '@/components/guest/chung/DinhHuongTuongLai.vue'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'

defineOptions({ name: 'HocSinhThpt' })

defineProps({
  audience: { type: Object, required: true },
})

const directions = dinhHuongThptList

const selectedDirection = ref(sessionStorage.getItem(DINH_HUONG_THPT_KEY) || '')
const { audiences, selectedCode, chonDoiTuong } = useDoiTuongAudiences()
const router = useRouter()

function chonDinhHuong(direction) {
  selectedDirection.value = direction.code
  sessionStorage.setItem(DINH_HUONG_THPT_KEY, direction.code)
  const name = routeNameDinhHuongThpt(direction.code)
  if (name) router.push({ name })
}
</script>

<template>
  <section class="py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="intro-card mb-3">
            <h2 class="h2 mb-2">Bạn thuộc nhóm đối tượng nào?</h2>
            <p class="text-secondary mb-0">
              Hãy chọn nhóm phù hợp với bạn để chúng tôi đưa ra lộ trình phù hợp nhất.
            </p>
          </div>

          <div class="directions-card">
            <h2 class="directions-heading">Là học sinh THPT, bạn định hướng làm gì sau khi tốt nghiệp</h2>
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
