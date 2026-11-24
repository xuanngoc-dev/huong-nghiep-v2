<template>
  <div class="soan-thao" :class="{ 'is-html': cheDoHtml }">
    <div class="soan-thao__cong-cu" role="toolbar" aria-label="Định dạng nội dung">
      <template v-if="!cheDoHtml">
        <div class="soan-thao__nhom">
          <CustomTooltip content="Hoàn tác (Ctrl+Z)" placement="top">
            <button type="button" aria-label="Hoàn tác" :disabled="!editor?.can().undo()" @click="lenh((c) => c.undo())">
              <CustomIcon><RefreshLeft /></CustomIcon>
            </button>
          </CustomTooltip>
          <CustomTooltip content="Làm lại (Ctrl+Y)" placement="top">
            <button type="button" aria-label="Làm lại" :disabled="!editor?.can().redo()" @click="lenh((c) => c.redo())">
              <CustomIcon><RefreshRight /></CustomIcon>
            </button>
          </CustomTooltip>
        </div>

        <div class="soan-thao__nhom">
          <CustomSelect
            class="soan-thao__kieu-khoi"
            :model-value="kieuKhoi"
            size="small"
            placeholder="Chọn kiểu đoạn"
            aria-label="Kiểu đoạn"
            @update:model-value="doiKieuKhoi"
          >
            <CustomOption v-for="k in KIEU_KHOI" :key="k.value" :label="k.label" :value="k.value" />
          </CustomSelect>
        </div>

        <div class="soan-thao__nhom">
          <CustomTooltip v-for="d in DINH_DANG" :key="d.ten" :content="d.nhan" placement="top">
            <button
              type="button"
              :aria-label="d.nhan"
              :aria-pressed="!!editor?.isActive(d.ten)"
              :class="{ 'is-active': editor?.isActive(d.ten) }"
              @click="lenh(d.lenh)"
            >
              <span :class="`soan-thao__chu soan-thao__chu--${d.ten}`">{{ d.ky_hieu }}</span>
            </button>
          </CustomTooltip>
        </div>

        <div class="soan-thao__nhom">
          <CustomTooltip v-for="d in KHOI" :key="d.ten" :content="d.nhan" placement="top">
            <button
              type="button"
              :aria-label="d.nhan"
              :aria-pressed="!!editor?.isActive(d.ten)"
              :class="{ 'is-active': editor?.isActive(d.ten) }"
              @click="lenh(d.lenh)"
            >
              <svg viewBox="0 0 16 16" aria-hidden="true"><path :d="d.hinh" /></svg>
            </button>
          </CustomTooltip>
        </div>

        <div class="soan-thao__nhom">
          <CustomTooltip v-for="d in CAN_LE" :key="d.gia_tri" :content="d.nhan" placement="top">
            <button
              type="button"
              :aria-label="d.nhan"
              :aria-pressed="!!editor?.isActive({ textAlign: d.gia_tri })"
              :class="{ 'is-active': editor?.isActive({ textAlign: d.gia_tri }) }"
              @click="lenh((c) => c.setTextAlign(d.gia_tri))"
            >
              <svg viewBox="0 0 16 16" aria-hidden="true"><path :d="d.hinh" /></svg>
            </button>
          </CustomTooltip>
        </div>

        <div class="soan-thao__nhom">
          <CustomTooltip content="Chèn / sửa liên kết" placement="top">
            <button
              type="button"
              aria-label="Chèn / sửa liên kết"
              :class="{ 'is-active': editor?.isActive('link') }"
              @click="suaLienKet"
            >
              <CustomIcon><Link /></CustomIcon>
            </button>
          </CustomTooltip>
          <CustomDropdown trigger="click" :items="menuAnh" @command="xuLyAnh">
            <button type="button" class="soan-thao__menu" aria-label="Ảnh" :disabled="dangTaiAnh">
              <CustomIcon v-if="!dangTaiAnh"><Picture /></CustomIcon>
              <CustomIcon v-else class="is-loading"><Loading /></CustomIcon>
              <span>Ảnh</span>
              <span v-if="soAnhNgoai" class="soan-thao__dem" :title="`${soAnhNgoai} ảnh từ trang khác`">{{ soAnhNgoai }}</span>
            </button>
          </CustomDropdown>
          <CustomDropdown trigger="click" :items="menuBang" @command="xuLyBang">
            <button type="button" class="soan-thao__menu" aria-label="Bảng">
              <CustomIcon><Grid /></CustomIcon>
              <span>Bảng</span>
            </button>
          </CustomDropdown>
        </div>

        <div class="soan-thao__nhom">
          <CustomTooltip content="Xóa định dạng" placement="top">
            <button
              type="button"
              aria-label="Xóa định dạng"
              @click="lenh((c) => c.unsetAllMarks().clearNodes())"
            >
              <CustomIcon><Brush /></CustomIcon>
            </button>
          </CustomTooltip>
        </div>
      </template>
      <span v-else class="soan-thao__goi-y">Đang sửa mã HTML. Bấm “Trình soạn thảo” để quay lại.</span>

      <CustomTooltip :content="cheDoHtml ? 'Quay lại trình soạn thảo' : 'Sửa mã HTML'" placement="top">
        <button
          type="button"
          class="soan-thao__menu soan-thao__doi-che-do"
          :aria-label="cheDoHtml ? 'Quay lại trình soạn thảo' : 'Sửa mã HTML'"
          :aria-pressed="cheDoHtml"
          :class="{ 'is-active': cheDoHtml }"
          @click="cheDoHtml = !cheDoHtml"
        >
          <span class="soan-thao__chu">&lt;/&gt;</span>
          <span>{{ cheDoHtml ? 'Trình soạn thảo' : 'HTML' }}</span>
        </button>
      </CustomTooltip>
    </div>

    <EditorContent v-show="!cheDoHtml" :editor="editor" class="soan-thao__noi-dung" />
    <CustomInput
      v-if="cheDoHtml"
      class="soan-thao__html"
      :model-value="model"
      type="textarea"
      :rows="16"
      placeholder="Nhập mã HTML"
      @update:model-value="model = $event"
    />

    <input ref="tepAnh" type="file" :accept="LOAI_ANH.join(',')" multiple hidden @change="onChonTep" />
  </div>
</template>

<script setup>
/**
 * SoanThaoNoiDung — trình soạn thảo nội dung HTML bằng Tiptap (khu quản trị).
 * - Dán nội dung sao chép từ trang web khác: giữ tiêu đề, đoạn, danh sách, trích dẫn, liên kết, ảnh, bảng, căn lề;
 *   bỏ style/script và thẻ lạ (chuanHoaHtmlDan + schema của Tiptap).
 * - Dán / kéo thả tệp ảnh: tải lên Thư viện (thư mục `thuMuc`) rồi chèn.
 * - Ảnh dán từ trang khác vẫn trỏ về trang đó; menu Ảnh → "Lưu ảnh ngoài về Thư viện" để tải về hệ thống.
 * - v-model là HTML; ảnh Thư viện lưu đường dẫn tương đối (xem anhTuongDoi / anhTuyetDoi).
 */
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { Image } from '@tiptap/extension-image'
import { TableKit } from '@tiptap/extension-table'
import { TextAlign } from '@tiptap/extension-text-align'
import { Placeholder } from '@tiptap/extensions'
import { Brush, Grid, Link, Loading, Picture, RefreshLeft, RefreshRight } from '@element-plus/icons-vue'
import { apiAssetUrl, apiOrigin } from '@/api/apiUrl'
import { importThuVienUrlTaoThuMuc, uploadThuVienTaoThuMuc } from '@/api/thuVien'
import { anhTuongDoi, anhTuyetDoi } from '@/utils/anhNoiDung'
import { chuanHoaHtmlDan, htmlHoacRong, laAnhNgoai } from './noiDungHtml'

defineOptions({ name: 'SoanThaoNoiDung' })

const props = defineProps({
  // Thư mục trong Thư viện để lưu ảnh tải lên / ảnh lưu về từ trang khác.
  thuMuc: { type: String, required: true },
  placeholder: { type: String, default: 'Nhập nội dung hoặc dán nội dung sao chép từ trang khác…' },
  toiDaMb: { type: Number, default: 5 },
})
const model = defineModel({ type: String, default: '' })

const LOAI_ANH = ['image/png', 'image/jpeg', 'image/webp', 'image/gif']
const GOC = apiOrigin()

const KIEU_KHOI = [
  { value: 'p', label: 'Đoạn văn' },
  { value: 2, label: 'Tiêu đề 2' },
  { value: 3, label: 'Tiêu đề 3' },
  { value: 4, label: 'Tiêu đề 4' },
]
const DINH_DANG = [
  { ten: 'bold', nhan: 'Đậm (Ctrl+B)', ky_hieu: 'B', lenh: (c) => c.toggleBold() },
  { ten: 'italic', nhan: 'Nghiêng (Ctrl+I)', ky_hieu: 'I', lenh: (c) => c.toggleItalic() },
  { ten: 'underline', nhan: 'Gạch chân (Ctrl+U)', ky_hieu: 'U', lenh: (c) => c.toggleUnderline() },
  { ten: 'strike', nhan: 'Gạch ngang', ky_hieu: 'S', lenh: (c) => c.toggleStrike() },
]
// Biểu tượng SVG 16×16 (nét) cho các nút không có icon tương ứng trong Element Plus.
const KHOI = [
  {
    ten: 'bulletList',
    nhan: 'Danh sách chấm',
    lenh: (c) => c.toggleBulletList(),
    hinh: 'M6 4h8M6 8h8M6 12h8M2.5 4h.01M2.5 8h.01M2.5 12h.01',
  },
  {
    ten: 'orderedList',
    nhan: 'Danh sách số',
    lenh: (c) => c.toggleOrderedList(),
    hinh: 'M6 4h8M6 8h8M6 12h8M2 3l1-.5V6M2 9.5h1.5L2 11.5h1.5',
  },
  {
    ten: 'blockquote',
    nhan: 'Trích dẫn',
    lenh: (c) => c.toggleBlockquote(),
    hinh: 'M3 4v8M6 5h7M6 8h7M6 11h5',
  },
  {
    ten: 'horizontalRule',
    nhan: 'Đường kẻ ngang',
    lenh: (c) => c.setHorizontalRule(),
    hinh: 'M2 8h12',
  },
]
const CAN_LE = [
  { gia_tri: 'left', nhan: 'Căn trái', hinh: 'M2 3h12M2 6.5h8M2 10h12M2 13.5h8' },
  { gia_tri: 'center', nhan: 'Căn giữa', hinh: 'M2 3h12M4 6.5h8M2 10h12M4 13.5h8' },
  { gia_tri: 'right', nhan: 'Căn phải', hinh: 'M2 3h12M6 6.5h8M2 10h12M6 13.5h8' },
  { gia_tri: 'justify', nhan: 'Căn đều', hinh: 'M2 3h12M2 6.5h12M2 10h12M2 13.5h12' },
]

const cheDoHtml = ref(false)
const dangTaiAnh = ref(false)
const soAnhNgoai = ref(0)
const tepAnh = ref(null)
// HTML (dạng lưu) vừa phát ra từ trình soạn thảo: model đổi từ ngoài (mở bài khác, sửa mã HTML) mới nạp lại.
let htmlDaPhat = model.value

function laTepAnh(file) {
  return LOAI_ANH.includes(file.type)
}

function demAnhNgoai(ed) {
  let so = 0
  ed.state.doc.descendants((node) => {
    if (node.type.name === 'image' && laAnhNgoai(node.attrs.src, GOC)) so += 1
  })
  soAnhNgoai.value = so
}

const editor = useEditor({
  content: anhTuyetDoi(htmlDaPhat, GOC),
  extensions: [
    StarterKit.configure({
      heading: { levels: [2, 3, 4] },
      link: {
        openOnClick: false,
        autolink: true,
        defaultProtocol: 'https',
        HTMLAttributes: { rel: 'noopener noreferrer nofollow', target: '_blank' },
      },
    }),
    Image.configure({ inline: false, allowBase64: false }),
    TableKit.configure({ table: { resizable: false } }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Placeholder.configure({ placeholder: props.placeholder }),
  ],
  editorProps: {
    transformPastedHTML: chuanHoaHtmlDan,
    // Dán ảnh chụp màn hình / tệp ảnh (không kèm HTML): tải lên Thư viện rồi chèn tại con trỏ.
    handlePaste(_view, event) {
      const data = event.clipboardData
      const files = [...(data?.files || [])].filter(laTepAnh)
      if (!files.length || data.getData('text/html')) return false
      taiVaChenAnh(files)
      return true
    },
    // Kéo thả tệp ảnh từ máy vào khung soạn thảo.
    handleDrop(view, event, _slice, moved) {
      const files = [...(event.dataTransfer?.files || [])].filter(laTepAnh)
      if (moved || !files.length) return false
      const toaDo = view.posAtCoords({ left: event.clientX, top: event.clientY })
      taiVaChenAnh(files, toaDo?.pos)
      return true
    },
  },
  // useEditor tạo editor ở onMounted (và tự hủy khi unmount): model đổi trước lúc đó thì nạp lại ở đây.
  onCreate: ({ editor: ed }) => {
    if (model.value !== htmlDaPhat) {
      htmlDaPhat = model.value
      ed.commands.setContent(anhTuyetDoi(model.value, GOC), { emitUpdate: false })
    }
    demAnhNgoai(ed)
  },
  onUpdate: ({ editor: ed }) => {
    demAnhNgoai(ed)
    htmlDaPhat = anhTuongDoi(htmlHoacRong(ed.getHTML()), GOC)
    model.value = htmlDaPhat
  },
})

watch(model, (value) => {
  if (!editor.value || value === htmlDaPhat) return
  htmlDaPhat = value
  editor.value.commands.setContent(anhTuyetDoi(value, GOC), { emitUpdate: false })
  demAnhNgoai(editor.value)
})

function lenh(goi) {
  if (!editor.value) return
  goi(editor.value.chain().focus()).run()
}

const kieuKhoi = ref('p')
watch(
  () => editor.value && KIEU_KHOI.find((k) => k.value !== 'p' && editor.value.isActive('heading', { level: k.value })),
  (k) => {
    kieuKhoi.value = k ? k.value : 'p'
  },
)

function doiKieuKhoi(value) {
  lenh((c) => (value === 'p' ? c.setParagraph() : c.setHeading({ level: value })))
}

async function suaLienKet() {
  if (!editor.value) return
  const cu = editor.value.getAttributes('link').href || ''
  let url
  try {
    ;({ value: url } = await ElMessageBox.prompt('Địa chỉ liên kết (để trống để bỏ liên kết)', 'Liên kết', {
      inputValue: cu,
      inputPlaceholder: 'https://…',
      confirmButtonText: 'Áp dụng',
      cancelButtonText: 'Hủy',
    }))
  } catch {
    return
  }
  const href = String(url || '').trim()
  if (!href) {
    lenh((c) => c.extendMarkRange('link').unsetLink())
    return
  }
  lenh((c) => c.extendMarkRange('link').setLink({ href: /^(https?:|mailto:|tel:|\/|#)/i.test(href) ? href : `https://${href}` }))
}

const menuAnh = ref([])
watch(
  soAnhNgoai,
  (so) => {
    menuAnh.value = [
      { command: 'tai-len', label: 'Tải ảnh từ máy lên' },
      { command: 'url', label: 'Chèn ảnh từ URL' },
      {
        command: 'luu-ngoai',
        label: so ? `Lưu ${so} ảnh từ trang khác về Thư viện` : 'Không có ảnh từ trang khác',
        disabled: !so,
        divided: true,
      },
    ]
  },
  { immediate: true },
)

const menuBang = [
  { command: 'chen', label: 'Chèn bảng 3 × 3' },
  { command: 'them-hang', label: 'Thêm hàng bên dưới', divided: true },
  { command: 'them-cot', label: 'Thêm cột bên phải' },
  { command: 'xoa-hang', label: 'Xóa hàng', divided: true },
  { command: 'xoa-cot', label: 'Xóa cột' },
  { command: 'xoa-bang', label: 'Xóa bảng' },
]

function xuLyBang(viec) {
  const lenhBang = {
    chen: (c) => c.insertTable({ rows: 3, cols: 3, withHeaderRow: true }),
    'them-hang': (c) => c.addRowAfter(),
    'them-cot': (c) => c.addColumnAfter(),
    'xoa-hang': (c) => c.deleteRow(),
    'xoa-cot': (c) => c.deleteColumn(),
    'xoa-bang': (c) => c.deleteTable(),
  }[viec]
  if (viec !== 'chen' && !editor.value?.isActive('table')) {
    ElMessage.info('Đặt con trỏ trong bảng trước khi sửa bảng')
    return
  }
  if (lenhBang) lenh(lenhBang)
}

async function xuLyAnh(viec) {
  if (viec === 'tai-len') tepAnh.value?.click()
  else if (viec === 'url') await chenAnhUrl()
  else if (viec === 'luu-ngoai') await luuAnhNgoai()
}

async function chenAnhUrl() {
  let url
  try {
    ;({ value: url } = await ElMessageBox.prompt('Địa chỉ ảnh', 'Chèn ảnh từ URL', {
      inputPlaceholder: 'https://…/anh.jpg',
      inputPattern: /^https?:\/\/\S+$/i,
      inputErrorMessage: 'URL ảnh phải bắt đầu bằng http:// hoặc https://',
      confirmButtonText: 'Chèn',
      cancelButtonText: 'Hủy',
    }))
  } catch {
    return
  }
  lenh((c) => c.setImage({ src: url.trim() }))
}

function onChonTep(event) {
  const files = [...(event.target.files || [])]
  event.target.value = ''
  if (files.length) taiVaChenAnh(files)
}

async function taiVaChenAnh(files, viTri) {
  const hopLe = files.filter((file) => {
    if (!laTepAnh(file)) {
      ElMessage.error(`"${file.name}": chỉ nhận ảnh PNG, JPG, WEBP hoặc GIF`)
      return false
    }
    if (file.size > props.toiDaMb * 1024 * 1024) {
      ElMessage.error(`"${file.name}": ảnh tối đa ${props.toiDaMb}MB`)
      return false
    }
    return true
  })
  if (!hopLe.length || !editor.value) return
  dangTaiAnh.value = true
  try {
    for (const file of hopLe) {
      const item = await uploadThuVienTaoThuMuc(file, props.thuMuc)
      const node = { type: 'image', attrs: { src: apiAssetUrl(item.duong_dan), alt: file.name.replace(/\.[^.]+$/, '') } }
      const chain = editor.value.chain().focus()
      ;(viTri != null ? chain.insertContentAt(viTri, node) : chain.insertContent(node)).run()
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Không tải được ảnh lên')
  } finally {
    dangTaiAnh.value = false
  }
}

/** Tải từng ảnh ngoài về Thư viện (server tải theo URL) rồi thay src trong nội dung; ảnh lỗi giữ nguyên. */
async function luuAnhNgoai() {
  if (!editor.value) return
  const dsUrl = new Set()
  editor.value.state.doc.descendants((node) => {
    if (node.type.name === 'image' && laAnhNgoai(node.attrs.src, GOC)) dsUrl.add(node.attrs.src)
  })
  if (!dsUrl.size) return

  dangTaiAnh.value = true
  const urlMoi = new Map()
  let soLoi = 0
  for (const url of dsUrl) {
    try {
      const item = await importThuVienUrlTaoThuMuc(url, props.thuMuc)
      urlMoi.set(url, apiAssetUrl(item.duong_dan))
    } catch {
      soLoi += 1
    }
  }
  dangTaiAnh.value = false
  if (!editor.value) return

  // Vị trí node có thể đổi nếu người dùng gõ tiếp trong lúc chờ: duyệt lại tài liệu hiện tại.
  const { tr } = editor.value.state
  editor.value.state.doc.descendants((node, pos) => {
    if (node.type.name === 'image' && urlMoi.has(node.attrs.src)) {
      tr.setNodeMarkup(pos, undefined, { ...node.attrs, src: urlMoi.get(node.attrs.src) })
    }
  })
  if (urlMoi.size) editor.value.view.dispatch(tr)

  if (soLoi) ElMessage.warning(`Đã lưu ${urlMoi.size} ảnh, ${soLoi} ảnh không tải được (giữ liên kết gốc)`)
  else ElMessage.success(`Đã lưu ${urlMoi.size} ảnh về Thư viện`)
}
</script>

<style scoped>
.soan-thao {
  width: 100%;
  overflow: hidden;
  border: 1px solid var(--el-border-color);
  border-radius: var(--el-border-radius-base);
  background: var(--el-bg-color);
}

.soan-thao:focus-within {
  border-color: var(--el-color-primary);
}

.soan-thao__cong-cu {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 8px;
  padding: 6px 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-light);
}

.soan-thao__nhom {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.soan-thao__nhom + .soan-thao__nhom {
  padding-left: 8px;
  border-left: 1px solid var(--el-border-color-lighter);
}

.soan-thao__cong-cu button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-width: 30px;
  height: 30px;
  padding: 0 6px;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  color: var(--el-text-color-regular);
  font: inherit;
  font-size: 13px;
  cursor: pointer;
}

.soan-thao__cong-cu button:hover:not(:disabled) {
  background: var(--el-fill-color);
  color: var(--el-color-primary);
}

.soan-thao__cong-cu button.is-active {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.soan-thao__cong-cu button:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.soan-thao__cong-cu button:focus-visible {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 1px;
}

.soan-thao__cong-cu svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.soan-thao__chu {
  font-weight: 600;
  line-height: 1;
}

.soan-thao__chu--italic {
  font-style: italic;
  font-family: Georgia, serif;
}

.soan-thao__chu--underline {
  text-decoration: underline;
}

.soan-thao__chu--strike {
  text-decoration: line-through;
}

.soan-thao__kieu-khoi {
  width: 120px;
}

.soan-thao__dem {
  min-width: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: var(--el-color-warning);
  color: #fff;
  font-size: 11px;
  line-height: 18px;
}

.soan-thao__doi-che-do {
  margin-left: auto;
}

.soan-thao__goi-y {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.soan-thao__html :deep(textarea) {
  border: 0;
  border-radius: 0;
  box-shadow: none;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 13px;
}

/* Nội dung soạn thảo: kiểu chữ gần với trang tin. */
.soan-thao__noi-dung :deep(.tiptap) {
  min-height: 320px;
  max-height: 600px;
  overflow-y: auto;
  padding: 12px 16px;
  outline: none;
  line-height: 1.65;
  overflow-wrap: anywhere;
}

.soan-thao__noi-dung :deep(.tiptap > * + *) {
  margin-top: 0.75em;
}

.soan-thao__noi-dung :deep(.tiptap p) {
  margin: 0;
}

.soan-thao__noi-dung :deep(.tiptap h2) {
  margin: 1.1em 0 0.4em;
  font-size: 1.35rem;
}

.soan-thao__noi-dung :deep(.tiptap h3) {
  margin: 1em 0 0.4em;
  font-size: 1.15rem;
}

.soan-thao__noi-dung :deep(.tiptap h4) {
  margin: 0.9em 0 0.3em;
  font-size: 1rem;
}

.soan-thao__noi-dung :deep(.tiptap ul),
.soan-thao__noi-dung :deep(.tiptap ol) {
  margin: 0;
  padding-left: 1.5em;
}

.soan-thao__noi-dung :deep(.tiptap blockquote) {
  margin: 0;
  padding: 4px 12px;
  border-left: 3px solid var(--el-color-primary-light-5);
  color: var(--el-text-color-regular);
}

.soan-thao__noi-dung :deep(.tiptap a) {
  color: var(--el-color-primary);
  text-decoration: underline;
}

.soan-thao__noi-dung :deep(.tiptap img) {
  display: block;
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.soan-thao__noi-dung :deep(.tiptap img.ProseMirror-selectednode) {
  outline: 2px solid var(--el-color-primary);
}

.soan-thao__noi-dung :deep(.tiptap hr) {
  border: 0;
  border-top: 1px solid var(--el-border-color);
}

.soan-thao__noi-dung :deep(.tiptap table) {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.soan-thao__noi-dung :deep(.tiptap th),
.soan-thao__noi-dung :deep(.tiptap td) {
  position: relative;
  padding: 6px 8px;
  border: 1px solid var(--el-border-color);
  vertical-align: top;
}

.soan-thao__noi-dung :deep(.tiptap th) {
  background: var(--el-fill-color-light);
  font-weight: 600;
  text-align: left;
}

.soan-thao__noi-dung :deep(.tiptap .selectedCell::after) {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--el-color-primary-light-9);
  opacity: 0.6;
  pointer-events: none;
}

.soan-thao__noi-dung :deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  height: 0;
  color: var(--el-text-color-placeholder);
  pointer-events: none;
}
</style>
