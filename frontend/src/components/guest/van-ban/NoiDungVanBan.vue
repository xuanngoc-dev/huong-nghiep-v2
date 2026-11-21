<template>
  <!-- Các mục của một văn bản (data/vanBanPhapLy.js); dùng ở trang văn bản và hộp thoại ở form đăng ký. -->
  <div class="noi-dung-van-ban">
    <section v-for="(muc, index) in vanBan.muc" :id="neo ? muc.id : undefined" :key="muc.id" class="noi-dung-van-ban__muc">
      <h2>{{ index + 1 }}. {{ muc.tieuDe }}</h2>
      <p v-for="(doan, i) in muc.doan || []" :key="`d${i}`">{{ doan }}</p>
      <ul v-if="muc.ds">
        <li v-for="(dong, i) in muc.ds" :key="i">{{ dong }}</li>
      </ul>
      <p v-for="(doan, i) in muc.sau || []" :key="`s${i}`">{{ doan }}</p>
    </section>
  </div>
</template>

<script setup>
defineOptions({ name: 'NoiDungVanBan' })

defineProps({
  // { tieuDe, muc: [{ id, tieuDe, doan, ds, sau }] }
  vanBan: { type: Object, required: true },
  // Gắn id cho từng mục để mục lục trỏ tới (#id); trong hộp thoại thì tắt để không trùng id với trang.
  neo: { type: Boolean, default: false },
})
</script>

<style scoped>
.noi-dung-van-ban__muc {
  /* Chừa chỗ cho header dính khi bấm mục lục. */
  scroll-margin-top: 90px;
}

.noi-dung-van-ban__muc + .noi-dung-van-ban__muc {
  margin-top: 28px;
}

.noi-dung-van-ban__muc h2 {
  margin: 0 0 12px;
  color: #0f172a;
  font-size: 1.15rem;
  font-weight: 500;
  line-height: 1.35;
}

.noi-dung-van-ban__muc p,
.noi-dung-van-ban__muc li {
  color: #334155;
  line-height: 1.7;
}

.noi-dung-van-ban__muc p {
  max-width: 72ch;
  margin: 0 0 12px;
}

.noi-dung-van-ban__muc ul {
  display: grid;
  gap: 6px;
  max-width: 72ch;
  margin: 0 0 12px;
  padding-left: 1.25rem;
}
</style>
