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
              <h2 class="stages-heading mb-0">Các nghề đi làm phổ biến</h2>
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

            <!-- Nghề của mọi nhóm, bỏ nghề bắt buộc đào tạo chính quy (học sinh không học tiếp);
                 nhóm nghề, mục tiêu, mức lương (theo nhóm) là bộ lọc. -->
            <!-- Từ khóa áp dụng khi bấm Tìm kiếm / Enter / xóa ô; ô chọn nhóm, mức lương lọc ngay khi đổi. -->
            <form class="loc-nhom" role="search" @submit.prevent="timKiem">
              <CustomInput
                v-model="tuKhoaNhap"
                class="loc-nhom__tu-khoa"
                placeholder="Tìm nghề: bán hàng, thợ điện…"
                aria-label="Tìm nghề theo từ khóa"
                clearable
                @clear="timKiem"
              >
                <template #prefix>
                  <CustomIcon><Search /></CustomIcon>
                </template>
              </CustomInput>
              <CustomSelect
                v-model="nhomId"
                class="loc-nhom__chon"
                placeholder="Tất cả nhóm nghề"
                clearable
                filterable
                aria-label="Lọc theo nhóm nghề"
              >
                <CustomOption v-for="nhom in dsNhomNghe" :key="nhom.id" :label="nhom.ten_nhom" :value="nhom.id" />
              </CustomSelect>
              <!-- Để trống = mọi mức lương (Element Plus coi '' là chưa chọn nên dùng placeholder thay cho một lựa chọn).
                   Mức lương tham khảo lấy theo nhóm nghề của từng nghề. -->
              <CustomSelect
                v-model="mucLuong"
                class="loc-nhom__chon"
                placeholder="Mức lương tham khảo"
                clearable
                aria-label="Lọc theo mức lương tham khảo"
              >
                <el-option-group v-for="nhom in MUC_LUONG_THEO_NHOM" :key="nhom.nhom" :label="nhom.nhom">
                  <CustomOption v-for="item in nhom.ds" :key="item.value" :label="item.label" :value="item.value" />
                </el-option-group>
              </CustomSelect>
              <CustomButton type="primary" native-type="submit" class="loc-nhom__nut">
                <CustomIcon><Search /></CustomIcon>
                <span>Tìm kiếm</span>
              </CustomButton>
            </form>

            <div v-if="dangTai" class="nhom-nghe__trang-thai" role="status">Đang tải danh sách nghề…</div>
            <div v-else-if="loi" class="nhom-nghe__trang-thai">
              {{ loi }}
              <button type="button" class="nhom-nghe__thu-lai" @click="taiDuLieu">Thử lại</button>
            </div>
            <div v-else-if="!dsLoc.length" class="nhom-nghe__trang-thai">
              <template v-if="!dsNghe.length">Chưa có dữ liệu nghề.</template>
              <template v-else>
                Không có nghề phù hợp với bộ lọc.
                <button type="button" class="nhom-nghe__thu-lai" @click="xoaBoLoc">Xóa bộ lọc</button>
              </template>
            </div>

            <template v-else>
              <p class="nghe-ds__dem">
                {{ dsLoc.length }} nghề không cần học chính quy
              </p>
              <div class="row g-3">
                <div v-for="nghe in dsTrang" :key="nghe.id" class="col-12 col-md-6">
                  <article class="nghe-item h-100" :class="`nghe-item--${nhomTheoId[nghe.nhom_nghe_di_lam_id]?.nhom_muc_tieu || 'khac'}`">
                    <h3 class="nghe-item__ten">{{ nghe.ten_nghe }}</h3>
                    <RouterLink
                      class="nghe-item__nhom"
                      :to="{ name: tenRoute('thpt-di-lam-nhom-nghe'), params: { maNhom: nghe.ma_nhom } }"
                    >
                      {{ nghe.ten_nhom }}
                    </RouterLink>
                    <p v-if="nghe.mo_ta_ngan" class="nghe-item__mo-ta">{{ nghe.mo_ta_ngan }}</p>
                    <dl class="nghe-item__thong-tin">
                      <div>
                        <dt>Lương khởi điểm (nhóm)</dt>
                        <dd>{{ luongNhom(nghe) }}</dd>
                      </div>
                      <div v-if="nghe.yeu_cau_bang_cap">
                        <dt>Cần có</dt>
                        <dd>{{ nghe.yeu_cau_bang_cap }}</dd>
                      </div>
                      <div v-if="nghe.yeu_cau_them">
                        <dt>Yêu cầu thêm</dt>
                        <dd>{{ nghe.yeu_cau_them }}</dd>
                      </div>
                    </dl>
                  </article>
                </div>
              </div>
              <div v-if="dsLoc.length > SO_NGHE_MOI_TRANG" class="nghe-ds__phan-trang">
                <CustomPagination
                  v-model:current-page="trang"
                  :page-size="SO_NGHE_MOI_TRANG"
                  :total="dsLoc.length"
                  layout="prev, pager, next"
                  background
                />
              </div>
            </template>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { fetchNgheCuTheDiLam, fetchNhomNgheDiLam } from '@/api/nhomNgheDiLam'
import GoiYKhaoSat from './di-lam/GoiYKhaoSat.vue'
import {
  LOAI_HINH_DAU_VAO,
  MUC_LUONG_THEO_NHOM,
  NHOM_MUC_TIEU,
  khoangLuong,
  locNgheCuThe,
} from './di-lam/nhomNghe'
import { DINH_HUONG_THPT_KEY, dinhHuongThptList } from './dinhHuong'
import { routeNameDinhHuongThpt } from './routes'
import { useTenRouteThpt } from './useTenRouteThpt'

defineOptions({ name: 'ThptDiLam' })

const BO_LOC = [{ value: '', label: 'Tất cả' }, ...NHOM_MUC_TIEU]
const SO_NGHE_MOI_TRANG = 10

const { tienTo, tenRoute } = useTenRouteThpt()
const route = useRoute()
const router = useRouter()
const currentDirection = computed(() => route.meta.dinhHuong || '')

// Nhóm nghề đang hoạt động và toàn bộ nghề cụ thể (vài trăm dòng) tải một lần; lọc, phân trang ngay trên trình duyệt
// vì mục tiêu, mức lương là thông tin của nhóm nghề, API nghề cụ thể không lọc được.
const dsNhomNghe = ref([])
const dsNghe = ref([])
const dangTai = ref(false)
const loi = ref('')
const mucTieu = ref('')
// tuKhoaNhap: chữ đang gõ; tuKhoa: từ khóa đã áp dụng (bấm Tìm kiếm / Enter).
const tuKhoaNhap = ref('')
const tuKhoa = ref('')
const nhomId = ref(null)
const mucLuong = ref('')
const trang = ref(1)

const nhomTheoId = computed(() => Object.fromEntries(dsNhomNghe.value.map((nhom) => [nhom.id, nhom])))
const boLoc = computed(() => ({
  tuKhoa: tuKhoa.value || '',
  nhomId: nhomId.value || null,
  mucTieu: mucTieu.value,
  mucLuong: mucLuong.value || '',
}))
const dsLoc = computed(() => locNgheCuThe(dsNghe.value, nhomTheoId.value, boLoc.value))
const dsTrang = computed(() =>
  dsLoc.value.slice((trang.value - 1) * SO_NGHE_MOI_TRANG, trang.value * SO_NGHE_MOI_TRANG),
)

// Đổi bộ lọc thì về trang 1.
watch(boLoc, () => {
  trang.value = 1
})

function luongNhom(nghe) {
  const nhom = nhomTheoId.value[nghe.nhom_nghe_di_lam_id]
  return nhom?.muc_luong_text || (nhom ? khoangLuong(nhom) : '—')
}

function timKiem() {
  tuKhoa.value = (tuKhoaNhap.value || '').trim()
}

function xoaBoLoc() {
  mucTieu.value = ''
  tuKhoaNhap.value = ''
  tuKhoa.value = ''
  nhomId.value = null
  mucLuong.value = ''
}

async function taiDuLieu() {
  dangTai.value = true
  loi.value = ''
  try {
    const [nhom, nghe] = await Promise.all([
      fetchNhomNgheDiLam({ trang_thai: 1, page: 1, page_size: 100 }),
      fetchNgheCuTheDiLam({ page: 1, page_size: 1000 }),
    ])
    dsNhomNghe.value = nhom.items || []
    dsNghe.value = nghe.items || []
  } catch {
    loi.value = 'Không tải được danh sách nghề.'
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

onMounted(taiDuLieu)
</script>

<style scoped>
.di-lam__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 600;
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
  font-weight: 600;
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

.loc-nhom {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.loc-nhom__tu-khoa {
  flex: 1 1 260px;
}

.loc-nhom__nut {
  flex: 0 0 auto;
}

.loc-nhom__chon {
  flex: 0 1 220px;
  min-width: 180px;
}

/* Điện thoại: mỗi ô lọc và nút Tìm kiếm chiếm cả hàng. */
@media (max-width: 575.98px) {
  .loc-nhom__chon,
  .loc-nhom__nut {
    flex: 1 1 100%;
  }
}

.nghe-ds__dem {
  margin: 0 0 8px;
  color: #5b6770;
  font-size: 0.875rem;
}

.nghe-ds__phan-trang {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

/* Thẻ nghề cụ thể: viền trái theo mục tiêu của nhóm nghề. */
.nghe-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px;
  border: 1px solid #d7eadf;
  border-left: 4px solid var(--guest-primary);
  border-radius: var(--guest-radius);
  background: #fff;
}

.nghe-item--kiem_tien_ngay {
  border-left-color: #e08a00;
}

.nghe-item--thu_nhap_dot_pha {
  border-left-color: #2563eb;
}

.nghe-item__ten {
  margin: 0;
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.35;
}

.nghe-item__nhom {
  align-self: flex-start;
  color: var(--guest-primary);
  font-size: 0.85rem;
  text-decoration: none;
}

.nghe-item__nhom:hover {
  text-decoration: underline;
}

.nghe-item__mo-ta {
  margin: 0;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
}

.nghe-item__thong-tin {
  display: grid;
  gap: 4px;
  margin: auto 0 0;
  padding: 8px 10px;
  border-radius: var(--guest-radius-sm);
  background: #f6fbf7;
  font-size: 0.85rem;
}

.nghe-item__thong-tin div {
  display: flex;
  gap: 6px;
}

.nghe-item__thong-tin dt {
  flex-shrink: 0;
  color: #5b6770;
  font-weight: 400;
}

.nghe-item__thong-tin dt::after {
  content: ':';
}

.nghe-item__thong-tin dd {
  margin: 0;
  color: #1c2b23;
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

}

/* Màn rất hẹp: bảng thông tin trong card còn 1 cột. */
</style>
