<script setup>
import { useRouter } from 'vue-router'
import anhPhanVan from '@/assets/guest/phan-van.jpg'
import { GIAI_DOAN_THI_DAI_HOC_KEY } from './giaiDoan'

defineOptions({ name: 'ThptNhacKhaoSat' })

const router = useRouter()

function thamGia() {
  sessionStorage.setItem(GIAI_DOAN_THI_DAI_HOC_KEY, 'chua-co')
  router.push({ name: 'thpt-thi-dai-hoc-chua-co' })
}
</script>

<template>
  <article class="holland-note nhac-khao-sat">
    <img
      class="nhac-khao-sat__image"
      :src="anhPhanVan"
      alt="Học sinh đứng giữa hai cánh cửa, phân vân chưa chọn hướng đi"
    />
    <div class="nhac-khao-sat__body">
      <h2 class="holland-note__title">Ngành bạn thích đã thực sự phù hợp?</h2>
      <p class="holland-note__text">
        Bạn có thể đã có ngành nghề mình yêu thích. Hệ thống vẫn giúp bạn đánh giá xem mình thực sự đã thích
        ngành đó chưa, hoặc chỉ ra những ngành nghề bạn chưa biết đến. Để chắc chắn về sự lựa chọn của mình,
        hãy làm khảo sát.
      </p>
      <button type="button" class="btn btn-success btn-sm nhac-khao-sat__action" @click="thamGia">
        Tham gia ngay
      </button>
    </div>
  </article>
</template>

<style scoped>
.nhac-khao-sat {
  display: flex;
  align-items: stretch;
  gap: 16px;
  padding: 12px;
}

.nhac-khao-sat__image {
  flex: 0 0 240px;
  width: 240px;
  object-fit: cover;
  border-radius: 10px;
}

.nhac-khao-sat__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  padding: 4px 6px 4px 0;
}

.nhac-khao-sat__action {
  align-self: flex-start;
  margin-top: 12px;
}

@media (max-width: 767.98px) {
  .nhac-khao-sat {
    flex-direction: column;
  }

  .nhac-khao-sat__image {
    flex-basis: auto;
    width: 100%;
    height: 180px;
  }

  .nhac-khao-sat__body {
    padding: 0 4px 4px;
  }
}
</style>
