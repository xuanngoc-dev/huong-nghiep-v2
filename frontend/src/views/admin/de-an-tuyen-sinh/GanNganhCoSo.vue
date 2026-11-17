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
          :model-value="filters.de_an_id"
          class="filter-proposal"
          placeholder="Đề án tuyển sinh"
          clearable
          filterable
          :disabled="!filterDeAnReady"
          :loading="deAnLoading"
          @update:model-value="onDeAnChange"
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

    <CustomCard v-loading="loading" shadow="never" class="catalog-card">
      <CustomEmpty
        v-if="!filters.de_an_id"
        description="Chọn trường hoặc năm, rồi chọn đề án để gắn ngành và cơ sở cho chương trình."
      />
      <template v-else>
        <div class="toolbar">
          <div class="summary">
            <CustomTag :type="soThieuNganh ? 'warning' : 'success'">
              Thiếu ngành: {{ soThieuNganh }}/{{ rows.length }}
            </CustomTag>
            <CustomTag :type="soThieuCoSo ? 'warning' : 'success'">
              Thiếu cơ sở: {{ soThieuCoSo }}/{{ rows.length }}
            </CustomTag>
            <CustomTag v-if="changedRows.length" type="primary">Chưa lưu: {{ changedRows.length }}</CustomTag>
          </div>
          <div class="toolbar__actions">
            <CustomTooltip
              :content="`Điền ngành gợi ý có độ tin cậy từ ${phanTram(nguongApDung)} cho chương trình chưa có ngành`"
              placement="top"
            >
              <CustomButton :disabled="!soGoiYApDung" @click="apDungGoiY">
                <CustomIcon><MagicStick /></CustomIcon>
                Áp dụng gợi ý ({{ soGoiYApDung }})
              </CustomButton>
            </CustomTooltip>
            <CustomButton type="primary" :disabled="!changedRows.length" :loading="saving" @click="onSave">
              <CustomIcon><Check /></CustomIcon>
              Lưu thay đổi
            </CustomButton>
          </div>
        </div>

        <div class="filters">
          <CustomInput v-model="filters.q" class="filter-q" clearable placeholder="Tìm theo mã xét tuyển hoặc tên chương trình">
            <template #prefix>
              <CustomIcon><Search /></CustomIcon>
            </template>
          </CustomInput>
          <CustomSwitch
            v-model="filters.chiThieu"
            active-text="Chỉ chương trình còn thiếu"
            inactive-text="Tất cả chương trình"
          />
          <div class="bulk">
            <CustomSelect
              v-model="bulkCoSoId"
              class="bulk__select"
              placeholder="Cơ sở cho dòng đã chọn"
              clearable
              :disabled="!coSoOptions.length"
            >
              <CustomOption v-for="item in coSoOptions" :key="item.id" :label="coSoLabel(item)" :value="item.id" />
            </CustomSelect>
            <CustomBadge :value="selectedRows.length" :hidden="!selectedRows.length">
              <CustomButton :disabled="!selectedRows.length || !bulkCoSoId" @click="ganCoSoHangLoat">
                Gán cơ sở
              </CustomButton>
            </CustomBadge>
          </div>
        </div>
        <p v-if="!coSoOptions.length" class="hint">
          Đề án chưa có cơ sở nào. Thêm cơ sở ở trang
          <RouterLink :to="{ name: 'de-an-tuyen-sinh-tru-so' }">Trụ sở</RouterLink> trước khi gắn.
        </p>

        <CustomTable
          ref="tableRef"
          :data="visibleRows"
          row-key="id"
          border
          max-height="640"
          :row-class-name="rowClass"
          @selection-change="(selection) => (selectedRows = selection)"
        >
          <CustomTableColumn type="selection" width="48" align="center" reserve-selection />
          <CustomTableColumn label="TT" width="60" align="center">
            <template #default="{ $index }">{{ $index + 1 }}</template>
          </CustomTableColumn>
          <CustomTableColumn prop="ma_xet_tuyen" label="Mã xét tuyển" width="120" />
          <CustomTableColumn prop="ten_chuong_trinh" label="Tên chương trình" min-width="240" />
          <CustomTableColumn label="Ngành chuẩn" min-width="320">
            <template #default="{ row }">
              <el-select-v2
                v-model="row.form.nganh_dao_tao_id"
                :options="nganhOptions"
                filterable
                clearable
                placeholder="Chọn ngành chuẩn"
                class="cell-select"
              />
              <div v-if="row.goi_y.length && row.form.nganh_dao_tao_id !== row.goi_y[0].nganh_dao_tao_id" class="goi-y">
                <CustomTooltip v-for="g in row.goi_y" :key="g.nganh_dao_tao_id" :content="g.ly_do" placement="top">
                  <button type="button" class="goi-y__chip" @click="row.form.nganh_dao_tao_id = g.nganh_dao_tao_id">
                    {{ g.ten_nganh }} · {{ phanTram(g.diem) }}
                  </button>
                </CustomTooltip>
              </div>
            </template>
          </CustomTableColumn>
          <CustomTableColumn label="Cơ sở" min-width="200">
            <template #default="{ row }">
              <CustomSelect
                v-model="row.form.co_so_id"
                clearable
                placeholder="Chọn cơ sở"
                class="cell-select"
                :disabled="!coSoOptions.length"
              >
                <CustomOption v-for="item in coSoOptions" :key="item.id" :label="coSoLabel(item)" :value="item.id" />
              </CustomSelect>
            </template>
          </CustomTableColumn>
          <CustomTableColumn label="Mã xét tuyển năm trước" width="170">
            <template #default="{ row }">
              <CustomInput
                v-model="row.form.ma_xet_tuyen_nam_truoc"
                maxlength="20"
                placeholder="Nếu trường đổi mã"
              />
            </template>
          </CustomTableColumn>
          <template #empty>
            <CustomEmpty :description="rows.length ? 'Không có chương trình khớp bộ lọc.' : 'Đề án chưa có chương trình.'" />
          </template>
        </CustomTable>
      </template>
    </CustomCard>
  </div>
</template>

<script setup>
/**
 * Gắn ngành chuẩn, cơ sở đào tạo và mã xét tuyển năm trước cho chương trình của một đề án (bước 1.4).
 * Sửa trực tiếp trên bảng, lưu một lần những dòng đã đổi; gợi ý ngành lấy từ API theo tên và mã xét tuyển.
 */
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { baoLoi } from '@/utils/baoLoi'
import { fetchGanNganhCoSo, luuGanNganhCoSo } from '@/api/chuongTrinhDaoTao'
import { fetchDeAnTuyenSinh } from '@/api/deAnTuyenSinh'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchTruSo } from '@/api/truSo'
import { fetchTruongHoc } from '@/api/truongHoc'
import { NAM_HOC, laNamHoc, nhanNamHoc } from '@/constants/namHoc'

defineOptions({ name: 'GanNganhCoSo' })

const loading = ref(false)
const saving = ref(false)
const deAnLoading = ref(false)
const truongOptions = ref([])
const deAnOptions = ref([])
const nganhOptions = ref([])
const coSoOptions = ref([])
const rows = ref([])
const selectedRows = ref([])
const tableRef = ref()
const bulkCoSoId = ref(null)
const nguongApDung = ref(0.85)
let deAnRequest = 0

const filters = reactive({
  ma_truong: '',
  nam_tuyen_sinh: '',
  de_an_id: '',
  q: '',
  chiThieu: false,
})

const filterDeAnReady = computed(() => Boolean(filters.ma_truong) || laNamHoc(filters.nam_tuyen_sinh) != null)

const changedRows = computed(() => rows.value.filter(daDoi))
const soThieuNganh = computed(() => rows.value.filter((row) => !row.form.nganh_dao_tao_id).length)
const soThieuCoSo = computed(() => rows.value.filter((row) => !row.form.co_so_id).length)
const soGoiYApDung = computed(() => rows.value.filter(coGoiYApDung).length)

const visibleRows = computed(() => {
  const tuKhoa = filters.q.trim().toLowerCase()
  return rows.value.filter((row) => {
    if (filters.chiThieu && row.form.nganh_dao_tao_id && row.form.co_so_id) return false
    if (!tuKhoa) return true
    return `${row.ma_xet_tuyen || ''} ${row.ten_chuong_trinh}`.toLowerCase().includes(tuKhoa)
  })
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

function coSoLabel(item) {
  return item.ten_tinh ? `${item.ten_co_so} (${item.ten_tinh})` : item.ten_co_so
}

function phanTram(value) {
  return `${Math.round(Number(value) * 100)}%`
}

function errorMessage(error, fallback) {
  const detailMessage = error?.response?.data?.detail
  if (typeof detailMessage === 'string') return detailMessage
  if (Array.isArray(detailMessage) && detailMessage[0]?.msg) return detailMessage[0].msg
  return fallback
}

function giaTriForm(row) {
  return {
    nganh_dao_tao_id: row.nganh_dao_tao_id ?? null,
    co_so_id: row.co_so_id ?? null,
    ma_xet_tuyen_nam_truoc: row.ma_xet_tuyen_nam_truoc || '',
  }
}

function daDoi(row) {
  const goc = row.goc
  const form = row.form
  return (
    (form.nganh_dao_tao_id ?? null) !== goc.nganh_dao_tao_id ||
    (form.co_so_id ?? null) !== goc.co_so_id ||
    (form.ma_xet_tuyen_nam_truoc || '').trim() !== goc.ma_xet_tuyen_nam_truoc
  )
}

function coGoiYApDung(row) {
  const goiY = row.goi_y[0]
  return !row.form.nganh_dao_tao_id && goiY && goiY.diem >= nguongApDung.value
}

function rowClass({ row }) {
  return daDoi(row) ? 'row--changed' : ''
}

async function loadTruongOptions() {
  const items = []
  for (let page = 1; page <= 20; page += 1) {
    const data = await fetchTruongHoc({ page, page_size: 1000 })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
  }
  items.sort((a, b) => String(a.ten_truong || '').localeCompare(String(b.ten_truong || ''), 'vi'))
  truongOptions.value = items
}

async function loadNganhOptions() {
  const data = await fetchNganh({ page: 1, page_size: 1000 }, { skipLoading: true })
  nganhOptions.value = (data.items || []).map((item) => ({
    value: item.id,
    label: `${item.ma_nganh} — ${item.ten_nganh}`,
  }))
}

async function loadDeAnOptions() {
  const requestId = ++deAnRequest
  const year = laNamHoc(filters.nam_tuyen_sinh)
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

async function loadRows() {
  const deAnId = filters.de_an_id
  rows.value = []
  coSoOptions.value = []
  selectedRows.value = []
  bulkCoSoId.value = null
  tableRef.value?.clearSelection()
  if (!deAnId) return
  loading.value = true
  try {
    const [data, coSo] = await Promise.all([
      fetchGanNganhCoSo({ de_an_id: deAnId, page: 1, page_size: 2000 }, { skipLoading: true }),
      fetchTruSo({ de_an_id: deAnId, page: 1, page_size: 1000 }),
    ])
    if (deAnId !== filters.de_an_id) return
    nguongApDung.value = data.nguong_ap_dung
    coSoOptions.value = coSo.items || []
    rows.value = (data.items || []).map((item) => ({ ...item, goc: giaTriForm(item), form: giaTriForm(item) }))
  } catch (error) {
    baoLoi(errorMessage(error, 'Không tải được chương trình của đề án'))
  } finally {
    loading.value = false
  }
}

// Đổi đề án khi còn thay đổi chưa lưu thì hỏi lại trước.
async function xacNhanBoThayDoi() {
  if (!changedRows.value.length) return true
  try {
    await ElMessageBox.confirm(
      `Có ${changedRows.value.length} chương trình chưa lưu. Bỏ các thay đổi này?`,
      'Thay đổi chưa lưu',
      { type: 'warning', confirmButtonText: 'Bỏ thay đổi', cancelButtonText: 'Ở lại' },
    )
    return true
  } catch {
    return false
  }
}

async function onScopeChange() {
  if (!(await xacNhanBoThayDoi())) return
  filters.de_an_id = ''
  rows.value = []
  await loadDeAnOptions()
}

async function onDeAnChange(value) {
  if (!(await xacNhanBoThayDoi())) return
  filters.de_an_id = value || ''
  await loadRows()
}

function apDungGoiY() {
  const ds = rows.value.filter(coGoiYApDung)
  ds.forEach((row) => {
    row.form.nganh_dao_tao_id = row.goi_y[0].nganh_dao_tao_id
  })
  ElMessage.success(`Đã điền ngành gợi ý cho ${ds.length} chương trình. Kiểm tra lại rồi bấm Lưu thay đổi.`)
}

function ganCoSoHangLoat() {
  selectedRows.value.forEach((row) => {
    row.form.co_so_id = bulkCoSoId.value
  })
  ElMessage.success(`Đã gán cơ sở cho ${selectedRows.value.length} chương trình. Bấm Lưu thay đổi để lưu.`)
  tableRef.value?.clearSelection()
}

async function onSave() {
  const items = changedRows.value.map((row) => ({
    id: row.id,
    nganh_dao_tao_id: row.form.nganh_dao_tao_id || null,
    co_so_id: row.form.co_so_id || null,
    ma_xet_tuyen_nam_truoc: (row.form.ma_xet_tuyen_nam_truoc || '').trim() || null,
  }))
  saving.value = true
  try {
    const result = await luuGanNganhCoSo({ de_an_id: filters.de_an_id, items })
    ElMessage.success(`Đã lưu ${result.updated} chương trình`)
    await loadRows()
  } catch (error) {
    baoLoi(errorMessage(error, 'Không lưu được ngành và cơ sở'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadTruongOptions().catch(() => {})
  loadNganhOptions().catch(() => baoLoi('Không tải được danh mục ngành đào tạo'))
})
</script>

<style scoped>
.scope,
.filters,
.summary,
.bulk {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.filter-school,
.filter-proposal {
  width: 320px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
}

.toolbar__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filters {
  margin-bottom: 12px;
}

.filter-q {
  width: 320px;
}

.bulk {
  margin-left: auto;
}

.bulk__select {
  width: 240px;
}

.hint {
  margin: 0 0 12px;
  color: var(--el-color-warning);
  font-size: 13px;
}

.cell-select {
  width: 100%;
}

.goi-y {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}

.goi-y__chip {
  padding: 2px 8px;
  border: 1px dashed var(--el-color-primary-light-5);
  border-radius: 10px;
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-size: 12px;
  line-height: 18px;
  cursor: pointer;
}

.goi-y__chip:hover {
  border-style: solid;
}

:deep(.row--changed) > td {
  background: var(--el-color-warning-light-9) !important;
}

@media (max-width: 640px) {
  .filter-school,
  .filter-year,
  .filter-proposal,
  .filter-q,
  .bulk,
  .bulk__select {
    width: 100%;
  }

  .bulk {
    margin-left: 0;
  }
}
</style>
