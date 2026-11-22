<template>
  <CustomDialog v-model="visible" :title="nghe?.ten_nghe || 'Chi tiết nghề'" width="80%" destroy-on-close>
    <!-- Hiển thị dạng form chỉ đọc (nhãn + ô nhập), cùng kiểu với ChiTietNgheCuThe (admin). -->
    <CustomForm v-if="nghe" class="form-grid form-grid--toi-da-4" label-position="top">
      <div class="form-grid__body">
        <template v-for="phan in dsPhan" :key="phan.tieuDe">
          <h3 class="form-grid__full chi-tiet-nghe__tieu-de">{{ phan.tieuDe }}</h3>
          <CustomFormItem v-if="phan.coAnh" class="form-grid__full" label="Hình ảnh mô tả">
            <div class="chi-tiet-nghe__khung-anh">
              <img v-if="anh" :src="anh" :alt="nghe.ten_nghe" />
              <span v-else>Chưa có ảnh</span>
            </div>
          </CustomFormItem>
          <CustomFormItem v-for="o in phan.oNgan" :key="o.label" :label="o.label">
            <CustomInput :model-value="o.giaTri || '—'" readonly />
          </CustomFormItem>
          <CustomFormItem v-for="o in phan.oDai || []" :key="o.key" class="form-grid__full" :label="o.label">
            <CustomInput :model-value="nghe[o.key] || '—'" type="textarea" :rows="4" readonly />
          </CustomFormItem>
        </template>
      </div>
    </CustomForm>

    <template #footer>
      <CustomButton @click="visible = false">Đóng</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/**
 * Modal chi tiết nghề cụ thể ở trang Thư viện ngành nghề (khách).
 * Dữ liệu lấy từ danh sách đã tải, không gọi thêm API. Giao diện nhãn + ô nhập chỉ đọc.
 */
import { computed } from 'vue'
import { MUC_DO_AP_LUC, daiLuong, khoangTrieu } from './nghe'

defineOptions({ name: 'ChiTietNgheModal' })

const props = defineProps({
  nghe: { type: Object, default: null },
  // Nhóm nghề của nghề (lấy lương nhóm khi nghề chưa có lương).
  nhom: { type: Object, default: null },
  // Ảnh đã chọn sẵn (ảnh nghề → ảnh nhóm → ảnh mặc định).
  anh: { type: String, default: '' },
})
const visible = defineModel({ type: Boolean, default: false })

const dsPhan = computed(() => {
  const n = props.nghe
  if (!n) return []
  return [
    {
      tieuDe: 'Thông tin chung',
      oNgan: [
        { label: 'Tên nghề', giaTri: n.ten_nghe },
        { label: 'Nhóm nghề', giaTri: n.ten_nhom },
        { label: 'Lương tham khảo', giaTri: daiLuong(n, props.nhom) },
        { label: 'Mức độ áp lực', giaTri: MUC_DO_AP_LUC[n.muc_do_ap_luc] },
        { label: 'Trình độ tối thiểu', giaTri: n.trinh_do_toi_thieu },
        {
          label: 'Bắt buộc đào tạo chính quy',
          giaTri: Number(n.bat_buoc_dao_tao_chinh_quy) === 1 ? 'Có' : 'Không',
        },
        { label: 'Yêu cầu thêm', giaTri: n.yeu_cau_them },
        { label: 'Bằng cấp / chứng chỉ bắt buộc', giaTri: n.yeu_cau_bang_cap },
      ],
      coAnh: true,
      oDai: [
        { key: 'mo_ta_ngan', label: 'Mô tả ngắn' },
        { key: 'mo_ta_cong_viec', label: 'Mô tả công việc' },
        { key: 'trach_nhiem_chinh', label: 'Trách nhiệm chính' },
        { key: 'vi_tri_tuyen_dung_mau', label: 'Vị trí tuyển dụng mẫu' },
      ],
    },
    {
      tieuDe: 'Đào tạo và kỹ năng',
      oNgan: [{ label: 'Hình thức đào tạo', giaTri: n.hinh_thuc_dao_tao }],
      oDai: [
        { key: 'chuyen_nganh_phu_hop', label: 'Chuyên ngành phù hợp' },
        { key: 'chung_chi_giay_phep', label: 'Chứng chỉ / giấy phép' },
        { key: 'ky_nang_chuyen_mon', label: 'Kỹ năng chuyên môn' },
        { key: 'ky_nang_mem', label: 'Kỹ năng mềm' },
      ],
    },
    {
      tieuDe: 'Lương tham khảo',
      oNgan: [
        { label: 'Khởi điểm', giaTri: khoangTrieu(n, n.luong_khoi_diem_min, n.luong_khoi_diem_max) },
        { label: 'Trung bình', giaTri: khoangTrieu(n, n.luong_trung_binh_min, n.luong_trung_binh_max) },
        { label: 'Mức cao', giaTri: khoangTrieu(n, n.luong_cao_min, n.luong_cao_max) },
        { label: 'Ghi chú lương', giaTri: n.ghi_chu_luong },
      ],
    },
    {
      tieuDe: 'Môi trường và triển vọng',
      oNgan: [
        { label: 'Đặc thù thời gian', giaTri: n.dac_thu_thoi_gian },
        { label: 'Yêu cầu sức khỏe', giaTri: n.yeu_cau_suc_khoe },
      ],
      oDai: [
        { key: 'moi_truong_lam_viec', label: 'Môi trường làm việc' },
        { key: 'trien_vong_nghe_nghiep', label: 'Triển vọng nghề nghiệp' },
        { key: 'lo_trinh_phat_trien', label: 'Lộ trình phát triển' },
      ],
    },
  ]
})
</script>

<style scoped>
.chi-tiet-nghe__tieu-de {
  margin: 8px 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  color: var(--el-text-color-primary);
  font-size: 15px;
  font-weight: 600;
}

.chi-tiet-nghe__tieu-de:first-child {
  margin-top: 0;
}

.chi-tiet-nghe__khung-anh {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 240px;
  max-width: 100%;
  aspect-ratio: 8 / 5;
  overflow: hidden;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  background: var(--el-fill-color-lighter);
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.chi-tiet-nghe__khung-anh img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
