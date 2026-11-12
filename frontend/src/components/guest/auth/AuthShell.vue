<script setup>
// Khung chung cho màn đăng nhập/đăng ký: desktop có banner ảnh bên trái và form bên phải,
// mobile chỉ hiển thị form. Nội dung form truyền qua slot mặc định.
defineProps({
  image: { type: String, required: true },
  eyebrow: { type: String, default: 'Định hướng nghề' },
  title: { type: String, required: true },
  text: { type: String, default: '' },
  highlights: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="auth-page container-fluid">
    <div class="row min-vh-100">
      <aside class="auth-banner col-lg-6 d-none d-lg-block p-0">
        <div class="auth-banner__inner">
          <img class="auth-banner__img" :src="image" alt="" decoding="async" />
          <RouterLink class="auth-brand-link auth-brand-link--light" :to="{ name: 'home' }">
            <span class="auth-brand-link__mark" aria-hidden="true">ĐH</span>
            Định hướng nghề
          </RouterLink>
          <div class="auth-banner__content">
            <p class="auth-banner__eyebrow">{{ eyebrow }}</p>
            <h2 class="auth-banner__title">{{ title }}</h2>
            <p v-if="text" class="auth-banner__text">{{ text }}</p>
            <ul v-if="highlights.length" class="auth-banner__list">
              <li v-for="item in highlights" :key="item">
                <el-icon aria-hidden="true"><CircleCheckFilled /></el-icon>
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
      </aside>

      <main class="auth-panel col-12 col-lg-6 d-flex flex-column">
        <div class="auth-panel__body">
          <div class="auth-form">
            <RouterLink class="auth-form__logo" :to="{ name: 'home' }" aria-label="Định hướng nghề – về trang chủ">
              ĐH
            </RouterLink>
            <slot />
          </div>
        </div>
        <RouterLink class="auth-panel__home" :to="{ name: 'home' }">
          <el-icon aria-hidden="true"><Back /></el-icon>
          Về trang chủ
        </RouterLink>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Phong cách "kính tối": nền tối có lưới chấm và luồng sáng, thẻ form kính mờ viền phát sáng,
   ô nhập là khung tối gọn, nhãn nằm phía trên. Màu theo tông xanh lá của các trang khách.
   Biến --el-color-primary chỉ áp dụng trong khung auth, không đổi theme của khu quản trị. */
.auth-page {
  /* Màu chủ đạo #3f9643 cho cả banner và khu vực form. Thẻ form là lớp kính xanh đậm hơn nền
     để chữ trắng đạt tương phản ≥ 6:1 (chữ trắng trực tiếp trên #3f9643 chỉ đạt 3.7:1). */
  --auth-primary: #3f9643;
  --auth-primary-strong: #2f7a33;
  --auth-accent: #d9f6dc;
  --auth-bg: #3f9643;
  --auth-line: rgba(255, 255, 255, 0.2);
  --auth-field: rgba(6, 30, 12, 0.35);
  --auth-text: #fff;
  --auth-muted: rgba(255, 255, 255, 0.85);
  --el-color-primary: #3f9643;
  --el-color-primary-light-3: #79b67b;
  --el-color-primary-light-5: #9fcba1;
  --el-color-primary-light-7: #c5e0c7;
  --el-color-primary-light-8: #d9ead9;
  --el-color-primary-light-9: #ecf5ec;
  --el-color-primary-dark-2: #327836;
  background: var(--auth-bg);
}

/* Banner */
.auth-banner__inner {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
  color: #fff;
}

.auth-banner__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.auth-banner__inner::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(63, 150, 67, 0.35) 0%, rgba(63, 150, 67, 0.2) 35%, rgba(24, 74, 30, 0.92) 100%),
    linear-gradient(90deg, rgba(47, 122, 51, 0.45), transparent 70%);
}

.auth-banner .auth-brand-link,
.auth-banner__content {
  position: absolute;
  z-index: 1;
  left: 40px;
}

.auth-banner .auth-brand-link {
  top: 32px;
}

.auth-banner__content {
  right: 40px;
  bottom: 40px;
  max-width: 560px;
}

.auth-banner__eyebrow {
  margin: 0 0 12px;
  color: var(--auth-accent);
  font-size: 0.82rem;
  font-weight: 400;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.auth-banner__title {
  margin: 0;
  color: #fff;
  font-size: clamp(1.6rem, 2.4vw, 2.2rem);
  font-weight: 400;
  line-height: 1.25;
}

.auth-banner__text {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.86);
  line-height: 1.65;
}

.auth-banner__list {
  display: grid;
  gap: 8px;
  margin: 20px 0 0;
  padding: 0;
  list-style: none;
}

.auth-banner__list li {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.92);
}

.auth-banner__list .el-icon {
  color: var(--auth-accent);
}

/* Brand (logo trên banner) */
.auth-brand-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 400;
  text-decoration: none;
}

.auth-brand-link--light {
  color: #fff;
}

.auth-brand-link__mark {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  font-size: 0.78rem;
  backdrop-filter: blur(6px);
}

/* Khu vực form: nền tối, lưới chấm, luồng sáng rọi từ trên xuống. */
.auth-panel {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  padding: 20px;
  background:
    radial-gradient(ellipse 60% 45% at 50% -5%, rgba(255, 255, 255, 0.22), transparent 70%),
    radial-gradient(rgba(255, 255, 255, 0.09) 1px, transparent 1.5px) 0 0 / 24px 24px,
    linear-gradient(180deg, var(--auth-primary) 0%, #37883b 55%, var(--auth-primary-strong) 100%);
  color: var(--auth-text);
}

.auth-panel__body {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  padding-block: 32px;
}

/* Thẻ form kính tối */
.auth-form {
  position: relative;
  width: 100%;
  max-width: 440px;
  padding: 36px 28px 28px;
  border: 1px solid var(--auth-line);
  border-radius: 24px;
  background:
    radial-gradient(ellipse 70% 40% at 50% 0%, rgba(255, 255, 255, 0.08), transparent 70%),
    linear-gradient(180deg, rgba(20, 70, 28, 0.5), rgba(12, 48, 18, 0.62));
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    0 30px 80px rgba(10, 40, 16, 0.4);
  backdrop-filter: blur(18px);
  text-align: center;
  animation: auth-rise 0.6s cubic-bezier(0.2, 0.7, 0.2, 1) both;
}

/* Điểm sáng trên viền trên của thẻ */
.auth-form::before {
  content: '';
  position: absolute;
  top: -1px;
  left: 50%;
  width: 45%;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, transparent, var(--auth-accent), transparent);
  box-shadow: 0 0 18px 2px rgba(255, 255, 255, 0.45);
  transform: translateX(-50%);
}

@keyframes auth-rise {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
}

.auth-form__logo {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  margin: 0 auto 20px;
  border: 1px solid var(--auth-line);
  border-radius: 16px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0.08));
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.25),
    0 10px 24px rgba(10, 40, 16, 0.3);
  color: #fff;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-decoration: none;
}

.auth-form__logo:focus-visible {
  outline: 2px solid var(--auth-accent);
  outline-offset: 3px;
}

.auth-panel__home {
  display: inline-flex;
  align-items: center;
  align-self: center;
  gap: 6px;
  color: var(--auth-muted);
  font-size: 0.9rem;
  text-decoration: none;
}

.auth-panel__home:hover {
  color: #fff;
}

/* Nội dung trong slot (thuộc Login/Register) */
.auth-form :deep(.auth-brand) {
  margin-bottom: 28px;
}

.auth-form :deep(.auth-brand h1) {
  margin: 0 0 6px;
  background: linear-gradient(180deg, #fff, #dff3e1);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: 1.9rem;
  font-weight: 400;
}

.auth-form :deep(.auth-brand p) {
  margin: 0;
  color: var(--auth-muted);
}

/* Ô nhập: nhãn nằm phía trên, chỉ ô nhập là khung tối gọn 44px. */
.auth-form :deep(.el-form-item) {
  /* Chừa chỗ cho dòng báo lỗi (đặt tuyệt đối dưới ô) để không dính vào nhãn của trường kế tiếp. */
  margin-bottom: 24px;
  text-align: left;
}

.auth-form :deep(.el-form-item__label) {
  height: auto;
  margin: 0 0 6px;
  padding: 0;
  color: var(--auth-muted);
  font-size: 0.85rem;
  font-weight: 500;
  line-height: 1.4;
}

.auth-form :deep(.el-form-item__label::before) {
  color: #ffd0d0 !important;
}

.auth-form :deep(.el-input__wrapper) {
  min-height: 44px;
  padding: 0 14px;
  border-radius: 12px;
  background: var(--auth-field);
  box-shadow: 0 0 0 1px var(--auth-line) inset;
  transition:
    box-shadow 0.2s ease,
    background 0.2s ease;
}

.auth-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.35) inset;
}

.auth-form :deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.75) inset,
    0 0 0 4px rgba(255, 255, 255, 0.16);
}

.auth-form :deep(.el-form-item.is-error .el-input__wrapper) {
  box-shadow:
    0 0 0 1px #ffb4b4 inset,
    0 0 0 3px rgba(255, 120, 120, 0.22);
}

.auth-form :deep(.el-input__inner) {
  color: #fff;
  font-size: 0.95rem;
}

.auth-form :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.55);
}

/* Giữ nền tối khi trình duyệt tự điền */
.auth-form :deep(.el-input__inner:-webkit-autofill) {
  -webkit-text-fill-color: #fff;
  transition: background-color 9999s ease-out;
}

.auth-form :deep(.el-input__prefix),
.auth-form :deep(.el-input__suffix),
.auth-form :deep(.el-input__icon) {
  color: rgba(255, 255, 255, 0.6);
}

.auth-form :deep(.el-form-item__error) {
  padding-top: 4px;
  color: #ffd0d0;
  font-weight: 500;
}

/* Nút chính: sáng trên nền tối, chữ tối, có mũi tên. */
.auth-form :deep(.submit-btn) {
  width: 100%;
  height: 50px;
  margin-top: 8px;
  border: 0;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 12px 28px rgba(10, 40, 16, 0.3);
  color: var(--auth-primary-strong);
  font-size: 1rem;
  font-weight: 400;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
}

.auth-form :deep(.submit-btn:hover),
.auth-form :deep(.submit-btn:focus-visible) {
  background: #f1faf2;
  color: var(--auth-primary-strong);
  transform: translateY(-1px);
  box-shadow: 0 16px 34px rgba(10, 40, 16, 0.38);
}

.auth-form :deep(.submit-btn .el-icon) {
  margin-left: 8px;
}

.auth-form :deep(.auth-footer) {
  margin: 24px 0 0;
  color: var(--auth-muted);
}

.auth-form :deep(.auth-footer a) {
  margin-left: 4px;
  color: #fff;
  font-weight: 400;
  text-decoration: underline;
  text-underline-offset: 3px;
}

@media (min-width: 992px) {
  .auth-panel {
    padding: 32px 40px;
  }

  .auth-form {
    padding: 40px 36px 32px;
  }
}

@media (max-width: 575.98px) {
  .auth-form {
    padding: 32px 20px 24px;
    border-radius: 20px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .auth-form,
  .auth-form :deep(.submit-btn) {
    animation: none;
    transition: none;
  }
}
</style>
