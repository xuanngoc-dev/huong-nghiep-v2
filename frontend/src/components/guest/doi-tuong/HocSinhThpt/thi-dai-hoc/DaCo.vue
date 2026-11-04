<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchNhomNganh } from '@/api/nhomNganhDaoTao'
import { GIAI_DOAN_THI_DAI_HOC_KEY, giaiDoanThiDaiHocList } from './giaiDoan'
import { routeNameGiaiDoanThiDaiHoc } from '../routes'

defineOptions({ name: 'ThptThiDaiHocDaCo' })

const stages = giaiDoanThiDaiHocList
const route = useRoute()
const router = useRouter()
const currentStage = computed(() => route.meta.giaiDoan || '')

const danhSach = ref([])
const dangTai = ref(false)
const loi = ref('')
const SO_MOI_TRANG = 8

const ten = ref('')
const maLinhVuc = ref('')
const boLoc = ref({ ten: '', maLinhVuc: '' })
const trang = ref(1)
const nhomDangXem = ref(null)
const nganh = ref([])
const dangTaiNganh = ref(false)
const loiNganh = ref('')
const trangNganh = ref(1)

const linhVucOptions = computed(() => {
  const map = new Map()
  for (const item of danhSach.value) {
    if (!map.has(item.ma_linh_vuc)) map.set(item.ma_linh_vuc, item.ten_linh_vuc)
  }
  return [...map.entries()]
    .map(([ma, tenLinhVuc]) => ({ ma, ten: tenLinhVuc }))
    .sort((a, b) => a.ten.localeCompare(b.ten, 'vi'))
})

const ketQua = computed(() => {
  const tuKhoa = boLoc.value.ten.toLocaleLowerCase('vi')
  const ma = boLoc.value.maLinhVuc
  return danhSach.value.filter((item) => {
    if (ma && item.ma_linh_vuc !== ma) return false
    if (!tuKhoa) return true
    return item.ten_nhom_nganh.toLocaleLowerCase('vi').includes(tuKhoa)
  })
})

const ketQuaTrang = computed(() => {
  const batDau = (trang.value - 1) * SO_MOI_TRANG
  return ketQua.value.slice(batDau, batDau + SO_MOI_TRANG)
})

const nganhTrang = computed(() => {
  const batDau = (trangNganh.value - 1) * SO_MOI_TRANG
  return nganh.value.slice(batDau, batDau + SO_MOI_TRANG)
})

function timKiem() {
  boLoc.value = {
    ten: ten.value.trim(),
    maLinhVuc: maLinhVuc.value || '',
  }
  trang.value = 1
}

function diChonTruong(item) {
  router.push({
    name: 'thpt-thi-dai-hoc-chon-truong',
    params: { maNganh: item.ma_nganh },
  })
}

async function xemNganh(nhom) {
  nhomDangXem.value = nhom
  trangNganh.value = 1
  dangTaiNganh.value = true
  loiNganh.value = ''
  nganh.value = []
  try {
    const pageSize = 200
    let page = 1
    const items = []
    while (page <= 20) {
      const data = await fetchNganh(
        { page, page_size: pageSize, trang_thai: 1, ma_nhom_nganh: nhom.ma_nhom_nganh },
        { skipLoading: true },
      )
      items.push(...(data.items || []))
      if (items.length >= (data.total || 0) || !data.items?.length) break
      page += 1
    }
    items.sort((a, b) => a.ten_nganh.localeCompare(b.ten_nganh, 'vi'))
    nganh.value = items
  } catch {
    loiNganh.value = 'Không tải được danh sách ngành.'
  } finally {
    dangTaiNganh.value = false
  }
}

function quayLaiNhom() {
  nhomDangXem.value = null
  nganh.value = []
  loiNganh.value = ''
}

function chonGiaiDoan(stage) {
  sessionStorage.setItem(GIAI_DOAN_THI_DAI_HOC_KEY, stage.code)
  const name = routeNameGiaiDoanThiDaiHoc(stage.code)
  if (name && name !== route.name) {
    router.push({ name })
    return
  }
  if (!name) router.push({ name: 'thpt-thi-dai-hoc' })
}

async function taiNhomNganh() {
  dangTai.value = true
  loi.value = ''
  try {
    const pageSize = 200
    let page = 1
    const items = []
    while (page <= 20) {
      const data = await fetchNhomNganh(
        { page, page_size: pageSize, trang_thai: 1 },
        { skipLoading: true },
      )
      items.push(...(data.items || []))
      if (items.length >= (data.total || 0) || !data.items?.length) break
      page += 1
    }
    items.sort((a, b) => a.ten_nhom_nganh.localeCompare(b.ten_nhom_nganh, 'vi'))
    danhSach.value = items
  } catch {
    loi.value = 'Không tải được danh sách nhóm ngành.'
  } finally {
    dangTai.value = false
  }
}

onMounted(taiNhomNganh)
</script>

<template>
  <section class="da-co py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <article class="intro-card">
            <h2 class="h2 mb-2">Bạn đã có ngành nghề mong muốn?</h2>
            <p class="text-secondary mb-0">
              Chọn nhóm ngành, rồi đối chiếu trường đào tạo, tổ hợp môn và cách xét tuyển.
            </p>
          </article>

          <div class="stages-card holland-overview mt-3">
            <header class="holland-overview__header">
              <h2 class="holland-overview__title">
                {{ nhomDangXem ? nhomDangXem.ten_nhom_nganh : 'Nhóm ngành đào tạo' }}
              </h2>
              <p class="holland-overview__lead">
                {{
                  nhomDangXem
                    ? 'Các ngành thuộc nhóm này.'
                    : 'Lọc theo tên nhóm ngành và lĩnh vực.'
                }}
              </p>
            </header>

            <button v-if="nhomDangXem" type="button" class="nhom-back" @click="quayLaiNhom">
              Quay lại nhóm ngành
            </button>

            <form v-else class="nhom-filter" @submit.prevent="timKiem">
              <div class="nhom-filter__field nhom-filter__field--ten">
                <label class="nhom-filter__label" for="loc-ten-nhom">Tên</label>
                <CustomInput
                  id="loc-ten-nhom"
                  v-model="ten"
                  placeholder="Nhập tên nhóm ngành"
                  clearable
                />
              </div>
              <div class="nhom-filter__field nhom-filter__field--linh-vuc">
                <label class="nhom-filter__label" for="loc-linh-vuc">Lĩnh vực</label>
                <CustomSelect
                  id="loc-linh-vuc"
                  v-model="maLinhVuc"
                  class="nhom-filter__select"
                  filterable
                  placeholder="Tất cả lĩnh vực"
                >
                  <CustomOption
                    v-for="item in linhVucOptions"
                    :key="item.ma"
                    :label="item.ten"
                    :value="item.ma"
                  />
                </CustomSelect>
              </div>
              <button type="submit" class="btn btn-success btn-sm nhom-filter__submit">Tìm kiếm</button>
            </form>

            <template v-if="nhomDangXem">
              <p v-if="loiNganh" class="holland-note holland-note__text">{{ loiNganh }}</p>
              <p v-else-if="dangTaiNganh" class="holland-overview__lead text-center">Đang tải ngành…</p>
              <p v-else-if="!nganh.length" class="holland-note holland-note__text">
                Nhóm này chưa có ngành.
              </p>
              <div v-else class="row g-3">
                <div v-for="item in nganhTrang" :key="item.id" class="col-12 col-md-6 col-lg-3">
                  <article class="nhom-card h-100">
                    <p class="nhom-card__code">{{ item.ma_nganh }}</p>
                    <div class="nhom-card__main">
                      <p class="nhom-card__field">{{ item.trinh_do }}</p>
                      <h3 class="nhom-card__name">{{ item.ten_nganh }}</h3>
                      <p class="nhom-card__en">{{ item.ten_tieng_anh }}</p>
                      <p v-if="item.mo_ta" class="nhom-card__text">{{ item.mo_ta }}</p>
                    </div>
                    <button type="button" class="nhom-card__majors" @click="diChonTruong(item)">
                      Chọn
                    </button>
                  </article>
                </div>
              </div>
              <div v-if="!dangTaiNganh && !loiNganh && nganh.length" class="nhom-pager">
                <CustomPagination
                  v-model:current-page="trangNganh"
                  :page-size="SO_MOI_TRANG"
                  :total="nganh.length"
                  layout="total, prev, pager, next"
                  background
                />
              </div>
            </template>

            <p v-else-if="loi" class="holland-note holland-note__text">{{ loi }}</p>
            <p v-else-if="dangTai" class="holland-overview__lead text-center">Đang tải nhóm ngành…</p>
            <p v-else-if="!ketQua.length" class="holland-note holland-note__text">
              Không có nhóm ngành khớp bộ lọc.
            </p>
            <div v-else class="row g-3">
              <div v-for="item in ketQuaTrang" :key="item.id" class="col-12 col-md-6 col-lg-3">
                <article class="nhom-card h-100">
                  <p class="nhom-card__code">{{ item.ma_nhom_nganh }}</p>
                  <div class="nhom-card__main">
                    <p class="nhom-card__field">{{ item.ten_linh_vuc }}</p>
                    <h3 class="nhom-card__name">{{ item.ten_nhom_nganh }}</h3>
                    <p class="nhom-card__en">{{ item.ten_tieng_anh }}</p>
                    <p v-if="item.mo_ta" class="nhom-card__text">{{ item.mo_ta }}</p>
                  </div>
                  <button type="button" class="nhom-card__majors" @click="xemNganh(item)">
                    {{ item.so_nganh || 0 }} Ngành
                  </button>
                </article>
              </div>
            </div>
            <div v-if="!nhomDangXem && !dangTai && !loi && ketQua.length" class="nhom-pager">
              <CustomPagination
                v-model:current-page="trang"
                :page-size="SO_MOI_TRANG"
                :total="ketQua.length"
                layout="total, prev, pager, next"
                background
              />
            </div>
          </div>
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="chon-lai-giai-doan" class="h4 mb-3">Chọn lại giai đoạn</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-giai-doan">
              <button
                v-for="stage in stages"
                :key="stage.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': currentStage === stage.code }"
                @click="chonGiaiDoan(stage)"
              >
                <img class="switch-card__image" :src="stage.image" :alt="stage.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">{{ stage.name }}</span>
                  <span class="switch-card__text">{{ stage.description }}</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.da-co :is(.h2, .h4, .holland-overview__title, .switch-card__name, .nhom-filter__submit) {
  font-weight: 400;
}

.nhom-back {
  align-self: flex-start;
  border: 0;
  padding: 0;
  background: transparent;
  color: var(--guest-primary);
  font: inherit;
  font-weight: 400;
  cursor: pointer;
}

.nhom-back:hover {
  text-decoration: underline;
}

.nhom-filter {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 8px;
}

.nhom-filter__field--ten {
  flex: 1 1 180px;
  max-width: 240px;
}

.nhom-filter__field--linh-vuc {
  flex: 1 1 160px;
  max-width: 220px;
}

.nhom-filter__label {
  display: block;
  margin-bottom: 4px;
  color: #5c6b62;
  font-size: 0.75rem;
  font-weight: 400;
}

.nhom-filter__select {
  width: 100%;
}

.nhom-filter__submit {
  height: 32px;
  padding-inline: 12px;
}

@media (max-width: 767.98px) {
  .nhom-filter__field--ten,
  .nhom-filter__field--linh-vuc,
  .nhom-filter__submit {
    flex-basis: 100%;
    max-width: none;
  }
}

.nhom-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  padding: 16px;
  overflow: hidden;
  border: 2px solid #7eae8c;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(31, 122, 77, 0.16);
}

.nhom-card__main {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  padding-right: 28px;
}

.nhom-card__code {
  position: absolute;
  top: 5px;
  right: -45px;
  z-index: 1;
  width: 118px;
  margin: 0;
  padding: 4px 0;
  background: var(--guest-primary);
  box-shadow: 0 2px 6px rgba(28, 43, 35, 0.2);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 400;
  letter-spacing: 0.04em;
  line-height: 1.2;
  text-align: center;
  transform: rotate(45deg);
}

.nhom-card__majors {
  align-self: flex-end;
  border: 0;
  border-radius: 8px;
  padding: 6px 12px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.8125rem;
  font-weight: 400;
  line-height: 1.2;
  cursor: pointer;
}

.nhom-card__majors:hover {
  background: var(--guest-primary-hover);
}

.nhom-card__field {
  margin: 0;
  color: var(--guest-primary);
  font-size: 0.78rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  line-height: 1.35;
  text-transform: uppercase;
}

.nhom-card__name {
  margin: 0;
  color: #1c2b23;
  font-size: 1.15rem;
  font-weight: 400;
  line-height: 1.35;
}

.nhom-card__en,
.nhom-card__text {
  margin: 0;
  color: #5c6b62;
  line-height: 1.45;
}

.nhom-card__text {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.nhom-pager {
  display: flex;
  justify-content: flex-end;
}

.nhom-pager :deep(.el-pagination) {
  font-weight: 400;
}
</style>
