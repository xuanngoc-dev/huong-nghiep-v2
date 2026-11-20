<template>
  <CustomCard shadow="never" class="catalog-card">
    <div class="toolbar doi-chieu__toolbar">
      <h2 class="toolbar__title">Đối chiếu dữ liệu</h2>
      <CustomButton v-if="props.coTheSua" :disabled="props.dangXuLy" plain @click="moTruongMoi">Thêm hoặc thay thế trường</CustomButton>
    </div>
    <div class="filters doi-chieu__filters">
      <CustomSelect v-model="nhom" class="filter-status" aria-label="Nhóm dữ liệu" placeholder="Chọn nhóm dữ liệu">
        <CustomOption label="Tất cả nhóm" value="tat_ca" />
        <CustomOption v-for="n in cacNhom" :key="n.nhom" :label="`${n.nhom} (${n.soLuong})`" :value="n.nhom" />
      </CustomSelect>
      <CustomInput v-model="tuKhoa" class="filter-search" aria-label="Tìm mục cần đối chiếu" placeholder="Tìm theo tên mục, mã hoặc giá trị" clearable />
      <el-checkbox v-model="chiMauThuan">Chỉ mục có mâu thuẫn</el-checkbox>
      <el-checkbox v-if="props.coBanTruoc" v-model="chiThayDoi">Chỉ mục đã thay đổi</el-checkbox>
    </div>

    <div class="doi-chieu">
      <div class="doi-chieu__danh-sach">
        <p v-if="!mucLoc.length" class="chu-thich">Không có mục phù hợp.</p>
        <ul v-else class="danh-sach-muc">
          <li v-for="muc in mucTheoTrang" :key="muc.duong_dan">
            <button type="button" class="nut-muc" :class="{ 'nut-muc--chon': muc.duong_dan === duongDanChon }" :aria-pressed="muc.duong_dan === duongDanChon" @click="chonMuc(muc)">
              <small>{{ muc.viTri }}</small>
              <span class="nut-muc__nhan"><strong>{{ muc.nhan }}</strong><CustomTag size="small" :type="trangThaiMuc(muc).loai">{{ trangThaiMuc(muc).nhan }}</CustomTag></span>
              <span class="nut-muc__gia-tri">{{ hienGiaTri(giaTriHienTai(muc)) }}</span>
            </button>
          </li>
        </ul>
        <CustomPagination v-if="mucLoc.length > kichThuoc" v-model:current-page="trang" :page-size="kichThuoc" :total="mucLoc.length" :pager-count="5" layout="prev, pager, next" small />
      </div>

      <section v-if="mucChon" ref="khungNoiDung" class="doi-chieu__noi-dung" aria-labelledby="tieu-de-muc" tabindex="-1">
        <p class="chu-thich">{{ mucChon.nhom }} · {{ mucChon.viTri }}</p>
        <h3 id="tieu-de-muc">{{ mucChon.nhan }}</h3>
        <details class="duong-dan">
          <summary>Đường dẫn dữ liệu</summary>
          <code>{{ mucChon.duong_dan }}</code>
        </details>

        <div v-if="!mucChon.daBo" class="gia-tri">
          <div><h4>AI đề xuất</h4><pre>{{ hienGiaTri(mucChon.gia_tri_ai) }}</pre></div>
          <div><h4>Giá trị trong bản nháp</h4><pre>{{ hienGiaTri(mucChon.giaTri) }}</pre></div>
        </div>
        <div v-if="mucChon.daThayDoi" class="gia-tri gia-tri--truoc">
          <div><h4>{{ mucChon.daBo ? 'Đã bỏ · Giá trị ở phiên bản trước' : 'Giá trị ở phiên bản trước' }}</h4><pre>{{ hienGiaTri(mucChon.giaTriTruoc) }}</pre></div>
        </div>

        <h4 v-if="mucChon.dan_chung?.length" class="tieu-de-dan-chung">Dẫn chứng</h4>
        <p v-if="!mucChon.daBo && !mucChon.dan_chung?.length" class="chu-thich">Chưa có dẫn chứng cho mục này.</p>
        <ul v-if="mucChon.dan_chung?.length" class="dan-chung">
          <li v-for="danChung in cacDanChung" :key="danChung.id" class="dan-chung__the">
            <div class="dan-chung__dau">
              <strong>{{ nguonTheoId.get(danChung.nguon_id)?.tieu_de || `Nguồn #${danChung.nguon_id}` }}</strong>
              <el-checkbox v-if="choSuaMuc" :model-value="bieuMau.dan_chung_ids.includes(danChung.id)" :disabled="props.dangXuLy || (bieuMau.dan_chung_ids.length >= 50 && !bieuMau.dan_chung_ids.includes(danChung.id))" @change="chonDanChung(danChung.id, $event)">Làm căn cứ</el-checkbox>
              <CustomTag v-else-if="mucChon.dan_chung_ids?.includes(danChung.id)" size="small" type="success">Căn cứ đã chọn</CustomTag>
            </div>
            <p class="chu-thich">
              {{ danChung.vi_tri || 'Vị trí chưa xác định' }}
              <span v-if="nguonTheoId.get(danChung.nguon_id)?.ngay_hieu_luc"> · Hiệu lực {{ ngayVanBan(nguonTheoId.get(danChung.nguon_id).ngay_hieu_luc) }}</span>
            </p>
            <p class="dan-chung__gia-tri">Giá trị theo nguồn · <strong>{{ hienGiaTri(danChung.gia_tri) }}</strong></p>
            <blockquote v-if="danChung.trich_dan">{{ danChung.trich_dan }}</blockquote>
            <div v-if="danChung.lienKet.url" class="dan-chung__lien-ket">
              <a class="cell-link" :href="danChung.lienKet.url" target="_blank" rel="noopener noreferrer">{{ danChung.lienKet.nhan }}</a>
              <a v-if="danChung.lienKet.trangNguon" class="cell-link" :href="danChung.lienKet.trangNguon" target="_blank" rel="noopener noreferrer">Mở trang nguồn</a>
            </div>
          </li>
        </ul>

        <CustomForm v-if="choSuaMuc" :model="bieuMau" class="form-grid doi-chieu__form" :disabled="props.dangXuLy" @submit.prevent="chuanBiLuu">
          <div class="form-grid__body">
            <CustomFormItem class="form-grid__full" label="Giá trị chỉnh sửa (JSON)">
              <CustomInput v-model="bieuMau.giaTriJson" class="json-input" type="textarea" :autosize="{ minRows: 2, maxRows: 10 }" placeholder='Nhập giá trị JSON, ví dụ 95, "A00", null hoặc []' />
            </CustomFormItem>
            <CustomFormItem class="form-grid__full" label="Ghi chú đối chiếu hoặc lý do sửa">
              <CustomInput v-model="bieuMau.ghi_chu" type="textarea" :autosize="{ minRows: 2, maxRows: 6 }" placeholder="Nhập lý do sửa hoặc ghi chú nếu dữ liệu chưa công bố" maxlength="2000" show-word-limit />
            </CustomFormItem>
            <CustomFormItem class="form-grid__full">
              <el-checkbox v-model="bieuMau.da_kiem_tra">Đã kiểm tra mục này</el-checkbox>
            </CustomFormItem>
            <div v-for="(danChung, index) in bieuMau.dan_chung_moi" :key="index" class="form-grid__full dan-chung__them">
              <div class="dan-chung__dau">
                <h4>Dẫn chứng bổ sung</h4>
                <CustomButton link type="danger" @click="bieuMau.dan_chung_moi.splice(index, 1)">Bỏ dẫn chứng</CustomButton>
              </div>
              <div class="form-grid__body">
                <CustomFormItem class="form-grid__span-2" label="Tài liệu" required>
                  <CustomSelect v-model="danChung.nguon_id" placeholder="Chọn nguồn đã sử dụng" filterable>
                    <CustomOption v-for="nguon in nguonApDung" :key="nguon.id" :label="nguon.tieu_de || nguon.url" :value="nguon.id" />
                  </CustomSelect>
                </CustomFormItem>
                <CustomFormItem class="form-grid__full" label="Trang PDF hoặc mục trên website" required>
                  <CustomInput v-model="danChung.vi_tri" placeholder="Nhập số trang PDF hoặc tên mục trên website" maxlength="400" />
                </CustomFormItem>
                <CustomFormItem class="form-grid__full" label="Đoạn trích" required>
                  <CustomInput v-model="danChung.trich_dan" type="textarea" placeholder="Nhập đoạn trích nguyên văn chứa giá trị" maxlength="2000" show-word-limit />
                </CustomFormItem>
              </div>
            </div>
          </div>
          <div class="doi-chieu__nut">
            <CustomButton v-if="nguonApDung.length" :disabled="bieuMau.dan_chung_moi.length >= 20" plain @click="themDanChung">Bổ sung dẫn chứng</CustomButton>
            <CustomButton v-if="suaTheoDuongDan.has(mucChon.duong_dan) || daNhapSua" text @click="boSuaMuc">Bỏ chỉnh sửa mục</CustomButton>
          </div>
          <el-alert v-if="loi" :title="loi" type="error" show-icon :closable="false" class="doi-chieu__loi" />
        </CustomForm>
        <p v-else-if="mucChon.ghi_chu" class="ghi-chu"><strong>Ghi chú đối chiếu</strong> · {{ mucChon.ghi_chu }}</p>
      </section>
    </div>
  </CustomCard>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { bangNhau, hienGiaTri, nhomMuc, phanTichGiaTri } from './doi-chieu-ban-nhap'
import { lienKetDanChung, ngayVanBan } from './thu-thap-du-lieu'

const props = defineProps({
  cacMuc: { type: Array, required: true },
  nguon: { type: Array, required: true },
  capNhat: { type: Number, required: true },
  coTheSua: Boolean,
  coBanTruoc: Boolean,
  dangXuLy: Boolean,
})
const thayDoi = defineModel({ type: Array, required: true })
const emit = defineEmits(['them-truong'])

const nhom = ref('tat_ca')
const tuKhoa = ref('')
const chiMauThuan = ref(false)
const chiThayDoi = ref(false)
const trang = ref(1)
const kichThuoc = 12
const duongDanChon = ref('')
const khungNoiDung = ref(null)
const loi = ref('')
const bieuMau = reactive({ giaTriJson: '', ghi_chu: '', da_kiem_tra: false, dan_chung_ids: [], dan_chung_moi: [] })

const nguonTheoId = computed(() => new Map(props.nguon.map((nguon) => [nguon.id, nguon])))
const nguonApDung = computed(() => props.nguon.filter((nguon) => nguon.chinh_thuc && nguon.phu_hop && nguon.lua_chon === 'su_dung'))
const suaTheoDuongDan = computed(() => new Map(thayDoi.value.map((item) => [item.duong_dan, item])))
const cacNhom = computed(() => nhomMuc(props.cacMuc))
const mucLoc = computed(() => {
  const cauTim = tuKhoa.value.trim().toLocaleLowerCase('vi')
  return props.cacMuc.filter((muc) => (nhom.value === 'tat_ca' || nhom.value === muc.nhom)
    && (!chiMauThuan.value || muc.mau_thuan)
    && (!chiThayDoi.value || muc.daThayDoi)
    && (!cauTim || `${muc.nhan} ${muc.viTri} ${muc.duong_dan} ${hienGiaTri(muc.giaTri)}`.toLocaleLowerCase('vi').includes(cauTim)))
})
const mucTheoTrang = computed(() => mucLoc.value.slice((trang.value - 1) * kichThuoc, trang.value * kichThuoc))
const mucChon = computed(() => props.cacMuc.find((muc) => muc.duong_dan === duongDanChon.value))
const cacDanChung = computed(() => (mucChon.value?.dan_chung || []).map((danChung) => ({
  ...danChung,
  lienKet: lienKetDanChung(danChung, nguonTheoId.value.get(danChung.nguon_id)),
})))
const choSuaMuc = computed(() => props.coTheSua && mucChon.value && !mucChon.value.daBo)
const daNhapSua = computed(() => Boolean(choSuaMuc.value && (
  bieuMau.giaTriJson !== JSON.stringify(mucChon.value.giaTri, null, 2)
  || bieuMau.ghi_chu !== (mucChon.value.ghi_chu || '')
  || bieuMau.da_kiem_tra !== Boolean(mucChon.value.da_kiem_tra)
  || !bangNhau(bieuMau.dan_chung_ids, mucChon.value.dan_chung_ids || [])
  || bieuMau.dan_chung_moi.length
)))

watch([nhom, tuKhoa, chiMauThuan, chiThayDoi], () => { trang.value = 1 })
watch([() => props.cacMuc, () => props.capNhat], ([items, lan], truoc) => {
  if (!mucChon.value) {
    const mucUuTien = items.find((muc) => muc.mau_thuan) || items[0]
    duongDanChon.value = mucUuTien?.duong_dan || ''
    if (mucUuTien) trang.value = Math.floor(items.indexOf(mucUuTien) / kichThuoc) + 1
    napBieuMau()
  } else if (lan !== truoc?.[1] || !daNhapSua.value) {
    napBieuMau()
  }
}, { immediate: true })

function napBieuMau() {
  const muc = mucChon.value
  if (!muc) return
  const sua = suaTheoDuongDan.value.get(muc.duong_dan)
  bieuMau.giaTriJson = JSON.stringify(Object.hasOwn(sua || {}, 'gia_tri') ? sua.gia_tri : muc.giaTri, null, 2) ?? ''
  bieuMau.ghi_chu = sua?.ghi_chu ?? muc.ghi_chu ?? ''
  bieuMau.da_kiem_tra = sua?.da_kiem_tra ?? Boolean(muc.da_kiem_tra)
  bieuMau.dan_chung_ids = [...(sua?.dan_chung_ids || muc.dan_chung_ids || [])]
  bieuMau.dan_chung_moi = (sua?.dan_chung_moi || []).map((item) => ({ ...item }))
  loi.value = ''
}

function trangThaiMuc(muc) {
  if (muc.daBo) return { nhan: 'Đã bỏ', loai: 'info' }
  if (suaTheoDuongDan.value.has(muc.duong_dan) || (muc === mucChon.value && daNhapSua.value)) return { nhan: 'Chưa lưu', loai: 'warning' }
  if (muc.mau_thuan) return { nhan: 'Mâu thuẫn', loai: 'danger' }
  if (muc.da_kiem_tra) return { nhan: 'Đã kiểm tra', loai: 'success' }
  if (!muc.dan_chung_ids?.length && !muc.ghi_chu) return { nhan: 'Cần đối chiếu', loai: 'warning' }
  return { nhan: 'Chưa kiểm tra', loai: 'info' }
}

function giaTriHienTai(muc) {
  const sua = suaTheoDuongDan.value.get(muc.duong_dan)
  return Object.hasOwn(sua || {}, 'gia_tri') ? sua.gia_tri : muc.giaTri
}

function chonDanChung(id, daChon) {
  bieuMau.dan_chung_ids = daChon ? [...bieuMau.dan_chung_ids, id] : bieuMau.dan_chung_ids.filter((item) => item !== id)
}

function themDanChung() {
  bieuMau.dan_chung_moi.push({ nguon_id: null, vi_tri: '', trich_dan: '' })
}

function chonMuc(muc) {
  if (duongDanChon.value === muc.duong_dan || !chuanBiLuu()) return
  duongDanChon.value = muc.duong_dan
  napBieuMau()
}

async function moDuongDan(duongDan) {
  const muc = props.cacMuc.find((item) => item.duong_dan === duongDan)
  if (!muc || !chuanBiLuu()) return
  duongDanChon.value = duongDan
  nhom.value = muc.nhom
  tuKhoa.value = ''
  chiMauThuan.value = false
  chiThayDoi.value = false
  napBieuMau()
  await nextTick()
  trang.value = Math.floor(mucLoc.value.indexOf(muc) / kichThuoc) + 1
  khungNoiDung.value?.focus()
}

function boSuaMuc() {
  thayDoi.value = thayDoi.value.filter((item) => item.duong_dan !== duongDanChon.value)
  napBieuMau()
}

function moTruongMoi() {
  if (chuanBiLuu()) emit('them-truong', mucChon.value?.duong_dan || '')
}

function chuanBiLuu() {
  if (!choSuaMuc.value || (!daNhapSua.value && !suaTheoDuongDan.value.has(duongDanChon.value))) return true
  const muc = mucChon.value
  let giaTri
  try {
    giaTri = phanTichGiaTri(bieuMau.giaTriJson)
  } catch {
    loi.value = 'Giá trị chỉnh sửa cần đúng cú pháp JSON.'
    return false
  }
  const voiGiaTriMoi = !bangNhau(giaTri, muc.giaTri)
  const doiCanCu = !bangNhau(bieuMau.dan_chung_ids, muc.dan_chung_ids || []) || bieuMau.dan_chung_moi.length > 0
  const ghiChu = bieuMau.ghi_chu.trim()
  if ((voiGiaTriMoi || doiCanCu) && !ghiChu) {
    loi.value = 'Nhập lý do khi thay đổi giá trị hoặc căn cứ.'
    return false
  }
  if (bieuMau.dan_chung_moi.some((item) => !item.nguon_id || !item.vi_tri.trim() || !item.trich_dan.trim())) {
    loi.value = 'Điền đủ tài liệu, vị trí và đoạn trích cho dẫn chứng bổ sung.'
    return false
  }
  const phanConLai = thayDoi.value.filter((item) => item.duong_dan !== muc.duong_dan)
  const duLieu = {
    duong_dan: muc.duong_dan,
    ...(voiGiaTriMoi ? { gia_tri: giaTri } : {}),
    dan_chung_ids: [...bieuMau.dan_chung_ids],
    dan_chung_moi: bieuMau.dan_chung_moi.map((item) => ({
      nguon_id: item.nguon_id, vi_tri: item.vi_tri.trim(), trich_dan: item.trich_dan.trim(), gia_tri: giaTri,
    })),
    ghi_chu: ghiChu,
    da_kiem_tra: bieuMau.da_kiem_tra,
  }
  loi.value = ''
  thayDoi.value = voiGiaTriMoi || doiCanCu || ghiChu !== (muc.ghi_chu || '') || bieuMau.da_kiem_tra !== Boolean(muc.da_kiem_tra)
    ? [...phanConLai, duLieu]
    : phanConLai
  return true
}

defineExpose({ chuanBiLuu, daNhapSua, moDuongDan })
</script>

<style scoped>
.doi-chieu__toolbar { flex-wrap: wrap; }
.doi-chieu__filters { margin-bottom: 16px; }
.doi-chieu { display: grid; grid-template-columns: minmax(230px, 1fr) minmax(300px, 1.6fr); gap: 16px; }
.danh-sach-muc, .dan-chung { list-style: none; margin: 0; padding: 0; }
.danh-sach-muc { display: grid; gap: 6px; margin-bottom: 12px; }
.nut-muc { width: 100%; text-align: left; color: var(--el-text-color-primary); display: grid; gap: 4px; background: var(--el-bg-color); border: 1px solid var(--el-border-color-light); border-radius: 6px; padding: 8px; cursor: pointer; }
.nut-muc:hover, .nut-muc--chon { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.nut-muc__nhan, .dan-chung__dau, .doi-chieu__nut { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 12px; }
.nut-muc__nhan, .dan-chung__dau { justify-content: space-between; }
.nut-muc__gia-tri { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nut-muc small, .chu-thich { color: var(--el-text-color-secondary); overflow-wrap: anywhere; }
.doi-chieu__noi-dung { border: 1px solid var(--el-border-color-light); border-radius: 8px; padding: 16px; min-width: 0; align-self: start; }
.doi-chieu__noi-dung h3 { margin: 0; font-size: 18px; overflow-wrap: anywhere; }
.doi-chieu__noi-dung h4 { font-size: 14px; margin: 0 0 5px; font-weight: 600; }
.duong-dan { margin: 4px 0 12px; color: var(--el-text-color-secondary); overflow-wrap: anywhere; }
.duong-dan summary { cursor: pointer; }
.gia-tri { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-bottom: 12px; }
.gia-tri--truoc { grid-template-columns: 1fr; }
.gia-tri > div { background: var(--el-fill-color-light); border-radius: 6px; padding: 10px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; color: var(--el-text-color-primary); margin: 0; max-height: 180px; overflow-y: auto; }
.dan-chung { display: grid; gap: 8px; }
.dan-chung__the, .dan-chung__them { border: 1px solid var(--el-border-color-light); border-radius: 6px; padding: 12px; overflow-wrap: anywhere; }
.dan-chung__them { margin-bottom: 10px; }
.dan-chung__gia-tri, .chu-thich { margin: 4px 0; }
.dan-chung__lien-ket { display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 12px; }
blockquote { background: var(--el-fill-color-light); border-inline-start: 3px solid var(--el-border-color-darker); margin: 8px 0; padding: 8px 10px; white-space: pre-wrap; }
.doi-chieu__form, .doi-chieu__loi { margin-top: 12px; }
.doi-chieu__nut :deep(.el-button + .el-button) { margin-left: 0; }
.ghi-chu { margin: 12px 0 0; overflow-wrap: anywhere; }
@media (max-width: 860px) {
  .doi-chieu { grid-template-columns: 1fr; }
  .danh-sach-muc { max-height: 240px; overflow-y: auto; }
}
</style>
