<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tên bước, mô tả, hướng đi, quốc gia"
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
        <h2 class="toolbar__title">Danh sách thủ tục du học</h2>
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
            Thêm bước
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
        <CustomTableColumn prop="ten_huong" label="Hướng đi" min-width="170" />
        <CustomTableColumn label="Quốc gia" width="130" align="center">
          <template #default="{ row }">
            <span v-if="row.ten_quoc_gia">{{ row.ten_quoc_gia }}</span>
            <CustomTag v-else type="info" effect="light">Chung</CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="buoc_so" label="Bước" width="80" align="center" />
        <CustomTableColumn prop="ten_buoc" label="Tên bước" min-width="200" />
        <CustomTableColumn prop="mo_ta_thu_tuc" label="Mô tả thủ tục" min-width="300" />
        <CustomTableColumn label="Giấy tờ cần có" min-width="220">
          <template #default="{ row }">{{ row.giay_to_can_co || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thời gian dự kiến" width="150">
          <template #default="{ row }">{{ row.thoi_gian_du_kien || '—' }}</template>
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_buoc)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có bước thủ tục nào." />
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
    :title="editingId ? 'Cập nhật bước thủ tục' : 'Thêm bước thủ tục'"
    width="1040px"
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
        <CustomFormItem label="Bước số" prop="buoc_so">
          <CustomInputNumber
            v-model="form.buoc_so"
            placeholder="Nhập bước số"
            :min="1"
            :max="100"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên bước" prop="ten_buoc">
          <CustomInput v-model="form.ten_buoc" maxlength="255" placeholder="Nhập tên bước" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Thời gian dự kiến" prop="thoi_gian_du_kien">
          <CustomInput
            v-model="form.thoi_gian_du_kien"
            maxlength="100"
            placeholder="Nhập thời gian dự kiến (ví dụ: 1 - 3 tháng)"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mô tả thủ tục" prop="mo_ta_thu_tuc">
          <CustomInput
            v-model="form.mo_ta_thu_tuc"
            type="textarea"
            :rows="3"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập mô tả thủ tục"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Giấy tờ cần có" prop="giay_to_can_co">
          <CustomInput
            v-model="form.giay_to_can_co"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập giấy tờ cần có"
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
import { thuTucApi } from '@/api/thptDuHoc'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangDuHoc, useLienKetDuHoc } from '@/composables/useThptDuHoc'

const JSON_SAMPLE = `[
  {
    "ma_huong": "DU_HOC_NGHE",
    "ma_quoc_gia": "DE",
    "buoc_so": 1,
    "ten_buoc": "Học tiếng Đức",
    "mo_ta_thu_tuc": "Học từ A1 đến B1 và thi chứng chỉ Goethe hoặc telc.",
    "giay_to_can_co": "CCCD, học bạ THPT",
    "thoi_gian_du_kien": "6 - 12 tháng"
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
  api: thuTucApi,
  nhan: 'bước thủ tục',
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
const jsonImport = useJsonBatchImport({ label: 'bước thủ tục' })
const formRef = ref()
const form = reactive(emptyForm())

const rules = {
  thpt_duhoc_huong_di_id: [{ required: true, message: 'Vui lòng chọn hướng đi', trigger: 'change' }],
  buoc_so: [{ required: true, message: 'Vui lòng nhập bước số', trigger: 'change' }],
  ten_buoc: [{ required: true, message: 'Vui lòng nhập tên bước', trigger: 'blur' }],
  mo_ta_thu_tuc: [{ required: true, message: 'Vui lòng nhập mô tả thủ tục', trigger: 'blur' }],
}

function emptyForm() {
  return {
    thpt_duhoc_huong_di_id: null,
    thpt_duhoc_quoc_gia_id: null,
    buoc_so: undefined,
    ten_buoc: '',
    mo_ta_thu_tuc: '',
    giay_to_can_co: '',
    thoi_gian_du_kien: '',
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
    buoc_so: Number(item.buoc_so) || null,
    ten_buoc: String(item.ten_buoc ?? '').trim(),
    mo_ta_thu_tuc: String(item.mo_ta_thu_tuc ?? '').trim(),
    giay_to_can_co: giaTriTuyChon(item.giay_to_can_co),
    thoi_gian_du_kien: giaTriTuyChon(item.thoi_gian_du_kien),
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
    items = docMangJson(jsonText.value, 'bước thủ tục').map((item, index) => {
      const payload = chuanHoa({ ...item, ...lienKetTuJson(item, index + 1) })
      if (!payload.buoc_so || !payload.ten_buoc || !payload.mo_ta_thu_tuc) {
        throw new Error(`Phần tử thứ ${index + 1} thiếu buoc_so, ten_buoc hoặc mo_ta_thu_tuc`)
      }
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: thuTucApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await thuTucApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật bước thủ tục')
    } else {
      await thuTucApi.create(payload)
      ElMessage.success('Đã thêm bước thủ tục')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được bước thủ tục'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
