<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên hướng đi"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect v-model="filters.loai_hinh" placeholder="Chọn loại hình" clearable @change="onSearch">
          <CustomOption v-for="item in LOAI_HINH_DU_HOC" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <CustomSelect v-model="filters.trang_thai" placeholder="Chọn trạng thái" clearable @change="onSearch">
          <CustomOption label="Hoạt động" :value="1" />
          <CustomOption label="Ngừng sử dụng" :value="0" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách hướng đi du học</h2>
        <div class="toolbar__actions">
          <!-- Bật chỉ áp dụng cho dòng đã chọn đang tắt, Tắt cho dòng đang bật; badge là số dòng sẽ đổi. -->
          <CustomBadge :value="idsDangTat.length" :hidden="!idsDangTat.length" type="success">
            <CustomButton
              type="success"
              plain
              :disabled="!idsDangTat.length"
              :loading="dangDoiNhieu === 1"
              @click="doiTrangThaiDaChon(1)"
            >
              <CustomIcon><CircleCheck /></CustomIcon>
              Bật
            </CustomButton>
          </CustomBadge>
          <CustomBadge :value="idsDangBat.length" :hidden="!idsDangBat.length" type="warning">
            <CustomButton
              type="warning"
              plain
              :disabled="!idsDangBat.length"
              :loading="dangDoiNhieu === 0"
              @click="doiTrangThaiDaChon(0)"
            >
              <CustomIcon><CircleClose /></CustomIcon>
              Tắt
            </CustomButton>
          </CustomBadge>
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
            Thêm hướng đi
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
        <CustomTableColumn prop="ma_huong" label="Mã hướng đi" width="170" />
        <CustomTableColumn prop="ten_huong" label="Tên hướng đi" min-width="220" />
        <CustomTableColumn label="Loại hình" width="160" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauEnum(LOAI_HINH_DU_HOC, row.loai_hinh)" effect="light">
              {{ nhanEnum(LOAI_HINH_DU_HOC, row.loai_hinh) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Yêu cầu ngoại ngữ" min-width="220">
          <template #default="{ row }">{{ row.yeu_cau_ngoai_ngu || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thời gian chuẩn bị" min-width="180">
          <template #default="{ row }">{{ row.thoi_gian_chuan_bi_text || khoangThang(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Chi phí dự kiến" min-width="220">
          <template #default="{ row }">{{ row.chi_phi_du_kien_text || '—' }}</template>
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
              :aria-label="`Trạng thái ${row.ten_huong}`"
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_huong)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có hướng đi du học nào." />
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
    :title="editingId ? 'Cập nhật hướng đi du học' : 'Thêm hướng đi du học'"
    width="90%"
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
      <CustomInput v-model="jsonText" class="json-input" type="textarea" :rows="16" placeholder="Dán mảng JSON vào đây" />
    </div>

    <CustomForm v-else ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <CustomFormItem label="Mã hướng đi" prop="ma_huong">
          <CustomInput v-model="form.ma_huong" maxlength="50" placeholder="Nhập mã hướng đi (ví dụ: DU_HOC_NGHE)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên hướng đi" prop="ten_huong">
          <CustomInput v-model="form.ten_huong" maxlength="255" placeholder="Nhập tên hướng đi" />
        </CustomFormItem>
        <CustomFormItem label="Loại hình" prop="loai_hinh">
          <CustomSelect v-model="form.loai_hinh" placeholder="Chọn loại hình">
            <CustomOption v-for="item in LOAI_HINH_DU_HOC" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Trạng thái" prop="trang_thai">
          <CustomSelect v-model="form.trang_thai" placeholder="Chọn trạng thái" :clearable="false">
            <CustomOption label="Hoạt động" :value="1" />
            <CustomOption label="Ngừng sử dụng" :value="0" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Yêu cầu ngoại ngữ" prop="yeu_cau_ngoai_ngu">
          <CustomInput v-model="form.yeu_cau_ngoai_ngu" maxlength="255" placeholder="Nhập yêu cầu ngoại ngữ" />
        </CustomFormItem>

        <CustomFormItem class="form-grid__span-2" label="Thời gian chuẩn bị (mô tả)" prop="thoi_gian_chuan_bi_text">
          <CustomInput
            v-model="form.thoi_gian_chuan_bi_text"
            maxlength="100"
            placeholder="Nhập thời gian chuẩn bị (ví dụ: 8 - 18 tháng)"
          />
        </CustomFormItem>
        <CustomFormItem label="Chuẩn bị tối thiểu (tháng)" prop="thoi_gian_chuan_bi_thang_min">
          <CustomInputNumber
            v-model="form.thoi_gian_chuan_bi_thang_min"
            placeholder="Nhập số tháng tối thiểu"
            :min="0"
            :max="120"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Chuẩn bị tối đa (tháng)" prop="thoi_gian_chuan_bi_thang_max">
          <CustomInputNumber
            v-model="form.thoi_gian_chuan_bi_thang_max"
            placeholder="Nhập số tháng tối đa"
            :min="0"
            :max="120"
            :precision="0"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Chi phí dự kiến (mô tả)" prop="chi_phi_du_kien_text">
          <CustomInput
            v-model="form.chi_phi_du_kien_text"
            maxlength="255"
            placeholder="Nhập chi phí dự kiến (ví dụ: 150 - 350 triệu VNĐ)"
          />
        </CustomFormItem>

        <CustomFormItem class="form-grid__full" label="Mô tả đặc điểm" prop="mo_ta_dac_diem">
          <CustomInput
            v-model="form.mo_ta_dac_diem"
            type="textarea"
            :rows="3"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập mô tả đặc điểm"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Cơ hội làm thêm" prop="co_hoi_lam_them">
          <CustomInput
            v-model="form.co_hoi_lam_them"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập cơ hội làm thêm"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Lộ trình visa, định cư" prop="lo_trinh_visa_dinh_cu">
          <CustomInput
            v-model="form.lo_trinh_visa_dinh_cu"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập lộ trình visa, định cư"
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { huongDiApi } from '@/api/thptDuHoc'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangDuHoc } from '@/composables/useThptDuHoc'
import { LOAI_HINH_DU_HOC, mauEnum, nhanEnum } from '@/constants/thptDuHoc'

const TRUONG_TUY_CHON = [
  'yeu_cau_ngoai_ngu',
  'thoi_gian_chuan_bi_text',
  'thoi_gian_chuan_bi_thang_min',
  'thoi_gian_chuan_bi_thang_max',
  'chi_phi_du_kien_text',
  'co_hoi_lam_them',
  'lo_trinh_visa_dinh_cu',
]

const JSON_SAMPLE = `[
  {
    "ma_huong": "DU_HOC_NGHE",
    "ten_huong": "Du học nghề",
    "loai_hinh": "du_hoc_nghe",
    "mo_ta_dac_diem": "Học nghề kết hợp thực hành tại doanh nghiệp.",
    "yeu_cau_ngoai_ngu": "Tiếng Đức B1-B2",
    "thoi_gian_chuan_bi_text": "8 - 18 tháng",
    "thoi_gian_chuan_bi_thang_min": 8,
    "thoi_gian_chuan_bi_thang_max": 18,
    "chi_phi_du_kien_text": "150 - 350 triệu VNĐ"
  }
]`

const filters = reactive({ q: '', loai_hinh: '', trang_thai: '' })

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
  clearSelection,
  onSelectionChange,
  rowIndex,
  onSearch,
  onDelete,
  onDeleteSelected,
} = useBangDuHoc({
  api: huongDiApi,
  nhan: 'hướng đi',
  canhBaoXoa: 'Quốc gia, ngành, chi phí, thủ tục và kênh kết nối của hướng đi cũng bị xóa theo.',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.loai_hinh) params.loai_hinh = filters.loai_hinh
    if (filters.trang_thai !== '' && filters.trang_thai !== null) params.trang_thai = filters.trang_thai
    return params
  },
})

const idsDangBat = computed(() => selectedRows.value.filter((row) => row.trang_thai === 1).map((row) => row.id))
const idsDangTat = computed(() => selectedRows.value.filter((row) => row.trang_thai !== 1).map((row) => row.id))
// Trạng thái đang áp dụng cho các dòng đã chọn (1 bật / 0 tắt), null khi không chạy.
const dangDoiNhieu = ref(null)
const dangDoiTrangThai = ref({})
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'hướng đi' })
const formRef = ref()
const form = reactive(emptyForm())

function kiemTraKhoang(_rule, value, callback) {
  const min = form.thoi_gian_chuan_bi_thang_min
  if (value != null && min != null && min > value) callback(new Error('Tối đa phải ≥ tối thiểu'))
  else callback()
}

const rules = {
  ma_huong: [{ required: true, message: 'Vui lòng nhập mã hướng đi', trigger: 'blur' }],
  ten_huong: [{ required: true, message: 'Vui lòng nhập tên hướng đi', trigger: 'blur' }],
  loai_hinh: [{ required: true, message: 'Vui lòng chọn loại hình', trigger: 'change' }],
  mo_ta_dac_diem: [{ required: true, message: 'Vui lòng nhập mô tả đặc điểm', trigger: 'blur' }],
  thoi_gian_chuan_bi_thang_max: [{ validator: kiemTraKhoang, trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_huong: '',
    ten_huong: '',
    loai_hinh: '',
    mo_ta_dac_diem: '',
    yeu_cau_ngoai_ngu: '',
    thoi_gian_chuan_bi_text: '',
    thoi_gian_chuan_bi_thang_min: undefined,
    thoi_gian_chuan_bi_thang_max: undefined,
    chi_phi_du_kien_text: '',
    co_hoi_lam_them: '',
    lo_trinh_visa_dinh_cu: '',
    trang_thai: 1,
  }
}

function khoangThang(row) {
  const tu = row.thoi_gian_chuan_bi_thang_min
  const den = row.thoi_gian_chuan_bi_thang_max
  if (!tu && !den) return '—'
  return tu === den || !den ? `${tu} tháng` : `${tu || 0} - ${den} tháng`
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
  const payload = {
    ma_huong: String(item.ma_huong ?? '').trim().toUpperCase(),
    ten_huong: String(item.ten_huong ?? '').trim(),
    loai_hinh: item.loai_hinh,
    mo_ta_dac_diem: String(item.mo_ta_dac_diem ?? '').trim(),
    trang_thai: item.trang_thai ?? 1,
  }
  for (const key of TRUONG_TUY_CHON) payload[key] = giaTriTuyChon(item[key])
  return payload
}

function openCreate() {
  resetForm()
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

async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    const data = await huongDiApi.updateTrangThai(row.id, moi)
    row.trang_thai = data.trang_thai
    ElMessage.success(moi === 1 ? `Đã bật "${row.ten_huong}"` : `Đã tắt "${row.ten_huong}"`)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái'))
  } finally {
    const conLai = { ...dangDoiTrangThai.value }
    delete conLai[row.id]
    dangDoiTrangThai.value = conLai
  }
  return false
}

async function doiTrangThaiDaChon(trangThai) {
  const ids = trangThai === 1 ? idsDangTat.value : idsDangBat.value
  if (!ids.length) return
  const hanhDong = trangThai === 1 ? 'Bật' : 'Tắt'
  try {
    await ElMessageBox.confirm(
      `${hanhDong} ${ids.length} hướng đi đã chọn đang ${trangThai === 1 ? 'tắt' : 'bật'}?`,
      `Xác nhận ${hanhDong.toLowerCase()} hướng đi`,
      {
        type: 'warning',
        confirmButtonText: hanhDong,
        cancelButtonText: 'Hủy',
        confirmButtonClass: trangThai === 1 ? 'el-button--success' : 'el-button--warning',
      },
    )
  } catch {
    return
  }
  dangDoiNhieu.value = trangThai
  try {
    const result = await huongDiApi.updateTrangThaiMany(ids, trangThai)
    ElMessage.success(`Đã ${trangThai === 1 ? 'bật' : 'tắt'} ${result.updated} hướng đi`)
    clearSelection()
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái các hướng đi đã chọn'))
  } finally {
    dangDoiNhieu.value = null
  }
}

async function onSubmitJson() {
  let items
  try {
    items = docMangJson(jsonText.value, 'hướng đi').map((item, index) => {
      const payload = chuanHoa(item)
      if (!payload.ma_huong || !payload.ten_huong || !payload.loai_hinh || !payload.mo_ta_dac_diem) {
        throw new Error(`Phần tử thứ ${index + 1} thiếu ma_huong, ten_huong, loai_hinh hoặc mo_ta_dac_diem`)
      }
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: huongDiApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await huongDiApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật hướng đi')
    } else {
      await huongDiApi.create(payload)
      ElMessage.success('Đã thêm hướng đi')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được hướng đi'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
