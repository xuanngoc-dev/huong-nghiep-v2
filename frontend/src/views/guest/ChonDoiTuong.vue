<script setup>
import { ref } from 'vue'
import thcsImage from '@/assets/guest/thcs.jpg'
import thptImage from '@/assets/guest/thpt.jpg'
import phuHuynhImage from '@/assets/guest/phu-huynh.jpg'
import nhaTruongImage from '@/assets/guest/nha-truong.jpg'
import sinhVienImage from '@/assets/guest/sinh-vien.jpg'
import thanhNienImage from '@/assets/guest/thanh-nien.jpg'
import nhaTuyenDungImage from '@/assets/guest/nha-tuyen-dung.jpg'

const DOI_TUONG_KEY = 'doi_tuong'

const audiences = [
  {
    code: 'hoc-sinh-thcs',
    name: 'Học sinh THCS',
    description: 'Bạn đang học cấp trung học cơ sở và muốn hiểu sở thích, năng lực trước khi chọn hướng lên THPT.',
    image: thcsImage,
  },
  {
    code: 'hoc-sinh-thpt',
    name: 'Học sinh THPT định hướng học Đại học, Cao đẳng',
    description: 'Lựa chọn ngành học phù hợp với năng lực và đam mê.',
    image: thptImage,
  },
  {
    code: 'phu-huynh',
    name: 'Phụ huynh',
    description: 'Bạn đang cùng con tìm hiểu năng lực và cân nhắc ngành học, trường học phù hợp.',
    image: phuHuynhImage,
  },
  {
    code: 'nha-truong',
    name: 'Nhà trường',
    description: 'Bạn là giáo viên hoặc cán bộ nhà trường, muốn hỗ trợ học sinh trong hoạt động hướng nghiệp.',
    image: nhaTruongImage,
  },
  {
    code: 'sinh-vien',
    name: 'Sinh viên',
    description: 'Bạn đang học cao đẳng hoặc đại học và muốn đối chiếu ngành đang học hoặc tìm hướng phù hợp hơn.',
    image: sinhVienImage,
  },
  {
    code: 'thanh-nien-ngoai-truong',
    name: 'Thanh niên ngoài trường',
    description: 'Bạn hiện không đi học và đang tìm hướng nghề để học tiếp hoặc bắt đầu đi làm.',
    image: thanhNienImage,
  },
  {
    code: 'nha-tuyen-dung',
    name: 'Nhà tuyển dụng',
    description: 'Bạn đại diện đơn vị tuyển dụng và muốn tìm hiểu định hướng, nhóm tính cách của ứng viên.',
    image: nhaTuyenDungImage,
  },
]

const selectedCode = ref(sessionStorage.getItem(DOI_TUONG_KEY) || '')

function chonDoiTuong(audience) {
  selectedCode.value = audience.code
  sessionStorage.setItem(DOI_TUONG_KEY, audience.code)
}
</script>

<template>
  <section class="py-5">
    <div class="container">
      <div class="mb-4 col-lg-8">
        <h1 class="h2 mb-2">Bạn thuộc đối tượng nào?</h1>
        <p class="text-secondary mb-0">
          Chọn nhóm gần với bạn nhất. Mỗi nhóm có mô tả ngắn để bạn nhận ra mình thuộc đối tượng nào.
        </p>
      </div>

      <div class="row g-4">
        <div v-for="audience in audiences" :key="audience.code" class="col-md-6 col-xl-4">
          <article
            class="audience-card h-100"
            :class="{ 'is-selected': selectedCode === audience.code }"
          >
            <img class="audience-card__image" :src="audience.image" :alt="audience.name" />
            <h2 class="audience-card__title">{{ audience.name }}</h2>
            <p class="audience-card__text">{{ audience.description }}</p>
            <div class="audience-card__action">
              <button type="button" class="audience-card__button" @click="chonDoiTuong(audience)">
                Bắt đầu
              </button>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.audience-card {
  display: flex;
  flex-direction: column;
  padding: 16px;
  border: 1px solid #d7eadf;
  border-radius: 22px;
  background: #fff;
}

.audience-card.is-selected {
  border-color: #1f7a4d;
  box-shadow: 0 0 0 1px #1f7a4d;
}

.audience-card__image {
  width: 100%;
  height: 190px;
  object-fit: cover;
  border-radius: 16px;
}

.audience-card__title {
  margin: 18px 0 8px;
  color: #1f7a4d;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.35;
}

.audience-card__text {
  flex: 1;
  margin: 0;
  color: #8d97a2;
  font-size: 1rem;
  line-height: 1.5;
}

.audience-card__action {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.audience-card__button {
  border: 0;
  border-radius: 999px;
  padding: 10px 22px;
  background: #3caf6a;
  color: #fff;
  font-weight: 700;
  line-height: 1.2;
}

.audience-card__button:hover {
  background: #349a5d;
}
</style>
