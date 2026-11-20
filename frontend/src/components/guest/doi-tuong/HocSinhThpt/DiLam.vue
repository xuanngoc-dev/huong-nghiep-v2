<template>
  <section class="di-lam py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <article class="intro-card mb-3">
            <h1 class="di-lam__title">Đi làm ngay sau khi tốt nghiệp</h1>
            <p class="di-lam__lead">
              Không phải ai cũng cần học đại học mới thành công. Đi làm sớm giúp bạn có thu nhập, tự lập và tích lũy
              kinh nghiệm thực tế trong khi bạn bè còn ngồi trên giảng đường. Điều quan trọng là chọn đúng nhóm nghề
              hợp với sở thích, sức khỏe và mục tiêu của bản thân.
            </p>

            <div class="row g-3">
              <!-- 3 ô / hàng trên màn rộng; 2 ô / hàng thì ô cuối trải hết hàng; mobile 1 ô / hàng. -->
              <div
                v-for="(item, index) in LOAI_HINH_DAU_VAO"
                :key="item.value"
                class="col-12 col-xl-4"
                :class="index < LOAI_HINH_DAU_VAO.length - 1 ? 'col-sm-6' : 'col-sm-12'"
              >
                <div class="loi-vao h-100">
                  <h2 class="loi-vao__title">{{ item.label }}</h2>
                  <p class="loi-vao__text">{{ item.moTa }}</p>
                </div>
              </div>
            </div>

            <div class="row g-3 mt-1">
              <div class="col-12 col-md-6">
                <div class="can-nhac can-nhac--uu">
                  <h2 class="can-nhac__title">Ưu điểm</h2>
                  <ul class="can-nhac__list">
                    <li>Có thu nhập sớm, giảm gánh nặng chi phí học tập cho gia đình.</li>
                    <li>Va chạm thực tế, biết mình thích gì trước khi quyết định học tiếp.</li>
                    <li>Nhiều nghề tăng lương nhanh theo tay nghề, không phụ thuộc bằng cấp.</li>
                  </ul>
                </div>
              </div>
              <div class="col-12 col-md-6">
                <div class="can-nhac can-nhac--luu-y">
                  <h2 class="can-nhac__title">Cần lưu ý</h2>
                  <ul class="can-nhac__list">
                    <li>Lương khởi điểm thường thấp, cần kiên trì 1-3 năm để lên tay nghề.</li>
                    <li>Một số nghề đòi hỏi sức khỏe, làm ca hoặc làm ngoài trời.</li>
                    <li>Nên học thêm chứng chỉ, kỹ năng để không bị “kẹt” ở vị trí phổ thông.</li>
                  </ul>
                </div>
              </div>
            </div>
          </article>

          <div class="stages-card">
            <div class="nhom-nghe__head">
              <h2 class="stages-heading mb-0">Các nhóm nghề đi làm phổ biến</h2>
              <div class="loc-muc-tieu" role="group" aria-label="Lọc theo mục tiêu">
                <button
                  v-for="item in BO_LOC"
                  :key="item.value"
                  type="button"
                  class="loc-muc-tieu__nut"
                  :class="{ 'is-active': mucTieu === item.value }"
                  :aria-pressed="mucTieu === item.value"
                  @click="mucTieu = item.value"
                >
                  {{ item.label }}
                </button>
              </div>
            </div>

            <div v-if="dangTai" class="nhom-nghe__trang-thai" role="status">Đang tải danh sách nhóm nghề…</div>
            <div v-else-if="loi" class="nhom-nghe__trang-thai">
              {{ loi }}
              <button type="button" class="nhom-nghe__thu-lai" @click="taiNhomNghe">Thử lại</button>
            </div>
            <div v-else-if="!dsHienThi.length" class="nhom-nghe__trang-thai">
              {{ dsNhomNghe.length ? 'Chưa có nhóm nghề nào cho mục tiêu này.' : 'Chưa có dữ liệu nhóm nghề.' }}
            </div>

            <div v-else class="row g-3">
              <div v-for="nhom in dsHienThi" :key="nhom.id" class="col-12 col-md-6">
                <article class="nhom-nghe-card h-100" :class="`nhom-nghe-card--${nhom.nhom_muc_tieu || 'khac'}`">
                  <div class="nhom-nghe-card__tags">
                    <span v-if="nhom.nhom_muc_tieu" class="nhom-nghe-card__muc-tieu">
                      {{ nhan(NHOM_MUC_TIEU, nhom.nhom_muc_tieu) }}
                    </span>
                    <span v-if="nhom.loai_hinh_dau_vao" class="nhom-nghe-card__loai">
                      {{ nhan(LOAI_HINH_DAU_VAO, nhom.loai_hinh_dau_vao) }}
                    </span>
                  </div>
                  <h3 class="nhom-nghe-card__ten">{{ nhom.ten_nhom }}</h3>
                  <p class="nhom-nghe-card__mo-ta">{{ nhom.mo_ta_dac_diem }}</p>

                  <dl class="nhom-nghe-card__thong-tin">
                    <div>
                      <dt>Đào tạo</dt>
                      <dd>{{ nhom.thoi_gian_dao_tao_text || thoiGianDaoTao(nhom) }}</dd>
                    </div>
                    <div>
                      <dt>Lương khởi điểm</dt>
                      <dd>{{ nhom.muc_luong_text || khoangLuong(nhom) }}</dd>
                    </div>
                    <div v-if="nhom.luong_kinh_nghiem_max != null">
                      <dt>Khi có kinh nghiệm</dt>
                      <dd>tới {{ soTrieu(nhom.luong_kinh_nghiem_max) }} triệu/tháng</dd>
                    </div>
                    <div v-if="nhom.ma_holland">
                      <dt>Nhóm Holland</dt>
                      <dd>{{ nhom.ma_holland }}</dd>
                    </div>
                  </dl>

                  <p v-if="nhom.danh_gia_trien_vong" class="nhom-nghe-card__trien-vong">
                    {{ nhom.danh_gia_trien_vong }}
                  </p>

                  <div v-if="moRong[nhom.id]" :id="`chi-tiet-${nhom.id}`" class="nhom-nghe-card__chi-tiet">
                    <p v-if="nhom.dieu_kien_dau_vao">
                      <strong>Điều kiện đầu vào:</strong> {{ nhom.dieu_kien_dau_vao }}
                    </p>
                    <p v-if="nhom.lo_trinh_phat_trien">
                      <strong>Lộ trình phát triển:</strong> {{ nhom.lo_trinh_phat_trien }}
                    </p>
                  </div>

                  <div class="nhom-nghe-card__chan">
                    <button
                      v-if="nhom.dieu_kien_dau_vao || nhom.lo_trinh_phat_trien"
                      type="button"
                      class="nhom-nghe-card__xem-them"
                      :aria-expanded="!!moRong[nhom.id]"
                      :aria-controls="`chi-tiet-${nhom.id}`"
                      @click="moRong[nhom.id] = !moRong[nhom.id]"
                    >
                      {{ moRong[nhom.id] ? 'Thu gọn' : 'Điều kiện & lộ trình' }}
                    </button>
                    <RouterLink
                      class="nhom-nghe-card__chi-tiet-link"
                      :to="{ name: tenRoute('thpt-di-lam-nhom-nghe'), params: { maNhom: nhom.ma_nhom } }"
                      :aria-label="`Chi tiết nhóm nghề ${nhom.ten_nhom}`"
                    >
                      Chi tiết
                    </RouterLink>
                  </div>
                </article>
              </div>
            </div>
          </div>

          <div class="d-flex flex-column gap-3 mt-3">
            <GoiYKhaoSat />
            <HoTroDinhHuong />
            <CauHoiThuongGap />
          </div>
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="chon-huong-di" class="h4 mb-3">Một số hướng đi khác cho bạn.</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-huong-di">
              <button
                v-for="item in dinhHuongThptList"
                :key="item.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': currentDirection === item.code, 'is-locked': !item.moTruyCap }"
                :disabled="!item.moTruyCap"
                @click="chonHuong(item)"
              >
                <img class="switch-card__image" :src="item.image" :alt="item.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">
                    {{ item.name }}
                    <span v-if="!item.moTruyCap" class="sap-ra-mat sap-ra-mat--inline">Sắp ra mắt</span>
                  </span>
                  <span class="switch-card__text">{{ item.description }}</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { fetchNhomNgheDiLam } from '@/api/nhomNgheDiLam'
import GoiYKhaoSat from './di-lam/GoiYKhaoSat.vue'
import { LOAI_HINH_DAU_VAO, NHOM_MUC_TIEU, khoangLuong, nhan, soTrieu, thoiGianDaoTao } from './di-lam/nhomNghe'
import { DINH_HUONG_THPT_KEY, dinhHuongThptList } from './dinhHuong'
import { routeNameDinhHuongThpt } from './routes'
import { useTenRouteThpt } from './useTenRouteThpt'

defineOptions({ name: 'ThptDiLam' })

const BO_LOC = [{ value: '', label: 'Tất cả' }, ...NHOM_MUC_TIEU]

const { tienTo, tenRoute } = useTenRouteThpt()
const route = useRoute()
const router = useRouter()
const currentDirection = computed(() => route.meta.dinhHuong || '')

const dsNhomNghe = ref([])
const dangTai = ref(false)
const loi = ref('')
const mucTieu = ref('')
const moRong = reactive({})

const dsHienThi = computed(() =>
  mucTieu.value ? dsNhomNghe.value.filter((nhom) => nhom.nhom_muc_tieu === mucTieu.value) : dsNhomNghe.value,
)

async function taiNhomNghe() {
  dangTai.value = true
  loi.value = ''
  try {
    const data = await fetchNhomNgheDiLam({ trang_thai: 1, page: 1, page_size: 100 })
    dsNhomNghe.value = data.items || []
  } catch {
    loi.value = 'Không tải được danh sách nhóm nghề.'
  } finally {
    dangTai.value = false
  }
}

function chonHuong(direction) {
  if (!direction.moTruyCap) return
  sessionStorage.setItem(DINH_HUONG_THPT_KEY, direction.code)
  const name = routeNameDinhHuongThpt(direction.code, tienTo.value)
  if (name && name !== route.name) router.push({ name })
}

onMounted(taiNhomNghe)
</script>

<style scoped>
.di-lam__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.35;
}

.di-lam__lead {
  margin: 0 0 16px;
  color: #3a4742;
  line-height: 1.6;
}

.loi-vao {
  padding: 14px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius);
  background: #fff;
}

.loi-vao__title,
.can-nhac__title {
  margin: 0 0 6px;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.loi-vao__text {
  margin: 0;
  color: #3a4742;
  font-size: 0.95rem;
  line-height: 1.5;
}

.can-nhac {
  height: 100%;
  padding: 14px;
  border-radius: var(--guest-radius);
  background: #fff;
}

.can-nhac--uu {
  border-left: 4px solid var(--guest-primary);
}

.can-nhac--luu-y {
  border-left: 4px solid #d98a1c;
}

.di-lam .can-nhac--luu-y .can-nhac__title {
  color: #b36b0c;
}

.can-nhac__list {
  margin: 0;
  padding-left: 18px;
  color: #3a4742;
  font-size: 0.95rem;
  line-height: 1.55;
}

.nhom-nghe__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.loc-muc-tieu {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.loc-muc-tieu__nut {
  border: 1px solid rgba(var(--guest-primary-rgb), 0.4);
  border-radius: 999px;
  padding: 6px 14px;
  background: #fff;
  color: var(--guest-primary);
  font-size: 0.875rem;
  line-height: 1.2;
  cursor: pointer;
}

.loc-muc-tieu__nut:hover {
  background: rgba(var(--guest-primary-rgb), 0.08);
}

.loc-muc-tieu__nut.is-active {
  border-color: var(--guest-primary);
  background: var(--guest-primary);
  color: #fff;
}

.loc-muc-tieu__nut:focus-visible,
.nhom-nghe-card__xem-them:focus-visible,
.nhom-nghe__thu-lai:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

.nhom-nghe__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.nhom-nghe__thu-lai {
  margin-left: 8px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.nhom-nghe-card {
  --mau-muc-tieu: var(--guest-primary);
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  border: 1px solid #d7eadf;
  border-top: 4px solid var(--mau-muc-tieu);
  border-radius: var(--guest-radius);
  background: #fff;
  transition: box-shadow 0.3s ease;
}

.nhom-nghe-card:hover {
  box-shadow: 0 16px 32px rgba(31, 122, 77, 0.14);
}

.nhom-nghe-card--kiem_tien_ngay {
  --mau-muc-tieu: #d98a1c;
}

.nhom-nghe-card--thu_nhap_dot_pha {
  --mau-muc-tieu: #1a66d1;
}

.nhom-nghe-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.nhom-nghe-card__muc-tieu,
.nhom-nghe-card__loai {
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 0.78rem;
  line-height: 1.3;
}

.nhom-nghe-card__muc-tieu {
  background: var(--mau-muc-tieu);
  color: #fff;
}

.nhom-nghe-card__loai {
  border: 1px solid #d7eadf;
  color: #3a4742;
}

.di-lam .nhom-nghe-card__ten {
  margin: 0;
  color: var(--guest-primary);
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1.35;
}

.nhom-nghe-card__mo-ta {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: #3a4742;
  font-size: 0.95rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
}

.nhom-nghe-card__thong-tin {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin: 0;
  padding: 10px;
  border-radius: var(--guest-radius-sm);
  background: #f6fbf7;
}

.nhom-nghe-card__thong-tin dt {
  color: #6b7780;
  font-size: 0.75rem;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.nhom-nghe-card__thong-tin dd {
  margin: 2px 0 0;
  color: #1c2b23;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.35;
}

.nhom-nghe-card__trien-vong {
  margin: 0;
  padding-left: 10px;
  border-left: 3px solid var(--mau-muc-tieu);
  color: #3a4742;
  font-size: 0.9rem;
  font-style: italic;
  line-height: 1.45;
}

.nhom-nghe-card__chi-tiet p {
  margin: 0 0 6px;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
}

.nhom-nghe-card__chan {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: auto;
}

.nhom-nghe-card__chi-tiet-link {
  margin-left: auto;
  border-radius: var(--guest-radius);
  padding: 7px 16px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.2;
  text-decoration: none;
}

.nhom-nghe-card__chi-tiet-link:hover {
  background: var(--guest-primary-hover);
  color: #fff;
}

.nhom-nghe-card__chi-tiet-link:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

.nhom-nghe-card__xem-them {
  border: 0;
  padding: 0;
  background: none;
  color: var(--guest-primary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
}

.nhom-nghe-card__xem-them:hover {
  text-decoration: underline;
}

@media (max-width: 767.98px) {
  .nhom-nghe__head {
    flex-direction: column;
    align-items: stretch;
  }

  /* Nút lọc cuộn ngang thay vì xuống nhiều dòng. */
  .loc-muc-tieu {
    flex-wrap: nowrap;
    overflow-x: auto;
    margin: 0 -15px;
    padding: 0 15px 4px;
    scrollbar-width: none;
  }

  .loc-muc-tieu::-webkit-scrollbar {
    display: none;
  }

  .loc-muc-tieu__nut {
    flex: 0 0 auto;
  }
}

@media (max-width: 575.98px) {
  .di-lam__title {
    font-size: 1.4rem;
  }

  .di-lam__lead,
  .loi-vao__text,
  .can-nhac__list {
    font-size: 0.9rem;
  }

  .di-lam .stages-heading {
    font-size: 1.2rem;
  }

  .nhom-nghe-card {
    padding: 14px;
  }

  .di-lam .nhom-nghe-card__ten {
    font-size: 1.1rem;
  }
}

/* Màn rất hẹp: bảng thông tin trong card còn 1 cột. */
@media (max-width: 359.98px) {
  .nhom-nghe-card__thong-tin {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
