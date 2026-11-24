<template>
  <KhungChiTiet v-model="visible" tieu-de="Chi tiết trường">
    <template v-if="t" #dau>
      <DauChiTiet
        :tieu-de="t.ten_truong"
        :phu="locNhan([t.ten_viet_tat, t.ten_tieng_anh]).join(' · ')"
        :anh="t.logo_url || t.anh_dai_dien_url || ''"
        icon="School"
        :ma="t.ma_truong || ''"
        :nhan="locNhan([loaiCoSo(t), t.loai_hinh, t.ten_tinh_thanh])"
        :loi-tat="loiTat([
          { label: 'Website', url: t.website },
          { label: 'Trang tuyển sinh', url: t.website_tuyen_sinh },
        ])"
      />
    </template>

    <template v-if="t">
      <CardThongTin tieu-de="Giới thiệu" icon="Document" :doan="t.gioi_thieu_ngan" rong />
      <CardThongTin tieu-de="Thông tin chung" icon="Postcard" :dong="thongTinChung" />
      <CardThongTin tieu-de="Đào tạo" icon="Reading" :dong="daoTao" />
      <CardThongTin tieu-de="Liên hệ" icon="Location" :dong="lienHe" />
      <CardThongTin tieu-de="Tuyển sinh" icon="Tickets" :dong="tuyenSinh" />
    </template>
  </KhungChiTiet>
</template>

<script setup>
/** Modal chi tiết trường ĐH, CĐ ở trang Tra cứu (khách). Dữ liệu lấy từ danh sách đã tải, không gọi thêm API. */
import { computed } from 'vue'
import KhungChiTiet from './KhungChiTiet.vue'
import DauChiTiet from './DauChiTiet.vue'
import CardThongTin from './CardThongTin.vue'
import { locNhan, loiTat, o, oLink } from './phanChiTiet'
import { loaiCoSo } from '../loaiTraCuu'

defineOptions({ name: 'ChiTietTruongModal' })

const props = defineProps({
  item: { type: Object, default: null },
})
const visible = defineModel({ type: Boolean, default: false })

const t = computed(() => props.item)

const thongTinChung = computed(() => [
  o('Mã trường', t.value.ma_truong),
  o('Tên gọi khác', t.value.ten_goi_khac),
  o('Loại cơ sở', loaiCoSo(t.value)),
  o('Loại hình', t.value.loai_hinh),
  o('Cơ quan chủ quản', t.value.co_quan_chu_quan),
  o('Năm thành lập', t.value.nam_thanh_lap),
  o('Trạng thái hoạt động', t.value.trang_thai_hoat_dong),
])

const daoTao = computed(() => [
  o('Bậc đào tạo', t.value.bac_dao_tao),
  o('Lĩnh vực đào tạo chính', t.value.linh_vuc_dao_tao_chinh),
  o('Lĩnh vực đào tạo khác', t.value.linh_vuc_dao_tao_khac),
  o('Học phí trung bình', t.value.hoc_phi_trung_binh),
])

const lienHe = computed(() => [
  o('Địa chỉ trụ sở', t.value.dia_chi_tru_so),
  o('Tỉnh / thành', t.value.ten_tinh_thanh),
  o('Vùng miền', t.value.vung_mien),
  oLink('Website', t.value.website, 'web'),
  oLink('Email', t.value.email, 'email'),
  oLink('Số điện thoại', t.value.so_dien_thoai, 'tel'),
])

const tuyenSinh = computed(() => [
  oLink('Hotline tuyển sinh', t.value.hotline_tuyen_sinh, 'tel'),
  oLink('Email tuyển sinh', t.value.email_tuyen_sinh, 'email'),
  oLink('Website tuyển sinh', t.value.website_tuyen_sinh, 'web'),
])
</script>
