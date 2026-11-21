<template>
  <div class="landing">
    <section class="landing__section" aria-labelledby="tra-cuu-title">
      <div class="container-fluid">
        <div class="landing__head">
          <p class="landing__eyebrow">Tra cứu</p>
          <h1 id="tra-cuu-title" class="landing__title">Tra cứu trường, ngành và thông tin tuyển sinh</h1>
          <p class="landing__lead">
            Tìm nhanh trường đại học, cao đẳng, ngành đào tạo, phương thức tuyển sinh, tổ hợp môn, bài thi
            đánh giá năng lực và chứng chỉ ngoại ngữ.
          </p>
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
              <el-icon aria-hidden="true"><Search /></el-icon>
              <input v-model="tuKhoa" type="search" :placeholder="loai.placeholder" :aria-label="`Tìm ${loai.label}`" />
              <button type="submit" class="landing__btn landing__btn--soft">Tìm kiếm</button>
            </div>
            <CustomSelect
              v-if="loai.boLoc"
              :model-value="giaTriLoc"
              class="tra-cuu__loc"
              clearable
              :placeholder="`Tất cả ${loai.boLoc.label.toLowerCase()}`"
              :aria-label="loai.boLoc.label"
              @update:model-value="doiLoc"
            >
              <CustomOption v-for="item in loai.boLoc.options" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </form>

          <div id="tra-cuu-ket-qua" role="tabpanel" aria-live="polite">
            <p v-if="!dangTai && !loi && tong" class="tra-cuu__dem">
              Tìm thấy <strong>{{ tong.toLocaleString('vi-VN') }}</strong> kết quả
            </p>

            <div v-if="dangTai" class="row g-3" aria-busy="true">
              <div v-for="n in 6" :key="n" class="col-12 col-md-6 col-xl-4">
                <el-skeleton class="tra-cuu__the" animated :rows="3" />
              </div>
            </div>

            <KhongCoDuLieu v-else-if="loi" :text="loi">
              <button type="button" class="landing__btn landing__btn--soft" @click="taiDuLieu">Thử lại</button>
            </KhongCoDuLieu>

            <KhongCoDuLieu
              v-else-if="!danhSach.length"
              :text="route.query.q ? `Không tìm thấy kết quả cho “${route.query.q}”.` : 'Chưa có dữ liệu.'"
            />

            <div v-else class="row g-3">
              <div v-for="item in danhSach" :key="item.id" class="col-12 col-md-6 col-xl-4">
                <button type="button" class="tra-cuu__the" @click="moChiTiet(item)">
                  <span class="tra-cuu__the-dau">
                    <strong class="tra-cuu__the-ten">{{ item.the.tieuDe }}</strong>
                    <span v-if="item.the.ma" class="tra-cuu__the-ma">{{ item.the.ma }}</span>
                  </span>
                  <span v-if="item.the.tags.length" class="tra-cuu__the-tags">
                    <span v-for="tag in item.the.tags" :key="tag" class="landing-explore__pill">{{ tag }}</span>
                  </span>
                  <span v-if="item.the.moTa" class="tra-cuu__the-mo-ta">{{ item.the.moTa }}</span>
                  <span class="lp-link">Xem chi tiết <el-icon aria-hidden="true"><Right /></el-icon></span>
                </button>
              </div>
            </div>

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
      </div>
    </section>

    <CustomDialog v-model="chiTietMo" :title="chiTiet?.the.tieuDe || ''" :width="720">
      <dl v-if="chiTiet" class="tra-cuu__chi-tiet">
        <template v-for="row in chiTiet.dong" :key="row.label">
          <dt>{{ row.label }}</dt>
          <dd>
            <a v-if="row.link" :href="row.value" target="_blank" rel="noopener noreferrer">{{ row.value }}</a>
            <template v-else>{{ row.value }}</template>
          </dd>
        </template>
      </dl>
    </CustomDialog>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Right, Search } from '@element-plus/icons-vue'
import KhongCoDuLieu from '@/components/guest/chung/KhongCoDuLieu.vue'
import { LOAI_TRA_CUU, timLoaiTraCuu } from '@/components/guest/tra-cuu/loaiTraCuu'
import { traCuuDanhMuc } from '@/components/guest/tra-cuu/apiTraCuu'
import '@/components/guest/landing/landing.css'

defineOptions({ name: 'TraCuu' })

const PAGE_SIZE = 12

const route = useRoute()
const router = useRouter()

// Trạng thái tìm kiếm nằm trên query (?loai=&q=&page=&<boLoc.key>=) để chia sẻ link và quay lại được.
const loai = computed(() => timLoaiTraCuu(route.query.loai))
const trang = computed(() => Math.max(1, Number.parseInt(route.query.page, 10) || 1))
const giaTriLoc = computed(() => (loai.value.boLoc ? route.query[loai.value.boLoc.key] || '' : ''))

const tuKhoa = ref(route.query.q || '')
const danhSach = ref([])
const tong = ref(0)
const dangTai = ref(false)
const loi = ref('')
const chiTietMo = ref(false)
const chiTiet = ref(null)

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
  chiTiet.value = { the: item.the, dong: loai.value.chiTiet(item) }
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
  display: flex;
  flex-wrap: wrap;
  gap: var(--lp-gap-sm);
  margin-bottom: var(--lp-gap);
}

.tra-cuu__o-tim {
  flex: 1 1 420px;
  margin-bottom: 0;
}

.tra-cuu__loc {
  flex: 0 1 240px;
  min-width: 200px;
  align-self: center;
}

.tra-cuu__dem {
  margin-bottom: var(--lp-gap-sm);
  color: var(--lp-muted);
}

.tra-cuu__the {
  display: flex;
  flex-direction: column;
  gap: var(--lp-gap-sm);
  width: 100%;
  height: 100%;
  padding: var(--lp-gap);
  border: 1px solid var(--lp-line);
  border-radius: var(--lp-radius);
  background: #fff;
  color: var(--lp-ink);
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

button.tra-cuu__the:hover,
button.tra-cuu__the:focus-visible {
  border-color: rgba(var(--lp-primary-rgb), 0.4);
  box-shadow: var(--lp-shadow-sm);
}

.tra-cuu__the-dau {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--lp-gap-sm);
}

.tra-cuu__the-ten {
  font-weight: 600;
  line-height: 1.4;
}

.tra-cuu__the-ma {
  flex-shrink: 0;
  padding: 0.1rem 0.5rem;
  border-radius: 6px;
  background: var(--lp-soft);
  color: var(--lp-primary-strong);
  font-size: 0.85rem;
  font-weight: 500;
}

.tra-cuu__the-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--lp-gap-xs);
}

.tra-cuu__the-tags .landing-explore__pill {
  padding: 0.25rem 0.6rem;
  font-size: 0.82rem;
}

.tra-cuu__the-mo-ta {
  display: -webkit-box;
  overflow: hidden;
  color: var(--lp-muted);
  font-size: 0.92rem;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
}

.tra-cuu__the .lp-link {
  margin-top: auto;
}

.tra-cuu__phan-trang {
  display: flex;
  justify-content: center;
  margin-top: var(--lp-gap);
}

.tra-cuu__chi-tiet {
  display: grid;
  grid-template-columns: minmax(140px, 200px) 1fr;
  gap: 0.6rem 1rem;
  margin: 0;
}

.tra-cuu__chi-tiet dt {
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.tra-cuu__chi-tiet dd {
  margin: 0;
  white-space: pre-line;
  overflow-wrap: anywhere;
}

@media (max-width: 575.98px) {
  .tra-cuu__loc {
    flex: 1 1 100%;
  }

  .tra-cuu__chi-tiet {
    grid-template-columns: 1fr;
    gap: 0.15rem;
  }

  .tra-cuu__chi-tiet dd {
    margin-bottom: 0.6rem;
  }
}
</style>
