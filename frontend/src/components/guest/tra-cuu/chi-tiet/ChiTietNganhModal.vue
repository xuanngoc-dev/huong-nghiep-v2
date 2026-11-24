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

      <!-- Lộ trình phát triển: các giai đoạn nối tiếp, hiện dạng các bước đánh số. -->
      <CardThongTin v-if="loTrinh.length" tieu-de="Lộ trình phát triển" icon="TrendCharts">
        <ol class="lo-trinh">
          <li v-for="buoc in loTrinh" :key="buoc.label">
            <strong>{{ buoc.label }}</strong>
            <p>{{ buoc.giaTri }}</p>
            <small v-if="buoc.ghiChu">{{ buoc.ghiChu }}</small>
          </li>
        </ol>
      </CardThongTin>
    </template>
  </KhungChiTiet>
</template>

<script setup>
/** Modal chi tiết ngành đào tạo ở trang Tra cứu (khách). Dữ liệu lấy từ danh sách đã tải, không gọi thêm API. */
import { computed } from 'vue'
import KhungChiTiet from './KhungChiTiet.vue'
import DauChiTiet from './DauChiTiet.vue'
import CardThongTin from './CardThongTin.vue'
import { dongTuDanhSach, locNhan, o } from './phanChiTiet'
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

const loTrinh = computed(() => dongTuDanhSach(n.value.lo_trinh_phat_trien))
</script>

<style scoped>
.lo-trinh {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: buoc;
}

.lo-trinh li {
  position: relative;
  padding-left: 36px;
  counter-increment: buoc;
}

.lo-trinh li::before {
  content: counter(buoc);
  position: absolute;
  top: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #eaf5eb;
  color: #2f7a33;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Đường nối giữa các bước. */
.lo-trinh li:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 28px;
  bottom: -10px;
  left: 11px;
  width: 2px;
  background: #d7eadf;
}

.lo-trinh strong {
  color: #1c2b23;
  font-size: 0.875rem;
  font-weight: 600;
}

.lo-trinh p {
  margin: 2px 0 0;
  color: #3a4742;
  font-size: 0.875rem;
  line-height: 1.5;
}

.lo-trinh small {
  color: var(--el-text-color-secondary);
  font-size: 0.78rem;
  font-style: italic;
}
</style>
