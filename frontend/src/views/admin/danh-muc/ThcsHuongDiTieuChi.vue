<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên hướng đi hoặc tiêu chí"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.thcs_huong_di_id"
          placeholder="Chọn hướng đi"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption v-for="item in huongOptions" :key="item.id" :label="nhanHuong(item)" :value="item.id" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.thcs_tieu_chi_id"
          placeholder="Chọn tiêu chí"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption v-for="item in tieuChiOptions" :key="item.id" :label="nhanTieuChi(item)" :value="item.id" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Điểm phù hợp của hướng đi theo tiêu chí</h2>
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
            Chấm điểm
          </CustomButton>
        </div>
      </div>

      <CustomTable
        ref="tableRef"
        :loading="loading"
        :data="rows"
        :row-key="khoa"
        stripe
        border
        @selection-change="onSelectionChange"
      >
        <CustomTableColumn type="selection" width="48" reserve-selection align="center" />
        <CustomTableColumn label="STT" width="72" align="center">
          <template #default="{ $index }">{{ rowIndex($index) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Hướng đi" min-width="220">
          <template #default="{ row }">{{ row.ten_huong }} ({{ row.ma_huong }})</template>
        </CustomTableColumn>
        <CustomTableColumn label="Tiêu chí" min-width="240">
          <template #default="{ row }">{{ row.ten_tieu_chi }} ({{ row.ma_tieu_chi }})</template>
        </CustomTableColumn>
        <CustomTableColumn label="Nhóm tiêu chí" width="150" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.nhom_tieu_chi" type="info" effect="light">{{ row.nhom_tieu_chi }}</CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Điểm phù hợp" width="130" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauDiem(row.diem_phu_hop)" effect="light">{{ row.diem_phu_hop }}/5</CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Nhận định tư vấn" min-width="260">
          <template #default="{ row }">{{ row.nhan_dinh_tu_van || '—' }}</template>
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
          <CustomEmpty description="Chưa chấm điểm phù hợp cho hướng đi nào." />
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
    :title="dangSua ? 'Cập nhật điểm phù hợp' : 'Chấm điểm phù hợp cho hướng đi'"
    width="800px"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomRadioGroup v-if="!dangSua" v-model="createMode" class="create-mode">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!dangSua && createMode === 'json'" class="json-panel">
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
        placeholder="Dán mảng JSON vào đây (dùng ma_huong, ma_tieu_chi hoặc id)"
      />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Hướng đi" prop="thcs_huong_di_id">
          <CustomSelect v-model="form.thcs_huong_di_id" placeholder="Chọn hướng đi" filterable :disabled="!!dangSua">
            <CustomOption v-for="item in huongOptions" :key="item.id" :label="nhanHuong(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tiêu chí" prop="thcs_tieu_chi_id">
          <CustomSelect v-model="form.thcs_tieu_chi_id" placeholder="Chọn tiêu chí" filterable :disabled="!!dangSua">
            <CustomOption
              v-for="item in tieuChiOptions"
              :key="item.id"
              :label="nhanTieuChi(item)"
              :value="item.id"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Điểm phù hợp" prop="diem_phu_hop">
          <CustomSelect v-model="form.diem_phu_hop" placeholder="Chọn điểm phù hợp" :clearable="false">
            <CustomOption v-for="item in MUC_DIEM_PHU_HOP" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Nhận định tư vấn" prop="nhan_dinh_tu_van">
          <CustomInput
            v-model="form.nhan_dinh_tu_van"
            maxlength="255"
            show-word-limit
            placeholder="Nhập nhận định tư vấn (nếu có)"
          />
        </CustomFormItem>
      </div>
    </CustomForm>
    <template #footer>
      <JsonImportDialogFooter
        :batch="jsonImport"
        :saving="saving"
        :show-progress="!dangSua && createMode === 'json'"
        @cancel="dialogVisible = false"
        @save="onSubmit"
      />
    </template>
  </CustomDialog>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { huongDiTieuChiApi, tieuChiApi } from '@/api/thcsHuongDi'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, loadAll, useHuongDiThcs } from '@/composables/useThcsHuongDi'
import { MUC_DIEM_PHU_HOP, mauDiem } from '@/constants/thcsHuongDi'

const JSON_SAMPLE = `[
  {
    "ma_huong": "THPT_CONG_LAP",
    "ma_tieu_chi": "HOC_LUC",
    "diem_phu_hop": 5,
    "nhan_dinh_tu_van": "Học lực khá giỏi nên ưu tiên hướng này"
  },
  {
    "thcs_huong_di_id": 1,
    "thcs_tieu_chi_id": 2,
    "diem_phu_hop": 3
  }
]`

const { huongOptions, loadHuongOptions, nhanHuong, huongTuJson } = useHuongDiThcs()
const tieuChiOptions = ref([])

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
// Dòng đang sửa (khóa ghép không đổi được khi sửa).
const dangSua = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'điểm phù hợp' })
const formRef = ref()

const filters = reactive({ q: '', thcs_huong_di_id: '', thcs_tieu_chi_id: '' })
const form = reactive(emptyForm())

const rules = {
  thcs_huong_di_id: [{ required: true, message: 'Vui lòng chọn hướng đi', trigger: 'change' }],
  thcs_tieu_chi_id: [{ required: true, message: 'Vui lòng chọn tiêu chí', trigger: 'change' }],
  diem_phu_hop: [{ required: true, message: 'Vui lòng chọn điểm phù hợp', trigger: 'change' }],
}

function emptyForm() {
  return { thcs_huong_di_id: null, thcs_tieu_chi_id: null, diem_phu_hop: 3, nhan_dinh_tu_van: '' }
}

function khoa(row) {
  return `${row.thcs_huong_di_id}-${row.thcs_tieu_chi_id}`
}

function nhanTieuChi(item) {
  return `${item.ten_tieu_chi} (${item.ma_tieu_chi})`
}

async function loadTieuChiOptions() {
  try {
    tieuChiOptions.value = await loadAll(tieuChiApi.fetch)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách tiêu chí'))
  }
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.thcs_huong_di_id) params.thcs_huong_di_id = filters.thcs_huong_di_id
    if (filters.thcs_tieu_chi_id) params.thcs_tieu_chi_id = filters.thcs_tieu_chi_id
    const data = await huongDiTieuChiApi.fetch(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách điểm phù hợp'))
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

// Về trang 1 thì `current-change` của phân trang tự gọi load.
function onSearch() {
  clearSelection()
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

function resetForm() {
  Object.assign(form, emptyForm())
  dangSua.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function openCreate() {
  resetForm()
  // Đang lọc thì chọn sẵn hướng đi / tiêu chí đó.
  form.thcs_huong_di_id = filters.thcs_huong_di_id || null
  form.thcs_tieu_chi_id = filters.thcs_tieu_chi_id || null
  dialogVisible.value = true
}

function openEdit(row) {
  dangSua.value = row
  Object.assign(form, {
    thcs_huong_di_id: row.thcs_huong_di_id,
    thcs_tieu_chi_id: row.thcs_tieu_chi_id,
    diem_phu_hop: row.diem_phu_hop,
    nhan_dinh_tu_van: row.nhan_dinh_tu_van || '',
  })
  dialogVisible.value = true
}

// Nhận thcs_tieu_chi_id hoặc ma_tieu_chi; mã được đổi sang id theo danh sách đã tải.
function tieuChiTuJson(item, line) {
  const id = Number(item.thcs_tieu_chi_id) || null
  if (id) return id
  if (!item.ma_tieu_chi) throw new Error(`Phần tử thứ ${line} thiếu ma_tieu_chi hoặc thcs_tieu_chi_id`)
  const ma = String(item.ma_tieu_chi).trim().toUpperCase()
  const found = tieuChiOptions.value.find((t) => t.ma_tieu_chi === ma)
  if (!found) throw new Error(`Phần tử thứ ${line}: không tìm thấy tiêu chí có mã ${ma}`)
  return found.id
}

async function onSubmitJson() {
  let items
  try {
    items = docMangJson(jsonText.value, 'điểm phù hợp').map((item, index) => {
      const line = index + 1
      const diem = item.diem_phu_hop == null ? 3 : Number(item.diem_phu_hop)
      if (!(Number.isInteger(diem) && diem >= 1 && diem <= 5)) {
        throw new Error(`Phần tử thứ ${line}: diem_phu_hop phải là số nguyên 1-5`)
      }
      return {
        thcs_huong_di_id: huongTuJson(item, line),
        thcs_tieu_chi_id: tieuChiTuJson(item, line),
        diem_phu_hop: diem,
        nhan_dinh_tu_van: giaTriTuyChon(item.nhan_dinh_tu_van),
      }
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({
    items,
    createBatch: huongDiTieuChiApi.createBulk,
    jsonText,
    saving,
    dialogVisible,
    reload: load,
  })
}

async function onSubmit() {
  if (!dangSua.value && createMode.value === 'json') {
    await onSubmitJson()
    return
  }
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const phan = { diem_phu_hop: form.diem_phu_hop, nhan_dinh_tu_van: giaTriTuyChon(form.nhan_dinh_tu_van) }
    if (dangSua.value) {
      await huongDiTieuChiApi.update(dangSua.value.thcs_huong_di_id, dangSua.value.thcs_tieu_chi_id, phan)
      ElMessage.success('Đã cập nhật điểm phù hợp')
    } else {
      await huongDiTieuChiApi.create({
        thcs_huong_di_id: form.thcs_huong_di_id,
        thcs_tieu_chi_id: form.thcs_tieu_chi_id,
        ...phan,
      })
      ElMessage.success('Đã chấm điểm phù hợp')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được điểm phù hợp'))
  } finally {
    saving.value = false
  }
}

async function xacNhanXoa(noiDung) {
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
  if (!(await xacNhanXoa(`Xóa điểm của tiêu chí "${row.ten_tieu_chi}" khỏi hướng đi "${row.ten_huong}"?`))) return
  try {
    await huongDiTieuChiApi.remove(row.thcs_huong_di_id, row.thcs_tieu_chi_id)
    ElMessage.success('Đã xóa điểm phù hợp')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được điểm phù hợp'))
  }
}

async function onDeleteSelected() {
  const items = selectedRows.value.map((row) => ({
    thcs_huong_di_id: row.thcs_huong_di_id,
    thcs_tieu_chi_id: row.thcs_tieu_chi_id,
  }))
  if (!items.length) return
  if (!(await xacNhanXoa(`Xóa ${items.length} điểm phù hợp đã chọn?`))) return

  deleting.value = true
  try {
    const daChon = new Set(selectedRows.value.map(khoa))
    const removedOnPage = rows.value.filter((row) => daChon.has(khoa(row))).length
    const result = await huongDiTieuChiApi.removeMany(items)
    ElMessage.success(`Đã xóa ${result.deleted} điểm phù hợp`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các điểm phù hợp đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadHuongOptions()
  loadTieuChiOptions()
  load()
})
</script>
