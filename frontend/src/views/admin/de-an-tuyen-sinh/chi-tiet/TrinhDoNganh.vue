<script setup>
import { computed, reactive } from 'vue'
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'
import { HINH_THUC_LABELS, TRINH_DO_LABELS } from './format'

const props = defineProps({
  rows: { type: Array, default: () => [] },
})

const NONE = '__none__'

const TRINH_DO_ORDER = ['trung_cap', 'cao_dang', 'dai_hoc', 'thac_si', 'tien_si']
const HINH_THUC_ORDER = ['chinh_quy', 'lien_thong', 'vua_hoc_vua_lam', 'tu_xa', 'van_bang_2']

const { chuongTrinh, ghiChu, trinhDo, hinhThuc } = cotChung()

const columns = [
  chuongTrinh,
  trinhDo,
  hinhThuc,
  col('thoi_gian_dao_tao_nam', 'Thời gian (năm)', { width: 150, align: 'center', type: 'number' }),
  col('ma_nganh_chuan', 'Mã ngành chuẩn', { width: 150, align: 'center' }),
  ghiChu,
]

const filters = reactive({
  chuongTrinh: [],
  trinhDo: [],
  hinhThuc: [],
  thoiGian: [],
  maNganh: [],
})

function text(value) {
  return String(value ?? '').trim()
}

function rankedOptions(values, labels, order, emptyLabel) {
  const seen = new Set()
  const options = []
  let hasEmpty = false
  for (const raw of values) {
    const value = text(raw)
    if (!value) {
      hasEmpty = true
      continue
    }
    if (seen.has(value)) continue
    seen.add(value)
    options.push({ value, label: labels[value] || value })
  }
  const rank = new Map(order.map((value, index) => [value, index]))
  options.sort((a, b) => {
    const aRank = rank.has(a.value) ? rank.get(a.value) : order.length
    const bRank = rank.has(b.value) ? rank.get(b.value) : order.length
    if (aRank !== bRank) return aRank - bRank
    return a.label.localeCompare(b.label, 'vi')
  })
  if (hasEmpty && options.length) options.unshift({ value: NONE, label: emptyLabel })
  return options.length > 1 ? options : []
}

function durationToken(value) {
  if (value == null || value === '') return ''
  const number = Number(value)
  if (!Number.isFinite(number)) return text(value)
  return String(number)
}

function durationOptions() {
  const seen = new Set()
  const options = []
  let hasEmpty = false
  for (const row of props.rows) {
    const value = durationToken(row.thoi_gian_dao_tao_nam)
    if (!value) {
      hasEmpty = true
      continue
    }
    if (seen.has(value)) continue
    seen.add(value)
    const number = Number(value)
    options.push({
      value,
      label: Number.isFinite(number) ? `${number.toLocaleString('vi-VN')} năm` : value,
    })
  }
  options.sort((a, b) => {
    const aNum = Number(a.value)
    const bNum = Number(b.value)
    const aOk = Number.isFinite(aNum)
    const bOk = Number.isFinite(bNum)
    if (aOk && bOk) return aNum - bNum
    if (aOk) return -1
    if (bOk) return 1
    return a.label.localeCompare(b.label, 'vi')
  })
  if (hasEmpty && options.length) options.push({ value: NONE, label: 'Chưa xác định' })
  return options.length > 1 ? options : []
}

const filterFields = computed(() =>
  [
    {
      key: 'chuongTrinh',
      placeholder: 'Chương trình',
      width: 'filter-wide',
      options: rankedOptions(props.rows.map((row) => row.chuong_trinh), {}, [], 'Chưa xác định'),
      token: (row) => text(row.chuong_trinh) || NONE,
    },
    {
      key: 'trinhDo',
      placeholder: 'Trình độ',
      width: 'filter-narrow',
      options: rankedOptions(
        props.rows.map((row) => row.trinh_do_dao_tao),
        TRINH_DO_LABELS,
        TRINH_DO_ORDER,
        'Chưa xác định',
      ),
      token: (row) => text(row.trinh_do_dao_tao) || NONE,
    },
    {
      key: 'hinhThuc',
      placeholder: 'Hình thức',
      width: 'filter-mid',
      options: rankedOptions(
        props.rows.map((row) => row.hinh_thuc_dao_tao),
        HINH_THUC_LABELS,
        HINH_THUC_ORDER,
        'Chưa xác định',
      ),
      token: (row) => text(row.hinh_thuc_dao_tao) || NONE,
    },
    {
      key: 'thoiGian',
      placeholder: 'Thời gian đào tạo',
      width: 'filter-mid',
      options: durationOptions(),
      token: (row) => durationToken(row.thoi_gian_dao_tao_nam) || NONE,
    },
    {
      key: 'maNganh',
      placeholder: 'Mã ngành chuẩn',
      width: 'filter-narrow',
      options: rankedOptions(props.rows.map((row) => row.ma_nganh_chuan), {}, [], 'Chưa có mã'),
      token: (row) => text(row.ma_nganh_chuan) || NONE,
    },
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
  if (active && props.rows.length) return 'Không có trình độ ngành phù hợp bộ lọc.'
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
  width: 280px;
}

.filter-mid {
  width: 180px;
}

.filter-narrow {
  width: 150px;
}
</style>
