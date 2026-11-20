<template>
  <section class="chi-tiet-nhom py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div v-if="dangTaiNhom" class="intro-card chi-tiet-nhom__trang-thai" role="status">
            Đang tải thông tin nhóm nghề…
          </div>
          <div v-else-if="loiNhom" class="intro-card chi-tiet-nhom__trang-thai">
            {{ loiNhom }}
            <button type="button" class="chi-tiet-nhom__thu-lai" @click="taiNhomNghe">Thử lại</button>
          </div>
          <div v-else-if="!nhom" class="intro-card chi-tiet-nhom__trang-thai">
            Không tìm thấy nhóm nghề có mã “{{ maNhom }}”.
            <RouterLink :to="{ name: tenRoute('thpt-di-lam') }">Xem tất cả nhóm nghề</RouterLink>
          </div>

          <template v-else>
            <article class="intro-card nhom-tong-quan" :class="`nhom-tong-quan--${nhom.nhom_muc_tieu || 'khac'}`">
              <RouterLink class="nhom-tong-quan__quay-lai" :to="{ name: tenRoute('thpt-di-lam') }">
                ← Tất cả nhóm nghề
              </RouterLink>
              <div class="nhom-tong-quan__tags">
                <span v-if="nhom.nhom_muc_tieu" class="nhom-tong-quan__muc-tieu">
                  {{ nhan(NHOM_MUC_TIEU, nhom.nhom_muc_tieu) }}
                </span>
                <span v-if="nhom.loai_hinh_dau_vao" class="nhom-tong-quan__loai">
                  {{ nhan(LOAI_HINH_DAU_VAO, nhom.loai_hinh_dau_vao) }}
                </span>
              </div>
              <h1 class="nhom-tong-quan__ten">{{ nhom.ten_nhom }}</h1>
              <p class="nhom-tong-quan__mo-ta">{{ nhom.mo_ta_dac_diem }}</p>

              <dl class="nhom-tong-quan__thong-tin">
                <div>
                  <dt>Đào tạo</dt>
                  <dd>{{ nhom.thoi_gian_dao_tao_text || thoiGianDaoTao(nhom) }}</dd>
                </div>
                <div>
                  <dt>Lương khởi điểm</dt>
                  <dd>{{ nhom.muc_luong_text || khoangLuong(nhom) }}</dd>
                </div>
                <div>
                  <dt>Khi có kinh nghiệm</dt>
                  <dd>
                    {{
                      nhom.luong_kinh_nghiem_max != null
                        ? `tới ${soTrieu(nhom.luong_kinh_nghiem_max)} triệu/tháng`
                        : 'Đang cập nhật'
                    }}
                  </dd>
                </div>
                <div>
                  <dt>Nhóm Holland</dt>
                  <dd>{{ nhom.ma_holland || '—' }}</dd>
                </div>
              </dl>

              <p v-if="nhom.danh_gia_trien_vong" class="nhom-tong-quan__trien-vong">
                {{ nhom.danh_gia_trien_vong }}
              </p>

              <div v-if="nhom.dieu_kien_dau_vao || cacBuoc.length" class="row g-3">
                <div v-if="nhom.dieu_kien_dau_vao" class="col-12" :class="{ 'col-md-6': cacBuoc.length }">
                  <div class="nhom-tong-quan__khoi h-100">
                    <h2 class="nhom-tong-quan__khoi-tieu-de">Điều kiện đầu vào</h2>
                    <p class="mb-0">{{ nhom.dieu_kien_dau_vao }}</p>
                  </div>
                </div>
                <div v-if="cacBuoc.length" class="col-12" :class="{ 'col-md-6': nhom.dieu_kien_dau_vao }">
                  <div class="nhom-tong-quan__khoi h-100">
                    <h2 class="nhom-tong-quan__khoi-tieu-de">Lộ trình phát triển</h2>
                    <ol class="lo-trinh">
                      <li v-for="(buoc, index) in cacBuoc" :key="index">{{ buoc }}</li>
                    </ol>
                  </div>
                </div>
              </div>
            </article>

            <div class="stages-card mt-3">
              <h2 class="stages-heading">
                Các nghề cụ thể trong nhóm
                <span v-if="dsNghe.length" class="chi-tiet-nhom__so-luong">{{ dsNghe.length }} nghề</span>
              </h2>

              <div v-if="dangTaiNghe" class="chi-tiet-nhom__trang-thai" role="status">Đang tải danh sách nghề…</div>
              <div v-else-if="loiNghe" class="chi-tiet-nhom__trang-thai">
                {{ loiNghe }}
                <button type="button" class="chi-tiet-nhom__thu-lai" @click="taiNghe">Thử lại</button>
              </div>
              <div v-else-if="!dsNghe.length" class="chi-tiet-nhom__trang-thai">
                Nhóm nghề này chưa có nghề cụ thể.
              </div>
              <div v-else class="row g-3">
                <div v-for="(nghe, index) in dsNghe" :key="nghe.id" class="col-12 col-md-6">
                  <article class="nghe-card h-100">
                    <span class="nghe-card__so" aria-hidden="true">{{ index + 1 }}</span>
                    <div class="nghe-card__noi-dung">
                      <h3 class="nghe-card__ten">{{ nghe.ten_nghe }}</h3>
                      <p v-if="nghe.mo_ta_ngan" class="nghe-card__mo-ta">{{ nghe.mo_ta_ngan }}</p>
                      <p v-if="nghe.yeu_cau_them" class="nghe-card__yeu-cau">
                        <strong>Yêu cầu thêm:</strong> {{ nghe.yeu_cau_them }}
                      </p>
                    </div>
                  </article>
                </div>
              </div>
            </div>
          </template>

          <div class="mt-3">
            <GoiYKhaoSat />
          </div>
        </div>

        <div class="col-lg-3">
          <nav class="paths-card" aria-labelledby="menu-nhom-nghe">
            <h2 id="menu-nhom-nghe" class="h4 mb-3">Các nhóm nghề đi làm</h2>
            <p v-if="!dangTaiNhom && !dsNhom.length" class="chi-tiet-nhom__menu-rong">Chưa có nhóm nghề.</p>
            <ul class="menu-nhom">
              <li v-for="item in dsNhom" :key="item.id">
                <RouterLink
                  class="menu-nhom__muc"
                  :class="[`menu-nhom__muc--${item.nhom_muc_tieu || 'khac'}`, { 'is-active': item.id === nhom?.id }]"
                  :to="{ name: tenRoute('thpt-di-lam-nhom-nghe'), params: { maNhom: item.ma_nhom } }"
                  :aria-current="item.id === nhom?.id ? 'page' : undefined"
                >
                  <span class="menu-nhom__ten">{{ item.ten_nhom }}</span>
                  <span v-if="item.nhom_muc_tieu" class="menu-nhom__muc-tieu">
                    {{ nhan(NHOM_MUC_TIEU, item.nhom_muc_tieu) }}
                  </span>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchNgheCuTheDiLam, fetchNhomNgheDiLam } from '@/api/nhomNgheDiLam'
import GoiYKhaoSat from './GoiYKhaoSat.vue'
import { LOAI_HINH_DAU_VAO, NHOM_MUC_TIEU, khoangLuong, nhan, soTrieu, thoiGianDaoTao } from './nhomNghe'
import { useTenRouteThpt } from '../useTenRouteThpt'

defineOptions({ name: 'ThptDiLamChiTietNhomNghe' })

const route = useRoute()
const { tenRoute } = useTenRouteThpt()

const dsNhom = ref([])
const dangTaiNhom = ref(false)
const loiNhom = ref('')
const dsNghe = ref([])
const dangTaiNghe = ref(false)
const loiNghe = ref('')

const maNhom = computed(() => String(route.params.maNhom || '').toUpperCase())
const nhom = computed(() => dsNhom.value.find((item) => item.ma_nhom === maNhom.value) || null)

// Lộ trình nhập dạng "Bước 1 → Bước 2 → ..." thì tách thành từng bước.
const cacBuoc = computed(() =>
  (nhom.value?.lo_trinh_phat_trien || '')
    .split(/\s*(?:→|->)\s*/)
    .map((buoc) => buoc.trim().replace(/\.$/, ''))
    .filter(Boolean),
)

async function taiNhomNghe() {
  dangTaiNhom.value = true
  loiNhom.value = ''
  try {
    const data = await fetchNhomNgheDiLam({ trang_thai: 1, page: 1, page_size: 100 })
    dsNhom.value = data.items || []
  } catch {
    loiNhom.value = 'Không tải được thông tin nhóm nghề.'
  } finally {
    dangTaiNhom.value = false
  }
}

async function taiNghe() {
  const id = nhom.value?.id
  dsNghe.value = []
  loiNghe.value = ''
  if (!id) return
  dangTaiNghe.value = true
  try {
    const data = await fetchNgheCuTheDiLam({ nhom_nghe_di_lam_id: id, page: 1, page_size: 100 })
    // Bỏ kết quả về muộn khi người dùng đã chuyển sang nhóm khác.
    if (nhom.value?.id === id) dsNghe.value = data.items || []
  } catch {
    if (nhom.value?.id === id) loiNghe.value = 'Không tải được danh sách nghề cụ thể.'
  } finally {
    if (nhom.value?.id === id) dangTaiNghe.value = false
  }
}

watch(() => nhom.value?.id, taiNghe)

onMounted(taiNhomNghe)
</script>

<style scoped>
.chi-tiet-nhom__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.chi-tiet-nhom__trang-thai a,
.chi-tiet-nhom__thu-lai {
  margin-left: 6px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.nhom-tong-quan {
  --mau-muc-tieu: var(--guest-primary);
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-top: 4px solid var(--mau-muc-tieu);
}

.nhom-tong-quan--kiem_tien_ngay,
.menu-nhom__muc--kiem_tien_ngay {
  --mau-muc-tieu: #d98a1c;
}

.nhom-tong-quan--thu_nhap_dot_pha,
.menu-nhom__muc--thu_nhap_dot_pha {
  --mau-muc-tieu: #1a66d1;
}

.nhom-tong-quan__quay-lai {
  align-self: flex-start;
  color: var(--guest-primary);
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
}

.nhom-tong-quan__quay-lai:hover {
  text-decoration: underline;
}

.nhom-tong-quan__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.nhom-tong-quan__muc-tieu,
.nhom-tong-quan__loai {
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 0.8rem;
  line-height: 1.3;
}

.nhom-tong-quan__muc-tieu {
  background: var(--mau-muc-tieu);
  color: #fff;
}

.nhom-tong-quan__loai {
  border: 1px solid #d7eadf;
  background: #fff;
  color: #3a4742;
}

.chi-tiet-nhom .nhom-tong-quan__ten {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.3;
}

.nhom-tong-quan__mo-ta {
  margin: 0;
  color: #3a4742;
  line-height: 1.6;
}

.nhom-tong-quan__thong-tin {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 0;
  padding: 14px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius);
  background: #fff;
}

.nhom-tong-quan__thong-tin dt {
  color: #6b7780;
  font-size: 0.75rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.nhom-tong-quan__thong-tin dd {
  margin: 4px 0 0;
  color: #1c2b23;
  font-weight: 600;
  line-height: 1.35;
}

.nhom-tong-quan__trien-vong {
  margin: 0;
  padding-left: 12px;
  border-left: 3px solid var(--mau-muc-tieu);
  color: #3a4742;
  font-style: italic;
  line-height: 1.5;
}

.nhom-tong-quan__khoi {
  padding: 14px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius);
  background: #fff;
  color: #3a4742;
  line-height: 1.55;
}

.chi-tiet-nhom .nhom-tong-quan__khoi-tieu-de {
  margin: 0 0 8px;
  font-size: 1.05rem;
  font-weight: 700;
}

.lo-trinh {
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: buoc;
}

.lo-trinh li {
  position: relative;
  padding: 0 0 10px 34px;
  counter-increment: buoc;
}

.lo-trinh li:last-child {
  padding-bottom: 0;
}

.lo-trinh li::before {
  content: counter(buoc);
  position: absolute;
  top: 0;
  left: 0;
  display: grid;
  place-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
}

/* Đường nối giữa các bước. */
.lo-trinh li:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 26px;
  bottom: 2px;
  left: 11px;
  width: 2px;
  background: rgba(var(--guest-primary-rgb), 0.3);
}

.chi-tiet-nhom__so-luong {
  margin-left: 8px;
  border-radius: 999px;
  padding: 2px 10px;
  background: rgba(var(--guest-primary-rgb), 0.12);
  font-size: 0.85rem;
  font-weight: 500;
  vertical-align: middle;
}

.nghe-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius);
  background: #fff;
  transition: box-shadow 0.3s ease;
}

.nghe-card:hover {
  box-shadow: 0 16px 32px rgba(31, 122, 77, 0.14);
}

.nghe-card__so {
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

.nghe-card__noi-dung {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.chi-tiet-nhom .nghe-card__ten {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.35;
}

.nghe-card__mo-ta {
  margin: 0;
  color: #3a4742;
  font-size: 0.95rem;
  line-height: 1.5;
}

.nghe-card__yeu-cau {
  margin: 0;
  padding: 6px 10px;
  border-radius: var(--guest-radius-sm);
  background: #f6fbf7;
  color: #3a4742;
  font-size: 0.875rem;
  line-height: 1.45;
}

.chi-tiet-nhom__menu-rong {
  color: #5b6770;
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
  --mau-muc-tieu: var(--guest-primary);
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid #d7eadf;
  border-left: 4px solid var(--mau-muc-tieu);
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
  border-left-color: var(--mau-muc-tieu);
  box-shadow: 0 0 0 1px var(--guest-primary);
}

.menu-nhom__muc:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

.menu-nhom__ten {
  color: var(--guest-primary);
  font-weight: 700;
  line-height: 1.35;
}

.menu-nhom__muc-tieu {
  color: #6b7780;
  font-size: 0.8rem;
}

@media (max-width: 767.98px) {
  .nhom-tong-quan__thong-tin {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 575.98px) {
  .chi-tiet-nhom .nhom-tong-quan__ten {
    font-size: 1.4rem;
  }

  .nhom-tong-quan__mo-ta {
    font-size: 0.95rem;
  }

  .nghe-card {
    padding: 14px;
  }
}
</style>
