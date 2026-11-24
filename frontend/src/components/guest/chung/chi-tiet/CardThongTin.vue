<template>
  <section v-if="coNoiDung" class="card-thong-tin" :class="{ 'card-thong-tin--rong': rong, 'card-thong-tin--luu-y': luuY }">
    <h3>
      <el-icon aria-hidden="true"><component :is="icon" /></el-icon>{{ tieuDe }}
    </h3>

    <p v-if="coGiaTri(doan)" class="card-thong-tin__doan">{{ doan }}</p>

    <div v-if="nhanHienThi.length" class="card-thong-tin__nhan">
      <span v-for="tag in nhanHienThi" :key="tag">{{ tag }}</span>
    </div>

    <ul v-if="dsHienThi.length" class="card-thong-tin__ds">
      <li v-for="muc in dsHienThi" :key="muc">{{ muc }}</li>
    </ul>

    <dl v-if="dongHienThi.length">
      <div v-for="row in dongHienThi" :key="row.label" class="card-thong-tin__dong">
        <dt>{{ row.label }}</dt>
        <dd>
          <a v-if="row.href" :href="row.href" target="_blank" rel="noopener noreferrer">{{ row.giaTri }}</a>
          <template v-else>{{ row.giaTri }}</template>
          <small v-if="row.ghiChu">{{ row.ghiChu }}</small>
        </dd>
      </div>
    </dl>

    <!-- Nội dung riêng của từng loại (bảng cấu trúc bài thi, lộ trình…). -->
    <slot />
  </section>
</template>

<script setup>
/**
 * Một card nhóm thông tin trong modal chi tiết (tra cứu, thư viện ngành nghề): tiêu đề + icon, rồi đoạn văn /
 * nhãn / gạch đầu dòng / các dòng nhãn – giá trị / slot. Dòng và nhãn rỗng tự ẩn; card không còn nội dung nào thì ẩn cả card.
 */
import { computed, useSlots } from 'vue'
import { coGiaTri, locNhan } from './phanChiTiet'

defineOptions({ name: 'CardThongTin' })

const props = defineProps({
  tieuDe: { type: String, required: true },
  // Tên icon Element Plus.
  icon: { type: String, default: 'Document' },
  // [{ label, giaTri, href?, ghiChu? }] — dựng bằng o() / oLink() trong phanChiTiet.js.
  dong: { type: Array, default: () => [] },
  doan: { type: [String, Number], default: '' },
  nhan: { type: Array, default: () => [] },
  // Gạch đầu dòng: mục dài như câu (trách nhiệm, chứng chỉ…); mục ngắn dùng nhan.
  ds: { type: Array, default: () => [] },
  // Chiếm cả hàng lưới (đoạn văn dài, bảng).
  rong: { type: Boolean, default: false },
  // Nền vàng nhạt cho lưu ý / cảnh báo.
  luuY: { type: Boolean, default: false },
})

const slots = useSlots()

const dongHienThi = computed(() => props.dong.filter((row) => coGiaTri(row.giaTri)))
const nhanHienThi = computed(() => locNhan(props.nhan))
const dsHienThi = computed(() => locNhan(props.ds))
const coNoiDung = computed(
  () =>
    dongHienThi.value.length ||
    nhanHienThi.value.length ||
    dsHienThi.value.length ||
    coGiaTri(props.doan) ||
    !!slots.default,
)
</script>

<style scoped>
.card-thong-tin {
  min-width: 0;
  padding: 14px 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: #fff;
}

.card-thong-tin--rong {
  grid-column: 1 / -1;
}

.card-thong-tin--luu-y {
  border-color: #f3dfb0;
  background: #fffaf0;
}

.card-thong-tin h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  color: #1c2b23;
  font-size: 0.95rem;
  font-weight: 600;
}

.card-thong-tin h3 .el-icon {
  color: #2f7a33;
}

.card-thong-tin--luu-y h3 {
  border-bottom-color: #f3dfb0;
}

.card-thong-tin--luu-y h3 .el-icon {
  color: #b7791f;
}

.card-thong-tin__doan {
  margin: 0;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.6;
  white-space: pre-line;
}

.card-thong-tin__doan + .card-thong-tin__nhan,
.card-thong-tin__doan + .card-thong-tin__ds,
.card-thong-tin__doan + dl,
.card-thong-tin__nhan + dl,
.card-thong-tin__ds + dl {
  margin-top: 10px;
}

.card-thong-tin__ds {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding-left: 18px;
  color: #3a4742;
  font-size: 0.875rem;
  line-height: 1.5;
}

.card-thong-tin__ds li::marker {
  color: #2f7a33;
}

.card-thong-tin__nhan {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.card-thong-tin__nhan span {
  padding: 4px 10px;
  border: 1px solid #d7eadf;
  border-radius: 6px;
  background: #f4faf5;
  color: #2f7a33;
  font-size: 0.85rem;
  font-weight: 500;
}

.card-thong-tin dl {
  margin: 0;
}

.card-thong-tin__dong {
  display: grid;
  grid-template-columns: minmax(120px, 40%) minmax(0, 1fr);
  gap: 12px;
  padding: 6px 0;
}

.card-thong-tin__dong + .card-thong-tin__dong {
  border-top: 1px dashed var(--el-border-color-lighter);
}

.card-thong-tin__dong dt {
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.card-thong-tin__dong dd {
  margin: 0;
  color: #1c2b23;
  font-size: 0.875rem;
  white-space: pre-line;
  overflow-wrap: anywhere;
}

.card-thong-tin__dong small {
  display: block;
  margin-top: 2px;
  color: var(--el-text-color-secondary);
  font-size: 0.78rem;
  font-style: italic;
}

.card-thong-tin a {
  color: #2f7a33;
}

/* Khung dialog hẹp: nhãn nằm trên giá trị. */
@container (max-width: 420px) {
  .card-thong-tin__dong {
    grid-template-columns: minmax(0, 1fr);
    gap: 2px;
  }
}
</style>
