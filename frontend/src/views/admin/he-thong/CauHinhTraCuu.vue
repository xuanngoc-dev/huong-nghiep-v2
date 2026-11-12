<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomSelect
        v-model="filters.trang_thai"
        class="filter-status"
        placeholder="Trạng thái"
        clearable
        @change="onSearch"
      >
        <CustomOption label="Đang áp dụng" :value="1" />
        <CustomOption label="Ngừng sử dụng" :value="0" />
      </CustomSelect>
      <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      <CustomButton @click="onResetFilters">
        <CustomIcon><RefreshLeft /></CustomIcon>
        <span>Đặt lại</span>
      </CustomButton>
    </div>
  </CustomCard>

  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar">
      <h2 class="toolbar__title">Danh sách cấu hình tra cứu</h2>
      <div class="toolbar__actions">
        <CustomBadge :value="selectedRows.length" :hidden="!selectedRows.length" type="danger">
          <CustomButton
            type="danger"
            plain
            :disabled="!selectedRows.length"
            :loading="deleting"
            @click="onDeleteSelected"
          >
            <CustomIcon><Delete /></CustomIcon>
            Xóa
          </CustomButton>
        </CustomBadge>
        <CustomButton type="primary" @click="openCreate">
          <CustomIcon><Plus /></CustomIcon>
          Thêm cấu hình
        </CustomButton>
      </div>
    </div>
    <CustomTable
      ref="tableRef"
      :loading="loading"
      :data="rows"
      row-key="id"
      stripe
      border
      @selection-change="onSelectionChange"
    >
      <CustomTableColumn type="selection" width="48" reserve-selection align="center" :selectable="coTheXoa" />
      <CustomTableColumn label="STT" width="72" align="center">
        <template #default="{ $index }">{{ rowIndex($index) }}</template>
      </CustomTableColumn>
      <CustomTableColumn
        v-for="item in TRUONG_LUOT"
        :key="item.prop"
        :label="item.cot"
        :min-width="item.rong"
        align="center"
      >
        <template #default="{ row }">
          <CustomInputNumber
            v-if="dangSua(row, item.prop)"
            v-model="giaTriSua"
            class="o-sua"
            size="small"
            :min="0"
            :max="LUOT_TOI_DA"
            :precision="0"
            :disabled="dangLuuO"
            controls-position="right"
            @keydown.enter.prevent="luuO(row)"
            @keydown.esc.prevent="huySua"
            @blur="luuO(row)"
          />
          <span
            v-else
            class="o-gia-tri"
            tabindex="0"
            title="Nhấp đúp để sửa"
            @dblclick="batDauSua(row, item.prop)"
            @keydown.enter="batDauSua(row, item.prop)"
          >
            {{ hienSo(row[item.prop]) }} lượt / ngày
          </span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn v-for="item in TRUONG_BAT_TAT" :key="item.prop" :label="item.cot" :width="item.rong" align="center">
        <template #default="{ row }">
          <CustomTag
            class="o-gia-tri"
            :type="row[item.prop] ? 'success' : 'info'"
            size="small"
            tabindex="0"
            title="Nhấp đúp để bật/tắt"
            @dblclick="doiBatTat(row, item)"
            @keydown.enter="doiBatTat(row, item)"
          >
            {{ row[item.prop] ? 'Bật' : 'Tắt' }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <!-- <CustomTableColumn label="Giá báo cáo chuyên sâu" min-width="160" align="right">
        <template #default="{ row }">{{ hienGia(row.gia_bao_cao_chuyen_sau) }}</template>
      </CustomTableColumn> -->
      <CustomTableColumn label="Trạng thái" width="170" align="center">
        <template #default="{ row }">
          <CustomTooltip :content="KHOA_AP_DUNG" placement="top" :disabled="coTheXoa(row)">
            <CustomSwitch
              :model-value="row.trang_thai"
              :active-value="1"
              :inactive-value="0"
              active-text="Áp dụng"
              inactive-text="Ngừng"
              :disabled="!coTheXoa(row)"
              :loading="!!dangDoiTrangThai[row.id]"
              :before-change="() => doiTrangThai(row)"
              :aria-label="`Trạng thái cấu hình ${row.id}`"
            />
          </CustomTooltip>
        </template>
      </CustomTableColumn>
      <!-- <CustomTableColumn label="Cập nhật lúc" width="160" align="center">
        <template #default="{ row }">{{ formatThoiGian(row.updated_at) }}</template>
      </CustomTableColumn> -->
      <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <CustomTooltip content="Sửa" placement="top">
              <CustomButton link type="primary" aria-label="Sửa" @click="openEdit(row)">
                <CustomIcon><Edit /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip :content="coTheXoa(row) ? 'Xóa' : 'Không thể xóa cấu hình đang áp dụng'" placement="top">
              <CustomButton link type="danger" aria-label="Xóa" :disabled="!coTheXoa(row)" @click="onDelete(row)">
                <CustomIcon><Delete /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
        </template>
      </CustomTableColumn>
      <template #empty>
        <CustomEmpty description="Chưa có cấu hình tra cứu nào." />
      </template>
    </CustomTable>

    <div class="pager">
      <CustomPagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="onPageChange"
        @size-change="onSizeChange"
      />
    </div>
  </CustomCard>
  </div>

  <CustomDialog
    v-model="dialogVisible"
    :title="editingId ? 'Cập nhật cấu hình tra cứu' : 'Thêm cấu hình tra cứu'"
    width="min(720px, 94vw)"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomForm ref="formRef" :model="form" :rules="rules" label-position="top">
      <h3 class="form-section">Hạn mức mỗi ngày</h3>
      <CustomRow :gutter="16">
        <CustomCol v-for="item in TRUONG_LUOT" :key="item.prop" :xs="24" :sm="12" :md="6">
          <CustomFormItem :label="item.nhan" :prop="item.prop">
            <CustomInputNumber
              v-model="form[item.prop]"
              :min="0"
              :max="LUOT_TOI_DA"
              :precision="0"
              controls-position="right"
              class="w-full"
            />
          </CustomFormItem>
        </CustomCol>
      </CustomRow>

      <CustomRow :gutter="16">
        <CustomCol :xs="12" :sm="8">
          <CustomFormItem label="Trắc nghiệm Holland" prop="bat_tinh_nang_holland">
            <CustomSwitch v-model="form.bat_tinh_nang_holland" active-text="Bật" inactive-text="Tắt" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :xs="12" :sm="8">
          <CustomFormItem label="Thanh toán" prop="bat_thanh_toan">
            <CustomSwitch v-model="form.bat_thanh_toan" active-text="Bật" inactive-text="Tắt" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :xs="24" :sm="8">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSwitch
              v-model="form.trang_thai"
              :active-value="1"
              :inactive-value="0"
              active-text="Áp dụng"
              inactive-text="Ngừng"
              :disabled="dangSuaBanApDung"
            />
          </CustomFormItem>
        </CustomCol>
      </CustomRow>

      <CustomRow :gutter="16" v-if='false'>
        <CustomCol :xs="24" :sm="8">
          <CustomFormItem label="Giá báo cáo chuyên sâu (VNĐ)" prop="gia_bao_cao_chuyen_sau">
            <CustomInputNumber
              v-model="form.gia_bao_cao_chuyen_sau"
              :min="0"
              :max="GIA_TOI_DA"
              :step="1000"
              :precision="0"
              :formatter="dinhDangTien"
              :parser="docTien"
              controls-position="right"
              class="w-full"
            />
          </CustomFormItem>
        </CustomCol>
      </CustomRow>
      <p v-if="dangSuaBanApDung" class="field-hint">{{ KHOA_AP_DUNG }}</p>
      <p v-else-if="form.trang_thai === 1" class="field-hint">Lưu cấu hình đang áp dụng sẽ tắt các cấu hình khác.</p>
    </CustomForm>
    <template #footer>
      <CustomButton @click="dialogVisible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" @click="onSubmit">Lưu</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createCauHinhTraCuu,
  deleteCauHinhTraCuu,
  deleteCauHinhTraCuuMany,
  fetchCauHinhTraCuu,
  updateCauHinhTraCuu,
  updateTrangThaiCauHinhTraCuu,
} from '@/api/cauHinhTraCuu'

// Khớp giới hạn ở backend.
const LUOT_TOI_DA = 10000
const GIA_TOI_DA = 999999999999999
// nhan: nhãn trong form, cot/rong: tiêu đề và độ rộng cột trong bảng.
const TRUONG_LUOT = [
  { prop: 'so_luot_tra_cuu_khach_ngay', nhan: 'Tra cứu (khách vãng lai)', cot: 'Tra cứu (khách)', rong: 150 },
  { prop: 'so_luot_tra_cuu_thanh_vien_ngay', nhan: 'Tra cứu (thành viên)', cot: 'Tra cứu (thành viên)', rong: 170 },
  { prop: 'so_luot_tu_van_ai_ngay', nhan: 'Tư vấn AI', cot: 'Tư vấn', rong: 130 },
  { prop: 'so_luot_phan_tich_truong_ngay', nhan: 'Phân tích trường', cot: 'Phân tích', rong: 150 },
]
// Luôn phải có một cấu hình đang áp dụng: không tắt hay xóa được cấu hình đó, chỉ thay bằng cách bật cấu hình khác.
const KHOA_AP_DUNG = 'Đây là cấu hình đang áp dụng. Muốn ngừng, hãy bật một cấu hình khác để thay thế.'
const TRUONG_BAT_TAT = [
  { prop: 'bat_tinh_nang_holland', cot: 'Holland', ten: 'trắc nghiệm Holland', rong: 100 },
  { prop: 'bat_thanh_toan', cot: 'Thanh toán', ten: 'thanh toán', rong: 120 },
]

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const rows = ref([])
const selectedRows = ref([])
const tableRef = ref()
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()
const dangDoiTrangThai = ref({})
const trangThaiGoc = ref(null)
const dangSuaBanApDung = computed(() => !!editingId.value && trangThaiGoc.value === 1)

function coTheXoa(row) {
  return row.trang_thai !== 1
}

const filters = reactive(emptyFilters())

function emptyFilters() {
  return {
    trang_thai: '',
  }
}

const form = reactive(emptyForm())

const batBuoc = (message) => [{ required: true, type: 'number', message, trigger: 'change' }]

const rules = {
  so_luot_tra_cuu_khach_ngay: batBuoc('Vui lòng nhập số lượt tra cứu của khách'),
  so_luot_tra_cuu_thanh_vien_ngay: batBuoc('Vui lòng nhập số lượt tra cứu của thành viên'),
  so_luot_tu_van_ai_ngay: batBuoc('Vui lòng nhập số lượt tư vấn AI'),
  so_luot_phan_tich_truong_ngay: batBuoc('Vui lòng nhập số lượt phân tích trường'),
  gia_bao_cao_chuyen_sau: batBuoc('Vui lòng nhập giá báo cáo'),
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    so_luot_tra_cuu_khach_ngay: 1,
    so_luot_tra_cuu_thanh_vien_ngay: 5,
    so_luot_tu_van_ai_ngay: 10,
    so_luot_phan_tich_truong_ngay: 3,
    bat_tinh_nang_holland: true,
    bat_thanh_toan: false,
    gia_bao_cao_chuyen_sau: 0,
    trang_thai: 1,
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  trangThaiGoc.value = null
  formRef.value?.clearValidate()
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function hienSo(value) {
  return Number(value || 0).toLocaleString('vi-VN')
}

function hienGia(value) {
  const so = Number(value || 0)
  return so ? `${so.toLocaleString('vi-VN')} đ` : 'Miễn phí'
}

function dinhDangTien(value) {
  if (value === '' || value == null) return ''
  return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

function docTien(value) {
  return String(value || '').replace(/\D/g, '')
}

function formatThoiGian(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchCauHinhTraCuu(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách cấu hình tra cứu'))
  } finally {
    loading.value = false
  }
}

// before-change của switch: gọi API trước rồi tải lại danh sách (bật một cấu hình sẽ tắt các cấu hình khác),
// nên luôn trả false để switch không tự lật.
async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    await updateTrangThaiCauHinhTraCuu(row.id, moi)
    ElMessage.success(moi === 1 ? 'Đã áp dụng cấu hình' : 'Đã ngừng cấu hình')
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái'))
  } finally {
    const { [row.id]: _bo, ...conLai } = dangDoiTrangThai.value
    dangDoiTrangThai.value = conLai
  }
  return false
}

function onResetFilters() {
  Object.assign(filters, emptyFilters())
  onSearch()
}

function clearSelection() {
  selectedRows.value = []
  tableRef.value?.clearSelection()
}

function onSelectionChange(selection) {
  selectedRows.value = selection
}

function rowIndex(index) {
  return (page.value - 1) * pageSize.value + index + 1
}

function onSearch() {
  clearSelection()
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

function onPageChange() {
  load()
}

function onSizeChange() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  trangThaiGoc.value = row.trang_thai
  Object.assign(form, {
    so_luot_tra_cuu_khach_ngay: row.so_luot_tra_cuu_khach_ngay,
    so_luot_tra_cuu_thanh_vien_ngay: row.so_luot_tra_cuu_thanh_vien_ngay,
    so_luot_tu_van_ai_ngay: row.so_luot_tu_van_ai_ngay,
    so_luot_phan_tich_truong_ngay: row.so_luot_phan_tich_truong_ngay,
    bat_tinh_nang_holland: row.bat_tinh_nang_holland,
    bat_thanh_toan: row.bat_thanh_toan,
    gia_bao_cao_chuyen_sau: Number(row.gia_bao_cao_chuyen_sau || 0),
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

// Sửa trực tiếp trên bảng: nhấp đúp ô số lượt để sửa, Enter hoặc rời ô để lưu, Esc để hủy.
const oDangSua = ref(null)
const giaTriSua = ref(null)
const dangLuuO = ref(false)

function dangSua(row, prop) {
  return oDangSua.value?.id === row.id && oDangSua.value?.prop === prop
}

function batDauSua(row, prop) {
  if (dangLuuO.value) return
  oDangSua.value = { id: row.id, prop }
  giaTriSua.value = row[prop]
  nextTick(() => {
    const input = document.querySelector('.o-sua input')
    input?.focus()
    input?.select()
  })
}

function huySua() {
  oDangSua.value = null
  giaTriSua.value = null
}

function payloadTuRow(row, thayDoi) {
  return {
    so_luot_tra_cuu_khach_ngay: row.so_luot_tra_cuu_khach_ngay,
    so_luot_tra_cuu_thanh_vien_ngay: row.so_luot_tra_cuu_thanh_vien_ngay,
    so_luot_tu_van_ai_ngay: row.so_luot_tu_van_ai_ngay,
    so_luot_phan_tich_truong_ngay: row.so_luot_phan_tich_truong_ngay,
    bat_tinh_nang_holland: row.bat_tinh_nang_holland,
    bat_thanh_toan: row.bat_thanh_toan,
    gia_bao_cao_chuyen_sau: Number(row.gia_bao_cao_chuyen_sau || 0),
    trang_thai: row.trang_thai,
    ...thayDoi,
  }
}

async function luuO(row) {
  const o = oDangSua.value
  // Enter rồi blur gọi hai lần, lần sau bỏ qua.
  if (!o || o.id !== row.id || dangLuuO.value) return
  const moi = giaTriSua.value
  if (moi == null || moi === row[o.prop]) {
    huySua()
    return
  }
  dangLuuO.value = true
  try {
    const data = await updateCauHinhTraCuu(row.id, payloadTuRow(row, { [o.prop]: moi }))
    Object.assign(row, data)
    ElMessage.success('Đã cập nhật')
    huySua()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được giá trị'))
  } finally {
    dangLuuO.value = false
  }
}

async function doiBatTat(row, item) {
  if (dangLuuO.value) return
  const moi = !row[item.prop]
  dangLuuO.value = true
  try {
    const data = await updateCauHinhTraCuu(row.id, payloadTuRow(row, { [item.prop]: moi }))
    Object.assign(row, data)
    ElMessage.success(`Đã ${moi ? 'bật' : 'tắt'} ${item.ten}`)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được giá trị'))
  } finally {
    dangLuuO.value = false
  }
}

function payloadFromForm() {
  return {
    so_luot_tra_cuu_khach_ngay: form.so_luot_tra_cuu_khach_ngay,
    so_luot_tra_cuu_thanh_vien_ngay: form.so_luot_tra_cuu_thanh_vien_ngay,
    so_luot_tu_van_ai_ngay: form.so_luot_tu_van_ai_ngay,
    so_luot_phan_tich_truong_ngay: form.so_luot_phan_tich_truong_ngay,
    bat_tinh_nang_holland: form.bat_tinh_nang_holland,
    bat_thanh_toan: form.bat_thanh_toan,
    gia_bao_cao_chuyen_sau: form.gia_bao_cao_chuyen_sau ?? 0,
    trang_thai: form.trang_thai,
  }
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = payloadFromForm()
    if (editingId.value) {
      await updateCauHinhTraCuu(editingId.value, payload)
      ElMessage.success('Đã cập nhật cấu hình tra cứu')
    } else {
      await createCauHinhTraCuu(payload)
      ElMessage.success('Đã thêm cấu hình tra cứu')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được cấu hình tra cứu'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  if (!coTheXoa(row)) return
  try {
    await ElMessageBox.confirm('Xóa cấu hình này?', 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  try {
    await deleteCauHinhTraCuu(row.id)
    ElMessage.success('Đã xóa cấu hình tra cứu')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được cấu hình tra cứu'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return
  // Cấu hình được chọn trước rồi mới bật áp dụng vẫn còn trong danh sách chọn.
  if (selectedRows.value.some((row) => !coTheXoa(row))) {
    ElMessage.warning('Không thể xóa cấu hình đang áp dụng, hãy bỏ chọn cấu hình đó.')
    return
  }

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} cấu hình đã chọn?`,
      'Xác nhận xóa',
      {
        type: 'warning',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy',
        confirmButtonClass: 'el-button--danger',
      },
    )
  } catch {
    return
  }

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteCauHinhTraCuuMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} cấu hình`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các cấu hình đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.o-gia-tri {
  display: inline-block;
  min-width: 60px;
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
}

span.o-gia-tri:hover,
span.o-gia-tri:focus-visible {
  background: var(--el-fill-color-light);
  outline: 1px dashed var(--el-border-color);
}

.o-sua {
  width: 100%;
}

.config-hint {
  margin: -4px 0 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.form-section {
  margin: 0 0 10px;
  color: var(--el-text-color-primary);
  font-size: 14px;
  font-weight: 600;
}

.form-section:not(:first-child) {
  margin-top: 6px;
}

.w-full {
  width: 100%;
}
</style>
