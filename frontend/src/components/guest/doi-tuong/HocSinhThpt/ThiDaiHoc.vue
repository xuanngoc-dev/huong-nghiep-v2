<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import chuaCoImage from '@/assets/guest/thanh-nien.jpg'
import daCoImage from '@/assets/guest/sinh-vien.jpg'
import phanVanImage from '@/assets/guest/phu-huynh.jpg'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { DINH_HUONG_THPT_KEY, dinhHuongThptList } from './dinhHuong'
import { routeNameDinhHuongThpt } from './routes'

defineOptions({ name: 'ThptThiDaiHoc' })

const GIAI_DOAN_KEY = 'giai_doan_thi_dai_hoc'

const stages = [
  {
    code: 'chua-co',
    name: 'Chưa có ngành nghề phù hợp',
    description: 'Bạn chưa xác định ngành muốn theo và cần gợi ý từ sở thích, năng lực.',
    image: chuaCoImage,
  },
  {
    code: 'da-co',
    name: 'Đã có ngành nghề mong muốn',
    description: 'Bạn đã chọn ngành và muốn đối chiếu trường, tổ hợp môn và cách xét tuyển.',
    image: daCoImage,
  },
  {
    code: 'phan-van',
    name: 'Đang phân vân giữa vài ngành nghề',
    description: 'Bạn đang cân nhắc một vài ngành và cần so sánh để chốt hướng.',
    image: phanVanImage,
  },
]

const selectedStage = ref(sessionStorage.getItem(GIAI_DOAN_KEY) || '')
const route = useRoute()
const router = useRouter()
const currentDirection = computed(() => route.meta.dinhHuong || '')

function chonGiaiDoan(stage) {
  selectedStage.value = stage.code
  sessionStorage.setItem(GIAI_DOAN_KEY, stage.code)
}

function chonHuong(direction) {
  sessionStorage.setItem(DINH_HUONG_THPT_KEY, direction.code)
  const name = routeNameDinhHuongThpt(direction.code)
  if (name && name !== route.name) router.push({ name })
}
</script>

<template>
  <section class="py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="intro-card mb-3">
            <h2 class="h2 mb-2">Bạn đang ở giai đoạn nào trong hành trình?</h2>
            <p class="text-secondary mb-0">
              Không có ngành nghề tốt nhất, chỉ có ngành nghề phù hợp nhất
            </p>
          </div>
          <div class="stages-card">
            <h2 class="stages-heading">Bạn đang ở giai đoạn nào trong hành trình?</h2>
            <div class="row g-3">
              <div v-for="stage in stages" :key="stage.code" class="col-md-6 col-xl-4">
                <article class="stage-card h-100" :class="{ 'is-selected': selectedStage === stage.code }">
                  <div class="stage-card__media">
                    <img class="stage-card__image" :src="stage.image" :alt="stage.name" />
                    <button type="button" class="stage-card__button" @click="chonGiaiDoan(stage)">
                      Bắt đầu
                    </button>
                  </div>
                  <h3 class="stage-card__title">{{ stage.name }}</h3>
                  <p class="stage-card__text">{{ stage.description }}</p>
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
          <div class="paths-card">
            <h2 id="chon-huong-di" class="h4 mb-3">Một số hướng đi khác cho bạn.</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-huong-di">
              <button
                v-for="item in dinhHuongThptList"
                :key="item.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': currentDirection === item.code }"
                @click="chonHuong(item)"
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
