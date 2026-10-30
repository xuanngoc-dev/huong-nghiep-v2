<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchPhuongThucTuyenSinh } from '@/api/phuongThucTuyenSinh'

const props = defineProps({
  programs: { type: Array, default: () => [] },
  methods: { type: Array, default: () => [] },
})

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
          <CustomTooltip placement="top" :disabled="!column.hint">
            <template #content>
              <div class="method-tip">{{ column.hint }}</div>
            </template>
            <span class="method-header">{{ column.label }}</span>
          </CustomTooltip>
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

.method-header {
  cursor: help;
}

.method-tip {
  max-width: 320px;
  white-space: pre-line;
  line-height: 1.45;
}
</style>
