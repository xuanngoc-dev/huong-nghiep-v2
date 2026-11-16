<template>
  <div v-loading="dangTai" class="hs-xt">
    <header class="hs-xt__dau">
      <div>
        <h1 class="hs-xt__tieu-de">Hồ sơ xét tuyển</h1>
        <p class="hs-xt__phu">
          Điểm, bài thi, chứng chỉ và nguyện vọng dùng để tính khả năng trúng tuyển khi tìm trường phù hợp. Lưu ở đây
          thì Hồ sơ năng lực cũng được cập nhật theo.
        </p>
      </div>
      <CustomButton type="primary" :loading="dangLuu" @click="luu">
        <CustomIcon><Check /></CustomIcon>
        <span>Lưu hồ sơ</span>
      </CustomButton>
    </header>

    <div v-if="tuDuLieuCu" class="hs-xt__bao">
      <CustomIcon><InfoFilled /></CustomIcon>
      <span>
        Dữ liệu dưới đây lấy từ Hồ sơ năng lực (học lực suy ra từ điểm trung bình). Kiểm tra, bổ sung rồi bấm
        <strong>Lưu hồ sơ</strong> để tạo hồ sơ xét tuyển.
      </span>
    </div>

    <CustomCard shadow="never">
      <template #header>Thông tin chung</template>
      <CustomForm class="form-grid" label-position="top" @submit.prevent>
        <div class="form-grid__body">
          <CustomFormItem label="Năm tốt nghiệp THPT">
            <CustomInputNumber v-model="f.nam_tot_nghiep" :min="2000" :max="2100" :controls="false" placeholder="Nhập năm tốt nghiệp" />
          </CustomFormItem>
          <CustomFormItem label="Đã tốt nghiệp THPT">
            <CustomSwitch v-model="f.da_tot_nghiep" active-text="Đã / sẽ tốt nghiệp" inactive-text="Chưa" />
          </CustomFormItem>
          <CustomFormItem label="Chương trình THPT">
            <CustomSelect v-model="f.chuong_trinh_thpt" :clearable="false" placeholder="Chọn chương trình THPT">
              <CustomOption v-for="x in CHUONG_TRINH" :key="x.value" :label="x.label" :value="x.value" />
            </CustomSelect>
          </CustomFormItem>
          <CustomFormItem label="Hệ chuyên">
            <CustomSwitch v-model="f.he_chuyen" active-text="Học hệ chuyên" inactive-text="Không" />
          </CustomFormItem>
          <CustomFormItem label="Môn chuyên">
            <CustomSelect v-model="f.ma_mon_chuyen" filterable :disabled="!f.he_chuyen" placeholder="Chọn môn chuyên">
              <CustomOption v-for="m in mon" :key="m.ma_mon_hoc" :label="m.ten_mon_hoc" :value="m.ma_mon_hoc" />
            </CustomSelect>
          </CustomFormItem>
          <CustomFormItem class="form-grid__span-2" label="Trường THPT">
            <CustomInput v-model="f.ten_truong_thpt" maxlength="255" placeholder="Nhập trường THPT" />
          </CustomFormItem>
          <CustomFormItem label="Tỉnh/thành học THPT">
            <CustomSelect v-model="f.ma_tinh" filterable placeholder="Chọn tỉnh/thành">
              <CustomOption v-for="t in tinh" :key="t.ma_tinh" :label="t.ten_tinh" :value="t.ma_tinh" />
            </CustomSelect>
          </CustomFormItem>
          <CustomFormItem label="Khu vực ưu tiên">
            <CustomSelect v-model="f.ma_khu_vuc_uu_tien" placeholder="Chọn khu vực ưu tiên">
              <CustomOption v-for="k in khuVuc" :key="k.ma_khu_vuc" :label="k.ten_khu_vuc" :value="k.ma_khu_vuc" />
            </CustomSelect>
          </CustomFormItem>
          <CustomFormItem label="Đối tượng ưu tiên">
            <CustomSelect v-model="f.ma_doi_tuong_uu_tien" placeholder="Chọn đối tượng ưu tiên">
              <CustomOption v-for="d in doiTuong" :key="d.ma_doi_tuong" :label="d.ten_doi_tuong" :value="d.ma_doi_tuong" />
            </CustomSelect>
          </CustomFormItem>
          <CustomFormItem class="form-grid__span-2" label="Học phí tối đa mỗi năm (VNĐ)">
            <CustomInputNumber
              v-model="f.ngan_sach_hoc_phi_nam"
              :min="0"
              :step="1000000"
              :controls="false"
              placeholder="Nhập học phí tối đa gia đình chi trả được"
            />
          </CustomFormItem>
        </div>
      </CustomForm>
    </CustomCard>

    <CustomCard shadow="never">
      <template #header>Kết quả học tập từng năm</template>
      <CustomTable :data="f.ket_qua_nam_hoc" row-key="lop" border>
        <el-table-column label="Lớp" width="80" align="center" prop="lop" />
        <el-table-column label="Điểm TB cả năm" min-width="150">
          <template #default="{ row }">
            <CustomInputNumber v-model="row.diem_tb_chung" :min="0" :max="10" :step="0.1" :precision="2" :controls="false" placeholder="Nhập điểm TB" />
          </template>
        </el-table-column>
        <el-table-column label="Học lực" min-width="150">
          <template #default="{ row }">
            <CustomSelect v-model="row.hoc_luc" placeholder="Chọn học lực">
              <CustomOption v-for="m in MUC" :key="m.value" :label="m.label" :value="m.value" />
            </CustomSelect>
          </template>
        </el-table-column>
        <el-table-column label="Rèn luyện / hạnh kiểm" min-width="150">
          <template #default="{ row }">
            <CustomSelect v-model="row.ren_luyen" placeholder="Chọn rèn luyện">
              <CustomOption v-for="m in MUC" :key="m.value" :label="m.label" :value="m.value" />
            </CustomSelect>
          </template>
        </el-table-column>
      </CustomTable>
    </CustomCard>

    <CustomCard shadow="never">
      <template #header>
        <div class="hs-xt__khoi-dau">
          <span>Điểm thi tốt nghiệp THPT</span>
          <CustomButton size="small" @click="f.thpt.push({ ma_mon: '', diem: null, la_du_kien: true })">
            <CustomIcon><Plus /></CustomIcon><span>Thêm môn</span>
          </CustomButton>
        </div>
      </template>
      <CustomTable :data="f.thpt" border>
        <el-table-column label="Môn" min-width="180">
          <template #default="{ row }">
            <CustomSelect v-model="row.ma_mon" filterable placeholder="Chọn môn">
              <CustomOption v-for="m in mon" :key="m.ma_mon_hoc" :label="m.ten_mon_hoc" :value="m.ma_mon_hoc" />
            </CustomSelect>
          </template>
        </el-table-column>
        <el-table-column label="Điểm" width="140">
          <template #default="{ row }">
            <CustomInputNumber v-model="row.diem" :min="0" :max="10" :step="0.25" :precision="2" :controls="false" placeholder="Nhập điểm" />
          </template>
        </el-table-column>
        <el-table-column label="Điểm dự kiến / thi thử" width="170" align="center">
          <template #default="{ row }"><el-checkbox v-model="row.la_du_kien" /></template>
        </el-table-column>
        <el-table-column label="Thao tác" width="80" align="center">
          <template #default="{ $index }">
            <NutXoa @click="f.thpt.splice($index, 1)" />
          </template>
        </el-table-column>
        <template #empty><CustomEmpty description="Chưa có điểm thi THPT." /></template>
      </CustomTable>
    </CustomCard>

    <CustomCard shadow="never">
      <template #header>
        <div class="hs-xt__khoi-dau">
          <span>Điểm học bạ (trung bình cả năm)</span>
          <CustomButton size="small" @click="f.hocBa.push({ ma_mon: '', 10: null, 11: null, 12: null })">
            <CustomIcon><Plus /></CustomIcon><span>Thêm môn</span>
          </CustomButton>
        </div>
      </template>
      <CustomTable :data="f.hocBa" border>
        <el-table-column label="Môn" min-width="180">
          <template #default="{ row }">
            <CustomSelect v-model="row.ma_mon" filterable placeholder="Chọn môn">
              <CustomOption v-for="m in mon" :key="m.ma_mon_hoc" :label="m.ten_mon_hoc" :value="m.ma_mon_hoc" />
            </CustomSelect>
          </template>
        </el-table-column>
        <el-table-column v-for="lop in LOP" :key="lop" :label="`Lớp ${lop}`" width="130">
          <template #default="{ row }">
            <CustomInputNumber v-model="row[lop]" :min="0" :max="10" :step="0.1" :precision="2" :controls="false" placeholder="Nhập điểm" />
          </template>
        </el-table-column>
        <el-table-column label="Thao tác" width="80" align="center">
          <template #default="{ $index }">
            <NutXoa @click="f.hocBa.splice($index, 1)" />
          </template>
        </el-table-column>
        <template #empty><CustomEmpty description="Chưa có điểm học bạ." /></template>
      </CustomTable>
    </CustomCard>

    <CustomCard shadow="never">
      <template #header>
        <div class="hs-xt__khoi-dau">
          <span>Bài thi đánh giá năng lực / tư duy, SAT, ACT</span>
          <CustomButton size="small" @click="f.diem_bai_thi.push({ ma_bai_thi: '', nam_thi: namHienTai, diem: null, phan_tu_chon: '', ngay_thi: null })">
            <CustomIcon><Plus /></CustomIcon><span>Thêm bài thi</span>
          </CustomButton>
        </div>
      </template>
      <CustomTable :data="f.diem_bai_thi" border>
        <el-table-column label="Bài thi" min-width="200">
          <template #default="{ row }">
            <CustomSelect v-model="row.ma_bai_thi" filterable placeholder="Chọn bài thi">
              <CustomOption v-for="b in baiThi" :key="b.ma_bai_thi" :label="b.ten_bai_thi" :value="b.ma_bai_thi" />
            </CustomSelect>
          </template>
        </el-table-column>
        <el-table-column label="Năm thi" width="120">
          <template #default="{ row }">
            <CustomInputNumber v-model="row.nam_thi" :min="2000" :max="2100" :controls="false" placeholder="Nhập năm" />
          </template>
        </el-table-column>
        <el-table-column label="Điểm" width="130">
          <template #default="{ row }">
            <CustomInputNumber v-model="row.diem" :min="0" :precision="2" :controls="false" placeholder="Nhập điểm" />
          </template>
        </el-table-column>
        <el-table-column label="Phần tự chọn" min-width="150">
          <template #default="{ row }">
            <CustomInput v-model="row.phan_tu_chon" maxlength="50" placeholder="Ví dụ KHOA_HOC" />
          </template>
        </el-table-column>
        <el-table-column label="Thao tác" width="80" align="center">
          <template #default="{ $index }">
            <NutXoa @click="f.diem_bai_thi.splice($index, 1)" />
          </template>
        </el-table-column>
        <template #empty><CustomEmpty description="Chưa có bài thi." /></template>
      </CustomTable>
    </CustomCard>

    <CustomCard shadow="never">
      <template #header>
        <div class="hs-xt__khoi-dau">
          <span>Chứng chỉ ngoại ngữ / quốc tế</span>
          <CustomButton size="small" @click="f.chung_chi.push({ ma_chung_chi: '', diem: null, cap_do: '', ngay_cap: null, ngay_het_han: null })">
            <CustomIcon><Plus /></CustomIcon><span>Thêm chứng chỉ</span>
          </CustomButton>
        </div>
      </template>
      <CustomTable :data="f.chung_chi" border>
        <el-table-column label="Chứng chỉ" min-width="200">
          <template #default="{ row }">
            <CustomSelect v-model="row.ma_chung_chi" filterable placeholder="Chọn chứng chỉ">
              <CustomOption v-for="c in chungChi" :key="c.ma_chung_chi" :label="c.ten_chung_chi" :value="c.ma_chung_chi" />
            </CustomSelect>
          </template>
        </el-table-column>
        <el-table-column label="Điểm" width="120">
          <template #default="{ row }">
            <CustomInputNumber v-model="row.diem" :min="0" :precision="2" :controls="false" placeholder="Nhập điểm" />
          </template>
        </el-table-column>
        <el-table-column label="Cấp độ" width="120">
          <template #default="{ row }">
            <CustomInput v-model="row.cap_do" maxlength="30" placeholder="N3, B2..." />
          </template>
        </el-table-column>
        <el-table-column label="Ngày cấp" width="160">
          <template #default="{ row }">
            <CustomDatePicker v-model="row.ngay_cap" type="date" value-format="YYYY-MM-DD" placeholder="Chọn ngày" />
          </template>
        </el-table-column>
        <el-table-column label="Hết hạn" width="160">
          <template #default="{ row }">
            <CustomDatePicker v-model="row.ngay_het_han" type="date" value-format="YYYY-MM-DD" placeholder="Chọn ngày" />
          </template>
        </el-table-column>
        <el-table-column label="Thao tác" width="80" align="center">
          <template #default="{ $index }">
            <NutXoa @click="f.chung_chi.splice($index, 1)" />
          </template>
        </el-table-column>
        <template #empty><CustomEmpty description="Chưa có chứng chỉ." /></template>
      </CustomTable>
    </CustomCard>

    <CustomCard shadow="never">
      <template #header>
        <div class="hs-xt__khoi-dau">
          <span>Thành tích, giải thưởng</span>
          <CustomButton size="small" @click="f.thanh_tich.push({ ma_thanh_tich: '', ma_mon: '', muc_giai: null, nam_dat_giai: null, lop: null })">
            <CustomIcon><Plus /></CustomIcon><span>Thêm thành tích</span>
          </CustomButton>
        </div>
      </template>
      <CustomTable :data="f.thanh_tich" border>
        <el-table-column label="Thành tích" min-width="200">
          <template #default="{ row }">
            <CustomSelect v-model="row.ma_thanh_tich" filterable placeholder="Chọn thành tích">
              <CustomOption v-for="t in thanhTich" :key="t.ma_thanh_tich" :label="t.ten_thanh_tich" :value="t.ma_thanh_tich" />
            </CustomSelect>
          </template>
        </el-table-column>
        <el-table-column label="Môn" min-width="150">
          <template #default="{ row }">
            <CustomSelect v-model="row.ma_mon" filterable placeholder="Chọn môn">
              <CustomOption v-for="m in mon" :key="m.ma_mon_hoc" :label="m.ten_mon_hoc" :value="m.ma_mon_hoc" />
            </CustomSelect>
          </template>
        </el-table-column>
        <el-table-column label="Mức giải" width="160">
          <template #default="{ row }">
            <CustomSelect v-model="row.muc_giai" placeholder="Chọn mức giải">
              <CustomOption v-for="g in GIAI" :key="g.value" :label="g.label" :value="g.value" />
            </CustomSelect>
          </template>
        </el-table-column>
        <el-table-column label="Năm" width="110">
          <template #default="{ row }">
            <CustomInputNumber v-model="row.nam_dat_giai" :min="2000" :max="2100" :controls="false" placeholder="Nhập năm" />
          </template>
        </el-table-column>
        <el-table-column label="Thao tác" width="80" align="center">
          <template #default="{ $index }">
            <NutXoa @click="f.thanh_tich.splice($index, 1)" />
          </template>
        </el-table-column>
        <template #empty><CustomEmpty description="Chưa có thành tích." /></template>
      </CustomTable>
    </CustomCard>

    <CustomCard shadow="never">
      <template #header>Nguyện vọng</template>
      <CustomForm class="form-grid" label-position="top" @submit.prevent>
        <div class="form-grid__body">
          <CustomFormItem class="form-grid__span-2" label="Ngành mong muốn">
            <CustomSelect v-model="f.nganh" multiple filterable collapse-tags collapse-tags-tooltip placeholder="Chọn ngành">
              <CustomOption v-for="n in nganh" :key="n.ma_nganh" :label="`${n.ma_nganh} — ${n.ten_nganh}`" :value="n.ma_nganh" />
            </CustomSelect>
          </CustomFormItem>
          <CustomFormItem class="form-grid__span-2" label="Tỉnh/thành muốn học">
            <CustomSelect v-model="f.tinhMongMuon" multiple filterable collapse-tags collapse-tags-tooltip placeholder="Chọn tỉnh/thành">
              <CustomOption v-for="t in tinh" :key="t.ma_tinh" :label="t.ten_tinh" :value="t.ma_tinh" />
            </CustomSelect>
          </CustomFormItem>
          <CustomFormItem label="Vùng miền">
            <CustomSelect v-model="f.vung" multiple placeholder="Chọn vùng">
              <CustomOption v-for="v in VUNG" :key="v" :label="v" :value="v" />
            </CustomSelect>
          </CustomFormItem>
        </div>
      </CustomForm>
    </CustomCard>

    <div class="hs-xt__cuoi">
      <CustomButton type="primary" :loading="dangLuu" @click="luu">
        <CustomIcon><Check /></CustomIcon>
        <span>Lưu hồ sơ</span>
      </CustomButton>
    </div>
  </div>
</template>

<script setup>
/**
 * Hồ sơ xét tuyển (bước 4.5): nhập đầy đủ dữ liệu cho bộ tính xét tuyển — điểm từng môn, học bạ, bài thi,
 * chứng chỉ có hạn, thành tích có mức giải, nguyện vọng. Gọi API /ho-so-xet-tuyen/cua-toi; server ghi song song
 * sang Hồ sơ năng lực cũ.
 */
import { h, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { fetchBaiThiDanhGiaNangLuc } from '@/api/baiThiDanhGiaNangLuc'
import { fetchBangCapChungChi } from '@/api/bangCapChungChi'
import { fetchDoiTuongUuTien } from '@/api/doiTuongUuTien'
import { fetchHoSoXetTuyen, luuHoSoXetTuyen } from '@/api/hoSoXetTuyen'
import { fetchKhuVucUuTien } from '@/api/khuVucUuTien'
import { fetchMonHoc } from '@/api/monHoc'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchThanhTichHocTapNghienCuu } from '@/api/thanhTichHocTapNghienCuu'
import { fetchTinhThanh } from '@/api/tinhThanh'
import CustomButton from '@/components/element/CustomButton.vue'
import CustomIcon from '@/components/element/CustomIcon.vue'
import CustomTooltip from '@/components/element/CustomTooltip.vue'

defineOptions({ name: 'HoSoXetTuyen' })

const LOP = [10, 11, 12]
const MUC = [
  { value: 4, label: 'Tốt / Giỏi' },
  { value: 3, label: 'Khá' },
  { value: 2, label: 'Đạt / Trung bình' },
  { value: 1, label: 'Chưa đạt / Yếu' },
]
const GIAI = [
  { value: 1, label: 'Nhất / Vàng' },
  { value: 2, label: 'Nhì / Bạc' },
  { value: 3, label: 'Ba / Đồng' },
  { value: 4, label: 'Khuyến khích / Tư' },
  { value: 9, label: 'Tham gia' },
]
const CHUONG_TRINH = [
  { value: 'GDPT_2018', label: 'GDPT 2018' },
  { value: 'GDPT_2006', label: 'GDPT 2006' },
  { value: 'NUOC_NGOAI', label: 'Nước ngoài' },
]
const VUNG = ['Bắc', 'Trung', 'Nam']
const namHienTai = new Date().getFullYear()

// Nút xóa dòng: chỉ có icon, có tooltip (tự tắt trên mobile).
const NutXoa = (_props, { attrs }) =>
  h(CustomTooltip, { content: 'Xóa dòng', placement: 'top' }, () =>
    h(CustomButton, { link: true, type: 'danger', 'aria-label': 'Xóa dòng', onClick: attrs.onClick }, () =>
      h(CustomIcon, null, () => h(Delete)),
    ),
  )

const dangTai = ref(false)
const dangLuu = ref(false)
const tuDuLieuCu = ref(false)
const mon = ref([])
const tinh = ref([])
const khuVuc = ref([])
const doiTuong = ref([])
const baiThi = ref([])
const chungChi = ref([])
const thanhTich = ref([])
const nganh = ref([])
// Điểm học kỳ và nguyện vọng loại khác (chưa có ô nhập riêng) giữ nguyên khi lưu.
let diemHocKy = []
let mongMuonKhac = []

const f = reactive(formTrong())

function formTrong() {
  return {
    ten_ho_so: null,
    nam_tot_nghiep: namHienTai,
    da_tot_nghiep: true,
    chuong_trinh_thpt: 'GDPT_2018',
    he_chuyen: false,
    ma_mon_chuyen: '',
    ten_truong_thpt: '',
    ma_tinh: '',
    ma_khu_vuc_uu_tien: '',
    ma_doi_tuong_uu_tien: '',
    ngan_sach_hoc_phi_nam: null,
    ket_qua_nam_hoc: LOP.map((lop) => ({ lop, diem_tb_chung: null, hoc_luc: null, ren_luyen: null })),
    thpt: [],
    hocBa: [],
    diem_bai_thi: [],
    chung_chi: [],
    thanh_tich: [],
    nganh: [],
    tinhMongMuon: [],
    vung: [],
  }
}

const rong = (v) => (v === '' || v === undefined ? null : v)

function nap(data) {
  Object.assign(f, formTrong(), {
    ten_ho_so: data.ten_ho_so,
    nam_tot_nghiep: data.nam_tot_nghiep,
    da_tot_nghiep: data.da_tot_nghiep,
    chuong_trinh_thpt: data.chuong_trinh_thpt,
    he_chuyen: data.he_chuyen,
    ma_mon_chuyen: data.ma_mon_chuyen || '',
    ten_truong_thpt: data.ten_truong_thpt || '',
    ma_tinh: data.ma_tinh || '',
    ma_khu_vuc_uu_tien: data.ma_khu_vuc_uu_tien || '',
    ma_doi_tuong_uu_tien: data.ma_doi_tuong_uu_tien || '',
    ngan_sach_hoc_phi_nam: data.ngan_sach_hoc_phi_nam,
    diem_bai_thi: data.diem_bai_thi.map((b) => ({ ...b, phan_tu_chon: b.phan_tu_chon || '' })),
    chung_chi: data.chung_chi.map((c) => ({ ...c, cap_do: c.cap_do || '' })),
    thanh_tich: data.thanh_tich.map((t) => ({ ...t, ma_mon: t.ma_mon || '' })),
  })
  for (const k of data.ket_qua_nam_hoc) {
    const dong = f.ket_qua_nam_hoc.find((x) => x.lop === k.lop)
    if (dong) Object.assign(dong, k)
  }
  f.thpt = data.diem_mon
    .filter((d) => d.nguon_diem === 'THI_THPT')
    .map((d) => ({ ma_mon: d.ma_mon, diem: d.diem, la_du_kien: d.la_du_kien }))
  const hocBa = new Map()
  for (const d of data.diem_mon.filter((x) => x.nguon_diem === 'HOC_BA' && x.hoc_ky === 0)) {
    if (!hocBa.has(d.ma_mon)) hocBa.set(d.ma_mon, { ma_mon: d.ma_mon, 10: null, 11: null, 12: null })
    hocBa.get(d.ma_mon)[d.lop] = d.diem
  }
  f.hocBa = [...hocBa.values()]
  diemHocKy = data.diem_mon.filter((x) => x.nguon_diem === 'HOC_BA' && x.hoc_ky !== 0)
  f.nganh = data.mong_muon.filter((m) => m.loai === 'NGANH').map((m) => m.gia_tri)
  f.tinhMongMuon = data.mong_muon.filter((m) => m.loai === 'TINH_THANH').map((m) => m.gia_tri)
  f.vung = data.mong_muon.filter((m) => m.loai === 'VUNG_MIEN').map((m) => m.gia_tri)
  mongMuonKhac = data.mong_muon.filter((m) => !['NGANH', 'TINH_THANH', 'VUNG_MIEN'].includes(m.loai))
  tuDuLieuCu.value = Boolean(data.tu_du_lieu_cu)
}

function payload() {
  const diemMon = [
    ...f.thpt
      .filter((d) => d.ma_mon && d.diem != null)
      .map((d) => ({ ma_mon: d.ma_mon, nguon_diem: 'THI_THPT', diem: d.diem, la_du_kien: d.la_du_kien })),
    ...f.hocBa.flatMap((d) =>
      d.ma_mon
        ? LOP.filter((lop) => d[lop] != null).map((lop) => ({ ma_mon: d.ma_mon, nguon_diem: 'HOC_BA', lop, diem: d[lop] }))
        : [],
    ),
    ...diemHocKy,
  ]
  return {
    ten_ho_so: f.ten_ho_so,
    nam_tot_nghiep: rong(f.nam_tot_nghiep),
    da_tot_nghiep: f.da_tot_nghiep,
    chuong_trinh_thpt: f.chuong_trinh_thpt,
    he_chuyen: f.he_chuyen,
    ma_mon_chuyen: f.he_chuyen ? rong(f.ma_mon_chuyen) : null,
    ten_truong_thpt: rong(f.ten_truong_thpt?.trim()),
    ma_tinh: rong(f.ma_tinh),
    ma_khu_vuc_uu_tien: rong(f.ma_khu_vuc_uu_tien),
    ma_doi_tuong_uu_tien: rong(f.ma_doi_tuong_uu_tien),
    ngan_sach_hoc_phi_nam: rong(f.ngan_sach_hoc_phi_nam),
    ket_qua_nam_hoc: f.ket_qua_nam_hoc
      .filter((k) => k.diem_tb_chung != null || k.hoc_luc || k.ren_luyen)
      .map((k) => ({ lop: k.lop, diem_tb_chung: rong(k.diem_tb_chung), hoc_luc: rong(k.hoc_luc), ren_luyen: rong(k.ren_luyen) })),
    diem_mon: diemMon,
    diem_bai_thi: f.diem_bai_thi
      .filter((b) => b.ma_bai_thi && b.diem != null && b.nam_thi)
      .map((b) => ({ ...b, phan_tu_chon: rong(b.phan_tu_chon?.trim()) })),
    chung_chi: f.chung_chi
      .filter((c) => c.ma_chung_chi && (c.diem != null || c.cap_do))
      .map((c) => ({ ...c, cap_do: rong(c.cap_do?.trim()) })),
    thanh_tich: f.thanh_tich
      .filter((t) => t.ma_thanh_tich && t.muc_giai)
      .map((t) => ({ ...t, ma_mon: rong(t.ma_mon) })),
    mong_muon: [
      ...f.nganh.map((gia_tri) => ({ loai: 'NGANH', gia_tri })),
      ...f.tinhMongMuon.map((gia_tri) => ({ loai: 'TINH_THANH', gia_tri })),
      ...f.vung.map((gia_tri) => ({ loai: 'VUNG_MIEN', gia_tri })),
      ...mongMuonKhac,
    ],
  }
}

function thongBaoLoi(error, macDinh) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return macDinh
}

async function taiTatCa(ham) {
  const items = []
  for (let trang = 1; trang <= 20; trang += 1) {
    const data = await ham({ page: trang, page_size: 1000 })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
  }
  return items
}

async function luu() {
  dangLuu.value = true
  try {
    nap(await luuHoSoXetTuyen(payload()))
    ElMessage.success('Đã lưu hồ sơ xét tuyển')
  } catch (error) {
    ElMessage.error(thongBaoLoi(error, 'Không lưu được hồ sơ xét tuyển'))
  } finally {
    dangLuu.value = false
  }
}

onMounted(async () => {
  dangTai.value = true
  try {
    const [hoSo, ...danhMuc] = await Promise.all([
      fetchHoSoXetTuyen({ skipLoading: true }),
      taiTatCa(fetchMonHoc),
      taiTatCa(fetchTinhThanh),
      taiTatCa(fetchKhuVucUuTien),
      taiTatCa(fetchDoiTuongUuTien),
      taiTatCa(fetchBaiThiDanhGiaNangLuc),
      taiTatCa(fetchBangCapChungChi),
      taiTatCa(fetchThanhTichHocTapNghienCuu),
      taiTatCa(fetchNganh),
    ])
    ;[mon.value, tinh.value, khuVuc.value, doiTuong.value, baiThi.value, chungChi.value, thanhTich.value, nganh.value] =
      danhMuc
    // Hồ sơ tham chiếu danh mục bằng mã: bỏ dòng danh mục chưa có mã.
    baiThi.value = baiThi.value.filter((b) => b.ma_bai_thi)
    chungChi.value = chungChi.value.filter((c) => c.ma_chung_chi)
    nap(hoSo)
  } catch (error) {
    ElMessage.error(thongBaoLoi(error, 'Không tải được hồ sơ xét tuyển'))
  } finally {
    dangTai.value = false
  }
})
</script>

<style scoped>
.hs-xt {
  display: grid;
  gap: 16px;
}

.hs-xt__dau {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.hs-xt__tieu-de {
  margin: 0 0 4px;
  font-size: 20px;
}

.hs-xt__phu {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.hs-xt__bao {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--el-color-warning-light-9);
  font-size: 13px;
  line-height: 1.5;
}

.hs-xt__khoi-dau {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.hs-xt__cuoi {
  display: flex;
  justify-content: flex-end;
}
</style>
