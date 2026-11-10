<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiAssetUrl } from '@/api/apiUrl'
import {
  compressThuVien,
  copyThuVien,
  createThuMuc,
  deleteThuVien,
  deleteThuVienMany,
  extractThuVien,
  fetchThuVien,
  importThuVienUrl,
  moveThuVien,
  renameThuVien,
  uploadThuVien,
} from '@/api/thuVien'

const ACCEPT = '.jpg,.jpeg,.png,.gif,.webp,.mp4,.webm,.mov,.m4v,.zip,.rar,.7z,.tar,.gz,.tgz,.bz2,.xz,.tar.gz,.tar.bz2,.tar.xz'

const LOAI_LABEL = {
  thu_muc: 'Thư mục',
  hinh_anh: 'Hình ảnh',
  video: 'Video',
  nen: 'Tệp nén',
  tep: 'Tệp',
}

const loading = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const pendingFiles = ref([])
const deletingPath = ref('')
const extractingPath = ref('')
const compressing = ref(false)
const pasting = ref(false)
const deletingMany = ref(false)
const clipboard = ref(null)
const dialogVisible = ref(false)
const sourceUrl = ref('')
const previewKind = ref('')
const importingUrl = ref(false)
let previewToken = 0
const viewing = ref(null)
const viewMode = ref('bang')
const thuMuc = ref('')
const rows = ref([])
const selected = ref([])
const keyword = ref('')
const loai = ref('')

const crumbs = computed(() => {
  const parts = thuMuc.value.split('/').filter(Boolean)
  let path = ''
  return parts.map((ten) => {
    path = path ? `${path}/${ten}` : ten
    return { ten, path }
  })
})

function absoluteUrl(path) {
  return apiAssetUrl(path)
}

function displayPath(item) {
  if (!item) return ''
  if (item.la_thu_muc) return item.duong_dan_tuong_doi
  return absoluteUrl(item.duong_dan)
}

const filtered = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return rows.value.filter((item) => {
    if (q && !item.ten.toLowerCase().includes(q) && !displayPath(item).toLowerCase().includes(q)) {
      return false
    }
    if (item.la_thu_muc || !loai.value) return true
    return item.loai === loai.value
  })
})

watch(viewMode, () => {
  selected.value = []
})

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function formatSize(bytes) {
  if (bytes == null) return '—'
  const size = Number(bytes) || 0
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

function loaiTag(loaiItem) {
  if (loaiItem === 'hinh_anh') return 'success'
  if (loaiItem === 'video') return 'warning'
  if (loaiItem === 'nen') return 'primary'
  return 'info'
}

function rowIndex(index) {
  return index + 1
}

function isSelected(item) {
  return selected.value.includes(item.duong_dan_tuong_doi)
}

function toggleSelected(item, checked) {
  const path = item.duong_dan_tuong_doi
  if (checked) {
    if (!selected.value.includes(path)) selected.value = [...selected.value, path]
    return
  }
  selected.value = selected.value.filter((entry) => entry !== path)
}

function onSelectionChange(selection) {
  selected.value = selection.map((item) => item.duong_dan_tuong_doi)
}

async function load() {
  loading.value = true
  try {
    rows.value = await fetchThuVien(thuMuc.value)
    const alive = new Set(rows.value.map((item) => item.duong_dan_tuong_doi))
    selected.value = selected.value.filter((path) => alive.has(path))
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được thư viện'))
  } finally {
    loading.value = false
  }
}

function openFolder(path) {
  thuMuc.value = path
  keyword.value = ''
  selected.value = []
  load()
}

function openCreate() {
  dialogVisible.value = true
}

function kindFromUrl(url) {
  const path = url.split('?')[0].split('#')[0].toLowerCase()
  if (/\.(mp4|webm|mov|m4v)$/.test(path)) return 'video'
  if (/\.(jpe?g|png|gif|webp)$/.test(path)) return 'hinh_anh'
  if (/\.(zip|rar|7z|tar|gz|tgz|bz2|xz)$/.test(path)) return ''
  return ''
}

watch(sourceUrl, (value) => {
  const url = value.trim()
  const token = ++previewToken
  previewKind.value = ''
  if (!/^https?:\/\//i.test(url)) return
  const known = kindFromUrl(url)
  if (known) {
    previewKind.value = known
    return
  }
  window.setTimeout(() => {
    if (token !== previewToken) return
    const image = new Image()
    image.onload = () => {
      if (token === previewToken) previewKind.value = 'hinh_anh'
    }
    image.onerror = () => {
      if (token !== previewToken) return
      const video = document.createElement('video')
      video.preload = 'metadata'
      video.onloadedmetadata = () => {
        if (token === previewToken) previewKind.value = 'video'
      }
      video.src = url
    }
    image.src = url
  }, 300)
})

watch(dialogVisible, (open) => {
  if (open) return
  sourceUrl.value = ''
  previewKind.value = ''
  previewToken += 1
  pendingFiles.value = []
  uploadRef.value?.clearFiles()
})

function syncPending(_file, fileList) {
  pendingFiles.value = fileList
}

function removePending(file) {
  uploadRef.value?.handleRemove(file)
}

async function onUploadSelected() {
  const queue = pendingFiles.value.filter((item) => item.raw)
  if (!queue.length || uploading.value) return
  uploading.value = true
  const failed = []
  try {
    for (const item of queue) {
      try {
        await uploadThuVien(item.raw, thuMuc.value)
      } catch (error) {
        failed.push({
          uid: item.uid,
          name: item.name,
          message: errorMessage(error, `Không tải lên được ${item.name}`),
        })
      }
    }
  } finally {
    uploading.value = false
  }

  const failedIds = new Set(failed.map((item) => item.uid))
  for (const item of queue) {
    if (!failedIds.has(item.uid)) uploadRef.value?.handleRemove(item)
  }
  if (queue.length > failed.length) await load()
  if (!failed.length) {
    const label = queue.length === 1 ? queue[0].name : `${queue.length} file`
    ElMessage.success(`Đã tải lên ${label}`)
    dialogVisible.value = false
    return
  }
  if (failed.length < queue.length) {
    ElMessage.warning(
      `Đã tải lên ${queue.length - failed.length} file. Không tải được: ${failed.map((item) => item.name).join(', ')}`,
    )
    return
  }
  ElMessage.error(failed.length === 1 ? failed[0].message : `Không tải lên được ${failed.length} file`)
}

async function onImportUrl() {
  const url = sourceUrl.value.trim()
  if (!/^https?:\/\//i.test(url)) {
    ElMessage.warning('URL phải bắt đầu bằng http hoặc https')
    return
  }
  importingUrl.value = true
  try {
    await importThuVienUrl(url, thuMuc.value)
    ElMessage.success('Đã tải file từ URL')
    sourceUrl.value = ''
    previewKind.value = ''
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được file từ URL'))
  } finally {
    importingUrl.value = false
  }
}

async function promptName(title, message, value = '') {
  const result = await ElMessageBox.prompt(message, title, {
    confirmButtonText: 'Lưu',
    cancelButtonText: 'Hủy',
    inputValue: value,
    inputPattern: /\S+/,
    inputErrorMessage: 'Vui lòng nhập tên',
  })
  return result.value.trim()
}

async function onCreateFolder() {
  let ten = ''
  try {
    ten = await promptName('Tạo thư mục', 'Tên thư mục')
  } catch {
    return
  }
  try {
    await createThuMuc(thuMuc.value, ten)
    ElMessage.success('Đã tạo thư mục')
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tạo được thư mục'))
  }
}

async function onRename(item) {
  let tenMoi = ''
  try {
    tenMoi = await promptName('Đổi tên', item.la_thu_muc ? 'Tên thư mục mới' : 'Tên file mới', item.ten)
  } catch {
    return
  }
  if (tenMoi === item.ten) return
  try {
    await renameThuVien(item.duong_dan_tuong_doi, tenMoi)
    ElMessage.success('Đã đổi tên')
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi tên được'))
  }
}

async function onCompress() {
  if (!selected.value.length) return
  let tenTep = ''
  try {
    tenTep = await promptName('Nén các mục đã chọn', 'Tên file zip', 'thu-vien.zip')
  } catch {
    return
  }
  compressing.value = true
  try {
    await compressThuVien(thuMuc.value, selected.value, tenTep)
    selected.value = []
    ElMessage.success('Đã tạo file nén')
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không nén được các mục đã chọn'))
  } finally {
    compressing.value = false
  }
}

function rememberClipboard(mode, item = null) {
  const paths = item ? [item.duong_dan_tuong_doi] : [...selected.value]
  if (!paths.length) return
  clipboard.value = { mode, paths }
  const action = mode === 'di_chuyen' ? 'di chuyển' : 'sao chép'
  const label = item ? `"${item.ten}"` : `${paths.length} mục`
  ElMessage.success(`Đã chọn ${label} để ${action}. Mở thư mục đích rồi bấm Dán.`)
}

async function onPaste() {
  if (!clipboard.value?.paths?.length) return
  const moving = clipboard.value.mode === 'di_chuyen'
  pasting.value = true
  try {
    const result = moving
      ? await moveThuVien(clipboard.value.paths, thuMuc.value)
      : await copyThuVien(clipboard.value.paths, thuMuc.value)
    if (moving) clipboard.value = null
    selected.value = []
    ElMessage.success(moving ? `Đã di chuyển ${result.so_muc} mục` : `Đã dán ${result.so_muc} mục`)
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không dán được vào thư mục này'))
  } finally {
    pasting.value = false
  }
}

async function onDeleteSelected() {
  if (!selected.value.length) return
  const chosen = rows.value.filter((item) => selected.value.includes(item.duong_dan_tuong_doi))
  const hasFolder = chosen.some((item) => item.la_thu_muc)
  const count = selected.value.length
  const message = hasFolder
    ? `Xóa ${count} mục đã chọn? Thư mục sẽ bị xóa cùng toàn bộ file và thư mục con bên trong.`
    : `Xóa ${count} file đã chọn?`
  try {
    await ElMessageBox.confirm(message, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  deletingMany.value = true
  try {
    const result = await deleteThuVienMany([...selected.value])
    const removed = new Set(selected.value)
    if (clipboard.value) {
      const paths = clipboard.value.paths.filter((path) => !removed.has(path))
      clipboard.value = paths.length ? { ...clipboard.value, paths } : null
    }
    selected.value = []
    ElMessage.success(`Đã xóa ${result.so_muc} mục`)
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các mục đã chọn'))
  } finally {
    deletingMany.value = false
  }
}

async function onExtract(item) {
  extractingPath.value = item.duong_dan_tuong_doi
  try {
    const folder = await extractThuVien(item.duong_dan_tuong_doi)
    ElMessage.success(`Đã giải nén vào ${folder.ten}`)
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không giải nén được file'))
  } finally {
    extractingPath.value = ''
  }
}

function canPreview(item) {
  return item?.loai === 'hinh_anh' || item?.loai === 'video'
}

function openView(item) {
  if (!canPreview(item)) return
  viewing.value = item
}

async function copyPath(item) {
  const value = displayPath(item)
  try {
    await navigator.clipboard.writeText(value || '')
    ElMessage.success('Đã sao chép đường dẫn')
  } catch {
    ElMessage.error('Không sao chép được đường dẫn')
  }
}

async function onDelete(item) {
  const noun = item.la_thu_muc ? 'thư mục' : 'file'
  const message = item.la_thu_muc
    ? `Xóa thư mục "${item.ten}" sẽ xóa luôn toàn bộ file và thư mục con bên trong. Bạn có chắc muốn xóa?`
    : `Xóa file "${item.ten}"?`
  try {
    await ElMessageBox.confirm(message, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  deletingPath.value = item.duong_dan_tuong_doi
  try {
    await deleteThuVien(item.duong_dan_tuong_doi)
    ElMessage.success(`Đã xóa ${noun}`)
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được'))
  } finally {
    deletingPath.value = ''
  }
}

onMounted(load)
</script>

<template>
  <div class="library-page">
    <CustomCard shadow="never" class="library-card">
      <div class="toolbar">
        <div class="toolbar__lead">
          <h2 class="toolbar__title">Thư viện</h2>
          <nav class="crumbs" aria-label="Đường dẫn thư mục">
            <button type="button" :class="{ 'is-current': !thuMuc }" @click="openFolder('')">Gốc</button>
            <template v-for="crumb in crumbs" :key="crumb.path">
              <span>/</span>
              <button
                type="button"
                :class="{ 'is-current': crumb.path === thuMuc }"
                @click="openFolder(crumb.path)"
              >
                {{ crumb.ten }}
              </button>
            </template>
          </nav>
        </div>
        <div class="toolbar__actions">
          <CustomInput v-model="keyword" class="filter-search" placeholder="Tìm theo tên hoặc đường dẫn" clearable>
            <template #prefix>
              <CustomIcon><Search /></CustomIcon>
            </template>
          </CustomInput>
          <CustomSelect v-model="loai" class="filter-type" placeholder="Loại file" clearable>
            <CustomOption label="Hình ảnh" value="hinh_anh" />
            <CustomOption label="Video" value="video" />
            <CustomOption label="Tệp nén" value="nen" />
            <CustomOption label="Tệp khác" value="tep" />
          </CustomSelect>
          <div class="toolbar__buttons">
            <CustomTooltip v-if="selected.length" content="Nén các mục đã chọn thành file ZIP" placement="top">
              <span class="toolbar__tip">
                <CustomButton :loading="compressing" @click="onCompress">
                  <CustomIcon><Box /></CustomIcon>
                </CustomButton>
              </span>
            </CustomTooltip>
            <CustomTooltip v-if="selected.length" content="Chọn thư mục đích rồi bấm Dán để di chuyển" placement="top">
              <span class="toolbar__tip">
                <CustomButton @click="rememberClipboard('di_chuyen')">
                  <CustomIcon><Rank /></CustomIcon>
                </CustomButton>
              </span>
            </CustomTooltip>
            <CustomTooltip v-if="selected.length" content="Sao chép các mục đã chọn để dán sang thư mục khác" placement="top">
              <span class="toolbar__tip">
                <CustomButton @click="rememberClipboard('sao_chep')">
                  <CustomIcon><DocumentCopy /></CustomIcon>
                </CustomButton>
              </span>
            </CustomTooltip>
            <CustomTooltip
              v-if="selected.length || clipboard"
              :content="clipboard ? 'Dán vào thư mục đang mở' : 'Hãy sao chép hoặc di chuyển trước khi dán'"
              placement="top"
            >
              <span class="toolbar__tip">
                <CustomButton :disabled="!clipboard" :loading="pasting" @click="onPaste">
                  <CustomIcon><DocumentAdd /></CustomIcon>
                </CustomButton>
              </span>
            </CustomTooltip>
            <CustomTooltip v-if="selected.length" content="Xóa các mục đã chọn" placement="top">
              <span class="toolbar__tip">
                <CustomButton type="danger" plain :loading="deletingMany" @click="onDeleteSelected">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </span>
            </CustomTooltip>
            <CustomTooltip content="Tạo thư mục trong chỗ đang mở" placement="top">
              <span class="toolbar__tip">
                <CustomButton @click="onCreateFolder">
                  <CustomIcon><FolderAdd /></CustomIcon>
                </CustomButton>
              </span>
            </CustomTooltip>
            <CustomTooltip content="Tải ảnh, video hoặc file nén" placement="top">
              <span class="toolbar__tip">
                <CustomButton type="primary" @click="openCreate">
                  <CustomIcon><Upload /></CustomIcon>
                </CustomButton>
              </span>
            </CustomTooltip>
            <CustomRadioGroup v-model="viewMode" class="view-switch">
              <CustomRadioButton value="bang" title="Dạng bảng" aria-label="Dạng bảng">
                <CustomIcon><List /></CustomIcon>
              </CustomRadioButton>
              <CustomRadioButton value="luoi" title="Dạng lưới" aria-label="Dạng lưới">
                <CustomIcon><Grid /></CustomIcon>
              </CustomRadioButton>
            </CustomRadioGroup>
          </div>
        </div>
      </div>

      <CustomTable
        v-if="viewMode === 'bang'"
        :loading="loading"
        :data="filtered"
        row-key="duong_dan_tuong_doi"
        stripe
        border
        @selection-change="onSelectionChange"
      >
        <CustomTableColumn type="selection" width="48" align="center" />
        <CustomTableColumn label="STT" width="72" align="center">
          <template #default="{ $index }">{{ rowIndex($index) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Xem trước" width="108" align="center">
          <template #default="{ row }">
            <button
              v-if="row.la_thu_muc"
              type="button"
              class="thumb-button"
              aria-label="Mở thư mục"
              @click="openFolder(row.duong_dan_tuong_doi)"
            >
              <CustomIcon class="thumb-icon" :size="28"><Folder /></CustomIcon>
            </button>
            <img v-else-if="row.loai === 'hinh_anh'" class="thumb" :src="absoluteUrl(row.duong_dan)" :alt="row.ten" />
            <video v-else-if="row.loai === 'video'" class="thumb" :src="absoluteUrl(row.duong_dan)" muted preload="metadata" />
            <CustomIcon v-else class="thumb-icon" :size="28">
              <Files v-if="row.loai === 'nen'" />
              <Document v-else />
            </CustomIcon>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Tên" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <button
              v-if="row.la_thu_muc"
              type="button"
              class="folder-link"
              @click="openFolder(row.duong_dan_tuong_doi)"
            >
              {{ row.ten }}
            </button>
            <span v-else>{{ row.ten }}</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Loại" width="120" align="center">
          <template #default="{ row }">
            <CustomTag :type="loaiTag(row.loai)" effect="light">{{ LOAI_LABEL[row.loai] }}</CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Dung lượng" width="120" align="right">
          <template #default="{ row }">{{ formatSize(row.kich_thuoc) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Đường dẫn" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">{{ displayPath(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thao tác" width="300" fixed="right" align="center">
          <template #default="{ row }">
            <div class="icon-actions">
              <CustomTooltip v-if="canPreview(row)" content="Xem" placement="top">
                <CustomButton link type="primary" aria-label="Xem" @click="openView(row)">
                  <CustomIcon><View /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Sao chép đường dẫn" placement="top">
                <CustomButton link type="primary" aria-label="Sao chép đường dẫn" @click="copyPath(row)">
                  <CustomIcon><CopyDocument /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Sao chép file" placement="top">
                <CustomButton link type="primary" aria-label="Sao chép file" @click="rememberClipboard('sao_chep', row)">
                  <CustomIcon><DocumentCopy /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Di chuyển" placement="top">
                <CustomButton link type="primary" aria-label="Di chuyển" @click="rememberClipboard('di_chuyen', row)">
                  <CustomIcon><Rank /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip v-if="row.loai === 'nen'" content="Giải nén" placement="top">
                <CustomButton
                  link
                  type="primary"
                  aria-label="Giải nén"
                  :loading="extractingPath === row.duong_dan_tuong_doi"
                  @click="onExtract(row)"
                >
                  <CustomIcon><FolderOpened /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Đổi tên" placement="top">
                <CustomButton link type="primary" aria-label="Đổi tên" @click="onRename(row)">
                  <CustomIcon><EditPen /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Xóa" placement="top">
                <CustomButton
                  link
                  type="danger"
                  aria-label="Xóa"
                  :loading="deletingPath === row.duong_dan_tuong_doi"
                  @click="onDelete(row)"
                >
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Thư mục trống." />
        </template>
      </CustomTable>

      <div v-else v-loading="loading" class="grid-wrap">
        <div v-if="filtered.length" class="media-grid">
          <article v-for="item in filtered" :key="item.duong_dan_tuong_doi" class="media-card">
            <div class="media-preview">
              <el-checkbox
                class="media-check"
                :model-value="isSelected(item)"
                @change="(checked) => toggleSelected(item, checked)"
                @click.stop
              />
              <button
                v-if="item.la_thu_muc"
                type="button"
                class="preview-open"
                aria-label="Mở thư mục"
                @click="openFolder(item.duong_dan_tuong_doi)"
              >
                <CustomIcon :size="42"><Folder /></CustomIcon>
              </button>
              <img v-else-if="item.loai === 'hinh_anh'" :src="absoluteUrl(item.duong_dan)" :alt="item.ten" />
              <video v-else-if="item.loai === 'video'" :src="absoluteUrl(item.duong_dan)" controls preload="metadata" />
              <CustomIcon v-else :size="42">
                <Files v-if="item.loai === 'nen'" />
                <Document v-else />
              </CustomIcon>
            </div>
            <div class="media-body">
              <button
                v-if="item.la_thu_muc"
                type="button"
                class="media-name folder-link"
                :title="item.ten"
                @click="openFolder(item.duong_dan_tuong_doi)"
              >
                {{ item.ten }}
              </button>
              <p v-else class="media-name" :title="displayPath(item) || item.ten">{{ item.ten }}</p>
              <!-- <div class="media-meta">
                <CustomTag :type="loaiTag(item.loai)" effect="light">{{ LOAI_LABEL[item.loai] }}</CustomTag>
                <span>{{ formatSize(item.kich_thuoc) }}</span>
              </div> -->
              <div class="icon-actions">
                <CustomTooltip v-if="canPreview(item)" content="Xem" placement="top">
                  <CustomButton link type="primary" aria-label="Xem" @click="openView(item)">
                    <CustomIcon><View /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
                <CustomTooltip content="Sao chép đường dẫn" placement="top">
                  <CustomButton link type="primary" aria-label="Sao chép đường dẫn" @click="copyPath(item)">
                    <CustomIcon><CopyDocument /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
                <CustomTooltip content="Sao chép file" placement="top">
                  <CustomButton link type="primary" aria-label="Sao chép file" @click="rememberClipboard('sao_chep', item)">
                    <CustomIcon><DocumentCopy /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
                <CustomTooltip content="Di chuyển" placement="top">
                  <CustomButton link type="primary" aria-label="Di chuyển" @click="rememberClipboard('di_chuyen', item)">
                    <CustomIcon><Rank /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
                <CustomTooltip v-if="item.loai === 'nen'" content="Giải nén" placement="top">
                  <CustomButton
                    link
                    type="primary"
                    aria-label="Giải nén"
                    :loading="extractingPath === item.duong_dan_tuong_doi"
                    @click="onExtract(item)"
                  >
                    <CustomIcon><FolderOpened /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
                <CustomTooltip content="Đổi tên" placement="top">
                  <CustomButton link type="primary" aria-label="Đổi tên" @click="onRename(item)">
                    <CustomIcon><EditPen /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
                <CustomTooltip content="Xóa" placement="top">
                  <CustomButton
                    link
                    type="danger"
                    aria-label="Xóa"
                    :loading="deletingPath === item.duong_dan_tuong_doi"
                    @click="onDelete(item)"
                  >
                    <CustomIcon><Delete /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
              </div>
            </div>
          </article>
        </div>
        <CustomEmpty v-else-if="!loading" description="Thư mục trống." />
      </div>
    </CustomCard>
  </div>

  <CustomDialog v-model="dialogVisible" title="Thêm file" width="640px" height="680px">
    <el-upload
      ref="uploadRef"
      class="uploader"
      drag
      multiple
      :accept="ACCEPT"
      :auto-upload="false"
      :show-file-list="false"
      :on-change="syncPending"
      :on-remove="syncPending"
      :disabled="uploading || importingUrl"
    >
      <CustomIcon class="uploader__icon" :size="36"><UploadFilled /></CustomIcon>
      <div class="el-upload__text">
        Kéo thả ảnh, video hoặc file nén vào đây, hoặc <em>bấm để chọn</em>
      </div>
      <template #tip>
        <p class="uploader__tip">
          Ảnh, video, hoặc file nén ZIP, RAR, 7Z, TAR. Mỗi file tối đa 100 MB. File được lưu vào thư mục đang mở.
        </p>
      </template>
    </el-upload>

    <div class="url-import">
      <p class="url-import__label">Hoặc thêm từ URL</p>
      <div class="url-import__row">
        <CustomInput
          v-model="sourceUrl"
          placeholder="Dán URL http hoặc https của file"
          clearable
          :disabled="importingUrl"
          @keyup.enter="onImportUrl"
        />
        <CustomButton type="primary" :loading="importingUrl" :disabled="uploading" @click="onImportUrl">
          Tải về
        </CustomButton>
      </div>
      <div v-if="previewKind" class="url-preview">
        <img v-if="previewKind === 'hinh_anh'" :src="sourceUrl.trim()" alt="Xem trước ảnh" />
        <video v-else :src="sourceUrl.trim()" controls preload="metadata" />
      </div>
      <p v-if="previewKind" class="uploader__tip">Xem trước trước khi tải về thư viện.</p>
    </div>

    <ul v-if="pendingFiles.length" class="picked-files">
      <li v-for="file in pendingFiles" :key="file.uid" class="picked-files__item">
        <span class="picked-files__name" :title="file.name">{{ file.name }}</span>
        <span class="picked-files__size">{{ formatSize(file.size ?? file.raw?.size) }}</span>
        <CustomButton link type="danger" aria-label="Bỏ file" :disabled="uploading" @click="removePending(file)">
          <CustomIcon><Close /></CustomIcon>
        </CustomButton>
      </li>
    </ul>
    <template #footer>
      <CustomButton :disabled="uploading || importingUrl" @click="dialogVisible = false">Đóng</CustomButton>
      <CustomButton
        type="primary"
        :loading="uploading"
        :disabled="!pendingFiles.length || importingUrl"
        @click="onUploadSelected"
      >
        Tải lên
      </CustomButton>
    </template>
  </CustomDialog>

  <CustomDialog
    :model-value="!!viewing"
    :title="viewing?.ten || 'Xem chi tiết'"
    width="920px"
    height="780px"
    @update:model-value="(open) => { if (!open) viewing = null }"
  >
    <div v-if="viewing" class="viewer">
      <div class="viewer__stage">
        <img v-if="viewing.loai === 'hinh_anh'" :src="absoluteUrl(viewing.duong_dan)" :alt="viewing.ten" />
        <video v-else :src="absoluteUrl(viewing.duong_dan)" controls autoplay />
      </div>
      <dl class="viewer__meta">
        <div>
          <dt>Loại</dt>
          <dd>{{ LOAI_LABEL[viewing.loai] }}</dd>
        </div>
        <div>
          <dt>Dung lượng</dt>
          <dd>{{ formatSize(viewing.kich_thuoc) }}</dd>
        </div>
        <div>
          <dt>Đường dẫn</dt>
          <dd>{{ displayPath(viewing) }}</dd>
        </div>
      </dl>
    </div>
    <template #footer>
      <CustomButton @click="copyPath(viewing)">Sao chép đường dẫn</CustomButton>
      <CustomButton type="primary" @click="viewing = null">Đóng</CustomButton>
    </template>
  </CustomDialog>
</template>

<style scoped>
.library-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.library-card {
  border-radius: 12px;
}

.toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar__lead {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.toolbar__title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.crumbs {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.crumbs button {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--el-color-primary);
  cursor: pointer;
}

.crumbs button.is-current {
  color: var(--el-text-color-primary);
  font-weight: 600;
  cursor: default;
}

.toolbar__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-left: auto;
}

.toolbar__buttons {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.toolbar__tip {
  display: inline-flex;
}

.toolbar__buttons :deep(.el-button) {
  margin: 0;
}

.filter-search {
  width: 260px;
}

.filter-type {
  width: 150px;
}

.view-switch :deep(.el-radio-button__inner) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
}

.thumb,
.thumb-button {
  width: 72px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  vertical-align: middle;
}

.thumb-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  color: var(--el-color-warning);
  cursor: pointer;
}

.thumb-icon {
  color: var(--el-color-primary);
}

.folder-link {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--el-color-primary);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.icon-actions {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.icon-actions :deep(.el-button) {
  width: 32px;
  height: 32px;
  padding: 0;
  margin: 0;
}

.icon-actions :deep(.el-icon) {
  font-size: 22px !important;
}

.icon-actions :deep(.el-icon svg) {
  stroke: currentColor;
  stroke-width: 10;
  stroke-linejoin: round;
  paint-order: stroke fill;
}

.grid-wrap {
  min-height: 160px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
}

.media-card {
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
}

.media-preview {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 112px;
  background: var(--el-fill-color-light);
  color: var(--el-color-warning);
}

.media-check {
  position: absolute;
  top: 6px;
  left: 6px;
  z-index: 1;
  height: auto;
}

.preview-open {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.media-preview img,
.media-preview video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #111;
}

.media-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
}

.media-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.media-name {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  text-align: left;
}

.uploader {
  width: 100%;
}

.uploader :deep(.el-upload),
.uploader :deep(.el-upload-dragger) {
  width: 100%;
}

.uploader__icon {
  margin-bottom: 8px;
  color: var(--el-color-primary);
}

.uploader__tip {
  margin: 8px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.picked-files {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

.picked-files__item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 36px;
  padding: 4px 8px 4px 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-fill-color-light);
}

.picked-files__name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.picked-files__size {
  flex-shrink: 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.url-import {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
}

.url-import__label {
  margin: 0;
  font-weight: 600;
}

.url-import__row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.url-import__row :deep(.el-input) {
  flex: 1;
}

.url-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 180px;
  overflow: hidden;
  border-radius: 12px;
  background: #111;
}

.url-preview img,
.url-preview video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.viewer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  height: 100%;
}

.viewer__stage {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 280px;
  overflow: hidden;
  border-radius: 12px;
  background: #111;
}

.viewer__stage img,
.viewer__stage video {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.viewer__meta {
  display: grid;
  gap: 8px;
  margin: 0;
}

.viewer__meta div {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 8px;
}

.viewer__meta dt {
  color: var(--el-text-color-secondary);
}

.viewer__meta dd {
  margin: 0;
  overflow-wrap: anywhere;
}

@media (max-width: 1200px) {
  .media-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .media-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .toolbar__actions {
    margin-left: 0;
  }

  .filter-search,
  .filter-type {
    width: 100%;
  }

  .media-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .media-preview {
    height: 148px;
  }
}
</style>
