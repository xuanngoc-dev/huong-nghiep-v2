<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchPhuongThucTuyenSinh } from '@/api/phuongThucTuyenSinh'
import { buildMethodDetail } from './phuongThucChiTiet'

const props = defineProps({
  programs: { type: Array, default: () => [] },
  methods: { type: Array, default: () => [] },
  criteria: { type: Array, default: () => [] },
})

const detailVisible = ref(false)
const activeDetail = ref(null)

const filters = reactive({
  ten: [],
  ma: [],
  phuongThuc: [],
  toHop: [],
})

const catalogMethods = ref([])

function catalogLabel(item) {
  const code = String(item?.ma_phuong_thuc || '').trim()
  const name = String(item?.ten_phuong_thuc || '').trim()
  if (code && name) return `${code} — ${name}`
  return code || name
}

async function loadCatalogMethods() {
  const pageSize = 1000
  const collected = []
  let page = 1
  try {
    while (true) {
      const data = await fetchPhuongThucTuyenSinh(
        { page, page_size: pageSize },
        { skipLoading: true },
      )
      const items = data.items || []
      collected.push(...items)
      if (!items.length || collected.length >= (data.total || 0)) break
      page += 1
    }
    catalogMethods.value = collected
  } catch {
    ElMessage.error('Không tải được danh mục phương thức tuyển sinh')
  }
}

onMounted(loadCatalogMethods)

function programLabel(program) {
  const code = String(program?.ma_xet_tuyen || '').trim()
  const name = String(program?.ten_chuong_trinh || '').trim()
  if (code && name) return `${code} — ${name}`
  return code || name
}

function methodKey(method) {
  return String(method?.ma_phuong_thuc_cua_bo || method?.ma_phuong_thuc_cua_truong || '').trim()
}

function methodLabel(method) {
  const bo = String(method?.ma_phuong_thuc_cua_bo || '').trim()
  const truong = String(method?.ma_phuong_thuc_cua_truong || '').trim()
  if (bo && truong) return `${bo} (${truong})`
  return bo || truong
}

function comboCodes(method) {
  const value = method?.to_hop_mon_hoc
  if (value == null || value === '') return []
  const items = Array.isArray(value) ? value : [value]
  const codes = []
  for (const item of items) {
    const code = String(
      item && typeof item === 'object' ? item.ma_to_hop || item.ma || '' : item ?? '',
    ).trim()
    if (code && !codes.includes(code)) codes.push(code)
  }
  return codes
}

const methodColumns = computed(() => {
  const columns = new Map()
  for (const method of props.methods) {
    const key = methodKey(method)
    if (!key) continue
    if (!columns.has(key)) {
      columns.set(key, { key, label: methodLabel(method), names: [] })
    }
    const title = String(method.ten_phuong_thuc_cua_truong || '').trim()
    const column = columns.get(key)
    if (title && !column.names.includes(title)) column.names.push(title)
  }
  return [...columns.values()].map((column) => ({
    key: column.key,
    label: column.label,
    hint: column.names.join('\n'),
  }))
})

const tableRows = computed(() => {
  const usedByProgram = new Map()
  for (const method of props.methods) {
    const label = method.chuong_trinh || ''
    const key = methodKey(method)
    if (!label || !key) continue
    if (!usedByProgram.has(label)) usedByProgram.set(label, new Map())
    const byKey = usedByProgram.get(label)
    if (!byKey.has(key)) byKey.set(key, [])
    const codes = byKey.get(key)
    for (const code of comboCodes(method)) {
      if (!codes.includes(code)) codes.push(code)
    }
  }

  return props.programs.map((program) => {
    const used = usedByProgram.get(programLabel(program)) || new Map()
    const cells = {}
    for (const column of methodColumns.value) {
      cells[column.key] = used.has(column.key)
        ? { used: true, combos: used.get(column.key) }
        : { used: false, combos: [] }
    }
    const quota = program.chi_tieu_tuyen_sinh
    return {
      row_key: program.row_key,
      ten: program.ten_chuong_trinh || '—',
      chiTieu: quota == null || quota === '' ? '—' : Number(quota).toLocaleString('vi-VN'),
      ma: program.ma_xet_tuyen || '—',
      cells,
    }
  })
})

function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'vi'))
}

const programOptions = computed(() =>
  uniqueSorted(props.programs.map((program) => String(program.ten_chuong_trinh || '').trim())),
)

const codeOptions = computed(() =>
  uniqueSorted(props.programs.map((program) => String(program.ma_xet_tuyen || '').trim())),
)

const comboOptions = computed(() =>
  uniqueSorted(props.methods.flatMap((method) => comboCodes(method))),
)

function listsCombo(cell, code) {
  return Boolean(cell?.used && cell.combos.includes(code))
}

const filteredRows = computed(() =>
  tableRows.value.filter((row) => {
    if (filters.ten.length && !filters.ten.includes(row.ten)) return false
    if (filters.ma.length && !filters.ma.includes(row.ma)) return false
    if (filters.phuongThuc.length && !filters.phuongThuc.some((key) => row.cells[key]?.used)) return false
    if (filters.toHop.length) {
      const cells = filters.phuongThuc.length
        ? filters.phuongThuc.map((key) => row.cells[key])
        : Object.values(row.cells)
      const matched = cells.some((cell) => filters.toHop.some((code) => listsCombo(cell, code)))
      if (!matched) return false
    }
    return true
  }),
)

const visibleColumns = computed(() => {
  if (filters.phuongThuc.length) {
    return methodColumns.value.filter((column) => filters.phuongThuc.includes(column.key))
  }
  if (filters.toHop.length) {
    return methodColumns.value.filter((column) =>
      filteredRows.value.some((row) =>
        filters.toHop.some((code) => listsCombo(row.cells[column.key], code)),
      ),
    )
  }
  return methodColumns.value
})

const emptyText = computed(() => {
  const active = filters.ten.length || filters.ma.length || filters.phuongThuc.length || filters.toHop.length
  if (active && props.programs.length) return 'Không có chương trình phù hợp bộ lọc.'
  return 'Chưa có chương trình đào tạo.'
})

const detailByKey = computed(() => {
  const map = new Map()
  for (const column of methodColumns.value) {
    map.set(column.key, buildMethodDetail({
      label: column.label,
      subtitle: column.hint,
      methods: props.methods.filter((method) => methodKey(method) === column.key),
      criteria: props.criteria,
    }))
  }
  return map
})

function openMethodDetail(column) {
  activeDetail.value = detailByKey.value.get(column.key) || null
  detailVisible.value = true
}

function cellText(value) {
  if (value == null || value === '') return '—'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
</script>

<template>
  <div class="filters">
    <CustomSelect
      v-model="filters.ten"
      class="filter-program"
      placeholder="Chương trình/ngành đào tạo"
      multiple
      collapse-tags
      collapse-tags-tooltip
      clearable
      filterable
    >
      <CustomOption v-for="name in programOptions" :key="name" :label="name" :value="name" />
    </CustomSelect>
    <CustomSelect
      v-model="filters.ma"
      class="filter-code"
      placeholder="Mã xét tuyển"
      multiple
      collapse-tags
      collapse-tags-tooltip
      clearable
      filterable
    >
      <CustomOption v-for="code in codeOptions" :key="code" :label="code" :value="code" />
    </CustomSelect>
    <CustomSelect
      v-model="filters.phuongThuc"
      class="filter-method"
      placeholder="Phương thức tuyển sinh"
      multiple
      collapse-tags
      collapse-tags-tooltip
      clearable
      filterable
    >
      <CustomOption
        v-for="item in catalogMethods"
        :key="item.id"
        :label="catalogLabel(item)"
        :value="item.ma_phuong_thuc"
      />
    </CustomSelect>
    <CustomSelect
      v-model="filters.toHop"
      class="filter-combo"
      placeholder="Tổ hợp môn học"
      multiple
      collapse-tags
      collapse-tags-tooltip
      clearable
      filterable
    >
      <CustomOption v-for="code in comboOptions" :key="code" :label="code" :value="code" />
    </CustomSelect>
  </div>
  <CustomTable :data="filteredRows" row-key="row_key" stripe border max-height="520" class="program-method-table">
    <el-table-column label="TT" width="64" align="center">
      <template #default="{ $index }">{{ $index + 1 }}</template>
    </el-table-column>
    <el-table-column prop="ten" label="Chương trình/ngành đào tạo" min-width="260" />
    <el-table-column prop="chiTieu" label="Chỉ tiêu dự kiến" width="120" align="center" />
    <el-table-column prop="ma" label="Mã xét tuyển" width="130" align="center" />
    <el-table-column
      v-if="visibleColumns.length"
      label="Phương thức tuyển sinh/Tổ hợp xét tuyển"
      align="center"
    >
      <el-table-column
        v-for="column in visibleColumns"
        :key="column.key"
        :label="column.label"
        min-width="160"
        align="center"
        class-name="combo-cell"
      >
        <template #header>
          <div class="method-heading">
            <CustomTooltip placement="top" :disabled="!column.hint">
              <template #content>
                <div class="method-tip">{{ column.hint }}</div>
              </template>
              <span class="method-name">{{ column.label }}</span>
            </CustomTooltip>
            <CustomTooltip content="Xem chi tiết" placement="top">
              <button
                type="button"
                class="method-detail"
                aria-label="Xem chi tiết"
                @click.stop="openMethodDetail(column)"
              >
                <CustomIcon><View /></CustomIcon>
              </button>
            </CustomTooltip>
          </div>
        </template>
        <template #default="{ row }">
          <span v-if="row.cells[column.key].combos.length" class="combo-list">
            {{ row.cells[column.key].combos.join(', ') }}
          </span>
          <CustomIcon
            v-else-if="row.cells[column.key].used"
            class="mark mark--yes"
            aria-label="Có sử dụng"
          >
            <Check />
          </CustomIcon>
          <CustomIcon v-else class="mark mark--no" aria-label="Không sử dụng">
            <Close />
          </CustomIcon>
        </template>
      </el-table-column>
    </el-table-column>
    <template #empty>
      <CustomEmpty :description="emptyText" />
    </template>
  </CustomTable>

  <CustomDialog
    v-model="detailVisible"
    class="method-detail-dialog"
    :title="activeDetail?.title || 'Chi tiết phương thức'"
    width="90%"
    append-to-body
  >
    <p v-if="activeDetail?.subtitle" class="detail-sub">{{ activeDetail.subtitle }}</p>
    <div v-if="activeDetail?.sections.length" class="detail-body">
      <section v-for="section in activeDetail.sections" :key="section.key" class="detail-section">
        <h3>{{ section.title }}</h3>
        <article v-for="(block, index) in section.blocks" :key="`${section.key}-${index}`" class="detail-block">
          <h4 v-if="block.title">{{ block.title }}</h4>
          <p v-if="block.kind === 'text'" class="detail-text">{{ block.text }}</p>
          <p v-else-if="block.kind === 'formula'" class="formula">{{ block.formula }}</p>
          <div
            v-else-if="block.kind === 'table'"
            class="detail-table"
            :class="{ 'detail-table--wide': block.columns.length > 4 }"
          >
            <CustomTable :data="block.rows" border max-height="480">
              <el-table-column
                v-for="column in block.columns"
                :key="column.key"
                :label="column.label"
                :min-width="column.minWidth"
                show-overflow-tooltip
              >
                <template #default="{ row }">{{ cellText(row[column.key]) }}</template>
              </el-table-column>
            </CustomTable>
          </div>
          <div v-else-if="block.kind === 'groups'" class="score-groups">
            <div v-for="group in block.groups" :key="group.title" class="score-group">
              <h5>{{ group.title }}</h5>
              <CustomTable :data="group.rows" border max-height="480">
                <el-table-column label="Mức" min-width="160">
                  <template #default="{ row }">{{ row.loai }}</template>
                </el-table-column>
                <el-table-column label="Điểm" width="100" align="center">
                  <template #default="{ row }">{{ cellText(row.diem) }}</template>
                </el-table-column>
              </CustomTable>
            </div>
          </div>
          <ul v-if="block.notes?.length" class="detail-notes">
            <li v-for="note in block.notes" :key="note">{{ note }}</li>
          </ul>
        </article>
      </section>
    </div>
    <CustomEmpty v-else description="Phương thức này chưa có quy định quy đổi điểm hoặc cách tính điểm." />
  </CustomDialog>
</template>

<style scoped>
.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.filter-program {
  width: 280px;
}

.filter-code,
.filter-combo {
  width: 160px;
}

.filter-method {
  width: 320px;
}

.program-method-table :deep(thead.is-group th.el-table__cell) {
  background: var(--el-table-header-bg-color);
  color: var(--el-table-header-text-color);
}

.program-method-table :deep(.el-table__header .cell) {
  white-space: normal;
  line-height: 1.35;
  text-align: center;
}

.program-method-table :deep(td.el-table__cell:first-child .cell),
.program-method-table :deep(td.el-table__cell:nth-child(3) .cell),
.program-method-table :deep(td.el-table__cell:nth-child(4) .cell) {
  text-align: center;
}

.program-method-table :deep(td.combo-cell .cell) {
  white-space: normal;
  line-height: 1.4;
}

.combo-list {
  display: inline-block;
  max-width: 100%;
}

.mark {
  font-size: 18px;
  vertical-align: middle;
}

.mark--yes {
  color: var(--el-color-success);
}

.mark--no {
  color: var(--el-color-danger);
}

.method-heading {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  max-width: 100%;
}

.method-name {
  cursor: help;
}

.method-detail {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  margin-left: 4px;
  padding: 0;
  border: 1px solid rgb(255 255 255 / 85%);
  border-radius: 4px;
  background: rgb(255 255 255 / 18%);
  color: #fff;
  cursor: pointer;
}

.method-detail:hover {
  background: rgb(255 255 255 / 32%);
}

.method-detail :deep(.el-icon) {
  font-size: 14px;
}

.detail-sub,
.detail-body {
  font-size: var(--app-font-size);
  line-height: 1.5;
  color: var(--el-text-color-primary);
}

.detail-sub {
  margin: 0 0 16px;
  color: var(--el-text-color-secondary);
  white-space: pre-line;
}

.detail-section + .detail-section {
  margin-top: 22px;
}

.detail-section h3 {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 400;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.detail-block + .detail-block {
  margin-top: 14px;
}

.detail-block h4,
.score-group h5 {
  margin: 0 0 8px;
  font-size: inherit;
  font-weight: 400;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.detail-text,
.formula,
.detail-notes {
  font-size: inherit;
  line-height: 1.5;
}

.detail-text,
.formula {
  margin: 0;
}

.formula {
  padding: 10px 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  font-weight: 400;
}

.detail-notes {
  margin: 8px 0 0;
  padding-left: 18px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

.detail-table,
.detail-table--wide {
  width: 100%;
}

.score-groups {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 768px) {
  .score-groups {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.method-tip {
  max-width: 320px;
  white-space: pre-line;
  line-height: 1.45;
}
</style>
