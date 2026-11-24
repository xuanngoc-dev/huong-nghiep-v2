<template>
  <div class="landing">
    <section class="landing__section" aria-labelledby="tin-tuc-title">
      <div class="container-fluid">
        <div class="landing__head">
          <p class="landing__eyebrow">Tin tức</p>
          <h1 id="tin-tuc-title" class="landing__title">Tin tức tuyển sinh và hướng nghiệp</h1>
          <p class="landing__lead">
            Cập nhật thông tin tuyển sinh, kiến thức chọn ngành, chọn nghề và kỹ năng học tập.
          </p>
        </div>

        <div class="landing-explore__panel">
          <!-- Tab nhóm tin; nhóm đang chọn, từ khóa, trang lưu trên query (?nhom=&q=&page=) để chia sẻ link được. -->
          <div
            v-if="dsNhom.length"
            class="landing-explore__filters flex-nowrap flex-md-wrap overflow-x-auto"
            role="tablist"
            aria-label="Nhóm tin"
          >
            <button
              v-for="tab in dsTab"
              :key="tab.slug"
              type="button"
              class="landing-explore__chip"
              :class="{ 'is-active': tab.slug === nhomDangChon }"
              role="tab"
              :aria-selected="tab.slug === nhomDangChon"
              aria-controls="tin-tuc-ket-qua"
              @click="chonNhom(tab.slug)"
            >
              {{ tab.ten }}
              <span class="tin-tuc__so">{{ tab.soBai }}</span>
            </button>
          </div>

          <form class="landing-explore__search" role="search" @submit.prevent="timNgay">
            <label class="landing-explore__o-nhap">
              <el-icon aria-hidden="true"><Search /></el-icon>
              <input v-model="tuKhoa" type="search" placeholder="Tìm bài viết theo tiêu đề, tóm tắt…" aria-label="Tìm bài viết" />
            </label>
          </form>

          <div id="tin-tuc-ket-qua" role="tabpanel" aria-live="polite">
            <div v-if="dangTai" class="row g-3" aria-busy="true">
              <div v-for="n in 4" :key="n" class="col-12 col-md-6">
                <el-skeleton class="tin-tuc__khung-cho" animated>
                  <template #template>
                    <el-skeleton-item variant="image" class="tin-tuc__khung-cho-anh" />
                    <div class="tin-tuc__khung-cho-chu">
                      <el-skeleton-item variant="h3" style="width: 85%" />
                      <el-skeleton-item variant="text" style="width: 100%" />
                      <el-skeleton-item variant="text" style="width: 60%" />
                    </div>
                  </template>
                </el-skeleton>
              </div>
            </div>

            <KhongCoDuLieu v-else-if="loi" :text="loi">
              <button type="button" class="landing__btn landing__btn--soft" @click="taiDuLieu">Thử lại</button>
            </KhongCoDuLieu>

            <KhongCoDuLieu
              v-else-if="!dsNoiBat.length && !dsBai.length"
              :text="route.query.q ? `Không có bài viết nào khớp “${route.query.q}”.` : 'Chưa có bài viết.'"
            />

            <template v-else>
              <!-- Thẻ ngang như DoiTuongCard: 2 thẻ/hàng (tablet, desktop) → 1 (mobile).
                   Nổi bật chỉ ở tab "Tất cả", trang 1, không tìm kiếm. -->
              <template v-if="dsNoiBat.length">
                <h2 class="tin-tuc__muc">Nổi bật</h2>
                <div class="row g-3 tin-tuc__noi-bat">
                  <div v-for="bai in dsNoiBat" :key="bai.id" class="col-12 col-md-6">
                    <TheTinTuc :bai="bai" />
                  </div>
                </div>
              </template>

              <template v-if="dsBai.length">
                <h2 v-if="dsNoiBat.length" class="tin-tuc__muc">Mới nhất</h2>
                <div class="row g-3">
                  <div v-for="bai in dsBai" :key="bai.id" class="col-12 col-md-6">
                    <TheTinTuc :bai="bai" />
                  </div>
                </div>
              </template>

              <div v-if="tong > SO_BAI_MOI_TRANG" class="tin-tuc__phan-trang">
                <CustomPagination
                  :current-page="trang"
                  :page-size="SO_BAI_MOI_TRANG"
                  :total="tong"
                  layout="prev, pager, next"
                  background
                  @update:current-page="doiTrang"
                />
              </div>
            </template>
          </div>
        </div>

        <HoTroDinhHuong class="tin-tuc__ho-tro" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { tinTucCongKhaiApi } from '@/api/tinTuc'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import KhongCoDuLieu from '@/components/guest/chung/KhongCoDuLieu.vue'
import TheTinTuc from '@/components/guest/tin-tuc/TheTinTuc.vue'
import '@/components/guest/landing/landing.css'

defineOptions({ name: 'TinTuc' })

// Số chẵn: lưới 2 thẻ/hàng không bị lẻ.
const SO_BAI_MOI_TRANG = 10
const SO_NOI_BAT = 2
const TAT_CA = ''

const route = useRoute()
const router = useRouter()

const dsNhom = ref([])
const dsNoiBat = ref([])
const dsBai = ref([])
const tong = ref(0)
const dangTai = ref(false)
const loi = ref('')
const tuKhoa = ref(route.query.q || '')

// Slug nhóm trên query không còn hiển thị (nhóm đã ẩn, sai link) thì về "Tất cả".
const nhomDangChon = computed(() => {
  const slug = route.query.nhom || TAT_CA
  return !slug || dsNhom.value.some((nhom) => nhom.slug === slug) ? slug : TAT_CA
})
const trang = computed(() => Math.max(1, Number.parseInt(route.query.page, 10) || 1))

const dsTab = computed(() => [
  { slug: TAT_CA, ten: 'Tất cả', soBai: dsNhom.value.reduce((tongBai, nhom) => tongBai + nhom.so_bai_viet, 0) },
  ...dsNhom.value.map((nhom) => ({ slug: nhom.slug, ten: nhom.ten_nhom, soBai: nhom.so_bai_viet })),
])

let lanGoi = 0
let henGioTim = null

function capNhatQuery(thayDoi) {
  const query = { ...route.query, ...thayDoi }
  Object.keys(query).forEach((key) => {
    if (query[key] === '' || query[key] === null || query[key] === undefined) delete query[key]
  })
  router.replace({ name: 'tin-tuc', query })
}

function chonNhom(slug) {
  if (slug === nhomDangChon.value) return
  capNhatQuery({ nhom: slug || undefined, page: undefined })
}

function timNgay() {
  clearTimeout(henGioTim)
  capNhatQuery({ q: tuKhoa.value.trim(), page: undefined })
}

function doiTrang(page) {
  capNhatQuery({ page: page > 1 ? page : undefined })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function taiNhom() {
  try {
    dsNhom.value = await tinTucCongKhaiApi.nhomTin()
  } catch {
    // Không tải được nhóm: vẫn hiện danh sách bài (không có tab).
    dsNhom.value = []
  }
}

async function taiDuLieu() {
  const id = ++lanGoi
  dangTai.value = true
  loi.value = ''
  const q = route.query.q || undefined
  const nhom = nhomDangChon.value || undefined
  const coNoiBat = !nhom && !q && trang.value === 1
  try {
    const [ds, noiBat] = await Promise.all([
      tinTucCongKhaiApi.baiViet({ q, nhom, page: trang.value, page_size: SO_BAI_MOI_TRANG }),
      coNoiBat ? tinTucCongKhaiApi.baiViet({ is_noi_bat: 1, page: 1, page_size: SO_NOI_BAT }) : null,
    ])
    // Bỏ kết quả của lần gọi cũ khi người dùng đã đổi nhóm / từ khóa / trang.
    if (id !== lanGoi) return
    dsNoiBat.value = noiBat?.items || []
    // Bài nổi bật đã hiện ở khối trên thì không lặp lại trong "Mới nhất".
    const idNoiBat = new Set(dsNoiBat.value.map((bai) => bai.id))
    dsBai.value = (ds.items || []).filter((bai) => !idNoiBat.has(bai.id))
    tong.value = ds.total || 0
  } catch (err) {
    if (id !== lanGoi) return
    dsNoiBat.value = []
    dsBai.value = []
    tong.value = 0
    loi.value = err?.response?.data?.detail || 'Không tải được tin tức. Vui lòng thử lại.'
  } finally {
    if (id === lanGoi) dangTai.value = false
  }
}

// Gõ từ khóa: tự tìm sau khi ngừng gõ.
watch(tuKhoa, (value) => {
  clearTimeout(henGioTim)
  if (value.trim() === (route.query.q || '')) return
  henGioTim = setTimeout(timNgay, 400)
})

// Tải nhóm trước để biết slug nhóm trên query có hợp lệ không, rồi mới tải bài theo query.
const daCoNhom = taiNhom()
watch(
  () => route.query,
  async () => {
    if (route.name !== 'tin-tuc') return
    if ((route.query.q || '') !== tuKhoa.value.trim()) tuKhoa.value = route.query.q || ''
    await daCoNhom
    taiDuLieu()
  },
  { immediate: true },
)

onUnmounted(() => clearTimeout(henGioTim))
</script>

<style scoped>
.tin-tuc__so {
  margin-left: 6px;
  padding: 0 7px;
  border-radius: 999px;
  background: var(--lp-primary-soft);
  color: var(--lp-primary-strong);
  font-size: 0.8rem;
}

.landing-explore__chip.is-active .tin-tuc__so {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.tin-tuc__noi-bat {
  margin-bottom: var(--lp-gap);
}

.tin-tuc__muc {
  margin: 0 0 var(--lp-gap-sm, 12px);
  color: var(--lp-ink);
  font-size: 1.15rem;
  font-weight: 600;
}

/* Khung chờ cùng dáng thẻ ngang: ảnh trái 38%, chữ phải. */
.tin-tuc__khung-cho {
  display: flex;
  gap: 12px;
  overflow: hidden;
  border: 1px solid var(--lp-line);
  border-radius: var(--lp-radius);
  background: #fff;
}

.tin-tuc__khung-cho :deep(.tin-tuc__khung-cho-anh) {
  flex: 0 0 38%;
  height: 170px;
}

.tin-tuc__khung-cho-chu {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 10px;
  padding: 14px 12px 14px 0;
}

.tin-tuc__phan-trang {
  display: flex;
  justify-content: center;
  margin-top: var(--lp-gap);
}

.tin-tuc__ho-tro {
  margin-top: calc(var(--lp-gap) * 2);
}
</style>
