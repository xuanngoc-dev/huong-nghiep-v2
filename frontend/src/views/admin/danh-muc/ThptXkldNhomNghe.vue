<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên nhóm nghề"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
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
        <h2 class="toolbar__title">Danh sách nhóm nghề xuất khẩu lao động</h2>
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
            Thêm nhóm nghề
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
        <CustomTableColumn prop="ma_nhom" label="Mã nhóm nghề" width="170" />
        <CustomTableColumn prop="ten_nhom" label="Tên nhóm nghề" min-width="220" />
        <CustomTableColumn label="Yêu cầu ngoại ngữ" min-width="220">
          <template #default="{ row }">{{ row.yeu_cau_ngoai_ngu || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thời gian chuẩn bị" min-width="180">
          <template #default="{ row }">{{ row.thoi_gian_chuan_bi_text || khoangThang(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thu nhập" min-width="200">
          <template #default="{ row }">{{ row.muc_thu_nhap_text || khoangThuNhap(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Gia hạn visa" min-width="200">
          <template #default="{ row }">{{ row.kha_nang_gia_han_visa || '—' }}</template>
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
              :aria-label="`Trạng thái ${row.ten_nhom}`"
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
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.ten_nhom)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có nhóm nghề xuất khẩu lao động nào." />
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
    :title="editingId ? 'Cập nhật nhóm nghề xuất khẩu lao động' : 'Thêm nhóm nghề xuất khẩu lao động'"
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
        <CustomFormItem label="Mã nhóm nghề" prop="ma_nhom">
          <CustomInput v-model="form.ma_nhom" maxlength="50" placeholder="Nhập mã nhóm nghề (ví dụ: CO_KHI)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên nhóm nghề" prop="ten_nhom">
          <CustomInput v-model="form.ten_nhom" maxlength="255" placeholder="Nhập tên nhóm nghề" />
        </CustomFormItem>
        <CustomFormItem label="Trạng thái" prop="trang_thai">
          <CustomSelect v-model="form.trang_thai" placeholder="Chọn trạng thái" :clearable="false">
            <CustomOption label="Hoạt động" :value="1" />
            <CustomOption label="Ngừng sử dụng" :value="0" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Yêu cầu ngoại ngữ" prop="yeu_cau_ngoai_ngu">
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
        <CustomFormItem class="form-grid__span-2" label="Mức thu nhập (mô tả)" prop="muc_thu_nhap_text">
          <CustomInput
            v-model="form.muc_thu_nhap_text"
            maxlength="255"
            placeholder="Nhập mức thu nhập (ví dụ: 28 - 35 triệu VNĐ/tháng)"
          />
        </CustomFormItem>
        <CustomFormItem label="Thu nhập tối thiểu (triệu VNĐ/tháng)" prop="thu_nhap_thang_min">
          <CustomInputNumber
            v-model="form.thu_nhap_thang_min"
            placeholder="Nhập thu nhập tối thiểu"
            :min="0"
            :max="999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Thu nhập tối đa (triệu VNĐ/tháng)" prop="thu_nhap_thang_max">
          <CustomInputNumber
            v-model="form.thu_nhap_thang_max"
            placeholder="Nhập thu nhập tối đa"
            :min="0"
            :max="999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Khả năng gia hạn visa" prop="kha_nang_gia_han_visa">
          <CustomInput v-model="form.kha_nang_gia_han_visa" maxlength="255" placeholder="Nhập khả năng gia hạn visa" />
        </CustomFormItem>

        <CustomFormItem class="form-grid__full" label="Mô tả công việc" prop="mo_ta_cong_viec">
          <CustomInput
            v-model="form.mo_ta_cong_viec"
            type="textarea"
            :rows="3"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập mô tả công việc"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Điều kiện sức khỏe, thể lực" prop="dieu_kien_suc_khoe_the_luc">
          <CustomInput
            v-model="form.dieu_kien_suc_khoe_the_luc"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập điều kiện sức khỏe, thể lực"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Triển vọng sau khi về nước" prop="trien_vong_sau_ve_nuoc">
          <CustomInput
            v-model="form.trien_vong_sau_ve_nuoc"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập triển vọng sau khi về nước"
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
import { nhomNgheApi } from '@/api/thptXkld'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangXkld } from '@/composables/useThptXkld'

const TRUONG_TUY_CHON = [
  'yeu_cau_ngoai_ngu',
  'thoi_gian_chuan_bi_text',
  'thoi_gian_chuan_bi_thang_min',
  'thoi_gian_chuan_bi_thang_max',
  'muc_thu_nhap_text',
  'thu_nhap_thang_min',
  'thu_nhap_thang_max',
  'dieu_kien_suc_khoe_the_luc',
  'trien_vong_sau_ve_nuoc',
  'kha_nang_gia_han_visa',
]

const JSON_SAMPLE = `[
  {
    "ma_nhom": "CO_KHI",
    "ten_nhom": "Cơ khí, hàn, gia công kim loại",
    "mo_ta_cong_viec": "Vận hành máy, hàn, tiện, lắp ráp chi tiết kim loại tại nhà máy.",
    "dieu_kien_suc_khoe_the_luc": "Sức khỏe tốt, không mắc bệnh truyền nhiễm, thị lực đạt yêu cầu",
    "yeu_cau_ngoai_ngu": "Tiếng Nhật N4-N5",
    "thoi_gian_chuan_bi_text": "4 - 8 tháng",
    "thoi_gian_chuan_bi_thang_min": 4,
    "thoi_gian_chuan_bi_thang_max": 8,
    "muc_thu_nhap_text": "28 - 35 triệu VNĐ/tháng",
    "thu_nhap_thang_min": 28,
    "thu_nhap_thang_max": 35,
    "kha_nang_gia_han_visa": "Chuyển sang kỹ năng đặc định sau 3 năm"
  }
]`

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
  clearSelection,
  onSelectionChange,
  rowIndex,
  onSearch,
  onDelete,
  onDeleteSelected,
} = useBangXkld({
  api: nhomNgheApi,
  nhan: 'nhóm nghề',
  canhBaoXoa: 'Thị trường, nghề cụ thể, chi phí, thủ tục và kênh kết nối của nhóm nghề cũng bị xóa theo.',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
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
const jsonImport = useJsonBatchImport({ label: 'nhóm nghề' })
const formRef = ref()
const form = reactive(emptyForm())

function kiemTraKhoang(_rule, value, callback) {
  const min = form.thoi_gian_chuan_bi_thang_min
  if (value != null && min != null && min > value) callback(new Error('Tối đa phải ≥ tối thiểu'))
  else callback()
}

function kiemTraKhoangThuNhap(_rule, value, callback) {
  const min = form.thu_nhap_thang_min
  if (value != null && min != null && min > value) callback(new Error('Tối đa phải ≥ tối thiểu'))
  else callback()
}

const rules = {
  ma_nhom: [{ required: true, message: 'Vui lòng nhập mã nhóm nghề', trigger: 'blur' }],
  ten_nhom: [{ required: true, message: 'Vui lòng nhập tên nhóm nghề', trigger: 'blur' }],
  mo_ta_cong_viec: [{ required: true, message: 'Vui lòng nhập mô tả công việc', trigger: 'blur' }],
  thoi_gian_chuan_bi_thang_max: [{ validator: kiemTraKhoang, trigger: 'change' }],
  thu_nhap_thang_max: [{ validator: kiemTraKhoangThuNhap, trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_nhom: '',
    ten_nhom: '',
    mo_ta_cong_viec: '',
    dieu_kien_suc_khoe_the_luc: '',
    yeu_cau_ngoai_ngu: '',
    thoi_gian_chuan_bi_text: '',
    thoi_gian_chuan_bi_thang_min: undefined,
    thoi_gian_chuan_bi_thang_max: undefined,
    muc_thu_nhap_text: '',
    thu_nhap_thang_min: undefined,
    thu_nhap_thang_max: undefined,
    trien_vong_sau_ve_nuoc: '',
    kha_nang_gia_han_visa: '',
    trang_thai: 1,
  }
}

function khoangThang(row) {
  const tu = row.thoi_gian_chuan_bi_thang_min
  const den = row.thoi_gian_chuan_bi_thang_max
  if (!tu && !den) return '—'
  return tu === den || !den ? `${tu} tháng` : `${tu || 0} - ${den} tháng`
}

function khoangThuNhap(row) {
  const tu = row.thu_nhap_thang_min == null ? null : Number(row.thu_nhap_thang_min)
  const den = row.thu_nhap_thang_max == null ? null : Number(row.thu_nhap_thang_max)
  if (tu == null && den == null) return '—'
  return tu == null || den == null || tu === den ? `${tu ?? den} triệu VNĐ` : `${tu} - ${den} triệu VNĐ`
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
    ma_nhom: String(item.ma_nhom ?? '').trim().toUpperCase(),
    ten_nhom: String(item.ten_nhom ?? '').trim(),
    mo_ta_cong_viec: String(item.mo_ta_cong_viec ?? '').trim(),
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
    if (row[key] == null) continue
    // Decimal trả về dạng chuỗi, đổi sang số cho CustomInputNumber.
    values[key] = key.startsWith('thu_nhap_thang') ? Number(row[key]) : row[key]
  }
  Object.assign(form, values)
  dialogVisible.value = true
}

async function doiTrangThai(row) {
  const moi = row.trang_thai === 1 ? 0 : 1
  dangDoiTrangThai.value = { ...dangDoiTrangThai.value, [row.id]: true }
  try {
    const data = await nhomNgheApi.updateTrangThai(row.id, moi)
    row.trang_thai = data.trang_thai
    ElMessage.success(moi === 1 ? `Đã bật "${row.ten_nhom}"` : `Đã tắt "${row.ten_nhom}"`)
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
      `${hanhDong} ${ids.length} nhóm nghề đã chọn đang ${trangThai === 1 ? 'tắt' : 'bật'}?`,
      `Xác nhận ${hanhDong.toLowerCase()} nhóm nghề`,
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
    const result = await nhomNgheApi.updateTrangThaiMany(ids, trangThai)
    ElMessage.success(`Đã ${trangThai === 1 ? 'bật' : 'tắt'} ${result.updated} nhóm nghề`)
    clearSelection()
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được trạng thái các nhóm nghề đã chọn'))
  } finally {
    dangDoiNhieu.value = null
  }
}

async function onSubmitJson() {
  let items
  try {
    items = docMangJson(jsonText.value, 'nhóm nghề').map((item, index) => {
      const payload = chuanHoa(item)
      if (!payload.ma_nhom || !payload.ten_nhom || !payload.mo_ta_cong_viec) {
        throw new Error(`Phần tử thứ ${index + 1} thiếu ma_nhom, ten_nhom hoặc mo_ta_cong_viec`)
      }
      return payload
    })
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  await jsonImport.run({ items, createBatch: nhomNgheApi.createBulk, jsonText, saving, dialogVisible, reload: load })
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
      await nhomNgheApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật nhóm nghề')
    } else {
      await nhomNgheApi.create(payload)
      ElMessage.success('Đã thêm nhóm nghề')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được nhóm nghề'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
