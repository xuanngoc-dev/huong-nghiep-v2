<template>
  <div class="kq-nghe">
    <section>
      <header class="kq-section-head">
        <h3 class="kq-section-title">Nghề nghiệp phù hợp</h3>
        <p class="kq-muted">Ví dụ nghề theo các nhóm sở thích nổi bật; mức phù hợp thực tế còn tùy năng lực và điều kiện của bạn.</p>
      </header>
      <div v-if="ngheTheoNhom.length" class="row g-3">
        <div v-for="nhom in ngheTheoNhom" :key="nhom.ma_nhom" class="col-12 col-lg-4">
          <article class="kq-card kq-job">
            <h4 class="kq-job__name"><span class="kq-tag">{{ nhom.ma_nhom }}</span>{{ nhom.ten_nhom }}</h4>
            <p class="kq-job__text">{{ nhom.mo_ta }}</p>
            <ul class="kq-chips">
              <li v-for="ten in nhom.nghe" :key="ten" class="kq-chip kq-chip--plain">{{ ten }}</li>
            </ul>
          </article>
        </div>
      </div>
      <p v-else class="kq-muted">Chưa có ví dụ nghề cho các nhóm này.</p>
    </section>

    <section>
      <header class="kq-section-head kq-section-head--row">
        <div>
          <h3 class="kq-section-title">Ngành đào tạo phù hợp</h3>
          <p class="kq-muted">Xếp theo mức khớp với mã Holland {{ maNoiBat }}.</p>
        </div>
        <RouterLink class="kq-link" :to="{ name: 'thpt-thi-dai-hoc-nganh-phu-hop', params: { ssid }, query: routeQuery }">
          Xem tất cả và so sánh ngành
        </RouterLink>
      </header>
      <p v-if="loiNganh" class="kq-muted">{{ loiNganh }}</p>
      <p v-else-if="dangTaiNganh" class="kq-muted">Đang tải ngành phù hợp…</p>
      <p v-else-if="!nganh.length" class="kq-muted">Chưa có ngành đào tạo khớp kết quả của bạn.</p>
      <div v-else class="row g-3">
        <div v-for="item in nganhHien" :key="item.ma_nganh" class="col-12 col-md-6 col-xl-3">
          <article class="kq-card kq-major">
            <p class="kq-major__code">{{ item.ma_nganh }} · {{ item.ten_nhom_nganh }}</p>
            <h4 class="kq-major__name">{{ item.ten_nganh }}</h4>
            <p class="kq-major__tags">
              <span
                v-for="ma in item.ma_holand"
                :key="ma"
                class="kq-tag"
                :class="{ 'kq-tag--muted': !maTop.has(ma) }"
              >{{ ma }}</span>
            </p>
            <div class="kq-actions">
              <RouterLink
                class="btn btn-sm btn-outline-success"
                :to="{ name: 'thpt-thi-dai-hoc-chi-tiet-nganh', params: { ssid, maNganh: item.ma_nganh }, query: routeQuery }"
              >
                Tìm hiểu
              </RouterLink>
              <button
                type="button"
                class="btn btn-sm"
                :class="laQuanTam('nganh', item.ma_nganh) ? 'btn-success' : 'btn-light'"
                :aria-pressed="laQuanTam('nganh', item.ma_nganh)"
                @click="emit('doi-quan-tam', 'nganh', { ma_nganh: item.ma_nganh, ten_nganh: item.ten_nganh })"
              >
                {{ laQuanTam('nganh', item.ma_nganh) ? 'Đã quan tâm' : 'Quan tâm' }}
              </button>
            </div>
          </article>
        </div>
      </div>
      <button v-if="nganh.length > soNganhHien" type="button" class="kq-more" @click="soNganhHien += SO_NGANH">
        Xem thêm ngành
      </button>
    </section>

    <section>
      <header class="kq-section-head kq-section-head--row">
        <div>
          <h3 class="kq-section-title">Trường đào tạo phù hợp</h3>
          <p class="kq-muted">Trường có đào tạo ngành đang chọn trong năm {{ NAM }}.</p>
        </div>
        <CustomSelect v-model="maNganhTruong" class="kq-select" filterable placeholder="Chọn ngành để xem trường">
          <CustomOption v-for="item in luaChonNganh" :key="item.ma_nganh" :label="`${item.ma_nganh} — ${item.ten_nganh}`" :value="item.ma_nganh" />
        </CustomSelect>
      </header>
      <p v-if="!maNganhTruong" class="kq-muted">Chọn một ngành để xem trường đào tạo.</p>
      <p v-else-if="loiTruong" class="kq-muted">{{ loiTruong }}</p>
      <p v-else-if="dangTaiTruong" class="kq-muted">Đang tải trường đào tạo…</p>
      <p v-else-if="!truong.length" class="kq-muted">Chưa có dữ liệu trường đào tạo ngành này năm {{ NAM }}.</p>
      <div v-else class="row g-3">
        <div v-for="item in truong" :key="item.ma_truong" class="col-12 col-md-6 col-xl-4">
          <article class="kq-card kq-school">
            <div class="kq-school__body">
              <h4 class="kq-school__name">{{ item.ten_truong }}</h4>
              <p class="kq-muted">{{ [item.ma_truong, item.ten_tinh].filter(Boolean).join(' · ') }}</p>
            </div>
            <div class="kq-actions">
              <RouterLink
                class="btn btn-sm btn-outline-success"
                :to="{
                  name: 'thpt-thi-dai-hoc-chi-tiet-truong',
                  params: { ssid, maTruong: item.ma_truong },
                  query: { ...routeQuery, ma_nganh: maNganhTruong, nam: String(NAM) },
                }"
              >
                Chi tiết
              </RouterLink>
              <button
                type="button"
                class="btn btn-sm"
                :class="laQuanTam('truong', item.ma_truong) ? 'btn-success' : 'btn-light'"
                :aria-pressed="laQuanTam('truong', item.ma_truong)"
                @click="emit('doi-quan-tam', 'truong', { ma_truong: item.ma_truong, ten_truong: item.ten_truong, ma_nganh: maNganhTruong })"
              >
                {{ laQuanTam('truong', item.ma_truong) ? 'Đã quan tâm' : 'Quan tâm' }}
              </button>
            </div>
          </article>
        </div>
      </div>
      <div v-if="maNganhTruong" class="kq-actions kq-actions--end">
        <span class="kq-muted">Muốn biết khả năng trúng tuyển theo điểm của mình?</span>
        <RouterLink class="btn btn-success" :to="{ name: 'thpt-thi-dai-hoc-truong-phu-hop', params: { maNganh: maNganhTruong } }">
          Tìm trường phù hợp
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { fetchTruongTheoNganh } from '@/api/nganhHocTheoTruong'
import { ngheGoiY } from '@/utils/ketQuaHolland'

const props = defineProps({
  ssid: { type: String, required: true },
  top: { type: Array, default: () => [] },
  maNoiBat: { type: String, default: '' },
  danhMucNhom: { type: Array, default: () => [] },
  nganh: { type: Array, default: () => [] },
  dangTaiNganh: { type: Boolean, default: false },
  loiNganh: { type: String, default: '' },
  quanTam: { type: Object, required: true },
  routeQuery: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['doi-quan-tam'])

const SO_NGANH = 8
const SO_TRUONG = 6
const NAM = new Date().getFullYear()

const soNganhHien = ref(SO_NGANH)
const maNganhTruong = ref('')
const truong = ref([])
const dangTaiTruong = ref(false)
const loiTruong = ref('')
let lanTai = 0

// Nghề gộp theo nhóm sở thích: mỗi nhóm một thẻ có mô tả chung và các nghề ví dụ.
const ngheTheoNhom = computed(() => {
  const nghe = ngheGoiY(props.top, props.danhMucNhom, 6)
  return props.top
    .map((item) => {
      const cuaNhom = nghe.filter((x) => x.ma_nhom === item.ma_nhom)
      return { ma_nhom: item.ma_nhom, ten_nhom: item.ten_nhom, mo_ta: cuaNhom[0]?.mo_ta || '', nghe: cuaNhom.map((x) => x.ten) }
    })
    .filter((nhom) => nhom.nghe.length)
})
const maTop = computed(() => new Set(props.top.map((item) => item.ma_nhom)))
const nganhHien = computed(() => props.nganh.slice(0, soNganhHien.value))
// Ngành để xem trường: ngành đã quan tâm trước, rồi các ngành phù hợp nhất.
const luaChonNganh = computed(() => {
  const ds = [...props.quanTam.nganh, ...props.nganh.slice(0, 20)]
  const daCo = new Set()
  return ds.filter((item) => item.ma_nganh && !daCo.has(item.ma_nganh) && daCo.add(item.ma_nganh))
})

function laQuanTam(loai, ma) {
  const khoa = loai === 'nganh' ? 'ma_nganh' : 'ma_truong'
  return props.quanTam[loai].some((item) => item[khoa] === ma)
}

async function taiTruong(ma) {
  const lan = ++lanTai
  truong.value = []
  loiTruong.value = ''
  if (!ma) return
  dangTaiTruong.value = true
  try {
    const data = await fetchTruongTheoNganh(
      { ma_nganh: ma, nam_tuyen_sinh: NAM, page: 1, page_size: SO_TRUONG },
      { skipLoading: true },
    )
    if (lan === lanTai) truong.value = data.items || []
  } catch {
    if (lan === lanTai) loiTruong.value = 'Không tải được trường đào tạo.'
  } finally {
    if (lan === lanTai) dangTaiTruong.value = false
  }
}

watch(
  luaChonNganh,
  (ds) => {
    if (!maNganhTruong.value && ds.length) maNganhTruong.value = ds[0].ma_nganh
  },
  { immediate: true },
)
watch(maNganhTruong, taiTruong, { immediate: true })
</script>

<style scoped src="./ket-qua.css"></style>
