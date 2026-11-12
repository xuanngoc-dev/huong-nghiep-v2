<template>
<section class="chua-co">
    <div class="container-fluid">
      <div class="row g-4 mt-1">
        <div class="col-lg-9">
          <article class="intro-card">
            <div class="row g-3 align-items-center">
              <div class="col-md-5">
                <img
                  class="intro-card__image"
                  :src="anhChuaCo"
                  alt="Nhóm học sinh cùng tìm hiểu một nghề thực hành"
                />
              </div>
              <div class="col-md-7">
                <div class="intro-card__body">
                  <h2 class="h2 intro-card__title">Bạn chưa rõ mình phù hợp với ngành nghề nào?</h2>
                  <p class="intro-card__lead">
                    Làm khảo sát để hệ thống gợi ý ngành đào tạo gần với sở thích và năng lực của bạn.
                  </p>
                  <ol class="intro-card__steps">
                    <li>
                      <span class="intro-card__step-num" aria-hidden="true">1</span>
                      <span>Làm bài trắc nghiệm Holland để hiểu nhóm tính cách nổi bật của bạn.</span>
                    </li>
                    <li>
                      <span class="intro-card__step-num" aria-hidden="true">2</span>
                      <span>Đối chiếu kết quả với các ngành đào tạo phù hợp.</span>
                    </li>
                  </ol>
                  <div class="intro-card__actions">
                    <CustomButton type="primary" class="intro-card__cta" @click="moHuongDan">
                      Bắt đầu khảo sát
                      <span class="intro-card__cta-arrow" aria-hidden="true">→</span>
                    </CustomButton>
                  </div>
                </div>
              </div>
            </div>
          </article>


          <article class="stages-card mt-3">
            <h2 class="h4 mb-2">Nhóm ngành nghề</h2>
            <p class="text-secondary mb-3">Các nhóm ngành nghề để bạn tham khảo trước khi làm khảo sát.</p>
            <p v-if="loiHolland" class="holland-note holland-note__text mb-0">{{ loiHolland }}</p>
            <p v-else-if="dangTaiHolland" class="text-secondary mb-0">Đang tải nhóm ngành nghề…</p>
            <KhongCoDuLieu v-else-if="!nhomHolland.length" text="Chưa có nhóm ngành nghề." />
            <div v-else class="row g-3">
              <div v-for="item in nhomHolland" :key="item.id" class="col-12 col-md-6 col-lg-4">
                <div class="the-card">
                  <CardNganhDaoTao
                    class="h-100"
                    :ma="item.ma_nhom"
                    :ten="item.ten_nhom"
                    :ten-tieng-anh="item.ten_tieng_anh"
                    :mo-ta="moTaHolland(item)"
                    :hinh-anh="item.hinh_anh_mo_ta || ''"
                    :khoa="item.id"
                  />
                  <div class="the-card__veil">
                    <CustomButton
                      class="the-card__detail"
                      :aria-label="`Chi tiết nhóm ${item.ten_nhom}`"
                      @click="moChiTiet('holland', item)"
                    >
                      Chi tiết
                    </CustomButton>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <article class="stages-card mt-3">
            <h2 class="h4 mb-2">Ngành nghề nổi bật</h2>
            <p class="text-secondary mb-3">Một số ngành nhiều thí sinh đang tìm hiểu, để bạn tham khảo trước khi làm khảo sát.</p>
            <div
              v-if="nhomHolland.length"
              class="nhom-pills"
              role="tablist"
              aria-label="Nhóm ngành nghề"
            >
              <button
                v-for="nhom in nhomHolland"
                :id="`nhom-nghe-${nhom.ma_nhom}`"
                :key="nhom.ma_nhom"
                type="button"
                role="tab"
                class="nhom-pills__item"
                :class="{ 'is-active': maNhomDangChon === nhom.ma_nhom }"
                :aria-selected="maNhomDangChon === nhom.ma_nhom"
                :aria-controls="`nganh-nhom-${nhom.ma_nhom}`"
                :tabindex="maNhomDangChon === nhom.ma_nhom ? 0 : -1"
                @click="maNhomDangChon = nhom.ma_nhom"
                @keydown="dieuHuongNhom"
              >
                {{ nhom.ten_nhom }}
              </button>
            </div>
            <p v-if="loiNganh" class="holland-note holland-note__text mb-0">{{ loiNganh }}</p>
            <p v-else-if="dangTaiNganh || dangTaiHolland" class="text-secondary mb-0">Đang tải ngành…</p>
            <KhongCoDuLieu
              v-else-if="!nganhNoiBat.length"
              :text="maNhomDangChon ? 'Chưa có ngành nổi bật trong nhóm này.' : 'Chưa có ngành nổi bật.'"
            />
            <div
              v-else
              class="row g-3"
              :id="maNhomDangChon ? `nganh-nhom-${maNhomDangChon}` : undefined"
              :role="maNhomDangChon ? 'tabpanel' : undefined"
              :aria-labelledby="maNhomDangChon ? `nhom-nghe-${maNhomDangChon}` : undefined"
            >
              <div v-for="item in nganhNoiBat" :key="item.id" class="col-12 col-md-6 col-lg-4">
                <div class="the-card">
                  <CardNganhDaoTao
                    class="h-100"
                    :ma="item.ma_nganh"
                    :ten="item.ten_nganh"
                    :ten-tieng-anh="item.ten_tieng_anh"
                    :mo-ta="moTaNganh(item)"
                    :hinh-anh="item.hinh_anh_mo_ta || ''"
                    :khoa="item.id"
                  />
                  <div class="the-card__veil">
                    <CustomButton
                      class="the-card__detail"
                      :aria-label="`Chi tiết ngành ${item.ten_nganh}`"
                      @click="moChiTiet('nganh', item)"
                    >
                      Chi tiết
                    </CustomButton>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <article class="stages-card mt-3">
            <h2 class="h4 mb-2">Trường nổi bật</h2>
            <p class="text-secondary mb-3">Một số cơ sở đào tạo để bạn xem thêm khi đang tìm hướng đi.</p>
            <p v-if="loiTruong" class="holland-note holland-note__text mb-0">{{ loiTruong }}</p>
            <p v-else-if="dangTaiTruong" class="text-secondary mb-0">Đang tải trường…</p>
            <KhongCoDuLieu v-else-if="!truongNoiBat.length" text="Chưa có trường nổi bật." />
            <div v-else class="row g-3">
              <div v-for="item in truongNoiBat" :key="item.id" class="col-12 col-md-6 col-lg-4">
                <div class="the-card">
                  <CardNganhDaoTao
                    class="h-100"
                    :ma="item.ma_truong"
                    :ten="item.ten_truong"
                    :ten-tieng-anh="item.ten_tieng_anh || ''"
                    :mo-ta="item.gioi_thieu_ngan || moTaTruong(item)"
                    :hinh-anh="item.anh_dai_dien_url || item.logo_url || ''"
                    :khoa="item.id"
                  />
                  <div class="the-card__veil">
                    <CustomButton
                      class="the-card__detail"
                      :aria-label="`Chi tiết trường ${item.ten_truong}`"
                      @click="moChiTiet('truong', item)"
                    >
                      Chi tiết
                    </CustomButton>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <HoTroDinhHuong class="mt-3" />
          <CauHoiThuongGap class="mt-3" />
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="chon-lai-giai-doan" class="h4 mb-3">Chọn lại giai đoạn</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-giai-doan">
              <CustomButton
                v-for="stage in stages"
                :key="stage.code"
                class="switch-card"
                :class="{ 'is-selected': currentStage === stage.code }"
                @click="chonGiaiDoan(stage)"
              >
                <img class="switch-card__image" :src="stage.image" :alt="stage.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">{{ stage.name }}</span>
                  <span class="switch-card__text">{{ stage.description }}</span>
                </span>
              </CustomButton>
            </div>
          </div>
        </div>
      </div>
    </div>

    <CustomDialog v-model="chiTietMo" :title="tieuDeChiTiet" :width="760" :height="560">
      <div v-if="bangChiTiet.length" class="chi-tiet-wrap">
        <table class="chi-tiet-bang">
          <tbody v-for="nhom in bangChiTiet" :key="nhom.id">
            <tr>
              <th class="chi-tiet-bang__nhom" colspan="2">{{ nhom.ten }}</th>
            </tr>
            <tr v-for="(hang, index) in nhom.hang" :key="`${nhom.id}-${index}`">
              <th>{{ hang.label }}</th>
              <td>
                <a v-if="hang.href" :href="hang.href" target="_blank" rel="noopener noreferrer">{{ hang.value }}</a>
                <template v-else>{{ hang.value }}</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <div class="chi-tiet__footer">
          <CustomButton @click="chiTietMo = false">Đóng</CustomButton>
        </div>
      </template>
    </CustomDialog>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import { fetchTruongHoc } from '@/api/truongHoc'
import anhChuaCo from '@/assets/guest/thanh-nien.jpg'
import { noiMucLuong } from '@/utils/capTenGiaTri'
import { GIAI_DOAN_THI_DAI_HOC_KEY, giaiDoanThiDaiHocList } from './giaiDoan'
import { routeNameGiaiDoanThiDaiHoc } from '../routes'
import CardNganhDaoTao from './CardNganhDaoTao.vue'

defineOptions({ name: 'ThptThiDaiHocChuaCo' })

// Mặc định mở nhóm Nghệ thuật (A).
const MA_NHOM_MAC_DINH = 'A'
const SO_NGANH_NOI_BAT = 6
const SO_TRUONG_NOI_BAT = 6

const stages = giaiDoanThiDaiHocList
const route = useRoute()
const router = useRouter()
const currentStage = computed(() => route.meta.giaiDoan || '')
const nhomHolland = ref([])
const nganhNoiBat = ref([])
const truongNoiBat = ref([])
const dangTaiHolland = ref(false)
const dangTaiNganh = ref(false)
const dangTaiTruong = ref(false)
const loiHolland = ref('')
const loiNganh = ref('')
const loiTruong = ref('')
const chiTietMo = ref(false)
const doiTuongChiTiet = ref(null)
const maNhomDangChon = ref(MA_NHOM_MAC_DINH)

const NHAN_MUC_NGANH = {
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

function chonGiaiDoan(stage) {
  sessionStorage.setItem(GIAI_DOAN_THI_DAI_HOC_KEY, stage.code)
  const name = routeNameGiaiDoanThiDaiHoc(stage.code)
  if (name && name !== route.name) {
    router.push({ name })
    return
  }
  if (!name) router.push({ name: 'thpt-thi-dai-hoc' })
}

function moHuongDan() {
  router.push({ name: 'thpt-thi-dai-hoc-huong-dan-khao-sat' })
}

function moTaHolland(item) {
  return item.mo_ta || item.vi_du_nghe_nghiep || ''
}

function dieuHuongNhom(event) {
  const items = nhomHolland.value
  const index = items.findIndex((item) => item.ma_nhom === maNhomDangChon.value)
  if (index < 0 || !items.length) return
  const buoc = { ArrowRight: 1, ArrowLeft: -1, Home: -index, End: items.length - 1 - index }[event.key]
  if (buoc == null) return
  event.preventDefault()
  const ke = (index + buoc + items.length) % items.length
  maNhomDangChon.value = items[ke].ma_nhom
  nextTick(() => document.getElementById(`nhom-nghe-${items[ke].ma_nhom}`)?.focus())
}

watch(nhomHolland, (items) => {
  if (!items.some((item) => item.ma_nhom === maNhomDangChon.value)) {
    const macDinh = items.find((item) => item.ma_nhom === MA_NHOM_MAC_DINH)
    maNhomDangChon.value = (macDinh || items[0])?.ma_nhom || ''
  }
})

function moTaNganh(item) {
  if (item.mo_ta) return item.mo_ta
  if (item.ten_nhom_nganh && item.ten_nhom_nganh !== item.ten_nganh) return item.ten_nhom_nganh
  return ''
}

function moTaTruong(item) {
  return [item.ten_tinh_thanh, item.loai_co_so].filter(Boolean).join(' · ')
}

function noiGiaTri(value, sep = '\n') {
  if (Array.isArray(value)) {
    return value.map((item) => noiGiaTri(item, sep)).filter(Boolean).join(sep)
  }
  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(([key, item]) => {
        const text = noiGiaTri(item, sep)
        return text ? `${NHAN_MUC_NGANH[key] || key}: ${text}` : ''
      })
      .filter(Boolean)
      .join(sep)
  }
  if (value == null) return ''
  return String(value).trim()
}

function hrefLienKet(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  if (/^(https?:|mailto:|tel:)/i.test(text)) return text
  return `https://${text}`
}

function docChiTietNganh(item) {
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

function dongThongTin(label, value, href = '') {
  const text = Array.isArray(value) ? noiGiaTri(value, ' · ') : noiGiaTri(value)
  if (!text) return null
  return { label, value: text, href }
}

function moChiTiet(loai, item) {
  doiTuongChiTiet.value = { loai, item }
  chiTietMo.value = true
}

function gomHang(...hang) {
  return hang.filter(Boolean)
}

const tieuDeChiTiet = computed(() => {
  const current = doiTuongChiTiet.value
  if (!current) return 'Chi tiết'
  if (current.loai === 'holland') return current.item.ten_nhom
  if (current.loai === 'nganh') return current.item.ten_nganh
  return current.item.ten_truong
})

const bangChiTiet = computed(() => {
  const current = doiTuongChiTiet.value
  if (!current) return []
  const item = current.item
  let gioiThieu = []
  let tieuChi = []

  if (current.loai === 'holland') {
    gioiThieu = gomHang(
      dongThongTin('Mã nhóm', item.ma_nhom),
      dongThongTin('Tên tiếng Anh', item.ten_tieng_anh),
      dongThongTin('Mô tả', item.mo_ta),
    )
    tieuChi = gomHang(dongThongTin('Ví dụ nghề nghiệp', item.vi_du_nghe_nghiep))
  } else if (current.loai === 'nganh') {
    const { vanBan, json } = docChiTietNganh(item)
    const moTa = item.mo_ta || noiGiaTri(json?.mo_ta) || (!json ? vanBan : '')
    gioiThieu = gomHang(
      dongThongTin('Mã ngành', item.ma_nganh),
      dongThongTin('Tên tiếng Anh', item.ten_tieng_anh),
      dongThongTin('Nhóm ngành', [item.ma_nhom_nganh, item.ten_nhom_nganh].filter(Boolean).join(' · ')),
      dongThongTin('Trình độ', item.trinh_do),
      dongThongTin('Mô tả', moTa),
      !json && vanBan && item.mo_ta ? dongThongTin('Chi tiết', vanBan) : null,
    )
    tieuChi = gomHang(
      dongThongTin('Thời gian đào tạo', item.thoi_gian_dao_tao || json?.thoi_gian_dao_tao),
      dongThongTin('Mức lương tham khảo', noiMucLuong(item.muc_luong_tham_khao) || noiGiaTri(json?.muc_luong_tham_khao || json?.muc_luong)),
      dongThongTin('Nhu cầu việc làm', item.nhan_dan),
      dongThongTin('Nhóm Holland', item.ma_holand),
    )
    if (json) {
      const daHien = new Set(['mo_ta', 'muc_luong', 'muc_luong_tham_khao', 'thoi_gian_dao_tao'])
      for (const [key, value] of Object.entries(json)) {
        if (daHien.has(key)) continue
        const hang = dongThongTin(NHAN_MUC_NGANH[key] || key, value)
        if (hang) tieuChi.push(hang)
      }
    }
  } else {
    const linhVuc = [
      ...(item.linh_vuc_dao_tao_chinh || []),
      ...(item.linh_vuc_dao_tao_khac || []),
    ]
    gioiThieu = gomHang(
      dongThongTin('Mã trường', item.ma_truong),
      dongThongTin('Tên tiếng Anh', item.ten_tieng_anh),
      dongThongTin('Tên viết tắt', item.ten_viet_tat),
      dongThongTin('Tên gọi khác', item.ten_goi_khac),
      dongThongTin('Giới thiệu', item.gioi_thieu_ngan),
      dongThongTin('Giới thiệu chi tiết', item.gioi_thieu_chi_tiet),
    )
    tieuChi = gomHang(
      dongThongTin('Loại cơ sở', item.loai_co_so),
      dongThongTin('Loại hình', item.loai_hinh),
      dongThongTin('Cơ quan chủ quản', item.co_quan_chu_quan),
      dongThongTin('Khu vực', [item.vung_mien, item.ten_tinh_thanh, item.ten_phuong_xa].filter(Boolean).join(' · ')),
      dongThongTin('Địa chỉ', item.dia_chi_tru_so),
      dongThongTin('Điện thoại', item.so_dien_thoai, item.so_dien_thoai ? `tel:${String(item.so_dien_thoai).replace(/\s/g, '')}` : ''),
      dongThongTin('Email', item.email, item.email ? `mailto:${item.email}` : ''),
      dongThongTin('Website', item.website, hrefLienKet(item.website)),
      dongThongTin('Website tuyển sinh', item.website_tuyen_sinh, hrefLienKet(item.website_tuyen_sinh)),
      dongThongTin('Hotline tuyển sinh', item.hotline_tuyen_sinh),
      dongThongTin('Email tuyển sinh', item.email_tuyen_sinh, item.email_tuyen_sinh ? `mailto:${item.email_tuyen_sinh}` : ''),
      dongThongTin('Học phí trung bình', item.hoc_phi_trung_binh),
      dongThongTin('Bậc đào tạo', item.bac_dao_tao),
      dongThongTin('Năm thành lập', item.nam_thanh_lap),
      dongThongTin('Lĩnh vực đào tạo', [...new Set(linhVuc.map((tag) => String(tag || '').trim()).filter(Boolean))]),
      dongThongTin('Thế mạnh', item.the_manh),
    )
  }

  return [
    { id: 'gioi-thieu', ten: 'Giới thiệu', hang: gioiThieu },
    { id: 'tieu-chi', ten: 'Tiêu chí đặc thù', hang: tieuChi },
  ].filter((nhom) => nhom.hang.length)
})

async function taiNhomHolland() {
  dangTaiHolland.value = true
  loiHolland.value = ''
  try {
    const data = await fetchNhomHolland(
      { trang_thai: 1, page: 1, page_size: 100 },
      { skipLoading: true },
    )
    nhomHolland.value = data.items || []
  } catch {
    loiHolland.value = 'Không tải được nhóm ngành nghề.'
  } finally {
    dangTaiHolland.value = false
  }
}

let lanTaiNganh = 0

async function taiNganhNoiBat(maNhom) {
  const lan = ++lanTaiNganh
  dangTaiNganh.value = true
  loiNganh.value = ''
  nganhNoiBat.value = []
  try {
    const params = { trang_thai: 1, ngau_nhien: true, page: 1, page_size: SO_NGANH_NOI_BAT }
    if (maNhom) params.ma_holand = maNhom
    const data = await fetchNganh(params, { skipLoading: true })
    if (lan !== lanTaiNganh) return
    nganhNoiBat.value = data.items || []
  } catch {
    if (lan !== lanTaiNganh) return
    loiNganh.value = 'Không tải được ngành nổi bật.'
  } finally {
    if (lan === lanTaiNganh) dangTaiNganh.value = false
  }
}

watch(maNhomDangChon, taiNganhNoiBat, { immediate: true })

async function taiTruongNoiBat() {
  dangTaiTruong.value = true
  loiTruong.value = ''
  try {
    const data = await fetchTruongHoc(
      {
        loai_co_so: 'Đại học',
        trang_thai_hoat_dong: 'Đang hoạt động',
        ngau_nhien: true,
        page: 1,
        page_size: SO_TRUONG_NOI_BAT,
      },
      { skipLoading: true },
    )
    truongNoiBat.value = data.items || []
  } catch {
    loiTruong.value = 'Không tải được trường nổi bật.'
  } finally {
    dangTaiTruong.value = false
  }
}

onMounted(() => {
  taiNhomHolland()
  taiTruongNoiBat()
})
</script>

<style scoped>
.chua-co :is(.h2, .h4, .switch-card__name) {
  font-weight: 400;
}

.intro-card__image {
  display: block;
  width: 100%;
  height: 240px;
  object-fit: cover;
  border-radius: 10px;
}

.intro-card__body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.intro-card__eyebrow {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(var(--guest-primary-rgb, 63, 150, 67), 0.12);
  color: var(--guest-primary, #3f9643);
  font-size: 0.8rem;
  font-weight: 400;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.intro-card__title {
  margin: 0;
  line-height: 1.25;
}

.intro-card__lead {
  margin: 0;
  color: #1c2b23;
  font-size: 1.05rem;
  line-height: 1.55;
}

.intro-card__steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
  color: #5b6b62;
  font-size: 0.95rem;
  line-height: 1.5;
}

.intro-card__steps li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.intro-card__step-num {
  display: inline-flex;
  flex: none;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  margin-top: 1px;
  border-radius: 50%;
  background: rgba(var(--guest-primary-rgb, 63, 150, 67), 0.12);
  color: var(--guest-primary, #3f9643);
  font-size: 0.75rem;
  font-weight: 400;
}

.intro-card__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  margin-top: 4px;
}

.intro-card__cta {
  height: auto;
  margin: 0;
  padding: 12px 28px;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 400;
  box-shadow: 0 8px 20px rgba(var(--guest-primary-rgb, 63, 150, 67), 0.32);
  transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
  --el-button-bg-color: var(--guest-primary, #3f9643);
  --el-button-border-color: var(--guest-primary, #3f9643);
  --el-button-text-color: #fff;
  --el-button-hover-bg-color: var(--guest-primary-hover, #37843b);
  --el-button-hover-border-color: var(--guest-primary-hover, #37843b);
  --el-button-hover-text-color: #fff;
  --el-button-active-bg-color: var(--guest-primary-hover, #37843b);
  --el-button-active-border-color: var(--guest-primary-hover, #37843b);
  --el-button-active-text-color: #fff;
}

.intro-card__cta:hover,
.intro-card__cta:focus-visible {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(var(--guest-primary-rgb, 63, 150, 67), 0.4);
}

.intro-card__cta:focus-visible {
  outline: 2px solid var(--guest-primary, #3f9643);
  outline-offset: 3px;
}

.intro-card__cta-arrow {
  margin-left: 8px;
  transition: transform 0.18s ease;
}

.intro-card__cta:hover .intro-card__cta-arrow {
  transform: translateX(3px);
}

.intro-card__hint {
  color: #6c7a72;
  font-size: 0.875rem;
}

@media (prefers-reduced-motion: reduce) {
  .intro-card__cta,
  .intro-card__cta-arrow {
    transition: none;
  }

  .intro-card__cta:hover,
  .intro-card__cta:hover .intro-card__cta-arrow {
    transform: none;
  }
}

.nhom-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.nhom-pills__item {
  margin: 0;
  padding: 8px 16px;
  border: 1px solid var(--guest-primary, #3f9643);
  border-radius: 0.375rem;
  background: #fff;
  color: var(--guest-primary, #3f9643);
  font-size: 0.95rem;
  line-height: 1.3;
  cursor: pointer;
}

.nhom-pills__item.is-active {
  background: var(--guest-primary, #3f9643);
  color: #fff;
}

.nhom-pills__item:focus-visible {
  outline: 2px solid var(--guest-primary, #3f9643);
  outline-offset: 2px;
}

.the-card {
  position: relative;
  height: 100%;
  border-radius: 12px;
}

.the-card :deep(.card-dao-tao) {
  height: 100%;
  transition: background-color 0.22s ease;
}

.the-card:hover :deep(.card-dao-tao),
.the-card:focus-within :deep(.card-dao-tao) {
  background: #e7f5ea;
}

.the-card__veil {
  position: absolute;
  inset: 0;
  z-index: 4;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 16px;
  border-radius: 12px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease;
}

.the-card:hover .the-card__veil,
.the-card:focus-within .the-card__veil {
  opacity: 1;
}

.the-card__detail {
  height: auto;
  margin: 0;
  border: 0;
  border-radius: 0.375rem;
  padding: 8px 18px;
  background: #fff;
  box-shadow: 0 8px 18px rgba(16, 42, 28, 0.22);
  color: var(--guest-primary, #3f9643);
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.2;
  pointer-events: none;
  --el-button-bg-color: #fff;
  --el-button-border-color: transparent;
  --el-button-text-color: var(--guest-primary, #3f9643);
  --el-button-hover-bg-color: var(--guest-primary, #3f9643);
  --el-button-hover-border-color: transparent;
  --el-button-hover-text-color: #fff;
  --el-button-active-bg-color: var(--guest-primary-hover, #37843b);
  --el-button-active-border-color: transparent;
  --el-button-active-text-color: #fff;
}

.the-card:hover .the-card__detail,
.the-card:focus-within .the-card__detail {
  pointer-events: auto;
}

.the-card__detail:hover,
.the-card__detail:focus-visible {
  background: var(--guest-primary);
  border-color: transparent;
  color: #fff;
}

.chua-co :deep(.switch-card.el-button) {
  height: auto;
  margin: 0;
  font-size: inherit;
  font-weight: inherit;
  line-height: inherit;
  white-space: normal;
  justify-content: flex-start;
  text-align: left;
  --el-button-bg-color: #fff;
  --el-button-border-color: #d7eadf;
  --el-button-text-color: inherit;
  --el-button-hover-bg-color: #fff;
  --el-button-hover-border-color: #d7eadf;
  --el-button-hover-text-color: inherit;
  --el-button-active-bg-color: #fff;
  --el-button-active-border-color: var(--guest-primary);
  --el-button-active-text-color: inherit;
}

.chua-co :deep(.switch-card.el-button > span) {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  min-width: 0;
  white-space: normal;
}

.chi-tiet-wrap {
  overflow-x: auto;
}

.chi-tiet-bang {
  width: 100%;
  border-collapse: collapse;
  color: #121a28;
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.45;
}

.chi-tiet-bang th,
.chi-tiet-bang td {
  padding: 10px 12px;
  border: 1px solid #c5d5cc;
  font-weight: 400;
  text-align: left;
  vertical-align: top;
  white-space: pre-line;
}

.chi-tiet-bang__nhom {
  background: #3f9643;
  color: #fff;
  font-weight: 400;
}

.chi-tiet-bang tbody th:not(.chi-tiet-bang__nhom) {
  width: 190px;
  background: #e5f2ea;
  color: #3f9643;
  font-weight: 400;
}

.chi-tiet-bang td {
  background: #fff;
}

.chi-tiet-bang a {
  color: #1a66d1;
}

.chi-tiet__footer {
  display: flex;
  justify-content: flex-end;
}

@media (hover: none) {
  .the-card__veil {
    align-items: flex-end;
    justify-content: flex-end;
    padding: 12px;
    background: none;
    opacity: 1;
  }

  .the-card__detail {
    background: var(--guest-primary);
    color: #fff;
    pointer-events: auto;
    --el-button-bg-color: var(--guest-primary);
    --el-button-text-color: #fff;
    --el-button-hover-bg-color: var(--guest-primary-hover, #37843b);
    --el-button-hover-text-color: #fff;
  }
}
</style>
