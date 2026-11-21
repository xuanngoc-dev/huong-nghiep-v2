<template>
  <TrangVanBan :van-ban="DIEU_KHOAN_SU_DUNG" :lien-quan="CHINH_SACH_BAO_MAT" />
</template>

<script setup>
import TrangVanBan from '@/components/guest/van-ban/TrangVanBan.vue'
import { CHINH_SACH_BAO_MAT, DIEU_KHOAN_SU_DUNG } from '@/data/vanBanPhapLy'

defineOptions({ name: 'DieuKhoanSuDung' })
</script>
