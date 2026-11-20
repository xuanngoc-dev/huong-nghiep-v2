<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên hướng đi, mã Holland"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.muc_do_ap_luc_hoc_tap"
          placeholder="Chọn áp lực học tập"
          clearable
          @change="onSearch"
        >
          <CustomOption v-for="item in MUC_DO_AP_LUC_HOC_TAP" :key="item.value" :label="item.label" :value="item.value" />
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
        <h2 class="toolbar__title">Danh sách hướng đi sau THCS</h2>
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
        <CustomTableColumn label="Chi phí dự kiến" min-width="200">
          <template #default="{ row }">{{ row.chi_phi_du_kien_text || khoangChiPhi(row) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Áp lực học tập" width="140" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauEnum(MUC_DO_AP_LUC_HOC_TAP, row.muc_do_ap_luc_hoc_tap)" effect="light">
              {{ nhanEnum(MUC_DO_AP_LUC_HOC_TAP, row.muc_do_ap_luc_hoc_tap) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Mức tự giác" width="130" align="center">
          <template #default="{ row }">
            <CustomTag :type="mauEnum(MUC_DO_TU_GIAC, row.muc_do_tu_giac_can_thiet)" effect="light">
              {{ nhanEnum(MUC_DO_TU_GIAC, row.muc_do_tu_giac_can_thiet) }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Mã Holland" width="120" align="center">
          <template #default="{ row }">{{ row.ma_holland || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="thu_tu_hien_thi" label="Thứ tự" width="90" align="center" />
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
          <CustomEmpty description="Chưa có hướng đi sau THCS nào." />
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
    :title="editingId ? 'Cập nhật hướng đi sau THCS' : 'Thêm hướng đi sau THCS'"
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
          <CustomInput v-model="form.ma_huong" maxlength="50" placeholder="Nhập mã hướng đi (ví dụ: THPT_CONG_LAP)" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Tên hướng đi" prop="ten_huong">
          <CustomInput v-model="form.ten_huong" maxlength="255" placeholder="Nhập tên hướng đi" />
        </CustomFormItem>
        <CustomFormItem label="Mã Holland" prop="ma_holland">
          <CustomInput v-model="form.ma_holland" maxlength="20" placeholder="Nhập mã Holland (ví dụ: RIE)" />
        </CustomFormItem>
        <CustomFormItem label="Thứ tự hiển thị" prop="thu_tu_hien_thi">
          <CustomInputNumber
            v-model="form.thu_tu_hien_thi"
            placeholder="Nhập thứ tự hiển thị"
            :min="0"
            :max="100000"
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

        <CustomFormItem class="form-grid__span-2" label="Chi phí dự kiến (mô tả)" prop="chi_phi_du_kien_text">
          <CustomInput
            v-model="form.chi_phi_du_kien_text"
            maxlength="255"
            placeholder="Nhập chi phí dự kiến (ví dụ: 1 - 3 triệu VNĐ/tháng)"
          />
        </CustomFormItem>
        <CustomFormItem label="Chi phí tối thiểu (VNĐ/tháng)" prop="chi_phi_thang_min">
          <CustomInputNumber
            v-model="form.chi_phi_thang_min"
            placeholder="Nhập chi phí tối thiểu"
            :min="0"
            :max="99999999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Chi phí tối đa (VNĐ/tháng)" prop="chi_phi_thang_max">
          <CustomInputNumber
            v-model="form.chi_phi_thang_max"
            placeholder="Nhập chi phí tối đa"
            :min="0"
            :max="99999999.99"
            :precision="2"
            controls-position="right"
          />
        </CustomFormItem>
        <CustomFormItem label="Áp lực học tập" prop="muc_do_ap_luc_hoc_tap">
          <CustomSelect v-model="form.muc_do_ap_luc_hoc_tap" placeholder="Chọn áp lực học tập" :clearable="false">
            <CustomOption
              v-for="item in MUC_DO_AP_LUC_HOC_TAP"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Mức tự giác cần thiết" prop="muc_do_tu_giac_can_thiet">
          <CustomSelect v-model="form.muc_do_tu_giac_can_thiet" placeholder="Chọn mức tự giác" :clearable="false">
            <CustomOption v-for="item in MUC_DO_TU_GIAC" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>

        <CustomFormItem class="form-grid__full" label="Mô tả tổng quan" prop="mo_ta_tong_quan">
          <CustomInput
            v-model="form.mo_ta_tong_quan"
            type="textarea"
            :rows="3"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập mô tả tổng quan"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Đối tượng phù hợp" prop="doi_tuong_phu_hop">
          <CustomInput
            v-model="form.doi_tuong_phu_hop"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập đối tượng phù hợp"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Tính linh hoạt sau lớp 12" prop="tinh_linh_hoat_sau_lop_12">
          <CustomInput
            v-model="form.tinh_linh_hoat_sau_lop_12"
            type="textarea"
            :rows="2"
            maxlength="5000"
            placeholder="Nhập tính linh hoạt sau lớp 12"
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
import { huongDiApi } from '@/api/thcsHuongDi'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { docMangJson, errorMessage, giaTriTuyChon, useBangThcs } from '@/composables/useThcsHuongDi'
import { MUC_DO_AP_LUC_HOC_TAP, MUC_DO_TU_GIAC, mauEnum, nhanEnum } from '@/constants/thcsHuongDi'

const TRUONG_TUY_CHON = [
  'doi_tuong_phu_hop',
  'chi_phi_du_kien_text',
  'chi_phi_thang_min',
  'chi_phi_thang_max',
  'tinh_linh_hoat_sau_lop_12',
  'ma_holland',
]

const JSON_SAMPLE = `[
  {
    "ma_huong": "THPT_CONG_LAP",
    "ten_huong": "Học THPT công lập",
    "mo_ta_tong_quan": "Thi tuyển vào lớp 10 trường công lập, học chương trình phổ thông 3 năm.",
    "doi_tuong_phu_hop": "Học sinh có học lực khá trở lên, muốn thi đại học",
    "chi_phi_du_kien_text": "0,5 - 2 triệu VNĐ/tháng",
    "chi_phi_thang_min": 500000,
    "chi_phi_thang_max": 2000000,
    "muc_do_ap_luc_hoc_tap": "cao",
    "muc_do_tu_giac_can_thiet": "cao",
    "tinh_linh_hoat_sau_lop_12": "Thi đại học, cao đẳng, du học hoặc đi làm",
    "ma_holland": "IAS",
    "thu_tu_hien_thi": 1
  }
]`

const filters = reactive({ q: '', trang_thai: '', muc_do_ap_luc_hoc_tap: '' })

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
} = useBangThcs({
  api: huongDiApi,
  nhan: 'hướng đi',
  canhBaoXoa: 'Ưu/nhược điểm, điểm phù hợp theo tiêu chí và lời khuyên của hướng đi cũng bị xóa theo.',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai !== '' && filters.trang_thai !== null) params.trang_thai = filters.trang_thai
    if (filters.muc_do_ap_luc_hoc_tap) params.muc_do_ap_luc_hoc_tap = filters.muc_do_ap_luc_hoc_tap
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

function kiemTraKhoangChiPhi(_rule, value, callback) {
  const min = form.chi_phi_thang_min
  if (value != null && min != null && min > value) callback(new Error('Tối đa phải ≥ tối thiểu'))
  else callback()
}

const rules = {
  ma_huong: [{ required: true, message: 'Vui lòng nhập mã hướng đi', trigger: 'blur' }],
  ten_huong: [{ required: true, message: 'Vui lòng nhập tên hướng đi', trigger: 'blur' }],
  mo_ta_tong_quan: [{ required: true, message: 'Vui lòng nhập mô tả tổng quan', trigger: 'blur' }],
  chi_phi_thang_max: [{ validator: kiemTraKhoangChiPhi, trigger: 'change' }],
}

function emptyForm() {
  return {
    ma_huong: '',
    ten_huong: '',
    mo_ta_tong_quan: '',
    doi_tuong_phu_hop: '',
    chi_phi_du_kien_text: '',
    chi_phi_thang_min: undefined,
    chi_phi_thang_max: undefined,
    muc_do_ap_luc_hoc_tap: 'trung_binh',
    muc_do_tu_giac_can_thiet: 'cao',
    tinh_linh_hoat_sau_lop_12: '',
    ma_holland: '',
    thu_tu_hien_thi: 0,
    trang_thai: 1,
  }
}

const dinhDangSo = new Intl.NumberFormat('vi-VN')

function khoangChiPhi(row) {
  const tu = row.chi_phi_thang_min == null ? null : Number(row.chi_phi_thang_min)
  const den = row.chi_phi_thang_max == null ? null : Number(row.chi_phi_thang_max)
  if (tu == null && den == null) return '—'
  if (tu == null || den == null || tu === den) return `${dinhDangSo.format(tu ?? den)} VNĐ/tháng`
  return `${dinhDangSo.format(tu)} - ${dinhDangSo.format(den)} VNĐ/tháng`
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
    mo_ta_tong_quan: String(item.mo_ta_tong_quan ?? '').trim(),
    muc_do_ap_luc_hoc_tap: item.muc_do_ap_luc_hoc_tap || 'trung_binh',
    muc_do_tu_giac_can_thiet: item.muc_do_tu_giac_can_thiet || 'cao',
    thu_tu_hien_thi: Number(item.thu_tu_hien_thi) || 0,
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
    values[key] = key.startsWith('chi_phi_thang') ? Number(row[key]) : row[key]
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
      if (!payload.ma_huong || !payload.ten_huong || !payload.mo_ta_tong_quan) {
        throw new Error(`Phần tử thứ ${index + 1} thiếu ma_huong, ten_huong hoặc mo_ta_tong_quan`)
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
