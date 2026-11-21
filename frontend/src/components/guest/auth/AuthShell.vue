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

<style scoped>
/* Banner ảnh bên trái (desktop), form trên nền sáng bên phải. Màu chủ đạo xanh #3f9643; nút và chữ
   xanh trên nền sáng dùng #2f7a33 để đạt tương phản 4.5:1.
   Biến --el-color-primary chỉ áp dụng trong khung auth, không đổi theme của khu quản trị. */
.auth-page {
  --auth-primary: #3f9643;
  --auth-primary-strong: #2f7a33;
  --auth-primary-hover: #276a2b;
  --auth-bg: #f8fbf8;
  --auth-line: rgba(15, 23, 42, 0.08);
  --auth-text: #0f172a;
  --auth-muted: #475569;
  --el-color-primary: #2f7a33;
  --el-color-primary-light-3: #6da270;
  --el-color-primary-light-5: #97bd99;
  --el-color-primary-light-7: #c1d7c2;
  --el-color-primary-light-8: #d5e4d6;
  --el-color-primary-light-9: #eaf2eb;
  --el-color-primary-dark-2: #276a2b;
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

/* Lớp tối phía dưới để chữ trắng đọc được trên ảnh. */
.auth-banner__inner::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(11, 33, 18, 0.2) 0%, rgba(11, 33, 18, 0.15) 40%, rgba(11, 33, 18, 0.88) 100%);
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
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.9375rem;
  font-weight: 500;
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
  color: #b9e3bb;
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
  border-radius: 8px;
  background: var(--auth-primary-strong);
  color: #fff;
  font-size: 0.78rem;
}

/* Khu vực form */
.auth-panel {
  padding: 20px;
  background: var(--auth-bg);
  color: var(--auth-text);
}

.auth-panel__body {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  padding-block: 32px;
}

.auth-form {
  width: 100%;
  /* Đủ rộng cho 2 ô nhập trên một hàng (form-grid). */
  max-width: 640px;
  padding: 32px 28px 28px;
  border: 1px solid var(--auth-line);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  text-align: center;
  animation: auth-rise 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes auth-rise {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
}

.auth-form__logo {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin: 0 auto 20px;
  border-radius: 12px;
  background: var(--auth-primary-strong);
  color: #fff;
  font-size: 0.95rem;
  font-weight: 500;
  text-decoration: none;
}

.auth-form__logo:focus-visible {
  outline: 2px solid var(--auth-primary-strong);
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
  color: var(--auth-primary-strong);
}

/* Nội dung trong slot (thuộc Login/Register) */
.auth-form :deep(.auth-brand) {
  margin-bottom: 28px;
}

.auth-form :deep(.auth-brand h1) {
  margin: 0 0 6px;
  color: var(--auth-text);
  font-size: 1.75rem;
  font-weight: 400;
}

.auth-form :deep(.auth-brand p) {
  margin: 0;
  color: var(--auth-muted);
}

/* Ô nhập: nhãn nằm phía trên, ô nhập cao 44px. */
.auth-form :deep(.el-form-item) {
  /* Chừa chỗ cho dòng báo lỗi (đặt tuyệt đối dưới ô) để không dính vào nhãn của trường kế tiếp. */
  margin-bottom: 24px;
  text-align: left;
}

.auth-form :deep(.el-form-item__label) {
  height: auto;
  margin: 0 0 6px;
  padding: 0;
  color: var(--auth-text);
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.4;
}

.auth-form :deep(.el-input__wrapper),
.auth-form :deep(.el-select__wrapper) {
  min-height: 44px;
  padding: 0 12px;
  border-radius: 8px;
}

.auth-form :deep(.el-form-item__error) {
  padding-top: 4px;
}

/* Ô đồng ý chính sách & điều khoản: nhãn dài được xuống dòng, link màu chủ đạo. */
.auth-form :deep(.auth-dong-y) {
  margin-bottom: 20px;
}

.auth-form :deep(.auth-dong-y .el-checkbox) {
  align-items: flex-start;
  height: auto;
  white-space: normal;
}

.auth-form :deep(.auth-dong-y .el-checkbox__input) {
  margin-top: 3px;
}

.auth-form :deep(.auth-dong-y .el-checkbox__label) {
  color: var(--auth-muted);
  font-size: 0.9rem;
  line-height: 1.5;
}

.auth-form :deep(.auth-dong-y a) {
  color: var(--auth-primary-strong);
  font-weight: 500;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.auth-form :deep(.submit-btn) {
  width: 100%;
  height: 48px;
  margin-top: 8px;
  border: 0;
  border-radius: 8px;
  background: var(--auth-primary-strong);
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
  transition: background 0.15s ease;
}

.auth-form :deep(.submit-btn:hover),
.auth-form :deep(.submit-btn:focus-visible) {
  background: var(--auth-primary-hover);
  color: #fff;
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
  color: var(--auth-primary-strong);
  font-weight: 500;
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
    padding: 28px 20px 24px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .auth-form {
    animation: none;
  }
}
</style>
