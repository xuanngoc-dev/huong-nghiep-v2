<template>
  <div class="landing">
    <section class="landing__section" aria-labelledby="thu-vien-nganh-nghe-title">
      <div class="container-fluid">
        <div class="landing__head">
          <p class="landing__eyebrow">Thư viện ngành nghề</p>
          <h1 id="thu-vien-nganh-nghe-title" class="landing__title">Khám phá nghề khi đi làm</h1>
          <p class="landing__lead">
            Các nghề cụ thể theo từng nhóm nghề: mô tả công việc, mức lương tham khảo và yêu cầu bằng cấp.
          </p>
        </div>

        <div class="landing-explore__panel">
          <!-- Tab = nhóm nghề đi làm đang hoạt động (dm_nhom_nghe_di_lam), mặc định "Tất cả".
               Nhóm đang chọn lưu trên query ?nhom=<ma_nhom> để chia sẻ link được. -->
          <div
            class="landing-explore__filters flex-nowrap flex-md-wrap overflow-x-auto"
            role="tablist"
            aria-label="Nhóm nghề"
          >
            <button
              v-for="tab in dsTab"
              :key="tab.ma"
              type="button"
              class="landing-explore__chip"
              :class="{ 'is-active': tab.ma === maNhomDangChon }"
              role="tab"
              :aria-selected="tab.ma === maNhomDangChon"
              aria-controls="thu-vien-nganh-nghe-ket-qua"
              @click="chonNhom(tab.ma)"
            >
              {{ tab.ten }}
              <span v-if="!dangTai" class="thu-vien__so">{{ tab.soNghe }}</span>
            </button>
          </div>

          <form class="landing-explore__search" role="search" @submit.prevent>
            <label class="landing-explore__o-nhap">
              <el-icon aria-hidden="true"><Search /></el-icon>
              <input v-model="tuKhoa" type="search" placeholder="Tìm nghề: bán hàng, thợ điện…" aria-label="Tìm nghề" />
            </label>
          </form>

          <div id="thu-vien-nganh-nghe-ket-qua" role="tabpanel" aria-live="polite">
            <p v-if="dangTai" class="thu-vien__trang-thai" role="status">Đang tải danh sách nghề…</p>
            <KhongCoDuLieu v-else-if="loi" :text="loi">
              <button type="button" class="landing__btn landing__btn--soft" @click="taiDuLieu">Thử lại</button>
            </KhongCoDuLieu>
            <KhongCoDuLieu
              v-else-if="!dsLoc.length"
              :text="tuKhoa.trim() ? `Không có nghề nào khớp “${tuKhoa.trim()}”.` : 'Chưa có dữ liệu nghề.'"
            />

            <template v-else>
              <p class="thu-vien__dem">{{ dsLoc.length }} nghề</p>
              <!-- Card nghề dùng chung giao diện thẻ hướng đi (như DoiTuongCard): chỉ tên, mô tả ngắn, dải lương;
                   bấm "Xem chi tiết" mở modal đủ thông tin. 3 card/hàng (desktop) → 2 (tablet) → 1 (mobile). -->
              <div class="row g-3">
                <div v-for="nghe in dsTrang" :key="nghe.id" class="col-12 col-md-6 col-lg-4">
                  <HuongDiCard
                    :image="anhNghe(nghe)"
                    :title="nghe.ten_nghe"
                    :description="nghe.mo_ta_ngan || ''"
                    :note="`Lương: ${daiLuong(nghe, nhomTheoId[nghe.nhom_nghe_di_lam_id])}`"
                    cta="Xem chi tiết"
                    @chon="moChiTiet(nghe)"
                  />
                </div>
              </div>
              <div v-if="dsLoc.length > SO_NGHE_MOI_TRANG" class="thu-vien__phan-trang">
                <CustomPagination
                  v-model:current-page="trang"
                  :page-size="SO_NGHE_MOI_TRANG"
                  :total="dsLoc.length"
                  layout="prev, pager, next"
                  background
                />
              </div>
            </template>
          </div>
        </div>

        <ChiTietNgheModal
          v-model="chiTietMo"
          :nghe="ngheDangXem"
          :nhom="ngheDangXem ? nhomTheoId[ngheDangXem.nhom_nghe_di_lam_id] : null"
          :anh="ngheDangXem ? anhNghe(ngheDangXem) : ''"
        />

        <HoTroDinhHuong class="thu-vien__ho-tro" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import anhMacDinh from '@/assets/guest/nha-tuyen-dung.jpg'
import { apiAssetUrl } from '@/api/apiUrl'
import { fetchNgheCuTheDiLam, fetchNhomNgheDiLam } from '@/api/nhomNgheDiLam'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import HuongDiCard from '@/components/guest/chung/HuongDiCard.vue'
import KhongCoDuLieu from '@/components/guest/chung/KhongCoDuLieu.vue'
import { boDau } from '@/components/guest/doi-tuong/HocSinhThpt/di-lam/nhomNghe'
import ChiTietNgheModal from '@/components/guest/thu-vien/ChiTietNgheModal.vue'
import { daiLuong } from '@/components/guest/thu-vien/nghe'
import '@/components/guest/landing/landing.css'

defineOptions({ name: 'ThuVienNganhNghe' })

const TAT_CA = ''
const SO_NGHE_MOI_TRANG = 12

const route = useRoute()
const router = useRouter()

// Nhóm nghề đang hoạt động và toàn bộ nghề cụ thể (vài trăm dòng) tải một lần; lọc theo tab, từ khóa và phân trang
// ngay trên trình duyệt để tab "Tất cả" bỏ được nghề của nhóm đã tắt và đếm được số nghề mỗi tab.
const dsNhomNghe = ref([])
const dsNghe = ref([])
const dangTai = ref(false)
const loi = ref('')
const tuKhoa = ref(route.query.q || '')
const trang = ref(1)

const nhomTheoId = computed(() => Object.fromEntries(dsNhomNghe.value.map((nhom) => [nhom.id, nhom])))
// Chỉ giữ nghề thuộc nhóm đang hoạt động.
const dsNgheHopLe = computed(() => dsNghe.value.filter((nghe) => nhomTheoId.value[nghe.nhom_nghe_di_lam_id]))

const dsTab = computed(() => {
  const soNgheTheoNhom = {}
  dsNgheHopLe.value.forEach((nghe) => {
    soNgheTheoNhom[nghe.nhom_nghe_di_lam_id] = (soNgheTheoNhom[nghe.nhom_nghe_di_lam_id] || 0) + 1
  })
  return [
    { ma: TAT_CA, ten: 'Tất cả', soNghe: dsNgheHopLe.value.length },
    ...dsNhomNghe.value.map((nhom) => ({ ma: nhom.ma_nhom, ten: nhom.ten_nhom, soNghe: soNgheTheoNhom[nhom.id] || 0 })),
  ]
})

// Mã nhóm trên query không còn tồn tại (nhóm đã tắt, sai link) thì về "Tất cả".
const maNhomDangChon = computed(() => {
  const ma = route.query.nhom
  return dsNhomNghe.value.some((nhom) => nhom.ma_nhom === ma) ? ma : TAT_CA
})

const dsLoc = computed(() => {
  const q = boDau(tuKhoa.value.trim())
  return dsNgheHopLe.value.filter((nghe) => {
    if (maNhomDangChon.value !== TAT_CA && nghe.ma_nhom !== maNhomDangChon.value) return false
    return !q || boDau([nghe.ten_nghe, nghe.mo_ta_ngan, nghe.ten_nhom].join(' ')).includes(q)
  })
})
const dsTrang = computed(() =>
  dsLoc.value.slice((trang.value - 1) * SO_NGHE_MOI_TRANG, trang.value * SO_NGHE_MOI_TRANG),
)

// Đổi tab hoặc từ khóa thì về trang 1.
watch([maNhomDangChon, tuKhoa], () => {
  trang.value = 1
})

watch(tuKhoa, (value) => {
  router.replace({ name: 'thu-vien-nganh-nghe', query: { ...route.query, q: value.trim() || undefined } })
})

function chonNhom(ma) {
  router.replace({ name: 'thu-vien-nganh-nghe', query: { ...route.query, nhom: ma || undefined } })
}

// Ảnh của nghề → ảnh của nhóm → ảnh mặc định hướng đi làm. Ảnh tải lên Thư viện lưu đường dẫn tương đối:
// ghép origin API qua apiAssetUrl.
function anhNghe(nghe) {
  const anh = nghe.hinh_anh_mo_ta || nhomTheoId.value[nghe.nhom_nghe_di_lam_id]?.hinh_anh_mo_ta
  return anh ? apiAssetUrl(anh) : anhMacDinh
}

// Nghề đang xem lưu trên query ?nghe=<id> để chia sẻ link được; đóng modal thì bỏ query.
const ngheDangXem = computed(() => dsNgheHopLe.value.find((nghe) => String(nghe.id) === String(route.query.nghe)) || null)
const chiTietMo = computed({
  get: () => !!ngheDangXem.value,
  set: (mo) => {
    if (!mo) router.replace({ name: 'thu-vien-nganh-nghe', query: { ...route.query, nghe: undefined } })
  },
})

function moChiTiet(nghe) {
  router.replace({ name: 'thu-vien-nganh-nghe', query: { ...route.query, nghe: nghe.id } })
}

async function taiDuLieu() {
  dangTai.value = true
  loi.value = ''
  try {
    const [nhom, nghe] = await Promise.all([
      fetchNhomNgheDiLam({ trang_thai: 1, page: 1, page_size: 100 }),
      fetchNgheCuTheDiLam({ page: 1, page_size: 1000 }),
    ])
    dsNhomNghe.value = nhom.items || []
    dsNghe.value = nghe.items || []
  } catch {
    loi.value = 'Không tải được danh sách nghề.'
  } finally {
    dangTai.value = false
  }
}

onMounted(taiDuLieu)
</script>

<style scoped>
.thu-vien__so {
  margin-left: 6px;
  padding: 0 7px;
  border-radius: 999px;
  background: var(--lp-primary-soft);
  color: var(--lp-primary-strong);
  font-size: 0.8rem;
}

.landing-explore__chip.is-active .thu-vien__so {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.thu-vien__trang-thai,
.thu-vien__dem {
  margin: 0 0 var(--lp-gap-sm);
  color: var(--lp-muted);
}

.thu-vien__phan-trang {
  display: flex;
  justify-content: center;
  margin-top: var(--lp-gap);
}

.thu-vien__ho-tro {
  margin-top: calc(var(--lp-gap) * 2);
}
</style>
