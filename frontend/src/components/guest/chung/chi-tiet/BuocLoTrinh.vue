<template>
  <div class="buoc-lo-trinh">
    <!-- Thanh bước: vòng tròn đánh số nối bằng đường kẻ; đường kẻ tô màu tới bước đang xem. -->
    <ol class="buoc-lo-trinh__thanh" :style="{ '--so-buoc': dsBuoc.length }">
      <li
        v-for="(buoc, i) in dsBuoc"
        :key="i"
        :class="{ 'is-da-qua': i < hienTai, 'is-hien-tai': i === hienTai, 'is-noi-den': i <= hienTai }"
      >
        <button
          type="button"
          class="buoc-lo-trinh__so"
          :aria-current="i === hienTai ? 'step' : undefined"
          :aria-label="`Bước ${i + 1}: ${buoc.tieuDe}`"
          @click="hienTai = i"
        >
          {{ i + 1 }}
        </button>
        <span class="buoc-lo-trinh__nhan" :title="buoc.tieuDe">{{ buoc.tieuDe }}</span>
      </li>
    </ol>

    <!-- Nội dung bước đang xem. -->
    <div v-if="buocHienTai" class="buoc-lo-trinh__noi-dung" aria-live="polite">
      <span class="buoc-lo-trinh__dem">Bước {{ hienTai + 1 }}/{{ dsBuoc.length }}</span>
      <strong class="buoc-lo-trinh__ten">{{ buocHienTai.tieuDe }}</strong>
      <p v-if="buocHienTai.moTa">{{ buocHienTai.moTa }}</p>
      <small v-if="buocHienTai.ghiChu">{{ buocHienTai.ghiChu }}</small>

      <!-- Chi tiết theo mục (nghề: mô tả công việc, lương trung bình, ghi chú). -->
      <div v-if="chiTietHienTai.length" class="buoc-lo-trinh__chi-tiet">
        <div
          v-for="muc in chiTietHienTai"
          :key="muc.label"
          class="buoc-lo-trinh__muc"
          :class="{ 'is-noi-bat': muc.noiBat, 'is-rong': muc.rong }"
        >
          <span class="buoc-lo-trinh__muc-nhan">
            <el-icon v-if="muc.icon" aria-hidden="true"><component :is="muc.icon" /></el-icon>{{ muc.label }}
          </span>
          <span class="buoc-lo-trinh__muc-gia-tri">{{ muc.giaTri }}</span>
        </div>
      </div>
      <p v-else-if="buocHienTai.chiTiet && !buocHienTai.moTa" class="buoc-lo-trinh__trong">
        Chưa có thông tin chi tiết cho giai đoạn này.
      </p>
    </div>

    <div v-if="dsBuoc.length > 1" class="buoc-lo-trinh__nut">
      <CustomButton type="primary" :disabled="hienTai === 0" @click="hienTai--">Trước</CustomButton>
      <CustomButton type="primary" :disabled="hienTai === dsBuoc.length - 1" @click="hienTai++">Tiếp</CustomButton>
    </div>
  </div>
</template>

<script setup>
/**
 * Lộ trình phát triển dạng từng bước (step by step), dùng trong modal chi tiết nghề / ngành:
 * thanh vòng tròn đánh số + nội dung bước đang xem + nút Trước / Tiếp (bấm vòng tròn cũng chuyển bước).
 * Bước: chuỗi (chỉ tiêu đề) hoặc { tieuDe, moTa?, ghiChu?, chiTiet? }, chiTiet = [{ label, giaTri, icon?, noiBat?, rong? }]
 * hiện thành các ô trong phần nội dung (mục rỗng tự ẩn).
 */
import { computed, ref, watch } from 'vue'
import { coGiaTri } from './phanChiTiet'

defineOptions({ name: 'BuocLoTrinh' })

const props = defineProps({
  buoc: { type: Array, default: () => [] },
})

const dsBuoc = computed(() => props.buoc.map((b) => (typeof b === 'string' ? { tieuDe: b } : b)))
const hienTai = ref(0)
const buocHienTai = computed(() => dsBuoc.value[hienTai.value] || null)
const chiTietHienTai = computed(() => (buocHienTai.value?.chiTiet || []).filter((muc) => coGiaTri(muc.giaTri)))

// Đổi sang nghề / ngành khác: quay về bước đầu.
watch(
  () => props.buoc,
  () => {
    hienTai.value = 0
  },
)
</script>

<style scoped>
.buoc-lo-trinh {
  --buoc-mau: #2f7a33;
  --buoc-nen: #eaf5eb;
  --buoc-xam: #dfe3e1;
  --buoc-co: 40px;
  --buoc-net: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 8px 0 4px;
}

.buoc-lo-trinh__thanh {
  display: grid;
  grid-template-columns: repeat(var(--so-buoc), minmax(0, 1fr));
  width: 100%;
  max-width: calc(var(--so-buoc) * 180px);
  margin: 0;
  padding: 0;
  list-style: none;
}

.buoc-lo-trinh__thanh li {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

/* Đường kẻ nối từ tâm bước trước tới tâm bước này; tô màu khi đã đi tới bước này. */
.buoc-lo-trinh__thanh li + li::before {
  content: '';
  position: absolute;
  top: calc((var(--buoc-co) - var(--buoc-net)) / 2);
  right: 50%;
  left: -50%;
  height: var(--buoc-net);
  background: var(--buoc-xam);
  transition: background 0.25s ease;
}

.buoc-lo-trinh__thanh li.is-noi-den + li.is-noi-den::before {
  background: var(--buoc-mau);
}

.buoc-lo-trinh__so {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--buoc-co);
  height: var(--buoc-co);
  padding: 0;
  border: 3px solid var(--buoc-xam);
  border-radius: 50%;
  background: #fff;
  color: #9aa39f;
  font: inherit;
  font-size: 1rem;
  cursor: pointer;
  transition:
    border-color 0.25s ease,
    background 0.25s ease,
    color 0.25s ease;
}

.buoc-lo-trinh__so:hover {
  border-color: rgba(47, 122, 51, 0.5);
}

.buoc-lo-trinh__so:focus-visible {
  outline: 2px solid var(--buoc-mau);
  outline-offset: 2px;
}

.is-noi-den .buoc-lo-trinh__so {
  border-color: var(--buoc-mau);
  color: var(--buoc-mau);
}

.is-hien-tai .buoc-lo-trinh__so {
  background: var(--buoc-nen);
  font-weight: 600;
}

.buoc-lo-trinh__nhan {
  display: -webkit-box;
  max-width: 100%;
  overflow: hidden;
  padding: 0 6px;
  color: #6b7570;
  font-size: 0.8rem;
  line-height: 1.35;
  text-align: center;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.is-hien-tai .buoc-lo-trinh__nhan {
  color: #1c2b23;
  font-weight: 500;
}

.buoc-lo-trinh__noi-dung {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  max-width: 760px;
  padding: 12px 16px;
  border: 1px solid #d7eadf;
  border-radius: 8px;
  background: #f4faf5;
  text-align: center;
}

.buoc-lo-trinh__dem {
  color: var(--buoc-mau);
  font-size: 0.78rem;
}

.buoc-lo-trinh__ten {
  color: #1c2b23;
  font-size: 0.95rem;
  font-weight: 600;
}

.buoc-lo-trinh__noi-dung p {
  margin: 0;
  color: #3a4742;
  font-size: 0.875rem;
  line-height: 1.5;
}

.buoc-lo-trinh__noi-dung small {
  color: var(--el-text-color-secondary);
  font-size: 0.78rem;
  font-style: italic;
}

/* Các ô chi tiết của bước: mô tả rộng gấp đôi, lương nổi bật; khung hẹp thì xếp dọc. */
.buoc-lo-trinh__chi-tiet {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
  text-align: left;
}

.buoc-lo-trinh__muc {
  display: flex;
  flex: 1 1 180px;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid #e3efe6;
  border-radius: 8px;
  background: #fff;
}

.buoc-lo-trinh__muc.is-rong {
  flex: 2 1 280px;
}

.buoc-lo-trinh__muc-nhan {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--el-text-color-secondary);
  font-size: 0.78rem;
}

.buoc-lo-trinh__muc-nhan .el-icon {
  color: var(--buoc-mau);
}

.buoc-lo-trinh__muc-gia-tri {
  color: #1c2b23;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-line;
  overflow-wrap: anywhere;
}

.buoc-lo-trinh__muc.is-noi-bat .buoc-lo-trinh__muc-gia-tri {
  color: var(--buoc-mau);
  font-size: 1rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.buoc-lo-trinh__trong {
  margin: 4px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 0.82rem;
}

.buoc-lo-trinh__nut {
  display: flex;
  gap: 12px;
}

.buoc-lo-trinh__nut :deep(.el-button) {
  min-width: 96px;
  margin: 0;
}

/* Khung hẹp: vòng tròn nhỏ lại, ẩn tên dưới vòng tròn (tên bước đã hiện trong ô nội dung). */
@container (max-width: 480px) {
  .buoc-lo-trinh {
    --buoc-co: 32px;
    --buoc-net: 3px;
  }

  .buoc-lo-trinh__nhan {
    display: none;
  }
}
</style>
