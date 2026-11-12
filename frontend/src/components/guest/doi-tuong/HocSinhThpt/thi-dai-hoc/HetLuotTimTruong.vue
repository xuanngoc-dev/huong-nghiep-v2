<template>
  <article class="het-luot" aria-labelledby="het-luot-title">
    <img class="het-luot__image" :src="anhTruong" alt="" aria-hidden="true" />
    <div class="het-luot__body">
      <h3 id="het-luot-title" class="het-luot__title">
        Ngôi trường phù hợp với bạn đang chờ được khám phá!
        <span aria-hidden="true">🎓</span>
      </h3>
      <p class="het-luot__lead">
        Mỗi lựa chọn hôm nay đều có thể mở ra một cơ hội mới cho tương lai. Hãy tiếp tục khám phá những ngôi trường
        phù hợp với năng lực, sở thích và điều kiện tài chính của bạn.
      </p>
      <div class="het-luot__note">
        <p class="het-luot__note-title">
          <el-icon class="het-luot__note-icon" aria-hidden="true"><MagicStick /></el-icon>
          Hành trình của bạn vẫn tiếp tục!
        </p>
        <p class="het-luot__note-text">
          Bạn đã sử dụng hết lượt tìm kiếm miễn phí hôm nay. Có thể mở rộng lượt tìm kiếm ngay hoặc tiếp tục miễn
          phí vào ngày mai.
        </p>
      </div>
      <div class="het-luot__actions">
        <button type="button" class="het-luot__cta" @click="$emit('kham-pha')">
          Tiếp tục khám phá trường phù hợp
          <el-icon aria-hidden="true"><Right /></el-icon>
        </button>
        <p class="het-luot__sub">Xem các lựa chọn mua thêm lượt trước khi thanh toán</p>
      </div>
    </div>
  </article>
</template>

<script setup>
import anhTruong from '@/assets/guest/sinh-vien.jpg'

defineOptions({ name: 'HetLuotTimTruong' })

defineEmits(['kham-pha'])
</script>

<style scoped>
/* Ảnh bên trái, nội dung bên phải để card trải hết chiều ngang mà vẫn thấp. */
.het-luot {
  display: flex;
  align-items: stretch;
  gap: 20px;
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #c5d5cc;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 28px rgba(28, 43, 35, 0.08);
  text-align: left;
}

.het-luot__image {
  flex: 0 0 300px;
  width: 300px;
  min-height: 200px;
  object-fit: cover;
  border-radius: 12px;
  background: #e7edf2;
}

.het-luot__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.het-luot__title {
  margin: 0;
  color: #0c5c34;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.4;
}

.het-luot__lead {
  margin: 6px 0 0;
  color: #3a4742;
  font-size: 0.9375rem;
  line-height: 1.55;
}

.het-luot__note {
  margin-top: 10px;
  padding: 8px 12px;
  border-radius: 10px;
  background: #eef6f1;
}

.het-luot__note-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #1c2836;
  font-size: 0.9375rem;
  font-weight: 600;
}

.het-luot__note-icon {
  color: #2f9e5b;
  font-size: 18px;
}

.het-luot__note-text {
  margin: 2px 0 0;
  color: #3a4742;
  font-size: 0.875rem;
  line-height: 1.5;
}

.het-luot__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 14px;
  margin-top: 12px;
}

.het-luot__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 22px;
  border: 0;
  border-radius: 999px;
  background: #0c5c34;
  color: #fff;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    transform 0.2s ease;
}

.het-luot__cta:hover {
  background: #084422;
  transform: translateY(-1px);
}

.het-luot__cta:focus-visible {
  outline: 3px solid color-mix(in srgb, #0c5c34 35%, transparent);
  outline-offset: 2px;
}

.het-luot__sub {
  margin: 0;
  color: #5a6e63;
  font-size: 0.8125rem;
}

@media (max-width: 767.98px) {
  .het-luot {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }

  .het-luot__image {
    flex-basis: auto;
    width: 100%;
    min-height: 0;
    height: 140px;
  }

  .het-luot__title {
    font-size: 1.1rem;
  }

  .het-luot__cta {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .het-luot__cta {
    transition: none;
  }
}
</style>
