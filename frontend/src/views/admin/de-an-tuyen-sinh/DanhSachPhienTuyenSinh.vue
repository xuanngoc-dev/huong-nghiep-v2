<template>
  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">{{ props.tieuDe }}</h2>
      <DuyetNhieuPhien
        v-if="props.xetDuyet"
        v-model:dang-xu-ly="dangDuyetNhieu"
        :bo-loc="boLocApDung"
        :cho-phep-duyet="coPhamViDuyet"
        :disabled="dangTai || phienDangXoa !== null || !tong || coLocChuaApDung"
        @da-xu-ly="taiDanhSach"
      />
    </div>
    <form class="filters loc-phien" @submit.prevent="timKiem">
      <CustomInput
        v-model="boLoc.ma_truong"
        class="filter-search"
        aria-label="Mã trường"
        placeholder="Tìm theo mã trường"
        maxlength="20"
        clearable
        :disabled="dangDuyetNhieu"
        @clear="timKiem"
      />
      <CustomInputNumber
        v-model="boLoc.nam_tuyen_sinh"
        class="filter-year"
        aria-label="Năm tuyển sinh"
        placeholder="Nhập năm tuyển sinh"
        :controls="false"
        :phan-tach-hang-nghin="false"
        :min="1990"
        :max="2100"
        :precision="0"
        :disabled="dangDuyetNhieu"
      />
      <CustomSelect
        v-model="boLoc.trang_thai"
        class="filter-status"
        aria-label="Trạng thái"
        placeholder="Chọn trạng thái"
        :disabled="dangDuyetNhieu"
        @change="timKiem"
      >
        <CustomOption label="Tất cả trạng thái" value="tat_ca" />
        <CustomOption
          v-for="item in TUY_CHON_TRANG_THAI"
          :key="item.giaTri"
          :label="item.nhan"
          :value="item.giaTri"
        />
      </CustomSelect>
      <CustomButton type="primary" native-type="submit" :loading="dangTai" :disabled="dangDuyetNhieu">Lọc</CustomButton>
      <span v-if="coPhamViDuyet && coLocChuaApDung" class="cell-sub">Bấm Lọc để áp dụng điều kiện mới trước khi duyệt tất cả.</span>
    </form>
    <el-alert v-if="loi" :title="loi" type="error" show-icon :closable="false" class="loc-phien" />
    <CustomTable :loading="dangTai" :data="cacPhien" row-key="id" stripe border>
      <CustomTableColumn label="Mã phiên" min-width="100">
        <template #default="{ row }">#{{ row.id }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Trường" min-width="235">
        <template #default="{ row }">
          <div class="cell-stack">
            <strong>{{ row.ma_truong }} · {{ row.ten_truong }}</strong>
            <span v-if="row.co_so" class="cell-sub">{{ row.co_so }}</span>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn prop="nam_tuyen_sinh" label="Năm" width="85" />
      <CustomTableColumn label="Trạng thái" :min-width="props.xetDuyet ? 148 : 200">
        <template #default="{ row }">
          <div class="trang-thai-phien">
            <CustomTag :type="nhanTrangThai(row).loai">{{ nhanTrangThai(row).nhan }}</CustomTag>
            <router-link v-if="!props.xetDuyet && row.trang_thai === 'cho_duyet' && row.phien_ban" class="cell-link" :to="{ name: TRANG_XET_DUYET, query: { phien: row.id } }">Mở bản nháp</router-link>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn v-if="props.xetDuyet" label="Phiên bản" width="104">
        <template #default="{ row }">{{ row.phien_ban ?? '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Người tạo" min-width="130">
        <template #default="{ row }">{{ row.ten_nguoi_tao || `#${row.tao_boi}` }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Cập nhật" min-width="155">
        <template #default="{ row }">{{ ngayGio(row.cap_nhat_luc) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Thao tác" width="104" fixed="right" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <CustomTooltip :content="`Xem phiên #${row.id}`" placement="top">
              <CustomButton link type="primary" :aria-label="`Xem phiên #${row.id}`" :disabled="phienDangXoa === row.id || dangDuyetNhieu" @click="moPhien(row.id)">
                <CustomIcon><View /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip v-if="coTheXoa(row)" :content="`Xóa phiên #${row.id}`" placement="top">
              <CustomButton link type="danger" :aria-label="`Xóa phiên #${row.id}`" :disabled="phienDangXoa !== null || dangDuyetNhieu || dangTaoBanNhap(row)" :loading="phienDangXoa === row.id" @click="xoaPhien(row)">
                <CustomIcon><Delete /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Không có phiên phù hợp." />
      </template>
    </CustomTable>
    <div v-if="tong > kichThuoc" class="pager">
      <CustomPagination v-model:current-page="trang" :page-size="kichThuoc" :total="tong" :pager-count="5" :disabled="dangDuyetNhieu" layout="total, prev, pager, next" @current-change="taiDanhSach" />
    </div>
  </CustomCard>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { layDanhSachPhien, xoaPhienTuyenSinh } from '@/api/thuThapTuyenSinh'
import DuyetNhieuPhien from './DuyetNhieuPhien.vue'
import { TRANG_XET_DUYET, TUY_CHON_TRANG_THAI, loiPhien, ngayGio, trangThaiThuThap } from './thu-thap-du-lieu'

const props = defineProps({
  tieuDe: { type: String, required: true },
  trangChiTiet: { type: String, required: true },
  xetDuyet: Boolean,
  phienDangTao: { type: Set, default: () => new Set() },
})

const boLoc = reactive({ ma_truong: '', nam_tuyen_sinh: undefined, trang_thai: props.xetDuyet ? 'cho_duyet' : 'tat_ca' })
const thamSoLoc = computed(() => ({
  ma_truong: boLoc.ma_truong.trim().toUpperCase() || undefined,
  nam_tuyen_sinh: boLoc.nam_tuyen_sinh || undefined,
  trang_thai: boLoc.trang_thai === 'tat_ca' ? undefined : boLoc.trang_thai,
}))
const boLocApDung = ref(thamSoLoc.value)
const coLocChuaApDung = computed(() => Object.keys(boLocApDung.value).some((key) => thamSoLoc.value[key] !== boLocApDung.value[key]))
const coPhamViDuyet = computed(() => props.xetDuyet && [undefined, 'cho_duyet'].includes(boLocApDung.value.trang_thai))
const router = useRouter()
const cacPhien = ref([])
const trang = ref(1)
const tong = ref(0)
const loi = ref('')
const dangTai = ref(false)
const dangDuyetNhieu = ref(false)
const phienDangXoa = ref(null)
const coPhienDangTao = computed(() => cacPhien.value.some(dangTaoBanNhap))
const kichThuoc = 20
let thuTuTai = 0

async function taiDanhSach({ amTham = false } = {}) {
  if (amTham && (dangTai.value || dangDuyetNhieu.value || phienDangXoa.value !== null)) return
  const thuTu = ++thuTuTai
  if (!amTham) {
    dangTai.value = true
    loi.value = ''
  }
  try {
    const ketQua = await layDanhSachPhien({
      ...boLocApDung.value,
      page: trang.value,
      page_size: kichThuoc,
    })
    if (thuTu !== thuTuTai) return
    cacPhien.value = ketQua.items
    tong.value = ketQua.total
    const trangCuoi = Math.max(1, Math.ceil(tong.value / kichThuoc))
    if (trang.value > trangCuoi) {
      trang.value = trangCuoi
      await taiDanhSach({ amTham })
    }
  } catch (error) {
    if (!amTham && thuTu === thuTuTai) {
      loi.value = loiPhien(error).noiDung
      cacPhien.value = []
      tong.value = 0
    }
  } finally {
    if (thuTu === thuTuTai) dangTai.value = false
  }
}

watch(coPhienDangTao, (dangTao, _, onCleanup) => {
  if (!dangTao) return
  let conTheoDoi = true
  let henGio
  async function capNhat() {
    await taiDanhSach({ amTham: true })
    if (conTheoDoi) henGio = setTimeout(capNhat, 5000)
  }
  henGio = setTimeout(capNhat, 5000)
  onCleanup(() => {
    conTheoDoi = false
    clearTimeout(henGio)
  })
}, { immediate: true })

watch(() => props.phienDangTao.size, (moi, cu) => {
  if (moi < cu) taiDanhSach({ amTham: true })
})

function timKiem() {
  if (dangDuyetNhieu.value) return
  boLocApDung.value = thamSoLoc.value
  trang.value = 1
  taiDanhSach()
}

function nhanTrangThai(phien) {
  return trangThaiThuThap(phien, dangTaoBanNhap(phien), !props.xetDuyet)
}

function dangTaoBanNhap(phien) {
  return phien.dang_tao_ban_nhap || props.phienDangTao.has(phien.id)
}

function moPhien(id) {
  return router.push({ name: props.trangChiTiet, query: { phien: id } })
}

function coTheXoa(phien) {
  return ['thu_thap', 'cho_duyet', 'yeu_cau_bo_sung'].includes(phien.trang_thai)
}

async function xoaPhien(phien) {
  if (phienDangXoa.value !== null || dangDuyetNhieu.value || !coTheXoa(phien) || dangTaoBanNhap(phien)) return
  phienDangXoa.value = phien.id
  try {
    try {
      await ElMessageBox.confirm(
        `Xóa phiên #${phien.id} của ${phien.ma_truong} năm ${phien.nam_tuyen_sinh}? Nguồn đã lưu, các bản nháp và lịch sử xử lý của phiên cũng sẽ bị xóa.`,
        'Xác nhận xóa phiên',
        { type: 'warning', confirmButtonText: 'Xóa phiên', cancelButtonText: 'Hủy', confirmButtonClass: 'el-button--danger' },
      )
    } catch {
      return
    }
    await xoaPhienTuyenSinh(phien.id)
    ElMessage.success(`Đã xóa phiên #${phien.id}.`)
    await taiDanhSach()
  } catch (error) {
    const ketQua = loiPhien(error)
    if (ketQua.trangThai === 409) await taiDanhSach()
    loi.value = ketQua.noiDung
  } finally {
    phienDangXoa.value = null
  }
}

onMounted(taiDanhSach)
</script>

<style scoped>
.loc-phien { margin-bottom: 16px; }
.toolbar { flex-wrap: wrap; }
.trang-thai-phien { display: grid; justify-items: start; gap: 4px; }
</style>
