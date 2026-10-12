<script setup>
defineOptions({ name: 'HoTroDinhHuong' })

const cards = [
  {
    title: 'Nhóm hỗ trợ hướng nghiệp',
    text: 'Trao đổi với nhóm bạn cùng hướng và người đồng hành khi bạn cần góp ý về ngành, trường hoặc việc làm.',
    icon: 'UserFilled',
  },
  {
    title: 'Nhận hỗ trợ từ AI',
    text: 'Đặt câu hỏi theo hướng bạn vừa chọn và nhận gợi ý nhanh để làm rõ bước tiếp theo.',
    icon: 'MagicStick',
  },
  {
    title: 'Trao đổi trực tiếp với hệ thống',
    text: 'Nhắn tin với bộ phận hỗ trợ khi câu hỏi cần người phụ trách trả lời.',
    icon: 'ChatDotRound',
  },
]
</script>

<template>
  <section class="support-card" aria-labelledby="ho-tro-dinh-huong-title">
    <h2 id="ho-tro-dinh-huong-title" class="support-card__title">Hỗ trợ</h2>
    <div class="row g-3">
      <div v-for="card in cards" :key="card.title" class="col-md-4">
        <article class="support-item h-100">
          <span class="support-item__icon" aria-hidden="true">
            <el-icon :size="28"><component :is="card.icon" /></el-icon>
          </span>
          <span class="support-item__body">
            <h3>{{ card.title }}</h3>
            <p>{{ card.text }}</p>
          </span>
        </article>
      </div>
    </div>
  </section>
</template>
