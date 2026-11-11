<template>
  <section class="landing__section" aria-labelledby="final-cta-title">
    <div class="container-fluid">
      <div class="landing-final" data-reveal>
        <h2 id="final-cta-title" class="landing__title">Tương lai bắt đầu từ sự lựa chọn hôm nay</h2>
        <p>
          Khám phá tiềm năng, lựa chọn con đường phù hợp và từng bước hiện thực hóa mục tiêu nghề
          nghiệp của bạn.
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
