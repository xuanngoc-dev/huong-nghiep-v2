<template>
  <!-- Dùng chung giao diện thẻ hướng đi (như DoiTuongCard): ảnh trái, nội dung phải; nhãn góc ảnh là nhóm tin. -->
  <HuongDiCard
    :image="bai.anh_dai_dien ? apiAssetUrl(bai.anh_dai_dien) : anhMacDinh"
    :title="bai.tieu_de"
    :description="bai.tom_tat || ''"
    :nhan="bai.ten_nhom"
    :note="ghiChu"
    :to="{ name: 'tin-tuc-chi-tiet', params: { slug: bai.slug } }"
    cta="Đọc tiếp"
  />
</template>

<script setup>
/** Thẻ bài viết ở trang tin tức (khách). */
import { computed } from 'vue'
import anhMacDinh from '@/assets/guest/thpt.jpg'
import { apiAssetUrl } from '@/api/apiUrl'
import HuongDiCard from '@/components/guest/chung/HuongDiCard.vue'
import { dinhDangNgay } from '@/utils/thoiGian'

defineOptions({ name: 'TheTinTuc' })

const props = defineProps({
  // Một bài từ API /tin-tuc/cong-khai/bai-viet.
  bai: { type: Object, required: true },
})

// Dòng phụ: ngày đăng · lượt xem.
const ghiChu = computed(() => {
  const ngay = dinhDangNgay(props.bai.created_at)
  const luotXem = props.bai.luot_xem ? `${props.bai.luot_xem.toLocaleString('vi-VN')} lượt xem` : ''
  return [ngay, luotXem].filter(Boolean).join(' · ')
})
</script>
