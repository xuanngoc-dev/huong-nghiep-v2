<template>
  <section class="phan-van py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <article class="intro-card">
            <h2 class="h2 mb-2">Bạn đang phân vân giữa vài ngành nghề?</h2>
            <p class="text-secondary mb-0">
              Chọn nhóm ngành nghề, rồi đánh dấu những ngành bạn đang cân nhắc để so sánh.
            </p>
          </article>

          <article class="stages-card mt-3">
            <div class="phan-van-list mb-3">
              <p class="phan-van-list__label">
                Danh sách phân vân
                <span>({{ danhSachPhanVan.length }}/{{ SO_NGANH_PHAN_VAN_TOI_DA }})</span>
              </p>
              <p v-if="!danhSachPhanVan.length" class="phan-van-list__empty">
                Chưa chọn ngành. Mở một nhóm ngành nghề và đánh dấu ngành bạn đang cân nhắc.
              </p>
              <div class="phan-van-list__bar">
                <ul v-if="danhSachPhanVan.length" class="phan-van-list__items">
                  <li v-for="item in danhSachPhanVan" :key="item.ma_nganh">
                    <span>{{ item.ten_nganh }}</span>
                    <CustomButton
                      text
                      circle
                      type="danger"
                      size="small"
                      class="phan-van-list__remove"
                      :aria-label="`Bỏ ${item.ten_nganh}`"
                      @click="doiPhanVan(item)"
                    >
                      <CustomIcon :size="14"><Close /></CustomIcon>
                    </CustomButton>
                  </li>
                </ul>
                <div class="phan-van-list__actions">
                  <CustomTooltip
                    content="Chọn từ 2 đến 3 ngành để so sánh."
                    placement="top"
                    :disabled="coTheSoSanh"
                  >
                    <span class="phan-van-list__tooltip">
                      <CustomBadge :value="danhSachPhanVan.length" :max="SO_NGANH_PHAN_VAN_TOI_DA" show-zero>
                        <CustomButton type="primary" :disabled="!coTheSoSanh" @click="moSoSanh">
                          So sánh
                        </CustomButton>
                      </CustomBadge>
                    </span>
                  </CustomTooltip>
                </div>
              </div>
            </div>

            <template v-if="nhomDangXem">
              <button type="button" class="nhom-back mb-3" @click="quayLaiNhom">
                Quay lại nhóm ngành nghề
              </button>
              <h2 class="h4 mb-2">{{ nhomDangXem.ten_nhom }}</h2>
              <p class="text-secondary mb-3">
                Đánh dấu ngành bạn đang cân nhắc. Có thể chọn tối đa {{ SO_NGANH_PHAN_VAN_TOI_DA }} ngành từ các nhóm khác nhau.
              </p>
              <p v-if="loiNganh" class="text-secondary mb-0">{{ loiNganh }}</p>
              <p v-else-if="dangTaiNganh" class="text-secondary mb-0">Đang tải ngành…</p>
              <KhongCoDuLieu v-else-if="!nganhTheoNhom.length" text="Nhóm này chưa có ngành." />
              <div v-else class="row g-3">
                <div v-for="item in nganhTrang" :key="item.id" class="col-12 col-md-6 col-lg-4">
                  <CardNganhDaoTao
                    class="h-100"
                    :ma="item.ma_nganh"
                    :ten="item.ten_nganh"
                    :ten-tieng-anh="item.ten_tieng_anh"
                    :mo-ta="moTaNganh(item)"
                    :hinh-anh="item.hinh_anh_mo_ta || ''"
                    :khoa="item.id"
                    co-the-chon
                    :da-chon="daChon(item)"
                    :khoa-chon="!daChon(item) && hetCho()"
                    :href-kham-pha="hrefChonTruong(item)"
                    @doi-chon="doiPhanVan(item)"
                    @het-cho="baoHetCho"
                  />
                </div>
              </div>
              <div v-if="!dangTaiNganh && !loiNganh && nganhTheoNhom.length" class="nhom-pager">
                <CustomPagination
                  v-model:current-page="trangNganh"
                  :page-size="SO_MOI_TRANG"
                  :total="nganhTheoNhom.length"
                  layout="total, prev, pager, next"
                  background
                />
              </div>
            </template>

            <template v-else>
              <h2 class="h4 mb-2">Nhóm ngành nghề</h2>
              <p class="text-secondary mb-3">Chọn nhóm gần với ngành bạn đang phân vân.</p>
              <p v-if="loiNhom" class="text-secondary mb-0">{{ loiNhom }}</p>
              <p v-else-if="dangTaiNhom" class="text-secondary mb-0">Đang tải nhóm ngành nghề…</p>
              <KhongCoDuLieu v-else-if="!nhomNghe.length" text="Chưa có nhóm ngành nghề." />
              <div v-else class="row g-3">
                <div v-for="item in nhomNghe" :key="item.id" class="col-12 col-md-6 col-lg-4">
                  <CardNganhDaoTao
                    class="h-100"
                    :ma="item.ma_nhom"
                    :ten="item.ten_nhom"
                    :ten-tieng-anh="item.ten_tieng_anh"
                    :mo-ta="moTaHolland(item)"
                    :hinh-anh="item.hinh_anh_mo_ta || ''"
                    :khoa="item.id"
                    hanh-dong="Chọn"
                    @chon="chonNhom(item)"
                  />
                </div>
              </div>
            </template>
          </article>

          <NhacKhaoSat class="mt-3" />
          <HoTroDinhHuong class="mt-3" />
          <CauHoiThuongGap class="mt-3" />
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="chon-lai-giai-doan" class="h4 mb-3">Chọn lại giai đoạn</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-giai-doan">
              <button
                v-for="stage in stages"
                :key="stage.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': currentStage === stage.code }"
                @click="chonGiaiDoan(stage)"
              >
                <img class="switch-card__image" :src="stage.image" :alt="stage.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">{{ stage.name }}</span>
                  <span class="switch-card__text">{{ stage.description }}</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <CustomDialog v-model="soSanhMo" title="So sánh ngành" :width="960" height="70vh">
      <p v-if="loiSoSanh" class="so-sanh-trang-thai">{{ loiSoSanh }}</p>
      <p v-else-if="dangTaiSoSanh" class="so-sanh-trang-thai">Đang tải dữ liệu so sánh…</p>
      <div v-else class="so-sanh-wrap">
        <table class="so-sanh so-sanh--nganh">
          <thead>
            <tr>
              <th>Tiêu chí</th>
              <th v-for="item in nganhSoSanh" :key="item.ma_nganh">{{ item.ten_nganh }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hang in TIEU_CHI_SO_SANH" :key="hang.id">
              <th>{{ hang.ten }}</th>
              <td v-for="item in nganhSoSanh" :key="item.ma_nganh">{{ giaTriTieuChi(item, hang.id) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <div class="so-sanh-footer">
          <p class="so-sanh-footer__text">Tham gia khảo sát để lựa chọn ngành phù hợp.</p>
          <div class="so-sanh-footer__actions">
            <CustomButton @click="soSanhMo = false">Đóng</CustomButton>
            <CustomButton type="primary" @click="lamKhaoSat">Làm khảo sát</CustomButton>
          </div>
        </div>
      </template>
    </CustomDialog>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import { GIAI_DOAN_THI_DAI_HOC_KEY, giaiDoanThiDaiHocList } from './giaiDoan'
import { routeNameGiaiDoanThiDaiHoc } from '../routes'
import CardNganhDaoTao from './CardNganhDaoTao.vue'
import NhacKhaoSat from './NhacKhaoSat.vue'
import { noiMucLuong } from '@/utils/capTenGiaTri'

defineOptions({ name: 'ThptThiDaiHocPhanVan' })

const DANH_SACH_PHAN_VAN_KEY = 'danh_sach_phan_van'
const SO_NGANH_PHAN_VAN_TOI_DA = 3
const SO_MOI_TRANG = 8
const TIEU_CHI_SO_SANH = [
  { id: 'mo_ta', ten: 'Mô tả/ngành học' },
  { id: 'ky_nang_phu_hop', ten: 'Kỹ năng phù hợp' },
  { id: 'mon_hoc_tieu_bieu', ten: 'Môn học tiêu biểu' },
  { id: 'co_hoi_nghe_nghiep', ten: 'Cơ hội nghề nghiệp' },
  { id: 'muc_luong', ten: 'Mức lương (tham khảo)' },
  { id: 'cong_cu', ten: 'Công cụ thường dùng' },
  { id: 'do_phu_hop', ten: 'Độ phù hợp với bản thân' },
  { id: 'diem_can_nhac', ten: 'Điểm cân nhắc' },
  { id: 'truong_dao_tao', ten: 'Các trường đào tạo' },
]

const stages = giaiDoanThiDaiHocList
const route = useRoute()
const router = useRouter()
const currentStage = computed(() => route.meta.giaiDoan || '')

const nhomNghe = ref([])
const nganh = ref([])
const dangTaiNhom = ref(false)
const dangTaiNganh = ref(false)
const loiNhom = ref('')
const loiNganh = ref('')
const nhomDangXem = ref(null)
const trangNganh = ref(1)
const danhSachPhanVan = ref(docDanhSachPhanVan())
const soSanhMo = ref(false)
const dangTaiSoSanh = ref(false)
const loiSoSanh = ref('')
const nganhSoSanh = ref([])

function moTaHolland(item) {
  return item.mo_ta || item.vi_du_nghe_nghiep || ''
}

function maHollandCua(item) {
  const value = item?.ma_holand
  if (Array.isArray(value)) return value.map((code) => String(code).toUpperCase())
  if (typeof value === 'string' && value.trim()) return [value.trim().toUpperCase()]
  return []
}

function moTaNganh(item) {
  if (item.mo_ta) return item.mo_ta
  if (item.ten_nhom_nganh && item.ten_nhom_nganh !== item.ten_nganh) return item.ten_nhom_nganh
  return ''
}

const nganhTheoNhom = computed(() => {
  const ma = String(nhomDangXem.value?.ma_nhom || '').toUpperCase()
  if (!ma) return []
  return nganh.value
    .filter((item) => maHollandCua(item).includes(ma))
    .sort((a, b) => a.ten_nganh.localeCompare(b.ten_nganh, 'vi'))
})

const nganhTrang = computed(() => {
  const batDau = (trangNganh.value - 1) * SO_MOI_TRANG
  return nganhTheoNhom.value.slice(batDau, batDau + SO_MOI_TRANG)
})

const coTheSoSanh = computed(() => danhSachPhanVan.value.length >= 2)

function docDanhSachPhanVan() {
  try {
    const data = JSON.parse(sessionStorage.getItem(DANH_SACH_PHAN_VAN_KEY) || '[]')
    if (!Array.isArray(data)) return []
    return data
      .filter((item) => item && item.ma_nganh && item.ten_nganh)
      .slice(0, SO_NGANH_PHAN_VAN_TOI_DA)
  } catch {
    return []
  }
}

function daChon(item) {
  return danhSachPhanVan.value.some((nganhDaChon) => nganhDaChon.ma_nganh === item.ma_nganh)
}

function hetCho() {
  return danhSachPhanVan.value.length >= SO_NGANH_PHAN_VAN_TOI_DA
}

function baoHetCho() {
  ElMessage.warning(`Chỉ chọn tối đa ${SO_NGANH_PHAN_VAN_TOI_DA} ngành phân vân.`)
}

function banGhiPhanVan(item) {
  return {
    ma_nganh: item.ma_nganh,
    ten_nganh: item.ten_nganh,
    ten_tieng_anh: item.ten_tieng_anh || '',
    ma_nhom_nganh: item.ma_nhom_nganh || '',
    ten_nhom_nganh: item.ten_nhom_nganh || '',
    trinh_do: item.trinh_do || '',
    ma_holand: Array.isArray(item.ma_holand) ? item.ma_holand : [],
    mo_ta: item.mo_ta || '',
    muc_luong_tham_khao: item.muc_luong_tham_khao || '',
    nhan_dan: item.nhan_dan || '',
    thoi_gian_dao_tao: item.thoi_gian_dao_tao || '',
    chi_tiet: item.chi_tiet || '',
  }
}

function doiPhanVan(item) {
  if (daChon(item)) {
    danhSachPhanVan.value = danhSachPhanVan.value.filter((nganhDaChon) => nganhDaChon.ma_nganh !== item.ma_nganh)
    return
  }
  if (hetCho()) {
    baoHetCho()
    return
  }
  danhSachPhanVan.value = [...danhSachPhanVan.value, banGhiPhanVan(item)]
}

function noiChiTiet(value) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean).join('\n')
  }
  if (value == null) return ''
  return String(value).trim()
}

function chiTietNganh(nganh) {
  const text = String(nganh.chi_tiet || '').trim()
  if (!text.startsWith('{')) return {}
  try {
    const data = JSON.parse(text)
    return data && typeof data === 'object' && !Array.isArray(data) ? data : {}
  } catch {
    return {}
  }
}

function giaTriTieuChi(nganh, id) {
  const chiTiet = chiTietNganh(nganh)
  if (id === 'mo_ta') return nganh.mo_ta || noiChiTiet(chiTiet.mo_ta) || '—'
  if (id === 'muc_luong') return noiMucLuong(nganh.muc_luong_tham_khao) || noiChiTiet(chiTiet.muc_luong_tham_khao) || '—'
  if (id === 'do_phu_hop') return noiChiTiet(chiTiet.do_phu_hop) || '—'
  return noiChiTiet(chiTiet[id]) || '—'
}

async function taiNganhTheoMa(item) {
  const data = await fetchNganh(
    { page: 1, page_size: 20, q: item.ma_nganh, trang_thai: 1 },
    { skipLoading: true },
  )
  return (data.items || []).find((nganh) => nganh.ma_nganh === item.ma_nganh) || item
}

function lamKhaoSat() {
  const ma = danhSachPhanVan.value.map((item) => item.ma_nganh).filter(Boolean)
  router.push({
    name: 'thpt-thi-dai-hoc-huong-dan-khao-sat',
    query: ma.length ? { ma_nganh: ma } : {},
  })
}

async function moSoSanh() {
  if (!coTheSoSanh.value) {
    ElMessage.warning('Hãy chọn từ 2 đến 3 ngành để so sánh.')
    return
  }
  soSanhMo.value = true
  dangTaiSoSanh.value = true
  loiSoSanh.value = ''
  nganhSoSanh.value = danhSachPhanVan.value.map(banGhiPhanVan)
  try {
    nganhSoSanh.value = await Promise.all(
      danhSachPhanVan.value.map(async (item) => {
        try {
          return await taiNganhTheoMa(item)
        } catch {
          return item
        }
      }),
    )
  } catch {
    loiSoSanh.value = 'Không tải được dữ liệu so sánh.'
  } finally {
    dangTaiSoSanh.value = false
  }
}

function hrefChonTruong(item) {
  return router.resolve({
    name: 'thpt-thi-dai-hoc-chon-truong',
    params: { maNganh: item.ma_nganh },
  }).href
}

function chonNhom(item) {
  nhomDangXem.value = item
  trangNganh.value = 1
}

function quayLaiNhom() {
  nhomDangXem.value = null
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

async function taiHetNganh() {
  const pageSize = 200
  let page = 1
  const items = []
  while (page <= 20) {
    const data = await fetchNganh(
      { page, page_size: pageSize, trang_thai: 1 },
      { skipLoading: true },
    )
    items.push(...(data.items || []))
    if (items.length >= (data.total || 0) || !data.items?.length) break
    page += 1
  }
  return items
}

async function taiNhomNghe() {
  dangTaiNhom.value = true
  loiNhom.value = ''
  try {
    const data = await fetchNhomHolland(
      { trang_thai: 1, page: 1, page_size: 100 },
      { skipLoading: true },
    )
    nhomNghe.value = data.items || []
  } catch {
    loiNhom.value = 'Không tải được nhóm ngành nghề.'
  } finally {
    dangTaiNhom.value = false
  }
}

async function taiNganh() {
  dangTaiNganh.value = true
  loiNganh.value = ''
  try {
    nganh.value = await taiHetNganh()
  } catch {
    loiNganh.value = 'Không tải được danh sách ngành.'
  } finally {
    dangTaiNganh.value = false
  }
}

watch(danhSachPhanVan, (value) => {
  sessionStorage.setItem(DANH_SACH_PHAN_VAN_KEY, JSON.stringify(value))
  if (value.length < 2) {
    soSanhMo.value = false
    return
  }
  if (!soSanhMo.value) return
  const maConLai = new Set(value.map((item) => item.ma_nganh))
  nganhSoSanh.value = nganhSoSanh.value.filter((item) => maConLai.has(item.ma_nganh))
}, { deep: true })

onMounted(() => {
  taiNhomNghe()
  taiNganh()
})
</script>
