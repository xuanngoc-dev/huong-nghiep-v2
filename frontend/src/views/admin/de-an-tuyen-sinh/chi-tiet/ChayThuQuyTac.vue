<template>
  <CustomDialog v-model="visible" title="Chạy thử quy tắc xét tuyển" width="90%" append-to-body>
    <p class="chay-thu__mo-ta">
      Tính một hồ sơ với quy tắc của riêng đề án này (kể cả khi đang "thử nghiệm"); không ghi gì vào CSDL. Đối chiếu
      vài phương án với đề án gốc, đúng thì tải hồ sơ và kết quả về làm bộ test hồi quy
      (<code>backend/tests/du_lieu/hoi_quy_xet_tuyen/&lt;MA_TRUONG&gt;_&lt;NAM&gt;/</code>).
    </p>

    <CustomForm class="form-grid" label-position="top" @submit.prevent>
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__full" label="Hồ sơ (JSON hồ sơ xét tuyển)">
          <CustomInput
            v-model="jsonText"
            type="textarea"
            :rows="8"
            placeholder="Dán hồ sơ dạng PUT /ho-so-xet-tuyen/cua-toi, hoặc bấm Lấy hồ sơ của tôi / Điền mẫu"
          />
        </CustomFormItem>
        <CustomFormItem label="Ngày tính">
          <CustomDatePicker v-model="homNay" type="date" value-format="YYYY-MM-DD" placeholder="Chọn ngày" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Nguồn hồ sơ">
          <div class="chay-thu__nut">
            <CustomButton :loading="dangLayHoSo" @click="layHoSoCuaToi">Lấy hồ sơ của tôi</CustomButton>
            <CustomButton text type="primary" @click="dienMau">Điền mẫu</CustomButton>
          </div>
        </CustomFormItem>
      </div>
    </CustomForm>

    <template v-if="ketQua">
      <div class="chay-thu__tom-tat">
        <span>
          <strong>{{ ketQua.ket_qua.so_phuong_an }}</strong> phương án tính được ·
          <strong>{{ soDuDieuKien }}</strong> đủ điều kiện · <strong>{{ ketQua.ket_qua.so_chuong_trinh }}</strong> chương
          trình xếp hạng
        </span>
        <div class="chay-thu__nut">
          <CustomButton size="small" @click="taiHoSo">
            <CustomIcon><Download /></CustomIcon><span>Tải hồ sơ mẫu</span>
          </CustomButton>
          <CustomButton size="small" @click="taiKetQua">
            <CustomIcon><Download /></CustomIcon><span>Tải kết quả mong đợi</span>
          </CustomButton>
        </div>
      </div>
      <ul v-if="ketQua.gia_dinh.length" class="chay-thu__gia-dinh">
        <li v-for="(g, i) in ketQua.gia_dinh" :key="i">Giả định: {{ g }}</li>
      </ul>
      <CustomSwitch v-model="chiDuDieuKien" active-text="Chỉ phương án đủ điều kiện" />
      <CustomTable :data="phuongAn" border stripe max-height="420" class="chay-thu__bang">
        <el-table-column prop="ma_xet_tuyen" label="Mã XT" width="110" />
        <el-table-column prop="ten_chuong_trinh" label="Chương trình" min-width="220" show-overflow-tooltip />
        <el-table-column prop="ma_cong_thuc" label="Công thức" min-width="150" show-overflow-tooltip />
        <el-table-column label="Tổ hợp" width="80" align="center">
          <template #default="{ row }">{{ row.ma_to_hop || '—' }}</template>
        </el-table-column>
        <el-table-column label="Điểm gốc" width="90" align="right">
          <template #default="{ row }">{{ so(row.diem_goc) }}</template>
        </el-table-column>
        <el-table-column label="Cộng / ƯT" width="100" align="right">
          <template #default="{ row }">{{ so(row.diem_cong) }} / {{ so(row.diem_uu_tien) }}</template>
        </el-table-column>
        <el-table-column label="Điểm xét" width="90" align="right">
          <template #default="{ row }">{{ so(row.diem_xet) }}</template>
        </el-table-column>
        <el-table-column label="Chênh (thang 30)" width="130" align="right">
          <template #default="{ row }">{{ so(row.chenh_lech_30) }}</template>
        </el-table-column>
        <el-table-column label="Đủ ĐK" width="80" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.du_dieu_kien ? 'success' : 'danger'" size="small">
              {{ row.du_dieu_kien ? 'Đạt' : 'Không' }}
            </CustomTag>
          </template>
        </el-table-column>
        <el-table-column prop="ly_do" label="Lý do không đạt" min-width="220" show-overflow-tooltip />
        <template #empty><CustomEmpty description="Không có phương án nào." /></template>
      </CustomTable>
    </template>

    <template #footer>
      <CustomButton @click="visible = false">Đóng</CustomButton>
      <CustomButton type="primary" :loading="dangChay" :disabled="!jsonText.trim()" @click="chay">Chạy thử</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/** Chạy thử quy tắc của một đề án (bước 5.4): đối chiếu trên dữ liệu thật trước khi chuyển sang "đang áp dụng". */
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { chayThuQuyTacXetTuyen } from '@/api/deAnTuyenSinh'
import { fetchHoSoXetTuyen } from '@/api/hoSoXetTuyen'
import { taiFileJson } from '@/utils/jsonFile'

const props = defineProps({
  deAnId: { type: Number, required: true },
})
const visible = defineModel({ type: Boolean, default: false })

// Trường chỉ có ở phản hồi GET, API chạy thử không nhận.
const CHI_DOC = ['id', 'la_ho_so_chinh', 'tu_du_lieu_cu', 'cap_nhat_luc']
const MAU = {
  nam_tot_nghiep: 2026,
  ma_khu_vuc_uu_tien: 'KV2-NT',
  ma_tinh: '01',
  ket_qua_nam_hoc: [{ lop: 12, diem_tb_chung: 8.5, hoc_luc: 4, ren_luyen: 4 }],
  diem_mon: [
    { ma_mon: 'TOAN', nguon_diem: 'THI_THPT', diem: 8.5 },
    { ma_mon: 'LY', nguon_diem: 'THI_THPT', diem: 8 },
    { ma_mon: 'HOA', nguon_diem: 'THI_THPT', diem: 7.75 },
    { ma_mon: 'ANH', nguon_diem: 'THI_THPT', diem: 8 },
    { ma_mon: 'TOAN', nguon_diem: 'HOC_BA', lop: 12, diem: 8.8 },
  ],
  chung_chi: [{ ma_chung_chi: 'IELTS', diem: 6.5, ngay_het_han: '2027-12-01' }],
}

const jsonText = ref('')
const homNay = ref(new Date().toISOString().slice(0, 10))
const dangChay = ref(false)
const dangLayHoSo = ref(false)
const ketQua = ref(null)
const chiDuDieuKien = ref(false)

const soDuDieuKien = computed(() => (ketQua.value?.ket_qua.phuong_an || []).filter((p) => p.du_dieu_kien).length)
const phuongAn = computed(() =>
  (ketQua.value?.ket_qua.phuong_an || []).filter((p) => !chiDuDieuKien.value || p.du_dieu_kien),
)

function so(value) {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 4 })
}

function thongBaoLoi(error, macDinh) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) {
    const viTri = (detail[0].loc || []).slice(1).join('.')
    return viTri ? `${viTri}: ${detail[0].msg}` : detail[0].msg
  }
  return macDinh
}

function dienMau() {
  jsonText.value = JSON.stringify(MAU, null, 2)
}

async function layHoSoCuaToi() {
  dangLayHoSo.value = true
  try {
    const hoSo = await fetchHoSoXetTuyen()
    for (const k of CHI_DOC) delete hoSo[k]
    jsonText.value = JSON.stringify(hoSo, null, 2)
  } catch (error) {
    ElMessage.error(thongBaoLoi(error, 'Không lấy được hồ sơ xét tuyển của bạn'))
  } finally {
    dangLayHoSo.value = false
  }
}

async function chay() {
  let hoSo
  try {
    hoSo = JSON.parse(jsonText.value)
  } catch {
    ElMessage.error('Hồ sơ không phải JSON hợp lệ')
    return
  }
  dangChay.value = true
  try {
    ketQua.value = await chayThuQuyTacXetTuyen(props.deAnId, { ho_so: hoSo, hom_nay: homNay.value || null })
  } catch (error) {
    ketQua.value = null
    ElMessage.error(thongBaoLoi(error, 'Không chạy thử được'))
  } finally {
    dangChay.value = false
  }
}

function taiHoSo() {
  taiFileJson(`ho_so_${ketQua.value.ma_truong}_${ketQua.value.nam_tuyen_sinh}.json`, ketQua.value.ho_so_bo_tinh)
}

function taiKetQua() {
  taiFileJson(`ket_qua_${ketQua.value.ma_truong}_${ketQua.value.nam_tuyen_sinh}.json`, ketQua.value.ket_qua)
}
</script>

<style scoped>
.chay-thu__mo-ta {
  margin: 0 0 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.chay-thu__nut {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chay-thu__tom-tat {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin: 8px 0;
}

.chay-thu__gia-dinh {
  margin: 0 0 8px;
  padding-left: 18px;
  color: var(--el-color-warning-dark-2);
  font-size: 13px;
}

.chay-thu__bang {
  margin-top: 8px;
}
</style>
