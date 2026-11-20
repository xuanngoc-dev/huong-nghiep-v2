<template>
  <div class="catalog-page">
    <template v-if="!id">
      <div class="dieu-huong">
        <router-link class="cell-link" :to="{ name: TRANG_THU_THAP }">Thu thập dữ liệu</router-link>
      </div>
      <DanhSachPhienTuyenSinh tieu-de="Xét duyệt dữ liệu" :trang-chi-tiet="TRANG_XET_DUYET" xet-duyet />
    </template>

    <template v-else>
      <div class="dieu-huong">
        <router-link class="cell-link" :to="{ name: TRANG_XET_DUYET }">‹ Hàng đợi xét duyệt</router-link>
        <router-link class="cell-link" :to="{ name: TRANG_THU_THAP, query: { phien: id } }">{{ chiTiet?.trang_thai === 'yeu_cau_bo_sung' ? 'Mở phiên để bổ sung nguồn' : 'Xem nguồn đã thu thập' }}</router-link>
      </div>
      <CustomCard v-if="!chiTiet" shadow="never" class="catalog-card">
        <p v-if="dangTai" role="status">Đang tải hồ sơ…</p>
        <template v-else-if="loiTai">
          <el-alert :title="loiTai" type="error" show-icon :closable="false" />
          <CustomButton class="canh-bao" @click="tai">Tải lại</CustomButton>
        </template>
      </CustomCard>

      <template v-else>
        <CustomCard shadow="never" class="catalog-card">
          <div class="toolbar">
            <h2 class="toolbar__title">{{ chiTiet.ma_truong }} · {{ chiTiet.ten_truong }} · {{ chiTiet.nam_tuyen_sinh }}</h2>
            <CustomTag :type="trangThaiHienThi.loai" aria-live="polite">{{ trangThaiHienThi.nhan }}</CustomTag>
          </div>
          <dl class="thong-tin">
            <div><dt>Mã phiên</dt><dd>#{{ id }}</dd></div>
            <div v-if="chiTiet.co_so"><dt>Cơ sở</dt><dd>{{ chiTiet.co_so }}</dd></div>
            <div><dt>Người tạo phiên</dt><dd>{{ chiTiet.ten_nguoi_tao || `#${chiTiet.tao_boi}` }}</dd></div>
            <div v-if="banNhap"><dt>Người tạo phiên bản</dt><dd>{{ banNhap.ten_nguoi_tao || '—' }}</dd></div>
            <div v-if="banNhap"><dt>Ngày tạo phiên bản</dt><dd>{{ ngayGio(banNhap.tao_luc) }}</dd></div>
          </dl>
          <div v-if="banNhap" class="phien-ban">
            <label for="phien-ban-xet-duyet">Phiên bản</label>
            <CustomSelect id="phien-ban-xet-duyet" :model-value="banNhap.phien_ban" placeholder="Chọn phiên bản" :disabled="Boolean(thaoTac)" @change="moPhienBan">
              <CustomOption v-for="muc in chiTiet.cac_phien_ban" :key="muc.phien_ban" :label="`Phiên bản ${muc.phien_ban}${muc.phien_ban === chiTiet.phien_ban ? ' · Mới nhất' : ''}`" :value="muc.phien_ban" />
            </CustomSelect>
          </div>

          <el-alert v-if="phienBan" title="Đang xem phiên bản lưu trong lịch sử" type="info" show-icon :closable="false" class="canh-bao">
            <router-link class="cell-link" :to="{ name: TRANG_XET_DUYET, query: { phien: id } }">Mở phiên bản mới nhất</router-link>
          </el-alert>

          <el-alert v-if="chiTiet.trang_thai === 'yeu_cau_bo_sung' && chiTiet.yeu_cau_bo_sung" title="Yêu cầu bổ sung" type="warning" show-icon :closable="false" class="canh-bao">
            <p>{{ chiTiet.yeu_cau_bo_sung.ly_do }}</p>
            <ul v-if="chiTiet.yeu_cau_bo_sung.duong_dan.length" class="danh-sach-bao">
              <li v-for="duongDan in chiTiet.yeu_cau_bo_sung.duong_dan" :key="duongDan">{{ duongDan }}</li>
            </ul>
          </el-alert>

          <div v-if="daDuyet" class="da-duyet">
            <dl class="thong-tin">
              <div><dt>Mã đề án đã nhập</dt><dd>#{{ chiTiet.de_an_id }}</dd></div>
              <div><dt>Người duyệt</dt><dd>{{ chiTiet.ten_nguoi_duyet || `#${chiTiet.duyet_boi}` }}</dd></div>
              <div><dt>Thời điểm duyệt</dt><dd>{{ ngayGio(chiTiet.duyet_luc) }}</dd></div>
            </dl>
            <div class="cac-nut">
              <CustomButton v-if="chiTiet.de_an_id" type="primary" @click="moDeAn(chiTiet.de_an_id)"><CustomIcon><View /></CustomIcon> Mở đề án</CustomButton>
              <CustomButton :disabled="Boolean(thaoTac)" :loading="thaoTac === 'tai-json'" @click="taiJson"><CustomIcon><Download /></CustomIcon> Tải JSON</CustomButton>
            </div>
          </div>

          <el-alert v-if="loiThaoTac" :title="loiThaoTac.noiDung" type="error" show-icon :closable="false" class="canh-bao">
            <ul v-if="loiThaoTac.loi.length" class="danh-sach-bao">
              <li v-for="(loi, index) in loiThaoTac.loi" :key="index">
                <button v-if="duongDanLoi(loi)" class="nut-dong-loi" type="button" @click="doiChieu?.moDuongDan(duongDanLoi(loi))">{{ loi }}</button>
                <template v-else>{{ loi }}</template>
              </li>
            </ul>
            <CustomButton v-if="loiThaoTac.deAnId" link type="primary" @click="moDeAn(loiThaoTac.deAnId)">Mở đề án hiện có</CustomButton>
            <CustomButton v-else-if="loiThaoTac.trangThai === 409" link type="primary" @click="taiBanMoi">Tải phiên bản mới nhất</CustomButton>
          </el-alert>

          <div v-if="coTheSua" class="cac-nut thao-tac">
            <CustomButton :disabled="Boolean(thaoTac)" :loading="thaoTac === 'luu'" @click="luuBanNhap">Sửa và lưu nháp</CustomButton>
            <CustomButton type="warning" plain :disabled="Boolean(thaoTac)" @click="moBoSung">Yêu cầu bổ sung</CustomButton>
            <CustomButton type="primary" :disabled="Boolean(thaoTac || banNhap?.loi?.length)" :loading="thaoTac === 'duyet'" @click="duyetBanNhap">Duyệt và đưa vào hệ thống</CustomButton>
            <span v-if="coChinhSua" class="chu-thich" role="status">Có chỉnh sửa chưa lưu</span>
          </div>
        </CustomCard>

        <CustomCard v-if="banNhap?.loi?.length || Object.keys(nguonBiBoQua).length || ghiChuTrichXuat.length || loiSoSanh" shadow="never" class="catalog-card">
          <el-alert v-if="banNhap.loi?.length" title="Các mục cần xử lý trước khi duyệt" type="warning" show-icon :closable="false">
            <ul class="danh-sach-bao danh-sach-bao--cuon">
              <li v-for="(loi, index) in banNhap.loi" :key="index">
                <button v-if="duongDanLoi(loi)" class="nut-dong-loi" type="button" @click="doiChieu?.moDuongDan(duongDanLoi(loi))">{{ loi }}</button>
                <template v-else>{{ loi }}</template>
              </li>
            </ul>
          </el-alert>
          <el-alert v-if="Object.keys(nguonBiBoQua).length" title="Bản nháp đã lưu có nguồn bị bỏ qua" type="warning" show-icon :closable="false" class="canh-bao">
            <ul class="danh-sach-bao danh-sach-bao--cuon">
              <li v-for="(lyDo, nguonId) in nguonBiBoQua" :key="nguonId">{{ lyDo }}</li>
            </ul>
          </el-alert>
          <details v-if="ghiChuTrichXuat.length" class="ghi-chu">
            <summary>Ghi chú trích xuất ({{ ghiChuTrichXuat.length }})</summary>
            <ul class="danh-sach-bao danh-sach-bao--cuon">
              <li v-for="(ghiChu, index) in ghiChuTrichXuat" :key="index">{{ ghiChu }}</li>
            </ul>
          </details>
          <p v-if="loiSoSanh" class="chu-thich" role="status">{{ loiSoSanh }}</p>
        </CustomCard>

        <CustomCard v-if="Object.keys(canXacNhan).length || doiChieuNguon.length" shadow="never" class="catalog-card">
          <h3>Đối chiếu danh sách và chỉ tiêu</h3>
          <details v-if="doiChieuNguon.length" class="ghi-chu">
            <summary>Các mục đã đối chiếu trong tài liệu ({{ doiChieuNguon.length }})</summary>
            <ul class="danh-sach-bao danh-sach-bao--cuon">
              <li v-for="(nguon, index) in doiChieuNguon" :key="index">
                <strong>Nguồn #{{ nguon.nguon_id }} · {{ nguon.vi_tri }}</strong>
                <p>{{ nguon.trich_dan }}</p>
                <p v-if="nguon.cac_ma?.length">{{ nguon.cac_ma.join(', ') }}</p>
                <p v-if="nguon.tong_cong_bo != null">Số mã công bố: {{ nguon.tong_cong_bo }}</p>
              </li>
            </ul>
          </details>
          <CustomForm v-if="coTheSua" :model="lyDoDoiChieu" @submit.prevent="luuBanNhap">
            <CustomFormItem v-for="(yeuCau, khoa) in canXacNhan" :key="khoa" :label="khoa === 'chuong_trinh' ? 'Xác nhận danh sách mã' : 'Xác nhận phạm vi chỉ tiêu'">
              <p class="chu-thich">{{ yeuCau }}</p>
              <CustomSelect v-model="lyDoDoiChieu[khoa].nguon_id" clearable placeholder="Chọn nguồn làm căn cứ" :disabled="Boolean(thaoTac)">
                <CustomOption v-for="nguon in nguonXacNhan" :key="nguon.id" :value="nguon.id" :label="`#${nguon.id} · ${nguon.tieu_de}`" />
              </CustomSelect>
              <CustomInput v-model="lyDoDoiChieu[khoa].ly_do" type="textarea" :rows="2" maxlength="2000" placeholder="Lý do xác nhận" :disabled="Boolean(thaoTac)" />
            </CustomFormItem>
            <CustomButton v-if="coSuaXacNhan" :disabled="Boolean(thaoTac)" @click="luuBanNhap">Lưu xác nhận đối chiếu</CustomButton>
          </CustomForm>
        </CustomCard>

        <DoiChieuBanNhap v-if="banNhap" ref="doiChieu" :key="id" v-model="thayDoi" :cap-nhat="doiMoi" :cac-muc="cacMuc" :nguon="banNhap.nguon || chiTiet.nguon" :co-the-sua="coTheSua" :co-ban-truoc="Boolean(banTruoc)" :dang-xu-ly="Boolean(thaoTac)" @them-truong="moThemTruong" />
        <CustomCard v-else shadow="never" class="catalog-card"><CustomEmpty description="Phiên này chưa có bản nháp." /></CustomCard>

        <CustomCard v-if="chiTiet.lich_su.length" shadow="never" class="catalog-card">
          <details>
            <summary>Lịch sử xử lý ({{ chiTiet.lich_su.length }})</summary>
            <ul class="lich-su">
              <li v-for="(muc, index) in chiTiet.lich_su" :key="index">
                <strong>{{ hanhDong[muc.hanh_dong] || muc.hanh_dong }}</strong>
                <span class="chu-thich"> · {{ muc.nguoi_dung || '—' }} · {{ ngayGio(muc.tao_luc) }}<template v-if="muc.phien_ban"> · Phiên bản {{ muc.phien_ban }}</template></span>
                <details v-if="muc.chi_tiet && Object.keys(muc.chi_tiet).length" class="lich-su__chi-tiet">
                  <summary>Xem chi tiết</summary><pre>{{ hienGiaTri(muc.chi_tiet) }}</pre>
                </details>
              </li>
            </ul>
          </details>
        </CustomCard>
      </template>
    </template>

    <CustomDialog v-model="boSung.hien" title="Yêu cầu bổ sung" width="640px" :close-on-click-modal="false">
      <CustomForm class="form-grid" :model="boSung" @submit.prevent="guiBoSung">
        <div class="form-grid__body">
          <CustomFormItem class="form-grid__full" label="Mục cần làm rõ" required>
            <el-select-v2 v-model="boSung.duongDan" :options="tuyChonBoSung" multiple :multiple-limit="100" filterable placeholder="Chọn các mục cần bổ sung" />
          </CustomFormItem>
          <CustomFormItem class="form-grid__full" label="Lý do yêu cầu bổ sung" required>
            <CustomInput v-model="boSung.lyDo" type="textarea" :rows="3" placeholder="Nhập nội dung cần làm rõ hoặc nguồn cần bổ sung" maxlength="2000" show-word-limit />
          </CustomFormItem>
        </div>
      </CustomForm>
      <template #footer>
        <CustomButton @click="boSung.hien = false">Hủy</CustomButton>
        <CustomButton type="warning" :disabled="Boolean(thaoTac) || !boSung.duongDan.length || !boSung.lyDo.trim()" @click="guiBoSung">Gửi yêu cầu bổ sung</CustomButton>
      </template>
    </CustomDialog>

    <CustomDialog v-model="themTruong.hien" title="Thêm hoặc thay thế trường" width="640px" :close-on-click-modal="false">
      <CustomForm class="form-grid" :model="themTruong" @submit.prevent="luuTruong">
        <div class="form-grid__body">
          <CustomFormItem class="form-grid__full" label="Đường dẫn JSON Pointer" required>
            <CustomInput v-model="themTruong.duongDan" placeholder="Nhập đường dẫn, ví dụ /dats_tuyen_sinh/ghi_chu" maxlength="500" />
          </CustomFormItem>
          <CustomFormItem class="form-grid__full" label="Giá trị mới (JSON)" required>
            <CustomInput v-model="themTruong.giaTriJson" type="textarea" class="json-input" :rows="4" placeholder='Nhập giá trị JSON, ví dụ "Theo thông báo của trường"' />
          </CustomFormItem>
          <CustomFormItem class="form-grid__full" label="Lý do sửa" required>
            <CustomInput v-model="themTruong.lyDo" type="textarea" :rows="2" placeholder="Nhập lý do thêm hoặc thay thế trường" maxlength="2000" show-word-limit />
          </CustomFormItem>
        </div>
      </CustomForm>
      <el-alert v-if="themTruong.loi" :title="themTruong.loi" type="error" show-icon :closable="false" />
      <template #footer>
        <CustomButton @click="themTruong.hien = false">Hủy</CustomButton>
        <CustomButton type="primary" :disabled="Boolean(thaoTac) || !themTruong.duongDan.trim() || !themTruong.giaTriJson.trim() || !themTruong.lyDo.trim()" @click="luuTruong">Áp dụng vào bản nháp</CustomButton>
      </template>
    </CustomDialog>

    <ChiTietDeAnDialog v-model="hienDeAn" :de-an-id="deAnId" />
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { duyetBanNhapTuyenSinh, layJsonTuyenSinhDaDuyet, layPhienTuyenSinh, suaBanNhapTuyenSinh, yeuCauBoSungTuyenSinh } from '@/api/thuThapTuyenSinh'
import { taiNoiDungJson } from '@/utils/jsonFile'
import ChiTietDeAnDialog from './ChiTietDeAnDialog.vue'
import DanhSachPhienTuyenSinh from './DanhSachPhienTuyenSinh.vue'
import DoiChieuBanNhap from './DoiChieuBanNhap.vue'
import { giaTriTheoDuongDan, hienGiaTri, lapDanhSachMuc, phanTichGiaTri, tachDuongDan } from './doi-chieu-ban-nhap'
import { TRANG_THU_THAP, TRANG_XET_DUYET, loiPhien, ngayGio, nguonBiBoQuaKhiTaoBanNhap, trangThaiPhien } from './thu-thap-du-lieu'
import { usePhienTuyenSinh } from './usePhienTuyenSinh'

const router = useRouter()
const { id, phienBan, chiTiet, dangTai, loiTai, dangTaoBanNhap, tai, apDung } = usePhienTuyenSinh(true)
const doiChieu = ref(null)
const doiMoi = ref(0)
const thayDoi = ref([])
const thaoTac = ref('')
const loiThaoTac = ref(null)
const banTruoc = ref(null)
const loiSoSanh = ref('')
const hienDeAn = ref(false)
const deAnId = ref(null)
const boSung = reactive({ hien: false, duongDan: [], lyDo: '' })
const themTruong = reactive({ hien: false, duongDan: '', giaTriJson: '', lyDo: '', loi: '' })
const lyDoDoiChieu = reactive({ chuong_trinh: {}, chi_tieu: {} })

const hanhDong = {
  tao_phien: 'Tạo phiên', tim_nguon: 'Tìm nguồn', them_nguon: 'Bổ sung URL', chon_nguon: 'Cập nhật lựa chọn nguồn',
  chon_nhieu_nguon: 'Dùng tất cả nguồn phù hợp',
  tao_ban_nhap_that_bai: 'Tạo bản nháp thất bại',
  dung_tao_ban_nhap: 'Dừng tạo bản nháp',
  tao_ban_nhap: 'Tạo bản nháp', sua_ban_nhap: 'Sửa bản nháp', luu_ban_nhap: 'Lưu bản nháp', yeu_cau_bo_sung: 'Yêu cầu bổ sung', duyet: 'Duyệt và nhập',
}

const banNhap = computed(() => chiTiet.value?.ban_nhap)
const nguonBiBoQua = computed(() => nguonBiBoQuaKhiTaoBanNhap(chiTiet.value))
const ghiChuTrichXuat = computed(() => {
  const daHien = new Set(Object.values(nguonBiBoQua.value))
  return (banNhap.value?.ghi_chu || []).filter((ghiChu) => !daHien.has(ghiChu))
})
const cacMuc = computed(() => lapDanhSachMuc(banNhap.value, banTruoc.value))
const duongDanBanNhap = computed(() => new Set(banNhap.value?.muc?.map((muc) => muc.duong_dan)))
const trangThaiHienThi = computed(() => trangThaiPhien(chiTiet.value?.trang_thai, dangTaoBanNhap.value))
const coTheSua = computed(() => Boolean(banNhap.value && !phienBan.value && !dangTaoBanNhap.value && chiTiet.value?.trang_thai === 'cho_duyet'))
const daDuyet = computed(() => !phienBan.value && chiTiet.value?.trang_thai === 'da_duyet_va_nhap')
const canXacNhan = computed(() => banNhap.value?.doi_chieu?.can_xac_nhan || {})
const doiChieuNguon = computed(() => banNhap.value?.doi_chieu?.nguon || [])
const xacNhanDaLuu = computed(() => banNhap.value?.doi_chieu?.xac_nhan || {})
const nguonXacNhan = computed(() => (banNhap.value?.nguon || []).filter((nguon) => nguon.chinh_thuc && nguon.phu_hop
  && nguon.lua_chon === 'su_dung' && !nguon.chi_diem_lich_su && nguon.nam_ap_dung === chiTiet.value?.nam_tuyen_sinh))
const xacNhanThayDoi = computed(() => Object.fromEntries(Object.keys(canXacNhan.value)
  .map((khoa) => {
    const { nguon_id, ly_do: noiDung } = lyDoDoiChieu[khoa]
    const ly_do = noiDung?.trim()
    return [khoa, ly_do ? { nguon_id, ly_do } : null]
  })
  .filter(([khoa, canCu]) => canCu?.ly_do !== xacNhanDaLuu.value[khoa]?.ly_do
    || canCu?.nguon_id !== xacNhanDaLuu.value[khoa]?.nguon_id)))
const coSuaXacNhan = computed(() => Object.keys(xacNhanThayDoi.value).length > 0)
const coChinhSua = computed(() => Boolean(thayDoi.value.length || doiChieu.value?.daNhapSua || coSuaXacNhan.value))
const tuyChonBoSung = computed(() => boSung.hien ? cacMuc.value.filter((muc) => !muc.daBo).map((muc) => ({
  label: `${muc.nhan} · ${muc.viTri} · ${muc.duong_dan}`,
  value: muc.duong_dan,
})) : [])

watch([id, phienBan], () => {
  thayDoi.value = []
  thaoTac.value = ''
  loiThaoTac.value = null
  boSung.hien = false
  themTruong.hien = false
})

watch(banNhap, () => {
  for (const khoa of Object.keys(lyDoDoiChieu)) {
    lyDoDoiChieu[khoa] = { nguon_id: null, ly_do: '', ...xacNhanDaLuu.value[khoa] }
  }
}, { immediate: true })

watch([id, () => banNhap.value?.phien_ban], async ([phienId, ban], _, onCleanup) => {
  banTruoc.value = null
  loiSoSanh.value = ''
  const soBanTruoc = Math.max(0, ...(chiTiet.value?.cac_phien_ban || []).map((muc) => muc.phien_ban).filter((so) => so < ban))
  if (!soBanTruoc) return
  let conHieuLuc = true
  onCleanup(() => { conHieuLuc = false })
  try {
    const ketQua = await layPhienTuyenSinh(phienId, soBanTruoc)
    if (conHieuLuc) banTruoc.value = ketQua.ban_nhap
  } catch {
    if (conHieuLuc) loiSoSanh.value = 'Không tải được phiên bản trước để so sánh.'
  }
}, { immediate: true })

function xacNhanBoSua() {
  if (!coChinhSua.value) return true
  return ElMessageBox.confirm('Bạn có chỉnh sửa chưa lưu. Rời màn hình sẽ bỏ các chỉnh sửa này.', 'Chỉnh sửa chưa lưu', {
    type: 'warning', confirmButtonText: 'Bỏ chỉnh sửa', cancelButtonText: 'Tiếp tục sửa',
  }).then(() => true).catch(() => false)
}

onBeforeRouteLeave(xacNhanBoSua)
onBeforeRouteUpdate(xacNhanBoSua)

function moPhienBan(so) {
  const query = { phien: id.value }
  if (so !== chiTiet.value.phien_ban) query.phien_ban = so
  return router.push({ name: TRANG_XET_DUYET, query })
}

function duongDanLoi(loi) {
  const viTri = /^\/?((?:thong_tin_import|dats_tuyen_sinh|quy_tac_xet_tuyen)\/[^:]+):/.exec(loi)?.[1]
  const duongDan = viTri ? `/${viTri}` : ''
  return duongDanBanNhap.value.has(duongDan) ? duongDan : ''
}

async function taiBanMoi() {
  if (!await xacNhanBoSua()) return
  thayDoi.value = []
  loiThaoTac.value = null
  await tai()
}

async function thucHien(ten, gui) {
  if (thaoTac.value) return false
  const phienId = id.value
  thaoTac.value = ten
  loiThaoTac.value = null
  try {
    const ketQua = await gui(phienId)
    if (ketQua && apDung(ketQua)) {
      thayDoi.value = []
      doiMoi.value += 1
      return true
    }
  } catch (error) {
    if (id.value === phienId) loiThaoTac.value = loiPhien(error)
  } finally {
    if (id.value === phienId) thaoTac.value = ''
  }
  return false
}

function coTheChuyenTrangThai() {
  if (!coTheSua.value || thaoTac.value || doiChieu.value?.chuanBiLuu() === false) return false
  if (!coChinhSua.value) return true
  loiThaoTac.value = { noiDung: 'Lưu bản nháp trước khi đổi trạng thái hồ sơ.', loi: [] }
  return false
}

async function luuBanNhap() {
  if (!coTheSua.value || thaoTac.value || doiChieu.value?.chuanBiLuu() === false) return
  if (!thayDoi.value.length && !coSuaXacNhan.value) {
    ElMessage.info('Chưa có chỉnh sửa để lưu.')
    return
  }
  if (thayDoi.value.length > 500) {
    loiThaoTac.value = { noiDung: 'Mỗi lần lưu tối đa 500 mục. Hãy bỏ bớt chỉnh sửa ở lần lưu này.', loi: [] }
    return
  }
  const xacNhan = coSuaXacNhan.value ? xacNhanThayDoi.value : undefined
  if (xacNhan && Object.values(xacNhan).some((canCu) => canCu && !canCu.nguon_id)) {
    loiThaoTac.value = { noiDung: 'Chọn nguồn làm căn cứ cho mỗi xác nhận đối chiếu.', loi: [] }
    return
  }
  if (await thucHien('luu', (phienId) => suaBanNhapTuyenSinh(phienId, banNhap.value.phien_ban, thayDoi.value, xacNhan))) {
    ElMessage.success('Đã lưu bản nháp.')
  }
}

function moBoSung() {
  if (!coTheChuyenTrangThai()) return
  boSung.duongDan = cacMuc.value.filter((muc) => !muc.daBo && muc.mau_thuan).slice(0, 20).map((muc) => muc.duong_dan)
  boSung.lyDo = ''
  boSung.hien = true
}

async function guiBoSung() {
  const lyDo = boSung.lyDo.trim()
  if (!coTheSua.value || !lyDo || !boSung.duongDan.length || thaoTac.value) return
  boSung.hien = false
  if (await thucHien('bo-sung', (phienId) => yeuCauBoSungTuyenSinh(phienId, banNhap.value.phien_ban, boSung.duongDan, lyDo))) {
    ElMessage.success('Đã gửi yêu cầu bổ sung.')
  }
}

async function duyetBanNhap() {
  if (!coTheChuyenTrangThai()) return
  const soBan = banNhap.value.phien_ban
  const phienId = id.value
  try {
    await ElMessageBox.confirm(`Nhập đề án và quy tắc xét tuyển của ${chiTiet.value.ma_truong} năm ${chiTiet.value.nam_tuyen_sinh} từ phiên bản ${soBan}?`, 'Duyệt và đưa vào hệ thống', {
      type: 'warning', confirmButtonText: 'Duyệt và nhập', cancelButtonText: 'Hủy',
    })
  } catch {
    return
  }
  if (id.value !== phienId || banNhap.value?.phien_ban !== soBan) return
  if (await thucHien('duyet', () => duyetBanNhapTuyenSinh(phienId, soBan))) ElMessage.success('Đã duyệt và nhập.')
}

function moThemTruong(duongDan) {
  themTruong.duongDan = duongDan
  themTruong.giaTriJson = ''
  themTruong.lyDo = ''
  themTruong.loi = ''
  themTruong.hien = true
}

function luuTruong() {
  const duongDan = themTruong.duongDan.trim()
  const lyDo = themTruong.lyDo.trim()
  if (!coTheSua.value || !duongDan || !lyDo) return
  if (!duongDan.startsWith('/') || /~(?![01])/.test(duongDan) || tachDuongDan(duongDan).length < 2) {
    themTruong.loi = 'Nhập đường dẫn JSON Pointer tới trường bên trong một trong ba nhánh dữ liệu.'
    return
  }
  let giaTri
  try {
    giaTri = phanTichGiaTri(themTruong.giaTriJson)
  } catch {
    themTruong.loi = 'Giá trị mới cần đúng cú pháp JSON.'
    return
  }
  const chieuDai = duongDan.lastIndexOf('/')
  const mucCha = giaTriTheoDuongDan(banNhap.value.du_lieu, duongDan.slice(0, chieuDai))
  if (!mucCha || typeof mucCha !== 'object') {
    themTruong.loi = 'Trường cha cần tồn tại dưới dạng đối tượng hoặc danh sách.'
    return
  }
  const muc = banNhap.value.muc.find((item) => item.duong_dan === duongDan)
  thayDoi.value = [
    ...thayDoi.value.filter((item) => item.duong_dan !== duongDan),
    { duong_dan: duongDan, gia_tri: giaTri, ghi_chu: lyDo, dan_chung_ids: muc?.dan_chung_ids || [], da_kiem_tra: false },
  ]
  doiMoi.value += 1
  themTruong.hien = false
  ElMessage.info('Đã ghi nhận chỉnh sửa. Chọn Sửa và lưu nháp để lưu.')
}

function moDeAn(idDeAn) {
  deAnId.value = Number(idDeAn)
  hienDeAn.value = true
}

function taiJson() {
  if (!daDuyet.value || thaoTac.value) return
  const { ma_truong, nam_tuyen_sinh } = chiTiet.value
  return thucHien('tai-json', async (phienId) => {
    const duLieu = await layJsonTuyenSinhDaDuyet(phienId)
    taiNoiDungJson(`${ma_truong}_${nam_tuyen_sinh}_tuyen_sinh.json`, duLieu)
  })
}
</script>

<style scoped>
.dieu-huong, .cac-nut { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.dieu-huong { justify-content: space-between; }
.toolbar { flex-wrap: wrap; }
.thong-tin { display: flex; flex-wrap: wrap; gap: 8px 28px; margin: 0; }
.thong-tin dt { color: var(--el-text-color-secondary); font-size: 12px; }
.thong-tin dd { margin: 0; }
.phien-ban { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 12px; }
.phien-ban :deep(.el-select) { width: 220px; }
.canh-bao, .da-duyet, .thao-tac { margin-top: 12px; }
.da-duyet .cac-nut { margin-top: 10px; }
.cac-nut :deep(.el-button + .el-button) { margin-left: 0; }
.chu-thich { color: var(--el-text-color-secondary); }
.danh-sach-bao { margin: 4px 0; padding-inline-start: 20px; overflow-wrap: anywhere; }
.danh-sach-bao--cuon { max-height: 205px; overflow-y: auto; }
.nut-dong-loi { background: none; border: none; color: inherit; cursor: pointer; padding: 0; text-align: left; text-decoration: underline; }
.ghi-chu { margin-top: 8px; }
summary { cursor: pointer; }
.lich-su { margin: 8px 0 0; padding-inline-start: 20px; }
.lich-su > li { margin-top: 6px; }
.lich-su__chi-tiet { padding-inline-start: 12px; }
.lich-su__chi-tiet pre { margin: 5px 0; max-height: 250px; overflow-y: auto; white-space: pre-wrap; overflow-wrap: anywhere; }
</style>
