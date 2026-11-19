<template>
  <div class="thu-thap" :class="{ 'thu-thap--xem': phienId }">
    <!-- Trái: các phiên thu thập -->
    <aside class="thu-thap__ds">
      <CustomButton type="primary" class="thu-thap__moi" :loading="dangTao" @click="taoPhien">
        <CustomIcon class="el-icon--left"><Plus /></CustomIcon>
        Phiên thu thập mới
      </CustomButton>
      <CustomInput v-model="tuKhoa" clearable placeholder="Tìm tiêu đề, mã trường">
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <div v-loading="dangTaiDs && !dsPhien.length" class="thu-thap__cuon">
        <button
          v-for="p in dsPhien"
          :key="p.id"
          type="button"
          class="phien"
          :class="{ 'is-active': p.id === phienId }"
          @click="chonPhien(p.id)"
        >
          <strong class="phien__ten">{{ p.tieu_de }}</strong>
          <span class="phien__dong">
            <span>{{ [p.ma_truong, p.nam_tuyen_sinh].filter(Boolean).join(' · ') || 'Chưa rõ trường' }}</span>
            <CustomTag :type="nhanPhien(p).type" size="small" effect="plain">{{ nhanPhien(p).text }}</CustomTag>
          </span>
        </button>
        <CustomEmpty v-if="!dangTaiDs && !dsPhien.length" description="Chưa có phiên thu thập nào." :image-size="70" />
      </div>
    </aside>

    <!-- Giữa: hội thoại với AI -->
    <section class="thu-thap__chat">
      <template v-if="chiTiet">
        <header class="thu-thap__dau">
          <CustomButton class="thu-thap__lui" link aria-label="Quay lại danh sách" @click="chonPhien(null)">
            <CustomIcon><ArrowLeft /></CustomIcon>
          </CustomButton>
          <div class="thu-thap__tieu-de">
            <strong>{{ chiTiet.phien.tieu_de }}</strong>
            <span>{{ moTaPhien }}</span>
          </div>
          <CustomTooltip content="Đổi tên phiên">
            <CustomButton link aria-label="Đổi tên phiên" @click="doiTen">
              <CustomIcon><EditPen /></CustomIcon>
            </CustomButton>
          </CustomTooltip>
          <CustomTooltip content="Xóa phiên">
            <CustomButton link type="danger" aria-label="Xóa phiên" @click="xoaPhien">
              <CustomIcon><Delete /></CustomIcon>
            </CustomButton>
          </CustomTooltip>
        </header>

        <div ref="khungTin" v-loading="dangTaiChiTiet" class="thu-thap__tin">
          <div v-if="!chiTiet.tin_nhan.length && !dangGui" class="thu-thap__chao">
            <p>
              Hãy yêu cầu AI thu thập đề án, ví dụ: <em>"Thu thập đề án tuyển sinh 2026 của Đại học Bách khoa Hà Nội"</em>.
              Bạn có thể dán link đề án hoặc tải tệp PDF / Word / Excel lên để AI đọc; chưa có nguồn thì AI tự tìm trên web.
            </p>
          </div>
          <template v-for="tin in tinHienThi" :key="tin.id">
            <div v-if="tin.vai_tro === 'cong_cu'" class="buoc" :class="`buoc--${tin.trang_thai || 'xong'}`">
              <CustomIcon class="buoc__icon">
                <Loading v-if="tin.trang_thai === 'dang_chay'" class="is-loading" />
                <component :is="iconCongCu(tin.ten)" v-else />
              </CustomIcon>
              <span class="buoc__mo-ta">{{ tin.noi_dung }}</span>
              <small v-if="tin.ket_qua" class="buoc__ket-qua">{{ tin.ket_qua }}</small>
            </div>
            <div v-else class="tin" :class="tin.vai_tro === 'user' ? 'tin--phai' : 'tin--trai'">
              <div class="bong">
                <span v-if="tin.vai_tro === 'user'" class="bong__chu">{{ tin.noi_dung }}</span>
                <ChatMarkdown v-else :text="tin.noi_dung || ''" />
              </div>
            </div>
          </template>
          <div v-if="dangGui" class="tin tin--trai">
            <div class="bong"><DangSoanTraLoi /></div>
          </div>
        </div>

        <div class="thu-thap__soan">
          <div v-if="chiTiet.tep.length" class="thu-thap__tep">
            <CustomTag
              v-for="t in chiTiet.tep"
              :key="t.id"
              closable
              size="small"
              :disable-transitions="true"
              @close="xoaTep(t)"
            >
              {{ t.ten_tep }} · {{ hienSo(t.so_ky_tu) }} ký tự
            </CustomTag>
          </div>
          <form class="thu-thap__nhap" @submit.prevent="gui">
            <input ref="oTep" type="file" multiple hidden :accept="DUOI_TEP" @change="chonTep" />
            <CustomTooltip content="Tải tệp nguồn (PDF, Word, Excel, HTML, văn bản)">
              <CustomButton aria-label="Tải tệp nguồn" :loading="dangTaiTep" :disabled="dangGui" @click="oTep.click()">
                <CustomIcon><Paperclip /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <textarea
              :value="cauHoi"
              rows="2"
              maxlength="8000"
              aria-label="Yêu cầu cho AI"
              placeholder="Yêu cầu AI thu thập, dán link đề án, hoặc yêu cầu sửa bản nháp… (Enter để gửi)"
              :disabled="dangGui"
              @input="cauHoi = $event.target.value"
              @keydown="phimNhap"
            />
            <div class="thu-thap__nut">
              <CustomButton type="primary" native-type="submit" :disabled="dangGui || !cauHoi.trim()">Gửi</CustomButton>
              <CustomButton type="danger" plain :disabled="!dangGui" @click="dung">Dừng</CustomButton>
            </div>
          </form>
        </div>
      </template>
      <div v-else class="thu-thap__trong">
        <CustomIcon class="thu-thap__trong-icon"><ChatDotRound /></CustomIcon>
        <p>Chọn một phiên hoặc tạo phiên thu thập mới.</p>
      </div>
    </section>

    <!-- Phải: bản nháp -->
    <aside v-if="chiTiet" class="thu-thap__nhap-panel">
      <h3>Bản nháp đề án</h3>
      <CustomEmpty v-if="!chiTiet.ban_nhap" description="Chưa có bản nháp. Yêu cầu AI thu thập để tạo bản nháp." :image-size="60" />
      <template v-else>
        <dl class="tom-tat">
          <template v-for="dong in dongTomTat" :key="dong[0]">
            <dt>{{ dong[0] }}</dt>
            <dd>{{ dong[1] ?? '—' }}</dd>
          </template>
        </dl>
        <div v-if="chiTiet.kiem_tra" class="kiem-tra">
          <CustomTag v-if="chiTiet.kiem_tra.hop_le" type="success" effect="light">Hợp lệ — sẵn sàng nhập</CustomTag>
          <CustomTag v-else type="danger" effect="light">Có {{ chiTiet.kiem_tra.loi?.length || 0 }} lỗi</CustomTag>
          <ul v-if="chiTiet.kiem_tra.loi?.length" class="kiem-tra__loi">
            <li v-for="(loi, i) in chiTiet.kiem_tra.loi" :key="i">{{ loi }}</li>
          </ul>
          <ul v-if="chiTiet.kiem_tra.canh_bao?.length" class="kiem-tra__canh-bao">
            <li v-for="(cb, i) in chiTiet.kiem_tra.canh_bao" :key="i">{{ cb }}</li>
          </ul>
        </div>
        <el-alert
          v-if="chiTiet.phien.trang_thai === 'da_nhap'"
          type="success"
          :closable="false"
          show-icon
          :title="`Đã nhập thành đề án #${chiTiet.phien.de_an_id}`"
        />
        <div class="thu-thap__thao-tac">
          <CustomButton :loading="dangKiemTra" @click="kiemTra">Kiểm tra lại</CustomButton>
          <CustomButton @click="moSuaJson">Sửa JSON</CustomButton>
          <CustomButton @click="taiJson">Tải JSON</CustomButton>
          <CustomButton
            v-if="chiTiet.phien.trang_thai === 'da_nhap'"
            type="success"
            plain
            :disabled="!chiTiet.phien.de_an_id"
            @click="xemDeAn = true"
          >
            Xem đề án
          </CustomButton>
          <CustomButton
            v-else
            type="primary"
            :loading="dangNhap"
            :disabled="!chiTiet.kiem_tra?.hop_le"
            @click="nhap"
          >
            Nhập vào đề án
          </CustomButton>
        </div>
      </template>
    </aside>

    <CustomDialog v-model="moJson" title="Sửa bản nháp (JSON)" width="900px" destroy-on-close>
      <p class="json__goi-y">Theo file chuẩn import đầy đủ. Lưu xong hệ thống kiểm tra lại như lần nhập thật.</p>
      <textarea v-model="jsonSua" class="json__o" spellcheck="false" aria-label="Bản nháp JSON" />
      <p v-if="loiJson" class="json__loi">{{ loiJson }}</p>
      <template #footer>
        <CustomButton @click="moJson = false">Hủy</CustomButton>
        <CustomButton type="primary" :loading="dangLuuJson" @click="luuJson">Lưu và kiểm tra</CustomButton>
      </template>
    </CustomDialog>

    <ChiTietDeAnDialog v-if="chiTiet?.phien.de_an_id" v-model="xemDeAn" :de-an-id="chiTiet.phien.de_an_id" />
  </div>
</template>

<script setup>
/** Thu thập dữ liệu đề án bằng chatbot AI: phiên (trái), hội thoại có các bước AI gọi công cụ (giữa), bản nháp (phải). */
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Collection, Document, EditPen, Reading, Search } from '@element-plus/icons-vue'
import {
  createPhienThuThap,
  deletePhienThuThap,
  deleteTepThuThap,
  fetchChiTietPhienThuThap,
  fetchPhienThuThap,
  guiTinNhanThuThap,
  kiemTraBanNhapThuThap,
  luuBanNhapThuThap,
  nhapBanNhapThuThap,
  taiTepThuThap,
  updatePhienThuThap,
} from '@/api/thuThapDuLieu'
import ChatMarkdown from '@/components/guest/chung/ChatMarkdown.vue'
import DangSoanTraLoi from '@/components/guest/chung/DangSoanTraLoi.vue'
import ChiTietDeAnDialog from '@/views/admin/de-an-tuyen-sinh/ChiTietDeAnDialog.vue'
import { hienSo } from '@/data/napTien'

const DUOI_TEP = '.pdf,.docx,.xlsx,.html,.htm,.txt,.csv,.json,.md'
const ICON_CONG_CU = {
  tim_kiem_web: Search,
  doc_trang_web: Reading,
  doc_tep: Document,
  tra_danh_muc: Collection,
  luu_ban_nhap: EditPen,
  xem_ban_nhap: Document,
  xem_huong_dan: Reading,
}

const route = useRoute()
const router = useRouter()
const dsPhien = ref([])
const tuKhoa = ref('')
const dangTaiDs = ref(false)
const dangTao = ref(false)
const chiTiet = ref(null)
const dangTaiChiTiet = ref(false)
const cauHoi = ref('')
const dangGui = ref(false)
// Lượt đang chạy: câu vừa gửi và các bước công cụ nhận qua stream (hiện tạm tới khi tải lại từ server).
const cauDangGui = ref('')
const buocDangChay = ref([])
const khungTin = ref(null)
const oTep = ref(null)
const dangTaiTep = ref(false)
const dangKiemTra = ref(false)
const dangNhap = ref(false)
const moJson = ref(false)
const jsonSua = ref('')
const loiJson = ref('')
const dangLuuJson = ref(false)
const xemDeAn = ref(false)
let controller = null

const phienId = computed(() => (route.query.phien ? Number(route.query.phien) : null))

const moTaPhien = computed(() => {
  const p = chiTiet.value?.phien
  if (!p) return ''
  return [p.ma_truong && `Trường ${p.ma_truong}`, p.nam_tuyen_sinh && `năm ${p.nam_tuyen_sinh}`, nhanPhien(p).text]
    .filter(Boolean)
    .join(' · ')
})

const tinHienThi = computed(() => {
  const ds = (chiTiet.value?.tin_nhan || []).map((t) => ({
    id: t.id,
    vai_tro: t.vai_tro,
    noi_dung: t.noi_dung,
    ten: t.du_lieu?.ten,
    ket_qua: t.du_lieu?.ket_qua,
  }))
  if (!dangGui.value) return ds
  return [
    ...ds,
    { id: 'dang-gui', vai_tro: 'user', noi_dung: cauDangGui.value },
    ...buocDangChay.value.map((b, i) => ({ id: `buoc-${i}`, vai_tro: 'cong_cu', noi_dung: b.mo_ta, ten: b.ten,
      ket_qua: b.ket_qua, trang_thai: b.trang_thai })),
  ]
})

const dongTomTat = computed(() => {
  const t = chiTiet.value?.tom_tat || {}
  return [
    ['Trường', t.ma_truong],
    ['Năm tuyển sinh', t.nam_tuyen_sinh],
    ['Tên đề án', t.ten_de_an],
    ['Cơ sở', t.so_co_so],
    ['Chương trình', t.so_chuong_trinh],
    ['Phương thức', t.so_phuong_thuc],
    ['Điểm chuẩn', t.so_diem_chuan],
  ]
})

function loiApi(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function nhanPhien(p) {
  if (p.trang_thai === 'da_nhap') return { text: 'Đã nhập', type: 'success' }
  if (!p.co_ban_nhap) return { text: 'Chưa có bản nháp', type: 'info' }
  if (p.hop_le) return { text: 'Bản nháp hợp lệ', type: 'primary' }
  return { text: 'Bản nháp có lỗi', type: 'warning' }
}

function iconCongCu(ten) {
  return ICON_CONG_CU[ten] || Document
}

async function taiDanhSach() {
  dangTaiDs.value = true
  try {
    const params = { page: 1, page_size: 100 }
    if (tuKhoa.value.trim()) params.q = tuKhoa.value.trim()
    dsPhien.value = (await fetchPhienThuThap(params, { skipLoading: true })).items
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không tải được danh sách phiên'))
  } finally {
    dangTaiDs.value = false
  }
}

async function cuonXuong() {
  await nextTick()
  if (khungTin.value) khungTin.value.scrollTop = khungTin.value.scrollHeight
}

async function taiChiTiet() {
  if (!phienId.value) {
    chiTiet.value = null
    return
  }
  dangTaiChiTiet.value = !chiTiet.value || chiTiet.value.phien.id !== phienId.value
  try {
    chiTiet.value = await fetchChiTietPhienThuThap(phienId.value, { skipLoading: true })
    cuonXuong()
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không tải được phiên thu thập'))
    chiTiet.value = null
  } finally {
    dangTaiChiTiet.value = false
  }
}

// Phiên đang xem nằm trên URL (?phien=<id>) để tải lại trang vẫn mở đúng phiên.
function chonPhien(id) {
  if (dangGui.value) dung()
  router.replace({ query: { ...route.query, phien: id || undefined } })
}

async function taoPhien() {
  dangTao.value = true
  try {
    const phien = await createPhienThuThap({})
    await taiDanhSach()
    chonPhien(phien.id)
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không tạo được phiên'))
  } finally {
    dangTao.value = false
  }
}

async function doiTen() {
  let tieuDe
  try {
    ;({ value: tieuDe } = await ElMessageBox.prompt('Tiêu đề phiên', 'Đổi tên', {
      inputValue: chiTiet.value.phien.tieu_de,
      inputValidator: (v) => Boolean(String(v || '').trim()) || 'Vui lòng nhập tiêu đề.',
      confirmButtonText: 'Lưu',
      cancelButtonText: 'Hủy',
    }))
  } catch {
    return
  }
  try {
    await updatePhienThuThap(phienId.value, { tieu_de: tieuDe.trim() })
    await Promise.all([taiChiTiet(), taiDanhSach()])
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không đổi được tên phiên'))
  }
}

async function xoaPhien() {
  try {
    await ElMessageBox.confirm(
      `Xóa phiên "${chiTiet.value.phien.tieu_de}" cùng hội thoại, tệp và bản nháp? Đề án đã nhập không bị xóa.`,
      'Xác nhận xóa',
      { type: 'warning', confirmButtonText: 'Xóa', cancelButtonText: 'Hủy', confirmButtonClass: 'el-button--danger' },
    )
  } catch {
    return
  }
  try {
    await deletePhienThuThap(phienId.value)
    ElMessage.success('Đã xóa phiên')
    chonPhien(null)
    taiDanhSach()
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không xóa được phiên'))
  }
}

async function chonTep(event) {
  const files = [...(event.target.files || [])]
  event.target.value = ''
  if (!files.length) return
  dangTaiTep.value = true
  try {
    for (const file of files) {
      try {
        await taiTepThuThap(phienId.value, file)
      } catch (error) {
        ElMessage.error(`${file.name}: ${loiApi(error, 'Không đọc được tệp')}`)
      }
    }
    await taiChiTiet()
  } finally {
    dangTaiTep.value = false
  }
}

async function xoaTep(tep) {
  try {
    await deleteTepThuThap(phienId.value, tep.id)
    await taiChiTiet()
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không xóa được tệp'))
  }
}

function capNhatBuoc(data) {
  // Sự kiện "xong" / "loi" của cùng một bước thay cho dòng "dang_chay" trước đó.
  const ds = buocDangChay.value
  const i = ds.findLastIndex((b) => b.mo_ta === data.mo_ta && b.trang_thai === 'dang_chay')
  if (i >= 0 && data.trang_thai !== 'dang_chay') ds.splice(i, 1, data)
  else ds.push(data)
  cuonXuong()
}

async function gui() {
  const text = cauHoi.value.trim()
  if (!phienId.value || !text || dangGui.value) return
  dangGui.value = true
  cauDangGui.value = text
  buocDangChay.value = []
  cauHoi.value = ''
  cuonXuong()
  let loi = ''
  controller = new AbortController()
  try {
    await guiTinNhanThuThap(phienId.value, text, {
      signal: controller.signal,
      onEvent(event, data) {
        if (event === 'cong_cu') capNhatBuoc(data)
        else if (event === 'ban_nhap' && chiTiet.value) {
          chiTiet.value = { ...chiTiet.value, kiem_tra: data.kiem_tra, tom_tat: data.tom_tat || {}, ban_nhap: chiTiet.value.ban_nhap || {} }
        } else if (event === 'loi') loi = data.message
      },
    })
  } catch (error) {
    if (!controller.signal.aborted) loi = error.message || 'Không kết nối được AI.'
  } finally {
    dangGui.value = false
    controller = null
    await Promise.all([taiChiTiet(), taiDanhSach()])
    if (loi) {
      ElMessage.error(loi)
      if (!cauHoi.value) cauHoi.value = text
    }
  }
}

function dung() {
  controller?.abort()
}

function phimNhap(event) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    gui()
  }
}

async function kiemTra() {
  dangKiemTra.value = true
  try {
    const kq = await kiemTraBanNhapThuThap(phienId.value)
    chiTiet.value = { ...chiTiet.value, kiem_tra: kq.kiem_tra, tom_tat: kq.tom_tat }
    taiDanhSach()
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không kiểm tra được bản nháp'))
  } finally {
    dangKiemTra.value = false
  }
}

function moSuaJson() {
  jsonSua.value = JSON.stringify(chiTiet.value.ban_nhap, null, 2)
  loiJson.value = ''
  moJson.value = true
}

async function luuJson() {
  let duLieu
  try {
    duLieu = JSON.parse(jsonSua.value)
  } catch (error) {
    loiJson.value = `JSON không hợp lệ: ${error.message}`
    return
  }
  dangLuuJson.value = true
  try {
    await luuBanNhapThuThap(phienId.value, duLieu)
    moJson.value = false
    ElMessage.success('Đã lưu bản nháp')
    await Promise.all([taiChiTiet(), taiDanhSach()])
  } catch (error) {
    loiJson.value = loiApi(error, 'Không lưu được bản nháp')
  } finally {
    dangLuuJson.value = false
  }
}

function taiJson() {
  const p = chiTiet.value.phien
  const blob = new Blob([JSON.stringify(chiTiet.value.ban_nhap, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `ban_nhap_${p.ma_truong || 'de_an'}_${p.nam_tuyen_sinh || ''}.json`
  a.click()
  URL.revokeObjectURL(a.href)
}

async function nhap() {
  const t = chiTiet.value.tom_tat || {}
  try {
    await ElMessageBox.confirm(
      `Nhập bản nháp thành đề án ${t.ma_truong} năm ${t.nam_tuyen_sinh} (${t.so_chuong_trinh} chương trình)?`,
      'Nhập vào đề án',
      { type: 'warning', confirmButtonText: 'Nhập', cancelButtonText: 'Hủy' },
    )
  } catch {
    return
  }
  dangNhap.value = true
  try {
    const kq = await nhapBanNhapThuThap(phienId.value)
    ElMessage.success(`Đã nhập thành đề án #${kq.de_an_id}`)
    await Promise.all([taiChiTiet(), taiDanhSach()])
  } catch (error) {
    ElMessage.error(loiApi(error, 'Không nhập được bản nháp'))
  } finally {
    dangNhap.value = false
  }
}

let henTim = null
watch(tuKhoa, () => {
  clearTimeout(henTim)
  henTim = setTimeout(taiDanhSach, 300)
})
watch(phienId, () => {
  cauHoi.value = ''
  taiChiTiet()
})

onMounted(() => {
  taiDanhSach()
  taiChiTiet()
})
onBeforeUnmount(() => controller?.abort())
</script>

<style scoped>
.thu-thap {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 320px;
  height: calc(100vh - 270px);
  min-height: 560px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
}

.thu-thap__ds {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
  padding: 12px;
  border-right: 1px solid var(--el-border-color-lighter);
}

.thu-thap__moi {
  width: 100%;
}

.thu-thap__cuon {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.phien {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  margin-bottom: 4px;
  padding: 10px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--el-text-color-primary);
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.phien:hover {
  background: var(--el-fill-color-light);
}

.phien.is-active {
  background: var(--el-color-primary-light-9);
  box-shadow: inset 3px 0 0 var(--el-color-primary);
}

.phien__ten {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.phien__dong {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.thu-thap__chat {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}

.thu-thap__dau {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.thu-thap__lui {
  display: none;
}

.thu-thap__tieu-de {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.thu-thap__tieu-de strong,
.thu-thap__tieu-de span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.thu-thap__tieu-de span {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.thu-thap__tin {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
  background: var(--el-fill-color-light);
}

.thu-thap__chao {
  margin: auto;
  max-width: 520px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
  text-align: center;
}

.tin {
  display: flex;
}

.tin--phai {
  justify-content: flex-end;
}

.bong {
  max-width: min(85%, 760px);
  padding: 9px 14px;
  border-radius: 8px;
  background: var(--el-bg-color);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  line-height: 1.55;
  word-break: break-word;
}

.tin--trai .bong {
  max-width: 100%;
}

.tin--phai .bong {
  background: var(--el-color-primary);
  color: #fff;
}

.bong__chu {
  white-space: pre-wrap;
}

.bong :deep(p) {
  margin: 0 0 6px;
}

.bong :deep(p:last-child) {
  margin-bottom: 0;
}

/* Một bước AI gọi công cụ / tìm web */
.buoc {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.buoc__icon {
  flex: 0 0 auto;
  color: var(--el-color-primary);
}

.buoc--loi .buoc__icon,
.buoc--loi .buoc__ket-qua {
  color: var(--el-color-danger);
}

.buoc__mo-ta {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.buoc__ket-qua {
  flex: 0 0 auto;
  opacity: 0.85;
}

.thu-thap__soan {
  padding: 10px 16px 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.thu-thap__tep {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.thu-thap__nhap {
  display: flex;
  align-items: stretch;
  gap: 8px;
}

.thu-thap__nhap textarea {
  flex: 1;
  min-width: 0;
  padding: 8px 10px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  font: inherit;
  resize: none;
}

.thu-thap__nhap textarea:focus {
  outline: none;
  border-color: var(--el-color-primary);
}

.thu-thap__nut {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.thu-thap__nut :deep(.el-button + .el-button) {
  margin-left: 0;
}

.thu-thap__trong {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light);
}

.thu-thap__trong-icon {
  font-size: 40px;
}

/* Bản nháp */
.thu-thap__nhap-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  overflow-y: auto;
  padding: 14px;
  border-left: 1px solid var(--el-border-color-lighter);
}

.thu-thap__nhap-panel h3 {
  margin: 0;
  font-size: 15px;
}

.tom-tat {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 6px 12px;
  margin: 0;
  font-size: 13px;
}

.tom-tat dt {
  color: var(--el-text-color-secondary);
}

.tom-tat dd {
  margin: 0;
  word-break: break-word;
}

.kiem-tra__loi,
.kiem-tra__canh-bao {
  max-height: 220px;
  margin: 8px 0 0;
  overflow-y: auto;
  padding-left: 18px;
  font-size: 12px;
}

.kiem-tra__loi {
  color: var(--el-color-danger);
}

.kiem-tra__canh-bao {
  color: var(--el-color-warning-dark-2);
}

.thu-thap__thao-tac {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.thu-thap__thao-tac :deep(.el-button + .el-button) {
  margin-left: 0;
}

.json__goi-y {
  margin: 0 0 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.json__o {
  width: 100%;
  height: 60vh;
  padding: 10px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  resize: vertical;
}

.json__loi {
  margin: 8px 0 0;
  color: var(--el-color-danger);
}

/* Màn vừa: bản nháp xuống dưới hội thoại. */
@media (max-width: 1280px) {
  .thu-thap {
    grid-template-columns: 240px minmax(0, 1fr);
    grid-template-rows: minmax(0, 1fr) auto;
    height: auto;
  }

  .thu-thap__ds {
    grid-row: span 2;
    max-height: calc(100vh - 270px);
  }

  .thu-thap__chat {
    height: calc(100vh - 270px);
    min-height: 520px;
  }

  .thu-thap__nhap-panel {
    border-top: 1px solid var(--el-border-color-lighter);
    border-left: 0;
  }
}

/* Điện thoại: một cột; chọn phiên thì ẩn danh sách, có nút quay lại. */
@media (max-width: 767px) {
  .thu-thap {
    grid-template-columns: minmax(0, 1fr);
  }

  .thu-thap__ds {
    grid-row: auto;
    max-height: none;
    border-right: 0;
  }

  .thu-thap--xem .thu-thap__ds,
  .thu-thap:not(.thu-thap--xem) .thu-thap__chat,
  .thu-thap:not(.thu-thap--xem) .thu-thap__nhap-panel {
    display: none;
  }

  .thu-thap__lui {
    display: inline-flex;
  }

  .bong {
    max-width: 92%;
  }
}
</style>
