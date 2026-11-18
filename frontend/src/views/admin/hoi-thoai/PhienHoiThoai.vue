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
        <CustomSelect v-model="trangThai" clearable placeholder="Tất cả trạng thái" size="small">
          <CustomOption v-for="(tt, ma) in TRANG_THAI" :key="ma" :label="tt.nhan" :value="ma" />
        </CustomSelect>
      </div>

      <h2 class="hoi-thoai__nhom">
        Phiên hội thoại
        <span class="hoi-thoai__dem">{{ total.toLocaleString('vi-VN') }}</span>
      </h2>

      <div v-loading="dangTaiDs && !phienList.length" class="hoi-thoai__cuon">
        <!-- div thay cho button: bên trong có nút "…" mở menu thao tác (button không lồng button được). -->
        <div
          v-for="phien in phienList"
          :key="phien.id"
          role="button"
          tabindex="0"
          class="phien"
          :class="{ 'is-active': phien.id === phienDangChon?.id, 'is-menu': phien.id === menuMoId }"
          @click="chonPhien(phien)"
          @keydown.enter.self.prevent="chonPhien(phien)"
          @keydown.space.self.prevent="chonPhien(phien)"
          @contextmenu.prevent="moMenu(phien)"
        >
          <span class="avatar" :class="{ 'avatar--khach': !phien.user_id }">{{ chuDau(phien) }}</span>
          <span class="phien__than">
            <span class="phien__dong">
              <strong class="phien__ten">{{ tenNguoi(phien) }}</strong>
              <span class="phien__gio">{{ thoiGianTuongDoi(phien.tin_nhan_cuoi_luc || phien.created_at) }}</span>
            </span>
            <span class="phien__dong">
              <span class="phien__xem-truoc">{{ phien.tin_nhan_cuoi || phien.tieu_de || 'Chưa có tin nhắn' }}</span>
              <CustomTag
                v-if="phien.trang_thai !== 'dang_hoat_dong'"
                :type="TRANG_THAI[phien.trang_thai]?.type || 'info'"
                effect="plain"
                size="small"
                class="phien__trang-thai"
              >
                {{ TRANG_THAI[phien.trang_thai]?.nhan || phien.trang_thai }}
              </CustomTag>
            </span>
          </span>
          <CustomDropdown
            :ref="(el) => ganMenu(phien.id, el)"
            trigger="hover"
            placement="bottom-end"
            popper-class="phien-menu"
            :items="thaoTacPhien(phien)"
            @command="(viec) => thucHien(viec, phien)"
            @visible-change="(hien) => doiHienMenu(phien.id, hien)"
          >
            <span class="phien__menu" role="button" tabindex="0" aria-label="Thao tác với phiên" @click.stop>
              <CustomIcon><MoreFilled /></CustomIcon>
            </span>
          </CustomDropdown>
        </div>

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
          <CustomButton class="hoi-thoai__lui" link aria-label="Quay lại danh sách" @click="boChon">
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
          <div class="hoi-thoai__thao-tac">
            <CustomTooltip v-if="dangHoatDong" content="Kết thúc: người dùng không hỏi tiếp được trong phiên này">
              <CustomButton size="small" type="warning" plain :loading="dangLam(phienDangChon, 'da_dong')" @click="doiTrangThai('da_dong')">
                <CustomIcon class="el-icon--left"><CircleClose /></CustomIcon>
                Kết thúc
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip v-else content="Mở lại: người dùng hỏi tiếp được trong phiên này">
              <CustomButton
                size="small"
                type="success"
                plain
                :loading="dangLam(phienDangChon, 'dang_hoat_dong')"
                @click="doiTrangThai('dang_hoat_dong')"
              >
                <CustomIcon class="el-icon--left"><RefreshRight /></CustomIcon>
                Mở lại
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip v-if="phienDangChon.trang_thai !== 'luu_tru'" content="Lưu trữ (cũng khóa hỏi đáp)">
              <CustomButton size="small" :loading="dangLam(phienDangChon, 'luu_tru')" @click="doiTrangThai('luu_tru')">
                <CustomIcon><FolderOpened /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip content="Xóa phiên và toàn bộ tin nhắn">
              <CustomButton size="small" type="danger" plain :loading="dangLam(phienDangChon, 'xoa')" @click="xoaPhien()">
                <CustomIcon><Delete /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
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

        <p v-if="!dangHoatDong" class="hoi-thoai__da-ket-thuc">
          {{ phienDangChon.trang_thai === 'luu_tru' ? 'Phiên đã lưu trữ' : 'Phiên đã kết thúc' }} — người dùng không thể hỏi
          tiếp trong phiên này.
        </p>
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  deletePhienHoiThoai,
  doiTrangThaiPhienHoiThoai,
  fetchChiTietPhienHoiThoai,
  fetchPhienHoiThoai,
} from '@/api/hoiThoai'
import ChatMarkdown from '@/components/guest/chung/ChatMarkdown.vue'

const PAGE_SIZE = 30
const TRANG_THAI = {
  dang_hoat_dong: { nhan: 'Đang hoạt động', type: 'success' },
  da_dong: { nhan: 'Đã kết thúc', type: 'info' },
  luu_tru: { nhan: 'Lưu trữ', type: 'warning' },
}

const route = useRoute()
const router = useRouter()
const tuKhoa = ref('')
const doiTuong = ref('')
const trangThai = ref('')
const phienList = ref([])
const total = ref(0)
const page = ref(1)
const dangTaiDs = ref(false)
const phienDangChon = ref(null)
const tinNhan = ref([])
const dangTaiTinNhan = ref(false)
const khungTinNhan = ref(null)
const dangXuLy = ref('')
let lanTaiTinNhan = 0

const dangHoatDong = computed(() => phienDangChon.value?.trang_thai === 'dang_hoat_dong')

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
    if (trangThai.value) params.trang_thai = trangThai.value
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

// Mã phiên đang xem nằm trên URL (?phien=<ma_dinh_danh>) để tải lại trang vẫn mở đúng phiên.
function chonPhien(phien) {
  if (route.query.phien === phien.ma_dinh_danh) return
  router.replace({ query: { ...route.query, phien: phien.ma_dinh_danh } })
}

function boChon() {
  router.replace({ query: { ...route.query, phien: undefined } })
}

async function moPhien(ma) {
  if (!ma) {
    phienDangChon.value = null
    tinNhan.value = []
    return
  }
  // Hiện ngay thông tin có sẵn trong danh sách trong lúc tải tin nhắn.
  phienDangChon.value = phienList.value.find((item) => item.ma_dinh_danh === ma) || phienDangChon.value
  tinNhan.value = []
  const lan = ++lanTaiTinNhan
  dangTaiTinNhan.value = true
  try {
    const data = await fetchChiTietPhienHoiThoai(ma, { skipLoading: true })
    if (lan !== lanTaiTinNhan) return
    phienDangChon.value = data.phien
    tinNhan.value = data.tin_nhan
    await nextTick()
    if (khungTinNhan.value) khungTinNhan.value.scrollTop = khungTinNhan.value.scrollHeight
  } catch (error) {
    if (lan !== lanTaiTinNhan) return
    ElMessage.error(loiApi(error, 'Không tải được nội dung phiên hội thoại'))
    phienDangChon.value = null
  } finally {
    if (lan === lanTaiTinNhan) dangTaiTinNhan.value = false
  }
}

// dangXuLy = "<id phiên>:<việc>" của thao tác đang chạy (một thao tác một lúc).
function dangLam(phien, viec) {
  return dangXuLy.value === `${phien?.id}:${viec}`
}

// Kết thúc / mở lại / lưu trữ một phiên (mặc định phiên đang xem); cập nhật luôn dòng tương ứng trong danh sách.
async function doiTrangThai(moi, phien = phienDangChon.value) {
  if (!phien || dangXuLy.value) return
  if (moi === 'da_dong') {
    try {
      await ElMessageBox.confirm(
        `Kết thúc phiên hội thoại của ${tenNguoi(phien)}? Người dùng sẽ không hỏi tiếp được trong phiên này.`,
        'Kết thúc hội thoại',
        { type: 'warning', confirmButtonText: 'Kết thúc', cancelButtonText: 'Hủy' },
      )
    } catch {
      return
    }
  }
  dangXuLy.value = `${phien.id}:${moi}`
  try {
    const data = await doiTrangThaiPhienHoiThoai(phien.ma_dinh_danh, moi)
    if (phienDangChon.value?.id === data.id) phienDangChon.value = data
    phienList.value = phienList.value.map((item) => (item.id === data.id ? data : item))
    ElMessage.success(
      { da_dong: 'Đã kết thúc phiên hội thoại', luu_tru: 'Đã lưu trữ phiên hội thoại' }[moi] || 'Đã mở lại phiên hội thoại',
    )
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không cập nhật được trạng thái phiên hội thoại'))
  } finally {
    dangXuLy.value = ''
  }
}

async function xoaPhien(phien = phienDangChon.value) {
  if (!phien || dangXuLy.value) return
  try {
    await ElMessageBox.confirm(
      `Xóa phiên hội thoại của ${tenNguoi(phien)} cùng ${phien.so_tin_nhan} tin nhắn? Không thể khôi phục.`,
      'Xác nhận xóa',
      { type: 'warning', confirmButtonText: 'Xóa', cancelButtonText: 'Hủy', confirmButtonClass: 'el-button--danger' },
    )
  } catch {
    return
  }
  dangXuLy.value = `${phien.id}:xoa`
  try {
    await deletePhienHoiThoai(phien.ma_dinh_danh)
    phienList.value = phienList.value.filter((item) => item.id !== phien.id)
    total.value = Math.max(0, total.value - 1)
    if (phienDangChon.value?.id === phien.id) boChon()
    ElMessage.success('Đã xóa phiên hội thoại')
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không xóa được phiên hội thoại'))
  } finally {
    dangXuLy.value = ''
  }
}

// Menu "…" của từng phiên trong danh sách: rê chuột vào nút "…" hoặc chuột phải lên phiên để mở.
const menuMoId = ref(null)
const menuRefs = {}

function thaoTacPhien(phien) {
  const items = [{ command: 'xem', label: 'Xem hội thoại', icon: 'View' }]
  if (phien.trang_thai === 'dang_hoat_dong') {
    items.push({ command: 'da_dong', label: 'Kết thúc hội thoại', icon: 'CircleClose', type: 'warning' })
  } else {
    items.push({ command: 'dang_hoat_dong', label: 'Mở lại hội thoại', icon: 'RefreshRight', type: 'success' })
  }
  if (phien.trang_thai !== 'luu_tru') items.push({ command: 'luu_tru', label: 'Lưu trữ', icon: 'FolderOpened' })
  items.push({ command: 'xoa', label: 'Xóa', icon: 'Delete', type: 'danger', divided: true })
  return items
}

function thucHien(viec, phien) {
  if (viec === 'xem') chonPhien(phien)
  else if (viec === 'xoa') xoaPhien(phien)
  else doiTrangThai(viec, phien)
}

function ganMenu(id, el) {
  if (el) menuRefs[id] = el
  else delete menuRefs[id]
}

function doiHienMenu(id, hien) {
  if (hien) menuMoId.value = id
  else if (menuMoId.value === id) menuMoId.value = null
}

function moMenu(phien) {
  if (menuMoId.value && menuMoId.value !== phien.id) menuRefs[menuMoId.value]?.handleClose()
  menuRefs[phien.id]?.handleOpen()
}

// Menu kiểu hover không tự đóng khi bấm ra ngoài (trường hợp mở bằng chuột phải) nên tự đóng ở đây.
function dongMenuKhiBamNgoai(event) {
  if (!menuMoId.value || event.target.closest?.('.phien-menu, .phien__menu')) return
  menuRefs[menuMoId.value]?.handleClose()
}

let henTim = null
watch(tuKhoa, () => {
  clearTimeout(henTim)
  henTim = setTimeout(() => taiDanhSach(), 300)
})
watch([doiTuong, trangThai], () => taiDanhSach())
watch(() => route.query.phien, (ma) => moPhien(typeof ma === 'string' ? ma : ''))

onMounted(() => {
  document.addEventListener('pointerdown', dongMenuKhiBamNgoai, true)
  taiDanhSach()
  if (typeof route.query.phien === 'string') moPhien(route.query.phien)
})

onBeforeUnmount(() => document.removeEventListener('pointerdown', dongMenuKhiBamNgoai, true))
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

.phien:hover,
.phien.is-menu {
  background: var(--el-fill-color-light);
}

.phien:focus-visible {
  outline: 2px solid var(--el-color-primary);
  outline-offset: -2px;
}

/* Nút "…": hiện khi rê chuột / đang mở menu / phiên đang chọn; màn hình cảm ứng thì luôn hiện. */
.phien__menu {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  color: inherit;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
}

.phien:hover .phien__menu,
.phien.is-menu .phien__menu,
.phien.is-active .phien__menu,
.phien__menu:focus-visible {
  opacity: 1;
}

.phien__menu:hover {
  background: rgba(0, 0, 0, 0.06);
}

.phien.is-active .phien__menu:hover {
  background: rgba(255, 255, 255, 0.2);
}

@media (hover: none) {
  .phien__menu {
    opacity: 1;
  }
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
  flex: 1;
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

.hoi-thoai__thao-tac {
  display: flex;
  flex: 0 0 auto;
  gap: 6px;
}

.hoi-thoai__thao-tac :deep(.el-button + .el-button) {
  margin-left: 0;
}

.phien__trang-thai {
  flex: 0 0 auto;
}

.hoi-thoai__da-ket-thuc {
  margin: 0;
  padding: 8px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning-dark-2);
  font-size: 13px;
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
