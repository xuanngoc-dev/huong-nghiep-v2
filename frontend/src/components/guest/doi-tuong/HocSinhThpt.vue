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
              <div v-for="direction in directions" :key="direction.code" class="col-12 col-xl-6">
                <HuongDiCard
                  :image="direction.image"
                  :title="direction.name"
                  :description="direction.moTaChiTiet || direction.description"
                  cta="Bắt đầu"
                  :selected="selectedDirection === direction.code"
                  :locked="!direction.moTruyCap"
                  @chon="chonDinhHuong(direction)"
                />
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDoiTuongAudiences } from '@/composables/useDoiTuongAudiences'
import { routeNameDinhHuongThpt } from '@/components/guest/doi-tuong/HocSinhThpt/routes'
import { DINH_HUONG_THPT_KEY, dinhHuongThptList } from '@/components/guest/doi-tuong/HocSinhThpt/dinhHuong'
import DinhHuongTuongLai from '@/components/guest/chung/DinhHuongTuongLai.vue'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import HuongDiCard from '@/components/guest/chung/HuongDiCard.vue'

defineOptions({ name: 'HocSinhThpt' })

defineProps({
  audience: { type: Object, required: true },
})

const directions = dinhHuongThptList

const selectedDirection = ref(sessionStorage.getItem(DINH_HUONG_THPT_KEY) || '')
const { audiences, selectedCode, chonDoiTuong } = useDoiTuongAudiences()
const router = useRouter()

function chonDinhHuong(direction) {
  if (!direction.moTruyCap) return
  selectedDirection.value = direction.code
  sessionStorage.setItem(DINH_HUONG_THPT_KEY, direction.code)
  const name = routeNameDinhHuongThpt(direction.code)
  if (name) router.push({ name })
}
</script>
