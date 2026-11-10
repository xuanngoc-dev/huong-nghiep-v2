<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchTruongHoc } from '@/api/truongHoc'
import anhMacDinh from '@/assets/guest/sinh-vien.jpg'
import { docChiTiet, layChiTiet, noiGiaTri } from './chi-tiet/chiTiet'

defineOptions({ name: 'ThptChiTietTruong' })

const TABS = [
  { id: 'tong-quan', nhan: 'Tổng quan' },
  { id: 'quy-che', nhan: 'Quy chế tuyển sinh' },
  { id: 'phuong-thuc', nhan: 'Phương thức tuyển sinh' },
  { id: 'lo-trinh', nhan: 'Lộ trình chi tiết' },
  { id: 'danh-gia', nhan: 'Đánh giá & nhận xét' },
]

const route = useRoute()
const router = useRouter()
const ssid = computed(() => String(route.params.ssid || ''))
const maTruong = computed(() => String(route.params.maTruong || '').trim())
const maNganh = computed(() => String(route.query.ma_nganh || '').trim())

const dangTai = ref(false)
const loi = ref('')
const truong = ref(null)
const nganh = ref(null)
const anhHong = ref(false)
const tabDangChon = ref(TABS[0].id)

const tenNganh = computed(() => String(nganh.value?.ten_nganh || '').trim())

const moTaNganh = computed(() => {
  const item = nganh.value
  if (!item) return ''
  const { vanBan, json } = docChiTiet(item)
  return String(item.mo_ta || '').trim() || noiGiaTri(layChiTiet(json, ['tong_quan', 'mo_ta'])) || vanBan
})

const hienMoTaNganh = computed(() => tabDangChon.value === 'tong-quan' && Boolean(moTaNganh.value))

const anh = computed(() => {
  const url = String(truong.value?.anh_dai_dien_url || truong.value?.logo_url || '').trim()
  if (url && !anhHong.value) return url
  return anhMacDinh
})

function noi(value) {
  if (Array.isArray(value)) return value.map((item) => String(item || '').trim()).filter(Boolean).join(' · ')
  if (value == null) return ''
  return String(value).trim()
}

function hrefLienKet(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  if (/^(https?:|mailto:|tel:)/i.test(text)) return text
  return `https://${text}`
}

function dong(nhan, value, href = '') {
  const text = noi(value)
  if (!text) return null
  return { nhan, text, href }
}

const tomTat = computed(() => {
  const item = truong.value
  if (!item) return []
  return [
    dong('Loại cơ sở', item.loai_co_so),
    dong('Loại hình', item.loai_hinh),
    dong('Khu vực', [item.vung_mien, item.ten_tinh_thanh].filter(Boolean).join(' · ')),
    dong('Năm thành lập', item.nam_thanh_lap),
  ].filter(Boolean)
})

const tongQuan = computed(() => {
  const item = truong.value
  if (!item) return []
  const linhVuc = [...(item.linh_vuc_dao_tao_chinh || []), ...(item.linh_vuc_dao_tao_khac || [])]
  return [
    dong('Tên viết tắt', item.ten_viet_tat),
    dong('Tên gọi khác', item.ten_goi_khac),
    dong('Cơ quan chủ quản', item.co_quan_chu_quan),
    dong('Bậc đào tạo', item.bac_dao_tao),
    dong('Lĩnh vực đào tạo', [...new Set(linhVuc.map((tag) => String(tag || '').trim()).filter(Boolean))]),
    dong('Giới thiệu', item.gioi_thieu_ngan),
    dong('Giới thiệu chi tiết', item.gioi_thieu_chi_tiet),
    dong('Thế mạnh', item.the_manh),
    dong('Địa chỉ', [item.dia_chi_tru_so, item.ten_phuong_xa, item.ten_tinh_thanh].filter(Boolean).join(', ')),
    dong('Điện thoại', item.so_dien_thoai, item.so_dien_thoai ? `tel:${String(item.so_dien_thoai).replace(/\s/g, '')}` : ''),
    dong('Email', item.email, item.email ? `mailto:${item.email}` : ''),
    dong('Website', item.website, hrefLienKet(item.website)),
  ].filter(Boolean)
})

const hangTab = computed(() => (tabDangChon.value === 'tong-quan' ? tongQuan.value : []))

function idTab(id) {
  return `school-tab-${maTruong.value}-${id}`
}

function quayLai() {
  if (ssid.value && maNganh.value) {
    router.push({
      name: 'thpt-thi-dai-hoc-chi-tiet-nganh',
      params: { ssid: ssid.value, maNganh: maNganh.value },
    })
    return
  }
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push({ name: 'thpt-thi-dai-hoc' })
}

let lanTai = 0
let lanTaiNganh = 0

async function taiNganh(ma) {
  const lan = ++lanTaiNganh
  nganh.value = null
  if (!ma) return
  try {
    const data = await fetchNganh({ q: ma, trang_thai: 1, page: 1, page_size: 20 }, { skipLoading: true })
    if (lan !== lanTaiNganh) return
    nganh.value = (data.items || []).find((item) => String(item.ma_nganh).toUpperCase() === ma.toUpperCase()) || null
  } catch {
    if (lan !== lanTaiNganh) return
    nganh.value = null
  }
}

async function taiTruong(ma) {
  const lan = ++lanTai
  truong.value = null
  anhHong.value = false
  loi.value = ''
  tabDangChon.value = TABS[0].id
  if (!ma) {
    loi.value = 'Không có mã trường.'
    return
  }
  dangTai.value = true
  try {
    const data = await fetchTruongHoc({ q: ma, page: 1, page_size: 20 }, { skipLoading: true })
    if (lan !== lanTai) return
    const found = (data.items || []).find((item) => String(item.ma_truong).toUpperCase() === ma.toUpperCase())
    if (!found) {
      loi.value = 'Không tìm thấy trường này.'
      return
    }
    truong.value = found
  } catch {
    if (lan !== lanTai) return
    loi.value = 'Không tải được thông tin trường.'
  } finally {
    if (lan === lanTai) dangTai.value = false
  }
}

watch(maTruong, taiTruong, { immediate: true })
watch(maNganh, taiNganh, { immediate: true })
</script>

<template>
  <section class="quiz-flow">
    <div class="container-fluid">
      <div class="holland-overview">
        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải thông tin trường…</p>

        <template v-else-if="truong">
          <article class="major-detail">
            <div class="major-detail__head">
              <img class="major-detail__image" :src="anh" :alt="`Hình minh họa ${truong.ten_truong}`" @error="anhHong = true" />
              <div class="major-detail__intro">
                <p class="major-detail__code">{{ truong.ma_truong }}</p>
                <h3 class="major-detail__name">{{ truong.ten_truong }}</h3>
                <p v-if="truong.ten_tieng_anh" class="major-detail__en">{{ truong.ten_tieng_anh }}</p>
                <div v-if="tenNganh" class="major-detail__tags">
                  <CustomTag type="success" effect="plain">{{ tenNganh }}</CustomTag>
                </div>
                <p class="major-detail__text">{{ truong.gioi_thieu_ngan || 'Chưa có giới thiệu cho trường này.' }}</p>
                <dl v-if="tomTat.length" class="major-facts">
                  <div v-for="item in tomTat" :key="item.nhan" class="major-facts__item">
                    <dt>{{ item.nhan }}</dt>
                    <dd>{{ item.text }}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </article>

          <div class="major-tabs">
            <div class="major-tabs__bar" role="tablist" aria-label="Nội dung chi tiết trường">
              <button
                v-for="tab in TABS"
                :id="idTab(tab.id)"
                :key="tab.id"
                type="button"
                role="tab"
                class="major-tabs__pill"
                :class="{ 'is-active': tabDangChon === tab.id }"
                :aria-selected="tabDangChon === tab.id"
                :aria-controls="`school-panel-${maTruong}-${tab.id}`"
                :tabindex="tabDangChon === tab.id ? 0 : -1"
                @click="tabDangChon = tab.id"
              >
                {{ tab.nhan }}
              </button>
            </div>
            <div
              :id="`school-panel-${maTruong}-${tabDangChon}`"
              class="major-tabs__panel"
              role="tabpanel"
              :aria-labelledby="idTab(tabDangChon)"
            >
              <section v-if="hienMoTaNganh" class="nganh-mo-ta">
                <h3>Ngành {{ tenNganh }}</h3>
                <p>{{ moTaNganh }}</p>
              </section>
              <dl v-if="hangTab.length" class="truong-chi-tiet">
                <div v-for="item in hangTab" :key="item.nhan" class="truong-chi-tiet__row">
                  <dt>{{ item.nhan }}</dt>
                  <dd>
                    <a v-if="item.href" :href="item.href" target="_blank" rel="noopener noreferrer">{{ item.text }}</a>
                    <template v-else>{{ item.text }}</template>
                  </dd>
                </div>
              </dl>
              <KhongCoDuLieu v-else-if="!hienMoTaNganh" text="Chưa có thông tin cho mục này." />
            </div>
          </div>
        </template>

        <div class="major-nav">
          <button type="button" class="btn btn-outline-success" @click="quayLai">Quay lại chi tiết ngành</button>
        </div>
      </div>
    </div>
  </section>
</template>

<style src="./quiz-type.scss"></style>

<style scoped>
.major-detail__tags {
  margin-top: 10px;
}

.major-detail__tags :deep(.el-tag) {
  height: auto;
  padding-top: 4px;
  padding-bottom: 4px;
  white-space: normal;
  line-height: 1.4;
}

.nganh-mo-ta {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #c5d5cc;
}

.nganh-mo-ta h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.05rem;
  font-weight: 700;
}

.nganh-mo-ta p {
  margin: 8px 0 0;
  color: #1c2836;
  line-height: 1.55;
  white-space: pre-line;
}

.truong-chi-tiet {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
}

.truong-chi-tiet__row {
  display: grid;
  grid-template-columns: minmax(140px, 220px) minmax(0, 1fr);
  gap: 8px 16px;
  margin: 0;
}

.truong-chi-tiet dt {
  margin: 0;
  color: #5a7266;
  font-weight: 400;
}

.truong-chi-tiet dd {
  margin: 0;
  color: #1c2836;
  line-height: 1.5;
  white-space: pre-line;
}

.truong-chi-tiet a {
  color: #0c5c34;
  word-break: break-all;
}

@media (max-width: 575.98px) {
  .truong-chi-tiet__row {
    grid-template-columns: 1fr;
    gap: 2px;
  }
}
</style>
