<template>
  <article class="het-luot" aria-labelledby="het-luot-title">
    <img class="het-luot__image" :src="anhTruong" alt="" aria-hidden="true" />
    <div class="het-luot__body">
      <h3 id="het-luot-title" class="het-luot__title">
        Ngôi trường phù hợp với bạn đang chờ được khám phá
      </h3>
      <p class="het-luot__lead">
        Mỗi lựa chọn hôm nay đều có thể mở ra một cơ hội mới cho tương lai. Hãy tiếp tục khám phá những ngôi trường
        phù hợp với năng lực, sở thích và điều kiện tài chính của bạn.
      </p>
      <div class="het-luot__note">
        <p class="het-luot__note-title">
          <el-icon class="het-luot__note-icon" aria-hidden="true"><MagicStick /></el-icon>
          Hành trình của bạn vẫn tiếp tục
        </p>
        <p v-if="laThanhVien" class="het-luot__note-text">
          Bạn đã dùng hết lượt tìm kiếm miễn phí hôm nay và lượt tra cứu đã mua. Nạp thêm lượt tra cứu để tìm tiếp
          ngay, hoặc quay lại tìm miễn phí vào ngày mai.
        </p>
        <template v-else>
          <p class="het-luot__note-text">
            Bạn đã dùng hết lượt tìm thử dành cho khách hôm nay. Đăng ký hoặc đăng nhập để tiếp tục tìm trường ngay:
          </p>
          <ul class="het-luot__loi-ich">
            <li>
              <el-icon aria-hidden="true"><CircleCheck /></el-icon>
              <span>Được tìm miễn phí <strong>{{ soLuotThanhVien }} lượt mỗi ngày</strong></span>
            </li>
            <li>
              <el-icon aria-hidden="true"><CircleCheck /></el-icon>
              <span>Lưu hồ sơ năng lực để gợi ý trường sát với bạn hơn</span>
            </li>
            <li>
              <el-icon aria-hidden="true"><CircleCheck /></el-icon>
              <span>Xem lại lịch sử tìm kiếm và mua thêm lượt tra cứu khi cần</span>
            </li>
          </ul>
        </template>
      </div>
      <div v-if="!laThanhVien" class="het-luot__actions het-luot__actions--khach">
        <div class="het-luot__nut">
          <button type="button" class="het-luot__cta" @click="$emit('dang-ky')">
            <el-icon aria-hidden="true"><UserFilled /></el-icon>
            Đăng ký miễn phí
          </button>
          <button type="button" class="het-luot__cta het-luot__cta--phu" @click="$emit('dang-nhap')">
            Đăng nhập
          </button>
        </div>
      </div>
      <div v-else class="het-luot__actions">
        <button type="button" class="het-luot__cta" @click="$emit('kham-pha')">
          <el-icon aria-hidden="true"><Wallet /></el-icon>
          Nhận thêm lượt
        </button>
        <p class="het-luot__sub">Rất nhiều gói dịch vụ phù hợp với nhu cầu của bạn</p>
      </div>
    </div>
  </article>
</template>

<script setup>
import anhTruong from '@/assets/guest/sinh-vien.jpg'

defineOptions({ name: 'HetLuotTimTruong' })

defineProps({
  // Thành viên: hết cả lượt miễn phí lẫn lượt tra cứu đã mua → nút nạp tiền.
  laThanhVien: { type: Boolean, default: false },
  // Số lượt tìm miễn phí mỗi ngày của thành viên (gợi ý khách đăng ký).
  soLuotThanhVien: { type: Number, default: 5 },
})

// kham-pha: thành viên nạp thêm lượt; dang-ky / dang-nhap: khách hết lượt tìm thử.
defineEmits(['kham-pha', 'dang-ky', 'dang-nhap'])
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
  font-weight: 600;
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
  border-radius: 8px;
  background: #0c5c34;
  color: #fff;
  /* font-size: 0.9375rem; */
  font-weight: 500;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    transform 0.2s ease;
}

.het-luot__nut {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.het-luot__loi-ich {
  display: grid;
  gap: 6px;
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}

.het-luot__loi-ich li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
}

.het-luot__loi-ich .el-icon {
  flex-shrink: 0;
  margin-top: 3px;
  color: #3f9466;
}

.het-luot__cta:hover {
  background: #084422;
  transform: translateY(-1px);
}

.het-luot__cta:focus-visible {
  outline: 3px solid color-mix(in srgb, #0c5c34 35%, transparent);
  outline-offset: 2px;
}

.het-luot__cta--phu {
  border: 1px solid #0c5c34;
  background: #fff;
  color: #0c5c34;
}

.het-luot__cta--phu:hover {
  background: #eef6f1;
  color: #084422;
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
