<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Tìm tên cấu hình, mô tả"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect
        v-model="filters.kieu_tra_loi"
        class="filter-status"
        placeholder="Kiểu trả lời"
        clearable
        @change="onSearch"
      >
        <CustomOption v-for="item in KIEU_TRA_LOI" :key="item.value" :label="item.label" :value="item.value" />
      </CustomSelect>
      <CustomSelect
        v-model="filters.trang_thai"
        class="filter-status"
        placeholder="Trạng thái"
        clearable
        @change="onSearch"
      >
        <CustomOption label="Hoạt động" :value="1" />
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
      <h2 class="toolbar__title">Danh sách cấu hình EndUser</h2>
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
      <CustomTableColumn type="selection" width="48" reserve-selection align="center" />
      <CustomTableColumn label="STT" width="72" align="center">
        <template #default="{ $index }">{{ rowIndex($index) }}</template>
      </CustomTableColumn>
      <CustomTableColumn prop="id" label="ID" width="80" align="center" />
      <CustomTableColumn prop="ten_cau_hinh" label="Tên cấu hình" min-width="200" />
      <CustomTableColumn label="Kiểu trả lời" width="130" align="center">
        <template #default="{ row }">
          <CustomTag :type="row.kieu_tra_loi === 'tinh_huong' ? 'warning' : 'primary'" effect="light">
            {{ kieuTraLoiLabel(row.kieu_tra_loi) }}
          </CustomTag>
        </template>
      </CustomTableColumn>
      <CustomTableColumn prop="mo_ta" label="Mô tả" min-width="200">
        <template #default="{ row }">{{ row.mo_ta || '—' }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Trạng thái" width="150" align="center">
        <template #default="{ row }">
          <CustomSwitch
            :model-value="row.trang_thai"
            :active-value="1"
            :inactive-value="0"
            active-text="Hoạt động"
            inactive-text="Ngừng"
            :loading="!!dangDoiTrangThai[row.id]"
            :before-change="() => doiTrangThai(row)"
            :aria-label="`Trạng thái ${row.ten_cau_hinh}`"
          />
        </template>
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
        <CustomEmpty description="Chưa có cấu hình EndUser nào." />
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
    :title="editingId ? 'Cập nhật cấu hình EndUser' : 'Thêm cấu hình EndUser'"
    width="820px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomForm ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol :span="10" :xs="24">
          <CustomFormItem label="Tên cấu hình" prop="ten_cau_hinh">
            <CustomInput v-model="form.ten_cau_hinh" maxlength="255" placeholder="Ví dụ: banner_trang_chu" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="7" :xs="12">
          <CustomFormItem label="Kiểu trả lời" prop="kieu_tra_loi">
            <CustomSelect v-model="form.kieu_tra_loi" :clearable="false" style="width: 100%">
              <CustomOption v-for="item in KIEU_TRA_LOI" :key="item.value" :label="item.label" :value="item.value" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="7" :xs="12">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" :clearable="false" style="width: 100%">
              <CustomOption label="Hoạt động" :value="1" />
              <CustomOption label="Ngừng sử dụng" :value="0" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Mô tả" prop="mo_ta">
            <CustomInput
              v-model="form.mo_ta"
              type="textarea"
              :rows="3"
              maxlength="2000"
              show-word-limit
              placeholder="Cấu hình này dùng ở đâu, có ý nghĩa gì…"
            />
          </CustomFormItem>
        </CustomCol>
      </CustomRow>
    </CustomForm>
    <template #footer>
      <CustomButton @click="dialogVisible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" @click="onSubmit">Lưu</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createCauHinhEnduser,
  deleteCauHinhEnduser,
  deleteCauHinhEnduserMany,
  fetchCauHinhEnduser,
  updateCauHinhEnduser,
  updateTrangThaiCauHinhEnduser,
} from '@/api/cauHinhEnduser'

const KIEU_TRA_LOI = [
  { value: 'diem_so', label: 'Điểm số' },
  { value: 'tinh_huong', label: 'Tình huống' },
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

const filters = reactive(emptyFilters())

function emptyFilters() {
  return {
    q: '',
    kieu_tra_loi: '',
    trang_thai: '',
  }
}

const form = reactive(emptyForm())

const rules = {
  ten_cau_hinh: [{ required: true, message: 'Vui lòng nhập tên cấu hình', trigger: 'blur' }],
  kieu_tra_loi: [{ required: true, message: 'Vui lòng chọn kiểu trả lời', trigger: 'change' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ten_cau_hinh: '',
    kieu_tra_loi: 'diem_so',
    mo_ta: '',
    trang_thai: 1,
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  formRef.value?.clearValidate()
}

function kieuTraLoiLabel(value) {
  return KIEU_TRA_LOI.find((item) => item.value === value)?.label || value || '—'
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.kieu_tra_loi) params.kieu_tra_loi = filters.kieu_tra_loi
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchCauHinhEnduser(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách cấu hình EndUser'))
  } finally {
    loading.value = false
  }
}

// before-change của switch: gọi API trước và tự gán trạng thái từ kết quả trả về,
// nên luôn trả false để switch không tự lật (lỗi thì giữ nguyên trạng thái cũ).
async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    const data = await updateTrangThaiCauHinhEnduser(row.id, moi)
    row.trang_thai = data.trang_thai
    ElMessage.success(moi === 1 ? `Đã bật "${row.ten_cau_hinh}"` : `Đã tắt "${row.ten_cau_hinh}"`)
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
  Object.assign(form, {
    ten_cau_hinh: row.ten_cau_hinh,
    kieu_tra_loi: row.kieu_tra_loi || 'diem_so',
    mo_ta: row.mo_ta || '',
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ten_cau_hinh: form.ten_cau_hinh.trim(),
    kieu_tra_loi: form.kieu_tra_loi,
    mo_ta: form.mo_ta?.trim() || null,
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
      await updateCauHinhEnduser(editingId.value, payload)
      ElMessage.success('Đã cập nhật cấu hình EndUser')
    } else {
      await createCauHinhEnduser(payload)
      ElMessage.success('Đã thêm cấu hình EndUser')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được cấu hình EndUser'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`Xóa cấu hình "${row.ten_cau_hinh}"?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  try {
    await deleteCauHinhEnduser(row.id)
    ElMessage.success('Đã xóa cấu hình EndUser')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được cấu hình EndUser'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} cấu hình đã chọn?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteCauHinhEnduserMany(ids)
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
.filter-status {
  width: 170px;
}

@media (max-width: 640px) {
  .filter-status {
    width: 100%;
  }
}
</style>
