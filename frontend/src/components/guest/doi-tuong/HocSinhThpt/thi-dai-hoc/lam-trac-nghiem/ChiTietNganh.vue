<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import anhMacDinh from '@/assets/guest/sinh-vien.jpg'

defineOptions({ name: 'ThptChiTietNganh' })

const NHAN_MUC = {
  mo_ta: 'Mô tả',
  ky_nang_phu_hop: 'Kỹ năng phù hợp',
  mon_hoc_tieu_bieu: 'Môn học tiêu biểu',
  co_hoi_nghe_nghiep: 'Cơ hội nghề nghiệp',
  muc_luong: 'Mức lương tham khảo',
  muc_luong_tham_khao: 'Mức lương tham khảo',
  cong_cu: 'Công cụ thường dùng',
  do_phu_hop: 'Độ phù hợp',
  diem_can_nhac: 'Điểm cân nhắc',
  truong_dao_tao: 'Các trường đào tạo',
  thoi_gian_dao_tao: 'Thời gian đào tạo',
}
const THU_TU_CHI_TIET = [
  'ky_nang_phu_hop',
  'mon_hoc_tieu_bieu',
  'co_hoi_nghe_nghiep',
  'cong_cu',
  'do_phu_hop',
  'diem_can_nhac',
  'truong_dao_tao',
]
const DA_HIEN = new Set(['mo_ta', 'muc_luong', 'muc_luong_tham_khao', 'thoi_gian_dao_tao'])

const route = useRoute()
const router = useRouter()
const ssid = computed(() => String(route.params.ssid || ''))
const maNganh = computed(() => String(route.params.maNganh || '').trim())
const dangTai = ref(false)
const loi = ref('')
const nganh = ref(null)
const anhHong = ref(false)

const anh = computed(() => {
  const url = String(nganh.value?.hinh_anh_mo_ta || '').trim()
  if (url && !anhHong.value) return url
  return anhMacDinh
})

function queryMaNganh() {
  const ma = route.query.ma_nganh
  return ma ? { ma_nganh: ma } : {}
}

function noiGiaTri(value) {
  if (Array.isArray(value)) {
    return value.map((item) => noiGiaTri(item)).filter(Boolean).join('\n')
  }
  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(([key, item]) => {
        const text = noiGiaTri(item)
        return text ? `${NHAN_MUC[key] || key}: ${text}` : ''
      })
      .filter(Boolean)
      .join('\n')
  }
  if (value == null) return ''
  return String(value).trim()
}

function docChiTiet(item) {
  const text = String(item?.chi_tiet || '').trim()
  if (!text.startsWith('{')) return { vanBan: text, json: null }
  try {
    const data = JSON.parse(text)
    if (data && typeof data === 'object' && !Array.isArray(data)) return { vanBan: '', json: data }
  } catch {
    /* Giữ nguyên đoạn văn khi chi tiết không phải JSON. */
  }
  return { vanBan: text, json: null }
}

const moTa = computed(() => {
  if (!nganh.value) return ''
  const { vanBan, json } = docChiTiet(nganh.value)
  return nganh.value.mo_ta || noiGiaTri(json?.mo_ta) || vanBan
})

const tomTat = computed(() => {
  if (!nganh.value) return []
  const { json } = docChiTiet(nganh.value)
  const holand = Array.isArray(nganh.value.ma_holand) ? nganh.value.ma_holand.filter(Boolean).join(', ') : ''
  return [
    { nhan: 'Mã ngành', giaTri: nganh.value.ma_nganh },
    { nhan: 'Nhóm ngành', giaTri: [nganh.value.ma_nhom_nganh, nganh.value.ten_nhom_nganh].filter(Boolean).join(' · ') },
    { nhan: 'Trình độ', giaTri: nganh.value.trinh_do },
    { nhan: 'Thời gian đào tạo', giaTri: nganh.value.thoi_gian_dao_tao || noiGiaTri(json?.thoi_gian_dao_tao) },
    { nhan: 'Mức lương tham khảo', giaTri: nganh.value.muc_luong_tham_khao || noiGiaTri(json?.muc_luong_tham_khao || json?.muc_luong) },
    { nhan: 'Nhu cầu việc làm', giaTri: nganh.value.nhan_dan },
    { nhan: 'Nhóm Holland', giaTri: holand },
  ].filter((item) => item.giaTri)
})

const mucChiTiet = computed(() => {
  if (!nganh.value) return []
  const { vanBan, json } = docChiTiet(nganh.value)
  const muc = []
  if (json) {
    const keys = [
      ...THU_TU_CHI_TIET.filter((key) => key in json),
      ...Object.keys(json).filter((key) => !DA_HIEN.has(key) && !THU_TU_CHI_TIET.includes(key)),
    ]
    for (const key of keys) {
      if (DA_HIEN.has(key)) continue
      const giaTri = noiGiaTri(json[key])
      if (giaTri) muc.push({ id: key, nhan: NHAN_MUC[key] || key, giaTri })
    }
  } else if (vanBan && nganh.value.mo_ta) {
    muc.push({ id: 'chi-tiet', nhan: 'Chi tiết', giaTri: vanBan })
  }
  return muc
})

function quayLai() {
  if (!ssid.value) {
    router.push({ name: 'thpt-thi-dai-hoc' })
    return
  }
  router.push({
    name: 'thpt-thi-dai-hoc-nganh-phu-hop',
    params: { ssid: ssid.value },
    query: queryMaNganh(),
  })
}

async function taiNganh(ma) {
  nganh.value = null
  anhHong.value = false
  loi.value = ''
  if (!ma) {
    loi.value = 'Không có mã ngành.'
    return
  }
  dangTai.value = true
  try {
    const data = await fetchNganh(
      { q: ma, trang_thai: 1, page: 1, page_size: 20 },
      { skipLoading: true },
    )
    const found = (data.items || []).find((item) => String(item.ma_nganh).toUpperCase() === ma.toUpperCase())
    if (!found) {
      loi.value = 'Không tìm thấy ngành này.'
      return
    }
    nganh.value = found
  } catch {
    loi.value = 'Không tải được thông tin ngành.'
  } finally {
    dangTai.value = false
  }
}

watch(maNganh, taiNganh, { immediate: true })
</script>

<template>
  <section class="quiz-flow py-4">
    <div class="container-fluid">
      <div class="holland-overview">
        <header class="holland-overview__header">
          <h2 class="holland-overview__title">Chi tiết ngành</h2>
          <p v-if="nganh" class="holland-overview__lead">
            {{ [nganh.ma_nhom_nganh, nganh.ten_nhom_nganh].filter(Boolean).join(' · ') || nganh.ten_nganh }}
          </p>
          <p v-else class="holland-overview__lead">Thông tin đào tạo theo mã ngành trên đường dẫn.</p>
        </header>

        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải thông tin ngành…</p>

        <template v-else-if="nganh">
          <article class="major-detail">
            <img class="major-detail__image" :src="anh" :alt="`Hình minh họa ngành ${nganh.ten_nganh}`" @error="anhHong = true" />
            <div class="major-detail__intro">
              <p class="major-detail__code">{{ nganh.ma_nganh }}</p>
              <h3 class="major-detail__name">{{ nganh.ten_nganh }}</h3>
              <p v-if="nganh.ten_tieng_anh" class="major-detail__en">{{ nganh.ten_tieng_anh }}</p>
              <p class="major-detail__text">{{ moTa || 'Chưa có mô tả cho ngành này.' }}</p>
            </div>
          </article>

          <dl v-if="tomTat.length" class="major-facts">
            <div v-for="item in tomTat" :key="item.nhan" class="major-facts__item">
              <dt>{{ item.nhan }}</dt>
              <dd>{{ item.giaTri }}</dd>
            </div>
          </dl>

          <article v-for="muc in mucChiTiet" :key="muc.id" class="major-section">
            <h3>{{ muc.nhan }}</h3>
            <p>{{ muc.giaTri }}</p>
          </article>
        </template>

        <div class="major-nav">
          <button type="button" class="btn btn-outline-success" @click="quayLai">Quay lại ngành phù hợp</button>
        </div>
      </div>
    </div>
  </section>
</template>

<style src="./quiz-type.scss"></style>

<style scoped>
.major-detail {
  display: flex;
  align-items: stretch;
  gap: 18px;
  margin-top: 28px;
  padding: 16px;
  border: 1px solid #c5d5cc;
  border-radius: 12px;
  background: #f6faf7;
  box-shadow: 0 8px 22px rgba(28, 43, 35, 0.08);
}

.major-detail__image {
  flex: 0 0 280px;
  width: 280px;
  height: 180px;
  object-fit: cover;
  border-radius: 10px;
  background: #e7edf2;
}

.major-detail__intro {
  flex: 1;
  min-width: 0;
}

.major-detail__code {
  display: inline-block;
  margin: 0 0 6px;
  padding: 2px 10px;
  border-radius: 999px;
  background: #0c5c34;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.major-detail__name {
  margin: 0;
  color: #0c5c34;
  font-size: 1.45rem;
  font-weight: 700;
  line-height: 1.3;
}

.major-detail__en {
  margin: 4px 0 0;
  color: #3d5c4c;
  font-size: 1rem;
  line-height: 1.4;
}

.major-detail__text {
  margin: 10px 0 0;
  color: #1c2836;
  font-size: 1rem;
  line-height: 1.55;
  white-space: pre-line;
}

.major-facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
  margin: 16px 0 0;
}

.major-facts__item {
  margin: 0;
  padding: 12px 14px;
  border: 1px solid #c5d5cc;
  border-radius: 10px;
  background: #fff;
}

.major-facts__item dt {
  margin: 0;
  color: #31483d;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.major-facts__item dd {
  margin: 4px 0 0;
  color: #121a28;
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.45;
  white-space: pre-line;
}

.major-section {
  margin-top: 16px;
  padding: 16px 18px;
  border: 1px solid #c5d5cc;
  border-radius: 12px;
  background: #fff;
}

.major-section h3 {
  margin: 0;
  color: #0c5c34;
  font-size: 1.1rem;
  font-weight: 700;
}

.major-section p {
  margin: 8px 0 0;
  color: #1c2836;
  font-size: 1rem;
  line-height: 1.55;
  white-space: pre-line;
}

.major-nav {
  margin-top: 28px;
}

@media (max-width: 575.98px) {
  .major-detail {
    flex-direction: column;
  }

  .major-detail__image {
    flex-basis: auto;
    width: 100%;
    height: 160px;
  }
}
</style>
