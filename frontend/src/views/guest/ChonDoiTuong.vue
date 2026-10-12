<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DoiTuongCard from '@/components/guest/DoiTuongCard.vue'
import TinTucMoi from '@/components/guest/TinTucMoi.vue'
import { DOI_TUONG_KEY, doiTuongList } from '@/data/doiTuong'
import thcsImage from '@/assets/guest/thcs.jpg'
import thptImage from '@/assets/guest/thpt.jpg'
import phuHuynhImage from '@/assets/guest/phu-huynh.jpg'
import nhaTruongImage from '@/assets/guest/nha-truong.jpg'
import sinhVienImage from '@/assets/guest/sinh-vien.jpg'
import thanhNienImage from '@/assets/guest/thanh-nien.jpg'
import nhaTuyenDungImage from '@/assets/guest/nha-tuyen-dung.jpg'

const images = {
  'hoc-sinh-thcs': thcsImage,
  'hoc-sinh-thpt': thptImage,
  'phu-huynh': phuHuynhImage,
  'nha-truong': nhaTruongImage,
  'sinh-vien': sinhVienImage,
  'thanh-nien-ngoai-truong': thanhNienImage,
  'nha-tuyen-dung': nhaTuyenDungImage,
}

const router = useRouter()

const audiences = doiTuongList.map((item) => ({
  ...item,
  image: images[item.code],
}))

const selectedCode = ref(sessionStorage.getItem(DOI_TUONG_KEY) || '')

function chonDoiTuong(audience) {
  selectedCode.value = audience.code
  sessionStorage.setItem(DOI_TUONG_KEY, audience.code)
  router.push({ name: audience.code })
}
</script>

<template>
  <section class="py-5">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="mb-4">
            <h1 class="h2 mb-2">Bạn thuộc đối tượng nào?</h1>
            <p class="text-secondary mb-0">
              Chọn nhóm gần với bạn nhất. Mỗi nhóm có mô tả ngắn để bạn nhận ra mình thuộc đối tượng nào.
            </p>
          </div>

          <div class="row g-3">
            <div v-for="audience in audiences" :key="audience.code" class="col-md-6 col-xl-4">
              <DoiTuongCard
                :image="audience.image"
                :name="audience.name"
                :description="audience.description"
                :selected="selectedCode === audience.code"
                @select="chonDoiTuong(audience)"
              />
            </div>
          </div>
        </div>

        <div class="col-lg-3">
          <TinTucMoi />
        </div>
      </div>
    </div>
  </section>
</template>

