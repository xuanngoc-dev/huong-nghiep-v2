<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="filters">
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm tên loại câu hỏi"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
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
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách loại câu hỏi</h2>
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
            Thêm loại câu hỏi
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
        <CustomTableColumn prop="id" label="ID" width="100" align="center" />
        <CustomTableColumn prop="thu_tu_uu_tien" label="Thứ tự hiển thị" width="180" align="center" />
        <CustomTableColumn prop="ten_loai_cau_hoi" label="Tên loại câu hỏi" min-width="220" />
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
              :aria-label="`Trạng thái ${row.ten_loai_cau_hoi}`"
            />
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="ghi_chu" label="Ghi chú" min-width="220" >
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
          <CustomEmpty description="Chưa có loại câu hỏi nào." />
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
    :title="editingId ? 'Cập nhật loại câu hỏi' : 'Thêm loại câu hỏi'"
    width="800px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomRadioGroup v-if="!editingId" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!editingId && createMode === 'json'" class="json-panel">
      <div class="json-panel__head">
        <div class="json-panel__actions">
          <JsonFileButton v-model="jsonText" />
          <CustomButton text type="primary" @click="fillJsonSample">Điền mẫu</CustomButton>
        </div>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        placeholder="Dán mảng JSON vào đây"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Tên loại câu hỏi" prop="ten_loai_cau_hoi">
          <CustomInput
            v-model="form.ten_loai_cau_hoi"
            maxlength="150"
            placeholder="Ví dụ: Trắc nghiệm một đáp án"
          />
        </CustomFormItem>
        <CustomFormItem label="Thứ tự ưu tiên" prop="thu_tu_uu_tien">
          <CustomInputNumber
            v-model="form.thu_tu_uu_tien"
            placeholder="Nhập thứ tự ưu tiên"
            :min="1"
            :max="9999"
            :step="1"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Trạng thái" prop="trang_thai">
          <CustomSelect v-model="form.trang_thai" placeholder="Chọn trạng thái" :clearable="false">
            <CustomOption label="Hoạt động" :value="1" />
            <CustomOption label="Ngừng sử dụng" :value="0" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput
            v-model="form.ghi_chu"
            type="textarea"
            :rows="3"
            maxlength="2000"
            show-word-limit
            placeholder="Ghi chú thêm (nếu có)"
          />
        </CustomFormItem>
      </div>
    </CustomForm>
    <template #footer>
      <JsonImportDialogFooter
        :batch="jsonImport"
        :saving="saving"
        :show-progress="!editingId && createMode === 'json'"
        @cancel="dialogVisible = false"
        @save="onSubmit"
      />
    </template>
  </CustomDialog>
</template>

<script setup>
import { h, onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createLoaiCauHoi,
  createLoaiCauHoiBulk,
  deleteLoaiCauHoi,
  deleteLoaiCauHoiMany,
  fetchAnhHuongXoaLoaiCauHoi,
  fetchLoaiCauHoi,
  updateLoaiCauHoi,
} from '@/api/loaiCauHoi'

const JSON_SAMPLE = `[
  {
    "ten_loai_cau_hoi": "Trắc nghiệm một đáp án",
    "thu_tu_uu_tien": 1,
    "trang_thai": 1
  },
  {
    "ten_loai_cau_hoi": "Trắc nghiệm nhiều đáp án",
    "thu_tu_uu_tien": 2,
    "ghi_chu": "Chọn một hoặc nhiều phương án"
  }
]`

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
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'loại câu hỏi' })
const formRef = ref()
const dangDoiTrangThai = ref({})

const filters = reactive({
  q: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

const rules = {
  ten_loai_cau_hoi: [{ required: true, message: 'Vui lòng nhập tên loại câu hỏi', trigger: 'blur' }],
  thu_tu_uu_tien: [{ required: true, message: 'Vui lòng nhập thứ tự ưu tiên', trigger: 'change' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyForm() {
  return {
    ten_loai_cau_hoi: '',
    ghi_chu: '',
    thu_tu_uu_tien: 1,
    trang_thai: 1,
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng loại câu hỏi.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ten_loai_cau_hoi": "...", "thu_tu_uu_tien": 1 }]')
  }
  if (!data.length) {
    throw new Error('Mảng loại câu hỏi đang trống')
  }

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một loại câu hỏi`)
    }
    const ten = String(item.ten_loai_cau_hoi ?? '').trim()
    const order = Number(item.thu_tu_uu_tien)
    if (!ten || !Number.isInteger(order) || order < 1) {
      throw new Error(`Phần tử thứ ${line} thiếu ten_loai_cau_hoi hoặc thu_tu_uu_tien`)
    }
    return {
      ten_loai_cau_hoi: ten,
      thu_tu_uu_tien: order,
      trang_thai: item.trang_thai ?? 1,
      ghi_chu: item.ghi_chu == null ? null : String(item.ghi_chu).trim() || null,
    }
  })
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
    if (filters.trang_thai !== '' && filters.trang_thai !== null) {
      params.trang_thai = filters.trang_thai
    }
    const data = await fetchLoaiCauHoi(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách loại câu hỏi'))
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
    ten_loai_cau_hoi: row.ten_loai_cau_hoi,
    ghi_chu: row.ghi_chu || '',
    thu_tu_uu_tien: row.thu_tu_uu_tien,
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return {
    ten_loai_cau_hoi: form.ten_loai_cau_hoi.trim(),
    thu_tu_uu_tien: form.thu_tu_uu_tien,
    trang_thai: form.trang_thai,
    ghi_chu: form.ghi_chu?.trim() || null,
  }
}

async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    const data = await updateLoaiCauHoi(row.id, {
      ten_loai_cau_hoi: row.ten_loai_cau_hoi,
      thu_tu_uu_tien: row.thu_tu_uu_tien,
      trang_thai: moi,
      ghi_chu: row.ghi_chu ?? null,
    })
    row.trang_thai = data.trang_thai
    ElMessage.success(moi === 1 ? `Đã bật "${row.ten_loai_cau_hoi}"` : `Đã tắt "${row.ten_loai_cau_hoi}"`)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái'))
  } finally {
    const { [row.id]: _bo, ...conLai } = dangDoiTrangThai.value
    dangDoiTrangThai.value = conLai
  }
  return false
}

function fillJsonSample() {
  jsonText.value = JSON_SAMPLE
}

async function onSubmitJson() {
  let items
  try {
    items = parseJsonItems(jsonText.value)
  } catch (error) {
    ElMessage.error(error.message)
    return
  }

  await jsonImport.run({
    items,
    createBatch: createLoaiCauHoiBulk,
    jsonText,
    saving,
    dialogVisible,
    reload: load,
  })
}

async function onSubmit() {
  if (!editingId.value && createMode.value === 'json') {
    await onSubmitJson()
    return
  }

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = payloadFromForm()
    if (editingId.value) {
      await updateLoaiCauHoi(editingId.value, payload)
      ElMessage.success('Đã cập nhật loại câu hỏi')
    } else {
      await createLoaiCauHoi(payload)
      ElMessage.success('Đã thêm loại câu hỏi')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được loại câu hỏi'))
  } finally {
    saving.value = false
  }
}

/**
 * Hỏi xác nhận xóa; còn câu hỏi / phiên khảo sát liên quan thì liệt kê số lượng sẽ bị xóa kèm.
 * Trả null nếu người dùng hủy (hoặc không xem trước được), ngược lại trả xoaLienQuan để gửi kèm lệnh xóa.
 */
async function xacNhanXoa(ids, tieuDe) {
  let anhHuong
  try {
    anhHuong = await fetchAnhHuongXoaLoaiCauHoi(ids)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không kiểm tra được dữ liệu liên quan'))
    return null
  }
  const xoaLienQuan = Boolean(anhHuong.so_cau_hoi || anhHuong.so_phien)
  const message = xoaLienQuan
    ? h('div', [
        h('p', `${tieuDe}? Thao tác này sẽ xóa luôn:`),
        h('ul', { style: 'margin: 8px 0; padding-left: 20px' }, [
          h('li', `${anhHuong.so_cau_hoi} câu hỏi thuộc loại này`),
          h('li', `${anhHuong.so_dap_an} đáp án của các câu hỏi đó`),
          h('li', `${anhHuong.so_phien} phiên khảo sát đã thực hiện có câu hỏi thuộc loại này (xóa cả phiên)`),
        ]),
        h('p', { style: 'color: var(--el-color-danger)' }, 'Dữ liệu đã xóa không thể khôi phục.'),
      ])
    : `${tieuDe}?`
  try {
    await ElMessageBox.confirm(message, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: xoaLienQuan ? 'Đồng ý xóa tất cả' : 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return null
  }
  return { xoaLienQuan }
}

async function onDelete(row) {
  const xacNhan = await xacNhanXoa([row.id], `Xóa loại câu hỏi "${row.ten_loai_cau_hoi}"`)
  if (!xacNhan) return

  try {
    await deleteLoaiCauHoi(row.id, xacNhan.xoaLienQuan)
    ElMessage.success('Đã xóa loại câu hỏi')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được loại câu hỏi'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return

  const xacNhan = await xacNhanXoa(ids, `Xóa ${ids.length} loại câu hỏi đã chọn`)
  if (!xacNhan) return

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteLoaiCauHoiMany(ids, xacNhan.xoaLienQuan)
    ElMessage.success(`Đã xóa ${result.deleted} loại câu hỏi`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các loại câu hỏi đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>
