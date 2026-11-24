<template>
  <KhungChiTiet v-model="visible" tieu-de="Chi tiết ngành đào tạo">
    <template v-if="n" #dau>
      <DauChiTiet
        :tieu-de="n.ten_nganh"
        :phu="n.ten_tieng_anh || ''"
        :anh="n.hinh_anh_mo_ta || ''"
        :anh-logo="false"
        icon="Reading"
        :ma="n.ma_nganh || ''"
        :nhan="locNhan([n.ten_nhom_nganh, n.trinh_do, n.thoi_gian_dao_tao])"
      />
    </template>

    <template v-if="n">
      <CardThongTin tieu-de="Giới thiệu ngành" icon="Document" :doan="n.chi_tiet || n.mo_ta" rong />
      <CardThongTin tieu-de="Thông tin ngành" icon="Postcard" :dong="thongTinNganh" />
      <CardThongTin tieu-de="Nhóm tính cách Holland phù hợp" icon="User" :nhan="nhomHolland" />
      <CardThongTin tieu-de="Công việc sau khi ra trường" icon="Suitcase" :dong="dongTuDanhSach(n.mo_ta_cong_viec)" />

      <CardThongTin v-if="loTrinh.length" tieu-de="Lộ trình phát triển" icon="TrendCharts">
        <BuocLoTrinh :buoc="loTrinh" />
      </CardThongTin>
    </template>
  </KhungChiTiet>
</template>

<script setup>
/** Modal chi tiết ngành đào tạo ở trang Tra cứu (khách). Dữ liệu lấy từ danh sách đã tải, không gọi thêm API. */
import { computed } from 'vue'
import KhungChiTiet from '@/components/guest/chung/chi-tiet/KhungChiTiet.vue'
import DauChiTiet from '@/components/guest/chung/chi-tiet/DauChiTiet.vue'
import CardThongTin from '@/components/guest/chung/chi-tiet/CardThongTin.vue'
import BuocLoTrinh from '@/components/guest/chung/chi-tiet/BuocLoTrinh.vue'
import { dongTuDanhSach, locNhan, o } from '@/components/guest/chung/chi-tiet/phanChiTiet'
import { NOI_DUNG_NHOM } from '@/utils/ketQuaHolland'

defineOptions({ name: 'ChiTietNganhModal' })

const props = defineProps({
  item: { type: Object, default: null },
})
const visible = defineModel({ type: Boolean, default: false })

const n = computed(() => props.item)

const thongTinNganh = computed(() => [
  o('Mã ngành', n.value.ma_nganh),
  o('Nhóm ngành', locNhan([n.value.ma_nhom_nganh, n.value.ten_nhom_nganh]).join(' – ')),
  o('Trình độ', n.value.trinh_do),
  o('Thời gian đào tạo', n.value.thoi_gian_dao_tao),
  o('Mức lương tham khảo', n.value.muc_luong_tham_khao),
])

// ma_holand: ["R", "I"] → "R – Kỹ thuật", "I – Nghiên cứu"; mã lạ giữ nguyên.
const nhomHolland = computed(() => {
  const ma = Array.isArray(n.value.ma_holand) ? n.value.ma_holand : locNhan([n.value.ma_holand])
  return ma.map((m) => (NOI_DUNG_NHOM[m] ? `${m} – ${NOI_DUNG_NHOM[m].ten}` : m))
})

// [{ name, value, ghi_chu }] → bước { tieuDe, moTa, ghiChu }.
const loTrinh = computed(() =>
  dongTuDanhSach(n.value.lo_trinh_phat_trien).map((d) => ({ tieuDe: d.label, moTa: d.giaTri, ghiChu: d.ghiChu })),
)
</script>

