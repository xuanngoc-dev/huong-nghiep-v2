<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tên ngành, hướng đi, quốc gia"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.thpt_duhoc_huong_di_id"
          placeholder="Chọn hướng đi"
          clearable
          filterable
          @change="onDoiHuongLoc"
        >
          <CustomOption v-for="item in huongOptions" :key="item.id" :label="nhanHuong(item)" :value="item.id" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.thpt_duhoc_quoc_gia_id"
          placeholder="Chọn quốc gia"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in quocGiaCuaHuong(filters.thpt_duhoc_huong_di_id)"
            :key="item.id"
            :label="nhanQuocGia(item, !filters.thpt_duhoc_huong_di_id)"
            :value="item.id"
          />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách ngành du học</h2>
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
            Thêm ngành
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
        <CustomTableColumn prop="ten_nganh" label="Tên ngành" min-width="200" />
        <CustomTableColumn prop="ten_huong" label="Hướng đi" min-width="170" />
        <CustomTableColumn label="Quốc gia" width="140" align="center">
          <template #default="{ row }">
            <span v-if="row.ten_quoc_gia">{{ row.ten_quoc_gia }}</span>
            <CustomTag v-else type="info" effect="light">Chung</CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Nhu cầu nhân lực" width="150">
          <template #default="{ row }">{{ row.nhu_cau_nhan_luc || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mức lương tham khảo" min-width="240">
          <template #default="{ row }">{{ row.muc_luong_tham_khao || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Ghi chú" min-width="200">
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_nganh)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có ngành du học nào." />
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
    :title="editingId ? 'Cập nhật ngành du học' : 'Thêm ngành du học'"
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
        placeholder="Dán mảng JSON vào đây (dùng ma_huong, ma_quoc_gia hoặc id tương ứng)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Hướng đi" prop="thpt_duhoc_huong_di_id">
          <CustomSelect
            v-model="form.thpt_duhoc_huong_di_id"
            placeholder="Chọn hướng đi"
            filterable
            @change="boQuocGiaSaiHuong(form)"
          >
            <CustomOption v-for="item in huongOptions" :key="item.id" :label="nhanHuong(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Quốc gia" prop="thpt_duhoc_quoc_gia_id">
          <CustomSelect
            v-model="form.thpt_duhoc_quoc_gia_id"
            placeholder="Chọn quốc gia (trống = chung)"
            clearable
            filterable
            :disabled="!form.thpt_duhoc_huong_di_id"
          >
            <CustomOption
              v-for="item in quocGiaCuaHuong(form.thpt_duhoc_huong_di_id)"
              :key="item.id"
              :label="nhanQuocGia(item)"
              :value="item.id"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên ngành" prop="ten_nganh">
          <CustomInput v-model="form.ten_nganh" maxlength="255" placeholder="Nhập tên ngành" />
        </CustomFormItem>
        <CustomFormItem label="Nhu cầu nhân lực" prop="nhu_cau_nhan_luc">
          <CustomInput v-model="form.nhu_cau_nhan_luc" maxlength="255" placeholder="Nhập nhu cầu nhân lực" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mức lương tham khảo" prop="muc_luong_tham_khao">
          <CustomInput
            v-model="form.muc_luong_tham_khao"
            maxlength="255"
            placeholder="Nhập mức lương tham khảo (ví dụ: 2.800 - 3.500 EUR/tháng)"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">
          <CustomInput v-model="form.ghi_chu" type="textarea" :rows="3" maxlength="5000" placeholder="Nhập ghi chú" />
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
import { nganhApi } from '@/api/thptDuHoc'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangDuHoc, useLienKetDuHoc } from '@/composables/useThptDuHoc'

const JSON_SAMPLE = `[
  {
    "ma_huong": "DU_HOC_NGHE",
    "ma_quoc_gia": "DE",
    "ten_nganh": "Điều dưỡng",
    "nhu_cau_nhan_luc": "Rất cao",
    "muc_luong_tham_khao": "2.800 - 3.500 EUR/tháng",
    "ghi_chu": "Yêu cầu tiếng Đức B2"
  }
]`

const filters = reactive({ q: '', thpt_duhoc_huong_di_id: '', thpt_duhoc_quoc_gia_id: '' })

const { huongOptions, loadOptions, quocGiaCuaHuong, nhanHuong, nhanQuocGia, boQuocGiaSaiHuong, lienKetTuJson } =
  useLienKetDuHoc()
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
  api: nganhApi,
  nhan: 'ngành',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thpt_duhoc_huong_di_id) params.thpt_duhoc_huong_di_id = filters.thpt_duhoc_huong_di_id
    if (filters.thpt_duhoc_quoc_gia_id) params.thpt_duhoc_quoc_gia_id = filters.thpt_duhoc_quoc_gia_id
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'ngành' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  thpt_duhoc_huong_di_id: [{ required: true, message: 'Vui lòng chọn hướng đi', trigger: 'change' }],
  ten_nganh: [{ required: true, message: 'Vui lòng nhập tên ngành', trigger: 'blur' }],
}

function emptyForm() {
  return {
    thpt_duhoc_huong_di_id: null,
    thpt_duhoc_quoc_gia_id: null,
    ten_nganh: '',
    nhu_cau_nhan_luc: '',
    muc_luong_tham_khao: '',
    ghi_chu: '',
  }
}

function onDoiHuongLoc() {
  boQuocGiaSaiHuong(filters)
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
    thpt_duhoc_huong_di_id: item.thpt_duhoc_huong_di_id,
    thpt_duhoc_quoc_gia_id: item.thpt_duhoc_quoc_gia_id || null,
    ten_nganh: String(item.ten_nganh ?? '').trim(),
    nhu_cau_nhan_luc: giaTriTuyChon(item.nhu_cau_nhan_luc),
    muc_luong_tham_khao: giaTriTuyChon(item.muc_luong_tham_khao),
    ghi_chu: giaTriTuyChon(item.ghi_chu),
  }
}

function openCreate() {
  resetForm()
  // Đang lọc thì chọn sẵn hướng đi, quốc gia đó.
  form.thpt_duhoc_huong_di_id = filters.thpt_duhoc_huong_di_id || null
  form.thpt_duhoc_quoc_gia_id = filters.thpt_duhoc_quoc_gia_id || null
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
    items = docMangJson(jsonText.value, 'ngành').map((item, index) => {
      const payload = chuanHoa({ ...item, ...lienKetTuJson(item, index + 1) })
      if (!payload.ten_nganh) throw new Error(`Phần tử thứ ${index + 1} thiếu ten_nganh`)
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: nganhApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await nganhApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật ngành')
    } else {
      await nganhApi.create(payload)
      ElMessage.success('Đã thêm ngành')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được ngành'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
