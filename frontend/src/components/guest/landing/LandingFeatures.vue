<template>
  <section id="tinh-nang" class="landing__section" aria-labelledby="features-title">
    <div class="container-fluid">
      <div class="landing__head row g-lp align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Tính năng cốt lõi</p>
          <h2 id="features-title" class="landing__title">Không có định hướng tốt nhất, chỉ có định hướng phù hợp nhất</h2>
        </div>
      </div>

      <!-- Cùng kiểu thẻ với trang chọn đối tượng (HuongDiCard): ảnh trái, nội dung phải. -->
      <div class="row g-lp" data-stagger>
        <div v-for="item in features" :key="item.id" class="col-12 col-md-6 col-xl-4">
          <!-- moChat: mở khung chat nổi thay cho trang /demo-chat (đã tạm bỏ). -->
          <HuongDiCard
            :image="item.image"
            :title="item.title"
            :description="item.description"
            :to="item.moChat ? null : item.to"
            cta="Tìm hiểu thêm"
            @chon="item.moChat && chat.moKhungChat()"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { features } from '@/data/landing'
import { useChatStore } from '@/stores/chat'
import HuongDiCard from '@/components/guest/chung/HuongDiCard.vue'

const chat = useChatStore()
</script>
