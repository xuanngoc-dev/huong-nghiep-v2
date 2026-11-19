<template>
  <div class="hoi-thoai" :class="{ 'hoi-thoai--xem': phienDangChon }">
    <!-- Trái: danh sách hội thoại của thành viên -->
    <aside class="hoi-thoai__ds">
      <div class="hoi-thoai__tim">
        <CustomButton type="primary" class="hoi-thoai__moi" @click="batDauMoi">
          <CustomIcon class="el-icon--left"><Plus /></CustomIcon>
          Cuộc hội thoại mới
        </CustomButton>
        <CustomInput v-model="tuKhoa" clearable placeholder="Tìm theo tiêu đề">
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomRadioGroup v-model="trangThai" size="small" class="hoi-thoai__loc">
          <CustomRadioButton value="">Tất cả</CustomRadioButton>
          <CustomRadioButton value="dang-hoat-dong">Đang hoạt động</CustomRadioButton>
          <CustomRadioButton value="da-ket-thuc">Đã kết thúc</CustomRadioButton>
        </CustomRadioGroup>
      </div>

      <h2 class="hoi-thoai__nhom">
        Hội thoại của bạn
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
          <span class="avatar" :class="{ 'avatar--ket-thuc': !dangHoatDong(phien) }">
            <CustomIcon><ChatDotRound /></CustomIcon>
          </span>
          <span class="phien__than">
            <span class="phien__dong">
              <strong class="phien__ten">{{ phien.tieu_de || 'Hội thoại không tiêu đề' }}</strong>
              <span class="phien__gio">{{ thoiGianTuongDoi(phien.tin_nhan_cuoi_luc || phien.created_at) }}</span>
            </span>
            <span class="phien__dong">
              <span class="phien__xem-truoc">{{ phien.tin_nhan_cuoi || 'Chưa có tin nhắn' }}</span>
              <CustomTag v-if="!dangHoatDong(phien)" type="info" effect="plain" size="small" class="phien__trang-thai">
                Đã kết thúc
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
            <span class="phien__menu" role="button" tabindex="0" aria-label="Thao tác với hội thoại" @click.stop>
              <CustomIcon><MoreFilled /></CustomIcon>
            </span>
          </CustomDropdown>
        </div>

        <CustomEmpty
          v-if="!dangTaiDs && !phienList.length"
          description="Bạn chưa có cuộc hội thoại nào với trợ lý."
          :image-size="80"
        />
        <div v-if="phienList.length < total" class="hoi-thoai__them">
          <CustomButton link type="primary" :loading="dangTaiDs" @click="taiThem">Tải thêm</CustomButton>
        </div>
      </div>
    </aside>

    <!-- Phải: nội dung hội thoại -->
    <section class="hoi-thoai__noi-dung">
      <template v-if="phienDangChon">
        <header class="hoi-thoai__dau" :class="{ 'hoi-thoai__dau--token': token }">
          <CustomButton class="hoi-thoai__lui" link aria-label="Quay lại danh sách" @click="boChon">
            <CustomIcon><ArrowLeft /></CustomIcon>
          </CustomButton>
          <span class="avatar avatar--bot">AI</span>
          <div v-if="phienDangChon.moi" class="hoi-thoai__nguoi">
            <strong class="hoi-thoai__ten">Cuộc hội thoại mới</strong>
            <span class="hoi-thoai__phu">Đặt câu hỏi đầu tiên để bắt đầu trò chuyện với trợ lý</span>
          </div>
          <div v-else class="hoi-thoai__nguoi">
            <!-- Sửa tiêu đề tại chỗ: Enter hoặc nút ✓ để lưu, Esc hoặc nút ✕ để hủy. -->
            <div v-if="dangSuaTieuDe" class="hoi-thoai__sua-tieu-de">
              <CustomInput
                ref="oTieuDe"
                v-model="tieuDeMoi"
                size="small"
                maxlength="255"
                placeholder="Tiêu đề cuộc hội thoại"
                aria-label="Tiêu đề cuộc hội thoại"
                @keydown.enter.prevent="(event) => luuTieuDe(event.target.value)"
                @keydown.esc.prevent="huySuaTieuDe"
              />
              <CustomTooltip content="Lưu tiêu đề">
                <CustomButton
                  size="small"
                  type="primary"
                  aria-label="Lưu tiêu đề"
                  :loading="dangLuuTieuDe"
                  @click="luuTieuDe()"
                >
                  <CustomIcon><Check /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Hủy">
                <CustomButton size="small" aria-label="Hủy sửa tiêu đề" @click="huySuaTieuDe">
                  <CustomIcon><Close /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
            <div v-else class="hoi-thoai__tieu-de-dong">
              <strong class="hoi-thoai__ten" title="Bấm đúp để sửa tiêu đề" @dblclick="batDauSuaTieuDe">
                {{ phienDangChon.tieu_de || 'Hội thoại không tiêu đề' }}
              </strong>
              <CustomTooltip content="Sửa tiêu đề">
                <CustomButton link class="hoi-thoai__nut-sua" aria-label="Sửa tiêu đề" @click="batDauSuaTieuDe">
                  <CustomIcon><EditPen /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
            <span class="hoi-thoai__phu">
              Bắt đầu {{ gioPhut(phienDangChon.created_at) }} · {{ phienDangChon.so_tin_nhan }} tin nhắn
            </span>
          </div>
          <div class="hoi-thoai__the">
            <CustomTag v-if="phienDangChon.moi" type="primary" effect="light" size="small">Mới</CustomTag>
            <CustomTag v-else :type="dangHoatDong(phienDangChon) ? 'success' : 'info'" effect="light" size="small">
              {{ dangHoatDong(phienDangChon) ? 'Đang hoạt động' : 'Đã kết thúc' }}
            </CustomTag>
          </div>
        </header>
        <!-- Thanh Token AI ngay dưới đầu khung, chạy hết bề ngang (thay đường viền dưới): % token khả dụng trên
             tổng token (khả dụng + đã dùng), số % ở giữa; bấm để nạp thêm. Hai lớp chữ chồng khít nhau: chữ tối
             trên nền, chữ trắng trên phần có màu (cắt theo %), nên chữ luôn đọc được. -->
        <CustomTooltip v-if="token" :content="moTaToken">
          <RouterLink
            :to="{ name: 'nap-tien', query: { loai: 'token' } }"
            class="hoi-thoai__token-thanh"
            role="progressbar"
            :aria-label="moTaToken"
            :aria-valuenow="phanTramToken"
            aria-valuemin="0"
            aria-valuemax="100"
          >
            <span class="hoi-thoai__token-chu">{{ nhanToken }}</span>
            <span
              class="hoi-thoai__token-mau"
              :style="{ background: mauToken, clipPath: `inset(0 ${100 - phanTramToken}% 0 0)` }"
              aria-hidden="true"
            >
              <span class="hoi-thoai__token-chu">{{ nhanToken }}</span>
            </span>
          </RouterLink>
        </CustomTooltip>

        <div ref="khungTinNhan" v-loading="dangTaiTinNhan" class="hoi-thoai__tin-nhan">
          <div
            v-for="nhom in nhomTinNhan"
            :key="nhom.key"
            class="nhom"
            :class="nhom.laNguoiDung ? 'nhom--phai' : 'nhom--trai'"
          >
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
                  <DangSoanTraLoi v-else-if="tin.dang_tra_loi" />
                  <p v-if="tin.trang_thai === 'loi'" class="bong__loi">
                    {{ tin.loi_hien_thi || 'Trợ lý không trả lời được câu hỏi này.' }}
                  </p>
                  <p v-if="tenNguon(tin)" class="bong__nguon">Nguồn: {{ tenNguon(tin) }}</p>
                </template>
              </div>
              <span class="nhom__gio">{{ gioPhut(nhom.tinNhan[nhom.tinNhan.length - 1].created_at) }}</span>
            </div>
          </div>
          <!-- Hội thoại mới chưa có tin nhắn: lời chào và câu hỏi gợi ý. -->
          <div v-if="phienDangChon.moi && !tinHienThi.length" class="hoi-thoai__chao">
            <span class="avatar avatar--lon avatar--bot"><CustomIcon><ChatDotRound /></CustomIcon></span>
            <p>{{ LOI_CHAO }}</p>
            <div class="hoi-thoai__goi-y">
              <CustomButton v-for="cau in CAU_HOI_GOI_Y" :key="cau" round @click="hoiGoiY(cau)">{{ cau }}</CustomButton>
            </div>
          </div>
          <CustomEmpty
            v-else-if="!dangTaiTinNhan && !tinHienThi.length"
            description="Cuộc hội thoại chưa có tin nhắn."
            :image-size="80"
          />
        </div>

        <p v-if="!dangHoatDong(phienDangChon)" class="hoi-thoai__da-ket-thuc">
          Cuộc hội thoại đã kết thúc, không thể hỏi tiếp.
          <CustomButton link type="primary" @click="batDauMoi">Bắt đầu cuộc hội thoại mới</CustomButton>
        </p>
        <form v-else class="hoi-thoai__soan" @submit.prevent="gui">
          <GoiYLenh :text="cauHoi" class="hoi-thoai__goi-y-lenh" @chon="chonLenh" />
          <CustomInput
            ref="oNhap"
            v-model="cauHoi"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 5 }"
            resize="none"
            maxlength="4000"
            :disabled="dangGuiTaiDay || dangTaiTinNhan"
            placeholder="Nhập câu hỏi… (Enter để gửi, Shift + Enter để xuống dòng, gõ / để xem lệnh)"
            aria-label="Nội dung câu hỏi"
            @keydown="phimNhap"
            @compositionupdate="(event) => (dangGoDo = event.target.value)"
            @compositionend="dangGoDo = ''"
          />
          <CustomButton v-if="dangGuiTaiDay" type="danger" plain @click="chat.stop()">Dừng</CustomButton>
          <CustomButton
            v-else
            type="primary"
            native-type="submit"
            :disabled="!coNoiDung || chat.state.sending || dangTaiTinNhan"
          >
            Gửi
            <CustomIcon class="el-icon--right"><Promotion /></CustomIcon>
          </CustomButton>
        </form>
      </template>

      <div v-else class="hoi-thoai__trong">
        <span class="avatar avatar--lon avatar--bot"><CustomIcon><ChatDotRound /></CustomIcon></span>
        <p>Chọn một cuộc hội thoại để xem nội dung.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
/** Thành viên: trái là các cuộc hội thoại của mình với trợ lý, phải là tin nhắn của cuộc đang chọn và ô hỏi tiếp. */
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  doiTieuDeHoiThoaiCuaToi,
  fetchChiTietHoiThoaiCuaToi,
  fetchHoiThoaiCuaToi,
  ketThucHoiThoaiCuaToi,
} from '@/api/hoiThoai'
import { useChatStore } from '@/stores/chat'
import { fetchHoSo } from '@/api/hoSo'
import { hienSo } from '@/data/napTien'
import ChatMarkdown from '@/components/guest/chung/ChatMarkdown.vue'
import DangSoanTraLoi from '@/components/guest/chung/DangSoanTraLoi.vue'
import GoiYLenh from '@/components/guest/chung/GoiYLenh.vue'
import { cuPhap, goiYLenh, phanTichLenh } from '@/utils/chatLenh'
import { WELCOME as LOI_CHAO } from '@/utils/chatSession'

const PAGE_SIZE = 30
const CAU_HOI_GOI_Y = [
  'Phương thức xét tuyển ngành Marketing trường NEU 2026?',
  'Bách khoa Hà Nội có những ngành nào?',
  'Những trường nào có ngành Công nghệ thông tin hoặc Logistics?',
]

const route = useRoute()
const router = useRouter()
const chat = useChatStore()
const tuKhoa = ref('')
const trangThai = ref('')
const phienList = ref([])
const total = ref(0)
const page = ref(1)
const dangTaiDs = ref(false)
const phienDangChon = ref(null)
const tinNhan = ref([])
const dangTaiTinNhan = ref(false)
const khungTinNhan = ref(null)
const cauHoi = ref('')
// Nội dung ô nhập khi bộ gõ tiếng Việt (Telex/VNI) đang gõ dở một chữ: el-input chỉ cập nhật v-model khi chốt chữ
// (nhấn phím cách), nên dùng thêm giá trị này để mở nút Gửi ngay khi ô có chữ.
const dangGoDo = ref('')
const coNoiDung = computed(() => Boolean(cauHoi.value.trim() || dangGoDo.value.trim()))
const oNhap = ref(null)
// Đang gửi câu hỏi từ trang này: khung phải hiện tin nhắn của chat store (có câu trả lời đang stream).
const dangGuiTaiDay = ref(false)
let lanTaiTinNhan = 0
let henFocus = false
const dangSuaTieuDe = ref(false)
// Số dư token AI của tài khoản: { con, da } — khả dụng / đã dùng; null khi chưa tải được.
const token = ref(null)
const dangLuuTieuDe = ref(false)
const tieuDeMoi = ref('')
const oTieuDe = ref(null)

const phanTramToken = computed(() => {
  const tong = (token.value?.con || 0) + (token.value?.da || 0)
  return tong ? Math.min(100, Math.round(((token.value.con || 0) / tong) * 100)) : 0
})

// Màu theo % còn lại: từ 90% trở lên xanh dương; 90% → 20% đổi dần (xanh dương → xanh lá → vàng → cam)
// theo sắc độ HSL; 10–20% cam; dưới 10% đỏ.
const MAU_XANH_DUONG = 217
const MAU_CAM = 30
const mauToken = computed(() => {
  const p = phanTramToken.value
  if (p < 10) return 'hsl(0, 78%, 50%)'
  if (p < 20) return `hsl(${MAU_CAM}, 92%, 48%)`
  const tiLe = Math.min(1, (p - 20) / (90 - 20))
  return `hsl(${Math.round(MAU_CAM + tiLe * (MAU_XANH_DUONG - MAU_CAM))}, 80%, 46%)`
})

const nhanToken = computed(() => {
  const { con = 0, da = 0 } = token.value || {}
  return con || da ? `Token AI còn ${phanTramToken.value}%` : 'Chưa có Token AI — bấm để nạp'
})

const moTaToken = computed(() => {
  if (!token.value) return ''
  const { con, da } = token.value
  if (!con && !da) return 'Bạn chưa có token AI. Bấm để nạp gói Token AI.'
  return `Còn ${hienSo(con)} / ${hienSo(con + da)} token (đã dùng ${hienSo(da)}). Bấm để nạp thêm.`
})

async function taiToken() {
  try {
    const hoSo = await fetchHoSo({ skipLoading: true })
    token.value = { con: hoSo.so_luong_token_kha_dung || 0, da: hoSo.so_luong_token_da_dung || 0 }
  } catch {
    // Không tải được thì giữ số cũ (hoặc ẩn thanh token).
  }
}

function loiApi(error, fallback) {
  const detail = error?.response?.data?.detail
  return typeof detail === 'string' ? detail : fallback
}

function dangHoatDong(phien) {
  return phien?.trang_thai === 'dang_hoat_dong'
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

// Tin nhắn của chat store → cùng dạng tin nhắn API để hiển thị chung.
function tuKhungChat(m) {
  if (m.role === 'user') {
    return { id: m.id, loai_nguoi_gui: 'user', noi_dung_tin_nhan: m.text, trang_thai: 'thanh_cong', created_at: m.at }
  }
  return {
    id: m.id,
    loai_nguoi_gui: 'bot',
    noi_dung_phan_hoi: m.text,
    nguon_tham_khao: m.sources,
    trang_thai: m.status === 'error' ? 'loi' : 'thanh_cong',
    loi_hien_thi: m.error,
    dang_tra_loi: m.status === 'streaming',
    created_at: m.at,
  }
}

// Lệnh "/..." và câu trả lời của lệnh: chỉ hiện trong trang, không lưu server; xóa khi đổi hội thoại hoặc gửi câu hỏi thật.
const tinCucBo = ref([])

const tinHienThi = computed(() => {
  if (dangGuiTaiDay.value && chat.state.maPhien === phienDangChon.value?.ma_dinh_danh) {
    return chat.state.messages.filter((m) => m.id !== 'welcome' && !m.local).map(tuKhungChat)
  }
  return [...tinNhan.value, ...tinCucBo.value]
})

// Gộp các tin liên tiếp của cùng một bên (bạn / trợ lý) thành một nhóm như khung chat.
const nhomTinNhan = computed(() => {
  const nhom = []
  for (const tin of tinHienThi.value) {
    const laNguoiDung = tin.loai_nguoi_gui === 'user'
    const cuoi = nhom[nhom.length - 1]
    if (cuoi && cuoi.laNguoiDung === laNguoiDung) cuoi.tinNhan.push(tin)
    else nhom.push({ key: tin.id, laNguoiDung, tinNhan: [tin] })
  }
  return nhom
})

async function taiDanhSach({ them = false } = {}) {
  dangTaiDs.value = true
  try {
    const params = { page: them ? page.value + 1 : 1, page_size: PAGE_SIZE }
    if (tuKhoa.value.trim()) params.q = tuKhoa.value.trim()
    if (trangThai.value) params.trang_thai = trangThai.value
    const data = await fetchHoiThoaiCuaToi(params, { skipLoading: true })
    phienList.value = them ? [...phienList.value, ...data.items] : data.items
    total.value = data.total
    page.value = data.page
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không tải được danh sách hội thoại'))
  } finally {
    dangTaiDs.value = false
  }
}

function taiThem() {
  taiDanhSach({ them: true })
}

// Mã hội thoại đang xem nằm trên URL (?phien=<ma_dinh_danh>) để tải lại trang vẫn mở đúng hội thoại.
// Trang này dùng chung cho 2 route: danh-sach-hoi-thoai và hoi-thoai-moi (mở sẵn một hội thoại mới).
function chonPhien(phien) {
  if (route.name === 'danh-sach-hoi-thoai' && route.query.phien === phien.ma_dinh_danh) return
  router.replace({ name: 'danh-sach-hoi-thoai', query: { ...route.query, phien: phien.ma_dinh_danh } })
}

function boChon() {
  router.replace({ name: 'danh-sach-hoi-thoai', query: { ...route.query, phien: undefined } })
}

function taoMaPhien() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID()
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.floor(Math.random() * 16)
    return (c === 'x' ? r : (r % 4) + 8).toString(16)
  })
}

// Hội thoại mới chỉ có mã (UUID) phía trình duyệt; server tạo phiên với đúng mã này khi nhận câu hỏi đầu tiên,
// nên vào trang mà không hỏi gì thì không sinh phiên rỗng.
function khoiTaoMoi() {
  lanTaiTinNhan++
  dangSuaTieuDe.value = false
  dangTaiTinNhan.value = false
  cauHoi.value = ''
  tinNhan.value = []
  tinCucBo.value = []
  phienDangChon.value = {
    id: null,
    moi: true,
    ma_dinh_danh: taoMaPhien(),
    tieu_de: null,
    trang_thai: 'dang_hoat_dong',
    so_tin_nhan: 0,
    created_at: new Date().toISOString(),
  }
  nextTick(() => oNhap.value?.focus())
}

function batDauMoi() {
  if (route.name === 'hoi-thoai-moi') khoiTaoMoi()
  else router.push({ name: 'hoi-thoai-moi' })
}

function dongBoTuUrl() {
  if (route.name === 'hoi-thoai-moi') {
    if (!phienDangChon.value?.moi) khoiTaoMoi()
    return
  }
  const ma = typeof route.query.phien === 'string' ? route.query.phien : ''
  // Hội thoại vừa tạo từ trang "mới" đã có sẵn dữ liệu, không tải lại.
  if (ma && ma === phienDangChon.value?.ma_dinh_danh && !phienDangChon.value.moi && tinNhan.value.length) return
  moPhien(ma)
}

async function moPhien(ma) {
  cauHoi.value = ''
  dangSuaTieuDe.value = false
  tinCucBo.value = []
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
    const data = await fetchChiTietHoiThoaiCuaToi(ma, { skipLoading: true })
    if (lan !== lanTaiTinNhan) return
    phienDangChon.value = data.phien
    tinNhan.value = data.tin_nhan
    await cuonXuong()
    if (henFocus) oNhap.value?.focus()
  } catch (error) {
    if (lan !== lanTaiTinNhan) return
    ElMessage.error(loiApi(error, 'Không tải được nội dung hội thoại'))
    phienDangChon.value = null
  } finally {
    if (lan === lanTaiTinNhan) {
      dangTaiTinNhan.value = false
      henFocus = false
    }
  }
}

async function cuonXuong() {
  await nextTick()
  if (khungTinNhan.value) khungTinNhan.value.scrollTop = khungTinNhan.value.scrollHeight
}

// Tải lại phiên sau khi gửi (tin nhắn đã lưu, số tin nhắn, trạng thái) và cập nhật dòng trong danh sách.
// Hội thoại mới: server vừa tạo phiên → thêm vào danh sách và chuyển URL sang hội thoại đó.
// Hội thoại vừa có tin nhắn mới lên đầu danh sách (như server: tin nhắn gần nhất trước). Chỉ chuyển dòng đang có
// trong danh sách, không tự thêm để giữ đúng bộ lọc đang chọn.
function lenDauDanhSach(phien) {
  if (!phienList.value.some((item) => item.id === phien.id)) return
  phienList.value = [phien, ...phienList.value.filter((item) => item.id !== phien.id)]
}

async function lamMoiPhien(ma, moi = false) {
  try {
    const data = await fetchChiTietHoiThoaiCuaToi(ma, { skipLoading: true })
    if (moi) taiDanhSach()
    else lenDauDanhSach(data.phien)
    if (phienDangChon.value?.ma_dinh_danh !== ma) return
    phienDangChon.value = data.phien
    tinNhan.value = data.tin_nhan
    if (moi) router.replace({ name: 'danh-sach-hoi-thoai', query: { phien: ma } })
  } catch (error) {
    if (!moi) {
      ElMessage.error(loiApi(error, 'Không tải lại được cuộc hội thoại'))
      return
    }
    // Server chưa lưu được phiên (vd. lỗi mạng): giữ nguyên những gì đã hiện để người dùng thấy lỗi và hỏi lại.
    if (phienDangChon.value?.ma_dinh_danh === ma) {
      tinNhan.value = chat.state.messages.filter((m) => m.id !== 'welcome').map(tuKhungChat)
    }
  }
}

// Gửi câu hỏi ngay trong trang: nạp hội thoại đang xem vào chat store (để gửi kèm lịch sử, nối tiếp đúng phiên)
// rồi gửi qua API chat stream; xong thì lấy lại tin nhắn đã lưu từ server.
async function gui() {
  const phien = phienDangChon.value
  const text = cauHoi.value.trim()
  if (!phien || !text || chat.state.sending || dangTaiTinNhan.value || !dangHoatDong(phien)) return
  if (phanTichLenh(text)) return chayLenh(text, phien)
  tinCucBo.value = []
  await chat.loadModels()
  chat.moHoiThoai(phien.ma_dinh_danh, tinNhan.value)
  // Đưa hội thoại lên đầu ngay khi gửi (xem trước là câu vừa hỏi); có câu trả lời thì lamMoiPhien cập nhật lại.
  const dong = phienList.value.find((item) => item.id === phien.id)
  if (dong) lenDauDanhSach({ ...dong, tin_nhan_cuoi: text, tin_nhan_cuoi_luc: new Date().toISOString() })
  dangGuiTaiDay.value = true
  cauHoi.value = ''
  cuonXuong()
  try {
    await chat.send(text)
    if (chat.state.hetToken) {
      // Hết token AI: câu hỏi chưa được lưu, trả lại ô nhập và mời nạp gói Token AI.
      cauHoi.value = text
      moiNapToken(chat.state.error)
    } else if (chat.state.error) {
      // Không gửi được (chưa có model, câu hỏi quá dài…): trả lại câu hỏi để sửa.
      ElMessage.error(chat.state.error)
      cauHoi.value = text
    }
    if (chat.state.daKetThuc) ElMessage.warning('Cuộc hội thoại đã kết thúc, không thể hỏi tiếp.')
    await lamMoiPhien(phien.ma_dinh_danh, phien.moi)
  } finally {
    dangGuiTaiDay.value = false
    cuonXuong()
    // Token được trừ sau mỗi lượt trả lời.
    taiToken()
  }
}

async function moiNapToken(thongBao) {
  try {
    await ElMessageBox.confirm(thongBao, 'Hết token AI', {
      type: 'warning',
      confirmButtonText: 'Nạp Token AI',
      cancelButtonText: 'Để sau',
    })
  } catch {
    return
  }
  router.push({ name: 'nap-tien', query: { loai: 'token' } })
}

function hoiGoiY(cau) {
  cauHoi.value = cau
  gui()
}

// Chạy lệnh "/..." (utils/chatLenh.js) trên hội thoại đang xem; câu trả lời hiện như tin nhắn của trợ lý.
async function chayLenh(text, phien) {
  cauHoi.value = ''
  const tinNhanThat = tinNhan.value.map((t) => ({
    role: t.loai_nguoi_gui === 'user' ? 'user' : 'bot',
    text: t.loai_nguoi_gui === 'user' ? t.noi_dung_tin_nhan : t.noi_dung_phan_hoi,
  }))
  const at = new Date().toISOString()
  const traLoi = await chat.chayLenh(text, {
    maPhien: phien.moi ? null : phien.ma_dinh_danh,
    tinNhan: tinNhanThat,
    moi: batDauMoi,
    thuLai() {
      const cuoi = [...tinNhanThat].reverse().find((t) => t.role === 'user')
      if (!cuoi) return 'Chưa có câu hỏi nào để hỏi lại.'
      cauHoi.value = cuoi.text
      gui()
    },
    sauKetThuc() {
      const daDong = { ...phien, trang_thai: 'da_dong' }
      if (phienDangChon.value?.id === phien.id) phienDangChon.value = daDong
      phienList.value = phienList.value.map((item) => (item.id === phien.id ? daDong : item))
    },
  })
  if (!traLoi || phienDangChon.value?.ma_dinh_danh !== phien.ma_dinh_danh) return
  const id = `lenh-${Date.now()}`
  tinCucBo.value.push(
    { id: `${id}-hoi`, loai_nguoi_gui: 'user', noi_dung_tin_nhan: text, trang_thai: 'thanh_cong', created_at: at },
    { id: `${id}-dap`, loai_nguoi_gui: 'bot', noi_dung_phan_hoi: traLoi, trang_thai: 'thanh_cong', created_at: at },
  )
  cuonXuong()
}

function chonLenh(lenh) {
  cauHoi.value = `/${lenh.ten}${lenh.thamSo ? ' ' : ''}`
  oNhap.value?.focus()
}

function phimNhap(event) {
  // Tab: điền lệnh đầu tiên đang được gợi ý.
  const goiY = goiYLenh(cauHoi.value)
  if (event.key === 'Tab' && goiY.length && cauHoi.value !== cuPhap(goiY[0]).split(' ')[0]) {
    event.preventDefault()
    chonLenh(goiY[0])
    return
  }
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    gui()
  }
}

// Menu "…" của từng hội thoại: rê chuột vào nút "…" hoặc chuột phải lên hội thoại để mở.
const menuMoId = ref(null)
const menuRefs = {}

function thaoTacPhien(phien) {
  const items = [{ command: 'xem', label: 'Xem hội thoại', icon: 'View' }]
  if (dangHoatDong(phien)) items.push({ command: 'hoi-tiep', label: 'Hỏi tiếp', icon: 'ChatLineRound', type: 'primary' })
  items.push({ command: 'doi-ten', label: 'Đổi tên', icon: 'EditPen' })
  if (dangHoatDong(phien)) {
    items.push({ command: 'ket-thuc', label: 'Kết thúc hội thoại', icon: 'CircleClose', type: 'warning', divided: true })
  }
  return items
}

function thucHien(viec, phien) {
  if (viec === 'doi-ten') return doiTenQuaHopThoai(phien)
  if (viec === 'ket-thuc') return ketThuc(phien)
  if (viec === 'hoi-tiep') {
    henFocus = true
    if (route.query.phien === phien.ma_dinh_danh) oNhap.value?.focus()
  }
  chonPhien(phien)
}

// Cập nhật phiên vừa sửa ở khung phải (nếu đang xem) và trong danh sách.
function capNhatPhien(data) {
  if (phienDangChon.value?.id === data.id) phienDangChon.value = data
  phienList.value = phienList.value.map((item) => (item.id === data.id ? data : item))
}

async function doiTieuDe(phien, tieuDe) {
  try {
    capNhatPhien(await doiTieuDeHoiThoaiCuaToi(phien.ma_dinh_danh, tieuDe))
    ElMessage.success('Đã đổi tiêu đề cuộc hội thoại')
    return true
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không đổi được tiêu đề cuộc hội thoại'))
    return false
  }
}

function batDauSuaTieuDe() {
  if (!phienDangChon.value || phienDangChon.value.moi) return
  tieuDeMoi.value = phienDangChon.value.tieu_de || ''
  dangSuaTieuDe.value = true
  nextTick(() => oTieuDe.value?.focus())
}

function huySuaTieuDe() {
  dangSuaTieuDe.value = false
}

// Lưu khi nhấn Enter hoặc bấm nút ✓. Enter truyền giá trị đang hiện trong ô (event.target.value): bộ gõ tiếng Việt
// (Telex/VNI) chưa chốt chữ đang gõ dở thì v-model vẫn là giá trị cũ, vd. "Hỏi đáp về NEU" bị lưu thành "Hỏi đáp về".
// Bấm nút ✓ thì ô mất focus trước nên bộ gõ đã chốt chữ, v-model đúng.
async function luuTieuDe(giaTri = tieuDeMoi.value) {
  const phien = phienDangChon.value
  if (!phien || phien.moi || !dangSuaTieuDe.value || dangLuuTieuDe.value) return
  const tieuDe = String(giaTri).trim()
  if (!tieuDe) {
    ElMessage.warning('Vui lòng nhập tiêu đề.')
    return
  }
  if (tieuDe === phien.tieu_de) {
    dangSuaTieuDe.value = false
    return
  }
  dangLuuTieuDe.value = true
  // Lỗi thì giữ ô sửa để sửa lại.
  if (await doiTieuDe(phien, tieuDe)) dangSuaTieuDe.value = false
  dangLuuTieuDe.value = false
}

async function doiTenQuaHopThoai(phien) {
  let tieuDe
  try {
    ;({ value: tieuDe } = await ElMessageBox.prompt('Tiêu đề mới của cuộc hội thoại', 'Đổi tên', {
      inputValue: phien.tieu_de || '',
      inputValidator: (value) => {
        const t = String(value || '').trim()
        if (!t) return 'Vui lòng nhập tiêu đề.'
        return t.length <= 255 || 'Tiêu đề tối đa 255 ký tự.'
      },
      confirmButtonText: 'Lưu',
      cancelButtonText: 'Hủy',
    }))
  } catch {
    return
  }
  if (tieuDe.trim() !== phien.tieu_de) await doiTieuDe(phien, tieuDe.trim())
}

async function ketThuc(phien) {
  try {
    await ElMessageBox.confirm(
      `Kết thúc cuộc hội thoại "${phien.tieu_de || 'không tiêu đề'}"? Sau khi kết thúc bạn không thể hỏi tiếp trong cuộc này.`,
      'Kết thúc hội thoại',
      { type: 'warning', confirmButtonText: 'Kết thúc', cancelButtonText: 'Hủy' },
    )
  } catch {
    return
  }
  try {
    capNhatPhien(await ketThucHoiThoaiCuaToi(phien.ma_dinh_danh))
    if (chat.state.maPhien === phien.ma_dinh_danh) chat.state.daKetThuc = true
    ElMessage.success('Đã kết thúc cuộc hội thoại')
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không kết thúc được cuộc hội thoại'))
  }
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
watch(trangThai, () => taiDanhSach())
watch(() => [route.name, route.query.phien], dongBoTuUrl)
// Câu trả lời đang stream: cuộn theo.
watch(() => [chat.state.messages.length, chat.state.messages.at(-1)?.text], () => {
  if (dangGuiTaiDay.value) cuonXuong()
})

onMounted(() => {
  document.addEventListener('pointerdown', dongMenuKhiBamNgoai, true)
  chat.loadModels()
  taiToken()
  taiDanhSach()
  dongBoTuUrl()
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

/* Danh sách hội thoại */
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

.hoi-thoai__moi {
  width: 100%;
}

.hoi-thoai__chao {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  max-width: 560px;
  margin: 40px auto 0;
  color: var(--el-text-color-regular);
  text-align: center;
}

.hoi-thoai__chao p {
  margin: 0;
  line-height: 1.6;
}

.hoi-thoai__goi-y {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.hoi-thoai__goi-y :deep(.el-button) {
  margin-left: 0;
  white-space: normal;
  height: auto;
  line-height: 1.4;
  text-align: left;
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
  border-radius: 8px;
  color: var(--el-text-color-primary);
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

/* Nút "…": hiện khi rê chuột / đang mở menu / hội thoại đang chọn; màn hình cảm ứng thì luôn hiện. */
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

.phien__trang-thai {
  flex: 0 0 auto;
}

.hoi-thoai__them {
  padding: 8px;
  text-align: center;
}

/* Avatar */
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

.avatar .el-icon {
  font-size: 18px;
}

.avatar--ket-thuc {
  background: var(--el-fill-color);
  color: var(--el-text-color-secondary);
}

.avatar--bot {
  background: var(--el-color-primary);
  color: #fff;
}

.avatar--lon {
  width: 64px;
  height: 64px;
}

.avatar--lon .el-icon {
  font-size: 28px;
}

.phien.is-active .avatar {
  box-shadow: 0 0 0 2px #fff;
}

/* Nội dung hội thoại */
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

/* Có thanh token: thanh (ngay dưới đầu khung) thay cho đường viền dưới. */
.hoi-thoai__dau--token {
  border-bottom-color: transparent;
}

/* Nền thanh = phần token đã dùng: sọc chéo đan xen 3 màu nhạt (chữ tối ở giữa vẫn đọc rõ). */
.hoi-thoai__token-thanh {
  position: relative;
  display: block;
  flex: 0 0 auto;
  height: 18px;
  overflow: hidden;
  background: repeating-linear-gradient(
    135deg,
    #e4e7ed 0 6px,
    #f4f4f5 6px 12px,
    #fde2e2 12px 18px,
    #f4f4f5 18px 24px
  );
  text-decoration: none;
}

.hoi-thoai__token-mau {
  position: absolute;
  inset: 0;
  transition:
    clip-path 0.4s ease,
    background-color 0.4s ease;
}

.hoi-thoai__token-chu {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-regular);
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
  white-space: nowrap;
}

.hoi-thoai__token-mau .hoi-thoai__token-chu {
  color: #fff;
}

.hoi-thoai__token-thanh:focus-visible {
  outline: 2px solid var(--el-color-primary);
  outline-offset: -2px;
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

.hoi-thoai__ten,
.hoi-thoai__phu {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hoi-thoai__phu {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.hoi-thoai__sua-tieu-de {
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 460px;
}

.hoi-thoai__sua-tieu-de :deep(.el-button + .el-button) {
  margin-left: 0;
}

.hoi-thoai__tieu-de-dong {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}

.hoi-thoai__ten {
  min-width: 0;
}

/* Nút sửa tiêu đề: hiện rõ khi rê chuột vào tiêu đề; màn hình cảm ứng thì luôn hiện. */
.hoi-thoai__nut-sua {
  flex: 0 0 auto;
  opacity: 0.45;
  transition: opacity 0.15s;
}

.hoi-thoai__tieu-de-dong:hover .hoi-thoai__nut-sua,
.hoi-thoai__nut-sua:focus-visible {
  opacity: 1;
}

@media (hover: none) {
  .hoi-thoai__nut-sua {
    opacity: 1;
  }
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

/* Trợ lý bên trái (không có avatar để tiết kiệm diện tích), câu hỏi của bạn bên phải. */
.nhom {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 18px;
}

.nhom--phai {
  justify-content: flex-end;
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

.nhom--trai .bong--loi {
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
  border: 1px solid var(--el-border-color);
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

.hoi-thoai__da-ket-thuc {
  margin: 0;
  padding: 12px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning-dark-2);
  font-size: 13px;
}

.hoi-thoai__soan {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.hoi-thoai__goi-y-lenh {
  right: 20px;
  left: 20px;
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

/* Điện thoại: một cột, chọn hội thoại thì chuyển sang xem nội dung và có nút quay lại. */
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
