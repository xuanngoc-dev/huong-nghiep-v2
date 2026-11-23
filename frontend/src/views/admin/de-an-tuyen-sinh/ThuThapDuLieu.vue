<template>
  <div class="catalog-page">
    <template v-if="!id">
      <CustomCard shadow="never" class="catalog-card">
        <div class="toolbar">
          <h2 class="toolbar__title">Thu thập dữ liệu</h2>
          <router-link class="cell-link" :to="{ name: TRANG_XET_DUYET }">Xét duyệt dữ liệu</router-link>
        </div>
        <CustomForm :model="form" class="form-grid" @submit.prevent="batDau(true)">
          <div class="form-grid__body">
            <CustomFormItem label="Mã trường" required>
              <CustomInput v-model="form.ma_truong" placeholder="Nhập mã trường" maxlength="20" :disabled="dangTao" />
            </CustomFormItem>
            <CustomFormItem label="Năm tuyển sinh" required>
              <CustomInputNumber v-model="form.nam_tuyen_sinh" placeholder="Nhập năm tuyển sinh" :min="1990" :max="2100" :precision="0" :controls="false" :phan-tach-hang-nghin="false" :disabled="dangTao" />
            </CustomFormItem>
          </div>
          <p v-if="dangNhanDien" class="chu-thich" role="status">Đang nhận diện trường…</p>
          <p v-else-if="loiNhanDien" class="chu-thich chu-thich--loi" role="alert">{{ loiNhanDien }}</p>
          <p v-else-if="truong" class="nhan-dien">
            <strong>{{ truong.ten_truong }}</strong>
            <span v-if="truong.co_so">{{ truong.co_so }}</span>
          </p>
          <div class="toolbar__actions">
            <CustomButton type="primary" native-type="submit" :disabled="!truong || !form.nam_tuyen_sinh || dangTao">
              Thu thập toàn bộ
            </CustomButton>
            <CustomButton native-type="button" :disabled="!truong || !form.nam_tuyen_sinh || dangTao" @click="batDau(false)">
              <CustomIcon><Search /></CustomIcon> Tìm nguồn để chọn
            </CustomButton>
          </div>
          <p v-if="dangTao" class="chu-thich" role="status">Đang tạo phiên thu thập…</p>
        </CustomForm>
        <el-alert v-if="loiTao" :title="loiTao" type="error" show-icon :closable="false" class="canh-bao" />
      </CustomCard>
      <DanhSachPhienTuyenSinh tieu-de="Các phiên thu thập" :trang-chi-tiet="TRANG_THU_THAP" :phien-dang-tao="phienDangTao" />
    </template>

    <template v-else>
      <div class="dieu-huong">
        <router-link class="cell-link" :to="{ name: TRANG_THU_THAP }">‹ Các phiên thu thập</router-link>
        <router-link v-if="chiTiet?.phien_ban" v-slot="{ href, navigate }" custom :to="{ name: TRANG_XET_DUYET, query: { phien: id } }">
          <CustomButton tag="a" :href="href" type="primary" @click="navigate">Mở bản nháp và xét duyệt</CustomButton>
        </router-link>
      </div>
      <CustomCard v-if="!chiTiet" shadow="never" class="catalog-card">
        <p v-if="dangTai" role="status">Đang tải phiên…</p>
        <template v-else-if="loiTai">
          <el-alert :title="loiTai" type="error" show-icon :closable="false" />
          <CustomButton class="canh-bao" @click="tai">Tải lại</CustomButton>
        </template>
      </CustomCard>

      <template v-else>
        <CustomCard shadow="never" class="catalog-card">
          <div class="toolbar">
            <h2 class="toolbar__title">{{ chiTiet.ma_truong }} · {{ chiTiet.ten_truong }} · {{ chiTiet.nam_tuyen_sinh }}</h2>
            <CustomTag :type="trangThaiHienThi.loai">{{ trangThaiHienThi.nhan }}</CustomTag>
          </div>
          <dl class="thong-tin-phien">
            <div><dt>Mã phiên</dt><dd>#{{ id }}</dd></div>
            <div v-if="chiTiet.co_so"><dt>Cơ sở</dt><dd>{{ chiTiet.co_so }}</dd></div>
            <div><dt>Người tạo</dt><dd>{{ chiTiet.ten_nguoi_tao || `#${chiTiet.tao_boi}` }}</dd></div>
            <div><dt>Ngày tạo</dt><dd>{{ ngayGio(chiTiet.tao_luc) }}</dd></div>
          </dl>
          <el-alert v-if="chiTiet.yeu_cau_bo_sung && chiTiet.trang_thai === 'yeu_cau_bo_sung'" title="Yêu cầu bổ sung" type="warning" show-icon :closable="false" class="canh-bao">
            <p class="noi-dung-bao">{{ chiTiet.yeu_cau_bo_sung.ly_do }}</p>
            <ul v-if="chiTiet.yeu_cau_bo_sung.duong_dan?.length" class="danh-sach-bao">
              <li v-for="muc in chiTiet.yeu_cau_bo_sung.duong_dan" :key="muc">{{ muc }}</li>
            </ul>
          </el-alert>
        </CustomCard>

        <CustomCard shadow="never" class="catalog-card">
          <div class="toolbar">
            <h2 class="toolbar__title">Nguồn tài liệu</h2>
            <div v-if="choPhepSuaNguon" class="toolbar__actions">
              <CustomButton v-if="coNguonChuaChon || thaoTac === 'chon-tat-ca'" type="primary" plain :disabled="khoaNguon" :loading="thaoTac === 'chon-tat-ca'" @click="thucHien('chon-tat-ca', () => chonTatCaNguonTuyenSinh(id))">
                Dùng tất cả nguồn phù hợp
              </CustomButton>
              <CustomButton :disabled="khoaNguon || !coNguonDungNam" @click="taoBanNhap(false)">
                Tạo nháp từ nguồn đã chọn
              </CustomButton>
              <CustomButton type="primary" :disabled="khoaNguon" :loading="dangTaoBanNhap || dangKiemTraBanNhap" @click="taoBanNhap(true)">
                Thu thập toàn bộ
              </CustomButton>
            </div>
          </div>
          <div v-if="choPhepSuaNguon" class="tim-nguon">
            <CustomButton :disabled="khoaNguon" :loading="dangTimNguon" @click="timNguon">
              <CustomIcon><Search /></CustomIcon> {{ chiTiet.nguon.length ? 'Tìm lại' : 'Tìm nguồn' }}
            </CustomButton>
          </div>
          <p v-if="choPhepSuaNguon" class="chu-thich">Mở tài liệu để đối chiếu trường, cơ sở và năm trước khi chọn dùng. Đã chọn {{ nguonDaChon }} nguồn áp dụng.</p>
          <p v-if="choPhepSuaNguon && nguonDaChon && !coNguonDungNam" class="chu-thich">Chọn ít nhất một nguồn tuyển sinh đúng năm để tạo nháp từ nguồn đã chọn.</p>
          <div v-if="dangTaoBanNhap || dangDung" class="tien-do-nhap">
            <div class="tien-do-nhap__dau">
              <div>
                <p class="tien-do-nhap__nhan" role="status">{{ nhanTienDo }}</p>
                <p v-if="thoiGianDaChay" class="tien-do-nhap__dong-ho">Đã chạy {{ thoiGianDaChay }}</p>
              </div>
              <CustomButton type="danger" plain :disabled="!chiTiet.luot_tao_ban_nhap" :loading="dangDung" @click="dungTaoBanNhap">Dừng tạo bản nháp</CustomButton>
            </div>
            <progress v-if="coTienDoDem" :value="tienDo.da_xu_ly" :max="tienDo.tong" aria-label="Tiến độ bước hiện tại" />
            <progress v-else aria-label="Đang xử lý bước hiện tại" />
          </div>
          <p v-else-if="dangKiemTraBanNhap" class="chu-thich" role="status">Đang kiểm tra trạng thái phiên với máy chủ…</p>
          <p v-else-if="dangTimNguon" class="chu-thich" role="status">Đang tìm nguồn web theo từng nhóm thông tin tuyển sinh…</p>
          <el-alert v-if="thongBaoDung" :title="thongBaoDung" type="info" show-icon :closable="false" class="canh-bao" />
          <el-alert v-if="loiHienThi" :title="loiHienThi.noiDung" type="error" show-icon :closable="false" class="canh-bao">
            <p v-if="loiHienThi.xayRaLuc" class="noi-dung-bao">Lần tạo bản nháp gần nhất · {{ ngayGio(loiHienThi.xayRaLuc) }}</p>
            <ul v-if="loiHienThi.loi.length" class="danh-sach-bao">
              <li v-for="(loi, viTri) in loiHienThi.loi" :key="viTri">{{ loi }}</li>
            </ul>
            <div v-if="nguonLoi.length" class="nguon__nut">
              <CustomButton v-for="nguon in nguonLoi" :key="nguon.id" link type="primary" @click="moNguonLoi(nguon.id)">
                Xem nguồn #{{ nguon.id }}
              </CustomButton>
            </div>
          </el-alert>
          <el-alert v-if="Object.keys(nguonBiBoQua).length" title="Đã lưu bản nháp. Một số nguồn đã được bỏ qua." type="warning" show-icon :closable="false" class="canh-bao">
            <ul class="danh-sach-bao">
              <li v-for="(lyDo, nguonId) in nguonBiBoQua" :key="nguonId">{{ lyDo }}</li>
            </ul>
          </el-alert>
          <el-alert v-if="chiTiet.canh_bao_nguon.length" title="Nguồn cần kiểm tra" type="warning" show-icon :closable="false" class="canh-bao">
            <ul class="danh-sach-bao">
              <li v-for="(canhBao, viTri) in chiTiet.canh_bao_nguon" :key="viTri">{{ canhBao }}</li>
            </ul>
          </el-alert>
          <CustomForm v-if="choPhepSuaNguon" :model="nguonMoi" class="form-grid them-nguon" @submit.prevent="themNguon">
            <div class="form-grid__body">
              <CustomFormItem class="form-grid__span-2" label="URL tài liệu chính thức">
                <CustomInput v-model="nguonMoi.url" placeholder="Nhập URL trang web hoặc PDF của trường" maxlength="2000" :disabled="khoaNguon" />
              </CustomFormItem>
            </div>
            <CustomButton type="primary" plain native-type="submit" :disabled="khoaNguon || !nguonMoi.url.trim()" :loading="thaoTac === 'them'">
              <CustomIcon><Plus /></CustomIcon> Bổ sung URL
            </CustomButton>
          </CustomForm>

          <CustomEmpty v-if="!chiTiet.nguon.length && !khoaNguon" description="Chưa có tài liệu. Hãy tìm nguồn hoặc bổ sung URL chính thức." />
          <ul v-else-if="chiTiet.nguon.length" class="nguon-list">
            <li v-for="nguon in chiTiet.nguon" :id="`nguon-tuyen-sinh-${nguon.id}`" :key="nguon.id" class="nguon" tabindex="-1">
              <div class="nguon__dau">
                <h3>{{ nguon.tieu_de || nguon.url }}</h3>
                <CustomTag :type="nguon.lua_chon === 'su_dung' ? 'success' : 'info'">
                  {{ nhanLuaChon[nguon.lua_chon] || 'Chưa chọn' }}
                </CustomTag>
                <CustomTag v-if="loiHienThi?.nguonIds?.includes(nguon.id)" type="danger">Nguồn #{{ nguon.id }} · Cần kiểm tra</CustomTag>
                <CustomTag v-if="!nguon.chinh_thuc || !nguon.phu_hop" type="warning">{{ nguon.chinh_thuc ? 'Chưa phù hợp' : 'Chưa xác minh nguồn chính thức' }}</CustomTag>
              </div>
              <dl class="nguon__thong-tin">
                <div><dt>Cơ quan</dt><dd>{{ nguon.co_quan || '—' }}</dd></div>
                <div><dt>Loại</dt><dd>{{ nhanLoaiNguon[nguon.loai] || nguon.loai || '—' }}</dd></div>
                <div><dt>Năm áp dụng</dt><dd>{{ nguon.nam_ap_dung || '—' }}</dd></div>
                <div><dt>Ngày công bố</dt><dd>{{ ngayVanBan(nguon.ngay_cong_bo) }}</dd></div>
                <div><dt>Truy cập</dt><dd>{{ ngayGio(nguon.truy_cap_luc) }}</dd></div>
                <div v-if="nguon.ngay_hieu_luc"><dt>Ngày hiệu lực</dt><dd>{{ ngayVanBan(nguon.ngay_hieu_luc) }}</dd></div>
              </dl>
              <dl v-if="nguon.thay_the_url || nguon.pham_vi_dieu_chinh" class="nguon__thong-tin nguon__thong-tin--dieu-chinh">
                <div v-if="nguon.thay_the_url">
                  <dt>Tài liệu được thay thế</dt>
                  <dd><a v-if="urlTaiLieu(nguon.thay_the_url)" class="cell-link" :href="urlTaiLieu(nguon.thay_the_url)" target="_blank" rel="noopener noreferrer">{{ nguon.thay_the_url }}</a><span v-else>{{ nguon.thay_the_url }}</span></dd>
                </div>
                <div v-if="nguon.pham_vi_dieu_chinh"><dt>Phạm vi điều chỉnh</dt><dd>{{ nguon.pham_vi_dieu_chinh }}</dd></div>
              </dl>
              <p v-if="nguon.ly_do" class="chu-thich">{{ nguon.ly_do }}</p>
              <p v-if="nguon.ly_do_loai" class="chu-thich">Lý do loại nguồn · {{ nguon.ly_do_loai }}</p>
              <p class="nguon__url">{{ nguon.url }}</p>
              <div class="nguon__nut">
                <a v-if="urlTaiLieu(nguon.url)" class="cell-link" :href="urlTaiLieu(nguon.url)" target="_blank" rel="noopener noreferrer">Mở tài liệu</a>
                <a v-if="urlTaiLieu(nguon.url_trang_cong_bo) && nguon.url_trang_cong_bo !== nguon.url" class="cell-link" :href="urlTaiLieu(nguon.url_trang_cong_bo)" target="_blank" rel="noopener noreferrer">Mở trang công bố</a>
                <template v-if="choPhepSuaNguon">
                  <CustomButton v-if="nguon.lua_chon !== 'su_dung'" type="primary" plain :disabled="khoaNguon || !nguonHopLe(nguon)" :loading="thaoTac === `su_dung-${nguon.id}`" @click="chonNguon(nguon, 'su_dung')">Dùng nguồn</CustomButton>
                  <CustomButton v-if="nguon.lua_chon !== 'loai'" :disabled="khoaNguon" :loading="thaoTac === `loai-${nguon.id}`" @click="moLoaiNguon(nguon)">Loại nguồn</CustomButton>
                  <CustomButton v-if="nguon.lua_chon !== 'chua_chon'" link :disabled="khoaNguon" :loading="thaoTac === `chua_chon-${nguon.id}`" @click="chonNguon(nguon, 'chua_chon')">Bỏ lựa chọn</CustomButton>
                </template>
              </div>
            </li>
          </ul>
        </CustomCard>
      </template>
    </template>

    <CustomDialog v-model="loaiNguon.hien" title="Loại nguồn" width="560px" :close-on-click-modal="false">
      <p>{{ loaiNguon.nguon?.tieu_de || loaiNguon.nguon?.url }}</p>
      <CustomForm class="form-grid" :model="loaiNguon" @submit.prevent="xacNhanLoaiNguon">
        <div class="form-grid__body">
          <CustomFormItem class="form-grid__full" label="Lý do loại nguồn">
            <CustomInput v-model="loaiNguon.lyDo" type="textarea" placeholder="Nhập lý do loại nguồn (không bắt buộc)" maxlength="1000" show-word-limit />
          </CustomFormItem>
        </div>
      </CustomForm>
      <template #footer>
        <CustomButton @click="loaiNguon.hien = false">Hủy</CustomButton>
        <CustomButton type="danger" :disabled="khoaNguon" @click="xacNhanLoaiNguon">Loại nguồn</CustomButton>
      </template>
    </CustomDialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref, shallowReactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  chonNguonTuyenSinh,
  chonTatCaNguonTuyenSinh,
  dungTaoBanNhapTuyenSinh,
  nhanDienTruong,
  taoBanNhapTuyenSinh,
  taoPhienTuyenSinh,
  themNguonTuyenSinh,
  timNguonTuyenSinh,
} from '@/api/thuThapTuyenSinh'
import DanhSachPhienTuyenSinh from './DanhSachPhienTuyenSinh.vue'
import { TRANG_THU_THAP, TRANG_XET_DUYET, chiTietLoiPhien, loiPhien, loiTaoBanNhapDaLuu, ngayGio, ngayVanBan, nguonBiBoQuaKhiTaoBanNhap, trangThaiThuThap, urlTaiLieu } from './thu-thap-du-lieu'
import { usePhienTuyenSinh } from './usePhienTuyenSinh'

const router = useRouter()
const phienChoKhoiDong = shallowReactive(new Map())
const phienDangTao = computed(() => new Set(phienChoKhoiDong.keys()))
const { id, chiTiet, dangTai, loiTai, dangTaoBanNhap, dangKiemTraBanNhap, tai, kiemTraLaiBanNhap, apDung } = usePhienTuyenSinh(false, (phienId) => phienChoKhoiDong.has(phienId))
const form = reactive({ ma_truong: '', nam_tuyen_sinh: new Date().getFullYear() })
const truong = ref(null)
const dangNhanDien = ref(false)
const loiNhanDien = ref('')
const loiTao = ref('')
const dangTao = ref(false)
const thaoTac = ref('')
const loiThaoTac = ref(null)
const dangDung = ref(false)
const thongBaoDung = ref('')
const banChoMo = ref(null)
const bayGio = ref(Date.now())
const nguonMoi = reactive({ url: '' })
const loaiNguon = reactive({ hien: false, nguon: null, lyDo: '' })
let lanMoPhien = 0

const nhanLuaChon = { su_dung: 'Đã chọn dùng', loai: 'Đã loại', chua_chon: 'Chưa chọn' }
const nhanLoaiNguon = {
  de_an: 'Đề án', phu_luc: 'Phụ lục', dieu_chinh: 'Điều chỉnh', thong_bao: 'Thông báo',
  diem_lich_su: 'Điểm chuẩn lịch sử', khac: 'Khác',
}
const nhanBuoc = {
  tim_nguon: 'Đang tìm nguồn tuyển sinh',
  tim_bo_sung: 'Đang tìm nguồn cho các mục còn thiếu',
  ra_soat_do_phu: 'AI đang rà soát dữ liệu và đề xuất nguồn cần tìm thêm',
  doc_nguon: 'Đang đọc nguồn đã chọn',
  doc_lai_nguon: 'Đang đọc lại nguồn cho các mục còn thiếu',
  doc_bo_sung: 'Đang đọc phụ lục và bảng ảnh',
  lap_ma_tran: 'Đang đối chiếu danh mục chương trình, diện và tổ hợp',
  kiem_ke_cong_thuc: 'Đang kiểm kê công thức trong nguồn',
  chieu_cong_thuc: 'Đang đối chiếu công thức với trường dữ liệu trong bản nháp',
  doi_chieu_cong_thuc: 'Đang đối chiếu dẫn chứng của từng công thức',
  doi_chieu_lien_ket: 'Đang đối chiếu phương thức và công thức theo mã xét tuyển',
  phan_tich_mau_thuan: 'AI đang đọc các nguồn có số liệu khác nhau',
  xac_minh_nguon: 'Đang xác minh nguồn',
  trich_xuat: 'Đang trích xuất dữ liệu tuyển sinh',
  luu_ban_nhap: 'Đang lưu bản nháp',
}

const maTruong = computed(() => form.ma_truong.trim().toUpperCase())
const choPhepSuaNguon = computed(() => ['thu_thap', 'yeu_cau_bo_sung'].includes(chiTiet.value?.trang_thai))
const khoaNguon = computed(() => Boolean(thaoTac.value || dangTaoBanNhap.value || dangKiemTraBanNhap.value || dangDung.value))
const dangTimNguon = computed(() => thaoTac.value === 'tim')
const trangThaiHienThi = computed(() => {
  if (!dangTaoBanNhap.value) {
    if (dangKiemTraBanNhap.value) return { nhan: 'Đang kiểm tra bản nháp', loai: 'warning' }
    if (dangTimNguon.value) return { nhan: 'Đang tìm nguồn', loai: 'warning' }
  }
  return trangThaiThuThap(chiTiet.value, dangTaoBanNhap.value)
})
const chiTietLoiTao = computed(() => dangTaoBanNhap.value || dangKiemTraBanNhap.value ? null : loiTaoBanNhapDaLuu(chiTiet.value))
const loiHienThi = computed(() => {
  const trucTiep = loiThaoTac.value
  const daLuu = chiTietLoiTao.value
  if (!daLuu) return trucTiep
  const thayThePhanHoi = trucTiep?.thaoTac === 'tao-ban-nhap'
    && (trucTiep.noiDung === daLuu.message || !trucTiep.trangThai || trucTiep.dangTaoBanNhap)
  if (trucTiep && !thayThePhanHoi) return trucTiep
  return { ...chiTietLoiPhien(daLuu), xayRaLuc: daLuu.xay_ra_luc }
})
const tienDo = computed(() => chiTiet.value?.tien_do_tao_ban_nhap)
const coTienDoDem = computed(() => tienDo.value?.tong > 0 && Number.isInteger(tienDo.value?.da_xu_ly))
const nhanTienDo = computed(() => {
  if (dangDung.value) return 'Đang dừng tạo bản nháp…'
  const nhan = nhanBuoc[tienDo.value?.buoc] || 'Đang chuẩn bị tạo bản nháp'
  return coTienDoDem.value ? `${nhan} · ${tienDo.value.da_xu_ly}/${tienDo.value.tong}` : `${nhan}…`
})
const thoiGianDaChay = computed(() => {
  const batDau = Date.parse(chiTiet.value?.bat_dau_tao_ban_nhap_luc) || phienChoKhoiDong.get(id.value)?.batDau
  if (!batDau) return ''
  const giay = Math.max(0, Math.floor((bayGio.value - batDau) / 1000))
  return [Math.floor(giay / 3600), Math.floor(giay / 60) % 60, giay % 60]
    .map((giaTri) => String(giaTri).padStart(2, '0')).join(':')
})
const cacNguonDaChon = computed(() => chiTiet.value?.nguon.filter((nguon) => nguon.lua_chon === 'su_dung' && nguonHopLe(nguon)) || [])
const nguonDaChon = computed(() => cacNguonDaChon.value.length)
const coNguonDungNam = computed(() => cacNguonDaChon.value.some((nguon) => !nguon.chi_diem_lich_su && nguon.nam_ap_dung === chiTiet.value.nam_tuyen_sinh))
const coNguonChuaChon = computed(() => chiTiet.value?.nguon.some((nguon) => nguon.lua_chon === 'chua_chon' && nguonHopLe(nguon)))
const nguonLoi = computed(() => chiTiet.value?.nguon.filter((nguon) => loiHienThi.value?.nguonIds?.includes(nguon.id)) || [])
const nguonBiBoQua = computed(() => nguonBiBoQuaKhiTaoBanNhap(chiTiet.value))

function nguonHopLe(nguon) {
  return nguon.chinh_thuc && nguon.phu_hop && (nguon.nam_ap_dung === chiTiet.value.nam_tuyen_sinh || nguon.chi_diem_lich_su)
}

watch(maTruong, (ma, _, onCleanup) => {
  truong.value = null
  loiNhanDien.value = ''
  loiTao.value = ''
  dangNhanDien.value = Boolean(ma)
  if (!ma) return
  let conHieuLuc = true
  const henGio = setTimeout(async () => {
    try {
      const ketQua = await nhanDienTruong(ma)
      if (conHieuLuc) truong.value = ketQua
    } catch (error) {
      if (conHieuLuc) loiNhanDien.value = loiPhien(error).noiDung
    } finally {
      if (conHieuLuc) dangNhanDien.value = false
    }
  }, 300)
  onCleanup(() => {
    conHieuLuc = false
    clearTimeout(henGio)
  })
})

watch(id, () => {
  lanMoPhien += 1
  thaoTac.value = ''
  loiThaoTac.value = null
  dangDung.value = false
  thongBaoDung.value = ''
  banChoMo.value = null
  nguonMoi.url = ''
  loaiNguon.hien = false
})

watch(() => dangTaoBanNhap.value || dangDung.value, (dangXuLy, _, onCleanup) => {
  if (!dangXuLy) return
  const capNhatDongHo = () => { bayGio.value = Date.now() }
  capNhatDongHo()
  const henGio = setInterval(capNhatDongHo, 1000)
  onCleanup(() => clearInterval(henGio))
})

watch(chiTiet, async (phien) => {
  const choMo = banChoMo.value
  if (!choMo || phien?.id !== id.value || router.currentRoute.value.name !== TRANG_THU_THAP) return
  if (phien.dang_tao_ban_nhap) {
    if (phien.luot_tao_ban_nhap > choMo.luot) banChoMo.value = null
    return
  }
  banChoMo.value = null
  if (phien.trang_thai === 'cho_duyet' && phien.phien_ban > choMo.phienBanTruoc) {
    await router.push({ name: TRANG_XET_DUYET, query: { phien: phien.id } })
  }
})

onBeforeUnmount(() => { lanMoPhien += 1 })

function theoDoiPhienHienTai() {
  const phienId = id.value
  const lucMo = lanMoPhien
  return () => phienId === id.value && lucMo === lanMoPhien && router.currentRoute.value.name === TRANG_THU_THAP
}

async function batDau(tuDong) {
  if (!truong.value || !form.nam_tuyen_sinh || dangTao.value) return
  dangTao.value = true
  loiTao.value = ''
  try {
    const phien = await taoPhienTuyenSinh({ ma_truong: truong.value.ma_truong, nam_tuyen_sinh: form.nam_tuyen_sinh }, tuDong)
    await router.push({ name: TRANG_THU_THAP, query: { phien: phien.id } })
    if (!apDung(phien)) return
    if (tuDong) {
      banChoMo.value = { luot: phien.luot_tao_ban_nhap, phienBanTruoc: 0 }
    } else {
      await timNguon()
    }
  } catch (error) {
    loiTao.value = loiPhien(error).noiDung
  } finally {
    dangTao.value = false
  }
}

function timNguon() {
  return thucHien('tim', () => timNguonTuyenSinh(id.value))
}

async function thucHien(ten, gui) {
  if (!choPhepSuaNguon.value || khoaNguon.value) return false
  const conMoPhien = theoDoiPhienHienTai()
  thaoTac.value = ten
  loiThaoTac.value = null
  thongBaoDung.value = ''
  try {
    const ketQua = await gui()
    return conMoPhien() && apDung(ketQua)
  } catch (error) {
    if (conMoPhien()) {
      const loi = loiPhien(error)
      loiThaoTac.value = { ...loi, thaoTac: ten }
      if (loi.trangThai === 409) await kiemTraLaiBanNhap(loi.dangTaoBanNhap)
    }
    return false
  } finally {
    if (conMoPhien()) thaoTac.value = ''
  }
}

async function themNguon() {
  if (khoaNguon.value) return
  if (!urlTaiLieu(nguonMoi.url.trim())) {
    loiThaoTac.value = { noiDung: 'Nhập URL http hoặc https của tài liệu.', loi: [] }
    return
  }
  if (await thucHien('them', () => themNguonTuyenSinh(id.value, nguonMoi.url.trim()))) nguonMoi.url = ''
}

function chonNguon(nguon, luaChon, lyDo) {
  return thucHien(`${luaChon}-${nguon.id}`, () => chonNguonTuyenSinh(id.value, nguon.id, luaChon, lyDo))
}

function moNguonLoi(nguonId) {
  const theNguon = document.getElementById(`nguon-tuyen-sinh-${nguonId}`)
  theNguon?.focus({ preventScroll: true })
  theNguon?.scrollIntoView({ block: 'nearest' })
}

function moLoaiNguon(nguon) {
  loaiNguon.nguon = nguon
  loaiNguon.lyDo = nguon.ly_do_loai || ''
  loaiNguon.hien = true
}

function xacNhanLoaiNguon() {
  if (khoaNguon.value) return
  loaiNguon.hien = false
  chonNguon(loaiNguon.nguon, 'loai', loaiNguon.lyDo.trim() || undefined)
}

async function taoBanNhap(tuDong) {
  if (!choPhepSuaNguon.value || khoaNguon.value || (!tuDong && !coNguonDungNam.value)) return
  const phienId = id.value
  const lanKhoiDong = { batDau: Date.now() }
  const conMoPhien = theoDoiPhienHienTai()
  const conKhoiDong = () => phienChoKhoiDong.get(phienId) === lanKhoiDong
  const phienBanTruoc = chiTiet.value.phien_ban ?? 0
  phienChoKhoiDong.set(phienId, lanKhoiDong)
  loiThaoTac.value = null
  thongBaoDung.value = ''
  try {
    const phien = await taoBanNhapTuyenSinh(phienId, tuDong)
    if (conMoPhien() && conKhoiDong() && !dangDung.value) {
      banChoMo.value = { luot: phien.luot_tao_ban_nhap, phienBanTruoc }
      await kiemTraLaiBanNhap()
    }
  } catch (error) {
    if (!conMoPhien() || !conKhoiDong() || dangDung.value) return
    const loi = loiPhien(error)
    if (loi.dangTaoBanNhap) {
      banChoMo.value = null
      await kiemTraLaiBanNhap(true)
      return
    }
    if (!loi.trangThai || loi.trangThai >= 500) {
      const phien = await kiemTraLaiBanNhap()
      if (!conMoPhien() || !conKhoiDong() || !phien || phien.dang_tao_ban_nhap || phien.trang_thai === 'cho_duyet') return
      if (!loi.trangThai) loi.noiDung = 'Mất kết nối trước khi nhận phản hồi tạo bản nháp.'
    }
    banChoMo.value = null
    loiThaoTac.value = { ...loi, thaoTac: 'tao-ban-nhap' }
  } finally {
    if (conKhoiDong()) phienChoKhoiDong.delete(phienId)
  }
}

async function dungTaoBanNhap() {
  const luot = chiTiet.value?.luot_tao_ban_nhap
  if (!luot || dangDung.value) return
  const phienId = id.value
  const lanKhoiDong = phienChoKhoiDong.get(phienId)
  const conMoPhien = theoDoiPhienHienTai()
  const banDangTao = banChoMo.value
  dangDung.value = true
  banChoMo.value = null
  loiThaoTac.value = null
  try {
    const phien = await dungTaoBanNhapTuyenSinh(phienId, luot)
    if (phienChoKhoiDong.get(phienId) === lanKhoiDong) phienChoKhoiDong.delete(phienId)
    if (conMoPhien() && apDung(phien)) {
      thongBaoDung.value = phien.trang_thai === 'cho_duyet'
        ? 'Bản nháp đã được lưu trước khi yêu cầu dừng.'
        : 'Đã dừng tạo bản nháp.'
    }
  } catch (error) {
    if (!conMoPhien()) return
    const loi = loiPhien(error)
    loiThaoTac.value = { ...loi, thaoTac: 'dung-tao-ban-nhap' }
    if (loi.trangThai === 409 || !loi.trangThai || loi.trangThai >= 500) {
      const phien = await kiemTraLaiBanNhap(loi.dangTaoBanNhap)
      if (conMoPhien() && phien?.luot_tao_ban_nhap === luot) banChoMo.value = banDangTao
    }
  } finally {
    if (conMoPhien()) dangDung.value = false
  }
}
</script>

<style scoped>
.dieu-huong, .nguon__nut, .nguon__dau { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.dieu-huong { justify-content: space-between; }
.nhan-dien { display: flex; flex-direction: column; margin: 0 0 14px; gap: 4px; }
.nhan-dien span, .chu-thich { color: var(--el-text-color-secondary); }
.chu-thich { margin: 0 0 10px; }
.chu-thich--loi { color: var(--el-color-danger); }
.tim-nguon { margin: 0 0 12px; }
.tien-do-nhap { display: grid; gap: 10px; margin: 12px 0; padding: 12px 14px; border: 1px solid var(--el-border-color-light); border-radius: 8px; }
.tien-do-nhap__dau { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; }
.tien-do-nhap__nhan { font-weight: 600; margin: 0; }
.tien-do-nhap__dong-ho { color: var(--el-text-color-secondary); font-variant-numeric: tabular-nums; margin: 4px 0 0; }
.tien-do-nhap progress { width: 100%; height: 10px; accent-color: var(--el-color-primary); }
.canh-bao { margin-top: 12px; }
.noi-dung-bao { margin: 4px 0; }
.danh-sach-bao { margin: 4px 0; padding-inline-start: 20px; overflow-wrap: anywhere; }
.thong-tin-phien, .nguon__thong-tin { display: flex; flex-wrap: wrap; gap: 8px 30px; margin: 0; }
dt { font-size: 12px; color: var(--el-text-color-secondary); }
dd { margin: 0; }
.them-nguon { margin: 16px 0; }
.nguon-list { display: grid; gap: 12px; list-style: none; margin: 16px 0 0; padding: 0; }
.nguon { border: 1px solid var(--el-border-color-light); border-radius: 8px; padding: 14px; min-width: 0; }
.nguon h3 { font-size: 15px; font-weight: 600; margin: 0; overflow-wrap: anywhere; }
.nguon__thong-tin { margin: 12px 0; }
.nguon__thong-tin--dieu-chinh { display: grid; gap: 8px; overflow-wrap: anywhere; }
.nguon__url { margin: 6px 0 10px; color: var(--el-text-color-secondary); font-size: 12px; overflow-wrap: anywhere; }
.nguon__nut :deep(.el-button + .el-button), .toolbar__actions :deep(.el-button + .el-button) { margin-left: 0; }
@media (max-width: 767px) {
  .toolbar { flex-wrap: wrap; }
}
</style>
