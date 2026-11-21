<template>
  <TrangVanBan :van-ban="CHINH_SACH_BAO_MAT" :lien-quan="DIEU_KHOAN_SU_DUNG" />
</template>

<script setup>
import TrangVanBan from '@/components/guest/van-ban/TrangVanBan.vue'
import { CHINH_SACH_BAO_MAT, DIEU_KHOAN_SU_DUNG } from '@/data/vanBanPhapLy'

defineOptions({ name: 'ChinhSachBaoMat' })
</script>
