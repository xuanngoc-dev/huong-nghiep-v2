<template>
  <KhungChiTiet v-model="visible" tieu-de="Chi tiết bài thi đánh giá năng lực">
    <template v-if="b" #dau>
      <DauChiTiet
        :tieu-de="b.ten_bai_thi"
        :phu="b.ten_chi_tiet || ''"
        icon="EditPen"
        :ma="b.ten_viet_tat || b.ma_bai_thi || ''"
        :nhan="locNhan([LOAI_CHUNG_CHI[b.loai_chung_chi], b.loai_danh_gia, b.don_vi_to_chuc])"
        :loi-tat="loiTat([
          { label: 'Website chính thức', url: b.website_chinh_thuc },
          { label: 'Nguồn dữ liệu', url: b.nguon_du_lieu_url },
        ])"
      />
    </template>

    <template v-if="b">
      <CardThongTin tieu-de="Giới thiệu" icon="Document" :doan="b.mo_ta" rong />
      <CardThongTin tieu-de="Thông tin chung" icon="Postcard" :dong="thongTinChung" />
      <CardThongTin tieu-de="Hình thức và điểm" icon="DataAnalysis" :dong="hinhThucVaDiem" />

      <CardThongTin v-if="cauTruc.length" tieu-de="Cấu trúc bài thi" icon="List" rong>
        <div class="cau-truc">
          <table>
            <thead>
              <tr>
                <th scope="col">Phần thi</th>
                <th scope="col">Số câu</th>
                <th scope="col">Thời lượng</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(phan, i) in cauTruc" :key="i">
                <td>{{ phan.phan }}</td>
                <td>{{ coGiaTri(phan.so_cau) ? phan.so_cau : '—' }}</td>
                <td>{{ coGiaTri(phan.thoi_luong_phut) ? `${phan.thoi_luong_phut} phút` : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardThongTin>

      <CardThongTin tieu-de="Lưu ý" icon="WarningFilled" :doan="b.ghi_chu" rong luu-y />
    </template>
  </KhungChiTiet>
</template>

<script setup>
/** Modal chi tiết bài thi đánh giá năng lực ở trang Tra cứu (khách). Dữ liệu lấy từ danh sách đã tải, không gọi thêm API. */
import { computed } from 'vue'
import KhungChiTiet from '@/components/guest/chung/chi-tiet/KhungChiTiet.vue'
import DauChiTiet from '@/components/guest/chung/chi-tiet/DauChiTiet.vue'
import CardThongTin from '@/components/guest/chung/chi-tiet/CardThongTin.vue'
import { LOAI_CHUNG_CHI, coGiaTri, khoangNam, locNhan, loiTat, o } from '@/components/guest/chung/chi-tiet/phanChiTiet'

defineOptions({ name: 'ChiTietBaiThiModal' })

const props = defineProps({
  item: { type: Object, default: null },
})
const visible = defineModel({ type: Boolean, default: false })

const b = computed(() => props.item)

const thongTinChung = computed(() => [
  o('Đơn vị tổ chức', b.value.don_vi_to_chuc),
  o('Lĩnh vực', b.value.linh_vuc),
  o('Loại đánh giá', b.value.loai_danh_gia),
  o('Đối tượng dự thi', b.value.doi_tuong_du_thi),
  o('Năm áp dụng', khoangNam(b.value.nam_ap_dung_tu, b.value.nam_ap_dung_den)),
  o('Trạng thái', b.value.trang_thai),
])

const hinhThucVaDiem = computed(() => [
  o('Môn thi', b.value.mon),
  o('Hình thức thi', b.value.hinh_thuc_thi),
  o('Thời lượng', b.value.thoi_luong_phut, { donVi: 'phút' }),
  o('Thang điểm', b.value.thang_diem, { donVi: b.value.don_vi_diem || '' }),
  o('Cách công bố kết quả', b.value.cach_cong_bo_ket_qua),
])

const cauTruc = computed(() =>
  Array.isArray(b.value.cau_truc_bai_thi) ? b.value.cau_truc_bai_thi.filter((phan) => coGiaTri(phan?.phan)) : [],
)
</script>

<style scoped>
/* Bảng cuộn ngang trong card khi khung hẹp, không đẩy rộng dialog. */
.cau-truc {
  overflow-x: auto;
}

.cau-truc table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.cau-truc th,
.cau-truc td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  text-align: left;
}

.cau-truc th {
  background: #f4faf5;
  color: #2f7a33;
  font-weight: 600;
  white-space: nowrap;
}

.cau-truc td:not(:first-child),
.cau-truc th:not(:first-child) {
  width: 120px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
</style>
