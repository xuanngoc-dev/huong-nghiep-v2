<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { danhSachTruong, noiDungTruong } from '@/api/kiemTraDuLieu'
import KhoiDuLieu from '@/components/guest/kiem-tra-du-lieu/KhoiDuLieu.vue'
import NoiDungPhuongThuc from '@/components/guest/kiem-tra-du-lieu/NoiDungPhuongThuc.vue'
import {
  KHOA_NGANH_META,
  coGiaTri,
  khop,
  khoaConLai,
  khoiTrungNhau,
  maNganh,
  mucKhacNhau,
  nhan,
  nhanTruong,
  nhomPhuongThuc,
  tenNganh,
} from '@/components/guest/kiem-tra-du-lieu/nhanDuLieu'

defineOptions({ name: 'ValidateData' })

const danhSach = ref([])
const tenTep = ref('')
const noiDung = ref(null)
const dangTaiDanhSach = ref(false)
const dangTaiNoiDung = ref(false)
const loi = ref('')
const tab = ref('truong')
const tuKhoaPhuongThuc = ref('')
const tuKhoaNganh = ref('')
const tuKhoaApDung = ref('')
const khoaPhuongThuc = ref('')
const khoaNganh = ref('')
const khoaApDung = ref('')
const moPhuongThuc = ref('0')
const moQuyDoi = ref('')
const moUuTien = ref('')
const hienJsonTruong = ref(false)

const truongChon = computed(() => danhSach.value.find((item) => item.ten_tep === tenTep.value) || null)
const duLieu = computed(() => noiDung.value?.du_lieu ?? null)
const truong = computed(() => (duLieu.value && typeof duLieu.value === 'object' && !Array.isArray(duLieu.value) ? duLieu.value.truong || {} : {}))
const nganhs = computed(() => (Array.isArray(duLieu.value?.danh_sach_nganh) ? duLieu.value.danh_sach_nganh : []))
const gocKhac = computed(() => {
  if (!duLieu.value || typeof duLieu.value !== 'object' || Array.isArray(duLieu.value)) return {}
  return khoaConLai(duLieu.value, ['truong', 'danh_sach_nganh'])
})
const jsonTruong = computed(() => JSON.stringify(truong.value, null, 2))

const nganhCoKhoa = computed(() => nganhs.value.map((nganh, index) => ({ khoa: String(index), nganh })))
const nhom = computed(() => nhomPhuongThuc(nganhs.value))
const nhomLoc = computed(() =>
  nhom.value.filter((item) => khop(tuKhoaPhuongThuc.value, item.ma, item.ten, item.loai)),
)
const nhomDangChon = computed(() => nhomLoc.value.find((item) => item.key === khoaPhuongThuc.value) || null)
const khacNhau = computed(() => (nhomDangChon.value ? mucKhacNhau(nhomDangChon.value.apDung) : []))
const apDungLoc = computed(() => {
  const rows = nhomDangChon.value?.apDung || []
  return rows.filter((item) =>
    khop(tuKhoaApDung.value, tenNganh(item.nganh), maNganh(item.nganh), item.nganh.ten_nganh, item.nganh.ten_chuong_trinh),
  )
})
const banDangChon = computed(() => apDungLoc.value.find((item) => item.khoa === khoaApDung.value) || null)

const nganhLoc = computed(() =>
  nganhCoKhoa.value.filter((item) =>
    khop(tuKhoaNganh.value, tenNganh(item.nganh), maNganh(item.nganh), item.nganh.ten_nganh, item.nganh.ten_chuong_trinh),
  ),
)
const nganhDangChon = computed(() => nganhLoc.value.find((item) => item.khoa === khoaNganh.value) || null)
const phuongThucCuaNganh = computed(() =>
  (Array.isArray(nganhDangChon.value?.nganh.phuong_thuc_tuyen_sinh) ? nganhDangChon.value.nganh.phuong_thuc_tuyen_sinh : []).filter(
    (item) => item && typeof item === 'object',
  ),
)
const nganhConLai = computed(() =>
  khoaConLai(nganhDangChon.value?.nganh, [...KHOA_NGANH_META, 'dieu_kien_nganh', 'phuong_thuc_tuyen_sinh']),
)

const quyDoi = computed(() => khoiTrungNhau(nganhs.value, 'quy_doi_diem'))
const uuTien = computed(() => khoiTrungNhau(nganhs.value, 'diem_cong_uu_tien'))

const thongKe = computed(() => ({
  soNganh: nganhs.value.length,
  soPhuongThuc: nhom.value.length,
  soBanGhi: nhom.value.reduce((total, item) => total + item.apDung.length, 0),
  soQuyDoi: quyDoi.value.length,
  soUuTien: uuTien.value.length,
}))

watch(nhomLoc, (list) => {
  if (!list.some((item) => item.key === khoaPhuongThuc.value)) khoaPhuongThuc.value = list[0]?.key || ''
})
watch(apDungLoc, (list) => {
  if (!list.some((item) => item.khoa === khoaApDung.value)) khoaApDung.value = list[0]?.khoa || ''
})
watch(nganhLoc, (list) => {
  if (!list.some((item) => item.khoa === khoaNganh.value)) khoaNganh.value = list[0]?.khoa || ''
})
watch(khoaNganh, () => {
  moPhuongThuc.value = '0'
})
watch(tenTep, (ten) => {
  taiNoiDung(ten)
})

onMounted(taiDanhSach)

async function taiDanhSach() {
  dangTaiDanhSach.value = true
  loi.value = ''
  try {
    danhSach.value = await danhSachTruong()
  } catch (error) {
    loi.value = thongBao(error)
  } finally {
    dangTaiDanhSach.value = false
  }
}

async function taiNoiDung(ten) {
  noiDung.value = null
  hienJsonTruong.value = false
  moQuyDoi.value = ''
  moUuTien.value = ''
  tuKhoaPhuongThuc.value = ''
  tuKhoaNganh.value = ''
  tuKhoaApDung.value = ''
  if (!ten) return
  dangTaiNoiDung.value = true
  loi.value = ''
  try {
    noiDung.value = await noiDungTruong(ten)
  } catch (error) {
    loi.value = thongBao(error)
  } finally {
    dangTaiNoiDung.value = false
  }
}

function thongBao(error) {
  const detail = error?.response?.data?.detail
  return typeof detail === 'string' ? detail : 'Không tải được dữ liệu tuyển sinh.'
}

function hienSo(value) {
  if (value == null || value === '') return '—'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

function tomTat(khoi) {
  const nganh = new Set(khoi.apDung.map((item) => `${item.ma}|${item.nganh}`))
  const phuongThuc = [...new Set(khoi.apDung.map((item) => [item.maPhuongThuc, item.phuongThuc].filter(Boolean).join(' ')))]
  return { soNganh: nganh.size, phuongThuc }
}

function tieuDeKhoi(khoi, index, nhanKhoi) {
  const info = tomTat(khoi)
  const mau = info.phuongThuc.slice(0, 2).join('; ')
  const them = info.phuongThuc.length > 2 ? ` +${info.phuongThuc.length - 2}` : ''
  return `${nhanKhoi} ${index + 1} · ${info.soNganh} ngành · ${mau}${them}`
}
</script>

<template>
  <section v-loading="dangTaiDanhSach || dangTaiNoiDung" class="validate-data">
    <div class="container-fluid">
      <header class="validate-data__head">
        <div>
          <h1>Kiểm tra dữ liệu</h1>
          <p>Chọn trường để xem thông tin tuyển sinh, phương thức, ngành, điểm quy đổi và điểm ưu tiên, khuyến khích.</p>
        </div>
        <el-select
          v-model="tenTep"
          class="school-select"
          filterable
          clearable
          placeholder="Chọn trường"
          no-data-text="Chưa có file tuyển sinh"
        >
          <el-option v-for="item in danhSach" :key="item.ten_tep" :label="nhanTruong(item)" :value="item.ten_tep" />
        </el-select>
      </header>

      <el-alert v-if="loi" class="validate-data__alert" :title="loi" type="error" :closable="false" show-icon />

      <el-empty v-if="!noiDung && !loi" description="Chọn một trường trong danh sách." />

      <template v-else-if="noiDung">
        <div class="validate-data__meta">
          <strong>{{ truong.ten_truong || truongChon?.ten_truong }}</strong>
          <span v-if="truong.ma_truong || truongChon?.ma_truong">{{ truong.ma_truong || truongChon?.ma_truong }}</span>
          <span v-if="truong.nam_tuyen_sinh">Năm {{ truong.nam_tuyen_sinh }}</span>
          <span>{{ thongKe.soNganh }} ngành</span>
          <span>{{ thongKe.soPhuongThuc }} phương thức</span>
          <span>{{ thongKe.soQuyDoi }} cách quy đổi</span>
          <span>{{ thongKe.soUuTien }} cách cộng ưu tiên</span>
          <span class="file-name">{{ noiDung.ten_tep }}</span>
        </div>
        <el-alert
          v-if="noiDung.hop_le === false"
          class="validate-data__alert"
          title="File này chưa đúng cấu trúc tuyển sinh (trường, danh sách ngành, phương thức)."
          type="warning"
          :closable="false"
          show-icon
        />

        <el-tabs v-model="tab" class="validate-data__tabs">
          <el-tab-pane label="Thông tin trường" name="truong">
            <div class="pane-bar">
              <h2>Thông tin trường</h2>
              <el-switch v-model="hienJsonTruong" active-text="JSON gốc" />
            </div>
            <pre v-if="hienJsonTruong" class="json-block">{{ jsonTruong }}</pre>
            <KhoiDuLieu v-else :value="truong" />
            <article v-if="coGiaTri(gocKhac)" class="extra-block">
              <h2>Dữ liệu khác của file</h2>
              <KhoiDuLieu :value="gocKhac" />
            </article>
          </el-tab-pane>

          <el-tab-pane lazy :label="`Theo phương thức (${thongKe.soPhuongThuc})`" name="phuong-thuc">
            <div class="work">
              <aside class="picker">
                <el-input v-model="tuKhoaPhuongThuc" clearable placeholder="Tìm phương thức" />
                <p v-if="!nhomLoc.length" class="empty-note">Không có phương thức khớp.</p>
                <div v-else class="picker__list">
                  <button
                    v-for="item in nhomLoc"
                    :key="item.key"
                    type="button"
                    :class="{ 'is-active': item.key === khoaPhuongThuc }"
                    @click="khoaPhuongThuc = item.key"
                  >
                    <strong>{{ item.ten }}</strong>
                    <small>{{ [item.ma, item.loai].filter(Boolean).join(' · ') }}</small>
                    <span>{{ item.apDung.length }} ngành</span>
                  </button>
                </div>
              </aside>

              <div v-if="nhomDangChon" class="detail">
                <h2>{{ nhomDangChon.ten }}</h2>
                <p class="detail__lead">{{ [nhomDangChon.ma, nhomDangChon.loai].filter(Boolean).join(' · ') }}</p>
                <el-alert
                  v-if="nhomDangChon.apDung.length > 1 && !khacNhau.length"
                  title="Các mục chính giống nhau ở mọi ngành trong phương thức này."
                  type="success"
                  :closable="false"
                  show-icon
                />
                <el-alert
                  v-else-if="khacNhau.length"
                  :title="`Khác nhau theo ngành: ${khacNhau.join(', ')}`"
                  type="info"
                  :closable="false"
                  show-icon
                />
                <el-input v-model="tuKhoaApDung" class="detail__search" clearable placeholder="Lọc ngành trong phương thức" />
                <div class="picker__list picker__list--majors">
                  <button
                    v-for="item in apDungLoc"
                    :key="item.khoa"
                    type="button"
                    :class="{ 'is-active': item.khoa === khoaApDung }"
                    @click="khoaApDung = item.khoa"
                  >
                    <strong>{{ tenNganh(item.nganh) }}</strong>
                    <small>{{ maNganh(item.nganh) || item.nganh.ten_nganh }}</small>
                    <span>
                      Chỉ tiêu {{ hienSo(item.phuongThuc.chi_tieu_phuong_thuc) }} · Điểm chuẩn {{ hienSo(item.phuongThuc.diem_chuan) }} · Điểm sàn {{ hienSo(item.phuongThuc.diem_san) }}
                    </span>
                  </button>
                </div>
                <NoiDungPhuongThuc v-if="banDangChon" :phuong-thuc="banDangChon.phuongThuc" />
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane lazy :label="`Theo ngành (${thongKe.soNganh})`" name="nganh">
            <div class="work">
              <aside class="picker">
                <el-input v-model="tuKhoaNganh" clearable placeholder="Tìm ngành, mã ngành, mã xét tuyển" />
                <p v-if="!nganhLoc.length" class="empty-note">Không có ngành khớp.</p>
                <div v-else class="picker__list">
                  <button
                    v-for="item in nganhLoc"
                    :key="item.khoa"
                    type="button"
                    :class="{ 'is-active': item.khoa === khoaNganh }"
                    @click="khoaNganh = item.khoa"
                  >
                    <strong>{{ tenNganh(item.nganh) }}</strong>
                    <small>{{ maNganh(item.nganh) }}</small>
                    <span v-if="item.nganh.ten_chuong_trinh && item.nganh.ten_nganh !== item.nganh.ten_chuong_trinh">{{ item.nganh.ten_nganh }}</span>
                  </button>
                </div>
              </aside>

              <div v-if="nganhDangChon" class="detail">
                <h2>{{ tenNganh(nganhDangChon.nganh) }}</h2>
                <dl class="meta">
                  <div v-for="key in KHOA_NGANH_META" :key="key">
                    <dt>{{ nhan(key) }}</dt>
                    <dd>{{ hienSo(nganhDangChon.nganh[key]) }}</dd>
                  </div>
                </dl>
                <article class="extra-block">
                  <h3>Điều kiện ngành</h3>
                  <KhoiDuLieu :value="nganhDangChon.nganh.dieu_kien_nganh" />
                </article>
                <article v-if="coGiaTri(nganhConLai)" class="extra-block">
                  <h3>Thông tin khác của ngành</h3>
                  <KhoiDuLieu :value="nganhConLai" />
                </article>
                <h3 class="detail__methods">Phương thức của ngành ({{ phuongThucCuaNganh.length }})</h3>
                <el-collapse v-if="phuongThucCuaNganh.length" v-model="moPhuongThuc" accordion>
                  <el-collapse-item
                    v-for="(phuongThuc, index) in phuongThucCuaNganh"
                    :key="`${khoaNganh}-${index}`"
                    :name="String(index)"
                    :title="`${phuongThuc.ma_phuong_thuc || '—'} · ${phuongThuc.ten_phuong_thuc || 'Phương thức'}`"
                  >
                    <NoiDungPhuongThuc v-if="moPhuongThuc === String(index)" :phuong-thuc="phuongThuc" />
                  </el-collapse-item>
                </el-collapse>
                <p v-else class="empty-note">Ngành này chưa có phương thức tuyển sinh.</p>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane lazy :label="`Điểm quy đổi (${thongKe.soQuyDoi})`" name="quy-doi">
            <p v-if="!quyDoi.length" class="empty-note">Trường này không có điểm quy đổi trong dữ liệu.</p>
            <el-collapse v-else v-model="moQuyDoi" accordion>
              <el-collapse-item
                v-for="(khoi, index) in quyDoi"
                :key="index"
                :name="String(index)"
                :title="tieuDeKhoi(khoi, index, 'Cách quy đổi')"
              >
                <template v-if="moQuyDoi === String(index)">
                  <KhoiDuLieu :value="khoi.value" />
                  <h3 class="usage-title">Áp dụng cho {{ khoi.apDung.length }} bản ghi</h3>
                  <ul class="usage-list">
                    <li v-for="(item, itemIndex) in khoi.apDung" :key="itemIndex">
                      {{ item.ma || 'Không mã' }} · {{ item.nganh }} — {{ item.maPhuongThuc }} {{ item.phuongThuc }}
                    </li>
                  </ul>
                </template>
              </el-collapse-item>
            </el-collapse>
          </el-tab-pane>

          <el-tab-pane lazy :label="`Điểm ưu tiên (${thongKe.soUuTien})`" name="uu-tien">
            <p v-if="!uuTien.length" class="empty-note">Trường này không có điểm ưu tiên, khuyến khích trong dữ liệu.</p>
            <el-collapse v-else v-model="moUuTien" accordion>
              <el-collapse-item
                v-for="(khoi, index) in uuTien"
                :key="index"
                :name="String(index)"
                :title="tieuDeKhoi(khoi, index, 'Cách cộng điểm')"
              >
                <template v-if="moUuTien === String(index)">
                  <KhoiDuLieu :value="khoi.value" />
                  <h3 class="usage-title">Áp dụng cho {{ khoi.apDung.length }} bản ghi</h3>
                  <ul class="usage-list">
                    <li v-for="(item, itemIndex) in khoi.apDung" :key="itemIndex">
                      {{ item.ma || 'Không mã' }} · {{ item.nganh }} — {{ item.maPhuongThuc }} {{ item.phuongThuc }}
                    </li>
                  </ul>
                </template>
              </el-collapse-item>
            </el-collapse>
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>
  </section>
</template>

<style scoped>
.validate-data {
  padding: 28px 0 48px;
}

.validate-data__head {
  display: grid;
  gap: 16px;
  margin-bottom: 16px;
}

.validate-data__head h1 {
  margin: 0 0 6px;
  font-size: 32px;
}

.validate-data__head p,
.detail__lead,
.empty-note {
  margin: 0;
  color: #5c6b62;
}

.school-select {
  width: min(100%, 760px);
}

.validate-data__alert {
  margin-bottom: 16px;
}

.validate-data__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  align-items: center;
  margin-bottom: 16px;
}

.validate-data__meta span,
.file-name {
  color: #5c6b62;
}

.file-name {
  font-size: 13px;
}

.pane-bar,
.phuong-thuc-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.pane-bar h2,
.detail h2,
.extra-block h2,
.extra-block h3,
.detail__methods,
.usage-title {
  margin: 0;
}

.extra-block,
.detail__methods,
.usage-title,
.detail__search {
  margin-top: 16px;
}

.work {
  display: grid;
  grid-template-columns: minmax(240px, 320px) minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.picker__list {
  display: grid;
  gap: 8px;
  max-height: 70vh;
  margin-top: 8px;
  overflow: auto;
}

.picker__list--majors {
  max-height: 240px;
}

.picker__list button {
  display: grid;
  gap: 2px;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e4eee6;
  border-radius: 8px;
  background: #fff;
  color: inherit;
  text-align: left;
}

.picker__list button.is-active {
  border-color: #3f9643;
  background: #f3faf4;
}

.picker__list small,
.picker__list span {
  color: #5c6b62;
  font-size: 12px;
}

.detail {
  min-width: 0;
  padding: 16px;
  border: 1px solid #e4eee6;
  border-radius: 12px;
}

.meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px 16px;
  margin: 12px 0 0;
}

.meta dt {
  margin: 0;
  color: #5c6b62;
  font-size: 13px;
}

.meta dd {
  margin: 2px 0 0;
  font-weight: 600;
  word-break: break-word;
}

.json-block {
  margin: 0;
  max-height: 70vh;
  overflow: auto;
  padding: 12px;
  border-radius: 8px;
  background: #f4f7f5;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
}

.usage-list {
  max-height: 240px;
  margin: 8px 0 0;
  padding-left: 18px;
  overflow: auto;
}

@media (max-width: 900px) {
  .work {
    grid-template-columns: 1fr;
  }

  .picker__list,
  .picker__list--majors {
    max-height: 280px;
  }
}
</style>
