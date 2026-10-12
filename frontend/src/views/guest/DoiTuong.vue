<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { DOI_TUONG_KEY, doiTuongList } from '@/data/doiTuong'
import HocSinhThcs from '@/components/guest/doi-tuong/HocSinhThcs.vue'
import HocSinhThpt from '@/components/guest/doi-tuong/HocSinhThpt.vue'
import PhuHuynh from '@/components/guest/doi-tuong/PhuHuynh.vue'
import NhaTruong from '@/components/guest/doi-tuong/NhaTruong.vue'
import SinhVien from '@/components/guest/doi-tuong/SinhVien.vue'
import ThanhNienNgoaiTruong from '@/components/guest/doi-tuong/ThanhNienNgoaiTruong.vue'
import NhaTuyenDung from '@/components/guest/doi-tuong/NhaTuyenDung.vue'

const route = useRoute()

const audience = computed(() => doiTuongList.find((item) => item.code === route.meta.doiTuong))

watch(
  () => route.meta.doiTuong,
  (code) => {
    if (code) sessionStorage.setItem(DOI_TUONG_KEY, code)
  },
  { immediate: true },
)
</script>

<template>
  <HocSinhThcs v-if="audience?.ma === 'THCS'" :audience="audience" />
  <HocSinhThpt v-else-if="audience?.ma === 'THPT'" :audience="audience" />
  <PhuHuynh v-else-if="audience?.ma === 'PH'" :audience="audience" />
  <NhaTruong v-else-if="audience?.ma === 'NTR'" :audience="audience" />
  <SinhVien v-else-if="audience?.ma === 'SV'" :audience="audience" />
  <ThanhNienNgoaiTruong v-else-if="audience?.ma === 'TN'" :audience="audience" />
  <NhaTuyenDung v-else-if="audience?.ma === 'NTD'" :audience="audience" />
</template>
