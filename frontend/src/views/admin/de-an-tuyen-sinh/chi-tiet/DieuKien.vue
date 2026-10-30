<script setup>
import { computed, reactive } from 'vue'
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'
import { STATUS_LABELS } from './format'

const props = defineProps({
  rows: { type: Array, default: () => [] },
})

const NONE = '__none__'

const LOAI_LABELS = {
  bat_buoc: 'Nhóm bắt buộc',
  ngoai_ngu: 'Ngoại ngữ',
  quy_tac_ngoai_ngu: 'Quy tắc ngoại ngữ',
}

const LOAI_ORDER = ['bat_buoc', 'ngoai_ngu', 'quy_tac_ngoai_ngu']

const BAT_BUOC_LABELS = {
  '1': 'Có',
  '0': 'Không',
  [NONE]: 'Chưa xác định',
}

const OPERATOR_ORDER = ['<', '<=', '=', '==', '>=', '>', '!=', '<>']

const STATUS_ORDER = ['nhap', 'cong_bo', 'het_hieu_luc']

const { chuongTrinh, phuongThuc, ghiChu, trangThai, nguon } = cotChung()

const columns = [
  col('ma_dieu_kien', 'Mã', { width: 130, align: 'center' }),
  col('ten_dieu_kien', 'Tên điều kiện', { minWidth: 220 }),
  col('loai_dieu_kien', 'Loại', { width: 170, minWidth: 150, type: 'code', labels: LOAI_LABELS }),
  col('noi_dung_dieu_kien', 'Nội dung', { minWidth: 260 }),
  col('doi_tuong', 'Đối tượng', { minWidth: 200 }),
  chuongTrinh,
  phuongThuc,
  col('toan_tu_so_sanh', 'Toán tử', { width: 110, align: 'center' }),
  col('gia_tri_dieu_kien', 'Giá trị', { minWidth: 160 }),
  col('bat_buoc', 'Bắt buộc', { width: 110, align: 'center', type: 'bool' }),
  col('minh_chung_can_nop', 'Minh chứng', { minWidth: 200 }),
  col('thu_tu_kiem_tra', 'Thứ tự', { width: 90, align: 'center' }),
  nguon,
  trangThai,
  ghiChu,
]

const filters = reactive({
  chuongTrinh: [],
  phuongThuc: [],
  doiTuong: [],
  loai: [],
  batBuoc: [],
  toanTu: [],
  trangThai: [],
})

function text(value) {
  return String(value ?? '').trim()
}

function byLabel(a, b) {
  return a.label.localeCompare(b.label, 'vi')
}

function withNone(options, label) {
  if (!options.some((option) => option.value === NONE)) return options
  const rest = options.filter((option) => option.value !== NONE)
  if (!rest.length) return []
  return [{ value: NONE, label }, ...rest]
}

function scopeOptions(key) {
  const options = []
  const seen = new Set()
  for (const row of props.rows) {
    const value = text(row[key]) || NONE
    if (seen.has(value)) continue
    seen.add(value)
    options.push({
      value,
      label: value === NONE ? 'Áp dụng chung' : value,
    })
  }
  const named = options.filter((option) => option.value !== NONE).sort(byLabel)
  return withNone(named.concat(options.filter((option) => option.value === NONE)), 'Áp dụng chung')
}

function codedOptions(key, labels, order = []) {
  const options = []
  const seen = new Set()
  for (const row of props.rows) {
    const value = text(row[key]) || NONE
    if (seen.has(value)) continue
    seen.add(value)
    options.push({
      value,
      label: value === NONE ? '' : labels[value] || value,
    })
  }
  const rank = new Map(order.map((value, index) => [value, index]))
  options.sort((a, b) => {
    const aRank = rank.has(a.value) ? rank.get(a.value) : order.length
    const bRank = rank.has(b.value) ? rank.get(b.value) : order.length
    if (aRank !== bRank) return aRank - bRank
    return (labels[a.value] || a.value).localeCompare(labels[b.value] || b.value, 'vi')
  })
  return options
}

function loaiOptions() {
  return withNone(codedOptions('loai_dieu_kien', LOAI_LABELS, LOAI_ORDER), 'Chưa phân loại')
}

function boolOptions() {
  const options = []
  const seen = new Set()
  for (const row of props.rows) {
    const value = row.bat_buoc == null || row.bat_buoc === '' ? NONE : row.bat_buoc ? '1' : '0'
    if (seen.has(value)) continue
    seen.add(value)
    options.push({ value, label: BAT_BUOC_LABELS[value] })
  }
  const order = ['1', '0', NONE]
  options.sort((a, b) => order.indexOf(a.value) - order.indexOf(b.value))
  return options.filter((option) => option.value !== NONE || options.length > 1)
}

function operatorOptions() {
  const labels = { [NONE]: 'Không so sánh' }
  const options = codedOptions('toan_tu_so_sanh', labels, OPERATOR_ORDER)
  const named = options.filter((option) => option.value !== NONE)
  const none = options.filter((option) => option.value === NONE)
  if (!named.length) return []
  return [...named, ...none.map((option) => ({ ...option, label: 'Không so sánh' }))]
}

function statusOptions() {
  return withNone(codedOptions('trang_thai', STATUS_LABELS, STATUS_ORDER), 'Chưa xác định')
}

const filterFields = computed(() =>
  [
    { key: 'chuongTrinh', placeholder: 'Chương trình', width: 'filter-wide', options: scopeOptions('chuong_trinh'), token: (row) => text(row.chuong_trinh) || NONE },
    { key: 'phuongThuc', placeholder: 'Phương thức', width: 'filter-wide', options: scopeOptions('phuong_thuc'), token: (row) => text(row.phuong_thuc) || NONE },
    { key: 'doiTuong', placeholder: 'Đối tượng', width: 'filter-mid', options: scopeOptions('doi_tuong'), token: (row) => text(row.doi_tuong) || NONE },
    { key: 'loai', placeholder: 'Loại điều kiện', width: 'filter-mid', options: loaiOptions(), token: (row) => text(row.loai_dieu_kien) || NONE },
    {
      key: 'batBuoc',
      placeholder: 'Bắt buộc',
      width: 'filter-narrow',
      options: boolOptions(),
      token: (row) => (row.bat_buoc == null || row.bat_buoc === '' ? NONE : row.bat_buoc ? '1' : '0'),
    },
    { key: 'toanTu', placeholder: 'Toán tử', width: 'filter-narrow', options: operatorOptions(), token: (row) => text(row.toan_tu_so_sanh) || NONE },
    { key: 'trangThai', placeholder: 'Trạng thái', width: 'filter-narrow', options: statusOptions(), token: (row) => text(row.trang_thai) || NONE },
  ].filter((field) => field.options.length > 1),
)

const filteredRows = computed(() =>
  props.rows.filter((row) =>
    filterFields.value.every((field) => {
      const selected = filters[field.key]
      return !selected.length || selected.includes(field.token(row))
    }),
  ),
)

const emptyText = computed(() => {
  const active = filterFields.value.some((field) => filters[field.key].length)
  if (active && props.rows.length) return 'Không có điều kiện phù hợp bộ lọc.'
  return 'Chưa có dữ liệu.'
})
</script>

<template>
  <div v-if="filterFields.length" class="filters">
    <CustomSelect
      v-for="field in filterFields"
      :key="field.key"
      v-model="filters[field.key]"
      :class="field.width"
      :placeholder="field.placeholder"
      multiple
      collapse-tags
      collapse-tags-tooltip
      clearable
      filterable
    >
      <CustomOption
        v-for="option in field.options"
        :key="`${field.key}-${option.value}`"
        :label="option.label"
        :value="option.value"
      />
    </CustomSelect>
  </div>
  <BangChiTiet :rows="filteredRows" :columns="columns" :empty-text="emptyText" />
</template>

<style scoped>
.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.filter-wide {
  width: 260px;
}

.filter-mid {
  width: 200px;
}

.filter-narrow {
  width: 150px;
}
</style>
