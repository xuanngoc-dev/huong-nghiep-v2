<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên, slug"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect v-model="filters.trang_thai" placeholder="Chọn trạng thái" clearable @change="onSearch">
          <CustomOption v-for="item in TRANG_THAI" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách nhóm tin</h2>
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
            Thêm nhóm tin
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
        <CustomTableColumn prop="ma_nhom" label="Mã nhóm" min-width="180" />
        <CustomTableColumn prop="ten_nhom" label="Tên nhóm" min-width="200" />
        <CustomTableColumn prop="slug" label="Slug" min-width="180" show-overflow-tooltip />
        <CustomTableColumn label="Mô tả" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">{{ row.mo_ta || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="so_bai_viet" label="Số bài viết" width="110" align="center" />
        <CustomTableColumn prop="thu_tu" label="Thứ tự" width="90" align="center" />
        <CustomTableColumn label="Trạng thái" width="120" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.trang_thai ? 'success' : 'info'" effect="light">
              {{ row.trang_thai ? 'Hiển thị' : 'Ẩn' }}
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_nhom)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có nhóm tin nào." />
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
    :title="editingId ? 'Cập nhật nhóm tin' : 'Thêm nhóm tin'"
    width="800px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomForm ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem label="Mã nhóm" prop="ma_nhom">
          <CustomInput v-model="form.ma_nhom" maxlength="50" placeholder="Nhập mã nhóm (ví dụ: TUYEN_SINH)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên nhóm" prop="ten_nhom">
          <CustomInput v-model="form.ten_nhom" maxlength="255" placeholder="Nhập tên nhóm" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Slug" prop="slug">
          <CustomInput v-model="form.slug" maxlength="255" placeholder="Bỏ trống để tự tạo từ tên nhóm" />
        </CustomFormItem>
        <CustomFormItem label="Thứ tự" prop="thu_tu">
          <CustomInputNumber
            v-model="form.thu_tu"
            placeholder="Nhập thứ tự"
            :min="0"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Trạng thái" prop="trang_thai">
          <CustomSwitch
            v-model="form.trang_thai"
            :active-value="1"
            :inactive-value="0"
            active-text="Hiển thị"
            inactive-text="Ẩn"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mô tả" prop="mo_ta">
          <CustomInput v-model="form.mo_ta" type="textarea" :rows="3" maxlength="5000" placeholder="Nhập mô tả" />
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { nhomTinApi } from '@/api/tinTuc'
import { errorMessage, giaTriTuyChon, useBangDuHoc } from '@/composables/useThptDuHoc'

defineOptions({ name: 'NhomTin' })

const TRANG_THAI = [
  { value: 1, label: 'Hiển thị' },
  { value: 0, label: 'Ẩn' },
]

const filters = reactive({ q: '', trang_thai: '' })

const {
  loading,
  deleting,
  rows,
  selectedRows,
  tableRef,
  total,
  page,
  pageSize,
  load,
  onSelectionChange,
  rowIndex,
  onSearch,
  onDelete,
  onDeleteSelected,
} = useBangDuHoc({
  api: nhomTinApi,
  nhan: 'nhóm tin',
  canhBaoXoa: 'Chỉ xóa được nhóm không còn bài viết.',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai === 0 || filters.trang_thai === 1) params.trang_thai = filters.trang_thai
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  ma_nhom: [{ required: true, message: 'Vui lòng nhập mã nhóm', trigger: 'blur' }],
  ten_nhom: [{ required: true, message: 'Vui lòng nhập tên nhóm', trigger: 'blur' }],
}

function emptyForm() {
  return { ma_nhom: '', ten_nhom: '', slug: '', mo_ta: '', thu_tu: 0, trang_thai: 1 }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  formRef.value?.clearValidate()
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    ma_nhom: row.ma_nhom,
    ten_nhom: row.ten_nhom,
    slug: row.slug,
    mo_ta: row.mo_ta || '',
    thu_tu: row.thu_tu ?? 0,
    trang_thai: row.trang_thai,
  })
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = {
      ma_nhom: form.ma_nhom.trim().toUpperCase(),
      ten_nhom: form.ten_nhom.trim(),
      slug: giaTriTuyChon(form.slug),
      mo_ta: giaTriTuyChon(form.mo_ta),
      thu_tu: Number(form.thu_tu) || 0,
      trang_thai: form.trang_thai,
    }
    if (editingId.value) {
      await nhomTinApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật nhóm tin')
    } else {
      await nhomTinApi.create(payload)
      ElMessage.success('Đã thêm nhóm tin')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được nhóm tin'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
