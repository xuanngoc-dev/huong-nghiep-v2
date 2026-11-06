<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchNhomNganh } from '@/api/nhomNganhDaoTao'
import { GIAI_DOAN_THI_DAI_HOC_KEY, giaiDoanThiDaiHocList } from './giaiDoan'
import { routeNameGiaiDoanThiDaiHoc } from '../routes'
import CardNganhDaoTao from './CardNganhDaoTao.vue'
import NhacKhaoSat from './NhacKhaoSat.vue'

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
            <header class="holland-overview__header" v-if="false">
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
                  <CardNganhDaoTao
                    class="h-100"
                    :ma="item.ma_nganh"
                    :nhan="item.trinh_do"
                    :ten="item.ten_nganh"
                    :ten-tieng-anh="item.ten_tieng_anh"
                    :mo-ta="item.mo_ta || ''"
                    :hinh-anh="item.hinh_anh_mo_ta || ''"
                    :khoa="item.id"
                    hanh-dong="Chọn"
                    @chon="diChonTruong(item)"
                  />
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
              <div v-for="item in ketQuaTrang" :key="item.id" class="col-12 col-md-6 col-lg-4">
                <CardNganhDaoTao
                  class="h-100"
                  :ma="item.ma_nhom_nganh"
                  :nhan="item.ten_linh_vuc"
                  :ten="item.ten_nhom_nganh"
                  :ten-tieng-anh="item.ten_tieng_anh"
                  :mo-ta="item.mo_ta || ''"
                  :hinh-anh="item.hinh_anh_mo_ta || ''"
                  :khoa="item.id"
                  :hanh-dong="`${item.so_nganh || 0} Ngành`"
                  @chon="xemNganh(item)"
                />
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
          <NhacKhaoSat class="mt-3" />
          <!-- Hỗ trợ & FAQ -->
          <HoTroDinhHuong class="mt-3" />
          <CauHoiThuongGap class="mt-3" />
          <!-- /Hỗ trợ & FAQ -->
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
