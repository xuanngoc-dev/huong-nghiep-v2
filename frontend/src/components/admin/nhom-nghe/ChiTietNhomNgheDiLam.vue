<template>
  <CustomDialog v-model="visible" title="Chi tiết nhóm nghề đi làm" width="95%" destroy-on-close>
    <!-- Bố cục giống form Thêm/Cập nhật nhóm nghề: cùng lưới (tối đa 4 ô/hàng), thứ tự ô; ô chỉ đọc. -->
    <CustomForm v-if="nhom" class="form-grid form-grid--toi-da-4" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem v-for="o in dsONgan" :key="o.label" :label="o.label">
          <CustomInput :model-value="o.giaTri || '—'" readonly />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Hình ảnh mô tả">
          <div class="chi-tiet-nhom__khung-anh">
            <img v-if="nhom.hinh_anh_mo_ta" :src="apiAssetUrl(nhom.hinh_anh_mo_ta)" :alt="nhom.ten_nhom" />
            <span v-else>Chưa có ảnh</span>
          </div>
        </CustomFormItem>
        <CustomFormItem v-for="o in DS_O_DAI" :key="o.key" class="form-grid__half" :label="o.label">
          <CustomInput :model-value="nhom[o.key] || '—'" type="textarea" :rows="4" readonly />
        </CustomFormItem>
      </div>
    </CustomForm>

    <template #footer>
      <CustomButton @click="visible = false">Đóng</CustomButton>
      <CustomButton type="primary" @click="emit('sua', nhom)">
        <CustomIcon><Edit /></CustomIcon>
        <span>Sửa</span>
      </CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/**
 * Modal xem chi tiết một nhóm nghề đi làm (khu quản trị). Bấm "Sửa" phát sự kiện `sua` kèm nhóm.
 */
import { computed } from 'vue'
import { Edit } from '@element-plus/icons-vue'
import { apiAssetUrl } from '@/api/apiUrl'
import { LOAI_HINH_DAU_VAO, MUC_GIOI_THIEU, NHOM_MUC_TIEU } from './truongNhomNghe'

defineOptions({ name: 'ChiTietNhomNgheDiLam' })

const props = defineProps({
  nhom: { type: Object, default: null },
})
const emit = defineEmits(['sua'])
const visible = defineModel({ type: Boolean, default: false })

// Ô nhiều dòng: theo đúng thứ tự trong form.
const DS_O_DAI = [
  { key: 'mo_ta_dac_diem', label: 'Mô tả đặc điểm' },
  { key: 'dieu_kien_dau_vao', label: 'Điều kiện đầu vào' },
  { key: 'lo_trinh_phat_trien', label: 'Lộ trình phát triển' },
  ...MUC_GIOI_THIEU,
]

function nhan(ds, value) {
  return ds.find((item) => item.value === value)?.label
}

// Decimal từ API là chuỗi ("7.00"): bỏ phần thập phân thừa.
function so(value) {
  return value == null || value === '' ? '' : Number(value).toLocaleString('vi-VN')
}

const dsONgan = computed(() => {
  const nhom = props.nhom
  if (!nhom) return []
  return [
    { label: 'Mã nhóm', giaTri: nhom.ma_nhom },
    { label: 'Tên nhóm', giaTri: nhom.ten_nhom },
    { label: 'Loại hình đầu vào', giaTri: nhan(LOAI_HINH_DAU_VAO, nhom.loai_hinh_dau_vao) },
    { label: 'Nhóm mục tiêu', giaTri: nhan(NHOM_MUC_TIEU, nhom.nhom_muc_tieu) },
    { label: 'Mã Holland', giaTri: nhom.ma_holland },
    { label: 'Thời gian đào tạo (mô tả)', giaTri: nhom.thoi_gian_dao_tao_text },
    { label: 'Đào tạo tối thiểu (tháng)', giaTri: so(nhom.thoi_gian_dao_tao_thang_min) },
    { label: 'Đào tạo tối đa (tháng)', giaTri: so(nhom.thoi_gian_dao_tao_thang_max) },
    { label: 'Trạng thái', giaTri: nhom.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' },
    { label: 'Mức lương (mô tả)', giaTri: nhom.muc_luong_text },
    { label: 'Lương khởi điểm từ (triệu)', giaTri: so(nhom.luong_khoi_diem_min) },
    { label: 'Lương khởi điểm đến (triệu)', giaTri: so(nhom.luong_khoi_diem_max) },
    { label: 'Lương tối đa (triệu)', giaTri: so(nhom.luong_kinh_nghiem_max) },
    { label: 'Đánh giá triển vọng', giaTri: nhom.danh_gia_trien_vong },
  ]
})
</script>

<style scoped>
.chi-tiet-nhom__khung-anh {
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

.chi-tiet-nhom__khung-anh img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
