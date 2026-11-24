<template>
  <div class="landing">
    <section class="landing__section">
      <div class="container-fluid">
        <div v-if="dangTai" class="bai-viet" aria-busy="true">
          <el-skeleton animated :rows="10" />
        </div>

        <KhongCoDuLieu v-else-if="loi" :text="loi">
          <RouterLink class="landing__btn landing__btn--soft" :to="{ name: 'tin-tuc' }">Về trang tin tức</RouterLink>
        </KhongCoDuLieu>

        <template v-else-if="bai">
          <article class="bai-viet" aria-labelledby="bai-viet-tieu-de">
            <header class="bai-viet__dau">
              <RouterLink class="bai-viet__nhom" :to="{ name: 'tin-tuc', query: { nhom: bai.slug_nhom } }">
                {{ bai.ten_nhom }}
              </RouterLink>
              <h1 id="bai-viet-tieu-de" class="bai-viet__tieu-de">{{ bai.tieu_de }}</h1>
              <p class="bai-viet__meta">
                <time :datetime="bai.created_at">{{ dinhDangNgay(bai.created_at) }}</time>
                <template v-if="bai.tac_gia"><span aria-hidden="true">·</span> {{ bai.tac_gia }}</template>
                <span aria-hidden="true">·</span> {{ bai.luot_xem.toLocaleString('vi-VN') }} lượt xem
              </p>
              <p v-if="bai.tom_tat" class="bai-viet__tom-tat">{{ bai.tom_tat }}</p>
            </header>

            <img
              v-if="bai.anh_dai_dien"
              class="bai-viet__anh"
              :src="apiAssetUrl(bai.anh_dai_dien)"
              :alt="bai.tieu_de"
              decoding="async"
            />

            <!-- Nội dung đã lọc qua DOMPurify (lamSachHtml) trước khi hiển thị. -->
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div v-if="noiDung" class="bai-viet__noi-dung" v-html="noiDung" />

            <footer class="bai-viet__cuoi">
              <RouterLink class="bai-viet__quay-lai" :to="{ name: 'tin-tuc', query: { nhom: bai.slug_nhom } }">
                ← Xem thêm tin {{ bai.ten_nhom.toLowerCase() }}
              </RouterLink>
              <button type="button" class="landing__btn landing__btn--soft bai-viet__chia-se" @click="saoChepLienKet">
                <el-icon aria-hidden="true"><Link /></el-icon>
                {{ daSaoChep ? 'Đã sao chép liên kết' : 'Sao chép liên kết' }}
              </button>
            </footer>
          </article>

          <section v-if="bai.bai_lien_quan.length" class="bai-viet__lien-quan" aria-labelledby="bai-lien-quan-title">
            <h2 id="bai-lien-quan-title" class="bai-viet__lien-quan-tieu-de">Bài viết cùng chuyên mục</h2>
            <div class="row g-3">
              <div v-for="b in bai.bai_lien_quan" :key="b.id" class="col-12 col-md-6">
                <TheTinTuc :bai="b" />
              </div>
            </div>
          </section>
        </template>

        <HoTroDinhHuong class="bai-viet__ho-tro" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Link } from '@element-plus/icons-vue'
import { apiAssetUrl } from '@/api/apiUrl'
import { tinTucCongKhaiApi } from '@/api/tinTuc'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import KhongCoDuLieu from '@/components/guest/chung/KhongCoDuLieu.vue'
import TheTinTuc from '@/components/guest/tin-tuc/TheTinTuc.vue'
import { lamSachHtml } from '@/components/guest/tin-tuc/lamSachHtml'
import { dinhDangNgay } from '@/utils/thoiGian'
import '@/components/guest/landing/landing.css'

defineOptions({ name: 'TinTucChiTiet' })

const route = useRoute()

const bai = ref(null)
const dangTai = ref(false)
const loi = ref('')
const daSaoChep = ref(false)
let lanGoi = 0
let henGioSaoChep = null

const noiDung = computed(() => (bai.value?.noi_dung ? lamSachHtml(bai.value.noi_dung) : ''))

async function taiBai(slug) {
  const id = ++lanGoi
  dangTai.value = true
  loi.value = ''
  try {
    const data = await tinTucCongKhaiApi.chiTiet(slug)
    if (id !== lanGoi) return
    bai.value = data
    document.title = `${data.tieu_de} | Định hướng nghề`
  } catch (err) {
    if (id !== lanGoi) return
    bai.value = null
    // API trả 400 kèm detail khi không có bài (hoặc bài chưa xuất bản).
    loi.value = err?.response?.status === 400 ? 'Không tìm thấy bài viết hoặc bài đã ngừng hiển thị.' : 'Không tải được bài viết. Vui lòng thử lại.'
  } finally {
    if (id === lanGoi) dangTai.value = false
  }
}

async function saoChepLienKet() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    daSaoChep.value = true
    clearTimeout(henGioSaoChep)
    henGioSaoChep = setTimeout(() => {
      daSaoChep.value = false
    }, 2000)
  } catch {
    // Trình duyệt chặn clipboard (http, quyền): bỏ qua, người dùng tự sao chép trên thanh địa chỉ.
  }
}

// Bấm sang bài liên quan: cùng component, chỉ đổi slug → tải bài mới và lên đầu trang.
watch(
  () => route.params.slug,
  (slug) => {
    if (route.name !== 'tin-tuc-chi-tiet' || !slug) return
    taiBai(slug)
    window.scrollTo({ top: 0 })
  },
  { immediate: true },
)

onUnmounted(() => clearTimeout(henGioSaoChep))
</script>

<style scoped>
.bai-viet {
  margin: 0 auto;
}

.bai-viet__nhom {
  display: inline-block;
  margin-bottom: 10px;
  padding: 3px 10px;
  border-radius: 6px;
  background: var(--lp-primary-soft);
  color: var(--lp-primary-strong);
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-decoration: none;
  text-transform: uppercase;
}

.bai-viet__nhom:hover {
  text-decoration: underline;
}

.bai-viet__tieu-de {
  margin: 0;
  color: var(--lp-ink);
  font-size: clamp(1.5rem, 3vw, 2.1rem);
  font-weight: 700;
  line-height: 1.3;
}

.bai-viet__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 10px 0 0;
  color: var(--lp-muted);
  font-size: 0.875rem;
}

.bai-viet__tom-tat {
  margin: 16px 0 0;
  padding-left: 14px;
  border-left: 3px solid var(--lp-primary-strong);
  color: #2f3c36;
  font-size: 1.05rem;
  font-weight: 500;
  line-height: 1.6;
}

.bai-viet__anh {
  display: block;
  width: 100%;
  max-height: 460px;
  margin-top: 20px;
  border-radius: var(--lp-radius);
  object-fit: cover;
}

/* Kiểu chữ nội dung bài (HTML từ trình soạn thảo). */
.bai-viet__noi-dung {
  margin-top: 20px;
  color: #26332c;
  font-size: 1.02rem;
  line-height: 1.75;
  overflow-wrap: anywhere;
}

.bai-viet__noi-dung :deep(> * + *) {
  margin-top: 1em;
}

.bai-viet__noi-dung :deep(p) {
  margin-bottom: 0;
}

.bai-viet__noi-dung :deep(h2),
.bai-viet__noi-dung :deep(h3),
.bai-viet__noi-dung :deep(h4) {
  margin: 1.5em 0 0.5em;
  color: var(--lp-ink);
  font-weight: 700;
  line-height: 1.35;
}

.bai-viet__noi-dung :deep(h2) {
  font-size: 1.45rem;
}

.bai-viet__noi-dung :deep(h3) {
  font-size: 1.2rem;
}

.bai-viet__noi-dung :deep(h4) {
  font-size: 1.05rem;
}

.bai-viet__noi-dung :deep(ul),
.bai-viet__noi-dung :deep(ol) {
  margin-bottom: 0;
  padding-left: 1.5em;
}

.bai-viet__noi-dung :deep(li + li) {
  margin-top: 0.35em;
}

.bai-viet__noi-dung :deep(li p) {
  margin: 0;
}

.bai-viet__noi-dung :deep(a) {
  color: var(--lp-primary-strong);
  text-decoration: underline;
}

.bai-viet__noi-dung :deep(blockquote) {
  margin: 1.2em 0;
  padding: 10px 16px;
  border-left: 4px solid var(--lp-primary-strong);
  border-radius: 0 6px 6px 0;
  background: var(--lp-primary-soft);
}

.bai-viet__noi-dung :deep(img) {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 1.2em auto;
  border-radius: 6px;
}

.bai-viet__noi-dung :deep(hr) {
  margin: 2em 0;
  border: 0;
  border-top: 1px solid var(--lp-line);
}

/* Bảng rộng: cuộn ngang trong khung, không đẩy rộng trang. */
.bai-viet__noi-dung :deep(table) {
  display: block;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.bai-viet__noi-dung :deep(th),
.bai-viet__noi-dung :deep(td) {
  min-width: 120px;
  padding: 8px 12px;
  border: 1px solid var(--lp-line);
  vertical-align: top;
}

.bai-viet__noi-dung :deep(th) {
  background: var(--lp-primary-soft);
  color: var(--lp-ink);
  font-weight: 600;
  text-align: left;
}

.bai-viet__noi-dung :deep(th p),
.bai-viet__noi-dung :deep(td p) {
  margin: 0;
}

.bai-viet__cuoi {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid var(--lp-line);
}

.bai-viet__quay-lai {
  color: var(--lp-primary-strong);
  font-weight: 500;
  text-decoration: none;
}

.bai-viet__quay-lai:hover {
  text-decoration: underline;
}

.bai-viet__chia-se {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.bai-viet__lien-quan {
  margin-top: calc(var(--lp-gap) * 2);
}

.bai-viet__lien-quan-tieu-de {
  margin: 0 0 var(--lp-gap-sm, 12px);
  color: var(--lp-ink);
  font-size: 1.2rem;
  font-weight: 600;
}

.bai-viet__ho-tro {
  margin-top: calc(var(--lp-gap) * 2);
}
</style>
