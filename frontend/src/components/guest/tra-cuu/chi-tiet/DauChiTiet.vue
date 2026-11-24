<template>
  <header class="dau-chi-tiet">
    <div class="dau-chi-tiet__media" :class="{ 'is-anh': anh && !anhLogo }">
      <img v-if="anh" :src="anh" :alt="tieuDe" />
      <template v-else>
        <el-icon class="dau-chi-tiet__icon" aria-hidden="true"><component :is="icon" /></el-icon>
        <span v-if="ma" class="dau-chi-tiet__ma">{{ ma }}</span>
      </template>
    </div>
    <div class="dau-chi-tiet__ten">
      <h2>{{ tieuDe }}</h2>
      <p v-if="phu">{{ phu }}</p>
      <div v-if="nhan.length" class="dau-chi-tiet__nhan">
        <span v-for="tag in nhan" :key="tag">{{ tag }}</span>
      </div>
    </div>
    <div v-if="loiTat.length" class="dau-chi-tiet__loi-tat">
      <a v-for="l in loiTat" :key="l.label" :href="l.href" target="_blank" rel="noopener noreferrer">
        <el-icon aria-hidden="true"><Link /></el-icon>{{ l.label }}
      </a>
    </div>
  </header>
</template>

<script setup>
/**
 * Phần đầu modal chi tiết tra cứu: ảnh/logo (hoặc icon + mã như thẻ kết quả), tên, tên phụ, nhãn, nút lối tắt.
 */
import { Link } from '@element-plus/icons-vue'

defineOptions({ name: 'DauChiTiet' })

defineProps({
  tieuDe: { type: String, default: '' },
  // Dòng phụ dưới tên: tên viết tắt, tên tiếng Anh, tên đầy đủ…
  phu: { type: String, default: '' },
  anh: { type: String, default: '' },
  // true: logo (thu vừa khung, nền trắng); false: ảnh minh họa (phủ kín khung, rộng hơn).
  anhLogo: { type: Boolean, default: true },
  // Tên icon Element Plus khi không có ảnh.
  icon: { type: String, default: 'Document' },
  ma: { type: String, default: '' },
  nhan: { type: Array, default: () => [] },
  // [{ label, href }] — dựng bằng loiTat() trong phanChiTiet.js.
  loiTat: { type: Array, default: () => [] },
})
</script>

<style scoped>
/* Dialog gắn ra ngoài body nên không dùng biến --lp-* của landing; màu theo TheTraCuu. */
.dau-chi-tiet {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #d7eadf;
  border-radius: 8px;
  background: #f4faf5;
}

.dau-chi-tiet__media {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 88px;
  height: 88px;
  overflow: hidden;
  border: 1px solid #d7eadf;
  border-radius: 8px;
  background: #fff;
  color: #2f7a33;
}

.dau-chi-tiet__media img {
  width: 100%;
  height: 100%;
  padding: 6px;
  object-fit: contain;
}

.dau-chi-tiet__media.is-anh {
  width: 160px;
  height: 100px;
}

.dau-chi-tiet__media.is-anh img {
  padding: 0;
  object-fit: cover;
}

.dau-chi-tiet__icon {
  font-size: 26px;
  opacity: 0.75;
}

.dau-chi-tiet__ma {
  max-width: calc(100% - 8px);
  padding: 2px 6px;
  border: 1px solid rgba(47, 122, 51, 0.3);
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
  text-align: center;
}

.dau-chi-tiet__ten {
  flex: 1 1 260px;
  min-width: 0;
}

.dau-chi-tiet__ten h2 {
  margin: 0;
  color: #1c2b23;
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.35;
}

.dau-chi-tiet__ten p {
  margin: 2px 0 0;
  color: #5b6b63;
  font-size: 0.875rem;
}

.dau-chi-tiet__nhan {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.dau-chi-tiet__nhan span {
  padding: 2px 8px;
  border-radius: 6px;
  background: #eaf5eb;
  color: #2f7a33;
  font-size: 0.8rem;
  font-weight: 500;
}

.dau-chi-tiet__loi-tat {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dau-chi-tiet__loi-tat a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 0 14px;
  border: 1px solid rgba(47, 122, 51, 0.35);
  border-radius: 8px;
  background: #fff;
  color: #2f7a33;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
}

.dau-chi-tiet__loi-tat a:hover {
  border-color: #2f7a33;
}
</style>
