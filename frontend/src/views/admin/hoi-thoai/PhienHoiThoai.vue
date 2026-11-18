<template>
  <div class="hoi-thoai" :class="{ 'hoi-thoai--xem': phienDangChon }">
    <!-- Trái: danh sách phiên -->
    <aside class="hoi-thoai__ds">
      <div class="hoi-thoai__tim">
        <CustomInput v-model="tuKhoa" clearable placeholder="Tìm theo tiêu đề, tên, email, mã">
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomRadioGroup v-model="doiTuong" size="small" class="hoi-thoai__loc">
          <CustomRadioButton value="">Tất cả</CustomRadioButton>
          <CustomRadioButton value="thanh-vien">Thành viên</CustomRadioButton>
          <CustomRadioButton value="khach">Khách</CustomRadioButton>
        </CustomRadioGroup>
      </div>

      <h2 class="hoi-thoai__nhom">
        Phiên hội thoại
        <span class="hoi-thoai__dem">{{ total.toLocaleString('vi-VN') }}</span>
      </h2>

      <div v-loading="dangTaiDs && !phienList.length" class="hoi-thoai__cuon">
        <button
          v-for="phien in phienList"
          :key="phien.id"
          type="button"
          class="phien"
          :class="{ 'is-active': phien.id === phienDangChon?.id }"
          @click="chonPhien(phien)"
        >
          <span class="avatar" :class="{ 'avatar--khach': !phien.user_id }">{{ chuDau(phien) }}</span>
          <span class="phien__than">
            <span class="phien__dong">
              <strong class="phien__ten">{{ tenNguoi(phien) }}</strong>
              <span class="phien__gio">{{ thoiGianTuongDoi(phien.tin_nhan_cuoi_luc || phien.created_at) }}</span>
            </span>
            <span class="phien__xem-truoc">{{ phien.tin_nhan_cuoi || phien.tieu_de || 'Chưa có tin nhắn' }}</span>
          </span>
        </button>

        <CustomEmpty v-if="!dangTaiDs && !phienList.length" description="Chưa có phiên hội thoại nào." :image-size="80" />
        <div v-if="phienList.length < total" class="hoi-thoai__them">
          <CustomButton link type="primary" :loading="dangTaiDs" @click="taiThem">Tải thêm</CustomButton>
        </div>
      </div>
    </aside>

    <!-- Phải: nội dung phiên -->
    <section class="hoi-thoai__noi-dung">
      <template v-if="phienDangChon">
        <header class="hoi-thoai__dau">
          <CustomButton class="hoi-thoai__lui" link aria-label="Quay lại danh sách" @click="phienDangChon = null">
            <CustomIcon><ArrowLeft /></CustomIcon>
          </CustomButton>
          <span class="avatar" :class="{ 'avatar--khach': !phienDangChon.user_id }">{{ chuDau(phienDangChon) }}</span>
          <div class="hoi-thoai__nguoi">
            <strong>{{ tenNguoi(phienDangChon) }}</strong>
            <span>{{ phuDe(phienDangChon) }}</span>
          </div>
          <div class="hoi-thoai__the">
            <CustomTag :type="TRANG_THAI[phienDangChon.trang_thai]?.type || 'info'" effect="light" size="small">
              {{ TRANG_THAI[phienDangChon.trang_thai]?.nhan || phienDangChon.trang_thai }}
            </CustomTag>
            <CustomTag type="info" effect="plain" size="small">{{ phienDangChon.so_tin_nhan }} tin nhắn</CustomTag>
          </div>
        </header>

        <div ref="khungTinNhan" v-loading="dangTaiTinNhan" class="hoi-thoai__tin-nhan">
          <p v-if="phienDangChon.tieu_de" class="hoi-thoai__tieu-de">{{ phienDangChon.tieu_de }}</p>
          <div
            v-for="nhom in nhomTinNhan"
            :key="nhom.key"
            class="nhom"
            :class="nhom.laNguoiDung ? 'nhom--trai' : 'nhom--phai'"
          >
            <span v-if="nhom.laNguoiDung" class="avatar avatar--nho" :class="{ 'avatar--khach': !phienDangChon.user_id }">
              {{ chuDau(phienDangChon) }}
            </span>
            <span v-else class="avatar avatar--nho avatar--bot">AI</span>
            <div class="nhom__than">
              <div
                v-for="tin in nhom.tinNhan"
                :key="tin.id"
                class="bong"
                :class="{ 'bong--loi': tin.trang_thai === 'loi' }"
              >
                <span v-if="nhom.laNguoiDung" class="bong__chu">{{ tin.noi_dung_tin_nhan }}</span>
                <template v-else>
                  <ChatMarkdown v-if="tin.noi_dung_phan_hoi" :text="tin.noi_dung_phan_hoi" />
                  <p v-if="tin.trang_thai === 'loi'" class="bong__loi">Lỗi: {{ tin.loi_chi_tiet || 'Không trả lời được' }}</p>
                  <p v-if="tenNguon(tin)" class="bong__nguon">Nguồn: {{ tenNguon(tin) }}</p>
                </template>
              </div>
              <span class="nhom__gio">{{ moTaNhom(nhom) }}</span>
            </div>
          </div>
          <CustomEmpty
            v-if="!dangTaiTinNhan && !tinNhan.length"
            description="Phiên này chưa có tin nhắn."
            :image-size="80"
          />
        </div>

        <footer class="hoi-thoai__soan">
          <CustomInput disabled placeholder="Trợ lý đang trả lời tự động. Trả lời trực tiếp từ quản trị sẽ bổ sung sau." />
          <CustomButton type="primary" disabled>
            Gửi
            <CustomIcon class="el-icon--right"><Promotion /></CustomIcon>
          </CustomButton>
        </footer>
      </template>

      <div v-else class="hoi-thoai__trong">
        <span class="avatar avatar--lon avatar--bot"><CustomIcon><ChatDotRound /></CustomIcon></span>
        <p>Chọn một phiên hội thoại để xem nội dung.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
/** Phiên hội thoại với trợ lý: trái là danh sách phiên (chat_conversations), phải là tin nhắn của phiên đang chọn. */
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchChiTietPhienHoiThoai, fetchPhienHoiThoai } from '@/api/hoiThoai'
import ChatMarkdown from '@/components/guest/chung/ChatMarkdown.vue'

const PAGE_SIZE = 30
const TRANG_THAI = {
  dang_hoat_dong: { nhan: 'Đang hoạt động', type: 'success' },
  da_dong: { nhan: 'Đã đóng', type: 'info' },
  luu_tru: { nhan: 'Lưu trữ', type: 'warning' },
}

const tuKhoa = ref('')
const doiTuong = ref('')
const phienList = ref([])
const total = ref(0)
const page = ref(1)
const dangTaiDs = ref(false)
const phienDangChon = ref(null)
const tinNhan = ref([])
const dangTaiTinNhan = ref(false)
const khungTinNhan = ref(null)
let lanTaiTinNhan = 0

function loiApi(error, fallback) {
  const detail = error?.response?.data?.detail
  return typeof detail === 'string' ? detail : fallback
}

function tenNguoi(phien) {
  return phien.user_id ? phien.ho_ten || `Thành viên #${phien.user_id}` : 'Khách vãng lai'
}

function chuDau(phien) {
  if (!phien.user_id) return 'K'
  const tu = String(phien.ho_ten || '').trim().split(/\s+/).filter(Boolean)
  return (tu.length > 1 ? tu[0][0] + tu[tu.length - 1][0] : tu[0]?.[0] || '?').toUpperCase()
}

function phuDe(phien) {
  const phan = phien.user_id ? [phien.email] : [phien.ma_khach_vang_lai && `Mã khách ${phien.ma_khach_vang_lai.slice(0, 8)}`]
  return [...phan, phien.model_ai].filter(Boolean).join(' · ')
}

function thoiGianTuongDoi(value) {
  if (!value) return ''
  const giay = (Date.now() - new Date(value).getTime()) / 1000
  if (giay < 60) return 'Vừa xong'
  if (giay < 3600) return `${Math.floor(giay / 60)} phút`
  if (giay < 86400) return `${Math.floor(giay / 3600)} giờ`
  if (giay < 7 * 86400) return `${Math.floor(giay / 86400)} ngày`
  return new Date(value).toLocaleDateString('vi-VN')
}

function gioPhut(value) {
  return value ? new Date(value).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : ''
}

function tenNguon(tin) {
  const ds = Array.isArray(tin.nguon_tham_khao) ? tin.nguon_tham_khao : []
  return ds
    .map((item) => item?.ten)
    .filter(Boolean)
    .slice(0, 3)
    .join(', ')
}

// Gộp các tin liên tiếp của cùng một bên (người dùng / trợ lý) thành một nhóm như khung chat.
const nhomTinNhan = computed(() => {
  const nhom = []
  for (const tin of tinNhan.value) {
    const laNguoiDung = tin.loai_nguoi_gui === 'user'
    const cuoi = nhom[nhom.length - 1]
    if (cuoi && cuoi.laNguoiDung === laNguoiDung) cuoi.tinNhan.push(tin)
    else nhom.push({ key: tin.id, laNguoiDung, tinNhan: [tin] })
  }
  return nhom
})

function moTaNhom(nhom) {
  const cuoi = nhom.tinNhan[nhom.tinNhan.length - 1]
  if (nhom.laNguoiDung) return gioPhut(cuoi.created_at)
  const token = (cuoi.so_token_vao || 0) + (cuoi.so_token_ra || 0)
  return [
    gioPhut(cuoi.created_at),
    cuoi.model_ai,
    cuoi.thoi_gian_phan_hoi_ms != null && `${(cuoi.thoi_gian_phan_hoi_ms / 1000).toFixed(1)}s`,
    token && `${token.toLocaleString('vi-VN')} token`,
  ]
    .filter(Boolean)
    .join(' · ')
}

async function taiDanhSach({ them = false } = {}) {
  dangTaiDs.value = true
  try {
    const params = { page: them ? page.value + 1 : 1, page_size: PAGE_SIZE }
    if (tuKhoa.value.trim()) params.q = tuKhoa.value.trim()
    if (doiTuong.value) params.doi_tuong = doiTuong.value
    const data = await fetchPhienHoiThoai(params, { skipLoading: true })
    phienList.value = them ? [...phienList.value, ...data.items] : data.items
    total.value = data.total
    page.value = data.page
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không tải được danh sách phiên hội thoại'))
  } finally {
    dangTaiDs.value = false
  }
}

function taiThem() {
  taiDanhSach({ them: true })
}

async function chonPhien(phien) {
  phienDangChon.value = phien
  tinNhan.value = []
  const lan = ++lanTaiTinNhan
  dangTaiTinNhan.value = true
  try {
    const data = await fetchChiTietPhienHoiThoai(phien.id, { skipLoading: true })
    if (lan !== lanTaiTinNhan) return
    phienDangChon.value = data.phien
    tinNhan.value = data.tin_nhan
    await nextTick()
    if (khungTinNhan.value) khungTinNhan.value.scrollTop = khungTinNhan.value.scrollHeight
  } catch (error) {
    if (lan === lanTaiTinNhan) ElMessage.error(loiApi(error, 'Không tải được nội dung phiên hội thoại'))
  } finally {
    if (lan === lanTaiTinNhan) dangTaiTinNhan.value = false
  }
}

let henTim = null
watch(tuKhoa, () => {
  clearTimeout(henTim)
  henTim = setTimeout(() => taiDanhSach(), 300)
})
watch(doiTuong, () => taiDanhSach())

onMounted(() => taiDanhSach())
</script>

<style scoped>
.hoi-thoai {
  --ht-cao: calc(100vh - 150px);
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  height: var(--ht-cao);
  min-height: 520px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
}

/* Danh sách phiên */
.hoi-thoai__ds {
  display: flex;
  flex-direction: column;
  min-height: 0;
  border-right: 1px solid var(--el-border-color-lighter);
}

.hoi-thoai__tim {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.hoi-thoai__loc {
  display: flex;
}

.hoi-thoai__loc :deep(.el-radio-button) {
  flex: 1;
}

.hoi-thoai__loc :deep(.el-radio-button__inner) {
  width: 100%;
}

.hoi-thoai__nhom {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px 20px 8px;
  color: var(--el-color-primary);
  font-size: 1rem;
  font-weight: 600;
}

.hoi-thoai__dem {
  padding: 0 8px;
  border-radius: 999px;
  background: var(--el-color-primary-light-9);
  font-size: 12px;
  font-weight: 500;
}

.hoi-thoai__cuon {
  flex: 1;
  min-height: 120px;
  overflow-y: auto;
  padding: 0 10px 12px;
}

.phien {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  margin-bottom: 4px;
  padding: 10px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--el-text-color-primary);
  text-align: left;
  cursor: pointer;
}

.phien:hover {
  background: var(--el-fill-color-light);
}

.phien.is-active {
  background: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(var(--el-color-primary-rgb), 0.35);
  color: #fff;
}

.phien__than {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.phien__dong {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.phien__ten {
  overflow: hidden;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.phien__gio {
  flex: 0 0 auto;
  font-size: 12px;
  opacity: 0.75;
}

.phien__xem-truoc {
  overflow: hidden;
  font-size: 13px;
  opacity: 0.8;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hoi-thoai__them {
  padding: 8px;
  text-align: center;
}

/* Avatar chữ cái */
.avatar {
  display: inline-grid;
  flex: 0 0 auto;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 50%;
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  font-size: 14px;
  font-weight: 600;
}

.avatar--khach {
  background: var(--el-color-success-light-8);
  color: var(--el-color-success-dark-2);
}

.avatar--bot {
  background: var(--el-color-primary);
  color: #fff;
}

.avatar--nho {
  width: 32px;
  height: 32px;
  font-size: 12px;
}

.avatar--lon {
  width: 64px;
  height: 64px;
  font-size: 28px;
}

.phien.is-active .avatar {
  box-shadow: 0 0 0 2px #fff;
}

/* Nội dung phiên */
.hoi-thoai__noi-dung {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}

.hoi-thoai__dau {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.hoi-thoai__lui {
  display: none;
}

.hoi-thoai__nguoi {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.hoi-thoai__nguoi span {
  overflow: hidden;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hoi-thoai__the {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: flex-end;
}

.hoi-thoai__tin-nhan {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 20px;
  background: var(--el-fill-color-light);
}

.hoi-thoai__tieu-de {
  margin: 0 auto 16px;
  max-width: 80%;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  text-align: center;
}

.nhom {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 18px;
}

.nhom--phai {
  flex-direction: row-reverse;
}

.nhom__than {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: min(72%, 680px);
}

.nhom--phai .nhom__than {
  align-items: flex-end;
}

.bong {
  padding: 9px 14px;
  border-radius: 8px;
  background: var(--el-bg-color);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  color: var(--el-text-color-primary);
  line-height: 1.55;
  word-break: break-word;
}

.bong__chu {
  white-space: pre-wrap;
}

.nhom--phai .bong {
  background: var(--el-color-primary);
  color: #fff;
}

.nhom--phai .bong--loi {
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}

.bong :deep(p) {
  margin: 0 0 6px;
}

.bong :deep(p:last-child),
.bong :deep(ul:last-child),
.bong :deep(ol:last-child) {
  margin-bottom: 0;
}

.bong :deep(ul),
.bong :deep(ol) {
  margin: 0 0 6px;
  padding-left: 20px;
}

.bong :deep(table) {
  margin: 6px 0;
  border-collapse: collapse;
  font-size: 13px;
}

.bong :deep(th),
.bong :deep(td) {
  padding: 4px 8px;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.bong :deep(a) {
  color: inherit;
  text-decoration: underline;
}

.bong__loi {
  margin: 6px 0 0;
  font-weight: 500;
}

.bong__nguon {
  margin: 6px 0 0;
  font-size: 12px;
  opacity: 0.85;
}

.nhom__gio {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.hoi-thoai__soan {
  display: flex;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.hoi-thoai__trong {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
}

/* Điện thoại: một cột, chọn phiên thì chuyển sang xem nội dung và có nút quay lại. */
@media (max-width: 767px) {
  .hoi-thoai {
    grid-template-columns: minmax(0, 1fr);
  }

  .hoi-thoai__noi-dung {
    display: none;
  }

  .hoi-thoai--xem .hoi-thoai__ds {
    display: none;
  }

  .hoi-thoai--xem .hoi-thoai__noi-dung {
    display: flex;
  }

  .hoi-thoai__lui {
    display: inline-flex;
  }

  .nhom__than {
    max-width: 85%;
  }

  .hoi-thoai__the {
    display: none;
  }
}
</style>
