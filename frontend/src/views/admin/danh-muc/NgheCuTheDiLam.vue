<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tên nghề, mã, tên nhóm"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.nhom_nghe_di_lam_id"
          class="filter-parent"
          placeholder="Chọn nhóm nghề"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.co_bang_cap"
          placeholder="Bằng cấp bắt buộc"
          clearable
          @change="onSearch"
        >
          <CustomOption label="Có yêu cầu bằng cấp" :value="1" />
          <CustomOption label="Không yêu cầu bằng cấp" :value="0" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.chinh_quy"
          placeholder="Đào tạo chính quy"
          clearable
          @change="onSearch"
        >
          <CustomOption label="Bắt buộc chính quy" :value="1" />
          <CustomOption label="Không bắt buộc" :value="0" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách nghề cụ thể</h2>
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
            Thêm nghề
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
        <CustomTableColumn label="Hình ảnh" width="100" align="center">
          <template #default="{ row }">
            <img v-if="row.hinh_anh_mo_ta" class="thumb" :src="apiAssetUrl(row.hinh_anh_mo_ta)" :alt="row.ten_nghe" />
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_nghe" label="Tên nghề" min-width="220" />
        <CustomTableColumn label="Nhóm nghề" min-width="240">
          <template #default="{ row }">{{ row.ten_nhom }} ({{ row.ma_nhom }})</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mô tả ngắn" min-width="280">
          <template #default="{ row }">{{ row.mo_ta_ngan || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Yêu cầu thêm" min-width="200">
          <template #default="{ row }">{{ row.yeu_cau_them || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Bằng cấp bắt buộc" min-width="220">
          <template #default="{ row }">{{ row.yeu_cau_bang_cap || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Đào tạo chính quy" width="170" align="center">
          <template #default="{ row }">
            <CustomTag v-if="row.bat_buoc_dao_tao_chinh_quy" type="warning" size="small">Bắt buộc</CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Holland" width="100" align="center">
          <template #default="{ row }">{{ row.nhom_holland || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Mức độ áp lực" width="150" align="center">
          <template #default="{ row }">
            <CustomTag v-if="nhanMucDoApLuc(row.muc_do_ap_luc)" :type="nhanMucDoApLuc(row.muc_do_ap_luc).mau" size="small">
              {{ nhanMucDoApLuc(row.muc_do_ap_luc).label }}
            </CustomTag>
            <span v-else>—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Trình độ tối thiểu" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.trinh_do_toi_thieu || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Hình thức đào tạo" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ row.hinh_thuc_dao_tao || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn v-for="muc in KHOANG_LUONG" :key="muc.key" :label="muc.label" min-width="230">
          <template #default="{ row }">{{ khoangLuong(row, muc.key) || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn
          v-for="cot in COT_CHU_BANG"
          :key="cot.key"
          :label="cot.label"
          :min-width="cot.rong"
          show-overflow-tooltip
        >
          <template #default="{ row }">{{ (cot.hienThi ? cot.hienThi(row[cot.key]) : row[cot.key]) || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thao tác" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <CustomTooltip content="Xem chi tiết" placement="top">
                <CustomButton link type="primary" aria-label="Xem chi tiết" @click="openChiTiet(row)">
                  <CustomIcon><View /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
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
          <CustomEmpty description="Chưa có nghề cụ thể nào." />
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

  <ChiTietNgheCuThe v-model="chiTietMo" :nghe="ngheDangXem" @sua="suaTuChiTiet" />

  <CustomDialog
    v-model="dialogVisible"
    :title="editingId ? 'Cập nhật nghề cụ thể' : 'Thêm nghề cụ thể'"
    width="80%"
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
        placeholder="Dán mảng JSON vào đây (dùng ma_nhom hoặc nhom_nghe_di_lam_id)"
      />
    </div>

    <!-- Bố cục giống modal Chi tiết (ChiTietNgheCuThe): 4 ô/hàng trên desktop, 2 ô/hàng trên mobile, ô nhiều dòng cả hàng. -->
    <CustomForm v-else ref="formRef" class="form-grid form-grid--toi-da-4" :model="form" :rules="rules" label-position="top">
      <div class="form-grid__body">
        <h3 class="form-grid__full nhom-truong">Thông tin chung</h3>
        <CustomFormItem label="Tên nghề" prop="ten_nghe">
          <CustomInput v-model="form.ten_nghe" maxlength="255" placeholder="Nhập tên nghề" />
        </CustomFormItem>
        <CustomFormItem label="Nhóm nghề" prop="nhom_nghe_di_lam_id">
          <CustomSelect v-model="form.nhom_nghe_di_lam_id" placeholder="Chọn nhóm nghề" filterable>
            <CustomOption v-for="item in nhomOptions" :key="item.id" :label="nhanNhom(item)" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Yêu cầu thêm" prop="yeu_cau_them">
          <CustomInput v-model="form.yeu_cau_them" maxlength="500" placeholder="Nhập yêu cầu thêm (nếu có)" />
        </CustomFormItem>
        <CustomFormItem label="Bằng cấp / chứng chỉ bắt buộc" prop="yeu_cau_bang_cap">
          <CustomInput
            v-model="form.yeu_cau_bang_cap"
            maxlength="255"
            placeholder="Bỏ trống nếu không yêu cầu (vd. Giấy phép lái xe hạng C)"
          />
        </CustomFormItem>
        <CustomFormItem label="Nhóm Holland" prop="nhom_holland">
          <CustomInput v-model="form.nhom_holland" maxlength="20" placeholder="Nhập mã Holland (ví dụ: RC)" />
        </CustomFormItem>
        <CustomFormItem label="Mức độ áp lực" prop="muc_do_ap_luc">
          <CustomSelect v-model="form.muc_do_ap_luc" placeholder="Chọn mức độ áp lực" clearable>
            <CustomOption v-for="item in MUC_DO_AP_LUC" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Từ khóa tìm kiếm" prop="tu_khoa_tim_kiem">
          <CustomInput v-model="form.tu_khoa_tim_kiem" maxlength="500" placeholder="Ngăn cách bằng dấu ; (vd. hàn; cơ khí)" />
        </CustomFormItem>
        <CustomFormItem label="Bắt buộc đào tạo chính quy" prop="bat_buoc_dao_tao_chinh_quy">
          <CustomSwitch v-model="form.bat_buoc_dao_tao_chinh_quy" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Hình ảnh mô tả" prop="hinh_anh_mo_ta">
          <ChonHinhAnh v-model="form.hinh_anh_mo_ta" thu-muc="nghe-cu-the-di-lam" :alt="form.ten_nghe || 'Hình ảnh nghề'" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mô tả ngắn" prop="mo_ta_ngan">
          <CustomInput
            v-model="form.mo_ta_ngan"
            type="textarea"
            :rows="4"
            maxlength="5000"
            show-word-limit
            placeholder="Nhập mô tả ngắn"
          />
        </CustomFormItem>
        <CustomFormItem
          v-for="truong in VAN_BAN_CHUNG"
          :key="truong.key"
          class="form-grid__full"
          :label="truong.label"
          :prop="truong.key"
        >
          <CustomInput
            v-model="form[truong.key]"
            type="textarea"
            :rows="4"
            :maxlength="truong.toiDa"
            :placeholder="truong.placeholder"
          />
        </CustomFormItem>

        <h3 class="form-grid__full nhom-truong">Đào tạo và kỹ năng</h3>
        <CustomFormItem label="Hình thức đào tạo" prop="hinh_thuc_dao_tao">
          <CustomInput v-model="form.hinh_thuc_dao_tao" maxlength="255" placeholder="Nhập hình thức đào tạo (vd. Đào tạo tại chỗ 1-2 tuần)" />
        </CustomFormItem>
        <CustomFormItem label="Trình độ tối thiểu" prop="trinh_do_toi_thieu">
          <CustomInput v-model="form.trinh_do_toi_thieu" maxlength="100" placeholder="Nhập trình độ tối thiểu (vd. Tốt nghiệp THCS)" />
        </CustomFormItem>
        <CustomFormItem
          v-for="truong in VAN_BAN_DAO_TAO"
          :key="truong.key"
          class="form-grid__full"
          :label="truong.label"
          :prop="truong.key"
        >
          <CustomInput
            v-model="form[truong.key]"
            type="textarea"
            :rows="4"
            :maxlength="truong.toiDa"
            :placeholder="truong.placeholder"
          />
        </CustomFormItem>

        <h3 class="form-grid__full nhom-truong">Lương tham khảo</h3>
        <CustomFormItem v-for="truong in TRUONG_LUONG" :key="truong.key" :label="truong.label" :prop="truong.key">
          <MoneyInput v-model="form[truong.key]" :placeholder="`Nhập ${truong.label.toLowerCase()}`" />
        </CustomFormItem>
        <CustomFormItem label="Đơn vị tiền tệ" prop="don_vi_tien_te">
          <CustomInput v-model="form.don_vi_tien_te" maxlength="10" placeholder="Nhập đơn vị tiền tệ (vd. VND)" />
        </CustomFormItem>
        <CustomFormItem label="Chu kỳ lương" prop="chu_ky_luong">
          <CustomSelect v-model="form.chu_ky_luong" placeholder="Chọn chu kỳ lương" :clearable="false">
            <CustomOption v-for="item in CHU_KY_LUONG" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Ghi chú lương" prop="ghi_chu_luong">
          <CustomInput v-model="form.ghi_chu_luong" maxlength="500" placeholder="Nhập ghi chú lương (vd. Lương cứng + hoa hồng)" />
        </CustomFormItem>

        <h3 class="form-grid__full nhom-truong">Môi trường và triển vọng</h3>
        <CustomFormItem label="Đặc thù thời gian" prop="dac_thu_thoi_gian">
          <CustomInput v-model="form.dac_thu_thoi_gian" maxlength="500" placeholder="Nhập đặc thù thời gian (vd. Làm ca, có ca đêm)" />
        </CustomFormItem>
        <CustomFormItem label="Yêu cầu sức khỏe" prop="yeu_cau_suc_khoe">
          <CustomInput v-model="form.yeu_cau_suc_khoe" maxlength="500" placeholder="Nhập yêu cầu sức khỏe" />
        </CustomFormItem>
        <CustomFormItem
          v-for="truong in VAN_BAN_MOI_TRUONG"
          :key="truong.key"
          class="form-grid__full"
          :label="truong.label"
          :prop="truong.key"
        >
          <CustomInput
            v-model="form[truong.key]"
            type="textarea"
            :rows="4"
            :maxlength="truong.toiDa"
            :placeholder="truong.placeholder"
          />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Lộ trình phát triển" prop="lo_trinh_phat_trien">
          <BangLoTrinhNghe v-model="form.lo_trinh_phat_trien" />
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
import { apiAssetUrl } from '@/api/apiUrl'
import {
  CHU_KY_LUONG,
  KHOANG_LUONG,
  MUC_DO_AP_LUC,
  TRUONG_LUONG,
  VAN_BAN_CHUNG,
  VAN_BAN_DAO_TAO,
  VAN_BAN_MOI_TRUONG,
  chuanHoaLoTrinh,
  dsLoTrinh,
  khoangLuong,
  loiLoTrinh,
  nhanMucDoApLuc,
  soHoacNull,
  tenLoTrinh,
} from '@/components/admin/nghe-cu-the/truongNghe'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createNgheCuTheDiLam,
  createNgheCuTheDiLamBulk,
  deleteNgheCuTheDiLam,
  deleteNgheCuTheDiLamMany,
  fetchNgheCuTheDiLam,
  fetchNhomNgheDiLam,
  updateNgheCuTheDiLam,
} from '@/api/nhomNgheDiLam'

const JSON_SAMPLE = `[
  {
    "ma_nhom": "LAM_DEP",
    "ten_nghe": "Thợ trang điểm",
    "mo_ta_ngan": "Trang điểm cô dâu, sự kiện, chụp ảnh.",
    "yeu_cau_them": "Có bộ dụng cụ cá nhân"
  },
  {
    "ma_nhom": "Y_TE_CHAM_SOC",
    "ten_nghe": "Điều dưỡng",
    "mo_ta_ngan": "Theo dõi người bệnh, tiêm truyền, thực hiện y lệnh của bác sĩ.",
    "yeu_cau_bang_cap": "Bằng cao đẳng điều dưỡng trở lên và giấy phép hành nghề",
    "bat_buoc_dao_tao_chinh_quy": 1,
    "hinh_anh_mo_ta": "https://example.com/dieu-duong.jpg"
  },
  {
    "ma_nhom": "CONG_NHAN_SAN_XUAT",
    "ten_nghe": "Thợ hàn",
    "mo_ta_cong_viec": "Hàn nối kim loại cho kết cấu thép, đường ống, sản phẩm cơ khí.",
    "hinh_thuc_dao_tao": "Sơ cấp nghề hàn 3-6 tháng",
    "trinh_do_toi_thieu": "Tốt nghiệp THCS",
    "ky_nang_chuyen_mon": "Hàn các tư thế; đọc bản vẽ kỹ thuật",
    "luong_khoi_diem_min": 8000000,
    "luong_khoi_diem_max": 10000000,
    "chu_ky_luong": "thang",
    "muc_do_ap_luc": "trung_binh",
    "nhom_holland": "R",
    "tu_khoa_tim_kiem": "hàn; thợ hàn; cơ khí",
    "lo_trinh_phat_trien": [
      {
        "giai_doan": "Thợ phụ",
        "mo_ta_cong_viec": "Chuẩn bị phôi, phụ thợ chính",
        "luong_trung_binh_min": 7000000,
        "luong_trung_binh_max": 9000000,
        "ghi_chu": "Thường 6-12 tháng"
      },
      { "giai_doan": "Thợ hàn bậc 3G", "luong_trung_binh_min": 10000000, "luong_trung_binh_max": 15000000 }
    ]
  }
]`

// Cột chữ thông tin chi tiết trên bảng (nội dung dài rút gọn một dòng, rê chuột xem đủ).
const COT_CHU_BANG = [
  { key: 'ghi_chu_luong', label: 'Ghi chú lương', rong: 220 },
  { key: 'dac_thu_thoi_gian', label: 'Đặc thù thời gian', rong: 220 },
  { key: 'yeu_cau_suc_khoe', label: 'Yêu cầu sức khỏe', rong: 220 },
  ...[...VAN_BAN_CHUNG, ...VAN_BAN_DAO_TAO, ...VAN_BAN_MOI_TRUONG].map(({ key, label }) => ({ key, label, rong: 260 })),
  // Mảng giai đoạn: hiện tên các giai đoạn nối bằng "→".
  { key: 'lo_trinh_phat_trien', label: 'Lộ trình phát triển', rong: 260, hienThi: tenLoTrinh },
  { key: 'tu_khoa_tim_kiem', label: 'Từ khóa tìm kiếm', rong: 220 },
]

// Ô chữ tùy chọn: chuỗi rỗng gửi null.
const TRUONG_CHU = [
  'mo_ta_ngan',
  'yeu_cau_them',
  'yeu_cau_bang_cap',
  'hinh_anh_mo_ta',
  'hinh_thuc_dao_tao',
  'trinh_do_toi_thieu',
  'ghi_chu_luong',
  'dac_thu_thoi_gian',
  'yeu_cau_suc_khoe',
  'nhom_holland',
  'tu_khoa_tim_kiem',
  'muc_do_ap_luc',
  ...[...VAN_BAN_CHUNG, ...VAN_BAN_DAO_TAO, ...VAN_BAN_MOI_TRUONG].map((truong) => truong.key),
]

function chuHoacNull(value) {
  if (value == null) return null
  return String(value).trim() || null
}

/** Chuẩn hóa một nghề (từ form hoặc JSON) thành payload gửi API. */
function chuanHoa(item, nhomId) {
  return {
    nhom_nghe_di_lam_id: nhomId,
    ten_nghe: String(item.ten_nghe ?? '').trim(),
    bat_buoc_dao_tao_chinh_quy: laChinhQuy(item.bat_buoc_dao_tao_chinh_quy) ? 1 : null,
    don_vi_tien_te: chuHoacNull(item.don_vi_tien_te)?.toUpperCase() || 'VND',
    chu_ky_luong: item.chu_ky_luong || 'thang',
    ...Object.fromEntries(TRUONG_CHU.map((key) => [key, chuHoacNull(item[key])])),
    ...Object.fromEntries(TRUONG_LUONG.map(({ key }) => [key, soHoacNull(item[key])])),
    lo_trinh_phat_trien: chuanHoaLoTrinh(item.lo_trinh_phat_trien),
  }
}

// bat_buoc_dao_tao_chinh_quy: API lưu 1 hoặc null (bỏ trống = không bắt buộc); form dùng công tắc true/false.
function laChinhQuy(value) {
  return value === true || Number(value) === 1
}

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
const jsonImport = useJsonBatchImport({ label: 'nghề cụ thể' })
const formRef = ref()
const nhomOptions = ref([])
const chiTietMo = ref(false)
const ngheDangXem = ref(null)

const filters = reactive({
  q: '',
  nhom_nghe_di_lam_id: '',
  // 1 / 0; '' hoặc null (bấm xóa) = không lọc.
  co_bang_cap: '',
  chinh_quy: '',
})

const form = reactive(emptyForm())

const rules = {
  nhom_nghe_di_lam_id: [{ required: true, message: 'Vui lòng chọn nhóm nghề', trigger: 'change' }],
  ten_nghe: [{ required: true, message: 'Vui lòng nhập tên nghề', trigger: 'blur' }],
  ...Object.fromEntries(
    TRUONG_LUONG.filter(({ key }) => key.endsWith('_max')).map(({ key, label }) => [
      key,
      [{ validator: kiemTraKhoangLuong(key.replace(/_max$/, '_min'), `${label} phải ≥ mức từ`), trigger: 'change' }],
    ]),
  ),
  lo_trinh_phat_trien: [
    {
      validator: (_rule, value, callback) => {
        const loi = loiLoTrinh(value)
        callback(loi ? new Error(loi) : undefined)
      },
      trigger: 'change',
    },
  ],
}

function kiemTraKhoangLuong(minKey, nhanLoi) {
  return (_rule, value, callback) => {
    const min = form[minKey]
    if (value != null && min != null && min > value) callback(new Error(nhanLoi))
    else callback()
  }
}

function emptyForm() {
  return {
    nhom_nghe_di_lam_id: null,
    ten_nghe: '',
    bat_buoc_dao_tao_chinh_quy: false,
    ...Object.fromEntries(TRUONG_CHU.map((key) => [key, ''])),
    muc_do_ap_luc: null,
    ...Object.fromEntries(TRUONG_LUONG.map(({ key }) => [key, null])),
    don_vi_tien_te: 'VND',
    chu_ky_luong: 'thang',
    lo_trinh_phat_trien: [],
  }
}

function nhanNhom(item) {
  return `${item.ten_nhom} (${item.ma_nhom})`
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
    throw new Error('JSON không hợp lệ. Hãy dán một mảng nghề cụ thể.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "ma_nhom": "...", "ten_nghe": "..." }]')
  }
  if (!data.length) {
    throw new Error('Mảng nghề cụ thể đang trống')
  }
  const theoMa = new Map(nhomOptions.value.map((item) => [item.ma_nhom, item.id]))
  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một nghề cụ thể`)
    }
    const ten = String(item.ten_nghe ?? '').trim()
    if (!ten) throw new Error(`Phần tử thứ ${line} thiếu ten_nghe`)
    let nhomId = Number(item.nhom_nghe_di_lam_id) || null
    if (!nhomId && item.ma_nhom) {
      const ma = String(item.ma_nhom).trim().toUpperCase()
      nhomId = theoMa.get(ma)
      if (!nhomId) throw new Error(`Phần tử thứ ${line}: không tìm thấy nhóm nghề có mã ${ma}`)
    }
    if (!nhomId) throw new Error(`Phần tử thứ ${line} thiếu ma_nhom hoặc nhom_nghe_di_lam_id`)
    return chuanHoa(item, nhomId)
  })
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function loadAll(fetchFn) {
  const size = 100
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchFn({ page: current, page_size: size })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  return items
}

async function loadOptions() {
  try {
    nhomOptions.value = await loadAll(fetchNhomNgheDiLam)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nhóm nghề'))
  }
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.nhom_nghe_di_lam_id) params.nhom_nghe_di_lam_id = filters.nhom_nghe_di_lam_id
    if (filters.co_bang_cap === 0 || filters.co_bang_cap === 1) params.co_bang_cap = filters.co_bang_cap
    if (filters.chinh_quy === 0 || filters.chinh_quy === 1) params.chinh_quy = filters.chinh_quy
    const data = await fetchNgheCuTheDiLam(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nghề cụ thể'))
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
  // Đang lọc theo một nhóm thì chọn sẵn nhóm đó.
  form.nhom_nghe_di_lam_id = filters.nhom_nghe_di_lam_id || null
  dialogVisible.value = true
}

function openChiTiet(row) {
  ngheDangXem.value = row
  chiTietMo.value = true
}

function suaTuChiTiet(row) {
  chiTietMo.value = false
  openEdit(row)
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    nhom_nghe_di_lam_id: row.nhom_nghe_di_lam_id,
    ten_nghe: row.ten_nghe,
    bat_buoc_dao_tao_chinh_quy: laChinhQuy(row.bat_buoc_dao_tao_chinh_quy),
    ...Object.fromEntries(TRUONG_CHU.map((key) => [key, row[key] || ''])),
    muc_do_ap_luc: row.muc_do_ap_luc || null,
    ...Object.fromEntries(TRUONG_LUONG.map(({ key }) => [key, soHoacNull(row[key])])),
    don_vi_tien_te: row.don_vi_tien_te || 'VND',
    chu_ky_luong: row.chu_ky_luong || 'thang',
    lo_trinh_phat_trien: dsLoTrinh(row.lo_trinh_phat_trien),
  })
  dialogVisible.value = true
}

function payloadFromForm() {
  return chuanHoa(form, form.nhom_nghe_di_lam_id)
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
    createBatch: createNgheCuTheDiLamBulk,
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
      await updateNgheCuTheDiLam(editingId.value, payload)
      ElMessage.success('Đã cập nhật nghề cụ thể')
    } else {
      await createNgheCuTheDiLam(payload)
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
  if (!(await xacNhanXoa(`Xóa nghề "${row.ten_nghe}"?`))) return
  try {
    await deleteNgheCuTheDiLam(row.id)
    ElMessage.success('Đã xóa nghề cụ thể')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được nghề cụ thể'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return
  if (!(await xacNhanXoa(`Xóa ${ids.length} nghề cụ thể đã chọn?`))) return

  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteNgheCuTheDiLamMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} nghề cụ thể`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các nghề cụ thể đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>

<style scoped>
.nhom-truong {
  margin: 8px 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  color: var(--el-text-color-primary);
  font-size: 15px;
  font-weight: 600;
}

.nhom-truong:first-child {
  margin-top: 0;
}

.thumb {
  width: 72px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  vertical-align: middle;
}
</style>
