<template>
  <section class="xkld py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div v-if="dangTaiNhom" class="intro-card xkld__trang-thai" role="status">Đang tải thông tin nhóm nghề…</div>
          <div v-else-if="loiNhom" class="intro-card xkld__trang-thai">
            {{ loiNhom }}
            <button type="button" class="xkld__thu-lai" @click="taiNhomNghe">Thử lại</button>
          </div>
          <div v-else-if="!nhom" class="intro-card xkld__trang-thai">
            Không tìm thấy nhóm nghề có mã “{{ maNhom }}”.
            <RouterLink :to="{ name: tenRoute('thpt-xuat-khau-lao-dong') }">Xem tất cả nhóm nghề</RouterLink>
          </div>

          <div v-else class="stages-card">
            <div class="chi-tiet-huong">
              <RouterLink class="xkld__quay-lai" :to="{ name: tenRoute('thpt-xuat-khau-lao-dong') }">
                ← Tất cả nhóm nghề
              </RouterLink>
              <h1 class="xkld__title">{{ nhom.ten_nhom }}</h1>
              <p class="xkld__van-ban">{{ nhom.mo_ta_cong_viec }}</p>

              <dl class="thong-tin-luoi">
                <div v-if="nhom.yeu_cau_ngoai_ngu">
                  <dt>Ngoại ngữ</dt>
                  <dd>{{ nhom.yeu_cau_ngoai_ngu }}</dd>
                </div>
                <div v-if="thoiGianChuanBi(nhom)">
                  <dt>Thời gian chuẩn bị</dt>
                  <dd>{{ thoiGianChuanBi(nhom) }}</dd>
                </div>
                <div v-if="thuNhap(nhom)">
                  <dt>Thu nhập</dt>
                  <dd>{{ thuNhap(nhom) }}</dd>
                </div>
                <div v-if="nhom.kha_nang_gia_han_visa">
                  <dt>Gia hạn visa</dt>
                  <dd>{{ nhom.kha_nang_gia_han_visa }}</dd>
                </div>
              </dl>

              <div class="row g-3 mt-1">
                <div v-if="nhom.dieu_kien_suc_khoe_the_luc" class="col-12 col-md-6">
                  <div class="ghi-chu-khoi ghi-chu-khoi--lam-them">
                    <h3 class="ghi-chu-khoi__title">Điều kiện sức khỏe, thể lực</h3>
                    <p class="xkld__van-ban mb-0">{{ nhom.dieu_kien_suc_khoe_the_luc }}</p>
                  </div>
                </div>
                <div v-if="nhom.trien_vong_sau_ve_nuoc" class="col-12 col-md-6">
                  <div class="ghi-chu-khoi ghi-chu-khoi--visa">
                    <h3 class="ghi-chu-khoi__title">Triển vọng sau khi về nước</h3>
                    <p class="xkld__van-ban mb-0">{{ nhom.trien_vong_sau_ve_nuoc }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="loc-quoc-gia">
              <h3 id="loc-quoc-gia" class="loc-quoc-gia__title">Thị trường</h3>
              <div class="chip-nhom" role="group" aria-labelledby="loc-quoc-gia">
                <button
                  type="button"
                  class="chip"
                  :class="{ 'is-active': !thiTruongId }"
                  :aria-pressed="!thiTruongId"
                  @click="thiTruongId = null"
                >
                  Tất cả
                </button>
                <button
                  v-for="qg in dsThiTruong"
                  :key="qg.id"
                  type="button"
                  class="chip"
                  :class="{ 'is-active': thiTruongId === qg.id }"
                  :aria-pressed="thiTruongId === qg.id"
                  @click="thiTruongId = qg.id"
                >
                  {{ qg.ten_quoc_gia }}
                </button>
              </div>

              <div v-if="thiTruongDangChon" class="quoc-gia-chi-tiet">
                <p v-if="thiTruongDangChon.dac_diem_thi_truong" class="xkld__van-ban">
                  {{ thiTruongDangChon.dac_diem_thi_truong }}
                </p>
                <dl class="thong-tin-luoi">
                  <div v-if="thiTruongDangChon.loai_visa">
                    <dt>Loại visa</dt>
                    <dd>{{ thiTruongDangChon.loai_visa }}</dd>
                  </div>
                  <div v-if="thiTruongDangChon.thu_nhap_rieng_text">
                    <dt>Thu nhập tại thị trường</dt>
                    <dd>{{ thiTruongDangChon.thu_nhap_rieng_text }}</dd>
                  </div>
                  <div v-if="thiTruongDangChon.thoi_han_hop_dong_nam">
                    <dt>Thời hạn hợp đồng</dt>
                    <dd>{{ thiTruongDangChon.thoi_han_hop_dong_nam }} năm</dd>
                  </div>
                </dl>
              </div>
            </div>

            <div class="tab-muc" role="tablist" aria-label="Thông tin xuất khẩu lao động">
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
                <span class="tab-muc__dem">{{ locTheoThiTruong(chiTiet[tab.value]).length }}</span>
              </button>
            </div>

            <div :id="`panel-${tabMuc}`" role="tabpanel" :aria-labelledby="`tab-${tabMuc}`">
              <div v-if="dangTaiChiTiet" class="xkld__trang-thai" role="status">Đang tải thông tin…</div>
              <div v-else-if="loiChiTiet" class="xkld__trang-thai">
                {{ loiChiTiet }}
                <button type="button" class="xkld__thu-lai" @click="taiChiTiet(nhom.id)">Thử lại</button>
              </div>
              <div v-else-if="!dsTab.length" class="xkld__trang-thai">
                Chưa có dữ liệu {{ nhanTab.toLowerCase() }} cho lựa chọn này.
              </div>

              <div v-else-if="tabMuc === 'ngheCuThe'" class="row g-3">
                <div v-for="item in dsTab" :key="item.id" class="col-12 col-md-6">
                  <article class="muc-card h-100">
                    <div class="d-flex flex-wrap gap-2">
                      <span class="muc-card__nhan">{{ nhanEnum(YEU_CAU_GIOI_TINH, item.yeu_cau_gioi_tinh) }}</span>
                      <span v-if="item.ten_quoc_gia" class="muc-card__nhan">{{ item.ten_quoc_gia }}</span>
                    </div>
                    <h3 class="muc-card__ten">{{ item.ten_cong_viec }}</h3>
                    <p v-if="item.mo_ta_ngan" class="xkld__van-ban mb-0">{{ item.mo_ta_ngan }}</p>
                  </article>
                </div>
              </div>

              <div v-else-if="tabMuc === 'chiPhi'" class="d-flex flex-column gap-3">
                <div v-for="loai in nhomChiPhi" :key="loai.value" class="chi-phi-nhom">
                  <h3 class="chi-phi-nhom__title">{{ loai.label }}</h3>
                  <ul class="chi-phi-ds">
                    <li v-for="item in loai.items" :key="item.id" class="chi-phi-ds__dong">
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
                    <p class="xkld__van-ban">{{ item.mo_ta_thu_tuc }}</p>
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
                    <p v-if="item.mo_ta_ho_tro" class="xkld__van-ban mb-0">{{ item.mo_ta_ho_tro }}</p>
                    <p v-if="item.thong_tin_lien_he" class="muc-card__lien-he">
                      <strong>Liên hệ:</strong> {{ item.thong_tin_lien_he }}
                    </p>
                    <p v-if="item.luu_y_tranh_rui_ro" class="muc-card__ghi-chu">{{ item.luu_y_tranh_rui_ro }}</p>
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
          <nav class="paths-card" aria-labelledby="menu-nhom-nghe">
            <h2 id="menu-nhom-nghe" class="h4 mb-3">Các nhóm nghề xuất khẩu lao động</h2>
            <p v-if="!dangTaiNhom && !dsNhom.length" class="menu-nhom-rong">Chưa có nhóm nghề.</p>
            <ul class="menu-nhom">
              <li v-for="item in dsNhom" :key="item.id">
                <RouterLink
                  class="menu-nhom__muc"
                  :class="{ 'is-active': item.id === nhom?.id }"
                  :to="{ name: tenRoute('thpt-xuat-khau-lao-dong-nhom-nghe'), params: { maNhom: item.ma_nhom } }"
                  :aria-current="item.id === nhom?.id ? 'page' : undefined"
                >
                  <span class="menu-nhom__ten">{{ item.ten_nhom }}</span>
                  <span v-if="thuNhap(item)" class="menu-nhom__thu-nhap">{{ thuNhap(item) }}</span>
                </RouterLink>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { chiPhiApi, kenhKetNoiApi, ngheCuTheApi, nhomNgheApi, thiTruongApi, thuTucApi } from '@/api/thptXkld'
import { LOAI_CHI_PHI, LOAI_KENH, YEU_CAU_GIOI_TINH, nhanEnum } from '@/constants/thptXkld'
import { khoangTien, thoiGianChuanBi, thuNhap } from './xkld'
import { useTenRouteThpt } from '../useTenRouteThpt'

defineOptions({ name: 'ThptXuatKhauLaoDongChiTietNhomNghe' })

const TAB_MUC = [
  { value: 'ngheCuThe', label: 'Nghề cụ thể' },
  { value: 'chiPhi', label: 'Chi phí' },
  { value: 'thuTuc', label: 'Thủ tục' },
  { value: 'kenhKetNoi', label: 'Kênh kết nối' },
]

const API_TAB = { ngheCuThe: ngheCuTheApi, chiPhi: chiPhiApi, thuTuc: thuTucApi, kenhKetNoi: kenhKetNoiApi }

const route = useRoute()
const { tenRoute } = useTenRouteThpt()

const dsNhom = ref([])
const dangTaiNhom = ref(false)
const loiNhom = ref('')
const thiTruongId = ref(null)
const tabMuc = ref('ngheCuThe')

const dsThiTruong = ref([])
const chiTiet = reactive({ ngheCuThe: [], chiPhi: [], thuTuc: [], kenhKetNoi: [] })
const dangTaiChiTiet = ref(false)
const loiChiTiet = ref('')
// Chuyển nhóm nghề liên tục: chỉ nhận kết quả của lần tải mới nhất.
let lanTai = 0

const maNhom = computed(() => String(route.params.maNhom || '').toUpperCase())
const nhom = computed(() => dsNhom.value.find((item) => item.ma_nhom === maNhom.value) || null)
const thiTruongDangChon = computed(() => dsThiTruong.value.find((item) => item.id === thiTruongId.value) || null)
const nhanTab = computed(() => TAB_MUC.find((tab) => tab.value === tabMuc.value)?.label || '')
const dsTab = computed(() => locTheoThiTruong(chiTiet[tabMuc.value]))

const nhomChiPhi = computed(() =>
  LOAI_CHI_PHI.map((loai) => ({
    ...loai,
    items: dsTab.value.filter((item) => item.loai_chi_phi === loai.value),
  })).filter((nhomLoai) => nhomLoai.items.length),
)

// Dòng không gắn thị trường áp dụng chung cho cả nhóm nghề nên luôn hiển thị.
function locTheoThiTruong(ds) {
  if (!thiTruongId.value) return ds
  return ds.filter((item) => !item.thpt_xkld_thi_truong_id || item.thpt_xkld_thi_truong_id === thiTruongId.value)
}

async function taiNhomNghe() {
  dangTaiNhom.value = true
  loiNhom.value = ''
  try {
    const data = await nhomNgheApi.fetch({ trang_thai: 1, page: 1, page_size: 100 })
    dsNhom.value = data.items || []
  } catch {
    loiNhom.value = 'Không tải được thông tin nhóm nghề.'
  } finally {
    dangTaiNhom.value = false
  }
}

async function taiChiTiet(id) {
  const lan = ++lanTai
  dangTaiChiTiet.value = true
  loiChiTiet.value = ''
  const params = { thpt_xkld_nhom_nghe_id: id, page: 1, page_size: 200 }
  try {
    const [thiTruong, ...cacTab] = await Promise.all([
      thiTruongApi.fetch(params),
      ...TAB_MUC.map((tab) => API_TAB[tab.value].fetch(params)),
    ])
    if (lan !== lanTai) return
    dsThiTruong.value = thiTruong.items || []
    TAB_MUC.forEach((tab, index) => {
      chiTiet[tab.value] = cacTab[index].items || []
    })
  } catch {
    if (lan !== lanTai) return
    loiChiTiet.value = 'Không tải được thông tin của nhóm nghề này.'
  } finally {
    if (lan === lanTai) dangTaiChiTiet.value = false
  }
}

// Đổi nhóm nghề (qua menu hoặc URL) thì xóa dữ liệu cũ và tải lại.
watch(
  () => nhom.value?.id,
  (id) => {
    thiTruongId.value = null
    dsThiTruong.value = []
    TAB_MUC.forEach((tab) => {
      chiTiet[tab.value] = []
    })
    if (id) taiChiTiet(id)
  },
)

onMounted(taiNhomNghe)
</script>

<style scoped>
.xkld__thu-lai {
  margin-left: 8px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.xkld__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.xkld__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.35;
}

/* Trường Text của danh mục có thể xuống dòng. */
.xkld__van-ban {
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
.xkld__thu-lai:focus-visible {
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

.muc-card--doanh_nghiep_cap_phep {
  --mau-kenh: #1a66d1;
}

.muc-card--trung_tam_lao_dong_ngoai_nuoc {
  --mau-kenh: #d98a1c;
}

.muc-card--ho_tro_he_thong {
  --mau-kenh: #6b7780;
}

.xkld .muc-card__ten {
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

.xkld .thu-tuc__ten {
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
  .xkld__title {
    font-size: 1.4rem;
  }

  .xkld__lead,
  .xkld__van-ban {
    font-size: 0.9rem;
  }

  .xkld .stages-heading {
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

.xkld__trang-thai a {
  margin-left: 6px;
  color: var(--guest-primary);
  font-weight: 500;
}

.xkld__quay-lai {
  display: inline-block;
  margin-bottom: 8px;
  color: var(--guest-primary);
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
}

.xkld__quay-lai:hover {
  text-decoration: underline;
}

.menu-nhom {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.menu-nhom__muc {
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

.menu-nhom__muc:hover {
  box-shadow: 0 8px 20px rgba(31, 122, 77, 0.12);
}

.menu-nhom__muc.is-active {
  border-color: var(--guest-primary);
  box-shadow: 0 0 0 1px var(--guest-primary);
}

.menu-nhom__muc:focus-visible,
.xkld__quay-lai:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

.menu-nhom__ten {
  color: var(--guest-primary);
  font-weight: 700;
  line-height: 1.35;
}

.menu-nhom__thu-nhap,
.menu-nhom-rong {
  color: #6b7780;
  font-size: 0.8rem;
}
</style>
