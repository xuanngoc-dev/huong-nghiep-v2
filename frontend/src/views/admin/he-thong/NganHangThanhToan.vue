<template>
  <div class="catalog-page">
  <CustomCard shadow="never" class="catalog-card">
    <div class="filters">
      <CustomInput
        v-model="filters.q"
        class="filter-search"
        placeholder="Tìm ngân hàng, số tài khoản, chủ tài khoản"
        clearable
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <CustomIcon><Search /></CustomIcon>
        </template>
      </CustomInput>
      <CustomSelect
        v-model="filters.ngan_hang"
        class="filter-bank"
        placeholder="Ngân hàng"
        filterable
        clearable
        @change="onSearch"
      >
        <CustomOption
          v-for="item in nganHangOptions"
          :key="item.ten_ngan_hang_viet_tat"
          :label="item.ten_ngan_hang_viet_tat"
          :value="item.ten_ngan_hang_viet_tat"
        >
          <span class="bank-option">
            <strong>{{ item.ten_ngan_hang_viet_tat }}</strong>
            <small>{{ item.ten_ngan_hang }}</small>
          </span>
        </CustomOption>
      </CustomSelect>
      <CustomSelect
        v-model="filters.co_logo"
        class="filter-logo"
        placeholder="Logo"
        clearable
        @change="onSearch"
      >
        <CustomOption label="Đã có logo" :value="true" />
        <CustomOption label="Chưa có logo" :value="false" />
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
      <h2 class="toolbar__title">Danh sách ngân hàng thanh toán</h2>
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
          Thêm ngân hàng
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
      <CustomTableColumn label="Logo" width="96" align="center">
        <template #default="{ row }">
          <img
            v-if="row.logo_ngan_hang"
            class="bank-logo"
            :src="apiAssetUrl(row.logo_ngan_hang)"
            :alt="`Logo ${row.ten_ngan_hang_viet_tat}`"
          />
          <span v-else class="bank-logo bank-logo--text">{{ row.ten_ngan_hang_viet_tat.slice(0, 4) }}</span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Ngân hàng" min-width="260">
        <template #default="{ row }">
          <div class="bank-name">
            <strong>{{ row.ten_ngan_hang_viet_tat }}</strong>
            <span>{{ row.ten_ngan_hang }}</span>
            <small v-if="row.ten_ngan_hang_tieng_anh">{{ row.ten_ngan_hang_tieng_anh }}</small>
          </div>
        </template>
      </CustomTableColumn>
      <CustomTableColumn label="Số tài khoản" min-width="170">
        <template #default="{ row }">
          <span class="account-no">
            <span>{{ row.so_tai_khoan }}</span>
            <CustomTooltip content="Sao chép" placement="top">
              <CustomButton link type="primary" aria-label="Sao chép số tài khoản" @click="copySoTaiKhoan(row)">
                <CustomIcon><CopyDocument /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </span>
        </template>
      </CustomTableColumn>
      <CustomTableColumn prop="chu_tai_khoan" label="Chủ tài khoản" min-width="180" />
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
            :aria-label="`Trạng thái ${row.ten_ngan_hang_viet_tat} ${row.so_tai_khoan}`"
          />
        </template>
      </CustomTableColumn>
      <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="200">
        <template #default="{ row }">{{ row.ghi_chu || '—' }}</template>
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
        <CustomEmpty description="Chưa có ngân hàng thanh toán nào." />
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
    :title="editingId ? 'Cập nhật ngân hàng thanh toán' : 'Thêm ngân hàng thanh toán'"
    width="760px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomForm ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomFormItem label="Logo ngân hàng" prop="logo_ngan_hang" class="logo-field">
        <div class="logo-box" v-loading="dangTaiLogo">
          <div class="logo-preview" aria-label="Xem trước logo">
            <img
              v-if="form.logo_ngan_hang && !logoLoi"
              :src="apiAssetUrl(form.logo_ngan_hang)"
              alt="Xem trước logo"
              @error="logoLoi = true"
            />
            <span v-else>{{ logoLoi ? 'Không tải được ảnh' : 'Chưa có logo' }}</span>
          </div>
          <div class="logo-box__input">
            <CustomInput
              v-model="form.logo_ngan_hang"
              maxlength="500"
              placeholder="Dán URL logo, ví dụ https://…/vcb.png"
              clearable
              @input="logoLoi = false"
            />
            <div class="logo-box__actions">
              <CustomButton type="primary" plain :loading="dangTaiLogo" @click="chonFileLogo">
                <CustomIcon><Upload /></CustomIcon>
                <span>Chọn file</span>
              </CustomButton>
              <CustomButton v-if="form.logo_ngan_hang" link type="danger" @click="xoaLogo">Bỏ logo</CustomButton>
              <span class="logo-box__hint">PNG, JPG, WEBP hoặc GIF, tối đa {{ LOGO_TOI_DA_MB }}MB.</span>
            </div>
            <input
              ref="logoInput"
              type="file"
              :accept="LOGO_LOAI.join(',')"
              hidden
              @change="onChonLogo"
            />
          </div>
        </div>
      </CustomFormItem>

      <CustomRow :gutter="16">
        <CustomCol :span="8" :xs="12">
          <CustomFormItem label="Tên viết tắt" prop="ten_ngan_hang_viet_tat">
            <CustomInput v-model="form.ten_ngan_hang_viet_tat" maxlength="50" placeholder="Ví dụ: VCB" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="12">
          <CustomFormItem label="Tên ngân hàng" prop="ten_ngan_hang">
            <CustomInput
              v-model="form.ten_ngan_hang"
              maxlength="255"
              placeholder="Ví dụ: Ngân hàng TMCP Ngoại thương Việt Nam"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="12">
          <CustomFormItem label="Tên tiếng Anh" prop="ten_ngan_hang_tieng_anh">
            <CustomInput v-model="form.ten_ngan_hang_tieng_anh" maxlength="255" placeholder="Ví dụ: Vietcombank" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="12">
          <CustomFormItem label="Số tài khoản" prop="so_tai_khoan">
            <CustomInput v-model="form.so_tai_khoan" maxlength="60" placeholder="Ví dụ: 0123456789" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="12">
          <CustomFormItem label="Chủ tài khoản" prop="chu_tai_khoan">
            <CustomInput v-model="form.chu_tai_khoan" maxlength="255" placeholder="Ví dụ: CONG TY CP DTS" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="8" :xs="12">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" :clearable="false" style="width: 100%">
              <CustomOption label="Hoạt động" :value="1" />
              <CustomOption label="Ngừng sử dụng" :value="0" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Ghi chú" prop="ghi_chu">
            <CustomInput
              v-model="form.ghi_chu"
              type="textarea"
              :rows="3"
              maxlength="2000"
              show-word-limit
              placeholder="Ví dụ: chi nhánh, nội dung chuyển khoản…"
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
import { apiAssetUrl } from '@/api/apiUrl'
import {
  createNganHangThanhToan,
  deleteNganHangThanhToan,
  deleteNganHangThanhToanMany,
  fetchLuaChonNganHang,
  fetchNganHangThanhToan,
  updateNganHangThanhToan,
  updateTrangThaiNganHangThanhToan,
} from '@/api/nganHangThanhToan'
import { createThuMuc, uploadThuVien } from '@/api/thuVien'

// Logo tải lên được lưu trong thư mục này của Thư viện.
const THU_MUC_LOGO = 'ngan-hang'
const LOGO_TOI_DA_MB = 2
const LOGO_LOAI = ['image/png', 'image/jpeg', 'image/webp', 'image/gif']

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
const logoLoi = ref(false)
const logoInput = ref()
const dangTaiLogo = ref(false)

const nganHangOptions = ref([])
const dangDoiTrangThai = ref({})

const filters = reactive(emptyFilters())

function emptyFilters() {
  return {
    q: '',
    ngan_hang: '',
    co_logo: '',
    trang_thai: '',
  }
}

const form = reactive(emptyForm())

const rules = {
  ten_ngan_hang: [{ required: true, message: 'Vui lòng nhập tên ngân hàng', trigger: 'blur' }],
  ten_ngan_hang_viet_tat: [{ required: true, message: 'Vui lòng nhập tên viết tắt', trigger: 'blur' }],
  so_tai_khoan: [
    { required: true, message: 'Vui lòng nhập số tài khoản', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        const cleaned = String(value || '').replace(/[\s.-]/g, '')
        if (cleaned && !/^[0-9A-Za-z]{4,50}$/.test(cleaned)) {
          return callback(new Error('Số tài khoản chỉ gồm chữ và số, từ 4 đến 50 ký tự'))
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  chu_tai_khoan: [{ required: true, message: 'Vui lòng nhập chủ tài khoản', trigger: 'blur' }],
  logo_ngan_hang: [
    {
      validator: (_rule, value, callback) => {
        const text = String(value || '').trim()
        if (text && !/^(https?:\/\/|\/)/i.test(text)) {
          return callback(new Error('Logo phải là URL bắt đầu bằng http(s):// hoặc /'))
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ten_ngan_hang: '',
    ten_ngan_hang_tieng_anh: '',
    ten_ngan_hang_viet_tat: '',
    so_tai_khoan: '',
    chu_tai_khoan: '',
    logo_ngan_hang: '',
    ghi_chu: '',
    trang_thai: 1,
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  logoLoi.value = false
  formRef.value?.clearValidate()
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
    if (filters.ngan_hang) params.ngan_hang = filters.ngan_hang
    if (filters.co_logo !== '' && filters.co_logo !== null) params.co_logo = filters.co_logo
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchNganHangThanhToan(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách ngân hàng thanh toán'))
  } finally {
    loading.value = false
  }
}

async function loadNganHangOptions() {
  try {
    nganHangOptions.value = await fetchLuaChonNganHang()
  } catch {
    nganHangOptions.value = []
  }
}

// before-change của switch: gọi API trước và tự gán trạng thái từ kết quả trả về,
// nên luôn trả false để switch không tự lật (lỗi thì giữ nguyên trạng thái cũ).
async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    const data = await updateTrangThaiNganHangThanhToan(row.id, moi)
    row.trang_thai = data.trang_thai
    ElMessage.success(moi === 1 ? `Đã bật ${row.ten_ngan_hang_viet_tat}` : `Đã tắt ${row.ten_ngan_hang_viet_tat}`)
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
  logoLoi.value = false
  Object.assign(form, {
    ten_ngan_hang: row.ten_ngan_hang,
    ten_ngan_hang_tieng_anh: row.ten_ngan_hang_tieng_anh || '',
    ten_ngan_hang_viet_tat: row.ten_ngan_hang_viet_tat,
    so_tai_khoan: row.so_tai_khoan,
    chu_tai_khoan: row.chu_tai_khoan,
    logo_ngan_hang: row.logo_ngan_hang || '',
    ghi_chu: row.ghi_chu || '',
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ten_ngan_hang: form.ten_ngan_hang.trim(),
    ten_ngan_hang_tieng_anh: form.ten_ngan_hang_tieng_anh?.trim() || null,
    ten_ngan_hang_viet_tat: form.ten_ngan_hang_viet_tat.trim().toUpperCase(),
    so_tai_khoan: form.so_tai_khoan.replace(/[\s.-]/g, ''),
    chu_tai_khoan: form.chu_tai_khoan.trim().replace(/\s+/g, ' ').toUpperCase(),
    logo_ngan_hang: form.logo_ngan_hang?.trim() || null,
    ghi_chu: form.ghi_chu?.trim() || null,
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
      await updateNganHangThanhToan(editingId.value, payload)
      ElMessage.success('Đã cập nhật ngân hàng thanh toán')
    } else {
      await createNganHangThanhToan(payload)
      ElMessage.success('Đã thêm ngân hàng thanh toán')
    }
    dialogVisible.value = false
    await Promise.all([load(), loadNganHangOptions()])
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được ngân hàng thanh toán'))
  } finally {
    saving.value = false
  }
}

function chonFileLogo() {
  logoInput.value?.click()
}

async function taiLenThuMucLogo(file) {
  try {
    return await uploadThuVien(file, THU_MUC_LOGO)
  } catch (error) {
    // Lần đầu dùng: thư mục chưa có thì tạo rồi tải lại.
    if (error?.response?.status !== 404) throw error
    await createThuMuc('', THU_MUC_LOGO)
    return uploadThuVien(file, THU_MUC_LOGO)
  }
}

async function onChonLogo(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (!LOGO_LOAI.includes(file.type)) {
    ElMessage.error('Logo chỉ nhận ảnh PNG, JPG, WEBP hoặc GIF')
    return
  }
  if (file.size > LOGO_TOI_DA_MB * 1024 * 1024) {
    ElMessage.error(`Logo tối đa ${LOGO_TOI_DA_MB}MB`)
    return
  }
  dangTaiLogo.value = true
  try {
    const item = await taiLenThuMucLogo(file)
    form.logo_ngan_hang = item.duong_dan
    logoLoi.value = false
    formRef.value?.clearValidate('logo_ngan_hang')
    ElMessage.success('Đã tải logo lên')
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được logo lên'))
  } finally {
    dangTaiLogo.value = false
  }
}

function xoaLogo() {
  form.logo_ngan_hang = ''
  logoLoi.value = false
}

async function copySoTaiKhoan(row) {
  try {
    await navigator.clipboard.writeText(row.so_tai_khoan)
    ElMessage.success('Đã sao chép số tài khoản')
  } catch {
    ElMessage.error('Không sao chép được số tài khoản')
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Xóa tài khoản ${row.so_tai_khoan} của ${row.ten_ngan_hang_viet_tat}?`,
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
    await deleteNganHangThanhToan(row.id)
    ElMessage.success('Đã xóa ngân hàng thanh toán')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await Promise.all([load(), loadNganHangOptions()])
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được ngân hàng thanh toán'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  try {
    await ElMessageBox.confirm(
      `Xóa ${ids.length} tài khoản ngân hàng đã chọn?`,
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
    const result = await deleteNganHangThanhToanMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} tài khoản ngân hàng`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await Promise.all([load(), loadNganHangOptions()])
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các tài khoản đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  load()
  loadNganHangOptions()
})
</script>

<style scoped>
.bank-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 36px;
  object-fit: contain;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  background: #fff;
}

.bank-logo--text {
  color: var(--el-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.bank-name {
  display: flex;
  flex-direction: column;
  line-height: 1.4;
}

.bank-name small {
  color: var(--el-text-color-secondary);
}

.account-no {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: ui-monospace, Consolas, monospace;
  letter-spacing: 0.02em;
}

.logo-field :deep(.el-form-item__content) {
  display: block;
}

.logo-box {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  background: var(--el-fill-color-lighter);
}

.logo-preview {
  display: flex;
  flex: 0 0 120px;
  align-items: center;
  justify-content: center;
  height: 80px;
  padding: 6px;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  background: #fff;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.4;
  text-align: center;
}

.logo-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.logo-box__input {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.logo-box__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
}

.logo-box__actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.logo-box__hint {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.filter-status,
.filter-logo {
  width: 170px;
}

.filter-bank {
  width: 200px;
}

.bank-option {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.bank-option small {
  overflow: hidden;
  color: var(--el-text-color-secondary);
  text-overflow: ellipsis;
}

@media (max-width: 640px) {
  .filter-bank,
  .filter-logo,
  .filter-status {
    width: 100%;
  }

  .logo-box {
    align-items: stretch;
    flex-direction: column;
  }

  .logo-preview {
    flex-basis: auto;
  }
}
</style>
