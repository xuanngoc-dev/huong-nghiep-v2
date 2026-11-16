<template>
  <CustomDialog v-model="visible" title="Thanh toán gói cước" width="860px">
    <div v-if="giaoDich" class="thanh-toan">
      <section class="thanh-toan__goi" aria-label="Thông tin gói">
        <div>
          <span class="thanh-toan__loai">{{ loai.label }}</span>
          <h3 class="thanh-toan__ten">{{ giaoDich.ten_goi_cuoc }}</h3>
          <span class="thanh-toan__muted">Mã giao dịch: <strong>{{ giaoDich.ma_giao_dich }}</strong></span>
        </div>
        <dl class="thanh-toan__tom-tat">
          <div>
            <dt>Nhận được</dt>
            <dd>
              <s v-if="luotGoc !== null" class="thanh-toan__cu">{{ hienSo(luotGoc) }}</s>
              <strong>{{ hienSo(giaoDich.so_luot_nhan_duoc) }}</strong> {{ loai.donVi }}
            </dd>
          </div>
          <div>
            <dt>Thanh toán</dt>
            <dd>
              <s v-if="giaGoc !== null" class="thanh-toan__cu">{{ hienTien(giaGoc) }}</s>
              <strong class="thanh-toan__gia">{{ hienTien(giaoDich.so_tien_nap) }}</strong>
            </dd>
          </div>
        </dl>
      </section>

      <!-- Trái: danh sách ngân hàng; phải: mã QR và thông tin chuyển khoản. Khung hẹp thì xếp dọc. -->
      <div class="thanh-toan__than">
        <section class="thanh-toan__ngan-hang" aria-label="Chọn ngân hàng">
          <h4 class="thanh-toan__heading">Chọn ngân hàng thanh toán</h4>
          <p v-if="loiNganHang" class="thanh-toan__muted">{{ loiNganHang }}</p>
          <p v-else-if="dangTaiNganHang" class="thanh-toan__muted">Đang tải tài khoản nhận tiền…</p>
          <p v-else-if="!nganHang.length" class="thanh-toan__muted">
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
              @click="chonNganHang(item.id)"
            >
              <img
                v-if="item.logo_ngan_hang"
                class="bank-pick__logo"
                :src="apiAssetUrl(item.logo_ngan_hang)"
                :alt="item.ten_ngan_hang_viet_tat"
              />
              <span class="bank-pick__text">
                <strong>{{ item.ten_ngan_hang_viet_tat }}</strong>
                <span class="thanh-toan__muted">{{ item.so_tai_khoan }}</span>
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
              :alt="`Mã VietQR chuyển khoản ${hienTien(giaoDich.so_tien_nap)} tới ${nganHangChon.ten_ngan_hang_viet_tat}`"
              width="260"
              height="260"
              @error="loiQr = true"
            />
            <p v-else class="thanh-toan__qr-loi">
              Không tạo được mã QR cho ngân hàng này. Vui lòng chuyển khoản theo thông tin bên dưới.
            </p>
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

      <!-- <p class="thanh-toan__note">
        Ghi đúng nội dung chuyển khoản <strong>{{ giaoDich.noi_dung_chuyen_khoan }}</strong> để hệ thống tự nhận ra giao
        dịch. Edu coin hoặc lượt sẽ được cộng ngay khi ngân hàng báo nhận đủ tiền.
        <template v-if="giaoDich.thoi_gian_thanh_toan">
          Bạn đã báo chuyển khoản lúc {{ hienThoiGian(giaoDich.thoi_gian_thanh_toan) }}.
        </template>
      </p> -->
    </div>
    <template #footer>
      <CustomButton @click="visible = false">Đóng</CustomButton>
      <CustomButton
        v-if="giaoDich && !giaoDich.thoi_gian_thanh_toan"
        type="primary"
        :loading="dangBao"
        :disabled="!nganHangChon"
        @click="baoDaChuyenKhoan"
      >
        Tôi đã chuyển khoản
      </CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/**
 * Modal thanh toán một giao dịch nạp tiền đang chờ: chọn ngân hàng nhận tiền, hiện mã VietQR và thông tin chuyển
 * khoản. Đổi ngân hàng và "Tôi đã chuyển khoản" được lưu vào giao dịch (PATCH /tai-khoan/nap-tien/{id}).
 */
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { apiAssetUrl } from '@/api/apiUrl'
import { capNhatNapTien } from '@/api/napTien'
import { fetchNganHangNhanTien } from '@/api/nganHangThanhToan'
import { LOAI_AP_DUNG, hienSo, hienThoiGian, hienTien, timTheoGiaTri } from '@/data/napTien'

const visible = defineModel({ type: Boolean, default: false })

const props = defineProps({
  // Giao dịch nạp tiền (NapTienPublic).
  giaoDich: { type: Object, default: null },
  // Gói cước gốc (tùy chọn): có thì hiện giá/lượt gốc gạch ngang khi đang khuyến mãi.
  goi: { type: Object, default: null },
})
const emit = defineEmits(['updated'])

const nganHang = ref([])
const dangTaiNganHang = ref(false)
const loiNganHang = ref('')
const nganHangChonId = ref(null)
const loiQr = ref(false)
const dangBao = ref(false)

const loai = computed(() => {
  const item = timTheoGiaTri(LOAI_AP_DUNG, props.giaoDich?.loai_ap_dung)
  return { label: item.label, donVi: item.donVi || '' }
})
const giaGoc = computed(() => {
  const goc = props.goi?.gia_goc
  return goc !== undefined && goc !== null && Number(goc) !== Number(props.giaoDich?.so_tien_nap) ? goc : null
})
const luotGoc = computed(() => {
  const goc = props.goi?.so_luot_nhan_duoc_goc
  return goc !== undefined && goc !== null && Number(goc) !== Number(props.giaoDich?.so_luot_nhan_duoc) ? goc : null
})
const nganHangChon = computed(() => nganHang.value.find((item) => item.id === nganHangChonId.value) || null)

// Ảnh VietQR (img.vietqr.io): mã ngân hàng là tên viết tắt (VCB, MB, ICB, ...) hoặc mã BIN theo danh sách VietQR.
const qrUrl = computed(() => {
  const bank = nganHangChon.value
  const gd = props.giaoDich
  if (!bank || !gd) return ''
  const params = new URLSearchParams({
    amount: String(gd.so_tien_nap),
    addInfo: gd.noi_dung_chuyen_khoan || gd.ma_giao_dich,
    accountName: bank.chu_tai_khoan,
  })
  const ma = encodeURIComponent(bank.ten_ngan_hang_viet_tat)
  const stk = encodeURIComponent(bank.so_tai_khoan)
  return `https://img.vietqr.io/image/${ma}-${stk}-qr_only.png?${params}`
})

const thongTinChuyenKhoan = computed(() => {
  const bank = nganHangChon.value
  const gd = props.giaoDich
  if (!bank || !gd) return []
  const noiDung = gd.noi_dung_chuyen_khoan || gd.ma_giao_dich
  return [
    { nhan: 'Ngân hàng', hien: `${bank.ten_ngan_hang_viet_tat} - ${bank.ten_ngan_hang}` },
    { nhan: 'Số tài khoản', hien: bank.so_tai_khoan, saoChep: bank.so_tai_khoan, dam: true },
    { nhan: 'Chủ tài khoản', hien: bank.chu_tai_khoan },
    { nhan: 'Số tiền', hien: hienTien(gd.so_tien_nap), saoChep: String(gd.so_tien_nap), dam: true },
    { nhan: 'Nội dung', hien: noiDung, saoChep: noiDung, dam: true },
  ]
})

watch(qrUrl, () => {
  loiQr.value = false
})

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function taiNganHang() {
  if (nganHang.value.length) return
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

// Lưu ngân hàng đã chọn vào giao dịch để đối soát; lỗi thì vẫn cho xem QR.
async function chonNganHang(id) {
  nganHangChonId.value = id
  const gd = props.giaoDich
  if (!gd || gd.ngan_hang_thanh_toan_id === id) return
  try {
    const data = await capNhatNapTien(gd.id, { ngan_hang_thanh_toan_id: id }, { skipLoading: true })
    emit('updated', data)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được ngân hàng đã chọn'))
  }
}

async function baoDaChuyenKhoan() {
  const gd = props.giaoDich
  if (!gd) return
  dangBao.value = true
  try {
    const data = await capNhatNapTien(gd.id, { ngan_hang_thanh_toan_id: nganHangChonId.value, da_chuyen_khoan: true })
    emit('updated', data)
    ElMessage.success('Đã ghi nhận. Số dư sẽ được cộng ngay khi hệ thống nhận được tiền.')
    visible.value = false
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không ghi nhận được'))
  } finally {
    dangBao.value = false
  }
}

// Mở modal: tải ngân hàng, chọn sẵn ngân hàng đã lưu trong giao dịch (hoặc ngân hàng đầu tiên).
watch(
  () => [visible.value, props.giaoDich?.id],
  async ([open]) => {
    if (!open || !props.giaoDich) return
    await taiNganHang()
    const daLuu = props.giaoDich.ngan_hang_thanh_toan_id
    const id = nganHang.value.some((item) => item.id === daLuu) ? daLuu : nganHang.value[0]?.id ?? null
    if (id !== null) chonNganHang(id)
  },
  { immediate: true },
)
</script>

<style scoped>
/* 2 cột khi khung dialog đủ rộng (container query), hẹp thì xếp dọc. */
.thanh-toan {
  container-type: inline-size;
  display: grid;
  gap: 16px;
}

.thanh-toan__muted {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
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

.thanh-toan__cu {
  margin-right: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  font-weight: 400;
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

.bank-pick__logo {
  width: 56px;
  height: 36px;
  object-fit: contain;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  background: #fff;
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

.thanh-toan__note {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
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

/* Desktop: mã QR và thông tin chuyển khoản nằm cùng một hàng. */
@container (min-width: 760px) {
  .thanh-toan__chuyen-khoan {
    grid-template-columns: 200px minmax(0, 1fr);
    align-items: center;
  }

  .bank__row {
    grid-template-columns: 96px minmax(0, 1fr);
  }
}
</style>
