<template>
  <div v-loading="loading" class="quy-tac">
    <div class="quy-tac__dau">
      <div class="quy-tac__tom-tat">
        <CustomSelect
          :model-value="data?.trang_thai_xet_tuyen ?? 0"
          class="quy-tac__trang-thai"
          placeholder="Chọn trạng thái"
          :clearable="false"
          :disabled="!data || dangDoiTrangThai"
          @change="onDoiTrangThai"
        >
          <CustomOption v-for="(tt, ma) in TRANG_THAI" :key="ma" :label="tt.label" :value="Number(ma)" />
        </CustomSelect>
        <CustomTag :type="trangThai.tag" size="small">{{ trangThai.mo_ta }}</CustomTag>
        <span v-if="coQuyTac">
          {{ data.cong_thuc.length }} công thức · {{ soPhuongAn }} phương án · {{ data.nhom_dieu_kien.length }} nhóm
          điều kiện · {{ data.diem_cong.length }} điểm cộng
        </span>
        <span v-else-if="data">Chưa có quy tắc xét tuyển.</span>
      </div>
      <div class="quy-tac__nut">
        <CustomButton v-if="coQuyTac" @click="chayThuVisible = true">
          <CustomIcon><VideoPlay /></CustomIcon>
          <span>Chạy thử</span>
        </CustomButton>
        <CustomButton type="primary" @click="moImport">
          <CustomIcon><Upload /></CustomIcon>
          <span>Import quy tắc (JSON)</span>
        </CustomButton>
      </div>
    </div>

    <CustomEmpty
      v-if="data && !coQuyTac"
      description="Đề án chưa có quy tắc xét tuyển. Import file JSON chuẩn (docs/de-an-tuyen-sinh/chuan_du_lieu) để hệ thống tính được điểm xét."
    />

    <el-tabs v-else-if="coQuyTac" v-model="tab" class="quy-tac__tabs">
      <el-tab-pane :label="`Công thức (${data.cong_thuc.length})`" name="cong_thuc">
        <CustomTable :data="data.cong_thuc" row-key="id" border stripe max-height="460">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="chi-tiet-dong">
                <p v-if="row.mo_ta_cong_thuc"><strong>Công thức:</strong> {{ row.mo_ta_cong_thuc }}</p>
                <p v-if="row.he_so_mon.length">
                  <strong>Hệ số môn:</strong>
                  {{ row.he_so_mon.map((h) => `${h.ma_mon || h.nhom_mon} × ${soGon(h.he_so)}`).join(', ') }}
                </p>
                <p v-if="row.thanh_phan.length">
                  <strong>Thành phần:</strong>
                  {{ row.thanh_phan.map(moTaThanhPhan).join('; ') }}
                </p>
                <p v-if="!row.mo_ta_cong_thuc && !row.he_so_mon.length && !row.thanh_phan.length">Không có chi tiết.</p>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="ma_cong_thuc" label="Mã" min-width="150" />
          <el-table-column prop="ten_cong_thuc" label="Tên công thức" min-width="240" show-overflow-tooltip />
          <el-table-column prop="ma_phuong_thuc_cua_bo" label="Phương thức" width="110" align="center" />
          <el-table-column label="Kiểu tính" width="150">
            <template #default="{ row }">
              <CustomTag :type="KIEU_TINH[row.kieu_tinh]?.tag" size="small">
                {{ KIEU_TINH[row.kieu_tinh]?.label || row.kieu_tinh }}
              </CustomTag>
            </template>
          </el-table-column>
          <el-table-column label="Nguồn điểm" width="110">
            <template #default="{ row }">{{ NGUON_DIEM[row.nguon_diem_mon] || '—' }}</template>
          </el-table-column>
          <el-table-column label="Thang" width="80" align="center">
            <template #default="{ row }">{{ soGon(row.thang_diem) }}</template>
          </el-table-column>
          <el-table-column prop="so_phuong_an" label="Phương án" width="100" align="center" />
          <el-table-column label="Trạng thái" width="110" align="center">
            <template #default="{ row }">
              <CustomTag :type="row.trang_thai ? 'success' : 'info'" size="small">
                {{ row.trang_thai ? 'Đang dùng' : 'Chưa dùng' }}
              </CustomTag>
            </template>
          </el-table-column>
        </CustomTable>
      </el-tab-pane>

      <el-tab-pane :label="`Phương án theo chương trình (${data.chuong_trinh.length})`" name="phuong_an">
        <CustomTable :data="data.chuong_trinh" row-key="id" border stripe max-height="460">
          <el-table-column prop="ma_xet_tuyen" label="Mã xét tuyển" width="130" />
          <el-table-column prop="ten_chuong_trinh" label="Chương trình" min-width="240" show-overflow-tooltip />
          <el-table-column label="Phương án (công thức: tổ hợp)" min-width="420">
            <template #default="{ row }">
              <div v-if="row.phuong_an.length" class="phuong-an">
                <span v-for="pa in row.phuong_an" :key="pa.ma_cong_thuc" class="phuong-an__muc">
                  <strong>{{ pa.ma_cong_thuc }}</strong>
                  <template v-if="pa.to_hop.length">: {{ pa.to_hop.join(', ') }}</template>
                </span>
              </div>
              <CustomTag v-else type="warning" size="small">Chưa có phương án</CustomTag>
            </template>
          </el-table-column>
        </CustomTable>
      </el-tab-pane>

      <el-tab-pane :label="`Điều kiện (${data.nhom_dieu_kien.length})`" name="dieu_kien">
        <CustomTable :data="data.nhom_dieu_kien" row-key="id" border stripe max-height="460">
          <el-table-column prop="ma_nhom" label="Mã nhóm" min-width="150" />
          <el-table-column prop="ten_nhom" label="Lý do khi không đạt" min-width="240" show-overflow-tooltip />
          <el-table-column label="Áp dụng cho" min-width="170">
            <template #default="{ row }">{{ phamVi(row) }}</template>
          </el-table-column>
          <el-table-column label="Một trong các điều kiện" min-width="300">
            <template #default="{ row }">
              <div v-for="(dk, i) in row.dieu_kien" :key="i" class="dieu-kien">{{ moTaDieuKien(dk) }}</div>
            </template>
          </el-table-column>
          <el-table-column label="Bắt buộc" width="90" align="center">
            <template #default="{ row }">{{ row.bat_buoc ? 'Có' : 'Cảnh báo' }}</template>
          </el-table-column>
        </CustomTable>
      </el-tab-pane>

      <el-tab-pane :label="`Điểm cộng (${data.diem_cong.length})`" name="diem_cong">
        <CustomTable :data="data.diem_cong" row-key="id" border stripe max-height="460">
          <template #empty><CustomEmpty description="Đề án không có quy tắc điểm cộng." /></template>
          <el-table-column label="Loại" width="150">
            <template #default="{ row }">{{ LOAI_DIEM_CONG[row.loai_diem_cong] || row.loai_diem_cong }}</template>
          </el-table-column>
          <el-table-column prop="nhom_cong" label="Nhóm" width="140" />
          <el-table-column label="Điều kiện" min-width="240">
            <template #default="{ row }">{{ moTaDieuKien(row) }}</template>
          </el-table-column>
          <el-table-column label="Cộng (thang 30)" width="130" align="center">
            <template #default="{ row }">{{ soGon(row.diem_cong) }}</template>
          </el-table-column>
          <el-table-column label="Công thức" width="150">
            <template #default="{ row }">{{ row.ma_cong_thuc || 'Mọi công thức' }}</template>
          </el-table-column>
          <el-table-column prop="mo_ta" label="Mô tả" min-width="200" show-overflow-tooltip />
        </CustomTable>
      </el-tab-pane>

      <el-tab-pane :label="`Bảng quy đổi (${data.bang_quy_doi.length})`" name="bang_quy_doi">
        <CustomTable :data="data.bang_quy_doi" row-key="id" border stripe max-height="460">
          <template #empty><CustomEmpty description="Đề án không có bảng quy đổi." /></template>
          <el-table-column prop="ma_bang" label="Mã bảng" min-width="150" />
          <el-table-column prop="ten_bang" label="Tên bảng" min-width="260" show-overflow-tooltip />
          <el-table-column label="Thang đích" width="110" align="center">
            <template #default="{ row }">{{ soGon(row.thang_diem_dich) }}</template>
          </el-table-column>
          <el-table-column prop="so_muc" label="Số mức" width="90" align="center" />
        </CustomTable>
      </el-tab-pane>

      <el-tab-pane :label="`Lịch sử import (${data.lich_su.length})`" name="lich_su">
        <CustomTable :data="data.lich_su" row-key="id" border stripe max-height="460">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="chi-tiet-dong">
                <p><strong>Số dòng:</strong> {{ moTaSoDong(row.so_dong) }}</p>
                <template v-if="row.quy_dinh_chua_mo_hinh_hoa?.length">
                  <p><strong>Chưa tính được:</strong></p>
                  <ul>
                    <li v-for="(qd, i) in row.quy_dinh_chua_mo_hinh_hoa" :key="i">
                      <template v-if="qd.ma">{{ qd.ma }}: </template>{{ qd.mo_ta }}
                    </li>
                  </ul>
                </template>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Thời điểm" width="170">
            <template #default="{ row }">{{ hienThoiGian(row.tao_luc) }}</template>
          </el-table-column>
          <el-table-column label="File" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">{{ row.ten_file || '—' }}</template>
          </el-table-column>
          <el-table-column label="Người import" min-width="160">
            <template #default="{ row }">{{ row.nguoi_import || '—' }}</template>
          </el-table-column>
          <el-table-column label="Công thức / phương án" width="170" align="center">
            <template #default="{ row }">
              {{ row.so_dong?.xt_cong_thuc || 0 }} / {{ row.so_dong?.xt_phuong_an || 0 }}
            </template>
          </el-table-column>
        </CustomTable>
      </el-tab-pane>
    </el-tabs>

    <ChayThuQuyTac v-model="chayThuVisible" :de-an-id="props.deAnId" />

    <CustomDialog v-model="importVisible" title="Import quy tắc xét tuyển" width="800px" append-to-body>
      <p class="import__mo-ta">
        Chọn hoặc dán file JSON theo cấu trúc chuẩn (một trường, một năm). File phải đúng trường và năm của đề án này.
        Quy tắc cũ của đề án sẽ bị thay toàn bộ; file có lỗi thì không ghi gì.
      </p>
      <div class="import__chon">
        <CustomButton type="primary" plain :disabled="dangImport" @click="fileRef?.click()">
          <CustomIcon><Upload /></CustomIcon>
          <span>Chọn file</span>
        </CustomButton>
        <span class="import__ten-file">{{ tenFile || 'Chưa chọn file' }}</span>
        <input ref="fileRef" type="file" accept=".json,application/json" hidden @change="onChonFile" />
      </div>
      <CustomInput
        v-model="jsonText"
        type="textarea"
        :rows="8"
        placeholder="Hoặc dán nội dung JSON quy tắc xét tuyển vào đây"
        class="import__json"
        @input="ketQua = null"
      />

      <div v-if="loiImport.length" class="ket-qua ket-qua--loi">
        <p><strong>File có {{ loiImport.length }} lỗi, chưa ghi gì:</strong></p>
        <ul>
          <li v-for="(x, i) in loiImport.slice(0, 50)" :key="i">{{ x }}</li>
        </ul>
        <p v-if="loiImport.length > 50">… và {{ loiImport.length - 50 }} lỗi khác.</p>
      </div>
      <div v-if="ketQua" class="ket-qua">
        <p><strong>Đã import:</strong> {{ moTaSoDong(ketQua.so_dong) }}</p>
        <template v-if="ketQua.quy_dinh_chua_mo_hinh_hoa.length">
          <p><strong>Chưa tính được ({{ ketQua.quy_dinh_chua_mo_hinh_hoa.length }}):</strong></p>
          <ul>
            <li v-for="(qd, i) in ketQua.quy_dinh_chua_mo_hinh_hoa" :key="i">
              <template v-if="qd.ma">{{ qd.ma }}: </template>{{ qd.mo_ta }}
            </li>
          </ul>
        </template>
        <template v-if="ketQua.canh_bao.length">
          <p><strong>Cảnh báo ({{ ketQua.canh_bao.length }}):</strong></p>
          <ul class="ket-qua__canh-bao">
            <li v-for="(x, i) in ketQua.canh_bao" :key="i">{{ x }}</li>
          </ul>
        </template>
      </div>

      <template #footer>
        <CustomButton @click="importVisible = false">Đóng</CustomButton>
        <CustomButton type="primary" :loading="dangImport" :disabled="!jsonText.trim()" @click="onImport">
          Import
        </CustomButton>
      </template>
    </CustomDialog>
  </div>
</template>

<script setup>
/**
 * Tab "Quy tắc xét tuyển" của chi tiết đề án (bước 2.5): xem quy tắc đã chuẩn hóa (chỉ đọc) và import file
 * JSON chuẩn. Import thay toàn bộ quy tắc cũ; file lỗi thì hiện danh sách lỗi và không ghi gì.
 */
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { doiTrangThaiQuyTacXetTuyen, fetchQuyTacXetTuyen, importQuyTacXetTuyen } from '@/api/deAnTuyenSinh'
import { hienThoiGian } from '@/data/napTien'
import { docFileJson } from '@/utils/jsonFile'
import ChayThuQuyTac from './ChayThuQuyTac.vue'

const props = defineProps({
  deAnId: { type: Number, required: true },
})

const TRANG_THAI = {
  0: { label: 'Chưa chuẩn hóa', tag: 'info', mo_ta: 'Tìm trường dùng thuật toán cũ' },
  1: { label: 'Thử nghiệm', tag: 'warning', mo_ta: 'Tìm trường dùng thuật toán cũ' },
  2: { label: 'Đang áp dụng', tag: 'success', mo_ta: 'Tìm trường dùng bộ tính xét tuyển' },
}
const KIEU_TINH = {
  TO_HOP_MON: { label: 'Theo tổ hợp môn', tag: 'primary' },
  THANH_PHAN: { label: 'Bài thi / chứng chỉ', tag: 'success' },
  CHI_DIEU_KIEN: { label: 'Chỉ xét điều kiện', tag: 'info' },
  THU_CONG: { label: 'Chưa tự tính', tag: 'warning' },
}
const NGUON_DIEM = { THI_THPT: 'Thi THPT', HOC_BA: 'Học bạ' }
const LOAI_DIEM_CONG = {
  DIEM_THUONG: 'Điểm thưởng',
  DIEM_XET_THUONG: 'Điểm xét thưởng',
  DIEM_KHUYEN_KHICH: 'Điểm khuyến khích',
}
const TEN_BANG = {
  xt_cong_thuc: 'công thức',
  xt_phuong_an: 'phương án',
  xt_nhom_dieu_kien: 'nhóm điều kiện',
  xt_dieu_kien: 'điều kiện',
  xt_diem_cong: 'điểm cộng',
  xt_bang_quy_doi: 'bảng quy đổi',
  dats_chuong_trinh_dao_tao: 'chương trình mới',
  dats_tru_so: 'cơ sở mới',
  dats_hoc_phi: 'học phí',
  xt_diem_chuan: 'điểm chuẩn',
}

const loading = ref(false)
const data = ref(null)
const tab = ref('cong_thuc')
const importVisible = ref(false)
const dangImport = ref(false)
const jsonText = ref('')
const tenFile = ref('')
const fileRef = ref()
const ketQua = ref(null)
const loiImport = ref([])
const dangDoiTrangThai = ref(false)
const chayThuVisible = ref(false)

const coQuyTac = computed(() => Boolean(data.value?.cong_thuc.length))
const trangThai = computed(() => TRANG_THAI[data.value?.trang_thai_xet_tuyen ?? 0] || TRANG_THAI[0])
const soPhuongAn = computed(() => (data.value?.cong_thuc || []).reduce((tong, ct) => tong + ct.so_phuong_an, 0))

function soGon(value) {
  return value == null ? '—' : Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 8 })
}

function moTaThanhPhan(tp) {
  const nguon = tp.loai_nguon === 'BAI_THI' ? tp.ma_bai_thi : `chứng chỉ${tp.ma_mon ? ` ${tp.ma_mon}` : ''}`
  const bang = tp.ma_bang ? ` (bảng ${tp.ma_bang})` : ''
  return `M${tp.vi_tri}: ${tp.ten_thanh_phan || nguon}${bang} × ${soGon(tp.he_so)}`
}

function moTaDieuKien(dk) {
  const khoa = dk.khoa ? `[${dk.khoa}]` : ''
  const chuoi = `${dk.ma_chi_so}${khoa} ${dk.toan_tu} ${soGon(dk.gia_tri_so)}`
  return dk.mo_ta ? `${chuoi} — ${dk.mo_ta}` : chuoi
}

function phamVi(nhom) {
  const phan = []
  if (nhom.ma_cong_thuc) phan.push(`công thức ${nhom.ma_cong_thuc}`)
  if (nhom.ma_xet_tuyen) phan.push(`chương trình ${nhom.ma_xet_tuyen}`)
  return phan.length ? phan.join(', ') : 'Toàn đề án'
}

function moTaSoDong(soDong) {
  const phan = Object.entries(TEN_BANG)
    .filter(([bang]) => soDong?.[bang])
    .map(([bang, ten]) => `${soDong[bang]} ${ten}`)
  return phan.length ? phan.join(', ') : 'không có dòng nào'
}

async function load() {
  loading.value = true
  try {
    data.value = await fetchQuyTacXetTuyen(props.deAnId, { skipLoading: true })
  } catch (error) {
    data.value = null
    const detail = error?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Không tải được quy tắc xét tuyển')
  } finally {
    loading.value = false
  }
}

function moImport() {
  jsonText.value = ''
  tenFile.value = ''
  ketQua.value = null
  loiImport.value = []
  importVisible.value = true
}

async function onChonFile(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  const text = await docFileJson(file)
  if (text === null) return
  jsonText.value = text
  tenFile.value = file.name
  ketQua.value = null
  loiImport.value = []
}

async function onImport() {
  let duLieu
  try {
    duLieu = JSON.parse(jsonText.value)
  } catch {
    ElMessage.error('JSON không hợp lệ')
    return
  }
  dangImport.value = true
  ketQua.value = null
  loiImport.value = []
  try {
    ketQua.value = await importQuyTacXetTuyen(
      props.deAnId,
      { du_lieu: duLieu, ten_file: tenFile.value || null },
      { timeout: 300000 },
    )
    ElMessage.success('Đã import quy tắc xét tuyển')
    await load()
  } catch (error) {
    const detail = error?.response?.data?.detail
    if (detail && Array.isArray(detail.loi)) {
      loiImport.value = detail.loi
    } else if (typeof detail === 'string') {
      loiImport.value = [detail]
    } else if (Array.isArray(detail) && detail[0]?.msg) {
      loiImport.value = detail.map((x) => x.msg)
    } else {
      loiImport.value = ['Không import được quy tắc xét tuyển']
    }
  } finally {
    dangImport.value = false
  }
}

async function onDoiTrangThai(moi) {
  if (moi === 2) {
    try {
      await ElMessageBox.confirm(
        'Từ giờ lượt tìm trường của người dùng trong năm của đề án này sẽ tính điểm xét tuyển theo quy tắc đã import. Tiếp tục?',
        'Chuyển sang đang áp dụng',
        { type: 'warning', confirmButtonText: 'Áp dụng', cancelButtonText: 'Hủy' },
      )
    } catch {
      return
    }
  }
  dangDoiTrangThai.value = true
  try {
    const kq = await doiTrangThaiQuyTacXetTuyen(props.deAnId, moi)
    data.value.trang_thai_xet_tuyen = kq.trang_thai_xet_tuyen
    ElMessage.success(`Đã chuyển sang ${TRANG_THAI[kq.trang_thai_xet_tuyen].label.toLowerCase()}`)
  } catch (error) {
    const detail = error?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Không đổi được trạng thái')
  } finally {
    dangDoiTrangThai.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.quy-tac {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}

.quy-tac__dau {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.quy-tac__nut {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quy-tac__trang-thai {
  width: 170px;
}

.quy-tac__tom-tat {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-regular);
}

.chi-tiet-dong {
  padding: 4px 16px;
  line-height: 1.6;
}

.chi-tiet-dong p {
  margin: 0 0 4px;
}

.chi-tiet-dong ul,
.ket-qua ul {
  margin: 0 0 8px;
  padding-left: 20px;
}

.phuong-an {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dieu-kien + .dieu-kien {
  margin-top: 2px;
  padding-top: 2px;
  border-top: 1px dashed var(--el-border-color-lighter);
}

.import__mo-ta {
  margin: 0 0 12px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.import__chon {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.import__ten-file {
  color: var(--el-text-color-secondary);
  word-break: break-all;
}

.import__json :deep(textarea) {
  font-family: var(--el-font-family-mono, monospace);
  font-size: 13px;
}

.ket-qua {
  margin-top: 12px;
  padding: 12px;
  border-radius: 6px;
  background: var(--el-color-success-light-9);
  max-height: 320px;
  overflow: auto;
  line-height: 1.6;
}

.ket-qua p {
  margin: 0 0 4px;
}

.ket-qua--loi {
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}

.ket-qua__canh-bao {
  color: var(--el-color-warning-dark-2);
}
</style>
