<template>
  <CustomDialog v-model="visible" :title="tieuDe" width="80%" destroy-on-close>
    <div class="khung-chi-tiet">
      <!-- Slot #dau: phần đầu (DauChiTiet). Slot mặc định: các CardThongTin, xếp lưới 1 → 2 cột. -->
      <slot name="dau" />
      <div class="khung-chi-tiet__luoi">
        <slot />
      </div>
    </div>

    <template #footer>
      <CustomButton @click="visible = false">Đóng</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/** Khung dùng chung của các modal chi tiết tra cứu: dialog + phần đầu + lưới card. */
defineOptions({ name: 'KhungChiTiet' })

defineProps({
  tieuDe: { type: String, default: '' },
})
const visible = defineModel({ type: Boolean, default: false })
</script>

<style scoped>
.khung-chi-tiet {
  container-type: inline-size;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Lưới card theo bề rộng khung dialog (kể cả khi kéo đổi cỡ): 1 cột → 2 cột. Card .rong chiếm cả hàng. */
.khung-chi-tiet__luoi {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 16px;
}

@container (min-width: 720px) {
  .khung-chi-tiet__luoi {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
