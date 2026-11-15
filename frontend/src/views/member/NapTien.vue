<template>
  <el-card shadow="never" class="nap-tien">
    <template #header>
      <div class="nap-tien__header">
        <div>
          <h1 class="nap-tien__title">Nạp tiền</h1>
          <p class="nap-tien__lead">Nạp Edu coin hoặc mua thêm lượt tra cứu, hỏi đáp, khảo sát.</p>
        </div>
        <div class="nap-tien__actions">
          <CustomButton v-if="duongQuayLai" @click="quayLai">
            <CustomIcon><Back /></CustomIcon>
            <span>Quay lại tìm trường</span>
          </CustomButton>
          <CustomButton @click="router.push({ name: 'lich-su-nap-tien' })">
            <CustomIcon><Tickets /></CustomIcon>
            <span>Lịch sử nạp tiền</span>
          </CustomButton>
        </div>
      </div>
    </template>

    <section class="so-du" aria-label="Số dư tài khoản">
      <article v-for="item in LOAI" :key="item.key" class="so-du__card" :class="`so-du__card--${item.key}`">
        <span class="so-du__icon" aria-hidden="true">
          <CustomIcon><component :is="item.icon" /></CustomIcon>
        </span>
        <div class="so-du__body">
          <span class="so-du__label">{{ item.nhanSoDu }}</span>
          <strong class="so-du__value">{{ soDu ? hienSo(soDu[item.truongSoDu]) : '—' }}</strong>
          <span v-if="item.key === 'tra_cuu' && luotMienPhi" class="so-du__sub">
            Miễn phí hôm nay: {{ luotMienPhi.con_lai ?? 0 }}/{{ luotMienPhi.so_luot_ngay }}
          </span>
          <span v-else class="so-du__sub">{{ item.donVi }}</span>
        </div>
      </article>
    </section>
    <p v-if="loiSoDu" class="nap-tien__muted">{{ loiSoDu }}</p>

    <el-tabs v-model="tab" class="nap-tien__tabs">
      <el-tab-pane v-for="item in LOAI" :key="item.key" :name="item.key">
        <template #label>
          <span class="nap-tien__tab-label">
            <CustomIcon><component :is="item.icon" /></CustomIcon>
            {{ item.tenTab }}
          </span>
        </template>

        <p v-if="dangTaiGoi" class="nap-tien__muted">Đang tải các gói…</p>
        <p v-else-if="loiGoi" class="nap-tien__muted">{{ loiGoi }}</p>
        <CustomEmpty
          v-else-if="!goiTheoLoai[item.key].length"
          :description="`Hiện chưa có gói ${item.tenTab.toLowerCase()} đang bán.`"
          :image-size="80"
        />
        <div v-else class="goi-list">
          <article v-for="goi in goiTheoLoai[item.key]" :key="goi.id" class="goi">
            <span v-if="coKhuyenMai(goi)" class="goi__badge">Khuyến mãi</span>
            <span class="goi__name">{{ goi.ten_goi_cuoc }}</span>
            <span class="goi__luot">
              <s v-if="khac(goi.so_luot_nhan_duoc_khuyen_mai, goi.so_luot_nhan_duoc_goc)" class="goi__cu">
                {{ hienSo(goi.so_luot_nhan_duoc_goc) }}
              </s>
              <strong>{{ hienSo(luotNhan(goi)) }}</strong> {{ item.donVi }}
            </span>
            <span class="goi__gia">
              <s v-if="khac(goi.gia_khuyen_mai, goi.gia_goc)" class="goi__cu">{{ hienTien(goi.gia_goc) }}</s>
              {{ hienTien(giaBan(goi)) }}
            </span>
            <span v-if="item.key !== 'edu_coin' && luotNhan(goi) > 0" class="goi__don-gia">
              ≈ {{ hienTien(Math.round(giaBan(goi) / luotNhan(goi))) }} / lượt
            </span>
            <CustomButton
              type="primary"
              class="goi__dang-ky"
              :loading="dangDangKy === goi.id"
              :disabled="dangDangKy !== null && dangDangKy !== goi.id"
              @click="dangKy(goi)"
            >
              Đăng ký
            </CustomButton>
          </article>
        </div>
      </el-tab-pane>
    </el-tabs>

    <ThanhToanDialog v-model="thanhToanMo" :giao-dich="giaoDich" :goi="goiThanhToan" @updated="giaoDich = $event" />
  </el-card>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Coin, EditPen, Search } from '@element-plus/icons-vue'
import ThanhToanDialog from '@/components/member/ThanhToanDialog.vue'
import { fetchGoiCuocDangBan } from '@/api/cauHinhGoiCuoc'
import { fetchHoSo } from '@/api/hoSo'
import { taoNapTien } from '@/api/napTien'
import { fetchLuotTimTruong } from '@/api/timTruongPhuHop'

defineOptions({ name: 'MemberNapTien' })

// key khớp loai_ap_dung của gói cước; truongSoDu là trường số dư trong hồ sơ (GET /tai-khoan/ho-so).
const LOAI = [
  { key: 'edu_coin', tenTab: 'Edu coin', nhanSoDu: 'Edu coin', truongSoDu: 'edu_coin', donVi: 'Edu coin', icon: Coin },
  { key: 'tra_cuu', tenTab: 'Tra cứu', nhanSoDu: 'Lượt tra cứu', truongSoDu: 'luot_tra_cuu', donVi: 'lượt tra cứu', icon: Search },
  { key: 'hoi_dap', tenTab: 'Hỏi đáp', nhanSoDu: 'Lượt hỏi đáp', truongSoDu: 'luot_hoi_dap', donVi: 'lượt hỏi đáp', icon: ChatDotRound },
  { key: 'khao_sat', tenTab: 'Khảo sát', nhanSoDu: 'Lượt khảo sát', truongSoDu: 'luot_khao_sat', donVi: 'lượt khảo sát', icon: EditPen },
]
const KEYS = LOAI.map((item) => item.key)

const route = useRoute()
const router = useRouter()
const soDu = ref(null)
const loiSoDu = ref('')
const luotMienPhi = ref(null)
const dsGoi = ref([])
const dangTaiGoi = ref(false)
const loiGoi = ref('')
const thanhToanMo = ref(false)
const giaoDich = ref(null)
const goiThanhToan = ref(null)
const dangDangKy = ref(null)

// Chỉ quay về trang trong ứng dụng, tránh chuyển hướng ra ngoài.
const duongQuayLai = computed(() => {
  const value = String(route.query.redirect || '')
  return value.startsWith('/') && !value.startsWith('//') ? value : ''
})

// Tab mở đầu: theo ?loai=, đến từ trang tìm trường thì mở Tra cứu, còn lại mở Edu coin.
function tabBanDau() {
  const loai = String(route.query.loai || '')
  if (KEYS.includes(loai)) return loai
  return duongQuayLai.value ? 'tra_cuu' : 'edu_coin'
}

const tab = ref(tabBanDau())

watch(tab, (value) => {
  if (route.query.loai === value) return
  router.replace({ query: { ...route.query, loai: value } })
})

const goiTheoLoai = computed(() =>
  Object.fromEntries(KEYS.map((key) => [key, dsGoi.value.filter((goi) => goi.loai_ap_dung === key)])),
)

function khac(khuyenMai, goc) {
  return khuyenMai !== null && khuyenMai !== undefined && Number(khuyenMai) !== Number(goc)
}

function coKhuyenMai(goi) {
  return khac(goi.gia_khuyen_mai, goi.gia_goc) || khac(goi.so_luot_nhan_duoc_khuyen_mai, goi.so_luot_nhan_duoc_goc)
}

function giaBan(goi) {
  return goi.gia_khuyen_mai ?? goi.gia_goc
}

function luotNhan(goi) {
  return goi.so_luot_nhan_duoc_khuyen_mai ?? goi.so_luot_nhan_duoc_goc
}

function hienSo(value) {
  return Number(value || 0).toLocaleString('vi-VN')
}

function hienTien(value) {
  return `${hienSo(value)} đ`
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

// Đăng ký: tạo (hoặc dùng lại) giao dịch chờ thanh toán rồi mở modal thanh toán.
async function dangKy(goi) {
  dangDangKy.value = goi.id
  try {
    giaoDich.value = await taoNapTien({ goi_cuoc_id: goi.id })
    goiThanhToan.value = goi
    thanhToanMo.value = true
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đăng ký được gói'))
  } finally {
    dangDangKy.value = null
  }
}

function quayLai() {
  router.push(duongQuayLai.value)
}

async function taiSoDu() {
  loiSoDu.value = ''
  try {
    soDu.value = await fetchHoSo({ skipLoading: true })
  } catch {
    soDu.value = null
    loiSoDu.value = 'Không tải được số dư tài khoản.'
  }
}

async function taiLuotMienPhi() {
  try {
    luotMienPhi.value = await fetchLuotTimTruong()
  } catch {
    luotMienPhi.value = null
  }
}

async function taiGoi() {
  dangTaiGoi.value = true
  loiGoi.value = ''
  try {
    dsGoi.value = await fetchGoiCuocDangBan()
  } catch {
    dsGoi.value = []
    loiGoi.value = 'Không tải được danh sách gói.'
  } finally {
    dangTaiGoi.value = false
  }
}

// Đóng modal thì tải lại số dư (giao dịch có thể đã được cộng qua webhook).
watch(thanhToanMo, (open) => {
  if (!open) taiSoDu()
})

onMounted(() => {
  taiSoDu()
  taiLuotMienPhi()
  taiGoi()
})
</script>

<style scoped>
.nap-tien {
  border-radius: 12px;
}

.nap-tien__header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.nap-tien__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.nap-tien__title {
  margin: 0 0 4px;
  font-size: 20px;
  line-height: 1.4;
}

.nap-tien__lead,
.nap-tien__muted {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
}

/* Card số dư */
.so-du {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 8px;
}

.so-du__card {
  --so-du-color: #0c5c34;
  --so-du-bg: #eef6f1;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: 14px 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
}

.so-du__card--edu_coin {
  --so-du-color: #a15c07;
  --so-du-bg: #fff4e0;
}

.so-du__card--hoi_dap {
  --so-du-color: #1f5fa8;
  --so-du-bg: #eaf2fc;
}

.so-du__card--khao_sat {
  --so-du-color: #7a3fb0;
  --so-du-bg: #f4ecfb;
}

.so-du__icon {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: var(--so-du-bg);
  color: var(--so-du-color);
  font-size: 20px;
}

.so-du__body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.so-du__label,
.so-du__sub {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.4;
}

.so-du__sub {
  font-size: 12px;
}

.so-du__value {
  color: var(--so-du-color);
  font-size: 22px;
  line-height: 1.3;
}

/* Tabs và gói */
.nap-tien__tabs {
  margin-top: 16px;
}

.nap-tien__tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.goi-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding-top: 10px;
}

.goi {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 16px;
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
  transition: border-color 0.2s ease;
}

.goi:hover {
  border-color: #3f9466;
}

.goi__dang-ky {
  align-self: stretch;
  margin-top: 8px;
}

.goi__badge {
  position: absolute;
  top: -10px;
  right: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--el-color-danger);
  color: #fff;
  font-size: 12px;
}

.goi__name {
  font-weight: 600;
}

.goi__luot,
.goi__don-gia {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.goi__luot strong {
  color: var(--el-text-color-primary);
}

.goi__cu {
  margin-right: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  font-weight: 400;
}

.goi__gia {
  margin-top: 4px;
  color: #0c5c34;
  font-size: 20px;
  font-weight: 700;
}

@media (max-width: 991px) {
  .so-du {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .so-du__card {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }

  .goi-list {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .goi {
    transition: none;
  }
}
</style>
