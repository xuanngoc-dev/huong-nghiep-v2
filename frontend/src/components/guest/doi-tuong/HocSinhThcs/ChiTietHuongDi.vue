<template>
  <section class="thcs py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div v-if="dangTai" class="intro-card thcs__trang-thai" role="status">Đang tải thông tin hướng đi…</div>
          <div v-else-if="loi" class="intro-card thcs__trang-thai">
            {{ loi }}
            <button type="button" class="thcs__thu-lai" @click="taiHuongDi">Thử lại</button>
          </div>
          <div v-else-if="!huong" class="intro-card thcs__trang-thai">
            Không tìm thấy hướng đi có mã “{{ maHuong }}”.
            <RouterLink :to="{ name: goc }">Xem tất cả hướng đi</RouterLink>
          </div>

          <div v-else class="stages-card">
            <RouterLink class="thcs__quay-lai" :to="{ name: goc }">← Tất cả hướng đi</RouterLink>
            <h1 class="thcs__title">{{ huong.ten_huong }}</h1>
            <p class="thcs__van-ban">{{ huong.mo_ta_tong_quan }}</p>

            <dl class="thong-tin-luoi">
              <div v-if="chiPhi(huong)">
                <dt>Chi phí dự kiến</dt>
                <dd>{{ chiPhi(huong) }}</dd>
              </div>
              <div>
                <dt>Áp lực học tập</dt>
                <dd>
                  <span class="muc-do" :class="`muc-do--${mauEnum(MUC_DO_AP_LUC_HOC_TAP, huong.muc_do_ap_luc_hoc_tap)}`">
                    {{ nhanEnum(MUC_DO_AP_LUC_HOC_TAP, huong.muc_do_ap_luc_hoc_tap) }}
                  </span>
                </dd>
              </div>
              <div>
                <dt>Mức tự giác cần có</dt>
                <dd>
                  <span class="muc-do" :class="`muc-do--${mauEnum(MUC_DO_TU_GIAC, huong.muc_do_tu_giac_can_thiet)}`">
                    {{ nhanEnum(MUC_DO_TU_GIAC, huong.muc_do_tu_giac_can_thiet) }}
                  </span>
                </dd>
              </div>
              <div v-if="huong.ma_holland">
                <dt>Nhóm Holland phù hợp</dt>
                <dd>{{ huong.ma_holland }}</dd>
              </div>
            </dl>

            <div class="row g-3 mt-1">
              <div v-if="huong.doi_tuong_phu_hop" class="col-12 col-md-6">
                <div class="ghi-chu-khoi">
                  <h2 class="khoi__title">Phù hợp với ai?</h2>
                  <p class="thcs__van-ban mb-0">{{ huong.doi_tuong_phu_hop }}</p>
                </div>
              </div>
              <div v-if="huong.tinh_linh_hoat_sau_lop_12" class="col-12 col-md-6">
                <div class="ghi-chu-khoi ghi-chu-khoi--xanh">
                  <h2 class="khoi__title">Sau lớp 12 có thể làm gì?</h2>
                  <p class="thcs__van-ban mb-0">{{ huong.tinh_linh_hoat_sau_lop_12 }}</p>
                </div>
              </div>
            </div>

            <div v-if="dangTaiChiTiet" class="thcs__trang-thai" role="status">Đang tải thông tin…</div>
            <div v-else-if="loiChiTiet" class="thcs__trang-thai">
              {{ loiChiTiet }}
              <button type="button" class="thcs__thu-lai" @click="taiChiTiet(huong.id)">Thử lại</button>
            </div>
            <template v-else>
              <div v-if="uuDiem.length || nhuocDiem.length" class="phan">
                <h2 class="phan__title">Ưu điểm và nhược điểm</h2>
                <div class="row g-3">
                  <div class="col-12 col-md-6">
                    <ul class="uu-nhuoc uu-nhuoc--uu" aria-label="Ưu điểm">
                      <li v-for="item in uuDiem" :key="item.id">
                        <span class="uu-nhuoc__dau" aria-hidden="true">+</span>
                        <div>
                          <h3 class="uu-nhuoc__ten">{{ item.tieu_de }}</h3>
                          <p class="thcs__van-ban mb-0">{{ item.noi_dung_chi_tiet }}</p>
                        </div>
                      </li>
                      <li v-if="!uuDiem.length" class="uu-nhuoc__rong">Chưa có ưu điểm.</li>
                    </ul>
                  </div>
                  <div class="col-12 col-md-6">
                    <ul class="uu-nhuoc uu-nhuoc--nhuoc" aria-label="Nhược điểm">
                      <li v-for="item in nhuocDiem" :key="item.id">
                        <span class="uu-nhuoc__dau" aria-hidden="true">−</span>
                        <div>
                          <h3 class="uu-nhuoc__ten">{{ item.tieu_de }}</h3>
                          <p class="thcs__van-ban mb-0">{{ item.noi_dung_chi_tiet }}</p>
                        </div>
                      </li>
                      <li v-if="!nhuocDiem.length" class="uu-nhuoc__rong">Chưa có nhược điểm.</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div v-if="dsDiem.length" class="phan">
                <h2 class="phan__title">Hướng đi này hợp với ai?</h2>
                <p class="phan__lead">Mức phù hợp theo từng tiêu chí, thang 1 - 5.</p>
                <ul class="diem-ds">
                  <li v-for="item in dsDiem" :key="item.thcs_tieu_chi_id" class="diem-ds__dong">
                    <div class="diem-ds__dau">
                      <span class="diem-ds__ten">{{ item.ten_tieu_chi }}</span>
                      <span class="diem-ds__so">{{ item.diem_phu_hop }}/5</span>
                    </div>
                    <div
                      class="diem-ds__thanh"
                      role="meter"
                      :aria-valuenow="item.diem_phu_hop"
                      aria-valuemin="1"
                      aria-valuemax="5"
                      :aria-label="item.ten_tieu_chi"
                    >
                      <span :style="{ width: `${item.diem_phu_hop * 20}%` }"></span>
                    </div>
                    <p v-if="item.nhan_dinh_tu_van" class="diem-ds__nhan-dinh">{{ item.nhan_dinh_tu_van }}</p>
                  </li>
                </ul>
              </div>

              <div v-if="dsLoiKhuyen.length" class="phan">
                <h2 id="loi-khuyen" class="phan__title">Lời khuyên, lưu ý</h2>
                <div class="chip-nhom" role="group" aria-labelledby="loi-khuyen">
                  <button
                    v-for="item in LOC_LOI_KHUYEN"
                    :key="item.value"
                    type="button"
                    class="chip"
                    :class="{ 'is-active': locLoiKhuyen === item.value }"
                    :aria-pressed="locLoiKhuyen === item.value"
                    @click="locLoiKhuyen = item.value"
                  >
                    {{ item.label }}
                  </button>
                </div>
                <ul class="loi-khuyen">
                  <li v-for="item in loiKhuyenDangXem" :key="item.id" class="loi-khuyen__muc">
                    <span class="loi-khuyen__nhan">{{ nhanEnum(DOI_TUONG_NHAN_LUU_Y, item.doi_tuong_nhan) }}</span>
                    <p class="thcs__van-ban mb-0">{{ item.noi_dung_luu_y }}</p>
                  </li>
                  <li v-if="!loiKhuyenDangXem.length" class="uu-nhuoc__rong">Chưa có lời khuyên cho lựa chọn này.</li>
                </ul>
              </div>
            </template>
          </div>

          <div class="d-flex flex-column gap-3 mt-3">
            <HoTroDinhHuong />
            <CauHoiThuongGap />
          </div>
        </div>

        <div class="col-lg-3">
          <nav class="paths-card" aria-labelledby="menu-huong-di">
            <h2 id="menu-huong-di" class="h4 mb-3">Các hướng đi sau THCS</h2>
            <p v-if="!dangTai && !dsHuong.length" class="menu-rong">Chưa có hướng đi.</p>
            <ul class="menu-huong">
              <li v-for="item in dsHuong" :key="item.id">
                <RouterLink
                  class="menu-huong__muc"
                  :class="{ 'is-active': item.id === huong?.id }"
                  :to="{ name: tenRoute('hs-thcs-huong-di'), params: { maHuong: item.ma_huong } }"
                  :aria-current="item.id === huong?.id ? 'page' : undefined"
                >
                  <span class="menu-huong__ten">{{ item.ten_huong }}</span>
                  <span v-if="chiPhi(item)" class="menu-huong__phu">{{ chiPhi(item) }}</span>
                </RouterLink>
              </li>
            </ul>
            <RouterLink class="menu-huong__goi-y" :to="{ name: tenRoute('hs-thcs-tu-danh-gia') }">
              {{ laPhuHuynh ? 'Tìm hướng đi phù hợp với con →' : 'Tìm hướng đi phù hợp với bạn →' }}
            </RouterLink>
          </nav>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { huongDiTieuChiApi, loiKhuyenLuuYApi, uuNhuocDiemApi } from '@/api/thcsHuongDi'
import {
  DOI_TUONG_NHAN_LUU_Y,
  MUC_DO_AP_LUC_HOC_TAP,
  MUC_DO_TU_GIAC,
  mauEnum,
  nhanEnum,
} from '@/constants/thcsHuongDi'
import { useTenRouteThcs } from './useTenRouteThcs'
import { chiPhi, useDsHuongDiThcs } from './thcs'

defineOptions({ name: 'ThcsChiTietHuongDi' })

// Lời khuyên "cả hai" hiện ở cả bộ lọc học sinh lẫn phụ huynh.
const LOC_LOI_KHUYEN = [
  { value: '', label: 'Tất cả' },
  { value: 'hoc_sinh', label: 'Cho học sinh' },
  { value: 'phu_huynh', label: 'Cho phụ huynh' },
]

const route = useRoute()
const { goc, laPhuHuynh, tenRoute } = useTenRouteThcs()
const { dsHuong, dangTai, loi, taiHuongDi } = useDsHuongDiThcs()

const uuNhuoc = ref([])
const dsDiem = ref([])
const dsLoiKhuyen = ref([])
const dangTaiChiTiet = ref(false)
const loiChiTiet = ref('')
// Nhánh phụ huynh mặc định lọc lời khuyên cho phụ huynh.
const locLoiKhuyen = ref(laPhuHuynh.value ? 'phu_huynh' : '')
// Chuyển hướng đi liên tục: chỉ nhận kết quả của lần tải mới nhất.
let lanTai = 0

const maHuong = computed(() => String(route.params.maHuong || '').toUpperCase())
const huong = computed(() => dsHuong.value.find((item) => item.ma_huong === maHuong.value) || null)
const uuDiem = computed(() => uuNhuoc.value.filter((item) => item.loai === 'uu_diem'))
const nhuocDiem = computed(() => uuNhuoc.value.filter((item) => item.loai === 'nhuoc_diem'))
const loiKhuyenDangXem = computed(() =>
  locLoiKhuyen.value
    ? dsLoiKhuyen.value.filter((item) => [locLoiKhuyen.value, 'ca_hai'].includes(item.doi_tuong_nhan))
    : dsLoiKhuyen.value,
)

async function taiChiTiet(id) {
  const lan = ++lanTai
  dangTaiChiTiet.value = true
  loiChiTiet.value = ''
  const params = { thcs_huong_di_id: id, page: 1, page_size: 200 }
  try {
    const [uu, diem, loiKhuyen] = await Promise.all([
      uuNhuocDiemApi.fetch(params),
      huongDiTieuChiApi.fetch(params),
      loiKhuyenLuuYApi.fetch(params),
    ])
    if (lan !== lanTai) return
    uuNhuoc.value = uu.items || []
    dsDiem.value = diem.items || []
    dsLoiKhuyen.value = loiKhuyen.items || []
  } catch {
    if (lan !== lanTai) return
    loiChiTiet.value = 'Không tải được thông tin của hướng đi này.'
  } finally {
    if (lan === lanTai) dangTaiChiTiet.value = false
  }
}

// Đổi hướng đi (qua menu hoặc URL) thì xóa dữ liệu cũ và tải lại.
watch(
  () => huong.value?.id,
  (id) => {
    uuNhuoc.value = []
    dsDiem.value = []
    dsLoiKhuyen.value = []
    locLoiKhuyen.value = ''
    if (id) taiChiTiet(id)
  },
)

onMounted(taiHuongDi)
</script>

<style scoped>
.thcs__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.thcs__trang-thai a {
  margin-left: 6px;
  color: var(--guest-primary);
  font-weight: 500;
}

.thcs__thu-lai {
  margin-left: 8px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.thcs__quay-lai {
  display: inline-block;
  margin-bottom: 8px;
  color: var(--guest-primary);
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
}

.thcs__quay-lai:hover {
  text-decoration: underline;
}

.thcs__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.35;
}

/* Trường Text của danh mục có thể xuống dòng. */
.thcs__van-ban {
  margin: 0 0 12px;
  color: #3a4742;
  font-size: 0.95rem;
  line-height: 1.55;
  white-space: pre-line;
}

.thong-tin-luoi {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
  margin: 0;
  padding: 10px;
  border-radius: var(--guest-radius-sm);
  background: #f6fbf7;
}

.thong-tin-luoi dt {
  color: #6b7780;
  font-size: 0.75rem;
  font-weight: 400;
}

.thong-tin-luoi dd {
  margin: 2px 0 0;
  color: #1c2b23;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
}

.muc-do {
  display: inline-block;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.82rem;
}

.muc-do--success {
  background: #e3f4ea;
  color: #1f7a4d;
}

.muc-do--warning {
  background: #fdf1de;
  color: #a35f00;
}

.muc-do--danger {
  background: #fde7e3;
  color: #b42318;
}

.ghi-chu-khoi {
  height: 100%;
  padding: 14px;
  border: 1px solid #d7eadf;
  border-left: 4px solid var(--guest-primary);
  border-radius: var(--guest-radius);
  background: #fff;
}

.ghi-chu-khoi--xanh {
  border-left-color: #1a66d1;
}

.khoi__title,
.phan__title {
  margin: 0 0 8px;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.35;
}

.phan {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e3efe7;
}

.phan__title {
  font-size: 1.2rem;
}

.phan__lead {
  margin: -4px 0 12px;
  color: #6b7780;
  font-size: 0.875rem;
}

.uu-nhuoc {
  --mau: var(--guest-primary);
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  margin: 0;
  padding: 14px;
  border: 1px solid #d7eadf;
  border-top: 4px solid var(--mau);
  border-radius: var(--guest-radius);
  background: #fff;
  list-style: none;
}

.uu-nhuoc--nhuoc {
  --mau: #c2410c;
}

.uu-nhuoc li {
  display: flex;
  gap: 10px;
}

.uu-nhuoc__dau {
  display: inline-flex;
  flex: 0 0 24px;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--mau);
  color: #fff;
  font-weight: 600;
  line-height: 1;
}

.thcs .uu-nhuoc__ten {
  margin: 1px 0 4px;
  font-size: 0.98rem;
  font-weight: 600;
  line-height: 1.35;
}

.uu-nhuoc__rong {
  color: #6b7780;
  font-size: 0.9rem;
}

.diem-ds {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px 24px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.diem-ds__dau {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 0.92rem;
}

.diem-ds__ten {
  color: #1c2b23;
  font-weight: 500;
}

.diem-ds__so {
  color: var(--guest-primary);
  font-weight: 600;
}

.diem-ds__thanh {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #e3efe7;
}

.diem-ds__thanh span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--guest-primary);
}

.diem-ds__nhan-dinh {
  margin: 4px 0 0;
  color: #6b7780;
  font-size: 0.82rem;
  font-style: italic;
  line-height: 1.4;
}

.chip-nhom {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.chip {
  border: 1px solid rgba(var(--guest-primary-rgb), 0.4);
  border-radius: 999px;
  padding: 6px 14px;
  background: #fff;
  color: var(--guest-primary);
  font-size: 0.875rem;
  line-height: 1.2;
  cursor: pointer;
}

.chip:hover {
  background: rgba(var(--guest-primary-rgb), 0.08);
}

.chip.is-active {
  border-color: var(--guest-primary);
  background: var(--guest-primary);
  color: #fff;
}

.loi-khuyen {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.loi-khuyen__muc {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  padding: 12px 14px;
  border: 1px solid #d7eadf;
  border-left: 4px solid #d98a1c;
  border-radius: var(--guest-radius);
  background: #fff;
}

.loi-khuyen__nhan {
  border: 1px solid #d7eadf;
  border-radius: 999px;
  padding: 2px 8px;
  color: #3a4742;
  font-size: 0.75rem;
}

.menu-huong {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.menu-huong__muc {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid #d7eadf;
  border-left: 4px solid var(--guest-primary);
  border-radius: var(--guest-radius);
  background: #fff;
  text-decoration: none;
  transition: box-shadow 0.3s ease;
}

.menu-huong__muc:hover {
  box-shadow: 0 8px 20px rgba(31, 122, 77, 0.12);
}

.menu-huong__muc.is-active {
  border-color: var(--guest-primary);
  box-shadow: 0 0 0 1px var(--guest-primary);
}

.menu-huong__ten {
  color: var(--guest-primary);
  font-weight: 600;
  line-height: 1.35;
}

.menu-huong__phu,
.menu-rong {
  color: #6b7780;
  font-size: 0.8rem;
}

.menu-huong__goi-y {
  display: block;
  margin-top: 12px;
  border-radius: 999px;
  padding: 8px 14px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
}

.chip:focus-visible,
.thcs__thu-lai:focus-visible,
.thcs__quay-lai:focus-visible,
.menu-huong__muc:focus-visible,
.menu-huong__goi-y:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

@media (max-width: 767.98px) {
  .chip-nhom {
    flex-wrap: nowrap;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .chip {
    flex: 0 0 auto;
  }
}

@media (max-width: 575.98px) {
  .thcs__title {
    font-size: 1.4rem;
  }

  .thcs__van-ban {
    font-size: 0.9rem;
  }
}
</style>
