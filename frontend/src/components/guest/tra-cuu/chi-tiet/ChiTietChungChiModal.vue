<template>
  <KhungChiTiet v-model="visible" tieu-de="Chi tiết chứng chỉ ngoại ngữ">
    <template v-if="c" #dau>
      <DauChiTiet
        :tieu-de="c.ten_chung_chi"
        :phu="c.ten_chi_tiet || ''"
        icon="Medal"
        :ma="c.ma_chung_chi || ''"
        :nhan="locNhan([LOAI_CHUNG_CHI[c.loai_chung_chi], c.ten_ngon_ngu, c.linh_vuc])"
      />
    </template>

    <template v-if="c">
      <CardThongTin tieu-de="Thông tin chung" icon="Postcard" :dong="thongTinChung" />
      <CardThongTin tieu-de="Thi và điểm" icon="DataAnalysis" :dong="thiVaDiem" />
      <CardThongTin tieu-de="Kỹ năng được đánh giá" icon="Checked" :nhan="dsKyNang" rong />
      <CardThongTin tieu-de="Lưu ý" icon="WarningFilled" :doan="c.ghi_chu" rong luu-y />
    </template>
  </KhungChiTiet>
</template>

<script setup>
/** Modal chi tiết chứng chỉ ngoại ngữ ở trang Tra cứu (khách). Dữ liệu lấy từ danh sách đã tải, không gọi thêm API. */
import { computed } from 'vue'
import KhungChiTiet from './KhungChiTiet.vue'
import DauChiTiet from './DauChiTiet.vue'
import CardThongTin from './CardThongTin.vue'
import { LOAI_CHUNG_CHI, locNhan, o } from './phanChiTiet'

defineOptions({ name: 'ChiTietChungChiModal' })

const props = defineProps({
  item: { type: Object, default: null },
})
const visible = defineModel({ type: Boolean, default: false })

const c = computed(() => props.item)

const thongTinChung = computed(() => [
  o('Mã chứng chỉ', c.value.ma_chung_chi),
  o('Đơn vị cấp', c.value.don_vi_cap),
  o('Loại chứng chỉ', LOAI_CHUNG_CHI[c.value.loai_chung_chi] || c.value.loai_chung_chi),
  o('Lĩnh vực', c.value.linh_vuc),
  o('Ngôn ngữ', c.value.ten_ngon_ngu),
  o('Môn', c.value.mon),
  o('Trạng thái', c.value.trang_thai),
])

const thiVaDiem = computed(() => [
  o('Thang điểm', c.value.thang_diem, { donVi: c.value.don_vi_diem || '' }),
  { ...o('Hình thức thi', c.value.hinh_thuc_thi), ghiChu: c.value.ghi_chu_hinh_thuc_thi || '' },
  o('Thời hạn hiệu lực', c.value.thoi_han_hieu_luc_thang, { donVi: 'tháng' }),
])

// ky_nang_duoc_danh_gia thường là mảng; dữ liệu cũ dạng chuỗi "Nghe, Nói" thì tách theo dấu phẩy.
const dsKyNang = computed(() => {
  const value = c.value.ky_nang_duoc_danh_gia
  return Array.isArray(value) ? value : String(value || '').split(/[,;]/).map((kn) => kn.trim())
})
</script>
