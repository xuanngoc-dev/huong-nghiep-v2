<template>
  <!-- Bố cục như HuongDiCard (thẻ đối tượng): khối hình bên trái, nội dung bên phải. Dữ liệu danh mục hiện
       chưa có ảnh nên khối trái hiện mã (BKA, D01, 7480201…) như ô điền trên phiếu xét tuyển; có ảnh thì dùng ảnh. -->
  <button type="button" class="the-tra-cuu h-100" @click="emit('xem')">
    <span class="the-tra-cuu__media" :class="{ 'has-anh': the.anh }">
      <img v-if="the.anh" class="the-tra-cuu__anh" :src="the.anh" alt="" loading="lazy" decoding="async" />
      <template v-else>
        <el-icon class="the-tra-cuu__icon" aria-hidden="true"><component :is="icon" /></el-icon>
        <span v-if="the.ma" class="the-tra-cuu__ma">{{ the.ma }}</span>
      </template>
    </span>
    <span class="the-tra-cuu__body">
      <span class="the-tra-cuu__ten">{{ the.tieuDe }}</span>
      <span v-if="the.tags.length" class="the-tra-cuu__tags">
        <span v-for="tag in the.tags" :key="tag" class="the-tra-cuu__tag">{{ tag }}</span>
      </span>
      <span v-if="the.moTa" class="the-tra-cuu__mo-ta">{{ the.moTa }}</span>
      <span class="the-tra-cuu__xem">Xem chi tiết →</span>
    </span>
  </button>
</template>

<script setup>
defineOptions({ name: 'TheTraCuu' })

defineProps({
  // Kết quả của loai.the(item): { tieuDe, ma, tags, moTa, anh }.
  the: { type: Object, required: true },
  // Tên icon Element Plus của loại tra cứu, hiện trên khối trái khi không có ảnh.
  icon: { type: String, default: 'Document' },
})

const emit = defineEmits(['xem'])
</script>

<style scoped>
.the-tra-cuu {
  display: flex;
  width: 100%;
  overflow: hidden;
  padding: 0;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius, 8px);
  background: #fff;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s ease;
}

.the-tra-cuu:hover {
  border-color: rgba(63, 150, 67, 0.5);
}

.the-tra-cuu:focus-visible {
  outline: 2px solid #2f7a33;
  outline-offset: 2px;
}

.the-tra-cuu__media {
  position: relative;
  display: flex;
  flex: 0 0 30%;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 150px;
  padding: 12px;
  overflow: hidden;
  background: #eaf5eb;
  color: #2f7a33;
}

.the-tra-cuu__anh {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.the-tra-cuu__icon {
  font-size: 24px;
  opacity: 0.7;
}

.the-tra-cuu__ma {
  max-width: 100%;
  padding: 4px 8px;
  border: 1px solid rgba(47, 122, 51, 0.3);
  border-radius: 6px;
  background: #fff;
  font-size: 0.95rem;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
  text-align: center;
}

.the-tra-cuu__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  min-width: 0;
  padding: 14px 16px;
}

.the-tra-cuu__ten {
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.35;
}

.the-tra-cuu__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.the-tra-cuu__tag {
  padding: 2px 8px;
  border-radius: 6px;
  background: #eaf5eb;
  color: #2f7a33;
  font-size: 0.8rem;
  font-weight: 500;
}

.the-tra-cuu__mo-ta {
  display: -webkit-box;
  overflow: hidden;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
}

.the-tra-cuu__xem {
  margin-top: auto;
  color: #2f7a33;
  font-size: 0.875rem;
  font-weight: 500;
}

@media (max-width: 575.98px) {
  .the-tra-cuu__media {
    flex-basis: 28%;
    min-height: 120px;
  }

  .the-tra-cuu__body {
    padding: 12px;
  }

  .the-tra-cuu__mo-ta {
    -webkit-line-clamp: 2;
    line-clamp: 2;
  }
}
</style>
