<template>
  <section class="da-co py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <article class="intro-card">
            <h2 class="h2 mb-2">Bạn đã có ngành nghề mong muốn?</h2>
            <p class="text-secondary mb-0">
              Chọn nhóm ngành nghề, rồi chọn ngành để đối chiếu trường đào tạo, tổ hợp môn và cách xét tuyển.
            </p>
          </article>

          <article class="stages-card mt-3">
            <template v-if="nhomDangXem">
              <button type="button" class="nhom-back mb-3" @click="quayLaiNhom">
                Quay lại nhóm ngành nghề
              </button>
              <h2 class="h4 mb-2">{{ nhomDangXem.ten_nhom }}</h2>
              <p class="text-secondary mb-3">Các ngành thuộc nhóm này. Chọn ngành để xem trường đào tạo.</p>
              <p v-if="loiNganh" class="text-secondary mb-0">{{ loiNganh }}</p>
              <p v-else-if="dangTaiNganh" class="text-secondary mb-0">Đang tải ngành…</p>
              <KhongCoDuLieu v-else-if="!nganhTheoNhom.length" text="Nhóm này chưa có ngành." />
              <div v-else class="row g-3">
                <div v-for="item in nganhTrang" :key="item.id" class="col-12 col-md-6 col-lg-4">
                  <CardNganhDaoTao
                    class="h-100"
                    :ma="item.ma_nganh"
                    :ten="item.ten_nganh"
                    :ten-tieng-anh="item.ten_tieng_anh"
                    :mo-ta="moTaNganh(item)"
                    :hinh-anh="item.hinh_anh_mo_ta || ''"
                    :khoa="item.id"
                    hanh-dong="Chọn"
                    @chon="diChonTruong(item)"
                  />
                </div>
              </div>
              <div v-if="!dangTaiNganh && !loiNganh && nganhTheoNhom.length" class="nhom-pager">
                <CustomPagination
                  v-model:current-page="trangNganh"
                  :page-size="SO_MOI_TRANG"
                  :total="nganhTheoNhom.length"
                  layout="total, prev, pager, next"
                  background
                />
              </div>
            </template>

            <template v-else>
              <h2 class="h4 mb-2">Nhóm ngành nghề</h2>
              <p class="text-secondary mb-3">Bạn định hướng sẽ học ngành nghề nào?</p>
              <p v-if="loiNhom" class="text-secondary mb-0">{{ loiNhom }}</p>
              <p v-else-if="dangTaiNhom" class="text-secondary mb-0">Đang tải nhóm ngành nghề…</p>
              <KhongCoDuLieu v-else-if="!nhomNghe.length" text="Chưa có nhóm ngành nghề." />
              <div v-else class="row g-3">
                <div v-for="item in nhomNghe" :key="item.id" class="col-12 col-md-6 col-lg-4">
                  <CardNganhDaoTao
                    class="h-100"
                    :ma="item.ma_nhom"
                    :ten="item.ten_nhom"
                    :ten-tieng-anh="item.ten_tieng_anh"
                    :mo-ta="moTaHolland(item)"
                    :hinh-anh="item.hinh_anh_mo_ta || ''"
                    :khoa="item.id"
                    hanh-dong="Chọn"
                    @chon="chonNhom(item)"
                  />
                </div>
              </div>
            </template>
          </article>

          <NhacKhaoSat class="mt-3" />
          <HoTroDinhHuong class="mt-3" />
          <CauHoiThuongGap class="mt-3" />
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

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'
import { GIAI_DOAN_THI_DAI_HOC_KEY, giaiDoanThiDaiHocList } from './giaiDoan'
import { routeNameGiaiDoanThiDaiHoc } from '../routes'
import CardNganhDaoTao from './CardNganhDaoTao.vue'
import NhacKhaoSat from './NhacKhaoSat.vue'

defineOptions({ name: 'ThptThiDaiHocDaCo' })

const stages = giaiDoanThiDaiHocList
const route = useRoute()
const router = useRouter()
const currentStage = computed(() => route.meta.giaiDoan || '')

const SO_MOI_TRANG = 8
const nhomNghe = ref([])
const nganh = ref([])
const dangTaiNhom = ref(false)
const dangTaiNganh = ref(false)
const loiNhom = ref('')
const loiNganh = ref('')
const nhomDangXem = ref(null)
const trangNganh = ref(1)

function moTaHolland(item) {
  return item.mo_ta || item.vi_du_nghe_nghiep || ''
}

function maHollandCua(item) {
  const value = item?.ma_holand
  if (Array.isArray(value)) return value.map((code) => String(code).toUpperCase())
  if (typeof value === 'string' && value.trim()) return [value.trim().toUpperCase()]
  return []
}

function moTaNganh(item) {
  if (item.mo_ta) return item.mo_ta
  if (item.ten_nhom_nganh && item.ten_nhom_nganh !== item.ten_nganh) return item.ten_nhom_nganh
  return ''
}

const nganhTheoNhom = computed(() => {
  const ma = String(nhomDangXem.value?.ma_nhom || '').toUpperCase()
  if (!ma) return []
  return nganh.value
    .filter((item) => maHollandCua(item).includes(ma))
    .sort((a, b) => a.ten_nganh.localeCompare(b.ten_nganh, 'vi'))
})

const nganhTrang = computed(() => {
  const batDau = (trangNganh.value - 1) * SO_MOI_TRANG
  return nganhTheoNhom.value.slice(batDau, batDau + SO_MOI_TRANG)
})

function chonNhom(item) {
  nhomDangXem.value = item
  trangNganh.value = 1
}

function quayLaiNhom() {
  nhomDangXem.value = null
}

function diChonTruong(item) {
  router.push({
    name: 'thpt-thi-dai-hoc-chon-truong',
    params: { maNganh: item.ma_nganh },
  })
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

async function taiHetNganh() {
  const pageSize = 200
  let page = 1
  const items = []
  while (page <= 20) {
    const data = await fetchNganh(
      { page, page_size: pageSize, trang_thai: 1 },
      { skipLoading: true },
    )
    items.push(...(data.items || []))
    if (items.length >= (data.total || 0) || !data.items?.length) break
    page += 1
  }
  return items
}

async function taiNhomNghe() {
  dangTaiNhom.value = true
  loiNhom.value = ''
  try {
    const data = await fetchNhomHolland(
      { trang_thai: 1, page: 1, page_size: 100 },
      { skipLoading: true },
    )
    nhomNghe.value = data.items || []
  } catch {
    loiNhom.value = 'Không tải được nhóm ngành nghề.'
  } finally {
    dangTaiNhom.value = false
  }
}

async function taiNganh() {
  dangTaiNganh.value = true
  loiNganh.value = ''
  try {
    nganh.value = await taiHetNganh()
  } catch {
    loiNganh.value = 'Không tải được danh sách ngành.'
  } finally {
    dangTaiNganh.value = false
  }
}

onMounted(() => {
  taiNhomNghe()
  taiNganh()
})
</script>
