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
            <el-icon :size="22"><component :is="card.icon" /></el-icon>
          </span>
          <h3>{{ card.title }}</h3>
          <p>{{ card.text }}</p>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.support-card {
  padding: 15px;
  border: 1px solid rgba(var(--guest-primary-rgb), 0.28);
  border-radius: var(--guest-radius, 8px);
  background: #f6fbf7;
}

.support-card__title {
  margin: 0 0 12px;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.35;
}

.support-item {
  display: flex;
  flex-direction: column;
  padding: 15px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius, 8px);
  background: #fff;
}

.support-item__icon {
  display: inline-grid;
  place-items: center;
  width: 40px;
  height: 40px;
  margin-bottom: 12px;
  border-radius: var(--guest-radius-sm, 6px);
  background: #e7f5ee;
  color: var(--guest-primary);
}

.support-item h3 {
  margin: 0 0 8px;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.support-item p {
  margin: 0;
  color: #3a4742;
  line-height: 1.5;
}
</style>
