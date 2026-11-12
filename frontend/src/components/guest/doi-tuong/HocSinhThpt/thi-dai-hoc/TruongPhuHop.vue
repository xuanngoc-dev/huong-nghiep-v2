<template>
  <section class="truong-phu-hop py-4">
    <div class="container-fluid">

      <div class="stages-card holland-overview mt-3">
        <header class="holland-overview__header truong-phu-hop__header">
          <h2 class="holland-overview__title">Trường phù hợp</h2>
          <CustomButton link type="primary" @click="quayLai">Quay lại</CustomButton>
        </header>

        <article class="truong-phu-hop__hero">
          <div class="truong-phu-hop__info">
            <img
              class="truong-phu-hop__image"
              :src="anhNganh"
              :alt="`Hình minh họa ngành ${tenNganh}`"
              @error="anhNganhHong = true"
            />
            <div class="truong-phu-hop__intro">
              <p class="truong-phu-hop__kicker">Trường có đào tạo ngành</p>
              <p v-if="maNganh" class="truong-phu-hop__code">{{ maNganh }}</p>
              <h3 class="truong-phu-hop__name">{{ tenNganh }}</h3>
              <p v-if="nganh?.ten_tieng_anh" class="truong-phu-hop__en">{{ nganh.ten_tieng_anh }}</p>
              <p v-if="nganh?.mo_ta" class="truong-phu-hop__text">{{ nganh.mo_ta }}</p>
              <dl v-if="tomTatNganh.length" class="truong-phu-hop__facts">
                <div v-for="item in tomTatNganh" :key="item.nhan" class="truong-phu-hop__fact">
                  <dt>{{ item.nhan }}</dt>
                  <dd>{{ item.giaTri }}</dd>
                </div>
              </dl>
              <p class="truong-phu-hop__note">{{ moTaHoSo }}</p>
            </div>
          </div>
        </article>

        <article v-if="daDangNhap && hoSo" class="ho-so-tom-tat">
          <header class="ho-so-tom-tat__head">
            <div>
              <h3 class="ho-so-tom-tat__title">Thông tin của bạn</h3>
              <p class="ho-so-tom-tat__sub">
                {{ hoSo.ho_ten }}
                <span v-if="soMucThieu"> · còn {{ soMucThieu }} mục chưa cập nhật</span>
              </p>
            </div>
            <div class="ho-so-tom-tat__actions">
              <span class="luot-tim" :class="{ 'luot-tim--het': !conLuot }">{{ nhanLuot }}</span>
              <CustomButton type="primary" plain @click="hoSoMo = true">
                <CustomIcon><User /></CustomIcon>
                <span>Xem & cập nhật hồ sơ</span>
              </CustomButton>
            </div>
          </header>
          <ul class="ho-so-tom-tat__list">
            <li
              v-for="item in thongTinHoSo"
              :key="item.id"
              class="ho-so-chip"
              :class="{ 'ho-so-chip--trong': !item.giaTri }"
            >
              <CustomIcon class="ho-so-chip__icon"><component :is="item.icon" /></CustomIcon>
              <div class="ho-so-chip__body">
                <span class="ho-so-chip__label">{{ item.nhan }}</span>
                <CustomTooltip :content="item.goiY" placement="top" :disabled="!item.goiY">
                  <span class="ho-so-chip__value">{{ item.giaTri || 'Chưa cập nhật' }}</span>
                </CustomTooltip>
              </div>
            </li>
          </ul>
        </article>

        <article v-else-if="!daDangNhap" class="ho-so-tom-tat ho-so-tom-tat--khach">
          <header class="ho-so-tom-tat__head">
            <div>
              <h3 class="ho-so-tom-tat__title">Thông tin của bạn</h3>
              <p class="ho-so-tom-tat__sub">Nhập vài thông tin cơ bản để dùng thử tính năng tìm trường phù hợp.</p>
            </div>
            <span class="luot-tim" :class="{ 'luot-tim--het': !conLuot }">{{ nhanLuot }}</span>
          </header>
          <form class="ho-so-khach" @submit.prevent="timTheoHoSoKhach">
            <div class="ho-so-khach__field">
              <label class="nhom-filter__label" for="khach-tinh">Nơi ở</label>
              <CustomSelect
                id="khach-tinh"
                v-model="hoSoKhach.tinhId"
                filterable
                clearable
                placeholder="Chọn tỉnh/thành"
                :disabled="!conLuot"
              >
                <CustomOption v-for="item in tinhOptions" :key="item.id" :label="item.ten_tinh" :value="item.id" />
              </CustomSelect>
            </div>
            <div class="ho-so-khach__field">
              <label class="nhom-filter__label" for="khach-to-hop">Tổ hợp xét tuyển</label>
              <CustomSelect
                id="khach-to-hop"
                v-model="hoSoKhach.toHop"
                filterable
                clearable
                placeholder="Chọn tổ hợp"
                :disabled="!conLuot"
              >
                <CustomOption
                  v-for="item in toHopOptions"
                  :key="item.id"
                  :label="`${item.ma_to_hop} · ${item.ten_to_hop}`"
                  :value="item.ma_to_hop"
                />
              </CustomSelect>
            </div>
            <div class="ho-so-khach__field ho-so-khach__field--diem">
              <label class="nhom-filter__label" for="khach-diem">Điểm dự kiến</label>
              <CustomInputNumber
                id="khach-diem"
                v-model="hoSoKhach.diem"
                :min="0"
                :max="30"
                :step="0.25"
                :precision="2"
                controls-position="right"
                placeholder="Thang 30"
                :disabled="!conLuot"
              />
            </div>
            <div class="ho-so-khach__submit">
              <CustomButton type="primary" native-type="submit" :disabled="!conLuot">Tìm trường phù hợp</CustomButton>
            </div>
          </form>
          <div class="ho-so-khach__cta">
            <p>
              Đăng ký tài khoản để được tìm <strong>{{ SO_LUOT_THANH_VIEN }} lượt mỗi ngày</strong> và lưu hồ sơ đầy đủ:
              học lực, điểm thi thử từng môn, ưu tiên tuyển sinh, chứng chỉ và bài thi đánh giá năng lực.
            </p>
            <div class="truong-phu-hop__links">
              <CustomButton type="primary" @click="diDangKy">Đăng ký</CustomButton>
              <CustomButton @click="diDangNhap">Đăng nhập</CustomButton>
            </div>
          </div>
        </article>

        <div class="loai-co-so" role="group" aria-label="Loại cơ sở đào tạo">
          <button
            type="button"
            class="loai-co-so__chip"
            :class="{ 'is-active': !boLoc.loai }"
            :aria-pressed="!boLoc.loai"
            :disabled="!conLuot"
            @click="chonLoai('')"
          >
            Tất cả
          </button>
          <button
            v-for="item in LOAI_CO_SO"
            :key="item"
            type="button"
            class="loai-co-so__chip"
            :class="{ 'is-active': boLoc.loai === item }"
            :aria-pressed="boLoc.loai === item"
            :disabled="!conLuot"
            @click="chonLoai(item)"
          >
            {{ item }}
          </button>
        </div>

        <form class="nhom-filter" @submit.prevent="timCoLuot">
          <div class="nhom-filter__field nhom-filter__field--ten">
            <label class="nhom-filter__label" for="phu-hop-tu-khoa">Từ khóa</label>
            <CustomInput id="phu-hop-tu-khoa" v-model="tuKhoa" placeholder="Tên hoặc mã trường" clearable />
          </div>
          <div class="nhom-filter__field nhom-filter__field--khu-vuc">
            <label class="nhom-filter__label" for="phu-hop-khu-vuc">Khu vực</label>
            <CustomSelect id="phu-hop-khu-vuc" v-model="khuVuc" class="nhom-filter__select" clearable placeholder="Tất cả khu vực">
              <CustomOption v-for="item in KHU_VUC" :key="item" :label="item" :value="item" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--tinh">
            <label class="nhom-filter__label" for="phu-hop-tinh">Tỉnh/thành</label>
            <CustomSelect id="phu-hop-tinh" v-model="tinh" class="nhom-filter__select" filterable clearable placeholder="Tất cả tỉnh/thành">
              <CustomOption v-for="item in tinhOptions" :key="item.id" :label="item.ten_tinh" :value="item.ten_tinh" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--nam">
            <label class="nhom-filter__label" for="phu-hop-nam">Năm học</label>
            <CustomSelect id="phu-hop-nam" v-model="namHoc" class="nhom-filter__select" placeholder="Năm học">
              <CustomOption v-for="nam in namOptions" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__field nhom-filter__field--sap-xep">
            <label class="nhom-filter__label" for="phu-hop-sap-xep">Sắp xếp</label>
            <CustomSelect id="phu-hop-sap-xep" v-model="sapXep" class="nhom-filter__select" :disabled="!conLuot" @change="timCoLuot">
              <CustomOption v-for="item in sapXepOptions" :key="item.value" :label="item.label" :value="item.value" />
            </CustomSelect>
          </div>
          <div class="nhom-filter__actions">
            <CustomButton type="primary" native-type="submit" :disabled="!conLuot">Tìm kiếm</CustomButton>
            <CustomButton v-if="dangLocTheoHoSo" native-type="button" :disabled="!conLuot" @click="boLocHoSo">
              Bỏ lọc hồ sơ
            </CustomButton>
            <CustomButton v-else-if="tinhHoSo" native-type="button" :disabled="!conLuot" @click="locTheoHoSo">
              Lọc theo hồ sơ
            </CustomButton>
          </div>
        </form>

        <p v-if="!conLuot" class="luot-tim__het-note">
          <template v-if="daDangNhap">
            Bạn đã dùng hết {{ SO_LUOT_THANH_VIEN }} lượt tìm trường phù hợp hôm nay. Hãy quay lại vào ngày mai.
          </template>
          <template v-else>
            Bạn đã dùng lượt tìm thử.
            <button type="button" class="luot-tim__link" @click="diDangKy">Đăng ký</button> hoặc
            <button type="button" class="luot-tim__link" @click="diDangNhap">đăng nhập</button>
            để được tìm {{ SO_LUOT_THANH_VIEN }} lượt mỗi ngày.
          </template>
        </p>
        <p v-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
        <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải trường phù hợp…</p>
        <KhongCoDuLieu v-else-if="!danhSach.length" :text="thongBaoTrong" />
        <div v-else class="row g-3">
          <div v-for="item in danhSach" :key="item.ma_truong" class="col-12 col-md-6 col-lg-3">
            <article class="nhom-card h-100">
              <p class="nhom-card__code">{{ item.ma_truong }}</p>
              <div class="nhom-card__main">
                <p class="nhom-card__field">{{ item.loai_co_so || 'Cơ sở đào tạo' }}</p>
                <h3 class="nhom-card__name">{{ item.ten_truong }}</h3>
                <p v-if="item.ten_tieng_anh" class="nhom-card__en">{{ item.ten_tieng_anh }}</p>
                <p v-if="diaDiem(item)" class="nhom-card__meta">{{ diaDiem(item) }}</p>
                <p v-if="item.dia_chi_tru_so" class="nhom-card__meta">{{ item.dia_chi_tru_so }}</p>
                <p v-if="item.so_chuong_trinh || chiTieu(item.chi_tieu)" class="nhom-card__meta">
                  <span v-if="item.so_chuong_trinh">{{ item.so_chuong_trinh }} chương trình</span>
                  <span v-if="item.so_chuong_trinh && chiTieu(item.chi_tieu)"> · </span>
                  <span v-if="chiTieu(item.chi_tieu)">Chỉ tiêu {{ chiTieu(item.chi_tieu) }}</span>
                </p>
                <p v-if="hrefWebsite(item.website_tuyen_sinh || item.website)" class="nhom-card__addr">
                  <a
                    class="nhom-card__web"
                    :href="hrefWebsite(item.website_tuyen_sinh || item.website)"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {{ item.website_tuyen_sinh || item.website }}
                  </a>
                </p>
              </div>
            </article>
          </div>
        </div>
        <div v-if="!dangTai && !loi && total > soMoiTrang" class="nhom-pager">
          <CustomPagination
            v-model:current-page="trang"
            v-model:page-size="soMoiTrang"
            :total="total"
            :page-sizes="[12, 24, 48]"
            layout="total, sizes, prev, pager, next"
            background
          />
        </div>
      </div>
    </div>

    <el-drawer
      v-model="hoSoMo"
      title="Hồ sơ của tôi"
      direction="rtl"
      size="min(960px, 100%)"
      append-to-body
      destroy-on-close
      class="ho-so-drawer"
    >
      <HoSo embedded @saved="daLuuHoSo" />
    </el-drawer>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchTruongDaoTao } from '@/api/deAnTuyenSinh'
import { fetchDoiTuongUuTien } from '@/api/doiTuongUuTien'
import { fetchHoSo } from '@/api/hoSo'
import { fetchKhuVucUuTien } from '@/api/khuVucUuTien'
import { fetchMonHoc } from '@/api/monHoc'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchTinhThanh } from '@/api/tinhThanh'
import { fetchToHopMonHoc } from '@/api/toHopMonHoc'
import { danhSachNamHoc, nhanNamHoc } from '@/constants/namHoc'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import anhMacDinh from '@/assets/guest/sinh-vien.jpg'
import HoSo from '@/views/member/HoSo.vue'

defineOptions({ name: 'ThptThiDaiHocTruongPhuHop' })

const KHU_VUC = ['Bắc', 'Trung', 'Nam']
const LOAI_CO_SO = ['Đại học', 'Cao đẳng', 'Học viện']
const SAP_XEP = [
  { value: 'gan_toi', label: 'Gần nơi ở nhất', canHoSo: true },
  { value: 'ten_asc', label: 'Tên trường A → Z' },
  { value: 'ten_desc', label: 'Tên trường Z → A' },
  { value: 'chi_tieu_desc', label: 'Chỉ tiêu nhiều nhất' },
  { value: 'chuong_trinh_desc', label: 'Nhiều chương trình nhất' },
]
const NAM_HIEN_TAI = new Date().getFullYear()
// Lượt tìm trường phù hợp: thành viên N lượt mỗi ngày, khách 1 lượt dùng thử.
// Tạm đếm ở trình duyệt để lên giao diện, sẽ chuyển sang API khi có.
const SO_LUOT_THANH_VIEN = 5
const SO_LUOT_KHACH = 1
const KHOA_LUOT = 'thpt-tim-truong-phu-hop-luot'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const maNganh = computed(() => String(route.params.maNganh || '').trim())

const nganh = ref(null)
const hoSo = ref(null)
const tinhHoSo = ref(null)
const daDangNhap = ref(false)
const tinhOptions = ref([])
const danhMuc = ref({ monHoc: [], toHop: [], khuVucUuTien: [], doiTuongUuTien: [] })
const hoSoMo = ref(false)
const tuKhoa = ref('')
const khuVuc = ref('')
const namHoc = ref(NAM_HIEN_TAI)
const loai = ref('')
const tinh = ref('')
const sapXep = ref('ten_asc')
const boLoc = ref({
  tuKhoa: '',
  khuVuc: '',
  namHoc: NAM_HIEN_TAI,
  loai: '',
  tinh: '',
  sapXep: 'ten_asc',
})
const namOptions = danhSachNamHoc(NAM_HIEN_TAI)
const danhSach = ref([])
const total = ref(0)
const trang = ref(1)
const soMoiTrang = ref(12)
const dangTai = ref(false)
const loi = ref('')
const sanSang = ref(false)
const hoSoKhach = ref({ tinhId: null, toHop: '', diem: null })
const luotDaDung = ref(0)
let lanTai = 0

function homNay() {
  return new Date().toLocaleDateString('sv-SE')
}

function khoaLuot() {
  return daDangNhap.value ? `${KHOA_LUOT}:${auth.user?.id || 'tai-khoan'}` : `${KHOA_LUOT}:khach`
}

function docLuot() {
  try {
    const data = JSON.parse(localStorage.getItem(khoaLuot()) || 'null')
    // Lượt của thành viên tính theo ngày, của khách không bao giờ làm mới.
    if (!data || (daDangNhap.value && data.ngay !== homNay())) return 0
    return Number(data.da_dung) || 0
  } catch {
    return 0
  }
}

function ghiLuot(soLuot) {
  luotDaDung.value = soLuot
  try {
    localStorage.setItem(khoaLuot(), JSON.stringify({ ngay: homNay(), da_dung: soLuot }))
  } catch {
    // Trình duyệt chặn lưu trữ thì chỉ đếm trong phiên hiện tại.
  }
}

const tongLuot = computed(() => (daDangNhap.value ? SO_LUOT_THANH_VIEN : SO_LUOT_KHACH))
const luotConLai = computed(() => Math.max(tongLuot.value - luotDaDung.value, 0))
const conLuot = computed(() => luotConLai.value > 0)
const nhanLuot = computed(() => {
  if (daDangNhap.value) return `Hôm nay còn ${luotConLai.value}/${SO_LUOT_THANH_VIEN} lượt tìm`
  return conLuot.value ? 'Còn 1 lượt tìm thử' : 'Đã dùng lượt tìm thử'
})
const toHopOptions = computed(() =>
  danhMuc.value.toHop.filter((item) => item.trang_thai === 1 && item.ds_mon_hoc?.length === 3),
)

const tenNganh = computed(() => nganh.value?.ten_nganh || maNganh.value)
const anhNganhHong = ref(false)
const anhNganh = computed(() => {
  const url = String(nganh.value?.hinh_anh_mo_ta || '').trim()
  return url && !anhNganhHong.value ? url : anhMacDinh
})
const tomTatNganh = computed(() =>
  [
    { nhan: 'Nhóm ngành', giaTri: [nganh.value?.ma_nhom_nganh, nganh.value?.ten_nhom_nganh].filter(Boolean).join(' · ') },
    { nhan: 'Trình độ', giaTri: nganh.value?.trinh_do },
    { nhan: 'Thời gian đào tạo', giaTri: nganh.value?.thoi_gian_dao_tao },
  ].filter((item) => item.giaTri),
)
const sapXepOptions = computed(() => SAP_XEP.filter((item) => !item.canHoSo || tinhHoSo.value))

const moTaHoSo = computed(() => {
  if (!daDangNhap.value) {
    return 'Hiện danh sách gồm các trường có đào tạo ngành này. Nhập thông tin cơ bản bên dưới để dùng thử tìm trường phù hợp.'
  }
  if (tinhHoSo.value) {
    return 'Bộ lọc và thứ tự gợi ý dựa trên các thông tin chính trong hồ sơ của bạn.'
  }
  return 'Hồ sơ chưa có tỉnh thành. Cập nhật hồ sơ để lọc trường theo nơi bạn đang ở.'
})

const diemThiThu = computed(() => {
  const duKien = hoSo.value?.trinh_do_hoc_van?.diem_thi_thpt_quoc_gia?.du_kien || {}
  const diem = {}
  for (const [ma, value] of Object.entries(duKien)) {
    const so = Number(value)
    if (value !== null && value !== '' && Number.isFinite(so)) diem[ma] = so
  }
  return diem
})

// Tổ hợp có tổng điểm thi thử cao nhất (thang 30). Chỉ xét tổ hợp đúng 3 môn và đủ điểm cả 3:
// danh mục có vài tổ hợp đặc biệt lưu nhiều môn hơn (ví dụ K01 "1 trong 4 môn") nên cộng sẽ sai.
const toHopManh = computed(() => {
  const diem = diemThiThu.value
  if (!Object.keys(diem).length) return []
  return danhMuc.value.toHop
    .filter((item) => item.trang_thai === 1 && item.ds_mon_hoc?.length === 3)
    .filter((item) => item.ds_mon_hoc.every((ma) => ma in diem))
    .map((item) => ({
      ma: item.ma_to_hop,
      tong: Math.round(item.ds_mon_hoc.reduce((sum, ma) => sum + diem[ma], 0) * 100) / 100,
      mon: item.ds_mon_hoc,
    }))
    .sort((a, b) => b.tong - a.tong || a.ma.localeCompare(b.ma))
    .slice(0, 3)
})

const tenMon = computed(() => new Map(danhMuc.value.monHoc.map((item) => [item.ma_mon_hoc, item.ten_mon_hoc])))

const thongTinHoSo = computed(() => {
  if (!hoSo.value) return []
  const hocVan = hoSo.value.trinh_do_hoc_van || {}
  const khuVucUt = danhMuc.value.khuVucUuTien.find((item) => item.id === hoSo.value.khu_vuc_uu_tien_id)
  const doiTuongUt = danhMuc.value.doiTuongUuTien.find((item) => item.id === hoSo.value.doi_tuong_uu_tien_id)
  const hocLuc12 = hocVan.hoc_luc_trung_binh?.['12']
  const soMon = Object.keys(diemThiThu.value).length
  const toHop = toHopManh.value[0]
  const chungChi = [
    ...(hocVan.chung_chi_ngoai_ngu || []),
    ...(hocVan.bai_thi_danh_gia_nang_luc || []),
  ].length
  return [
    {
      id: 'noi-o',
      icon: 'Location',
      nhan: 'Nơi ở',
      giaTri: tinhHoSo.value
        ? [tinhHoSo.value.ten, tinhHoSo.value.khu_vuc && `miền ${tinhHoSo.value.khu_vuc}`].filter(Boolean).join(' · ')
        : '',
    },
    {
      id: 'diem-thi',
      icon: 'Medal',
      nhan: 'Điểm thi thử THPT',
      giaTri: toHop ? `${toHop.ma}: ${toHop.tong} điểm` : soMon ? `${soMon} môn đã nhập` : '',
      goiY: toHop ? `Tổ hợp cao nhất · ${toHop.mon.map((ma) => tenMon.value.get(ma) || ma).join(', ')}` : '',
    },
    {
      id: 'hoc-luc',
      icon: 'Reading',
      nhan: 'Học lực lớp 12',
      giaTri: hocLuc12 != null && hocLuc12 !== '' ? `${hocLuc12} điểm` : '',
    },
    {
      id: 'uu-tien',
      icon: 'Flag',
      nhan: 'Ưu tiên tuyển sinh',
      giaTri: [khuVucUt?.ma_khu_vuc, doiTuongUt?.ma_doi_tuong].filter(Boolean).join(' · '),
      goiY: [khuVucUt?.ten_khu_vuc, doiTuongUt?.ten_doi_tuong].filter(Boolean).join(' · '),
    },
    {
      id: 'chung-chi',
      icon: 'Tickets',
      nhan: 'Chứng chỉ, bài thi ĐGNL',
      giaTri: chungChi ? `${chungChi} mục` : '',
    },
  ]
})

const soMucThieu = computed(() => thongTinHoSo.value.filter((item) => !item.giaTri).length)

const dangLocTheoHoSo = computed(
  () => !!tinhHoSo.value && (boLoc.value.tinh === tinhHoSo.value.ten || boLoc.value.khuVuc === tinhHoSo.value.khu_vuc),
)

const thongBaoTrong = computed(() => {
  if (boLoc.value.tinh || boLoc.value.khuVuc || boLoc.value.tuKhoa || boLoc.value.loai) {
    return 'Không có trường đào tạo ngành này khớp bộ lọc.'
  }
  return 'Chưa có trường đào tạo cho ngành này.'
})

function hrefWebsite(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  if (/^https?:\/\//i.test(text)) return text
  return `https://${text}`
}

function diaDiem(item) {
  return [item.loai_co_so, item.vung_mien, item.ten_tinh_thanh].filter(Boolean).join(' · ')
}

function chiTieu(value) {
  if (value == null || value === '') return ''
  return Number(value).toLocaleString('vi-VN')
}

function quayLai() {
  router.push({
    name: 'thpt-thi-dai-hoc-chon-truong',
    params: { maNganh: maNganh.value },
  })
}

function diDangNhap() {
  router.push({ name: 'login', query: { redirect: route.fullPath } })
}

function diDangKy() {
  router.push({ name: 'register', query: { redirect: route.fullPath } })
}

async function taiNganh(ma) {
  nganh.value = null
  anhNganhHong.value = false
  if (!ma) return
  try {
    const data = await fetchNganh({ q: ma, trang_thai: 1, page: 1, page_size: 20 }, { skipLoading: true })
    nganh.value = (data.items || []).find((item) => String(item.ma_nganh).toUpperCase() === ma.toUpperCase()) || null
  } catch {
    nganh.value = null
  }
}

async function taiDanhMucHoSo() {
  const lay = (fetchFn) =>
    fetchFn({ page: 1, page_size: 1000 })
      .then((data) => data.items || [])
      .catch(() => [])
  const [monHoc, toHop, khuVucUuTien, doiTuongUuTien] = await Promise.all([
    lay(fetchMonHoc),
    lay(fetchToHopMonHoc),
    lay(fetchKhuVucUuTien),
    lay(fetchDoiTuongUuTien),
  ])
  danhMuc.value = { monHoc, toHop, khuVucUuTien, doiTuongUuTien }
}

// Lấy tỉnh/khu vực trong hồ sơ và đặt làm bộ lọc, thứ tự mặc định.
function apDungHoSo() {
  const tinhTim = tinhOptions.value.find((item) => item.id === hoSo.value?.tinh_thanh_id) || null
  if (!tinhTim) {
    tinhHoSo.value = null
    if (sapXep.value === 'gan_toi') sapXep.value = 'ten_asc'
    return
  }
  const khu = KHU_VUC.includes(tinhTim.khu_vuc) ? tinhTim.khu_vuc : ''
  tinhHoSo.value = { ten: tinhTim.ten_tinh, khu_vuc: khu }
  tinh.value = tinhTim.ten_tinh
  khuVuc.value = khu
  sapXep.value = 'gan_toi'
}

async function chuanBiHoSo() {
  daDangNhap.value = auth.isAuthenticated
  tinhHoSo.value = null
  hoSo.value = null
  let tinhItems = []
  try {
    const data = await fetchTinhThanh({ page: 1, page_size: 200, trang_thai: 1 }, { skipLoading: true })
    tinhItems = [...(data.items || [])]
    tinhItems.sort((a, b) => String(a.ten_tinh || '').localeCompare(String(b.ten_tinh || ''), 'vi'))
  } catch {
    tinhItems = []
  }
  tinhOptions.value = tinhItems
  if (!auth.isAuthenticated) {
    luotDaDung.value = docLuot()
    await taiDanhMucHoSo()
    return
  }
  try {
    const [data] = await Promise.all([fetchHoSo({ skipLoading: true }), taiDanhMucHoSo()])
    hoSo.value = data
    daDangNhap.value = true
  } catch {
    hoSo.value = null
    daDangNhap.value = false
    luotDaDung.value = docLuot()
    return
  }
  luotDaDung.value = docLuot()
  apDungHoSo()
  boLoc.value = { ...boLoc.value, tinh: tinh.value, khuVuc: khuVuc.value, sapXep: sapXep.value }
}

async function tai() {
  const ma = maNganh.value
  const lan = ++lanTai
  danhSach.value = []
  total.value = 0
  if (!ma) {
    loi.value = 'Không có mã ngành.'
    return
  }
  dangTai.value = true
  loi.value = ''
  try {
    const params = {
      ma_nganh: ma,
      nam_tuyen_sinh: boLoc.value.namHoc || NAM_HIEN_TAI,
      sap_xep: boLoc.value.sapXep,
      page: trang.value,
      page_size: soMoiTrang.value,
    }
    if (boLoc.value.tuKhoa) params.q = boLoc.value.tuKhoa
    if (boLoc.value.khuVuc) params.vung_mien = boLoc.value.khuVuc
    if (boLoc.value.loai) params.loai_co_so = boLoc.value.loai
    if (boLoc.value.tinh) params.ten_tinh_thanh = boLoc.value.tinh
    if (boLoc.value.sapXep === 'gan_toi' && tinhHoSo.value) {
      params.uu_tien_tinh = tinhHoSo.value.ten
      if (tinhHoSo.value.khu_vuc) params.uu_tien_khu_vuc = tinhHoSo.value.khu_vuc
    }
    const data = await fetchTruongDaoTao(params, { skipLoading: true })
    if (lan !== lanTai) return
    danhSach.value = data.items || []
    total.value = data.total || 0
  } catch {
    if (lan !== lanTai) return
    loi.value = 'Không tải được trường phù hợp.'
  } finally {
    if (lan === lanTai) dangTai.value = false
  }
}

function timKiem() {
  const nam = Number(namHoc.value)
  boLoc.value = {
    tuKhoa: tuKhoa.value.trim(),
    khuVuc: khuVuc.value || '',
    namHoc: Number.isInteger(nam) ? nam : NAM_HIEN_TAI,
    loai: loai.value || '',
    tinh: tinh.value || '',
    sapXep: sapXep.value || 'ten_asc',
  }
  if (trang.value !== 1) trang.value = 1
  else tai()
}

// Mỗi lần người dùng chủ động tìm (bấm Tìm kiếm, đổi loại, sắp xếp, lọc hồ sơ) trừ 1 lượt.
// Chuyển trang và lần tải đầu không tính.
function timCoLuot() {
  if (!conLuot.value) {
    ElMessage.warning(
      daDangNhap.value
        ? 'Bạn đã dùng hết lượt tìm trường phù hợp hôm nay.'
        : 'Bạn đã dùng lượt tìm thử. Đăng ký hoặc đăng nhập để tìm tiếp.',
    )
    return false
  }
  ghiLuot(luotDaDung.value + 1)
  timKiem()
  return true
}

function chonLoai(value) {
  if (!conLuot.value) return
  loai.value = value
  timCoLuot()
}

function boLocHoSo() {
  khuVuc.value = ''
  tinh.value = ''
  timCoLuot()
}

function locTheoHoSo() {
  if (!tinhHoSo.value) return
  tinh.value = tinhHoSo.value.ten
  khuVuc.value = tinhHoSo.value.khu_vuc
  timCoLuot()
}

// Khách: dùng nơi ở vừa nhập làm bộ lọc và thứ tự "gần nơi ở", giống hồ sơ thành viên.
// Tổ hợp và điểm dự kiến mới hiển thị, chưa gửi lên API.
function timTheoHoSoKhach() {
  const tinhChon = tinhOptions.value.find((item) => item.id === hoSoKhach.value.tinhId) || null
  if (tinhChon) {
    const khu = KHU_VUC.includes(tinhChon.khu_vuc) ? tinhChon.khu_vuc : ''
    tinhHoSo.value = { ten: tinhChon.ten_tinh, khu_vuc: khu }
    tinh.value = tinhChon.ten_tinh
    khuVuc.value = khu
    sapXep.value = 'gan_toi'
  } else {
    tinhHoSo.value = null
    if (sapXep.value === 'gan_toi') sapXep.value = 'ten_asc'
  }
  timCoLuot()
}

function daLuuHoSo(data) {
  hoSo.value = data
  hoSoMo.value = false
  apDungHoSo()
  timKiem()
}

watch(maNganh, (ma, truoc) => {
  if (!sanSang.value || !ma || ma === truoc) return
  taiNganh(ma)
  if (trang.value !== 1) trang.value = 1
  else tai()
})

watch(trang, () => {
  if (sanSang.value) tai()
})

watch(soMoiTrang, () => {
  if (!sanSang.value) return
  if (trang.value !== 1) trang.value = 1
  else tai()
})

onMounted(async () => {
  await Promise.all([taiNganh(maNganh.value), chuanBiHoSo()])
  sanSang.value = true
  tai()
})
</script>

<style scoped>
/* Tiêu đề trái, nút quay lại phải. Thêm .truong-phu-hop để thắng rule căn giữa dùng chung. */
.truong-phu-hop .truong-phu-hop__header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 16px;
  text-align: left;
}

.truong-phu-hop .truong-phu-hop__header .holland-overview__title {
  margin: 0;
}

/* Card thông tin ngành, cùng kiểu với major-detail ở trang chi tiết ngành. */
.truong-phu-hop__hero {
  display: flex;
  align-items: stretch;
  gap: 18px;
  padding: 16px;
  border: 1px solid #c5d5cc;
  border-radius: 12px;
  background: #f6faf7;
  box-shadow: 0 8px 22px rgba(28, 43, 35, 0.08);
  text-align: left;
}

.truong-phu-hop__info {
  flex: 1;
  display: flex;
  align-items: stretch;
  gap: 18px;
  min-width: 0;
}

.truong-phu-hop__image {
  flex: 0 0 300px;
  width: 300px;
  height: 200px;
  object-fit: cover;
  border-radius: 10px;
  background: #e7edf2;
}

.truong-phu-hop__intro {
  flex: 1;
  min-width: 0;
}

.truong-phu-hop__kicker {
  margin: 0 0 6px;
  color: #3d5c4c;
  font-size: 0.875rem;
}

.truong-phu-hop__code {
  display: inline-block;
  margin: 0 0 6px;
  padding: 2px 10px;
  border-radius: 0.375rem;
  background: #0c5c34;
  color: #fff;
  font-size: 0.85rem;
  letter-spacing: 0.03em;
}

.truong-phu-hop__name {
  margin: 0;
  color: #0c5c34;
  font-size: 1.45rem;
  font-weight: 400;
  line-height: 1.3;
}

.truong-phu-hop__en {
  margin: 4px 0 0;
  color: #3d5c4c;
  font-size: 1rem;
  line-height: 1.4;
}

.truong-phu-hop__text {
  display: -webkit-box;
  margin: 10px 0 0;
  overflow: hidden;
  color: #1c2836;
  font-size: 1rem;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.truong-phu-hop__facts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0 0;
}

.truong-phu-hop__fact {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  max-width: 100%;
  margin: 0;
  padding: 4px 12px;
  border: 1px solid #c5d5cc;
  border-radius: 0.375rem;
  background: #fff;
}

.truong-phu-hop__fact dt {
  margin: 0;
  color: #5a7266;
  font-size: 0.78rem;
  font-weight: 400;
  white-space: nowrap;
}

.truong-phu-hop__fact dt::after {
  content: ':';
}

.truong-phu-hop__fact dd {
  margin: 0;
  color: #1c2836;
  font-size: 0.85rem;
  line-height: 1.35;
}

.truong-phu-hop__note {
  margin: 12px 0 0;
  color: #2c3a4d;
  font-size: 0.9375rem;
  line-height: 1.5;
}

@media (max-width: 767.98px) {
  .truong-phu-hop__info {
    flex-direction: column;
  }

  .truong-phu-hop__image {
    flex-basis: auto;
    width: 100%;
    height: 180px;
  }
}

.truong-phu-hop__links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ho-so-tom-tat__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.luot-tim {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border: 1px solid #b7d0c2;
  border-radius: 999px;
  background: #eef6f1;
  color: #0c5c34;
  font-size: 0.875rem;
  line-height: 1.4;
  white-space: nowrap;
}

.luot-tim--het {
  border-color: #f0c9a8;
  background: #fff6ee;
  color: #a5541a;
}

.luot-tim__het-note {
  margin: 12px 0 0;
  padding: 10px 14px;
  border: 1px solid #f0c9a8;
  border-radius: 10px;
  background: #fff6ee;
  color: #7a3f13;
  font-size: 0.9375rem;
  line-height: 1.5;
  text-align: left;
}

.luot-tim__link {
  padding: 0;
  border: 0;
  background: none;
  color: #0c5c34;
  font: inherit;
  font-weight: 700;
  text-decoration: underline;
  cursor: pointer;
}

.ho-so-khach {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 12px;
  margin-top: 14px;
}

.ho-so-khach__field {
  display: flex;
  flex: 1 1 200px;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.ho-so-khach__field--diem {
  flex: 0 1 160px;
}

.ho-so-khach__field :deep(.el-select),
.ho-so-khach__field :deep(.el-input-number) {
  width: 100%;
}

.ho-so-khach__cta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px 16px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px dashed #c5d5cc;
}

.ho-so-khach__cta p {
  flex: 1 1 320px;
  margin: 0;
  color: #3a4742;
  font-size: 0.9375rem;
  line-height: 1.5;
}

.ho-so-tom-tat {
  margin-top: 16px;
  padding: 16px 18px;
  border: 1px solid #dfeae3;
  border-radius: 12px;
  background: #fff;
  text-align: left;
}

.ho-so-tom-tat__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.ho-so-tom-tat__title {
  margin: 0;
  color: #1f2d26;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.4;
}

.ho-so-tom-tat__sub {
  margin: 2px 0 0;
  color: #5f7268;
  font-size: 0.875rem;
  line-height: 1.4;
}

.ho-so-tom-tat__list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.ho-so-chip {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid #e3eee7;
  border-radius: 10px;
  background: #f6fbf8;
}

.ho-so-chip__icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: #1f7a4d;
  font-size: 18px;
}

.ho-so-chip__body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.ho-so-chip__label {
  color: #5f7268;
  font-size: 0.78rem;
  line-height: 1.35;
}

.ho-so-chip__value {
  overflow: hidden;
  color: #1f2d26;
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ho-so-chip--trong {
  border-style: dashed;
  background: #fff;
}

.ho-so-chip--trong .ho-so-chip__icon,
.ho-so-chip--trong .ho-so-chip__value {
  color: #9aa8a0;
  font-weight: 400;
}

.loai-co-so {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.loai-co-so__chip {
  padding: 6px 16px;
  border: 1px solid #cfe1d6;
  border-radius: 999px;
  background: #fff;
  color: #31483d;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.loai-co-so__chip:hover {
  border-color: #1f7a4d;
  color: #1f7a4d;
}

.loai-co-so__chip.is-active {
  border-color: #1f7a4d;
  background: #1f7a4d;
  color: #fff;
}

.loai-co-so__chip:focus-visible {
  outline: 2px solid rgba(31, 122, 77, 0.4);
  outline-offset: 2px;
}

@media (max-width: 767px) {
  .truong-phu-hop__hero {
    flex-direction: column;
  }

  .ho-so-tom-tat__head :deep(.el-button) {
    width: 100%;
  }
}

.nhom-filter__field--nam,
.nhom-filter__field--tinh,
.nhom-filter__field--sap-xep {
  flex: 1 1 160px;
  max-width: 220px;
}

.nhom-card__en,
.nhom-card__meta {
  margin: 0;
}
</style>
