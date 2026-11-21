<template>
  <section class="landing__section" aria-labelledby="final-cta-title">
    <div class="container-fluid">
      <div class="landing-final" data-reveal>
        <h2 id="final-cta-title" class="landing__title">Bắt đầu bằng việc chọn bạn là ai</h2>
        <p>
          Mỗi nhóm có hướng đi, trắc nghiệm và tra cứu riêng.
        </p>
        <div class="landing-final__actions">
          <RouterLink class="landing__btn landing__btn--primary" :to="{ name: 'register' }">
            Bắt đầu miễn phí
          </RouterLink>
          <RouterLink class="landing__btn landing__btn--ghost" :to="{ name: 'chon-doi-tuong' }">
            Khám phá ngay
          </RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>
