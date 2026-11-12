<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="filters">
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm họ tên, email hoặc số điện thoại"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.vai_tro"
          class="filter-status"
          placeholder="Vai trò"
          clearable
          @change="onSearch"
        >
          <CustomOption label="Người dùng" :value="0" />
          <CustomOption label="Quản trị" :value="1" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.trang_thai"
          class="filter-status"
          placeholder="Trạng thái"
          clearable
          @change="onSearch"
        >
          <CustomOption label="Hoạt động" :value="1" />
          <CustomOption label="Khóa" :value="0" />
        </CustomSelect>
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách tài khoản</h2>
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
            Thêm tài khoản
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
        <CustomTableColumn prop="ho_ten" label="Họ tên" min-width="160" />
        <CustomTableColumn prop="email" label="Email" min-width="200" />
        <CustomTableColumn prop="so_dien_thoai" label="Số điện thoại" width="140">
          <template #default="{ row }">{{ row.so_dien_thoai || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Vai trò" width="120" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.vai_tro === 1 ? 'warning' : 'info'" effect="light">
              {{ roleLabel(row.vai_tro) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Trạng thái" width="130" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.trang_thai === 1 ? 'success' : 'danger'" effect="light">
              {{ statusLabel(row.trang_thai) }}
            </CustomTag>
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
          <CustomEmpty description="Chưa có tài khoản nào." />
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
    :title="editingId ? 'Cập nhật tài khoản' : 'Thêm tài khoản'"
    width="640px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomForm ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Họ tên" prop="ho_ten">
            <CustomInput v-model="form.ho_ten" maxlength="150" placeholder="Họ và tên" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Email" prop="email">
            <CustomInput v-model="form.email" maxlength="255" placeholder="email@example.com" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Số điện thoại" prop="so_dien_thoai">
            <CustomInput v-model="form.so_dien_thoai" maxlength="20" placeholder="Số điện thoại" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem
            :label="editingId ? 'Mật khẩu mới (để trống nếu giữ nguyên)' : 'Mật khẩu'"
            prop="mat_khau"
          >
            <CustomInput
              v-model="form.mat_khau"
              type="password"
              show-password
              maxlength="128"
              :placeholder="editingId ? 'Để trống nếu không đổi' : 'Tối thiểu 6 ký tự'"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Vai trò" prop="vai_tro">
            <CustomSelect v-model="form.vai_tro" :clearable="false" style="width: 100%">
              <CustomOption label="Người dùng" :value="0" />
              <CustomOption label="Quản trị" :value="1" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" :clearable="false" style="width: 100%">
              <CustomOption label="Hoạt động" :value="1" />
              <CustomOption label="Khóa" :value="0" />
            </CustomSelect>
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
  createNguoiDung,
  deleteNguoiDung,
  deleteNguoiDungMany,
  fetchNguoiDung,
  updateNguoiDung,
} from '@/api/nguoiDung'

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

const filters = reactive({
  q: '',
  vai_tro: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

const rules = {
  ho_ten: [{ required: true, message: 'Vui lòng nhập họ tên', trigger: 'blur' }],
  email: [
    { required: true, message: 'Vui lòng nhập email', trigger: 'blur' },
    { type: 'email', message: 'Email không hợp lệ', trigger: ['blur', 'change'] },
  ],
  mat_khau: [
    {
      validator: (_rule, value, callback) => {
        if (!editingId.value && (!value || !String(value).trim())) {
          callback(new Error('Vui lòng nhập mật khẩu'))
          return
        }
        if (value && String(value).trim().length < 6) {
          callback(new Error('Mật khẩu phải có ít nhất 6 ký tự'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  vai_tro: [{ required: true, message: 'Vui lòng chọn vai trò', trigger: 'change' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ho_ten: '',
    email: '',
    so_dien_thoai: '',
    mat_khau: '',
    vai_tro: 0,
    trang_thai: 1,
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

function roleLabel(value) {
  return value === 1 ? 'Quản trị' : 'Người dùng'
}

function statusLabel(value) {
  return value === 1 ? 'Hoạt động' : 'Khóa'
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.vai_tro !== '' && filters.vai_tro !== null) params.vai_tro = filters.vai_tro
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchNguoiDung(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách tài khoản'))
  } finally {
    loading.value = false
  }
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
    ho_ten: row.ho_ten,
    email: row.email,
    so_dien_thoai: row.so_dien_thoai || '',
    mat_khau: '',
    vai_tro: row.vai_tro,
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  const payload = {
    ho_ten: form.ho_ten.trim(),
    email: form.email.trim().toLowerCase(),
    so_dien_thoai: form.so_dien_thoai?.trim() || null,
    vai_tro: form.vai_tro,
    trang_thai: form.trang_thai,
  }
  const password = form.mat_khau?.trim()
  if (!editingId.value) {
    payload.mat_khau = password
  } else if (password) {
    payload.mat_khau = password
  } else {
    payload.mat_khau = null
  }
  return payload
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = payloadFromForm()
    if (editingId.value) {
      await updateNguoiDung(editingId.value, payload)
      ElMessage.success('Đã cập nhật tài khoản')
    } else {
      await createNguoiDung(payload)
      ElMessage.success('Đã thêm tài khoản')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được tài khoản'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa tài khoản "${row.ho_ten}" (${row.email})?`,
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

  try {
    await deleteNguoiDung(row.id)
    ElMessage.success('Đã xóa tài khoản')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được tài khoản'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} tài khoản đã chọn?`,
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
    const result = await deleteNguoiDungMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} tài khoản`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các tài khoản đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.filter-status {
  width: 150px;
}

@media (max-width: 640px) {
  .filter-status {
    width: 100%;
  }
}
</style>
