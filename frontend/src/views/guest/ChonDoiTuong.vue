<script setup>
import DoiTuongCard from '@/components/guest/chung/DoiTuongCard.vue'
import TinTucMoi from '@/components/guest/chung/TinTucMoi.vue'
import { useDoiTuongAudiences } from '@/composables/useDoiTuongAudiences'

const { audiences, selectedCode, chonDoiTuong } = useDoiTuongAudiences()
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
                :ma="audience.ma"
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
