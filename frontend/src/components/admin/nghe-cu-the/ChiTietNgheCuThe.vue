<template>
  <CustomDialog v-model="visible" title="Chi tiết nghề cụ thể" width="80%" destroy-on-close>
    <!-- Hiển thị dạng form chỉ đọc (nhãn + ô nhập): 4 ô/hàng trên desktop, 2 ô/hàng trên mobile, ô nhiều dòng cả hàng. -->
    <CustomForm v-if="nghe" class="form-grid form-grid--toi-da-4" label-position="top">
      <div class="form-grid__body">
        <template v-for="phan in dsPhan" :key="phan.tieuDe">
          <h3 class="form-grid__full chi-tiet-nghe__tieu-de">{{ phan.tieuDe }}</h3>
          <CustomFormItem v-if="phan.coAnh" class="form-grid__full" label="Hình ảnh mô tả">
            <div class="chi-tiet-nghe__khung-anh">
              <img v-if="nghe.hinh_anh_mo_ta" :src="apiAssetUrl(nghe.hinh_anh_mo_ta)" :alt="nghe.ten_nghe" />
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
      <CustomButton type="primary" @click="emit('sua', nghe)">
        <CustomIcon><Edit /></CustomIcon>
        <span>Sửa</span>
      </CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/**
 * Modal xem chi tiết một nghề cụ thể đi làm (khu quản trị). Bấm "Sửa" phát sự kiện `sua` kèm nghề.
 */
import { computed } from 'vue'
import { Edit } from '@element-plus/icons-vue'
import { apiAssetUrl } from '@/api/apiUrl'
import {
  CHU_KY_LUONG,
  KHOANG_LUONG,
  VAN_BAN_CHUNG,
  VAN_BAN_DAO_TAO,
  VAN_BAN_MOI_TRUONG,
  khoangLuong,
  nhanMucDoApLuc,
} from './truongNghe'

defineOptions({ name: 'ChiTietNgheCuThe' })

const props = defineProps({
  nghe: { type: Object, default: null },
})
const emit = defineEmits(['sua'])
const visible = defineModel({ type: Boolean, default: false })

// Các phần giống form sửa: `oNgan` là ô một dòng (nhãn + giá trị đã định dạng), `oDai` là ô nhiều dòng theo cột dữ liệu.
const dsPhan = computed(() => {
  const nghe = props.nghe
  if (!nghe) return []
  return [
    {
      tieuDe: 'Thông tin chung',
      oNgan: [
        { label: 'Tên nghề', giaTri: nghe.ten_nghe },
        { label: 'Nhóm nghề', giaTri: nghe.ten_nhom && `${nghe.ten_nhom} (${nghe.ma_nhom})` },
        { label: 'Yêu cầu thêm', giaTri: nghe.yeu_cau_them },
        { label: 'Bằng cấp / chứng chỉ bắt buộc', giaTri: nghe.yeu_cau_bang_cap },
        { label: 'Nhóm Holland', giaTri: nghe.nhom_holland },
        { label: 'Mức độ áp lực', giaTri: nhanMucDoApLuc(nghe.muc_do_ap_luc)?.label },
        { label: 'Từ khóa tìm kiếm', giaTri: nghe.tu_khoa_tim_kiem },
        { label: 'Bắt buộc đào tạo chính quy', giaTri: nghe.bat_buoc_dao_tao_chinh_quy ? 'Có' : 'Không' },
      ],
      coAnh: true,
      oDai: [{ key: 'mo_ta_ngan', label: 'Mô tả ngắn' }, ...VAN_BAN_CHUNG],
    },
    {
      tieuDe: 'Đào tạo và kỹ năng',
      oNgan: [
        { label: 'Hình thức đào tạo', giaTri: nghe.hinh_thuc_dao_tao },
        { label: 'Trình độ tối thiểu', giaTri: nghe.trinh_do_toi_thieu },
      ],
      oDai: VAN_BAN_DAO_TAO,
    },
    {
      tieuDe: 'Lương tham khảo',
      oNgan: [
        ...KHOANG_LUONG.map(({ key, label }) => ({ label, giaTri: khoangLuong(nghe, key) })),
        { label: 'Đơn vị tiền tệ', giaTri: nghe.don_vi_tien_te },
        { label: 'Chu kỳ lương', giaTri: CHU_KY_LUONG.find((item) => item.value === nghe.chu_ky_luong)?.label },
        { label: 'Ghi chú lương', giaTri: nghe.ghi_chu_luong },
      ],
    },
    {
      tieuDe: 'Môi trường và triển vọng',
      oNgan: [
        { label: 'Đặc thù thời gian', giaTri: nghe.dac_thu_thoi_gian },
        { label: 'Yêu cầu sức khỏe', giaTri: nghe.yeu_cau_suc_khoe },
      ],
      oDai: VAN_BAN_MOI_TRUONG,
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
