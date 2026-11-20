<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomSelect
          v-model="filters.ma_truong"
          class="filter-school"
          placeholder="Chọn trường"
          clearable
          filterable
          @change="onScopeChange"
        >
          <CustomOption
            v-for="item in truongOptions"
            :key="item.id"
            :label="schoolLabel(item)"
            :value="item.ma_truong"
          />
        </CustomSelect>
        <CustomSelect
          v-model="filters.nam_tuyen_sinh"
          class="filter-year"
          placeholder="Chọn năm học"
          clearable
          @change="onScopeChange"
        >
          <CustomOption v-for="nam in NAM_HOC" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.ma_nganh"
          class="filter-major"
          placeholder="Chọn ngành đào tạo"
          clearable
          filterable
          @change="onNganhChange"
        >
          <CustomOption
            v-for="item in nganhOptions"
            :key="item.id"
            :label="`${item.ma_nganh} — ${item.ten_nganh}`"
            :value="item.ma_nganh"
          />
        </CustomSelect>
        <CustomSelect
          v-model="filters.de_an_id"
          class="filter-proposal"
          :placeholder="deAnPlaceholder"
          clearable
          filterable
          :disabled="!filterDeAnReady"
          :loading="deAnLoading"
          @change="onDeAnChange"
        >
          <CustomOption
            v-for="item in deAnOptions"
            :key="item.id"
            :label="deAnOptionLabel(item)"
            :value="item.id"
          />
        </CustomSelect>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <ChiTietDeAn
        v-if="filters.de_an_id"
        :de-an-id="filters.de_an_id"
        :ma-nganh="filters.ma_nganh || ''"
        tab-mac-dinh="dats_chuong_trinh_dao_tao"
      />
      <div v-else-if="coBoLoc" v-loading="listLoading">
        <p class="scope-caption">
          {{ listTotal }} chương trình khớp bộ lọc<template v-if="listTotal > programs.length">
            (hiển thị {{ programs.length }} chương trình đầu, hãy lọc hẹp hơn)</template
          >. Chọn đề án để xem đầy đủ chi tiết đề án.
        </p>
        <ChuongTrinh
          :key="listKey"
          :programs="programs"
          :methods="methods"
          hien-truong
          @xem-de-an="moChiTiet"
        />
      </div>
      <CustomEmpty
        v-else
        description="Chọn trường, năm học hoặc ngành để xem chương trình và phương thức; chọn đề án để xem chi tiết đề án."
      />
    </CustomCard>

    <ChiTietDeAnDialog v-model="chiTietVisible" :de-an-id="chiTietId" />
  </div>
</template>

<script setup>
/**
 * Chương trình & phương thức: lọc theo trường, năm học, ngành (mã ngành hoặc đầu mã); đề án không bắt buộc.
 * Có đề án: hiển thị như dialog chi tiết đề án. Không có: bảng chương trình gộp các đề án khớp bộ lọc.
 */
import { computed, onMounted, reactive, ref } from 'vue'
import { baoLoi } from '@/utils/baoLoi'
import { fetchChuongTrinhDaoTao } from '@/api/chuongTrinhDaoTao'
import { fetchDeAnTuyenSinh } from '@/api/deAnTuyenSinh'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchTruongHoc } from '@/api/truongHoc'
import { NAM_HOC, laNamHoc, nhanNamHoc } from '@/constants/namHoc'
import ChiTietDeAn from './ChiTietDeAn.vue'
import ChiTietDeAnDialog from './ChiTietDeAnDialog.vue'
import ChuongTrinh from './chi-tiet/ChuongTrinh.vue'

// Bảng gộp không phân trang: tối đa chừng này chương trình mỗi lần lọc.
const SO_CHUONG_TRINH_TOI_DA = 1000

const deAnLoading = ref(false)
const listLoading = ref(false)
const truongOptions = ref([])
const nganhOptions = ref([])
const deAnOptions = ref([])
const listItems = ref([])
const listTotal = ref(0)
const listKey = ref(0)
const chiTietVisible = ref(false)
const chiTietId = ref(null)
let deAnRequest = 0
let listRequest = 0

const filters = reactive({
  nam_tuyen_sinh: '',
  ma_truong: '',
  ma_nganh: '',
  de_an_id: '',
})

function schoolLabel(school) {
  if (!school) return ''
  return school.ma_truong ? `${school.ma_truong} — ${school.ten_truong}` : school.ten_truong
}

function deAnOptionLabel(item) {
  if (!item) return ''
  const name = item.ten_de_an || `Đề án #${item.id}`
  return [schoolLabel(item), item.nam_tuyen_sinh, name].filter((part) => part != null && part !== '').join(' · ')
}

function errorMessage(error, fallback) {
  const detailMessage = error?.response?.data?.detail
  if (typeof detailMessage === 'string') return detailMessage
  if (Array.isArray(detailMessage) && detailMessage[0]?.msg) return detailMessage[0].msg
  return fallback
}

function yearFilter() {
  return laNamHoc(filters.nam_tuyen_sinh)
}

const filterDeAnReady = computed(() => Boolean(filters.ma_truong) || yearFilter() != null)
const coBoLoc = computed(() => filterDeAnReady.value || Boolean(filters.ma_nganh))
const deAnPlaceholder = computed(() => {
  if (!filterDeAnReady.value) return 'Chọn trường hoặc năm để chọn đề án'
  if (!deAnLoading.value && !deAnOptions.value.length) return 'Không có đề án phù hợp'
  return 'Chọn đề án tuyển sinh (không bắt buộc)'
})

// Dữ liệu cho bảng gộp: mỗi chương trình nối với phương thức của nó bằng khóa riêng.
const programs = computed(() =>
  listItems.value.map((item) => ({
    ...item,
    row_key: String(item.id),
    chuong_trinh_key: String(item.id),
    ma_nganh_hien_thi: item.ma_nganh || (item.ma_nganh_chuan || []).join(', '),
  })),
)
const methods = computed(() =>
  listItems.value.flatMap((item) =>
    (item.phuong_thuc || []).map((method) => ({ ...method, chuong_trinh_key: String(item.id) })),
  ),
)

async function loadAll(fetchFn) {
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchFn({ page: current, page_size: 1000 })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  return items
}

async function loadTruongOptions() {
  const items = await loadAll(fetchTruongHoc)
  items.sort((a, b) => String(a.ten_truong || '').localeCompare(String(b.ten_truong || ''), 'vi'))
  truongOptions.value = items
}

async function loadNganhOptions() {
  const items = await loadAll((params) => fetchNganh(params))
  items.sort((a, b) => String(a.ma_nganh || '').localeCompare(String(b.ma_nganh || ''), 'vi', { numeric: true }))
  nganhOptions.value = items
}

async function loadDeAnOptions() {
  const requestId = ++deAnRequest
  const year = yearFilter()
  if (!filters.ma_truong && year == null) {
    deAnOptions.value = []
    return
  }
  deAnLoading.value = true
  try {
    const params = { page: 1, page_size: 1000 }
    if (filters.ma_truong) params.ma_truong = filters.ma_truong
    if (year != null) params.nam_tuyen_sinh = year
    const data = await fetchDeAnTuyenSinh(params)
    if (requestId !== deAnRequest) return
    deAnOptions.value = data.items || []
  } catch (error) {
    if (requestId !== deAnRequest) return
    deAnOptions.value = []
    baoLoi(errorMessage(error, 'Không tải được danh sách đề án tuyển sinh'))
  } finally {
    if (requestId === deAnRequest) deAnLoading.value = false
  }
}

async function loadList() {
  const requestId = ++listRequest
  if (filters.de_an_id || !coBoLoc.value) {
    listItems.value = []
    listTotal.value = 0
    return
  }
  listLoading.value = true
  try {
    const params = { page: 1, page_size: SO_CHUONG_TRINH_TOI_DA, kem_phuong_thuc: true }
    if (filters.ma_truong) params.ma_truong = filters.ma_truong
    if (yearFilter() != null) params.nam_tuyen_sinh = yearFilter()
    if (filters.ma_nganh) params.ma_nganh = filters.ma_nganh
    const data = await fetchChuongTrinhDaoTao(params)
    if (requestId !== listRequest) return
    listItems.value = data.items || []
    listTotal.value = data.total || 0
    // Làm mới bộ lọc bên trong bảng khi đổi phạm vi.
    listKey.value += 1
  } catch (error) {
    if (requestId !== listRequest) return
    listItems.value = []
    listTotal.value = 0
    baoLoi(errorMessage(error, 'Không tải được chương trình và phương thức'))
  } finally {
    if (requestId === listRequest) listLoading.value = false
  }
}

async function onScopeChange() {
  filters.de_an_id = ''
  await Promise.all([loadDeAnOptions(), loadList()])
}

function onNganhChange() {
  loadList()
}

function onDeAnChange() {
  loadList()
}

function moChiTiet(deAnId) {
  chiTietId.value = deAnId
  chiTietVisible.value = true
}

onMounted(() => {
  loadTruongOptions().catch(() => {})
  loadNganhOptions().catch(() => {})
})
</script>

<style scoped>
.scope-caption {
  margin: 0 0 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

</style>
