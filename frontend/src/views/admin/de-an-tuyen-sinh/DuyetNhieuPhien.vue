<template>
  <div class="toolbar__actions duyet-nhieu">
    <span v-if="tienDo" role="status">{{ tienDo }}</span>
    <CustomButton v-if="ketQua" :disabled="dangXuLy" @click="hienKetQua = true">Xem kết quả duyệt</CustomButton>
    <CustomButton v-if="props.choPhepDuyet" type="primary" :loading="dangXuLy" :disabled="props.disabled" @click="batDau">
      <CustomIcon><CircleCheck /></CustomIcon> Duyệt tất cả
    </CustomButton>
  </div>

  <CustomDialog v-model="hienKetQua" title="Kết quả duyệt hàng loạt" width="720px" append-to-body>
    <template v-if="ketQua">
      <p>{{ ketQua.phamVi }} · {{ ketQua.soPhien }} phiên chờ duyệt tại thời điểm xác nhận.</p>
      <p role="status"><strong>{{ ketQua.daDuyet.length }} phiên đã duyệt và nhập</strong> · {{ ketQua.thatBai.length }} phiên không duyệt được.</p>
      <el-alert v-if="ketQua.chuaXacMinh.length" type="warning" show-icon :closable="false" title="Chưa xác minh được kết quả của một phần yêu cầu">
        <p>{{ ketQua.lyDoGianDoan }} Hãy kiểm tra lại trạng thái các phiên này trước khi gửi lại.</p>
        <ul class="danh-sach-ket-qua">
          <li v-for="item in ketQua.chuaXacMinh" :key="item.id">Phiên #{{ item.id }} · Bản {{ item.phien_ban }}</li>
        </ul>
      </el-alert>
      <details v-if="ketQua.chuaGui.length" class="nhom-ket-qua">
        <summary>{{ ketQua.chuaGui.length }} phiên chưa gửi</summary>
        <ul class="danh-sach-ket-qua">
          <li v-for="item in ketQua.chuaGui" :key="item.id">Phiên #{{ item.id }} · Bản {{ item.phien_ban }}</li>
        </ul>
      </details>
      <details v-if="ketQua.thatBai.length" open class="nhom-ket-qua">
        <summary>Phiên không duyệt được</summary>
        <ul class="danh-sach-ket-qua">
          <li v-for="item in ketQua.thatBai" :key="item.id">
            <strong>Phiên #{{ item.id }} · Bản {{ item.phien_ban }}</strong> · {{ item.noiDung }}
            <span v-if="item.deAnId"> · Đề án #{{ item.deAnId }}</span>
            <ul v-if="item.loi.length">
              <li v-for="(lyDo, index) in item.loi" :key="index">{{ lyDo }}</li>
            </ul>
          </li>
        </ul>
      </details>
      <details v-if="ketQua.daDuyet.length" class="nhom-ket-qua">
        <summary>Phiên đã duyệt và nhập</summary>
        <ul class="danh-sach-ket-qua">
          <li v-for="item in ketQua.daDuyet" :key="item.id">Phiên #{{ item.id }} · Bản {{ item.phien_ban }} · Đề án #{{ item.de_an_id }}</li>
        </ul>
      </details>
    </template>
    <template #footer><CustomButton @click="hienKetQua = false">Đóng</CustomButton></template>
  </CustomDialog>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { duyetNhieuPhienTuyenSinh, layDanhSachPhien } from '@/api/thuThapTuyenSinh'
import { chiTietLoiPhien, loiPhien } from './thu-thap-du-lieu'

const props = defineProps({
  boLoc: { type: Object, required: true },
  choPhepDuyet: Boolean,
  disabled: Boolean,
})
const dangXuLy = defineModel('dangXuLy', { type: Boolean, default: false })
const emit = defineEmits(['da-xu-ly'])
const kichThuocTrang = 200
const kichThuocDot = 5
const dangTongHop = ref(false)
const dangDuyet = ref(false)
const soPhien = ref(0)
const soPhienDaPhanHoi = ref(0)
const hienKetQua = ref(false)
const ketQua = ref(null)
let daRoiTrang = false

const tienDo = computed(() => {
  if (dangTongHop.value) return 'Đang đếm phiên chờ duyệt…'
  if (dangDuyet.value) return `Đang duyệt · Đã có kết quả ${soPhienDaPhanHoi.value}/${soPhien.value} phiên`
  return ''
})

function giuKetQuaKhiDangDuyet() {
  if (!dangDuyet.value) return true
  ElMessage.info('Chờ yêu cầu duyệt hiện tại trả kết quả trước khi chuyển trang.')
  return false
}

onBeforeRouteLeave(giuKetQuaKhiDangDuyet)
onBeforeRouteUpdate(giuKetQuaKhiDangDuyet)
onBeforeUnmount(() => { daRoiTrang = true })

async function layPhienChoDuyet(boLoc) {
  const phien = new Map()
  let tong = null
  for (let page = 1; tong === null || (page - 1) * kichThuocTrang < tong; page += 1) {
    const ketQuaTrang = await layDanhSachPhien({ ...boLoc, trang_thai: 'cho_duyet', page, page_size: kichThuocTrang })
    if (daRoiTrang || (tong !== null && tong !== ketQuaTrang.total)) return null
    tong = ketQuaTrang.total
    for (const item of ketQuaTrang.items) {
      if (!item.phien_ban || item.trang_thai !== 'cho_duyet') continue
      phien.set(item.id, { id: item.id, phien_ban: item.phien_ban })
    }
  }
  return phien.size === tong ? [...phien.values()] : null
}

function moTaPhamVi(boLoc) {
  const truong = boLoc.ma_truong ? `Mã trường ${boLoc.ma_truong}` : 'Tất cả trường'
  const nam = boLoc.nam_tuyen_sinh ? `năm ${boLoc.nam_tuyen_sinh}` : 'tất cả năm'
  return `${truong}, ${nam}`
}

async function duyetCacPhien(phien, phamVi) {
  const tongHop = { soPhien: phien.length, phamVi, daDuyet: [], thatBai: [], chuaXacMinh: [], chuaGui: [], lyDoGianDoan: '' }
  for (let dau = 0; dau < phien.length; dau += kichThuocDot) {
    const dot = phien.slice(dau, dau + kichThuocDot)
    try {
      const ketQuaDot = await duyetNhieuPhienTuyenSinh(dot)
      const banTrongDot = new Map(dot.map((item) => [item.id, item.phien_ban]))
      const dsDaDuyet = ketQuaDot.da_duyet.filter((item) => banTrongDot.get(item.id) === item.phien_ban)
      const dsThatBai = ketQuaDot.that_bai.filter((item) => banTrongDot.get(item.id) === item.phien_ban)
      tongHop.daDuyet.push(...dsDaDuyet)
      tongHop.thatBai.push(...dsThatBai.map((item) => ({ ...item, ...chiTietLoiPhien(item.detail) })))
      soPhienDaPhanHoi.value = tongHop.daDuyet.length + tongHop.thatBai.length
      const daCoKetQua = new Set([...dsDaDuyet, ...dsThatBai].map((item) => item.id))
      tongHop.chuaXacMinh = dot.filter((item) => !daCoKetQua.has(item.id))
      if (tongHop.chuaXacMinh.length) tongHop.lyDoGianDoan = 'Máy chủ chưa trả đủ kết quả.'
    } catch (error) {
      tongHop.chuaXacMinh = dot
      tongHop.lyDoGianDoan = loiPhien(error).noiDung
    }
    if (tongHop.chuaXacMinh.length) {
      tongHop.chuaGui = phien.slice(dau + dot.length)
      break
    }
  }
  return tongHop
}

async function batDau() {
  if (dangXuLy.value || props.disabled) return
  dangXuLy.value = true
  dangTongHop.value = true
  const boLoc = { ...props.boLoc }
  try {
    const phien = await layPhienChoDuyet(boLoc)
    dangTongHop.value = false
    if (daRoiTrang) return
    if (!phien) {
      ElMessage.warning('Danh sách chờ duyệt đã thay đổi khi tổng hợp. Hãy xem lại danh sách trước khi duyệt.')
      emit('da-xu-ly')
      return
    }
    if (!phien.length) {
      ElMessage.info('Không còn phiên chờ duyệt theo bộ lọc hiện tại.')
      emit('da-xu-ly')
      return
    }
    const phamVi = moTaPhamVi(boLoc)
    try {
      await ElMessageBox.confirm(
        `${phamVi}. Duyệt và nhập ${phien.length} phiên đang chờ duyệt? Thao tác này sẽ tạo đề án và nhập quy tắc của các phiên hợp lệ vào hệ thống.`,
        'Duyệt tất cả phiên chờ duyệt',
        { type: 'warning', confirmButtonText: 'Duyệt và nhập', cancelButtonText: 'Hủy' },
      )
    } catch {
      return
    }
    if (daRoiTrang) return
    soPhien.value = phien.length
    soPhienDaPhanHoi.value = 0
    dangDuyet.value = true
    ketQua.value = await duyetCacPhien(phien, phamVi)
    hienKetQua.value = true
    emit('da-xu-ly')
  } catch (error) {
    if (!daRoiTrang) ElMessage.error(loiPhien(error).noiDung)
  } finally {
    dangTongHop.value = false
    dangDuyet.value = false
    dangXuLy.value = false
  }
}
</script>

<style scoped>
.duyet-nhieu :deep(.el-button + .el-button) { margin-left: 0; }
.nhom-ket-qua { margin-top: 12px; }
summary { cursor: pointer; }
.danh-sach-ket-qua { max-height: 200px; overflow: auto; overflow-wrap: anywhere; margin: 6px 0; padding-inline-start: 20px; }
.danh-sach-ket-qua li { margin-bottom: 4px; }
</style>
