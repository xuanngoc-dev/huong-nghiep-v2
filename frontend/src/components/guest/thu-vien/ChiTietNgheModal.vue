<template>
  <CustomDialog v-model="visible" :title="nghe?.ten_nghe || 'Chi tiết nghề'" width="80%" destroy-on-close>
    <article v-if="nghe" class="ct-nghe">
      <header class="ct-nghe__dau">
        <img class="ct-nghe__anh" :src="anh" :alt="nghe.ten_nghe" />
        <div class="ct-nghe__tom-tat">
          <p class="ct-nghe__nhom">{{ nghe.ten_nhom }}</p>
          <p class="ct-nghe__luong">{{ daiLuong(nghe, nhom) }}</p>
          <div class="ct-nghe__nhan">
            <span v-if="Number(nghe.bat_buoc_dao_tao_chinh_quy) === 1" class="ct-nghe__the ct-nghe__the--canh-bao">
              Cần đào tạo chính quy
            </span>
            <span v-if="MUC_DO_AP_LUC[nghe.muc_do_ap_luc]" class="ct-nghe__the">{{ MUC_DO_AP_LUC[nghe.muc_do_ap_luc] }}</span>
            <span v-if="nghe.trinh_do_toi_thieu" class="ct-nghe__the">{{ nghe.trinh_do_toi_thieu }}</span>
          </div>
          <p v-if="nghe.mo_ta_ngan" class="ct-nghe__mo-ta">{{ nghe.mo_ta_ngan }}</p>
        </div>
      </header>

      <!-- Chỉ hiện mục có dữ liệu. -->
      <section v-for="phan in dsPhan" :key="phan.tieuDe" class="ct-nghe__phan">
        <h3 class="ct-nghe__tieu-de">{{ phan.tieuDe }}</h3>
        <template v-for="muc in phan.muc" :key="muc.label">
          <div class="ct-nghe__muc">
            <h4>{{ muc.label }}</h4>
            <ul v-if="muc.danhSach" class="ct-nghe__chip">
              <li v-for="item in muc.danhSach" :key="item">{{ item }}</li>
            </ul>
            <p v-else>{{ muc.giaTri }}</p>
          </div>
        </template>
      </section>
    </article>
  </CustomDialog>
</template>

<script setup>
/**
 * Modal chi tiết nghề cụ thể ở trang Thư viện ngành nghề (khách). Dữ liệu lấy từ danh sách đã tải, không gọi thêm API.
 */
import { computed } from 'vue'
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

function vanBan(label, giaTri) {
  return giaTri ? { label, giaTri } : null
}

function danhSach(label, giaTri) {
  const ds = tachDanhSach(giaTri)
  return ds.length ? { label, danhSach: ds } : null
}

const dsPhan = computed(() => {
  const n = props.nghe
  if (!n) return []
  const luong = [
    vanBan('Khởi điểm', khoangTrieu(n, n.luong_khoi_diem_min, n.luong_khoi_diem_max)),
    vanBan('Trung bình', khoangTrieu(n, n.luong_trung_binh_min, n.luong_trung_binh_max)),
    vanBan('Mức cao', khoangTrieu(n, n.luong_cao_min, n.luong_cao_max)),
    vanBan('Ghi chú', n.ghi_chu_luong),
  ]
  return [
    {
      tieuDe: 'Công việc',
      muc: [
        vanBan('Mô tả công việc', n.mo_ta_cong_viec),
        vanBan('Trách nhiệm chính', n.trach_nhiem_chinh),
        danhSach('Vị trí tuyển dụng', n.vi_tri_tuyen_dung_mau),
      ],
    },
    {
      tieuDe: 'Học gì để làm nghề này',
      muc: [
        vanBan('Hình thức đào tạo', n.hinh_thuc_dao_tao),
        vanBan('Bằng cấp / chứng chỉ bắt buộc', n.yeu_cau_bang_cap),
        danhSach('Chứng chỉ, giấy phép', n.chung_chi_giay_phep),
        danhSach('Chuyên ngành phù hợp', n.chuyen_nganh_phu_hop),
        danhSach('Kỹ năng chuyên môn', n.ky_nang_chuyen_mon),
        danhSach('Kỹ năng mềm', n.ky_nang_mem),
        vanBan('Yêu cầu thêm', n.yeu_cau_them),
      ],
    },
    { tieuDe: 'Lương tham khảo', muc: luong },
    {
      tieuDe: 'Môi trường làm việc',
      muc: [
        vanBan('Nơi làm việc', n.moi_truong_lam_viec),
        vanBan('Thời gian làm việc', n.dac_thu_thoi_gian),
        vanBan('Yêu cầu sức khỏe', n.yeu_cau_suc_khoe),
      ],
    },
    {
      tieuDe: 'Triển vọng',
      muc: [vanBan('Triển vọng nghề nghiệp', n.trien_vong_nghe_nghiep), vanBan('Lộ trình phát triển', n.lo_trinh_phat_trien)],
    },
  ]
    .map((phan) => ({ ...phan, muc: phan.muc.filter(Boolean) }))
    .filter((phan) => phan.muc.length)
})
</script>

<style scoped>
.ct-nghe {
  display: flex;
  flex-direction: column;
  gap: 20px;
  color: #3a4742;
}

.ct-nghe__dau {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.ct-nghe__anh {
  flex: 0 0 240px;
  width: 240px;
  aspect-ratio: 8 / 5;
  object-fit: cover;
  border-radius: var(--guest-radius, 8px);
  background: #e3efe7;
}

.ct-nghe__tom-tat {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.ct-nghe__nhom,
.ct-nghe__luong,
.ct-nghe__mo-ta {
  margin: 0;
}

.ct-nghe__nhom {
  color: var(--guest-primary, #3f9643);
  font-size: 0.9rem;
}

.ct-nghe__luong {
  color: #1c2b23;
  font-size: 1.1rem;
  font-weight: 600;
}

.ct-nghe__mo-ta {
  line-height: 1.6;
}

.ct-nghe__nhan,
.ct-nghe__chip {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ct-nghe__the {
  padding: 2px 10px;
  border-radius: 999px;
  background: #eaf5eb;
  color: #2f7a33;
  font-size: 0.8rem;
}

.ct-nghe__the--canh-bao {
  background: #fff4e5;
  color: #9a5b00;
}

.ct-nghe__phan {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ct-nghe__tieu-de {
  margin: 0;
  padding-bottom: 6px;
  border-bottom: 1px solid #d7eadf;
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 600;
}

.ct-nghe__muc h4 {
  margin: 0 0 4px;
  color: #5b6770;
  font-size: 0.85rem;
  font-weight: 500;
}

.ct-nghe__muc p {
  margin: 0;
  line-height: 1.6;
  white-space: pre-line;
}

.ct-nghe__chip {
  margin: 0;
  padding: 0;
  list-style: none;
}

.ct-nghe__chip li {
  padding: 3px 10px;
  border: 1px solid #d7eadf;
  border-radius: 999px;
  background: #f6fbf7;
  font-size: 0.85rem;
}

/* Mobile: ảnh nằm trên, rộng cả khung. */
@media (max-width: 575.98px) {
  .ct-nghe__dau {
    flex-direction: column;
  }

  .ct-nghe__anh {
    flex-basis: auto;
    width: 100%;
  }
}
</style>
