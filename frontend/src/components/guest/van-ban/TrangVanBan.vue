<template>
  <div class="landing">
    <section class="landing__section" :aria-labelledby="`${vanBan.ma}-title`">
      <div class="container-fluid">
        <div class="landing__head">
          <p class="landing__eyebrow">Văn bản</p>
          <h1 :id="`${vanBan.ma}-title`" class="landing__title">{{ vanBan.tieuDe }}</h1>
          <p class="landing__lead">{{ vanBan.moTa }}</p>
          <p class="van-ban__cap-nhat">
            Cập nhật lần cuối: <time :datetime="vanBan.capNhat">{{ dinhDangNgay(vanBan.capNhat) }}</time>
          </p>
        </div>

        <div class="row g-lp">
          <!-- Mục lục: cột trái dính khi cuộn (desktop), nằm trên nội dung (mobile). -->
          <nav class="col-lg-3" aria-label="Mục lục">
            <ol class="van-ban__muc-luc">
              <li v-for="(muc, index) in vanBan.muc" :key="muc.id">
                <RouterLink :to="{ hash: `#${muc.id}` }">{{ index + 1 }}. {{ muc.tieuDe }}</RouterLink>
              </li>
            </ol>
          </nav>

          <article class="col-lg-9">
            <div class="van-ban__noi-dung">
              <NoiDungVanBan :van-ban="vanBan" neo />

              <p class="van-ban__lien-quan">
                Xem thêm:
                <RouterLink :to="{ name: lienQuan.ma }">{{ lienQuan.tieuDe }}</RouterLink>
              </p>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { dinhDangNgay } from '@/utils/thoiGian'
import NoiDungVanBan from './NoiDungVanBan.vue'
import '@/components/guest/landing/landing.css'

// Trang văn bản dài (chính sách, điều khoản): mục lục + các mục có neo #id. Nội dung ở data/vanBanPhapLy.js.
defineOptions({ name: 'TrangVanBan' })

defineProps({
  // { ma, tieuDe, moTa, capNhat, muc: [{ id, tieuDe, doan, ds, sau }] }
  vanBan: { type: Object, required: true },
  // Văn bản liên quan hiện ở cuối trang: { ma (tên route), tieuDe }.
  lienQuan: { type: Object, required: true },
})
</script>

<style scoped>
.van-ban__cap-nhat {
  margin: var(--lp-gap-sm) 0 0;
  color: var(--lp-muted);
  font-size: 0.875rem;
}

.van-ban__muc-luc {
  position: sticky;
  top: 90px;
  display: grid;
  gap: 2px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.van-ban__muc-luc a {
  display: block;
  padding: 6px 10px;
  border-radius: 6px;
  color: var(--lp-muted);
  font-size: 0.9rem;
  line-height: 1.4;
  text-decoration: none;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.van-ban__muc-luc a:hover {
  background: var(--lp-primary-soft);
  color: var(--lp-primary-strong);
}

.van-ban__noi-dung {
  padding: 32px;
  border: 1px solid var(--lp-line);
  border-radius: var(--lp-radius);
  background: #fff;
}

.van-ban__lien-quan {
  margin: 32px 0 0;
  padding-top: 20px;
  border-top: 1px solid var(--lp-line);
  color: var(--lp-muted);
}

.van-ban__lien-quan a {
  color: var(--lp-primary-strong);
  font-weight: 500;
}

@media (max-width: 991.98px) {
  .van-ban__muc-luc {
    position: static;
    padding: 12px;
    border: 1px solid var(--lp-line);
    border-radius: var(--lp-radius);
    background: #fff;
  }
}

@media (max-width: 575.98px) {
  .van-ban__noi-dung {
    padding: 20px 16px;
  }
}
</style>
