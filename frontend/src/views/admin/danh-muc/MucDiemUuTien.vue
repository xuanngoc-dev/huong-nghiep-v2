<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, căn cứ"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect v-model="filters.loai" class="filter-status" placeholder="Chọn loại" clearable @change="onSearch">
          <CustomOption v-for="(nhan, ma) in LOAI" :key="ma" :label="nhan" :value="ma" />
        </CustomSelect>
        <CustomInputNumber
          v-model="filters.nam"
          class="filter-status"
          :min="2000"
          :max="2100"
          :controls="false"
          placeholder="Áp dụng cho năm"
          @change="onSearch"
        />
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Mức điểm ưu tiên theo năm</h2>
        <div class="toolbar__actions">
          <CustomBadge :value="selectedRows.length" :hidden="!selectedRows.length" type="danger">
            <CustomButton type="danger" plain :disabled="!selectedRows.length" :loading="deleting" @click="onDeleteSelected">
              <CustomIcon><Delete /></CustomIcon>
              Xóa
            </CustomButton>
          </CustomBadge>
          <CustomButton type="primary" @click="openCreate">
            <CustomIcon><Plus /></CustomIcon>
            Thêm mức điểm
          </CustomButton>
        </div>
      </div>
      <p class="muc-diem__ghi-chu">
        Bộ tính xét tuyển lấy mức điểm khớp năm tuyển sinh. Mã không có mức nào khớp dùng điểm cộng trong danh mục
        Khu vực ưu tiên / Đối tượng ưu tiên.
      </p>

      <CustomTable
        ref="tableRef"
        :loading="loading"
        :data="rows"
        row-key="id"
        stripe
        border
        @selection-change="onSelectionChange"
      >
        <CustomTableColumn type="selection" width="48" reserve-selection align="center" />
        <CustomTableColumn label="Loại" width="120">
          <template #default="{ row }">{{ LOAI[row.loai] }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mã" min-width="200">
          <template #default="{ row }">{{ row.ma }}<span v-if="row.ten"> — {{ row.ten }}</span></template>
        </CustomTableColumn>
        <CustomTableColumn label="Áp dụng" width="140" align="center">
          <template #default="{ row }">{{ row.nam_ap_dung_tu }} – {{ row.nam_ap_dung_den || 'nay' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Điểm cộng" width="110" align="right">
          <template #default="{ row }">{{ formatScore(row.diem_cong) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="can_cu" label="Căn cứ" min-width="200">
          <template #default="{ row }">{{ row.can_cu || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <CustomTooltip content="Sửa" placement="top">
                <CustomButton link type="primary" aria-label="Sửa" @click="openEdit(row)">
                  <CustomIcon><Edit /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Xóa" placement="top">
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có mức điểm theo năm; bộ tính đang dùng điểm cộng của danh mục." />
        </template>
      </CustomTable>

      <div class="pager">
        <CustomPagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="load"
          @size-change="onSearch"
        />
      </div>
    </CustomCard>
  </div>

  <CustomDialog
    v-model="dialogVisible"
    :title="editingId ? 'Cập nhật mức điểm ưu tiên' : 'Thêm mức điểm ưu tiên'"
    width="800px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomForm ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem label="Loại" prop="loai">
          <CustomSelect v-model="form.loai" :clearable="false" placeholder="Chọn loại" @change="form.ma = ''">
            <CustomOption v-for="(nhan, ma) in LOAI" :key="ma" :label="nhan" :value="ma" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Mã ưu tiên" prop="ma">
          <CustomSelect v-model="form.ma" filterable placeholder="Chọn mã ưu tiên">
            <CustomOption v-for="m in luaChonMa" :key="m.ma" :label="`${m.ma} — ${m.ten} (${formatScore(m.diem)})`" :value="m.ma" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Điểm cộng" prop="diem_cong">
          <CustomInputNumber
            v-model="form.diem_cong"
            placeholder="Nhập điểm cộng"
            :min="0"
            :max="10"
            :step="0.25"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Áp dụng từ năm" prop="nam_ap_dung_tu">
          <CustomInputNumber v-model="form.nam_ap_dung_tu" :min="2000" :max="2100" :controls="false" placeholder="Nhập năm áp dụng từ" />
        </CustomFormItem>
        <CustomFormItem label="Áp dụng đến năm" prop="nam_ap_dung_den">
          <CustomInputNumber v-model="form.nam_ap_dung_den" :min="2000" :max="2100" :controls="false" placeholder="Để trống = đến nay" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Căn cứ" prop="can_cu">
          <CustomInput v-model="form.can_cu" maxlength="255" placeholder="Ví dụ: Thông tư 06/2026/TT-BGDĐT" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput v-model="form.ghi_chu" type="textarea" :rows="3" maxlength="2000" placeholder="Nhập ghi chú" />
        </CustomFormItem>
      </div>
    </CustomForm>
    <template #footer>
      <CustomButton @click="dialogVisible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" @click="onSubmit">Lưu</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/** Mức điểm cộng khu vực / đối tượng ưu tiên theo năm tuyển sinh (bước 5.1). */
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchDoiTuongUuTien } from '@/api/doiTuongUuTien'
import { fetchKhuVucUuTien } from '@/api/khuVucUuTien'
import {
  createMucDiemUuTien,
  deleteMucDiemUuTien,
  deleteMucDiemUuTienMany,
  fetchMucDiemUuTien,
  updateMucDiemUuTien,
} from '@/api/mucDiemUuTien'

const LOAI = { KHU_VUC: 'Khu vực', DOI_TUONG: 'Đối tượng' }

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const rows = ref([])
const selectedRows = ref([])
const tableRef = ref()
const formRef = ref()
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingId = ref(null)
const danhMuc = reactive({ KHU_VUC: [], DOI_TUONG: [] })
const filters = reactive({ q: '', loai: '', nam: null })
const form = reactive(emptyForm())

const luaChonMa = computed(() => danhMuc[form.loai] || [])

const rules = {
  loai: [{ required: true, message: 'Vui lòng chọn loại', trigger: 'change' }],
  ma: [{ required: true, message: 'Vui lòng chọn mã ưu tiên', trigger: 'change' }],
  diem_cong: [{ required: true, message: 'Vui lòng nhập điểm cộng', trigger: 'change' }],
  nam_ap_dung_tu: [{ required: true, message: 'Vui lòng nhập năm áp dụng từ', trigger: 'change' }],
}

function emptyForm() {
  return {
    loai: 'DOI_TUONG',
    ma: '',
    diem_cong: null,
    nam_ap_dung_tu: new Date().getFullYear(),
    nam_ap_dung_den: null,
    can_cu: '',
    ghi_chu: '',
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  formRef.value?.clearValidate()
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function formatScore(value) {
  if (value === null || value === undefined || value === '') return '—'
  return Number(value).toLocaleString('vi-VN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.loai) params.loai = filters.loai
    if (filters.nam) params.nam = filters.nam
    const data = await fetchMucDiemUuTien(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được mức điểm ưu tiên'))
  } finally {
    loading.value = false
  }
}

async function loadDanhMuc() {
  try {
    const [kv, dt] = await Promise.all([
      fetchKhuVucUuTien({ page: 1, page_size: 1000 }),
      fetchDoiTuongUuTien({ page: 1, page_size: 1000 }),
    ])
    danhMuc.KHU_VUC = kv.items.map((x) => ({ ma: x.ma_khu_vuc, ten: x.ten_khu_vuc, diem: x.diem_cong }))
    danhMuc.DOI_TUONG = dt.items.map((x) => ({ ma: x.ma_doi_tuong, ten: x.ten_doi_tuong, diem: x.diem_cong }))
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh mục ưu tiên'))
  }
}

function clearSelection() {
  selectedRows.value = []
  tableRef.value?.clearSelection()
}

function onSelectionChange(selection) {
  selectedRows.value = selection
}

function onSearch() {
  clearSelection()
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
  Object.assign(form, {
    loai: row.loai,
    ma: row.ma,
    diem_cong: row.diem_cong,
    nam_ap_dung_tu: row.nam_ap_dung_tu,
    nam_ap_dung_den: row.nam_ap_dung_den,
    can_cu: row.can_cu || '',
    ghi_chu: row.ghi_chu || '',
  })
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = {
      ...form,
      nam_ap_dung_den: form.nam_ap_dung_den || null,
      can_cu: form.can_cu?.trim() || null,
      ghi_chu: form.ghi_chu?.trim() || null,
    }
    if (editingId.value) {
      await updateMucDiemUuTien(editingId.value, payload)
      ElMessage.success('Đã cập nhật mức điểm ưu tiên')
    } else {
      await createMucDiemUuTien(payload)
      ElMessage.success('Đã thêm mức điểm ưu tiên')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được mức điểm ưu tiên'))
  } finally {
    saving.value = false
  }
}

async function xacNhan(noiDung) {
  try {
    await ElMessageBox.confirm(noiDung, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
    return true
  } catch {
    return false
  }
}

async function onDelete(row) {
  if (!(await xacNhan(`Xóa mức điểm ${row.ma} áp dụng ${row.nam_ap_dung_tu} – ${row.nam_ap_dung_den || 'nay'}?`))) return
  try {
    await deleteMucDiemUuTien(row.id)
    ElMessage.success('Đã xóa mức điểm ưu tiên')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) page.value -= 1
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được mức điểm ưu tiên'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length || !(await xacNhan(`Xóa ${ids.length} mức điểm ưu tiên đã chọn?`))) return
  deleting.value = true
  try {
    const result = await deleteMucDiemUuTienMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} mức điểm ưu tiên`)
    clearSelection()
    if (ids.length >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các mức điểm đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  load()
  loadDanhMuc()
})
</script>

<style scoped>
.muc-diem__ghi-chu {
  margin: 0 0 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
