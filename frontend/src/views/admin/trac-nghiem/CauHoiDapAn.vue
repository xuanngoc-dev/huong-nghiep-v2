<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useJsonBatchImport } from '@/composables/useJsonBatchImport'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createCauHoi,
  createCauHoiBulk,
  createCauTraLoi,
  deleteCauHoi,
  deleteCauHoiMany,
  deleteCauTraLoi,
  fetchCauHoi,
  updateCauHoi,
  updateCauTraLoi,
} from '@/api/cauHoiTracNghiem'
import { fetchLoaiCauHoi } from '@/api/loaiCauHoi'
import { fetchNhomHolland } from '@/api/nhomTinhCachHolland'

const JSON_SAMPLE = `[
  {
    "ma_holand": "R",
    "loai_cau_hoi_id": 1,
    "noi_dung_cau_hoi": "Bạn thích sửa chữa máy móc hơn là thảo luận ý tưởng.",
    "trang_thai": 1,
    "cau_tra_loi": [
      { "noi_dung_cau_tra_loi": "Rất đúng", "diem": 2 },
      { "noi_dung_cau_tra_loi": "Không đúng", "diem": 0 }
    ]
  }
]`

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const rows = ref([])
const selectedRows = ref([])
const tableRef = ref()
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const editingId = ref(null)
const createMode = ref('form')
const jsonText = ref('')
const jsonImport = useJsonBatchImport({ label: 'câu hỏi' })
const formRef = ref()
const hollandOptions = ref([])
const loaiOptions = ref([])

const filters = reactive({
  q: '',
  ma_holand: '',
  loai_cau_hoi_id: '',
  trang_thai: '',
})

const form = reactive(emptyForm())

const rules = {
  ma_holand: [{ required: true, message: 'Vui lòng chọn mã Holland', trigger: 'change' }],
  loai_cau_hoi_id: [{ required: true, message: 'Vui lòng chọn loại câu hỏi', trigger: 'change' }],
  noi_dung_cau_hoi: [{ required: true, message: 'Vui lòng nhập nội dung câu hỏi', trigger: 'blur' }],
  trang_thai: [{ required: true, message: 'Vui lòng chọn trạng thái', trigger: 'change' }],
}

function emptyAnswer() {
  return { id: null, noi_dung_cau_tra_loi: '', diem: 0 }
}

function emptyForm() {
  return {
    ma_holand: '',
    loai_cau_hoi_id: '',
    noi_dung_cau_hoi: '',
    ghi_chu: '',
    trang_thai: 1,
    cau_tra_loi: [],
  }
}

function hollandLabel(item) {
  const suffix = item.trang_thai === 1 ? '' : ' — ngừng sử dụng'
  return `${item.ma_nhom} · ${item.ten_nhom}${suffix}`
}

function hollandListLabel(code) {
  const item = hollandOptions.value.find((option) => option.ma_nhom === code)
  if (!item?.ten_nhom) return code ? `[${code}]` : '—'
  return `[${item.ma_nhom}] - ${item.ten_nhom}`
}

function loaiLabel(item) {
  const suffix = item.trang_thai === 1 ? '' : ' — ngừng sử dụng'
  return `${item.ten_loai_cau_hoi}${suffix}`
}

const answerEditor = ref(null)
const answerSaving = ref(false)

function isAddingAnswer(questionId) {
  return answerEditor.value?.questionId === questionId && answerEditor.value.answerId == null
}

function isEditingAnswer(questionId, answerId) {
  return answerEditor.value?.questionId === questionId && answerEditor.value.answerId === answerId
}

function answerTableRows(row) {
  const items = (row.cau_tra_loi || []).map((item) => ({ ...item, draft: false, empty: false }))
  if (isAddingAnswer(row.id)) {
    items.push({ id: `draft-${row.id}`, draft: true, empty: false })
  } else if (!items.length) {
    items.push({ id: `empty-${row.id}`, draft: false, empty: true })
  }
  return items
}

function onAnswerDblClick(question, answer) {
  if (answer.empty || answer.draft) return
  startEditAnswer(question, answer)
}

function resetForm() {
  Object.assign(form, emptyForm())
  form.cau_tra_loi = []
  editingId.value = null
  createMode.value = 'form'
  jsonText.value = ''
  jsonImport.reset()
  formRef.value?.clearValidate()
}

function parseAnswers(value, line) {
  if (value == null) return []
  if (!Array.isArray(value)) {
    throw new Error(`Phần tử thứ ${line} cần cau_tra_loi là mảng đáp án`)
  }
  if (value.length > 20) {
    throw new Error(`Phần tử thứ ${line} chỉ được tối đa 20 đáp án`)
  }
  return value.map((answer, index) => {
    if (!answer || typeof answer !== 'object' || Array.isArray(answer)) {
      throw new Error(`Đáp án ${index + 1} của phần tử thứ ${line} không hợp lệ`)
    }
    const content = String(answer.noi_dung_cau_tra_loi ?? '').trim()
    const score = Number(answer.diem)
    if (!content || !Number.isInteger(score)) {
      throw new Error(`Đáp án ${index + 1} của phần tử thứ ${line} thiếu nội dung hoặc điểm`)
    }
    return { noi_dung_cau_tra_loi: content, diem: score }
  })
}

function parseJsonItems(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('JSON không hợp lệ. Hãy dán một mảng câu hỏi.')
  }
  if (!Array.isArray(data)) {
    throw new Error('JSON phải là một mảng, ví dụ [{ "noi_dung_cau_hoi": "...", "ma_holand": "R" }]')
  }
  if (!data.length) throw new Error('Mảng câu hỏi đang trống')

  return data.map((item, index) => {
    const line = index + 1
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${line} không phải một câu hỏi`)
    }
    const content = String(item.noi_dung_cau_hoi ?? '').trim()
    const code = String(item.ma_holand ?? '').trim()
    const loaiId = Number(item.loai_cau_hoi_id)
    if (!content || !code || !Number.isInteger(loaiId) || loaiId < 1) {
      throw new Error(`Phần tử thứ ${line} thiếu noi_dung_cau_hoi, ma_holand hoặc loai_cau_hoi_id`)
    }
    return {
      noi_dung_cau_hoi: content,
      ma_holand: code,
      loai_cau_hoi_id: loaiId,
      ghi_chu: item.ghi_chu == null ? null : String(item.ghi_chu).trim() || null,
      trang_thai: item.trang_thai ?? 1,
      cau_tra_loi: parseAnswers(item.cau_tra_loi, line),
    }
  })
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

async function loadAll(fetchFn) {
  const size = 100
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchFn({ page: current, page_size: size })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  return items
}

async function loadOptions() {
  const [holland, loai] = await Promise.all([loadAll(fetchNhomHolland), loadAll(fetchLoaiCauHoi)])
  holland.sort((a, b) => a.ma_nhom.localeCompare(b.ma_nhom, 'vi'))
  loai.sort((a, b) => a.thu_tu_uu_tien - b.thu_tu_uu_tien)
  hollandOptions.value = holland
  loaiOptions.value = loai
}

async function load() {
  loading.value = true
  answerEditor.value = null
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.ma_holand) params.ma_holand = filters.ma_holand
    if (filters.loai_cau_hoi_id) params.loai_cau_hoi_id = filters.loai_cau_hoi_id
    if (filters.trang_thai !== '' && filters.trang_thai !== null) params.trang_thai = filters.trang_thai
    const data = await fetchCauHoi(params)
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách câu hỏi'))
  } finally {
    loading.value = false
  }
}

function clearSelection() {
  selectedRows.value = []
  tableRef.value?.clearSelection()
}

function onSelectionChange(selection) {
  selectedRows.value = selection
}

function rowIndex(index) {
  return (page.value - 1) * pageSize.value + index + 1
}

function onSearch() {
  clearSelection()
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

function onPageChange() {
  load()
}

function onSizeChange() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

function addAnswer() {
  if (form.cau_tra_loi.length >= 20) {
    ElMessage.warning('Mỗi câu hỏi chỉ có tối đa 20 đáp án')
    return
  }
  form.cau_tra_loi.push(emptyAnswer())
}

function removeAnswer(index) {
  form.cau_tra_loi.splice(index, 1)
}

async function openCreate() {
  resetForm()
  if (filters.ma_holand) form.ma_holand = filters.ma_holand
  if (filters.loai_cau_hoi_id) form.loai_cau_hoi_id = filters.loai_cau_hoi_id
  dialogVisible.value = true
  await loadOptions().catch(() => {})
}

async function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    ma_holand: row.ma_holand,
    loai_cau_hoi_id: row.loai_cau_hoi_id,
    noi_dung_cau_hoi: row.noi_dung_cau_hoi,
    ghi_chu: row.ghi_chu || '',
    trang_thai: row.trang_thai,
    cau_tra_loi: (row.cau_tra_loi || []).map((item) => ({
      id: item.id,
      noi_dung_cau_tra_loi: item.noi_dung_cau_tra_loi,
      diem: item.diem,
    })),
  })
  dialogVisible.value = true
  await loadOptions().catch(() => {})
}

function answersFromForm() {
  return form.cau_tra_loi.map((item, index) => {
    const content = String(item.noi_dung_cau_tra_loi ?? '').trim()
    if (!content) throw new Error(`Đáp án ${index + 1} chưa có nội dung`)
    if (item.diem === null || item.diem === '' || !Number.isInteger(Number(item.diem))) {
      throw new Error(`Đáp án ${index + 1} chưa có điểm`)
    }
    const payload = { noi_dung_cau_tra_loi: content, diem: Number(item.diem) }
    if (item.id) payload.id = item.id
    return payload
  })
}

function currentAnswers(questionId) {
  const row = rows.value.find((item) => item.id === questionId)
  return (row?.cau_tra_loi || []).map((item) => ({
    id: item.id,
    noi_dung_cau_tra_loi: item.noi_dung_cau_tra_loi,
    diem: item.diem,
  }))
}

function payloadFromForm() {
  return {
    ma_holand: String(form.ma_holand).trim().toUpperCase(),
    loai_cau_hoi_id: form.loai_cau_hoi_id,
    noi_dung_cau_hoi: form.noi_dung_cau_hoi.trim(),
    ghi_chu: form.ghi_chu?.trim() || null,
    trang_thai: form.trang_thai,
    cau_tra_loi: editingId.value ? currentAnswers(editingId.value) : answersFromForm(),
  }
}

function startAddAnswer(row) {
  if ((row.cau_tra_loi?.length || 0) >= 20) {
    ElMessage.warning('Mỗi câu hỏi chỉ có tối đa 20 đáp án')
    return
  }
  answerEditor.value = {
    questionId: row.id,
    answerId: null,
    noi_dung_cau_tra_loi: '',
    diem: 0,
  }
}

function startEditAnswer(row, answer) {
  answerEditor.value = {
    questionId: row.id,
    answerId: answer.id,
    noi_dung_cau_tra_loi: answer.noi_dung_cau_tra_loi,
    diem: answer.diem,
  }
}

function cancelAnswerEdit() {
  answerEditor.value = null
}

function answerPayload() {
  const editor = answerEditor.value
  const content = String(editor?.noi_dung_cau_tra_loi ?? '').trim()
  if (!content) throw new Error('Vui lòng nhập nội dung đáp án')
  if (editor.diem === null || editor.diem === '' || !Number.isInteger(Number(editor.diem))) {
    throw new Error('Vui lòng nhập điểm')
  }
  return { noi_dung_cau_tra_loi: content, diem: Number(editor.diem) }
}

async function saveAnswer(row) {
  let payload
  try {
    payload = answerPayload()
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  const editor = answerEditor.value
  answerSaving.value = true
  try {
    if (editor.answerId) {
      const updated = await updateCauTraLoi(row.id, editor.answerId, payload)
      const index = row.cau_tra_loi.findIndex((item) => item.id === editor.answerId)
      if (index >= 0) row.cau_tra_loi.splice(index, 1, updated)
      ElMessage.success('Đã cập nhật đáp án')
    } else {
      const created = await createCauTraLoi(row.id, payload)
      row.cau_tra_loi = [...(row.cau_tra_loi || []), created]
      ElMessage.success('Đã thêm đáp án')
    }
    answerEditor.value = null
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được đáp án'))
  } finally {
    answerSaving.value = false
  }
}

async function onDeleteAnswer(row, answer) {
  try {
    await ElMessageBox.confirm(`Xóa đáp án "${answer.noi_dung_cau_tra_loi}"?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }
  try {
    await deleteCauTraLoi(row.id, answer.id)
    row.cau_tra_loi = row.cau_tra_loi.filter((item) => item.id !== answer.id)
    if (answerEditor.value?.answerId === answer.id) answerEditor.value = null
    ElMessage.success('Đã xóa đáp án')
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được đáp án'))
  }
}

function fillJsonSample() {
  jsonText.value = JSON_SAMPLE
}

async function onSubmitJson() {
  let items
  try {
    items = parseJsonItems(jsonText.value)
  } catch (error) {
    ElMessage.error(error.message)
    return
  }

  await jsonImport.run({
    items,
    createBatch: createCauHoiBulk,
    jsonText,
    saving,
    dialogVisible,
    reload: load,
  })
}

async function onSubmit() {
  if (!editingId.value && createMode.value === 'json') {
    await onSubmitJson()
    return
  }
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  let payload
  try {
    payload = payloadFromForm()
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await updateCauHoi(editingId.value, payload)
      ElMessage.success('Đã cập nhật câu hỏi')
    } else {
      await createCauHoi(payload)
      ElMessage.success('Đã thêm câu hỏi')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được câu hỏi'))
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm('Xóa câu hỏi này và toàn bộ đáp án của nó?', 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }
  try {
    await deleteCauHoi(row.id)
    ElMessage.success('Đã xóa câu hỏi')
    tableRef.value?.toggleRowSelection(row, false)
    if (rows.value.length === 1 && page.value > 1) page.value -= 1
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được câu hỏi'))
  }
}

async function onDeleteSelected() {
  const ids = selectedRows.value.map((row) => row.id)
  if (!ids.length) return
  try {
    await ElMessageBox.confirm(`Xóa ${ids.length} câu hỏi đã chọn và đáp án của chúng?`, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return
  }
  deleting.value = true
  try {
    const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
    const result = await deleteCauHoiMany(ids)
    ElMessage.success(`Đã xóa ${result.deleted} câu hỏi`)
    clearSelection()
    if (removedOnPage >= rows.value.length && page.value > 1) {
      page.value -= 1
      return
    }
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không xóa được các câu hỏi đã chọn'))
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadOptions().catch(() => {})])
})
</script>

<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <div class="filters">
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm nội dung, ghi chú hoặc loại câu hỏi"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect
          v-model="filters.ma_holand"
          class="filter-status"
          placeholder="Holland"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in hollandOptions"
            :key="item.id"
            :label="hollandLabel(item)"
            :value="item.ma_nhom"
          />
        </CustomSelect>
        <CustomSelect
          v-model="filters.loai_cau_hoi_id"
          class="filter-parent"
          placeholder="Loại câu hỏi"
          clearable
          filterable
          @change="onSearch"
        >
          <CustomOption
            v-for="item in loaiOptions"
            :key="item.id"
            :label="loaiLabel(item)"
            :value="item.id"
          />
        </CustomSelect>
        <CustomSelect
          v-model="filters.trang_thai"
          class="filter-status"
          placeholder="Trạng thái"
          clearable
          @change="onSearch"
        >
          <CustomOption label="Hoạt động" :value="1" />
          <CustomOption label="Ngừng sử dụng" :value="0" />
        </CustomSelect>
        <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
      </div>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách câu hỏi - đáp án</h2>
        <div class="toolbar__actions">
          <CustomBadge :value="selectedRows.length" :hidden="!selectedRows.length" type="danger">
            <CustomButton
              type="danger"
              plain
              :disabled="!selectedRows.length"
              :loading="deleting"
              @click="onDeleteSelected"
            >
              <CustomIcon><Delete /></CustomIcon>
              Xóa
            </CustomButton>
          </CustomBadge>
          <CustomButton type="primary" @click="openCreate">
            <CustomIcon><Plus /></CustomIcon>
            Thêm câu hỏi
          </CustomButton>
        </div>
      </div>

      <CustomTable
        ref="tableRef"
        :loading="loading"
        :data="rows"
        row-key="id"
        stripe
        border
        @selection-change="onSelectionChange"
      >
        <CustomTableColumn type="selection" width="48" reserve-selection align="center" />
        <CustomTableColumn type="expand" width="48">
          <template #default="{ row }">
            <div class="answer-panel">
              <CustomTable
                class="answer-table"
                :data="answerTableRows(row)"
                row-key="id"
                border
                @row-dblclick="(answer) => onAnswerDblClick(row, answer)"
              >
                <CustomTableColumn label="STT" width="72" align="center">
                  <template #default="{ row: answer, $index }">
                    {{ answer.empty ? '—' : $index + 1 }}
                  </template>
                </CustomTableColumn>
                <CustomTableColumn label="Đáp án" min-width="240">
                  <template #default="{ row: answer }">
                    <CustomInput
                      v-if="answer.draft || isEditingAnswer(row.id, answer.id)"
                      v-model="answerEditor.noi_dung_cau_tra_loi"
                      maxlength="2000"
                      placeholder="Nội dung đáp án"
                    />
                    <span v-else-if="!answer.empty">{{ answer.noi_dung_cau_tra_loi }}</span>
                  </template>
                </CustomTableColumn>
                <CustomTableColumn label="Điểm" width="150" align="center">
                  <template #default="{ row: answer }">
                    <CustomInputNumber
                      v-if="answer.draft || isEditingAnswer(row.id, answer.id)"
                      v-model="answerEditor.diem"
                      :min="-9999"
                      :max="9999"
                      :step="1"
                      :precision="0"
                      controls-position="right"
                    />
                    <span v-else-if="!answer.empty">{{ answer.diem }}</span>
                  </template>
                </CustomTableColumn>
                <CustomTableColumn label="Thao tác" width="120" align="center">
                  <template #default="{ row: answer, $index }">
                    <div class="row-actions">
                      <template v-if="answer.draft || isEditingAnswer(row.id, answer.id)">
                        <CustomButton type="primary" link :loading="answerSaving" @click="saveAnswer(row)">
                          Lưu
                        </CustomButton>
                        <CustomButton link @click="cancelAnswerEdit">Hủy</CustomButton>
                      </template>
                      <template v-else>
                        <CustomTooltip v-if="!answer.empty" content="Xóa" placement="top">
                          <CustomButton
                            link
                            type="danger"
                            aria-label="Xóa đáp án"
                            @click.stop="onDeleteAnswer(row, answer)"
                          >
                            <CustomIcon><Delete /></CustomIcon>
                          </CustomButton>
                        </CustomTooltip>
                        <CustomTooltip
                          v-if="$index === answerTableRows(row).length - 1"
                          content="Thêm đáp án"
                          placement="top"
                        >
                          <CustomButton link type="primary" aria-label="Thêm đáp án" @click.stop="startAddAnswer(row)">
                            <CustomIcon><Plus /></CustomIcon>
                          </CustomButton>
                        </CustomTooltip>
                      </template>
                    </div>
                  </template>
                </CustomTableColumn>
              </CustomTable>
            </div>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="STT" width="72" align="center">
          <template #default="{ $index }">{{ rowIndex($index) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Holland" min-width="180">
          <template #default="{ row }">{{ hollandListLabel(row.ma_holand) }}</template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_loai_cau_hoi" label="Loại câu hỏi" min-width="160" />
        <CustomTableColumn prop="noi_dung_cau_hoi" label="Nội dung câu hỏi" min-width="280" />
        <CustomTableColumn label="Trạng thái" width="150" align="center">
          <template #default="{ row }">
            <CustomTag :type="row.trang_thai === 1 ? 'success' : 'info'" effect="light">
              {{ row.trang_thai === 1 ? 'Hoạt động' : 'Ngừng sử dụng' }}
            </CustomTag>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Ghi chú" min-width="160">
          <template #default="{ row }">{{ row.ghi_chu || '—' }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <CustomTooltip content="Sửa" placement="top">
                <CustomButton link type="primary" aria-label="Sửa" @click="openEdit(row)">
                  <CustomIcon><Edit /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Xóa" placement="top">
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có câu hỏi nào." />
        </template>
      </CustomTable>

      <div class="pager">
        <CustomPagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="onPageChange"
          @size-change="onSizeChange"
        />
      </div>
    </CustomCard>
  </div>

  <CustomDialog
    v-model="dialogVisible"
    :title="editingId ? 'Cập nhật câu hỏi' : 'Thêm câu hỏi'"
    width="920px"
    destroy-on-close
    :close-on-click-modal="!saving"
    :close-on-press-escape="!saving"
    :show-close="!saving"
    @closed="resetForm"
  >
    <CustomRadioGroup v-if="!editingId" v-model="createMode" class="create-mode" :disabled="saving">
      <CustomRadioButton value="form">Nhập form</CustomRadioButton>
      <CustomRadioButton value="json">Dán JSON</CustomRadioButton>
    </CustomRadioGroup>

    <div v-if="!editingId && createMode === 'json'" class="json-panel">
      <div class="json-panel__head">
        <p>
          Dán một mảng JSON. Mỗi phần tử cần <code>noi_dung_cau_hoi</code>, <code>ma_holand</code> và
          <code>loai_cau_hoi_id</code>. <code>cau_tra_loi</code> là mảng
          <code>{ "noi_dung_cau_tra_loi", "diem" }</code>.
        </p>
        <CustomButton text type="primary" :disabled="saving" @click="fillJsonSample">Điền mẫu</CustomButton>
      </div>
      <CustomInput
        v-model="jsonText"
        class="json-input"
        type="textarea"
        :rows="16"
        :disabled="saving"
        placeholder="Dán mảng JSON vào đây"
      />
    </div>

    <CustomForm v-else ref="formRef" :model="form" :rules="rules" label-position="top">
      <CustomRow :gutter="16">
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Mã Holland" prop="ma_holand">
            <CustomSelect
              v-model="form.ma_holand"
              filterable
              placeholder="Chọn mã Holland"
              style="width: 100%"
              :disabled="!hollandOptions.length"
            >
              <CustomOption
                v-for="item in hollandOptions"
                :key="item.id"
                :label="hollandLabel(item)"
                :value="item.ma_nhom"
              />
            </CustomSelect>
            <p v-if="!hollandOptions.length" class="field-hint">
              Chưa có nhóm Holland. Hãy thêm ở danh mục Nhóm Holland trước.
            </p>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Loại câu hỏi" prop="loai_cau_hoi_id">
            <CustomSelect
              v-model="form.loai_cau_hoi_id"
              filterable
              placeholder="Chọn loại câu hỏi"
              style="width: 100%"
              :disabled="!loaiOptions.length"
            >
              <CustomOption
                v-for="item in loaiOptions"
                :key="item.id"
                :label="loaiLabel(item)"
                :value="item.id"
              />
            </CustomSelect>
            <p v-if="!loaiOptions.length" class="field-hint">
              Chưa có loại câu hỏi. Hãy thêm ở danh mục Loại câu hỏi trước.
            </p>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="24">
          <CustomFormItem label="Nội dung câu hỏi" prop="noi_dung_cau_hoi">
            <CustomInput
              v-model="form.noi_dung_cau_hoi"
              type="textarea"
              :rows="3"
              maxlength="5000"
              show-word-limit
              placeholder="Nhập nội dung câu hỏi"
            />
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Trạng thái" prop="trang_thai">
            <CustomSelect v-model="form.trang_thai" :clearable="false" style="width: 100%">
              <CustomOption label="Hoạt động" :value="1" />
              <CustomOption label="Ngừng sử dụng" :value="0" />
            </CustomSelect>
          </CustomFormItem>
        </CustomCol>
        <CustomCol :span="12" :xs="24">
          <CustomFormItem label="Ghi chú" prop="ghi_chu">
            <CustomInput v-model="form.ghi_chu" maxlength="2000" placeholder="Ghi chú (nếu có)" />
          </CustomFormItem>
        </CustomCol>
        <CustomCol v-if="!editingId" :span="24">
          <div class="answers-head">
            <span>Đáp án</span>
            <CustomButton text type="primary" @click="addAnswer">
              <CustomIcon><Plus /></CustomIcon>
              Thêm đáp án
            </CustomButton>
          </div>
          <p v-if="!form.cau_tra_loi.length" class="field-hint">Chưa có đáp án. Có thể thêm sau.</p>
          <div v-for="(answer, index) in form.cau_tra_loi" :key="answer.id || index" class="answer-row">
            <CustomInput
              v-model="answer.noi_dung_cau_tra_loi"
              maxlength="2000"
              :placeholder="`Nội dung đáp án ${index + 1}`"
            />
            <CustomInputNumber
              v-model="answer.diem"
              :min="-9999"
              :max="9999"
              :step="1"
              :precision="0"
              controls-position="right"
            />
            <CustomButton link type="danger" aria-label="Xóa đáp án" @click="removeAnswer(index)">
              <CustomIcon><Delete /></CustomIcon>
            </CustomButton>
          </div>
        </CustomCol>
      </CustomRow>
    </CustomForm>
    <template #footer>
      <JsonImportDialogFooter
        :batch="jsonImport"
        :saving="saving"
        :show-progress="!editingId && createMode === 'json'"
        @cancel="dialogVisible = false"
        @save="onSubmit"
      />
    </template>
  </CustomDialog>
</template>

<style scoped>
.catalog-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.catalog-card {
  border-radius: 12px;
}

.filters,
.toolbar__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar__title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.row-actions :deep(.el-icon) {
  font-size: 20px !important;
}

.row-actions :deep(.el-icon svg) {
  stroke: currentColor;
  stroke-width: 1.15;
  stroke-linejoin: round;
  paint-order: stroke fill;
}

.filter-search {
  width: 320px;
}

.filter-parent {
  width: 240px;
}

.filter-status {
  width: 170px;
}

.create-mode {
  margin-bottom: 16px;
}

.json-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.json-panel__head p {
  margin: 0;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.json-input :deep(textarea) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
}

.field-hint {
  margin: 6px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.answers-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  font-weight: 600;
}

.answer-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px 40px;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.answer-panel {
  padding: 8px 12px 12px 48px;
}

.answer-table :deep(.el-input-number) {
  width: 120px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 640px) {
  .filter-search,
  .filter-parent,
  .filter-status,
  .answer-row {
    width: 100%;
    grid-template-columns: minmax(0, 1fr) 40px;
  }

  .answer-panel {
    padding-left: 12px;
  }

  .answer-row :deep(.el-input-number) {
    grid-column: 1;
  }
}
</style>
