<template>
  <article class="holland-note goi-y-khao-sat">
    <img
      class="goi-y-khao-sat__image"
      :src="anhPhanVan"
      alt="Học sinh đứng giữa hai cánh cửa, phân vân chưa chọn hướng đi"
    />
    <div class="goi-y-khao-sat__body">
      <h2 class="goi-y-khao-sat__title">Bạn chưa định hình được sẽ làm gì?</h2>
      <p class="holland-note__text">
        Đừng lo, rất nhiều bạn cũng như vậy. Chỉ cần làm bài khảo sát tính cách nghề nghiệp Holland, hệ thống sẽ
        chỉ ra nhóm tính cách nổi trội của bạn và gợi ý những nhóm ngành nghề phù hợp nhất để bạn bắt đầu.
      </p>

      <ul class="goi-y-khao-sat__diem" aria-label="Thông tin bài khảo sát">
        <li><strong>~20 phút</strong> trả lời theo cảm nhận</li>
        <li><strong>6 nhóm</strong> tính cách RIASEC</li>
        <li><strong>Gợi ý</strong> nhóm ngành nghề phù hợp</li>
      </ul>

      <div class="goi-y-khao-sat__riasec" aria-hidden="true">
        <span v-for="chu in RIASEC" :key="chu.ma" :title="chu.ten">{{ chu.ma }}</span>
      </div>

      <button type="button" class="btn btn-success goi-y-khao-sat__action" @click="thamGia">
        Làm khảo sát ngay
      </button>
    </div>
  </article>
</template>

<script setup>
import { useRouter } from 'vue-router'
import anhPhanVan from '@/assets/guest/phan-van.jpg'
import { useTenRouteThpt } from '../useTenRouteThpt'

defineOptions({ name: 'ThptDiLamGoiYKhaoSat' })

const RIASEC = [
  { ma: 'R', ten: 'Kỹ thuật' },
  { ma: 'I', ten: 'Nghiên cứu' },
  { ma: 'A', ten: 'Nghệ thuật' },
  { ma: 'S', ten: 'Xã hội' },
  { ma: 'E', ten: 'Quản lý' },
  { ma: 'C', ten: 'Nghiệp vụ' },
]

const { tenRoute } = useTenRouteThpt()
const router = useRouter()

function thamGia() {
  router.push({ name: tenRoute('thpt-di-lam-huong-dan-khao-sat') })
}
</script>

<style scoped>
.goi-y-khao-sat {
  display: flex;
  align-items: stretch;
  gap: 20px;
  padding: 16px;
}

.goi-y-khao-sat__image {
  flex: 0 0 280px;
  width: 280px;
  min-height: 220px;
  object-fit: cover;
  border-radius: 10px;
}

.goi-y-khao-sat__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
  min-width: 0;
}

.goi-y-khao-sat .goi-y-khao-sat__title {
  margin: 0;
  color: var(--guest-primary);
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.35;
}

.goi-y-khao-sat__diem {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.goi-y-khao-sat__diem li {
  border: 1px solid #d7eadf;
  border-radius: 999px;
  padding: 5px 12px;
  background: #fff;
  color: #3a4742;
  font-size: 0.875rem;
  line-height: 1.3;
}

.goi-y-khao-sat__diem strong {
  color: var(--guest-primary);
}

.goi-y-khao-sat__riasec {
  display: flex;
  gap: 6px;
}

.goi-y-khao-sat__riasec span {
  display: grid;
  place-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(var(--guest-primary-rgb), 0.12);
  color: var(--guest-primary);
  font-weight: 700;
}

.goi-y-khao-sat__action {
  align-self: flex-start;
  padding-inline: 20px;
}

@media (max-width: 767.98px) {
  .goi-y-khao-sat {
    flex-direction: column;
    gap: 14px;
    padding: 12px;
  }

  .goi-y-khao-sat__image {
    flex-basis: auto;
    width: 100%;
    min-height: 0;
    height: 180px;
  }

  .goi-y-khao-sat .goi-y-khao-sat__title {
    font-size: 1.2rem;
  }

  .goi-y-khao-sat__action {
    align-self: stretch;
  }
}
</style>
