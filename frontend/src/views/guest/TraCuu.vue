<template>
  <div class="landing">
    <section class="landing__section" aria-labelledby="tra-cuu-title">
      <div class="container-fluid">
        <div class="landing__head">
          <p class="landing__eyebrow">Tra cứu</p>
          <h1 id="tra-cuu-title" class="landing__title">Tra cứu trường, ngành và thông tin tuyển sinh</h1>
          <!-- <p class="landing__lead">
            Tìm nhanh trường đại học, cao đẳng, ngành đào tạo, phương thức tuyển sinh, tổ hợp môn, bài thi
            đánh giá năng lực và chứng chỉ ngoại ngữ.
          </p> -->
        </div>

        <div class="landing-explore__panel">
          <div
            class="landing-explore__filters flex-nowrap flex-md-wrap overflow-x-auto"
            role="tablist"
            aria-label="Loại tra cứu"
          >
            <button
              v-for="item in LOAI_TRA_CUU"
              :key="item.id"
              type="button"
              class="landing-explore__chip"
              :class="{ 'is-active': item.id === loai.id }"
              role="tab"
              :aria-selected="item.id === loai.id"
              aria-controls="tra-cuu-ket-qua"
              @click="chonLoai(item.id)"
            >
              {{ item.label }}
            </button>
          </div>

          <form class="tra-cuu__tim" role="search" @submit.prevent="timNgay">
            <div class="landing-explore__search tra-cuu__o-tim">
              <label class="landing-explore__o-nhap">
                <el-icon aria-hidden="true"><Search /></el-icon>
                <input v-model="tuKhoa" type="search" :placeholder="loai.placeholder" :aria-label="`Tìm ${loai.label}`" />
              </label>
              <CustomSelect v-if="loai.boLoc" :model-value="giaTriLoc" class="tra-cuu__loc" clearable
                :placeholder="`Tất cả ${loai.boLoc.label.toLowerCase()}`" :aria-label="loai.boLoc.label"
                @update:model-value="doiLoc">
                <CustomOption v-for="item in loai.boLoc.options" :key="item" :label="item" :value="item" />
              </CustomSelect>
              <button type="submit" class="landing__btn landing__btn--soft">Tìm kiếm</button>
            </div>
            
          </form>

          <div id="tra-cuu-ket-qua" role="tabpanel" aria-live="polite">
            <div class="tra-cuu__thanh-cong-cu">
              <p class="tra-cuu__dem">
                <template v-if="!dangTai && !loi && tong">
                  Tìm thấy <strong>{{ tong.toLocaleString('vi-VN') }}</strong> kết quả
                </template>
              </p>
              <div class="tra-cuu__kieu-xem" role="group" aria-label="Kiểu xem">
                <button
                  v-for="kieu in KIEU_XEM"
                  :key="kieu.id"
                  type="button"
                  :class="{ 'is-active': kieuXem === kieu.id }"
                  :aria-pressed="kieuXem === kieu.id"
                  :title="kieu.label"
                  @click="doiKieuXem(kieu.id)"
                >
                  <el-icon aria-hidden="true"><component :is="kieu.icon" /></el-icon>
                  <span>{{ kieu.label }}</span>
                </button>
              </div>
            </div>

            <div v-if="dangTai" class="row g-3" aria-busy="true">
              <div v-for="n in 8" :key="n" class="col-12 col-md-6 col-xl-4">
                <el-skeleton class="tra-cuu__khung-cho" animated :rows="3" />
              </div>
            </div>

            <KhongCoDuLieu v-else-if="loi" :text="loi">
              <button type="button" class="landing__btn landing__btn--soft" @click="taiDuLieu">Thử lại</button>
            </KhongCoDuLieu>

            <KhongCoDuLieu
              v-else-if="!danhSach.length"
              :text="route.query.q ? `Không tìm thấy kết quả cho “${route.query.q}”.` : 'Chưa có dữ liệu.'"
            />

            <!-- Lưới: 4 thẻ/hàng (desktop) → 2 (tablet) → 1 (mobile). -->
            <div v-else-if="kieuXem === 'luoi'" class="row g-3">
              <div v-for="item in danhSach" :key="item.id" class="col-12 col-md-6 col-xl-4">
                <TheTraCuu :the="item.the" :icon="loai.icon" @xem="moChiTiet(item)" />
              </div>
            </div>

            <CustomTable
              v-else
              :data="danhSach"
              row-key="id"
              stripe
              class="tra-cuu__bang"
              @row-click="moChiTiet"
            >
              <el-table-column label="Mã" width="120">
                <template #default="{ row }">
                  <span class="tra-cuu__bang-ma">{{ row.the.ma || '—' }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="loai.label" min-width="240">
                <template #default="{ row }">
                  <span class="tra-cuu__bang-ten">{{ row.the.tieuDe }}</span>
                </template>
              </el-table-column>
              <el-table-column v-if="coCotPhanLoai" label="Phân loại" min-width="200">
                <template #default="{ row }">{{ row.the.tags.join(' · ') }}</template>
              </el-table-column>
              <el-table-column v-if="coCotMoTa" label="Mô tả" min-width="280" show-overflow-tooltip>
                <template #default="{ row }">{{ row.the.moTa || '' }}</template>
              </el-table-column>
              <el-table-column label="" width="120" align="right">
                <template #default="{ row }">
                  <button type="button" class="tra-cuu__bang-xem" @click.stop="moChiTiet(row)">Xem chi tiết</button>
                </template>
              </el-table-column>
            </CustomTable>

            <div v-if="!dangTai && tong > PAGE_SIZE" class="tra-cuu__phan-trang">
              <CustomPagination
                :current-page="trang"
                :page-size="PAGE_SIZE"
                :total="tong"
                layout="total, prev, pager, next"
                background
                @update:current-page="doiTrang"
              />
            </div>
          </div>
        </div>

        <HoTroDinhHuong class="tra-cuu__ho-tro" />
      </div>
    </section>

    <!-- Modal chi tiết riêng theo loại tra cứu (components/guest/tra-cuu/chi-tiet). -->
    <component :is="chiTiet.modal" v-if="chiTiet" v-model="chiTietMo" :item="chiTiet.item" />
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, shallowRef, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import KhongCoDuLieu from '@/components/guest/chung/KhongCoDuLieu.vue'
import TheTraCuu from '@/components/guest/tra-cuu/TheTraCuu.vue'
import { LOAI_TRA_CUU, timLoaiTraCuu } from '@/components/guest/tra-cuu/loaiTraCuu'
import { traCuuDanhMuc } from '@/components/guest/tra-cuu/apiTraCuu'
import { MODAL_CHI_TIET_THEO_LOAI } from '@/components/guest/tra-cuu/chi-tiet'
import '@/components/guest/landing/landing.css'

defineOptions({ name: 'TraCuu' })

const PAGE_SIZE = 12

// Kiểu xem kết quả, lưu trên query ?xem=bang (mặc định lưới) như các bộ lọc khác.
const KIEU_XEM = [
  { id: 'luoi', label: 'Lưới', icon: 'Grid' },
  { id: 'bang', label: 'Bảng', icon: 'List' },
]

const route = useRoute()
const router = useRouter()

// Trạng thái tìm kiếm nằm trên query (?loai=&q=&page=&<boLoc.key>=) để chia sẻ link và quay lại được.
const loai = computed(() => timLoaiTraCuu(route.query.loai))
const trang = computed(() => Math.max(1, Number.parseInt(route.query.page, 10) || 1))
const giaTriLoc = computed(() => (loai.value.boLoc ? route.query[loai.value.boLoc.key] || '' : ''))
const kieuXem = computed(() => (route.query.xem === 'bang' ? 'bang' : 'luoi'))
// Cột "Phân loại" / "Mô tả" chỉ hiện khi trang kết quả có dữ liệu cho cột đó (vd. trường chưa có mô tả).
const coCotPhanLoai = computed(() => danhSach.value.some((item) => item.the.tags.length))
const coCotMoTa = computed(() => danhSach.value.some((item) => item.the.moTa))

const tuKhoa = ref(route.query.q || '')
const danhSach = ref([])
const tong = ref(0)
const dangTai = ref(false)
const loi = ref('')
const chiTietMo = ref(false)
// shallowRef: giữ component modal không bị bọc reactive.
const chiTiet = shallowRef(null)

let lanGoi = 0
let henGioTim = null

function capNhatQuery(thayDoi) {
  const query = { ...route.query, ...thayDoi }
  Object.keys(query).forEach((key) => {
    if (query[key] === '' || query[key] === null || query[key] === undefined) delete query[key]
  })
  router.replace({ name: 'tra-cuu', query })
}

function chonLoai(id) {
  if (id === loai.value.id) return
  // Bộ lọc riêng của loại cũ không áp dụng cho loại mới: chỉ giữ từ khóa.
  capNhatQuery({ loai: id, page: undefined, ...(loai.value.boLoc ? { [loai.value.boLoc.key]: undefined } : {}) })
}

function timNgay() {
  clearTimeout(henGioTim)
  capNhatQuery({ q: tuKhoa.value.trim(), page: undefined })
}

function doiLoc(value) {
  capNhatQuery({ [loai.value.boLoc.key]: value, page: undefined })
}

function doiKieuXem(kieu) {
  capNhatQuery({ xem: kieu === 'bang' ? 'bang' : undefined })
}

function doiTrang(page) {
  capNhatQuery({ page: page > 1 ? page : undefined })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function taiDuLieu() {
  const id = ++lanGoi
  const loaiHienTai = loai.value
  dangTai.value = true
  loi.value = ''
  try {
    const loc = loaiHienTai.boLoc && giaTriLoc.value ? { [loaiHienTai.boLoc.key]: giaTriLoc.value } : {}
    const data = await traCuuDanhMuc(loaiHienTai.id, {
      q: route.query.q,
      page: trang.value,
      pageSize: PAGE_SIZE,
      loc,
    })
    // Bỏ kết quả của lần gọi cũ khi người dùng đã đổi loại/từ khóa.
    if (id !== lanGoi) return
    danhSach.value = (data.items || []).map((item) => ({ ...item, the: loaiHienTai.the(item) }))
    tong.value = data.total || 0
  } catch (err) {
    if (id !== lanGoi) return
    danhSach.value = []
    tong.value = 0
    loi.value = err?.response?.data?.detail || 'Không tải được dữ liệu. Vui lòng thử lại.'
  } finally {
    if (id === lanGoi) dangTai.value = false
  }
}

function moChiTiet(item) {
  chiTiet.value = { modal: MODAL_CHI_TIET_THEO_LOAI[loai.value.id], item }
  chiTietMo.value = true
}

// Gõ từ khóa: tự tìm sau khi ngừng gõ.
watch(tuKhoa, (value) => {
  clearTimeout(henGioTim)
  if (value.trim() === (route.query.q || '')) return
  henGioTim = setTimeout(timNgay, 400)
})

watch(
  () => route.query,
  () => {
    if (route.name !== 'tra-cuu') return
    if ((route.query.q || '') !== tuKhoa.value.trim()) tuKhoa.value = route.query.q || ''
    taiDuLieu()
  },
  { immediate: true },
)

onUnmounted(() => clearTimeout(henGioTim))
</script>

<style scoped>
.tra-cuu__tim {
  --tra-cuu-tim-h: 40px;
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  gap: var(--lp-gap-sm);
  margin-bottom: var(--lp-gap);
}

.tra-cuu__o-tim {
  flex: 1 1 420px;
  margin-bottom: 0;
}

/* Đồng bộ chiều cao nhỏ hơn mặc định landing (48px) cho ô tìm / nút / select. */
.tra-cuu__tim :deep(.landing-explore__o-nhap),
.tra-cuu__tim :deep(.landing__btn) {
  min-height: var(--tra-cuu-tim-h);
  padding-top: 0;
  padding-bottom: 0;
}

.tra-cuu__loc {
  flex: 0 1 240px;
  min-width: 200px;
  align-self: stretch;
}

.tra-cuu__loc :deep(.el-select__wrapper) {
  min-height: var(--tra-cuu-tim-h);
  height: var(--tra-cuu-tim-h);
}

.tra-cuu__thanh-cong-cu {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--lp-gap-sm);
  margin-bottom: var(--lp-gap-sm);
}

.tra-cuu__dem {
  margin: 0;
  color: var(--lp-muted);
}

/* Chọn kiểu xem: hai nút liền nhau, nút đang chọn có nền nhạt. */
.tra-cuu__kieu-xem {
  display: inline-flex;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.18);
  border-radius: var(--lp-radius);
  background: #fff;
}

.tra-cuu__kieu-xem button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 0 12px;
  border: 0;
  background: transparent;
  color: var(--lp-muted);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.tra-cuu__kieu-xem button + button {
  border-left: 1px solid rgba(15, 23, 42, 0.18);
}

.tra-cuu__kieu-xem button:hover {
  color: var(--lp-primary-strong);
}

.tra-cuu__kieu-xem button.is-active {
  background: var(--lp-primary-soft);
  color: var(--lp-primary-strong);
  font-weight: 500;
}

.tra-cuu__khung-cho {
  padding: var(--lp-gap);
  border: 1px solid var(--lp-line);
  border-radius: var(--lp-radius);
  background: #fff;
}

.tra-cuu__bang :deep(.el-table__row) {
  cursor: pointer;
}

.tra-cuu__bang-ma {
  color: var(--lp-primary-strong);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.tra-cuu__bang-ten {
  color: var(--lp-ink);
  font-weight: 500;
}

.tra-cuu__bang-xem {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--lp-primary-strong);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
}

.tra-cuu__bang-xem:hover {
  text-decoration: underline;
}

.tra-cuu__ho-tro {
  margin-top: calc(var(--lp-gap) * 2);
}

.tra-cuu__phan-trang {
  display: flex;
  justify-content: center;
  margin-top: var(--lp-gap);
}

@media (max-width: 575.98px) {
  .tra-cuu__loc {
    flex: 1 1 100%;
  }
}
</style>
