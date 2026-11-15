<template>
  <el-card shadow="never" class="nap-tien">
    <template #header>
      <div class="nap-tien__header">
        <div>
          <h1 class="nap-tien__title">Nạp tiền</h1>
          <p class="nap-tien__lead">Nạp Edu coin hoặc mua thêm lượt tra cứu, hỏi đáp, khảo sát.</p>
        </div>
        <CustomButton v-if="duongQuayLai" @click="quayLai">
          <CustomIcon><Back /></CustomIcon>
          <span>Quay lại tìm trường</span>
        </CustomButton>
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
            <CustomButton type="primary" class="goi__dang-ky" @click="moThanhToan(goi)">Đăng ký</CustomButton>
          </article>
        </div>
      </el-tab-pane>
    </el-tabs>

    <CustomDialog v-model="thanhToanMo" title="Thanh toán gói cước" width="860px" @closed="goiThanhToan = null">
      <div v-if="goiThanhToan" class="thanh-toan">
        <section class="thanh-toan__goi" aria-label="Thông tin gói">
          <div>
            <span class="thanh-toan__loai">{{ loaiCuaGoi(goiThanhToan).tenTab }}</span>
            <h3 class="thanh-toan__ten">{{ goiThanhToan.ten_goi_cuoc }}</h3>
            <span class="nap-tien__muted">Mã gói: {{ goiThanhToan.ma_goi_cuoc }}</span>
          </div>
          <dl class="thanh-toan__tom-tat">
            <div>
              <dt>Nhận được</dt>
              <dd>
                <s v-if="khac(goiThanhToan.so_luot_nhan_duoc_khuyen_mai, goiThanhToan.so_luot_nhan_duoc_goc)" class="goi__cu">
                  {{ hienSo(goiThanhToan.so_luot_nhan_duoc_goc) }}
                </s>
                <strong>{{ hienSo(luotNhan(goiThanhToan)) }}</strong> {{ loaiCuaGoi(goiThanhToan).donVi }}
              </dd>
            </div>
            <div>
              <dt>Thanh toán</dt>
              <dd>
                <s v-if="khac(goiThanhToan.gia_khuyen_mai, goiThanhToan.gia_goc)" class="goi__cu">
                  {{ hienTien(goiThanhToan.gia_goc) }}
                </s>
                <strong class="thanh-toan__gia">{{ hienTien(giaBan(goiThanhToan)) }}</strong>
              </dd>
            </div>
          </dl>
        </section>

        <!-- Trái: danh sách ngân hàng; phải: mã QR và thông tin chuyển khoản. Khung hẹp thì xếp dọc. -->
        <div class="thanh-toan__than">
          <section class="thanh-toan__ngan-hang" aria-label="Chọn ngân hàng">
            <h4 class="thanh-toan__heading">Chọn ngân hàng thanh toán</h4>
            <p v-if="loiNganHang" class="nap-tien__muted">{{ loiNganHang }}</p>
            <p v-else-if="dangTaiNganHang" class="nap-tien__muted">Đang tải tài khoản nhận tiền…</p>
            <p v-else-if="!nganHang.length" class="nap-tien__muted">
              Hệ thống chưa có tài khoản nhận tiền, vui lòng quay lại sau.
            </p>
            <div v-else class="bank-pick" role="radiogroup" aria-label="Ngân hàng nhận tiền">
              <button
                v-for="item in nganHang"
                :key="item.id"
                type="button"
                role="radio"
                class="bank-pick__item"
                :class="{ 'is-active': nganHangChonId === item.id }"
                :aria-checked="nganHangChonId === item.id"
                @click="nganHangChonId = item.id"
              >
                <img
                  v-if="item.logo_ngan_hang"
                  class="bank__logo"
                  :src="apiAssetUrl(item.logo_ngan_hang)"
                  :alt="item.ten_ngan_hang_viet_tat"
                />
                <span class="bank-pick__text">
                  <strong>{{ item.ten_ngan_hang_viet_tat }}</strong>
                  <span class="nap-tien__muted">{{ item.so_tai_khoan }}</span>
                </span>
              </button>
            </div>
          </section>

          <section v-if="nganHangChon" class="thanh-toan__chuyen-khoan" aria-label="Thông tin chuyển khoản">
            <div class="thanh-toan__qr">
              <img
                v-if="!loiQr"
                :key="qrUrl"
                :src="qrUrl"
                :alt="`Mã VietQR chuyển khoản ${hienTien(giaBan(goiThanhToan))} tới ${nganHangChon.ten_ngan_hang_viet_tat}`"
                width="260"
                height="260"
                @error="loiQr = true"
              />
              <p v-else class="thanh-toan__qr-loi">
                Không tạo được mã QR cho ngân hàng này. Vui lòng chuyển khoản theo thông tin bên cạnh.
              </p>
              <!-- <span class="nap-tien__muted">Quét bằng ứng dụng ngân hàng để điền sẵn số tiền và nội dung.</span> -->
            </div>
            <dl class="bank__info">
              <div v-for="dong in thongTinChuyenKhoan" :key="dong.nhan" class="bank__row">
                <dt>{{ dong.nhan }}</dt>
                <dd>
                  <span :class="{ 'bank__value--strong': dong.dam }">{{ dong.hien }}</span>
                  <CustomButton
                    v-if="dong.saoChep"
                    link
                    type="primary"
                    :aria-label="`Sao chép ${dong.nhan.toLowerCase()}`"
                    @click="saoChep(dong.saoChep, dong.nhan)"
                  >
                    <CustomIcon><CopyDocument /></CustomIcon>
                  </CustomButton>
                </dd>
              </div>
            </dl>
          </section>
        </div>

        <p class="nap-tien__note">
          Ghi đúng nội dung chuyển khoản để hệ thống nhận ra tài khoản và gói bạn mua. Edu coin hoặc lượt mua thêm sẽ
          được cộng sau khi thanh toán được xác nhận.
        </p>
      </div>
      <template #footer>
        <CustomButton @click="thanhToanMo = false">Đóng</CustomButton>
      </template>
    </CustomDialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Coin, EditPen, Search } from '@element-plus/icons-vue'
import { apiAssetUrl } from '@/api/apiUrl'
import { fetchGoiCuocDangBan } from '@/api/cauHinhGoiCuoc'
import { fetchHoSo } from '@/api/hoSo'
import { fetchNganHangNhanTien } from '@/api/nganHangThanhToan'
import { fetchLuotTimTruong } from '@/api/timTruongPhuHop'
import { useAuthStore } from '@/stores/auth'

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
const auth = useAuthStore()
const soDu = ref(null)
const loiSoDu = ref('')
const luotMienPhi = ref(null)
const dsGoi = ref([])
const dangTaiGoi = ref(false)
const loiGoi = ref('')
const nganHang = ref([])
const dangTaiNganHang = ref(false)
const loiNganHang = ref('')
const thanhToanMo = ref(false)
const goiThanhToan = ref(null)
const nganHangChonId = ref(null)
const loiQr = ref(false)

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
const nganHangChon = computed(() => nganHang.value.find((item) => item.id === nganHangChonId.value) || null)
// Nội dung chuyển khoản chỉ gồm chữ, số và khoảng trắng: nhiều ngân hàng tự bỏ ký tự đặc biệt như "_".
const noiDungChuyenKhoan = computed(() => {
  const ma = String(goiThanhToan.value?.ma_goi_cuoc || '').replace(/[^0-9A-Za-z]/g, '').toUpperCase()
  return `DHN ${auth.user?.id || ''} ${ma}`.replace(/\s+/g, ' ').trim()
})
// Ảnh VietQR (img.vietqr.io): mã ngân hàng là tên viết tắt (VCB, MB, ICB, ...) hoặc mã BIN theo danh sách VietQR.
const qrUrl = computed(() => {
  const bank = nganHangChon.value
  const goi = goiThanhToan.value
  if (!bank || !goi) return ''
  const params = new URLSearchParams({
    amount: String(giaBan(goi)),
    addInfo: noiDungChuyenKhoan.value,
    accountName: bank.chu_tai_khoan,
  })
  const ma = encodeURIComponent(bank.ten_ngan_hang_viet_tat)
  const stk = encodeURIComponent(bank.so_tai_khoan)
  return `https://img.vietqr.io/image/${ma}-${stk}-compact2.png?${params}`
})
const thongTinChuyenKhoan = computed(() => {
  const bank = nganHangChon.value
  if (!bank || !goiThanhToan.value) return []
  const gia = giaBan(goiThanhToan.value)
  return [
    { nhan: 'Ngân hàng', hien: `${bank.ten_ngan_hang_viet_tat} - ${bank.ten_ngan_hang}` },
    { nhan: 'Số tài khoản', hien: bank.so_tai_khoan, saoChep: bank.so_tai_khoan, dam: true },
    { nhan: 'Chủ tài khoản', hien: bank.chu_tai_khoan },
    { nhan: 'Số tiền', hien: hienTien(gia), saoChep: String(gia), dam: true },
    { nhan: 'Nội dung', hien: noiDungChuyenKhoan.value, saoChep: noiDungChuyenKhoan.value, dam: true },
  ]
})

watch(qrUrl, () => {
  loiQr.value = false
})

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

function loaiCuaGoi(goi) {
  return LOAI.find((item) => item.key === goi.loai_ap_dung) || LOAI[0]
}

function moThanhToan(goi) {
  goiThanhToan.value = goi
  if (!nganHang.value.some((item) => item.id === nganHangChonId.value)) {
    nganHangChonId.value = nganHang.value[0]?.id ?? null
  }
  thanhToanMo.value = true
}

async function saoChep(text, nhan) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(`Đã sao chép ${nhan.toLowerCase()}`)
  } catch {
    ElMessage.error('Không sao chép được')
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

async function taiNganHang() {
  dangTaiNganHang.value = true
  loiNganHang.value = ''
  try {
    nganHang.value = await fetchNganHangNhanTien()
    nganHangChonId.value ??= nganHang.value[0]?.id ?? null
  } catch {
    loiNganHang.value = 'Không tải được tài khoản nhận tiền.'
  } finally {
    dangTaiNganHang.value = false
  }
}

onMounted(() => {
  taiSoDu()
  taiLuotMienPhi()
  taiGoi()
  taiNganHang()
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

/* Modal thanh toán: 2 cột khi khung dialog đủ rộng (container query), hẹp thì xếp dọc. */
.thanh-toan {
  container-type: inline-size;
  display: grid;
  gap: 16px;
}

.thanh-toan__goi {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--el-fill-color-lighter);
}

.thanh-toan__loai {
  display: inline-block;
  margin-bottom: 4px;
  padding: 1px 8px;
  border-radius: 999px;
  background: #eef6f1;
  color: #0c5c34;
  font-size: 12px;
}

.thanh-toan__ten {
  margin: 0 0 2px;
  font-size: 18px;
}

.thanh-toan__tom-tat {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin: 0;
}

.thanh-toan__tom-tat dt {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  font-weight: 400;
}

.thanh-toan__tom-tat dd {
  margin: 0;
}

.thanh-toan__gia {
  color: #0c5c34;
  font-size: 20px;
}

.thanh-toan__heading {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 600;
}

.thanh-toan__than {
  display: grid;
  gap: 16px;
  align-items: start;
}

.bank-pick {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 8px;
}

.bank-pick__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 10px;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
  text-align: left;
  cursor: pointer;
}

.bank-pick__item:hover {
  border-color: #3f9466;
}

.bank-pick__item.is-active {
  border-color: #0c5c34;
  box-shadow: 0 0 0 2px #0c5c34;
}

.bank-pick__text {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow-wrap: anywhere;
}

.thanh-toan__chuyen-khoan {
  display: grid;
  gap: 16px;
  align-items: start;
}

.thanh-toan__qr {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.thanh-toan__qr img {
  width: 260px;
  max-width: 100%;
  height: auto;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: #fff;
}

.thanh-toan__qr-loi {
  margin: 0;
  padding: 16px;
  border: 1px dashed var(--el-border-color);
  border-radius: 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

@container (min-width: 640px) {
  .thanh-toan__than {
    grid-template-columns: 260px minmax(0, 1fr);
  }

  .thanh-toan__ngan-hang .bank-pick {
    grid-template-columns: minmax(0, 1fr);
    max-height: 480px;
    overflow-y: auto;
    padding: 2px;
  }

  .thanh-toan__chuyen-khoan {
    padding-left: 16px;
    border-left: 1px solid var(--el-border-color-lighter);
  }
}

.bank__logo {
  width: 56px;
  height: 36px;
  object-fit: contain;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  background: #fff;
}

.bank__info {
  display: grid;
  gap: 6px;
  margin: 0;
}

.bank__row {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 8px;
  align-items: center;
}

.bank__row dt {
  color: var(--el-text-color-secondary);
  font-weight: 400;
}

.bank__row dd {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0;
  overflow-wrap: anywhere;
}

.bank__value--strong {
  font-weight: 600;
}

.nap-tien__note {
  margin: 12px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
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
