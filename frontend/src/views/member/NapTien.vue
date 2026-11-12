<template>
  <el-card shadow="never" class="nap-tien">
    <template #header>
      <div class="nap-tien__header">
        <div>
          <h1 class="nap-tien__title">Nạp tiền</h1>
          <p class="nap-tien__lead">Mua thêm lượt tìm trường phù hợp khi đã dùng hết lượt miễn phí trong ngày.</p>
        </div>
        <CustomButton v-if="duongQuayLai" @click="quayLai">
          <CustomIcon><Back /></CustomIcon>
          <span>Quay lại tìm trường</span>
        </CustomButton>
      </div>
    </template>

    <section class="nap-tien__section">
      <h2 class="nap-tien__heading">Lượt tìm trường hôm nay</h2>
      <p v-if="luot" class="nap-tien__luot" :class="{ 'is-het': !luot.con_lai }">
        Còn <strong>{{ luot.con_lai ?? 0 }}/{{ luot.so_luot_ngay }}</strong> lượt miễn phí hôm nay.
        <span v-if="!luot.con_lai">Lượt miễn phí sẽ được làm mới vào ngày mai.</span>
      </p>
      <p v-else class="nap-tien__muted">Đang tải số lượt…</p>
    </section>

    <section class="nap-tien__section">
      <h2 class="nap-tien__heading">1. Chọn gói lượt</h2>
      <div class="goi-list" role="radiogroup" aria-label="Gói lượt tìm trường">
        <button
          v-for="goi in GOI_LUOT"
          :key="goi.ma"
          type="button"
          role="radio"
          class="goi"
          :class="{ 'is-active': goiChon === goi.ma }"
          :aria-checked="goiChon === goi.ma"
          @click="goiChon = goi.ma"
        >
          <span v-if="goi.goiY" class="goi__badge">{{ goi.goiY }}</span>
          <span class="goi__name">{{ goi.ten }}</span>
          <span class="goi__luot">{{ goi.soLuot }} lượt tìm trường</span>
          <span class="goi__gia">{{ hienTien(goi.gia) }}</span>
          <span class="goi__don-gia">≈ {{ hienTien(Math.round(goi.gia / goi.soLuot)) }} / lượt</span>
        </button>
      </div>
      <p class="nap-tien__muted">Giá các gói đang là giá tham khảo.</p>
    </section>

    <section class="nap-tien__section">
      <h2 class="nap-tien__heading">2. Chuyển khoản</h2>
      <p v-if="loiNganHang" class="nap-tien__muted">{{ loiNganHang }}</p>
      <p v-else-if="dangTaiNganHang" class="nap-tien__muted">Đang tải tài khoản nhận tiền…</p>
      <p v-else-if="!nganHang.length" class="nap-tien__muted">Hệ thống chưa có tài khoản nhận tiền, vui lòng quay lại sau.</p>
      <div v-else class="bank-list">
        <article v-for="item in nganHang" :key="item.id" class="bank">
          <div class="bank__head">
            <img v-if="item.logo_ngan_hang" class="bank__logo" :src="apiAssetUrl(item.logo_ngan_hang)" :alt="item.ten_ngan_hang_viet_tat" />
            <div>
              <strong>{{ item.ten_ngan_hang_viet_tat }}</strong>
              <span class="nap-tien__muted d-block">{{ item.ten_ngan_hang }}</span>
            </div>
          </div>
          <dl class="bank__info">
            <div v-for="dong in thongTinChuyenKhoan(item)" :key="dong.nhan" class="bank__row">
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
        </article>
      </div>
      <p class="nap-tien__note">
        Ghi đúng nội dung chuyển khoản để hệ thống nhận ra tài khoản của bạn. Lượt mua thêm sẽ được cộng sau khi
        thanh toán được xác nhận.
      </p>
    </section>
  </el-card>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apiAssetUrl } from '@/api/apiUrl'
import { fetchNganHangNhanTien } from '@/api/nganHangThanhToan'
import { fetchLuotTimTruong } from '@/api/timTruongPhuHop'
import { useAuthStore } from '@/stores/auth'

defineOptions({ name: 'MemberNapTien' })

// Gói tham khảo để lên giao diện, sẽ lấy từ cấu hình khi có bảng gói và luồng thanh toán.
const GOI_LUOT = [
  { ma: 'G5', ten: 'Gói cơ bản', soLuot: 5, gia: 20000 },
  { ma: 'G15', ten: 'Gói phổ biến', soLuot: 15, gia: 50000, goiY: 'Phổ biến' },
  { ma: 'G40', ten: 'Gói tiết kiệm', soLuot: 40, gia: 100000, goiY: 'Tiết kiệm nhất' },
]

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const luot = ref(null)
const nganHang = ref([])
const dangTaiNganHang = ref(false)
const loiNganHang = ref('')
const goiChon = ref(GOI_LUOT[1].ma)

const goi = computed(() => GOI_LUOT.find((item) => item.ma === goiChon.value) || GOI_LUOT[0])
const noiDungChuyenKhoan = computed(() => `DHN ${auth.user?.id || ''} ${goi.value.ma}`.replace(/\s+/g, ' ').trim())
// Chỉ quay về trang trong ứng dụng, tránh chuyển hướng ra ngoài.
const duongQuayLai = computed(() => {
  const value = String(route.query.redirect || '')
  return value.startsWith('/') && !value.startsWith('//') ? value : ''
})

function hienTien(value) {
  return `${Number(value || 0).toLocaleString('vi-VN')} đ`
}

function thongTinChuyenKhoan(item) {
  return [
    { nhan: 'Số tài khoản', hien: item.so_tai_khoan, saoChep: item.so_tai_khoan, dam: true },
    { nhan: 'Chủ tài khoản', hien: item.chu_tai_khoan },
    { nhan: 'Số tiền', hien: hienTien(goi.value.gia), saoChep: String(goi.value.gia), dam: true },
    { nhan: 'Nội dung', hien: noiDungChuyenKhoan.value, saoChep: noiDungChuyenKhoan.value, dam: true },
  ]
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

async function taiLuot() {
  try {
    luot.value = await fetchLuotTimTruong()
  } catch {
    luot.value = null
  }
}

async function taiNganHang() {
  dangTaiNganHang.value = true
  loiNganHang.value = ''
  try {
    nganHang.value = await fetchNganHangNhanTien()
  } catch {
    loiNganHang.value = 'Không tải được tài khoản nhận tiền.'
  } finally {
    dangTaiNganHang.value = false
  }
}

onMounted(() => {
  taiLuot()
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

.d-block {
  display: block;
}

.nap-tien__section + .nap-tien__section {
  margin-top: 24px;
}

.nap-tien__heading {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 600;
}

.nap-tien__luot {
  margin: 0;
  padding: 10px 14px;
  border: 1px solid #b7d0c2;
  border-radius: 10px;
  background: #eef6f1;
  color: #0c5c34;
}

.nap-tien__luot.is-het {
  border-color: #f0c9a8;
  background: #fff6ee;
  color: #7a3f13;
}

.goi-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 8px;
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
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.goi:hover {
  border-color: #3f9466;
}

.goi.is-active {
  border-color: #0c5c34;
  box-shadow: 0 0 0 2px #0c5c34;
}

.goi__badge {
  position: absolute;
  top: -10px;
  right: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: #0c5c34;
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

.goi__gia {
  margin-top: 4px;
  color: #0c5c34;
  font-size: 20px;
  font-weight: 700;
}

.bank-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.bank {
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-fill-color-lighter);
}

.bank__head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
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

@media (max-width: 767px) {
  .goi-list {
    grid-template-columns: minmax(0, 1fr);
  }

  .bank-list {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .goi {
    transition: none;
  }
}
</style>
