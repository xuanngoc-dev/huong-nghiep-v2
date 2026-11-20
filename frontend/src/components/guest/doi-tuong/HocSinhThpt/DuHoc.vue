<template>
  <section class="du-hoc py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <article class="intro-card mb-3">
            <h1 class="du-hoc__title">Du học</h1>
            <p class="du-hoc__lead">
              Du học không chỉ có một con đường. Bạn có thể học nghề vừa học vừa làm, học đại học/cao đẳng chính quy
              hoặc học chuyển tiếp từ trong nước ra nước ngoài. Hãy chọn hướng đi, so sánh quốc gia, chi phí và thủ tục
              để chuẩn bị đúng ngay từ đầu.
            </p>

            <div v-if="dangTaiHuong" class="du-hoc__trang-thai" role="status">Đang tải các hướng đi du học…</div>
            <div v-else-if="loiHuong" class="du-hoc__trang-thai">
              {{ loiHuong }}
              <button type="button" class="du-hoc__thu-lai" @click="taiHuongDi">Thử lại</button>
            </div>
            <div v-else-if="!dsHuong.length" class="du-hoc__trang-thai">Chưa có dữ liệu hướng đi du học.</div>

            <div v-else class="row g-3" role="radiogroup" aria-label="Chọn hướng đi du học">
              <div v-for="huong in dsHuong" :key="huong.id" class="col-12 col-sm-6 col-xl-4">
                <button
                  type="button"
                  role="radio"
                  class="huong-card h-100"
                  :class="[`huong-card--${huong.loai_hinh}`, { 'is-active': huongId === huong.id }]"
                  :aria-checked="huongId === huong.id"
                  @click="chonHuongDuHoc(huong.id)"
                >
                  <span class="huong-card__loai">{{ nhanEnum(LOAI_HINH_DU_HOC, huong.loai_hinh) }}</span>
                  <span class="huong-card__ten">{{ huong.ten_huong }}</span>
                  <span class="huong-card__mo-ta">{{ huong.mo_ta_dac_diem }}</span>
                </button>
              </div>
            </div>
          </article>

          <div v-if="huongDangChon" class="stages-card">
            <div class="chi-tiet-huong">
              <h2 class="stages-heading mb-2">{{ huongDangChon.ten_huong }}</h2>
              <p class="du-hoc__van-ban">{{ huongDangChon.mo_ta_dac_diem }}</p>

              <dl class="thong-tin-luoi">
                <div v-if="huongDangChon.yeu_cau_ngoai_ngu">
                  <dt>Ngoại ngữ</dt>
                  <dd>{{ huongDangChon.yeu_cau_ngoai_ngu }}</dd>
                </div>
                <div v-if="thoiGianChuanBi(huongDangChon)">
                  <dt>Thời gian chuẩn bị</dt>
                  <dd>{{ thoiGianChuanBi(huongDangChon) }}</dd>
                </div>
                <div v-if="huongDangChon.chi_phi_du_kien_text">
                  <dt>Chi phí dự kiến</dt>
                  <dd>{{ huongDangChon.chi_phi_du_kien_text }}</dd>
                </div>
              </dl>

              <div class="row g-3 mt-1">
                <div v-if="huongDangChon.co_hoi_lam_them" class="col-12 col-md-6">
                  <div class="ghi-chu-khoi ghi-chu-khoi--lam-them">
                    <h3 class="ghi-chu-khoi__title">Cơ hội làm thêm</h3>
                    <p class="du-hoc__van-ban mb-0">{{ huongDangChon.co_hoi_lam_them }}</p>
                  </div>
                </div>
                <div v-if="huongDangChon.lo_trinh_visa_dinh_cu" class="col-12 col-md-6">
                  <div class="ghi-chu-khoi ghi-chu-khoi--visa">
                    <h3 class="ghi-chu-khoi__title">Lộ trình visa, định cư</h3>
                    <p class="du-hoc__van-ban mb-0">{{ huongDangChon.lo_trinh_visa_dinh_cu }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="loc-quoc-gia">
              <h3 id="loc-quoc-gia" class="loc-quoc-gia__title">Quốc gia</h3>
              <div class="chip-nhom" role="group" aria-labelledby="loc-quoc-gia">
                <button
                  type="button"
                  class="chip"
                  :class="{ 'is-active': !quocGiaId }"
                  :aria-pressed="!quocGiaId"
                  @click="quocGiaId = null"
                >
                  Tất cả
                </button>
                <button
                  v-for="qg in dsQuocGia"
                  :key="qg.id"
                  type="button"
                  class="chip"
                  :class="{ 'is-active': quocGiaId === qg.id }"
                  :aria-pressed="quocGiaId === qg.id"
                  @click="quocGiaId = qg.id"
                >
                  {{ qg.ten_quoc_gia }}
                </button>
              </div>

              <div v-if="quocGiaDangChon" class="quoc-gia-chi-tiet">
                <p v-if="quocGiaDangChon.dac_diem_noi_bat" class="du-hoc__van-ban">
                  {{ quocGiaDangChon.dac_diem_noi_bat }}
                </p>
                <dl class="thong-tin-luoi">
                  <div v-if="quocGiaDangChon.yeu_cau_ngoai_ngu_rieng">
                    <dt>Ngoại ngữ riêng</dt>
                    <dd>{{ quocGiaDangChon.yeu_cau_ngoai_ngu_rieng }}</dd>
                  </div>
                  <div v-if="quocGiaDangChon.co_hoi_viec_lam_visa">
                    <dt>Việc làm & visa</dt>
                    <dd>{{ quocGiaDangChon.co_hoi_viec_lam_visa }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <div class="tab-muc" role="tablist" aria-label="Thông tin du học">
              <button
                v-for="tab in TAB_MUC"
                :id="`tab-${tab.value}`"
                :key="tab.value"
                type="button"
                role="tab"
                class="tab-muc__nut"
                :class="{ 'is-active': tabMuc === tab.value }"
                :aria-selected="tabMuc === tab.value"
                :aria-controls="`panel-${tab.value}`"
                @click="tabMuc = tab.value"
              >
                {{ tab.label }}
                <span class="tab-muc__dem">{{ locTheoQuocGia(chiTiet[tab.value]).length }}</span>
              </button>
            </div>

            <div :id="`panel-${tabMuc}`" role="tabpanel" :aria-labelledby="`tab-${tabMuc}`">
              <div v-if="dangTaiChiTiet" class="du-hoc__trang-thai" role="status">Đang tải thông tin…</div>
              <div v-else-if="loiChiTiet" class="du-hoc__trang-thai">
                {{ loiChiTiet }}
                <button type="button" class="du-hoc__thu-lai" @click="taiChiTiet(huongId)">Thử lại</button>
              </div>
              <div v-else-if="!dsTab.length" class="du-hoc__trang-thai">
                Chưa có dữ liệu {{ nhanTab.toLowerCase() }} cho lựa chọn này.
              </div>

              <div v-else-if="tabMuc === 'nganh'" class="row g-3">
                <div v-for="item in dsTab" :key="item.id" class="col-12 col-md-6">
                  <article class="muc-card h-100">
                    <span v-if="item.ten_quoc_gia" class="muc-card__nhan">{{ item.ten_quoc_gia }}</span>
                    <h3 class="muc-card__ten">{{ item.ten_nganh }}</h3>
                    <dl class="thong-tin-luoi thong-tin-luoi--nho">
                      <div v-if="item.nhu_cau_nhan_luc">
                        <dt>Nhu cầu nhân lực</dt>
                        <dd>{{ item.nhu_cau_nhan_luc }}</dd>
                      </div>
                      <div v-if="item.muc_luong_tham_khao">
                        <dt>Lương tham khảo</dt>
                        <dd>{{ item.muc_luong_tham_khao }}</dd>
                      </div>
                    </dl>
                    <p v-if="item.ghi_chu" class="muc-card__ghi-chu">{{ item.ghi_chu }}</p>
                  </article>
                </div>
              </div>

              <div v-else-if="tabMuc === 'chiPhi'" class="d-flex flex-column gap-3">
                <div v-for="nhom in nhomChiPhi" :key="nhom.value" class="chi-phi-nhom">
                  <h3 class="chi-phi-nhom__title">{{ nhom.label }}</h3>
                  <ul class="chi-phi-ds">
                    <li v-for="item in nhom.items" :key="item.id" class="chi-phi-ds__dong">
                      <div class="chi-phi-ds__ten">
                        {{ item.ten_khoan_chi }}
                        <span v-if="item.ten_quoc_gia" class="muc-card__nhan">{{ item.ten_quoc_gia }}</span>
                        <span v-if="item.ghi_chu" class="chi-phi-ds__ghi-chu">{{ item.ghi_chu }}</span>
                      </div>
                      <div class="chi-phi-ds__so">
                        <span>{{ khoangTien(item) }}</span>
                        <span v-if="item.chi_phi_quy_doi_vnd_text" class="chi-phi-ds__quy-doi">
                          ≈ {{ item.chi_phi_quy_doi_vnd_text }}
                        </span>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <ol v-else-if="tabMuc === 'thuTuc'" class="thu-tuc">
                <li v-for="item in dsTab" :key="item.id" class="thu-tuc__buoc">
                  <span class="thu-tuc__so" aria-hidden="true">{{ item.buoc_so }}</span>
                  <div class="thu-tuc__noi-dung">
                    <h3 class="thu-tuc__ten">
                      {{ item.ten_buoc }}
                      <span v-if="item.ten_quoc_gia" class="muc-card__nhan">{{ item.ten_quoc_gia }}</span>
                    </h3>
                    <p class="du-hoc__van-ban">{{ item.mo_ta_thu_tuc }}</p>
                    <p v-if="item.giay_to_can_co" class="thu-tuc__phu">
                      <strong>Giấy tờ cần có:</strong> {{ item.giay_to_can_co }}
                    </p>
                    <p v-if="item.thoi_gian_du_kien" class="thu-tuc__phu">
                      <strong>Thời gian dự kiến:</strong> {{ item.thoi_gian_du_kien }}
                    </p>
                  </div>
                </li>
              </ol>

              <div v-else class="row g-3">
                <div v-for="item in dsTab" :key="item.id" class="col-12 col-md-6">
                  <article class="muc-card h-100" :class="`muc-card--${item.loai_kenh}`">
                    <div class="d-flex flex-wrap gap-2">
                      <span class="muc-card__loai">{{ nhanEnum(LOAI_KENH, item.loai_kenh) }}</span>
                      <span v-if="item.ten_quoc_gia" class="muc-card__nhan">{{ item.ten_quoc_gia }}</span>
                    </div>
                    <h3 class="muc-card__ten">{{ item.ten_kenh }}</h3>
                    <p v-if="item.mo_ta_ho_tro" class="du-hoc__van-ban mb-0">{{ item.mo_ta_ho_tro }}</p>
                    <p v-if="item.thong_tin_lien_he" class="muc-card__lien-he">
                      <strong>Liên hệ:</strong> {{ item.thong_tin_lien_he }}
                    </p>
                    <p v-if="item.luu_y_khi_ket_noi" class="muc-card__ghi-chu">{{ item.luu_y_khi_ket_noi }}</p>
                  </article>
                </div>
              </div>
            </div>
          </div>

          <div class="d-flex flex-column gap-3 mt-3">
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
import { chiPhiApi, huongDiApi, kenhKetNoiApi, nganhApi, quocGiaApi, thuTucApi } from '@/api/thptDuHoc'
import { LOAI_CHI_PHI, LOAI_HINH_DU_HOC, LOAI_KENH, nhanEnum } from '@/constants/thptDuHoc'
import { DINH_HUONG_THPT_KEY, dinhHuongThptList } from './dinhHuong'
import { routeNameDinhHuongThpt } from './routes'
import { useTenRouteThpt } from './useTenRouteThpt'

defineOptions({ name: 'ThptDuHoc' })

const TAB_MUC = [
  { value: 'nganh', label: 'Ngành học' },
  { value: 'chiPhi', label: 'Chi phí' },
  { value: 'thuTuc', label: 'Thủ tục' },
  { value: 'kenhKetNoi', label: 'Kênh kết nối' },
]

const API_TAB = { nganh: nganhApi, chiPhi: chiPhiApi, thuTuc: thuTucApi, kenhKetNoi: kenhKetNoiApi }

const { tienTo } = useTenRouteThpt()
const route = useRoute()
const router = useRouter()
const currentDirection = computed(() => route.meta.dinhHuong || '')

const dsHuong = ref([])
const dangTaiHuong = ref(false)
const loiHuong = ref('')
const huongId = ref(null)
const quocGiaId = ref(null)
const tabMuc = ref('nganh')

const dsQuocGia = ref([])
const chiTiet = reactive({ nganh: [], chiPhi: [], thuTuc: [], kenhKetNoi: [] })
const dangTaiChiTiet = ref(false)
const loiChiTiet = ref('')
// Bấm đổi hướng đi liên tục: chỉ nhận kết quả của lần tải mới nhất.
let lanTai = 0

const huongDangChon = computed(() => dsHuong.value.find((item) => item.id === huongId.value) || null)
const quocGiaDangChon = computed(() => dsQuocGia.value.find((item) => item.id === quocGiaId.value) || null)
const nhanTab = computed(() => TAB_MUC.find((tab) => tab.value === tabMuc.value)?.label || '')
const dsTab = computed(() => locTheoQuocGia(chiTiet[tabMuc.value]))

const nhomChiPhi = computed(() =>
  LOAI_CHI_PHI.map((loai) => ({
    ...loai,
    items: dsTab.value.filter((item) => item.loai_chi_phi === loai.value),
  })).filter((nhom) => nhom.items.length),
)

// Dòng không gắn quốc gia áp dụng chung cho cả hướng đi nên luôn hiển thị.
function locTheoQuocGia(ds) {
  if (!quocGiaId.value) return ds
  return ds.filter((item) => !item.thpt_duhoc_quoc_gia_id || item.thpt_duhoc_quoc_gia_id === quocGiaId.value)
}

function thoiGianChuanBi(huong) {
  if (huong.thoi_gian_chuan_bi_text) return huong.thoi_gian_chuan_bi_text
  const min = huong.thoi_gian_chuan_bi_thang_min || 0
  const max = huong.thoi_gian_chuan_bi_thang_max || 0
  if (!min && !max) return ''
  if (min && max && min !== max) return `${min} - ${max} tháng`
  return `${max || min} tháng`
}

const dinhDangSo = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })

function khoangTien(item) {
  const min = item.chi_phi_min != null ? Number(item.chi_phi_min) : null
  const max = item.chi_phi_max != null ? Number(item.chi_phi_max) : null
  const donVi = item.don_vi_tien || 'VND'
  if (min == null && max == null) return 'Tùy trường hợp'
  if (min != null && max != null && min !== max) return `${dinhDangSo.format(min)} - ${dinhDangSo.format(max)} ${donVi}`
  return `${dinhDangSo.format(max ?? min)} ${donVi}`
}

async function taiHuongDi() {
  dangTaiHuong.value = true
  loiHuong.value = ''
  try {
    const data = await huongDiApi.fetch({ trang_thai: 1, page: 1, page_size: 100 })
    dsHuong.value = data.items || []
    if (dsHuong.value.length && !huongDangChon.value) chonHuongDuHoc(dsHuong.value[0].id)
  } catch {
    loiHuong.value = 'Không tải được danh sách hướng đi du học.'
  } finally {
    dangTaiHuong.value = false
  }
}

async function taiChiTiet(id) {
  const lan = ++lanTai
  dangTaiChiTiet.value = true
  loiChiTiet.value = ''
  const params = { thpt_duhoc_huong_di_id: id, page: 1, page_size: 200 }
  try {
    const [quocGia, ...cacTab] = await Promise.all([
      quocGiaApi.fetch(params),
      ...TAB_MUC.map((tab) => API_TAB[tab.value].fetch(params)),
    ])
    if (lan !== lanTai) return
    dsQuocGia.value = quocGia.items || []
    TAB_MUC.forEach((tab, index) => {
      chiTiet[tab.value] = cacTab[index].items || []
    })
  } catch {
    if (lan !== lanTai) return
    loiChiTiet.value = 'Không tải được thông tin du học của hướng đi này.'
  } finally {
    if (lan === lanTai) dangTaiChiTiet.value = false
  }
}

function chonHuongDuHoc(id) {
  if (huongId.value === id) return
  huongId.value = id
  quocGiaId.value = null
  dsQuocGia.value = []
  TAB_MUC.forEach((tab) => {
    chiTiet[tab.value] = []
  })
  taiChiTiet(id)
}

function chonHuong(direction) {
  if (!direction.moTruyCap) return
  sessionStorage.setItem(DINH_HUONG_THPT_KEY, direction.code)
  const name = routeNameDinhHuongThpt(direction.code, tienTo.value)
  if (name && name !== route.name) router.push({ name })
}

onMounted(taiHuongDi)
</script>

<style scoped>
.du-hoc__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.35;
}

.du-hoc__lead {
  margin: 0 0 16px;
  color: #3a4742;
  line-height: 1.6;
}

/* Trường Text của danh mục có thể xuống dòng. */
.du-hoc__van-ban {
  margin: 0 0 12px;
  color: #3a4742;
  font-size: 0.95rem;
  line-height: 1.55;
  white-space: pre-line;
}

.du-hoc__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.du-hoc__thu-lai {
  margin-left: 8px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.huong-card {
  --mau-loai: var(--guest-primary);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  width: 100%;
  padding: 14px;
  border: 1px solid #d7eadf;
  border-top: 4px solid var(--mau-loai);
  border-radius: var(--guest-radius);
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition:
    box-shadow 0.3s ease,
    background-color 0.2s ease;
}

.huong-card:hover {
  box-shadow: 0 12px 24px rgba(31, 122, 77, 0.12);
}

.huong-card.is-active {
  border-color: var(--mau-loai);
  background: #f6fbf7;
  box-shadow: 0 0 0 2px var(--mau-loai);
}

.huong-card--du_hoc_nghe {
  --mau-loai: #d98a1c;
}

.huong-card--du_hoc_hoc_thuat {
  --mau-loai: #1a66d1;
}

.huong-card__loai {
  border-radius: 999px;
  padding: 3px 10px;
  background: var(--mau-loai);
  color: #fff;
  font-size: 0.78rem;
  line-height: 1.3;
}

.huong-card__ten {
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.huong-card__mo-ta {
  display: -webkit-box;
  overflow: hidden;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
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

.thong-tin-luoi:empty {
  display: none;
}

.thong-tin-luoi dt {
  color: #6b7780;
  font-size: 0.75rem;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.thong-tin-luoi dd {
  margin: 2px 0 0;
  color: #1c2b23;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
  white-space: pre-line;
}

.thong-tin-luoi--nho {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.ghi-chu-khoi {
  height: 100%;
  padding: 14px;
  border-radius: var(--guest-radius);
  background: #fff;
  border: 1px solid #d7eadf;
}

.ghi-chu-khoi--lam-them {
  border-left: 4px solid var(--guest-primary);
}

.ghi-chu-khoi--visa {
  border-left: 4px solid #1a66d1;
}

.ghi-chu-khoi__title,
.loc-quoc-gia__title,
.chi-phi-nhom__title {
  margin: 0 0 8px;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.loc-quoc-gia {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e3efe7;
}

.chip-nhom,
.tab-muc {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip,
.tab-muc__nut {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(var(--guest-primary-rgb), 0.4);
  border-radius: 999px;
  padding: 6px 14px;
  background: #fff;
  color: var(--guest-primary);
  font-size: 0.875rem;
  line-height: 1.2;
  cursor: pointer;
}

.chip:hover,
.tab-muc__nut:hover {
  background: rgba(var(--guest-primary-rgb), 0.08);
}

.chip.is-active,
.tab-muc__nut.is-active {
  border-color: var(--guest-primary);
  background: var(--guest-primary);
  color: #fff;
}

.chip:focus-visible,
.tab-muc__nut:focus-visible,
.huong-card:focus-visible,
.du-hoc__thu-lai:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

.quoc-gia-chi-tiet {
  margin-top: 12px;
}

.tab-muc {
  margin: 20px 0 16px;
  padding-top: 16px;
  border-top: 1px solid #e3efe7;
}

.tab-muc__dem {
  min-width: 20px;
  border-radius: 999px;
  padding: 1px 6px;
  background: rgba(var(--guest-primary-rgb), 0.12);
  font-size: 0.75rem;
  text-align: center;
}

.tab-muc__nut.is-active .tab-muc__dem {
  background: rgba(255, 255, 255, 0.25);
}

.muc-card {
  --mau-kenh: var(--guest-primary);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding: 16px;
  border: 1px solid #d7eadf;
  border-top: 4px solid var(--mau-kenh);
  border-radius: var(--guest-radius);
  background: #fff;
}

.muc-card .thong-tin-luoi {
  align-self: stretch;
}

.muc-card--trung_tam_tu_van {
  --mau-kenh: #1a66d1;
}

.muc-card--cong_dong {
  --mau-kenh: #d98a1c;
}

.muc-card--ho_tro_he_thong {
  --mau-kenh: #6b7780;
}

.du-hoc .muc-card__ten {
  margin: 0;
  color: var(--guest-primary);
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.35;
}

.muc-card__loai {
  border-radius: 999px;
  padding: 3px 10px;
  background: var(--mau-kenh);
  color: #fff;
  font-size: 0.78rem;
  line-height: 1.3;
}

.muc-card__nhan {
  display: inline-block;
  border: 1px solid #d7eadf;
  border-radius: 999px;
  padding: 2px 8px;
  color: #3a4742;
  font-size: 0.75rem;
  font-weight: 400;
  line-height: 1.3;
  vertical-align: middle;
}

.muc-card__ghi-chu {
  margin: 0;
  padding-left: 10px;
  border-left: 3px solid var(--mau-kenh);
  color: #3a4742;
  font-size: 0.9rem;
  font-style: italic;
  line-height: 1.45;
  white-space: pre-line;
}

.muc-card__lien-he {
  margin: 0;
  color: #3a4742;
  font-size: 0.9rem;
  word-break: break-word;
}

.chi-phi-ds {
  margin: 0;
  padding: 0;
  list-style: none;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius);
  background: #fff;
}

.chi-phi-ds__dong {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 4px 16px;
  padding: 10px 14px;
}

.chi-phi-ds__dong + .chi-phi-ds__dong {
  border-top: 1px solid #e3efe7;
}

.chi-phi-ds__ten {
  flex: 1 1 240px;
  color: #1c2b23;
  font-size: 0.95rem;
  font-weight: 500;
}

.chi-phi-ds__ghi-chu {
  display: block;
  color: #6b7780;
  font-size: 0.85rem;
  font-weight: 400;
}

.chi-phi-ds__so {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  color: var(--guest-primary);
  font-size: 0.95rem;
  font-weight: 600;
  text-align: right;
}

.chi-phi-ds__quy-doi {
  color: #6b7780;
  font-size: 0.8rem;
  font-weight: 400;
}

.thu-tuc {
  margin: 0;
  padding: 0;
  list-style: none;
}

.thu-tuc__buoc {
  position: relative;
  display: flex;
  gap: 14px;
  padding-bottom: 16px;
}

/* Đường nối giữa các bước. */
.thu-tuc__buoc:not(:last-child)::before {
  position: absolute;
  top: 34px;
  bottom: 0;
  left: 16px;
  width: 2px;
  background: #d7eadf;
  content: '';
}

.thu-tuc__so {
  display: inline-flex;
  flex: 0 0 34px;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--guest-primary);
  color: #fff;
  font-weight: 700;
}

.thu-tuc__noi-dung {
  flex: 1;
  min-width: 0;
}

.du-hoc .thu-tuc__ten {
  margin: 5px 0 6px;
  font-size: 1.02rem;
  font-weight: 700;
  line-height: 1.35;
}

.thu-tuc__phu {
  margin: 0 0 4px;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
  white-space: pre-line;
}

@media (max-width: 767.98px) {
  /* Chip quốc gia và tab cuộn ngang thay vì xuống nhiều dòng. */
  .chip-nhom,
  .tab-muc {
    flex-wrap: nowrap;
    overflow-x: auto;
    margin-right: -15px;
    margin-left: -15px;
    padding: 0 15px 4px;
    scrollbar-width: none;
  }

  .tab-muc {
    padding-top: 16px;
  }

  .chip-nhom::-webkit-scrollbar,
  .tab-muc::-webkit-scrollbar {
    display: none;
  }

  .chip,
  .tab-muc__nut {
    flex: 0 0 auto;
  }
}

@media (max-width: 575.98px) {
  .du-hoc__title {
    font-size: 1.4rem;
  }

  .du-hoc__lead,
  .du-hoc__van-ban {
    font-size: 0.9rem;
  }

  .du-hoc .stages-heading {
    font-size: 1.2rem;
  }

  .muc-card {
    padding: 14px;
  }

  .chi-phi-ds__so {
    align-items: flex-start;
    text-align: left;
  }
}

@media (max-width: 359.98px) {
  .thong-tin-luoi--nho {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
