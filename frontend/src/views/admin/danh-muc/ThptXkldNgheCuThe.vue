<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tên công việc, nhóm nghề, thị trường"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.thpt_xkld_nhom_nghe_id"
          placeholder="Chọn nhóm nghề"
          clearable
          filterable
          @change="onDoiNhomLoc"
        >
          <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.thpt_xkld_thi_truong_id"
          placeholder="Chọn thị trường"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in thiTruongCuaNhom(filters.thpt_xkld_nhom_nghe_id)"
            :key="item.id"
            :label="nhanThiTruong(item, !filters.thpt_xkld_nhom_nghe_id)"
            :value="item.id"
          />
        </CustomSelect>
        <CustomSelect v-model="filters.yeu_cau_gioi_tinh" placeholder="Chọn yêu cầu giới tính" clearable @change="onSearch">
          <CustomOption v-for="item in YEU_CAU_GIOI_TINH" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách nghề cụ thể xuất khẩu lao động</h2>
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
            Thêm nghề cụ thể
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
        <CustomTableColumn prop="ten_cong_viec" label="Tên công việc" min-width="200" />
        <CustomTableColumn prop="ten_nhom" label="Nhóm nghề" min-width="170" />
        <CustomTableColumn label="Thị trường" width="140" align="center">
          <template #default="{ row }">
            <span v-if="row.ten_quoc_gia">{{ row.ten_quoc_gia }}</span>
            <CustomTag v-else type="info" effect="light">Chung</CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Giới tính" width="140" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauEnum(YEU_CAU_GIOI_TINH, row.yeu_cau_gioi_tinh)" effect="light">
              {{ nhanEnum(YEU_CAU_GIOI_TINH, row.yeu_cau_gioi_tinh) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Mô tả ngắn" min-width="280">
          <template #default="{ row }">{{ row.mo_ta_ngan || '—' }}</template>
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_cong_viec)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có nghề cụ thể xuất khẩu lao động nào." />
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
    :title="editingId ? 'Cập nhật nghề cụ thể xuất khẩu lao động' : 'Thêm nghề cụ thể xuất khẩu lao động'"
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
          <CustomButton text type="primary" @click="jsonText = JSON_SAMPLE">Điền mẫu</CustomButton>
        </div>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        placeholder="Dán mảng JSON vào đây (dùng ma_nhom, ma_quoc_gia hoặc id tương ứng)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Nhóm nghề" prop="thpt_xkld_nhom_nghe_id">
          <CustomSelect
            v-model="form.thpt_xkld_nhom_nghe_id"
            placeholder="Chọn nhóm nghề"
            filterable
            @change="boThiTruongSaiNhom(form)"
          >
            <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Thị trường" prop="thpt_xkld_thi_truong_id">
          <CustomSelect
            v-model="form.thpt_xkld_thi_truong_id"
            placeholder="Chọn thị trường (trống = chung)"
            clearable
            filterable
            :disabled="!form.thpt_xkld_nhom_nghe_id"
          >
            <CustomOption
              v-for="item in thiTruongCuaNhom(form.thpt_xkld_nhom_nghe_id)"
              :key="item.id"
              :label="nhanThiTruong(item)"
              :value="item.id"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên công việc" prop="ten_cong_viec">
          <CustomInput v-model="form.ten_cong_viec" maxlength="255" placeholder="Nhập tên công việc" />
        </CustomFormItem>
        <CustomFormItem label="Yêu cầu giới tính" prop="yeu_cau_gioi_tinh">
          <CustomSelect v-model="form.yeu_cau_gioi_tinh" placeholder="Chọn yêu cầu giới tính" :clearable="false">
            <CustomOption v-for="item in YEU_CAU_GIOI_TINH" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mô tả ngắn" prop="mo_ta_ngan">
          <CustomInput
            v-model="form.mo_ta_ngan"
            type="textarea"
            :rows="3"
            maxlength="5000"
            placeholder="Nhập mô tả ngắn"
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ngheCuTheApi } from '@/api/thptXkld'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangXkld, useLienKetXkld } from '@/composables/useThptXkld'
import { YEU_CAU_GIOI_TINH, mauEnum, nhanEnum } from '@/constants/thptXkld'

const JSON_SAMPLE = `[
  {
    "ma_nhom": "CO_KHI",
    "ma_quoc_gia": "JP",
    "ten_cong_viec": "Hàn bán tự động",
    "mo_ta_ngan": "Hàn kết cấu thép tại xưởng, làm việc theo ca.",
    "yeu_cau_gioi_tinh": "nam"
  }
]`

const filters = reactive({ q: '', thpt_xkld_nhom_nghe_id: '', thpt_xkld_thi_truong_id: '', yeu_cau_gioi_tinh: '' })

const { nhomOptions, loadOptions, thiTruongCuaNhom, nhanNhom, nhanThiTruong, boThiTruongSaiNhom, lienKetTuJson } =
  useLienKetXkld()
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
} = useBangXkld({
  api: ngheCuTheApi,
  nhan: 'nghề cụ thể',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thpt_xkld_nhom_nghe_id) params.thpt_xkld_nhom_nghe_id = filters.thpt_xkld_nhom_nghe_id
    if (filters.thpt_xkld_thi_truong_id) params.thpt_xkld_thi_truong_id = filters.thpt_xkld_thi_truong_id
    if (filters.yeu_cau_gioi_tinh) params.yeu_cau_gioi_tinh = filters.yeu_cau_gioi_tinh
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'nghề cụ thể' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  thpt_xkld_nhom_nghe_id: [{ required: true, message: 'Vui lòng chọn nhóm nghề', trigger: 'change' }],
  ten_cong_viec: [{ required: true, message: 'Vui lòng nhập tên công việc', trigger: 'blur' }],
}

function emptyForm() {
  return {
    thpt_xkld_nhom_nghe_id: null,
    thpt_xkld_thi_truong_id: null,
    ten_cong_viec: '',
    mo_ta_ngan: '',
    yeu_cau_gioi_tinh: 'ca_hai',
  }
}

function onDoiNhomLoc() {
  boThiTruongSaiNhom(filters)
  onSearch()
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function chuanHoa(item) {
  return {
    thpt_xkld_nhom_nghe_id: item.thpt_xkld_nhom_nghe_id,
    thpt_xkld_thi_truong_id: item.thpt_xkld_thi_truong_id || null,
    ten_cong_viec: String(item.ten_cong_viec ?? '').trim(),
    mo_ta_ngan: giaTriTuyChon(item.mo_ta_ngan),
    yeu_cau_gioi_tinh: item.yeu_cau_gioi_tinh || 'ca_hai',
  }
}

function openCreate() {
  resetForm()
  // Đang lọc thì chọn sẵn nhóm nghề, thị trường đó.
  form.thpt_xkld_nhom_nghe_id = filters.thpt_xkld_nhom_nghe_id || null
  form.thpt_xkld_thi_truong_id = filters.thpt_xkld_thi_truong_id || null
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  const values = emptyForm()
  for (const key of Object.keys(values)) {
    if (row[key] != null) values[key] = row[key]
  }
  Object.assign(form, values)
  dialogVisible.value = true
}

async function onSubmitJson() {
  let items
  try {
    items = docMangJson(jsonText.value, 'nghề cụ thể').map((item, index) => {
      const payload = chuanHoa({ ...item, ...lienKetTuJson(item, index + 1) })
      if (!payload.ten_cong_viec) throw new Error(`Phần tử thứ ${index + 1} thiếu ten_cong_viec`)
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: ngheCuTheApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
    const payload = chuanHoa(form)
    if (editingId.value) {
      await ngheCuTheApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật nghề cụ thể')
    } else {
      await ngheCuTheApi.create(payload)
      ElMessage.success('Đã thêm nghề cụ thể')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được nghề cụ thể'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
