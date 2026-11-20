<template>
  <section class="quiz-flow nghe-phu-hop py-4">
    <div class="container-fluid">
      <div class="holland-overview">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Nhóm nghề đi làm phù hợp với bạn</h2>
          <p class="holland-overview__lead">
            Gợi ý dựa trên nhóm tính cách Holland nổi trội từ bài trắc nghiệm của bạn.
          </p>
        </header>

        <p v-if="dangTai" class="holland-overview__lead text-center" role="status">Đang phân tích kết quả…</p>
        <p v-else-if="loi" class="holland-note holland-note__text">
          {{ loi }}
          <button type="button" class="nghe-phu-hop__thu-lai" @click="taiKetQua">Thử lại</button>
        </p>

        <template v-else-if="ketQua">
          <BuocLamBai :ssid="ssid" :buoc="buoc" hien-tai="nhom-nghe-phu-hop" />

          <article v-if="!ketQua.da_xong" class="holland-note mt-4">
            <h3 class="holland-note__title">Bạn chưa hoàn thành bài trắc nghiệm</h3>
            <p class="holland-note__text">Trả lời hết các câu hỏi để kết quả gợi ý được chính xác.</p>
            <RouterLink
              v-if="buocChuaXong"
              class="btn btn-success btn-sm mt-2"
              :to="{ name: tenRoute('thpt-di-lam-lam-trac-nghiem'), params: { ssid, loaiCauHoiId: buocChuaXong.id } }"
            >
              Tiếp tục làm bài
            </RouterLink>
          </article>

          <div class="row g-3 mt-2">
            <div class="col-12 col-lg-4">
              <article class="holland-panel h-100 tinh-cach">
                <p class="holland-kicker">Nhóm tính cách nổi trội</p>
                <div v-if="ketQua.ma_noi_bat" class="tinh-cach__ma" :aria-label="`Mã Holland ${ketQua.ma_noi_bat}`">
                  <span v-for="chu in ketQua.ma_noi_bat" :key="chu">{{ chu }}</span>
                </div>
                <p v-else class="holland-note__text">Chưa đủ dữ liệu để xác định.</p>
                <ul class="tinh-cach__ds">
                  <li v-for="item in ketQua.nhom" :key="item.ma_nhom">
                    <div class="tinh-cach__dong">
                      <span><strong>{{ item.ma_nhom }}</strong> · {{ item.ten_nhom }}</span>
                      <span class="tinh-cach__diem">{{ item.diem }}</span>
                    </div>
                    <div class="tinh-cach__thanh" aria-hidden="true">
                      <span :style="{ width: `${phanTram(item.diem)}%` }" />
                    </div>
                  </li>
                </ul>
              </article>
            </div>

            <div class="col-12 col-lg-8">
              <div v-if="!ketQua.nhom_nghe.length" class="holland-panel h-100 nghe-phu-hop__rong">
                Chưa có nhóm nghề đi làm khớp với kết quả của bạn.
                <RouterLink :to="{ name: tenRoute('thpt-di-lam') }">Xem tất cả nhóm nghề</RouterLink>
              </div>
              <div v-else class="d-flex flex-column gap-3">
                <article
                  v-for="(nhom, index) in ketQua.nhom_nghe"
                  :key="nhom.id"
                  class="goi-y-card"
                  :class="{ 'goi-y-card--top': index < 3 }"
                >
                  <span class="goi-y-card__hang" aria-hidden="true">{{ index + 1 }}</span>
                  <div class="goi-y-card__noi-dung">
                    <div class="goi-y-card__tags">
                      <span v-if="index < 3" class="goi-y-card__nhan-top">Phù hợp nhất</span>
                      <span v-if="nhom.nhom_muc_tieu" class="goi-y-card__tag">
                        {{ nhan(NHOM_MUC_TIEU, nhom.nhom_muc_tieu) }}
                      </span>
                      <span v-if="nhom.loai_hinh_dau_vao" class="goi-y-card__tag">
                        {{ nhan(LOAI_HINH_DAU_VAO, nhom.loai_hinh_dau_vao) }}
                      </span>
                    </div>
                    <h3 class="goi-y-card__ten">{{ nhom.ten_nhom }}</h3>
                    <p class="goi-y-card__mo-ta">{{ nhom.mo_ta_dac_diem }}</p>
                    <dl class="goi-y-card__thong-tin">
                      <div>
                        <dt>Holland</dt>
                        <dd class="goi-y-card__holland">
                          <span
                            v-for="chu in nhom.ma_holland || ''"
                            :key="chu"
                            :class="{ 'is-khop': nhom.ma_khop.includes(chu) }"
                            >{{ chu }}</span
                          >
                        </dd>
                      </div>
                      <div>
                        <dt>Đào tạo</dt>
                        <dd>{{ nhom.thoi_gian_dao_tao_text || thoiGianDaoTao(nhom) }}</dd>
                      </div>
                      <div>
                        <dt>Lương khởi điểm</dt>
                        <dd>{{ nhom.muc_luong_text || khoangLuong(nhom) }}</dd>
                      </div>
                    </dl>
                  </div>
                  <RouterLink
                    class="goi-y-card__chi-tiet"
                    :to="{ name: tenRoute('thpt-di-lam-nhom-nghe'), params: { maNhom: nhom.ma_nhom } }"
                    :aria-label="`Chi tiết nhóm nghề ${nhom.ten_nhom}`"
                  >
                    Chi tiết
                  </RouterLink>
                </article>
              </div>
            </div>
          </div>

          <article class="holland-note mt-3">
            <h3 class="holland-note__title">Lưu ý:</h3>
            <p class="holland-note__text">
              Kết quả chỉ mang tính tham khảo. Hãy cân nhắc thêm sức khỏe, hoàn cảnh và mục tiêu thu nhập của bạn
              khi chọn nghề.
              <RouterLink :to="{ name: tenRoute('thpt-di-lam') }">Xem tất cả nhóm nghề đi làm</RouterLink>
            </p>
          </article>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchNhomNghePhuHop } from '@/api/phienKhaoSat'
import BuocLamBai from '../thi-dai-hoc/lam-trac-nghiem/BuocLamBai.vue'
import { useLuongKhaoSat } from '../luongKhaoSat'
import { useTenRouteThpt } from '../useTenRouteThpt'
import { LOAI_HINH_DAU_VAO, NHOM_MUC_TIEU, khoangLuong, nhan, thoiGianDaoTao } from './nhomNghe'

defineOptions({ name: 'ThptDiLamNhomNghePhuHop' })

const route = useRoute()
const { tenRoute } = useTenRouteThpt()
const { luong } = useLuongKhaoSat()

const ssid = computed(() => String(route.params.ssid || ''))
const ketQua = ref(null)
const dangTai = ref(false)
const loi = ref('')

// API trả các phần câu hỏi đã làm; phiên đã xong thì mọi phần đều xong.
const buoc = computed(() => [
  ...(ketQua.value?.buoc || []).map((item) => ({ id: item.id, ten: item.ten, xong: !!ketQua.value?.da_xong })),
  ...luong.value.buocCuoi.map(({ id, ten }) => ({ id, ten, xong: false })),
])
const buocChuaXong = computed(() => ketQua.value?.buoc?.[0] || null)
const diemCaoNhat = computed(() => Math.max(1, ...(ketQua.value?.nhom || []).map((item) => item.diem)))

function phanTram(diem) {
  return Math.round((Math.max(diem, 0) / diemCaoNhat.value) * 100)
}

async function taiKetQua() {
  ketQua.value = null
  loi.value = ''
  if (!ssid.value) {
    loi.value = 'Không có mã phiên khảo sát.'
    return
  }
  dangTai.value = true
  try {
    ketQua.value = await fetchNhomNghePhuHop(ssid.value)
  } catch (error) {
    const detail = error.response?.data?.detail
    loi.value =
      error.response?.status === 400 && typeof detail === 'string' ? detail : 'Không tải được kết quả trắc nghiệm.'
  } finally {
    dangTai.value = false
  }
}

watch(ssid, taiKetQua, { immediate: true })
</script>

<style src="../thi-dai-hoc/lam-trac-nghiem/quiz-type.scss"></style>

<style scoped>
.nghe-phu-hop__thu-lai {
  margin-left: 6px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.nghe-phu-hop__rong {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #5b6770;
  text-align: center;
}

.tinh-cach__ma {
  display: flex;
  gap: 8px;
  margin: 6px 0 14px;
}

.tinh-cach__ma span {
  display: grid;
  place-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 1.4rem;
  font-weight: 700;
}

.tinh-cach__ds {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.tinh-cach__dong {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  color: #3a4742;
  font-size: 0.9rem;
}

.tinh-cach__diem {
  font-weight: 600;
}

.tinh-cach__thanh {
  height: 6px;
  margin-top: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: #e6ece8;
}

.tinh-cach__thanh span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--guest-primary);
}

.goi-y-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius);
  background: #fff;
  transition: box-shadow 0.3s ease;
}

.goi-y-card:hover {
  box-shadow: 0 16px 32px rgba(31, 122, 77, 0.14);
}

.goi-y-card--top {
  border-color: rgba(var(--guest-primary-rgb), 0.45);
}

.goi-y-card__hang {
  display: grid;
  flex: 0 0 36px;
  place-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(var(--guest-primary-rgb), 0.12);
  color: var(--guest-primary);
  font-weight: 700;
}

.goi-y-card--top .goi-y-card__hang {
  background: var(--guest-primary);
  color: #fff;
}

.goi-y-card__noi-dung {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.goi-y-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.goi-y-card__nhan-top,
.goi-y-card__tag {
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.78rem;
  line-height: 1.4;
}

.goi-y-card__nhan-top {
  background: #fff4e0;
  color: #b36b0c;
  font-weight: 600;
}

.goi-y-card__tag {
  border: 1px solid #d7eadf;
  color: #3a4742;
}

.nghe-phu-hop .goi-y-card__ten {
  margin: 0;
  color: var(--guest-primary);
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.35;
}

.goi-y-card__mo-ta {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: #3a4742;
  font-size: 0.95rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.goi-y-card__thong-tin {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 24px;
  margin: 0;
}

.goi-y-card__thong-tin dt {
  color: #6b7780;
  font-size: 0.72rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.goi-y-card__thong-tin dd {
  margin: 2px 0 0;
  color: #1c2b23;
  font-size: 0.9rem;
  font-weight: 500;
}

.goi-y-card__holland {
  display: flex;
  gap: 3px;
}

.goi-y-card__holland span {
  display: grid;
  place-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: #eef2ef;
  color: #6b7780;
  font-size: 0.8rem;
  font-weight: 700;
}

.goi-y-card__holland span.is-khop {
  background: var(--guest-primary);
  color: #fff;
}

.goi-y-card__chi-tiet {
  align-self: center;
  border-radius: var(--guest-radius);
  padding: 7px 16px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  text-decoration: none;
}

.goi-y-card__chi-tiet:hover {
  background: var(--guest-primary-hover);
  color: #fff;
}

.goi-y-card__chi-tiet:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

@media (max-width: 575.98px) {
  .goi-y-card {
    flex-wrap: wrap;
    padding: 14px;
  }

  .goi-y-card__chi-tiet {
    flex: 1 0 100%;
    text-align: center;
  }
}
</style>
