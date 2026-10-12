<script setup>
import { ref } from 'vue'
import { useDoiTuongAudiences } from '@/composables/useDoiTuongAudiences'
import DinhHuongTuongLai from '@/components/guest/chung/DinhHuongTuongLai.vue'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import diLamImage from '@/assets/guest/nha-tuyen-dung.jpg'
import duHocNgheImage from '@/assets/guest/nha-truong.jpg'
import duHocImage from '@/assets/guest/sinh-vien.jpg'
import thiDaiHocImage from '@/assets/guest/thpt.jpg'
import khoiNghiepImage from '@/assets/guest/thanh-nien.jpg'
import xuatKhauImage from '@/assets/guest/thcs.jpg'

defineOptions({ name: 'HocSinhThpt' })

defineProps({
  audience: { type: Object, required: true },
})

const DINH_HUONG_KEY = 'dinh_huong_thpt'

const directions = [
  {
    code: 'di-lam',
    name: 'Đi làm ngay sau khi tốt nghiệp',
    description: 'Bắt đầu làm việc sớm và tích lũy kinh nghiệm thay vì học tiếp.',
    image: diLamImage,
  },
  {
    code: 'du-hoc-nghe',
    name: 'Du học nghề',
    description: 'Học nghề ở nước ngoài, vừa đào tạo vừa thực hành.',
    image: duHocNgheImage,
  },
  {
    code: 'du-hoc',
    name: 'Du học',
    description: 'Học đại học hoặc cao đẳng tại nước ngoài.',
    image: duHocImage,
  },
  {
    code: 'thi-dai-hoc',
    name: 'Thi Đại học & cao đẳng',
    description: 'Ôn thi và chọn ngành, trường trong nước.',
    image: thiDaiHocImage,
  },
  {
    code: 'khoi-nghiep',
    name: 'Khởi nghiệp',
    description: 'Tự xây dựng ý tưởng và bắt đầu công việc của riêng bạn.',
    image: khoiNghiepImage,
  },
  {
    code: 'xuat-khau-lao-dong',
    name: 'Xuất khẩu lao động',
    description: 'Đi làm việc có thời hạn ở nước ngoài theo chương trình lao động.',
    image: xuatKhauImage,
  },
]

const selectedDirection = ref(sessionStorage.getItem(DINH_HUONG_KEY) || '')
const { audiences, selectedCode, chonDoiTuong } = useDoiTuongAudiences()

function chonDinhHuong(direction) {
  selectedDirection.value = direction.code
  sessionStorage.setItem(DINH_HUONG_KEY, direction.code)
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

<style scoped>
.intro-card,
.directions-card,
.audiences-card {
  padding: 15px;
  border: 1px solid rgba(var(--guest-primary-rgb), 0.28);
  border-radius: var(--guest-radius, 8px);
  background: #f6fbf7;
}

@media (min-width: 992px) {
  .audiences-card {
    position: sticky;
    top: 84px;
    max-height: calc(100vh - 100px);
    overflow-y: auto;
  }
}

.directions-heading {
  margin: 0 0 16px;
  font-size: 1.35rem;
  line-height: 1.35;
}

.stage-card {
  display: flex;
  flex-direction: column;
  padding: 16px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius, 8px);
  background: #fff;
  transition: box-shadow 0.3s ease;
}

.stage-card:hover {
  box-shadow: 0 16px 32px rgba(31, 122, 77, 0.14);
}

.stage-card.is-selected {
  border-color: var(--guest-primary);
  box-shadow: 0 0 0 1px var(--guest-primary);
}

.stage-card.is-selected:hover {
  box-shadow:
    0 0 0 1px var(--guest-primary),
    0 16px 32px rgba(31, 122, 77, 0.14);
}

.stage-card__media {
  position: relative;
  overflow: hidden;
  border-radius: var(--guest-radius-sm, 6px);
}

.stage-card__image {
  display: block;
  width: 100%;
  height: 190px;
  object-fit: cover;
}

.stage-card__title {
  margin: 16px 0 8px;
  color: var(--guest-primary);
  font-size: 1.35rem;
  line-height: 1.35;
}

.stage-card__text {
  flex: 1;
  margin: 0;
  color: #3a4742;
  font-size: 1rem;
  line-height: 1.5;
}

.stage-card__button {
  position: absolute;
  right: 12px;
  bottom: 12px;
  border: 0;
  border-radius: 999px;
  padding: 10px 22px;
  background: var(--guest-primary);
  color: #fff;
  font-weight: 700;
  line-height: 1.2;
  cursor: pointer;
}

.stage-card__button:hover {
  background: var(--guest-primary-hover);
}

.switch-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  padding: 10px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius, 8px);
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition: box-shadow 0.3s ease;
}

.switch-card:hover {
  box-shadow: 0 16px 32px rgba(31, 122, 77, 0.14);
}

.switch-card.is-selected {
  border-color: var(--guest-primary);
  box-shadow: 0 0 0 1px var(--guest-primary);
}

.switch-card__image {
  flex: 0 0 72px;
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: var(--guest-radius-sm, 6px);
}

.switch-card__body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.switch-card__name {
  color: var(--guest-primary);
  font-weight: 700;
  line-height: 1.35;
}

.switch-card__text {
  color: #8d97a2;
  font-size: 0.85rem;
  line-height: 1.45;
}
</style>
