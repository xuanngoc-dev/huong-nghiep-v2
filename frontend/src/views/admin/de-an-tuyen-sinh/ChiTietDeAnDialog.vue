<template>
  <CustomDialog
    v-model="visible"
    class="de-an-detail-dialog"
    title="Chi tiết đề án tuyển sinh"
    width="94%"
    destroy-on-close
  >
    <ChiTietDeAn :de-an-id="props.deAnId" :active="visible" />
    <template #footer>
      <CustomButton @click="visible = false">Đóng</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import ChiTietDeAn from './ChiTietDeAn.vue'

const visible = defineModel({ type: Boolean, default: false })

const props = defineProps({
  deAnId: { type: Number, default: null },
})
</script>

<style>
.custom-dialog.de-an-detail-dialog.el-dialog .el-dialog__body {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.custom-dialog.de-an-detail-dialog.el-dialog .el-tabs__content {
  max-height: min(62vh, 640px);
  overflow: auto;
}
</style>
