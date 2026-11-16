<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="scope">
        <CustomSelect
          v-model="filters.ma_truong"
          class="filter-school"
          placeholder="Trường"
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
          placeholder="Năm học"
          clearable
          @change="onScopeChange"
        >
          <CustomOption v-for="nam in NAM_HOC" :key="nam" :label="nhanNamHoc(nam)" :value="nam" />
        </CustomSelect>
        <CustomSelect
          v-model="filters.de_an_id"
          class="filter-proposal"
          placeholder="Đề án tuyển sinh"
          clearable
          filterable
          :disabled="!filterDeAnReady"
          :loading="deAnLoading"

        >
          <CustomOption
            v-for="item in deAnOptions"
            :key="item.id"
            :label="deAnOptionLabel(item)"
            :value="item.id"
          />
        </CustomSelect>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <ChiTietDeAn v-if="filters.de_an_id" :de-an-id="filters.de_an_id" tab-mac-dinh="dats_chuong_trinh_dao_tao" />
      <CustomEmpty v-else description="Chọn trường hoặc năm, rồi chọn đề án để xem chi tiết đề án." />
    </CustomCard>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchDeAnTuyenSinh } from '@/api/deAnTuyenSinh'
import { fetchTruongHoc } from '@/api/truongHoc'
import { NAM_HOC, laNamHoc, nhanNamHoc } from '@/constants/namHoc'
import ChiTietDeAn from './ChiTietDeAn.vue'

const deAnLoading = ref(false)
const truongOptions = ref([])
const deAnOptions = ref([])
let deAnRequest = 0

const filters = reactive({
  nam_tuyen_sinh: '',
  ma_truong: '',
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

async function loadTruongOptions() {
  const pageSizeOptions = 1000
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchTruongHoc({ page: current, page_size: pageSizeOptions })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  items.sort((a, b) => String(a.ten_truong || '').localeCompare(String(b.ten_truong || ''), 'vi'))
  truongOptions.value = items
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
    ElMessage.error(errorMessage(error, 'Không tải được danh sách đề án tuyển sinh'))
  } finally {
    if (requestId === deAnRequest) deAnLoading.value = false
  }
}

async function onScopeChange() {
  filters.de_an_id = ''
  detail.value = null
  await loadDeAnOptions()
}

onMounted(() => {
  loadTruongOptions().catch(() => {})
})
</script>

<style scoped>
.scope {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.filter-school,
.filter-proposal {
  width: 320px;
}

@media (max-width: 640px) {
  .filter-school,
  .filter-year,
  .filter-proposal {
    width: 100%;
  }
}
</style>
