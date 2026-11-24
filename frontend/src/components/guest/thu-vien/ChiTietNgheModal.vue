<template>
  <KhungChiTiet v-model="visible" tieu-de="Chi tiết nghề">
    <template v-if="n" #dau>
      <DauChiTiet
        :tieu-de="n.ten_nghe"
        :phu="n.ten_nhom || ''"
        :anh="anh"
        :anh-logo="false"
        icon="Suitcase"
        :nhan="locNhan([MUC_DO_AP_LUC[n.muc_do_ap_luc], n.trinh_do_toi_thieu, ...nhomHolland])"
      />
    </template>

    <template v-if="n">
      <CardThongTin
        tieu-de="Giới thiệu nghề"
        icon="Document"
        :doan="locNhan([n.mo_ta_ngan, n.mo_ta_cong_viec]).join('\n\n')"
        rong
      />

      <!-- Lương theo 3 bậc; nghề chưa có số thì hiện dải lương của nhóm (daiLuong). -->
      <CardThongTin tieu-de="Lương tham khảo" icon="Money" rong>
        <div v-if="bacLuong.length" class="luong">
          <div v-for="bac in bacLuong" :key="bac.label" class="luong__bac">
            <span>{{ bac.label }}</span>
            <strong>{{ bac.giaTri }}</strong>
          </div>
        </div>
        <p v-else class="luong__chung">{{ daiLuong(n, nhom) }}</p>
        <p v-if="n.ghi_chu_luong" class="luong__ghi-chu">{{ n.ghi_chu_luong }}</p>
      </CardThongTin>

      <CardThongTin tieu-de="Trách nhiệm chính" icon="List" :ds="dsMuc(n.trach_nhiem_chinh)" />
      <CardThongTin tieu-de="Vị trí tuyển dụng" icon="Postcard" :nhan="dsMuc(n.vi_tri_tuyen_dung_mau)" />
      <CardThongTin tieu-de="Yêu cầu đầu vào" icon="Reading" :dong="yeuCau" />
      <CardThongTin tieu-de="Chứng chỉ / giấy phép" icon="Medal" :ds="dsMuc(n.chung_chi_giay_phep)" />
      <CardThongTin tieu-de="Kỹ năng chuyên môn" icon="Tools" :nhan="dsMuc(n.ky_nang_chuyen_mon)" />
      <CardThongTin tieu-de="Kỹ năng mềm" icon="ChatDotRound" :nhan="dsMuc(n.ky_nang_mem)" />
      <CardThongTin tieu-de="Môi trường làm việc" icon="OfficeBuilding" :dong="moiTruong" />
      <CardThongTin tieu-de="Triển vọng nghề nghiệp" icon="TrendCharts" :doan="n.trien_vong_nghe_nghiep" />

      <CardThongTin v-if="loTrinh.length" tieu-de="Lộ trình phát triển" icon="Guide" rong>
        <BuocLoTrinh :buoc="loTrinh" />
      </CardThongTin>
    </template>
  </KhungChiTiet>
</template>

<script setup>
/**
 * Modal chi tiết nghề cụ thể ở trang Thư viện ngành nghề (khách): thông tin gom thành các card,
 * lộ trình phát triển dạng từng bước. Dữ liệu lấy từ danh sách đã tải, không gọi thêm API.
 */
import { computed } from 'vue'
import KhungChiTiet from '@/components/guest/chung/chi-tiet/KhungChiTiet.vue'
import DauChiTiet from '@/components/guest/chung/chi-tiet/DauChiTiet.vue'
import CardThongTin from '@/components/guest/chung/chi-tiet/CardThongTin.vue'
import BuocLoTrinh from '@/components/guest/chung/chi-tiet/BuocLoTrinh.vue'
import { chuanHoaMuc, locNhan, o, tachLoTrinh } from '@/components/guest/chung/chi-tiet/phanChiTiet'
import { NOI_DUNG_NHOM } from '@/utils/ketQuaHolland'
import { MUC_DO_AP_LUC, daiLuong, khoangTrieu, tachDanhSach } from './nghe'

defineOptions({ name: 'ChiTietNgheModal' })

const props = defineProps({
  nghe: { type: Object, default: null },
  // Nhóm nghề của nghề (lấy lương nhóm khi nghề chưa có lương).
  nhom: { type: Object, default: null },
  // Ảnh đã chọn sẵn (ảnh nghề → ảnh nhóm → ảnh mặc định).
  anh: { type: String, default: '' },
})
const visible = defineModel({ type: Boolean, default: false })

const n = computed(() => props.nghe)

// nhom_holland: "R" hoặc "R, I" → "R – Kỹ thuật"…; mã lạ giữ nguyên.
const nhomHolland = computed(() =>
  String(n.value.nhom_holland || '')
    .split(/[^A-Za-z]+/)
    .filter(Boolean)
    .map((m) => m.toUpperCase())
    .map((m) => (NOI_DUNG_NHOM[m] ? `${m} – ${NOI_DUNG_NHOM[m].ten}` : m)),
)

const bacLuong = computed(() =>
  [
    { label: 'Khởi điểm', giaTri: khoangTrieu(n.value, n.value.luong_khoi_diem_min, n.value.luong_khoi_diem_max) },
    { label: 'Trung bình', giaTri: khoangTrieu(n.value, n.value.luong_trung_binh_min, n.value.luong_trung_binh_max) },
    { label: 'Mức cao', giaTri: khoangTrieu(n.value, n.value.luong_cao_min, n.value.luong_cao_max) },
  ].filter((bac) => bac.giaTri),
)

// bat_buoc_dao_tao_chinh_quy: 1 → Có, 0 → Không, chưa khai báo → ẩn.
const batBuocChinhQuy = computed(() => {
  const value = n.value.bat_buoc_dao_tao_chinh_quy
  if (value === null || value === undefined || value === '') return null
  return Number(value) === 1 ? 'Có' : 'Không'
})

const yeuCau = computed(() => [
  o('Trình độ tối thiểu', n.value.trinh_do_toi_thieu),
  o('Bắt buộc đào tạo chính quy', batBuocChinhQuy.value),
  o('Hình thức đào tạo', n.value.hinh_thuc_dao_tao),
  o('Chuyên ngành phù hợp', dsMuc(n.value.chuyen_nganh_phu_hop)),
  o('Bằng cấp bắt buộc', n.value.yeu_cau_bang_cap),
  o('Yêu cầu thêm', n.value.yeu_cau_them),
])

const moiTruong = computed(() => [
  o('Nơi làm việc', n.value.moi_truong_lam_viec),
  o('Thời gian', n.value.dac_thu_thoi_gian),
  o('Mức độ áp lực', MUC_DO_AP_LUC[n.value.muc_do_ap_luc]),
  o('Yêu cầu sức khỏe', n.value.yeu_cau_suc_khoe),
])

// Mảng giai đoạn { giai_doan, mo_ta_cong_viec, luong_trung_binh_min/max, ghi_chu } → bước của BuocLoTrinh.
// Dữ liệu cũ dạng chuỗi "A → B" (API chưa chuyển) thì chỉ có tên bước.
const loTrinh = computed(() => {
  const value = n.value.lo_trinh_phat_trien
  if (!Array.isArray(value)) return tachLoTrinh(value).map(chuanHoaMuc)
  return value
    .filter((buoc) => buoc?.giai_doan)
    .map((buoc) => ({
      tieuDe: buoc.giai_doan,
      chiTiet: [
        { label: 'Mô tả công việc', giaTri: buoc.mo_ta_cong_viec, icon: 'Suitcase', rong: true },
        {
          label: 'Mức lương trung bình',
          giaTri: khoangTrieu(n.value, buoc.luong_trung_binh_min, buoc.luong_trung_binh_max),
          icon: 'Money',
          noiBat: true,
        },
        { label: 'Ghi chú', giaTri: buoc.ghi_chu, icon: 'InfoFilled' },
      ],
    }))
})

// Chuỗi "a; b; c" → mục đã chuẩn hóa (viết hoa đầu, bỏ dấu chấm cuối).
function dsMuc(value) {
  return tachDanhSach(value).map(chuanHoaMuc).filter(Boolean)
}
</script>

<style scoped>
/* Ba bậc lương cạnh nhau, tự xuống hàng khi khung hẹp. */
.luong {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.luong__bac {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid #d7eadf;
  border-radius: 8px;
  background: #f4faf5;
}

.luong__bac span {
  color: var(--el-text-color-secondary);
  font-size: 0.8rem;
}

.luong__bac strong {
  color: #2f7a33;
  font-size: 1rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.luong__chung {
  margin: 0;
  color: #2f7a33;
  font-size: 1rem;
  font-weight: 600;
}

.luong__ghi-chu {
  margin: 10px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 0.82rem;
  font-style: italic;
}
</style>
