<template>
  <section class="thcs py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="intro-card mb-3">
            <RouterLink class="thcs__quay-lai" :to="{ name: DOI_TUONG_THCS }">← Tất cả hướng đi</RouterLink>
            <h1 class="thcs__title">Tìm hướng đi phù hợp sau lớp 9</h1>
            <p class="thcs__lead mb-0">
              Chọn mức đúng với bạn ở từng tiêu chí (1 là rất thấp, 5 là rất cao). Trả lời càng nhiều tiêu chí, gợi ý càng
              sát. Kết quả chỉ để tham khảo, hãy trao đổi thêm với bố mẹ và thầy cô.
            </p>
          </div>

          <div v-if="dangTai" class="stages-card thcs__trang-thai" role="status">Đang tải câu hỏi…</div>
          <div v-else-if="loi" class="stages-card thcs__trang-thai">
            {{ loi }}
            <button type="button" class="thcs__thu-lai" @click="taiDuLieu">Thử lại</button>
          </div>
          <div v-else-if="!dsTieuChi.length" class="stages-card thcs__trang-thai">Chưa có tiêu chí để tự đánh giá.</div>

          <template v-else>
            <div class="stages-card">
              <div v-for="nhom in nhomTieuChi" :key="nhom.ten" class="nhom-cau">
                <h2 class="nhom-cau__ten">{{ nhom.ten }}</h2>
                <fieldset v-for="tc in nhom.items" :key="tc.id" class="cau-hoi">
                  <legend class="cau-hoi__ten">{{ tc.ten_tieu_chi }}</legend>
                  <p v-if="tc.mo_ta_tieu_chi" class="cau-hoi__mo-ta">{{ tc.mo_ta_tieu_chi }}</p>
                  <div class="thang-diem" role="radiogroup" :aria-label="tc.ten_tieu_chi">
                    <button
                      v-for="muc in THANG_DIEM"
                      :key="muc.value"
                      type="button"
                      role="radio"
                      class="thang-diem__muc"
                      :class="{ 'is-active': traLoi[tc.id] === muc.value }"
                      :aria-checked="traLoi[tc.id] === muc.value"
                      @click="chon(tc.id, muc.value)"
                    >
                      <span class="thang-diem__so">{{ muc.value }}</span>
                      <span class="thang-diem__nhan">{{ muc.label }}</span>
                    </button>
                  </div>
                </fieldset>
              </div>

              <div class="hanh-dong">
                <span class="hanh-dong__dem">Đã trả lời {{ soDaTraLoi }}/{{ dsTieuChi.length }} tiêu chí</span>
                <button v-if="soDaTraLoi" type="button" class="nut nut--phu" @click="lamLai">Làm lại</button>
                <button type="button" class="nut" :disabled="soDaTraLoi < SO_CAU_TOI_THIEU" @click="xemKetQua">
                  Xem gợi ý
                </button>
              </div>
              <p v-if="soDaTraLoi < SO_CAU_TOI_THIEU" class="hanh-dong__nhac">
                Trả lời ít nhất {{ SO_CAU_TOI_THIEU }} tiêu chí để xem gợi ý.
              </p>
            </div>

            <div v-if="daXem && ketQua.length" id="ket-qua" ref="ketQuaEl" class="stages-card mt-3">
              <h2 class="ket-qua__title">Gợi ý hướng đi cho bạn</h2>
              <ol class="ket-qua">
                <li v-for="(item, index) in ketQua" :key="item.huong.id" class="ket-qua__muc" :class="{ 'is-top': index === 0 }">
                  <div class="ket-qua__dau">
                    <span class="ket-qua__hang" aria-hidden="true">{{ index + 1 }}</span>
                    <div class="ket-qua__ten-khoi">
                      <span class="ket-qua__ten">{{ item.huong.ten_huong }}</span>
                      <span v-if="index === 0" class="ket-qua__nhan">Phù hợp nhất</span>
                    </div>
                    <span class="ket-qua__phan-tram">{{ item.diem }}%</span>
                  </div>
                  <div
                    class="ket-qua__thanh"
                    role="meter"
                    :aria-valuenow="item.diem"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    :aria-label="`Mức phù hợp ${item.huong.ten_huong}`"
                  >
                    <span :style="{ width: `${item.diem}%` }"></span>
                  </div>
                  <p v-if="item.hop.length" class="ket-qua__ly-do">
                    <strong>Hợp với bạn:</strong> {{ item.hop.join(', ') }}
                  </p>
                  <p v-if="item.lech.length" class="ket-qua__ly-do ket-qua__ly-do--lech">
                    <strong>Cần cân nhắc:</strong> {{ item.lech.join(', ') }}
                  </p>
                  <RouterLink class="ket-qua__xem" :to="{ name: 'hs-thcs-huong-di', params: { maHuong: item.huong.ma_huong } }">
                    Xem chi tiết hướng đi →
                  </RouterLink>
                </li>
              </ol>
            </div>
            <div v-else-if="daXem" class="stages-card thcs__trang-thai mt-3">
              Chưa đủ dữ liệu điểm phù hợp để gợi ý. Bạn hãy xem từng hướng đi để tự so sánh.
            </div>
          </template>
        </div>

        <div class="col-lg-3">
          <nav class="paths-card" aria-labelledby="menu-huong-di">
            <h2 id="menu-huong-di" class="h4 mb-3">Các hướng đi sau THCS</h2>
            <ul class="menu-huong">
              <li v-for="item in dsHuong" :key="item.id">
                <RouterLink class="menu-huong__muc" :to="{ name: 'hs-thcs-huong-di', params: { maHuong: item.ma_huong } }">
                  <span class="menu-huong__ten">{{ item.ten_huong }}</span>
                  <span v-if="chiPhi(item)" class="menu-huong__phu">{{ chiPhi(item) }}</span>
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
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { huongDiTieuChiApi, tieuChiApi } from '@/api/thcsHuongDi'
import { loadAll } from '@/composables/useThcsHuongDi'
import { DOI_TUONG_THCS } from './routes'
import { chiPhi, mucHop, useDsHuongDiThcs } from './thcs'

defineOptions({ name: 'ThcsTuDanhGia' })

const TRA_LOI_KEY = 'thcs_tu_danh_gia'
const SO_CAU_TOI_THIEU = 3
const THANG_DIEM = [
  { value: 1, label: 'Rất thấp' },
  { value: 2, label: 'Thấp' },
  { value: 3, label: 'Vừa' },
  { value: 4, label: 'Cao' },
  { value: 5, label: 'Rất cao' },
]

const { dsHuong, taiHuongDi } = useDsHuongDiThcs()
const dsTieuChi = ref([])
// { huongDiId: { tieuChiId: điểm phù hợp } }
const diemTheoHuong = ref({})
const dangTai = ref(false)
const loi = ref('')
const traLoi = reactive(docTraLoi())
const daXem = ref(false)
const ketQuaEl = ref()

const soDaTraLoi = computed(() => dsTieuChi.value.filter((tc) => traLoi[tc.id]).length)

const nhomTieuChi = computed(() => {
  const nhom = new Map()
  for (const tc of dsTieuChi.value) {
    const ten = tc.nhom_tieu_chi || 'Khác'
    if (!nhom.has(ten)) nhom.set(ten, [])
    nhom.get(ten).push(tc)
  }
  return [...nhom].map(([ten, items]) => ({ ten, items }))
})

const ketQua = computed(() => {
  const tenTieuChi = Object.fromEntries(dsTieuChi.value.map((tc) => [tc.id, tc.ten_tieu_chi.toLowerCase()]))
  return dsHuong.value
    .map((huong) => {
      const diem = diemTheoHuong.value[huong.id] || {}
      const daTraLoi = Object.keys(diem).filter((id) => traLoi[id])
      return {
        huong,
        diem: mucHop(traLoi, diem),
        // Tiêu chí bạn cao và hướng đi cũng cần cao: lý do hợp; lệch từ 3 bậc trở lên: cần cân nhắc.
        hop: daTraLoi.filter((id) => traLoi[id] >= 4 && diem[id] >= 4).map((id) => tenTieuChi[id]).slice(0, 3),
        lech: daTraLoi.filter((id) => Math.abs(traLoi[id] - diem[id]) >= 3).map((id) => tenTieuChi[id]).slice(0, 3),
      }
    })
    .filter((item) => item.diem != null)
    .sort((a, b) => b.diem - a.diem)
})

function docTraLoi() {
  try {
    return JSON.parse(sessionStorage.getItem(TRA_LOI_KEY) || '{}')
  } catch {
    return {}
  }
}

function luuTraLoi() {
  try {
    sessionStorage.setItem(TRA_LOI_KEY, JSON.stringify(traLoi))
  } catch {
    // Không lưu được (chế độ riêng tư): vẫn dùng được trong phiên hiện tại.
  }
}

function chon(id, value) {
  traLoi[id] = value
  luuTraLoi()
}

function lamLai() {
  for (const key of Object.keys(traLoi)) delete traLoi[key]
  daXem.value = false
  luuTraLoi()
}

async function xemKetQua() {
  daXem.value = true
  await nextTick()
  ketQuaEl.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function taiDuLieu() {
  dangTai.value = true
  loi.value = ''
  try {
    const [tieuChi, diem] = await Promise.all([
      loadAll(tieuChiApi.fetch),
      loadAll(huongDiTieuChiApi.fetch),
      taiHuongDi(),
    ])
    dsTieuChi.value = tieuChi
    const theoHuong = {}
    for (const item of diem) {
      theoHuong[item.thcs_huong_di_id] ??= {}
      theoHuong[item.thcs_huong_di_id][item.thcs_tieu_chi_id] = item.diem_phu_hop
    }
    diemTheoHuong.value = theoHuong
  } catch {
    loi.value = 'Không tải được câu hỏi tự đánh giá.'
  } finally {
    dangTai.value = false
  }
}

onMounted(taiDuLieu)
</script>

<style scoped>
.thcs__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.thcs__thu-lai {
  margin-left: 8px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.thcs__quay-lai {
  display: inline-block;
  margin-bottom: 8px;
  color: var(--guest-primary);
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
}

.thcs__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.35;
}

.thcs__lead {
  color: #3a4742;
  line-height: 1.6;
}

.nhom-cau + .nhom-cau {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e3efe7;
}

.thcs .nhom-cau__ten {
  margin: 0 0 12px;
  color: var(--guest-primary);
  font-size: 1.1rem;
  font-weight: 700;
}

.cau-hoi {
  margin: 0 0 16px;
  padding: 0;
  border: 0;
}

.cau-hoi__ten {
  float: none;
  margin: 0;
  color: #1c2b23;
  font-size: 1rem;
  font-weight: 600;
}

.cau-hoi__mo-ta {
  margin: 2px 0 8px;
  color: #6b7780;
  font-size: 0.875rem;
}

.thang-diem {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  max-width: 560px;
  margin-top: 6px;
}

.thang-diem__muc {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 4px;
  border: 1px solid rgba(var(--guest-primary-rgb), 0.35);
  border-radius: var(--guest-radius-sm);
  background: #fff;
  color: #3a4742;
  cursor: pointer;
}

.thang-diem__muc:hover {
  background: rgba(var(--guest-primary-rgb), 0.08);
}

.thang-diem__muc.is-active {
  border-color: var(--guest-primary);
  background: var(--guest-primary);
  color: #fff;
}

.thang-diem__so {
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.2;
}

.thang-diem__nhan {
  font-size: 0.75rem;
  line-height: 1.2;
}

.hanh-dong {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid #e3efe7;
}

.hanh-dong__dem {
  margin-right: auto;
  color: #6b7780;
  font-size: 0.9rem;
}

.hanh-dong__nhac {
  margin: 8px 0 0;
  color: #6b7780;
  font-size: 0.85rem;
  text-align: right;
}

.nut {
  border: 1px solid var(--guest-primary);
  border-radius: 999px;
  padding: 8px 20px;
  background: var(--guest-primary);
  color: #fff;
  font-weight: 500;
  cursor: pointer;
}

.nut:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nut--phu {
  background: #fff;
  color: var(--guest-primary);
}

.ket-qua__title {
  margin: 0 0 12px;
  font-size: 1.25rem;
  font-weight: 700;
}

.ket-qua {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.ket-qua__muc {
  padding: 14px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius);
  background: #fff;
}

.ket-qua__muc.is-top {
  border-color: var(--guest-primary);
  box-shadow: 0 0 0 1px var(--guest-primary);
}

.ket-qua__dau {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.ket-qua__hang {
  display: inline-flex;
  flex: 0 0 30px;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(var(--guest-primary-rgb), 0.12);
  color: var(--guest-primary);
  font-weight: 700;
}

.is-top .ket-qua__hang {
  background: var(--guest-primary);
  color: #fff;
}

.ket-qua__ten-khoi {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.ket-qua__ten {
  color: #1c2b23;
  font-weight: 700;
  line-height: 1.35;
}

.ket-qua__nhan {
  border-radius: 999px;
  padding: 2px 8px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.72rem;
}

.ket-qua__phan-tram {
  color: var(--guest-primary);
  font-size: 1.15rem;
  font-weight: 700;
}

.ket-qua__thanh {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #e3efe7;
}

.ket-qua__thanh span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--guest-primary);
}

.ket-qua__ly-do {
  margin: 8px 0 0;
  color: #3a4742;
  font-size: 0.875rem;
  line-height: 1.5;
}

.ket-qua__ly-do--lech strong {
  color: #b42318;
}

.ket-qua__xem {
  display: inline-block;
  margin-top: 8px;
  color: var(--guest-primary);
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
}

.menu-huong {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.menu-huong__muc {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid #d7eadf;
  border-left: 4px solid var(--guest-primary);
  border-radius: var(--guest-radius);
  background: #fff;
  text-decoration: none;
}

.menu-huong__ten {
  color: var(--guest-primary);
  font-weight: 700;
  line-height: 1.35;
}

.menu-huong__phu {
  color: #6b7780;
  font-size: 0.8rem;
}

.thang-diem__muc:focus-visible,
.nut:focus-visible,
.thcs__thu-lai:focus-visible,
.thcs__quay-lai:focus-visible,
.ket-qua__xem:focus-visible,
.menu-huong__muc:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

@media (max-width: 575.98px) {
  .thcs__title {
    font-size: 1.4rem;
  }

  .thcs__lead {
    font-size: 0.9rem;
  }

  .thang-diem {
    gap: 4px;
  }

  .thang-diem__nhan {
    font-size: 0.68rem;
  }

  .hanh-dong__dem {
    width: 100%;
  }

  .hanh-dong .nut {
    flex: 1;
  }
}
</style>
