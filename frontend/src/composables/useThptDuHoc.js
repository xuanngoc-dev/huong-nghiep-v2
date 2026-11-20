import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { huongDiApi, quocGiaApi } from '@/api/thptDuHoc'

export function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

// Chuỗi rỗng/undefined → null, chuỗi được cắt khoảng trắng.
export function giaTriTuyChon(value) {
  const cleaned = typeof value === 'string' ? value.trim() : value
  return cleaned === '' || cleaned === undefined ? null : cleaned
}

export function docMangJson(text, nhan) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error(`JSON không hợp lệ. Hãy dán một mảng ${nhan}.`)
  }
  if (!Array.isArray(data)) throw new Error('JSON phải là một mảng các đối tượng')
  if (!data.length) throw new Error(`Mảng ${nhan} đang trống`)
  data.forEach((item, index) => {
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      throw new Error(`Phần tử thứ ${index + 1} không phải một ${nhan}`)
    }
  })
  return data
}

async function loadAll(fetchFn) {
  const size = 100
  const items = []
  for (let current = 1; current <= 20; current += 1) {
    const data = await fetchFn({ page: current, page_size: size })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
  }
  return items
}

/**
 * Danh sách hướng đi và quốc gia để chọn/lọc ở các trang danh mục du học THPT.
 * Bảng con gắn với một hướng đi; quốc gia bỏ trống nghĩa là áp dụng chung cho cả hướng đi.
 */
export function useLienKetDuHoc({ coQuocGia = true } = {}) {
  const huongOptions = ref([])
  const quocGiaOptions = ref([])

  async function loadOptions() {
    try {
      const [huong, quocGia] = await Promise.all([
        loadAll(huongDiApi.fetch),
        coQuocGia ? loadAll(quocGiaApi.fetch) : [],
      ])
      huongOptions.value = huong
      quocGiaOptions.value = quocGia
    } catch (error) {
      ElMessage.error(errorMessage(error, 'Không tải được danh sách hướng đi, quốc gia'))
    }
  }

  function quocGiaCuaHuong(huongId) {
    if (!huongId) return quocGiaOptions.value
    return quocGiaOptions.value.filter((item) => item.thpt_duhoc_huong_di_id === huongId)
  }

  function nhanHuong(item) {
    return `${item.ten_huong} (${item.ma_huong})`
  }

  function nhanQuocGia(item, kemHuong = false) {
    const ten = `${item.ten_quoc_gia} (${item.ma_quoc_gia})`
    return kemHuong ? `${ten} - ${item.ten_huong}` : ten
  }

  // Đổi hướng đi trong form/bộ lọc thì bỏ quốc gia không thuộc hướng đi mới.
  function boQuocGiaSaiHuong(target, huongKey = 'thpt_duhoc_huong_di_id', qgKey = 'thpt_duhoc_quoc_gia_id') {
    const qgId = target[qgKey]
    if (qgId && !quocGiaCuaHuong(target[huongKey]).some((item) => item.id === qgId)) {
      target[qgKey] = null
    }
  }

  /** Đọc liên kết của một phần tử JSON: nhận id hoặc mã (ma_huong, ma_quoc_gia). */
  function lienKetTuJson(item, line) {
    let huongId = Number(item.thpt_duhoc_huong_di_id) || null
    if (!huongId && item.ma_huong) {
      const ma = String(item.ma_huong).trim().toUpperCase()
      huongId = huongOptions.value.find((h) => h.ma_huong === ma)?.id
      if (!huongId) throw new Error(`Phần tử thứ ${line}: không tìm thấy hướng đi có mã ${ma}`)
    }
    if (!huongId) throw new Error(`Phần tử thứ ${line} thiếu ma_huong hoặc thpt_duhoc_huong_di_id`)
    if (!coQuocGia) return { thpt_duhoc_huong_di_id: huongId }

    let qgId = Number(item.thpt_duhoc_quoc_gia_id) || null
    if (!qgId && item.ma_quoc_gia) {
      const ma = String(item.ma_quoc_gia).trim().toUpperCase()
      qgId = quocGiaCuaHuong(huongId).find((q) => q.ma_quoc_gia === ma)?.id
      if (!qgId) throw new Error(`Phần tử thứ ${line}: hướng đi không có quốc gia mã ${ma}`)
    }
    return { thpt_duhoc_huong_di_id: huongId, thpt_duhoc_quoc_gia_id: qgId }
  }

  return {
    huongOptions,
    quocGiaOptions,
    loadOptions,
    quocGiaCuaHuong,
    nhanHuong,
    nhanQuocGia,
    boQuocGiaSaiHuong,
    lienKetTuJson,
  }
}

/**
 * Bảng danh sách có phân trang, chọn nhiều và xóa của một danh mục du học THPT.
 * `params()` trả về bộ lọc hiện tại; `nhan` là tên đối tượng viết thường (dùng trong thông báo).
 */
export function useBangDuHoc({ api, nhan, params, canhBaoXoa = '' }) {
  const loading = ref(false)
  const deleting = ref(false)
  const rows = ref([])
  const selectedRows = ref([])
  const tableRef = ref()
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)

  async function load() {
    loading.value = true
    try {
      const data = await api.fetch({ page: page.value, page_size: pageSize.value, ...params() })
      rows.value = data.items
      total.value = data.total
    } catch (error) {
      ElMessage.error(errorMessage(error, `Không tải được danh sách ${nhan}`))
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

  // Về trang 1 thì `current-change` của phân trang tự gọi load.
  function onSearch() {
    clearSelection()
    if (page.value !== 1) {
      page.value = 1
      return
    }
    load()
  }

  async function xacNhanXoa(noiDung) {
    try {
      await ElMessageBox.confirm(`${noiDung}${canhBaoXoa ? ` ${canhBaoXoa}` : ''}`, 'Xác nhận xóa', {
        type: 'warning',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy',
        confirmButtonClass: 'el-button--danger',
      })
      return true
    } catch {
      return false
    }
  }

  async function onDelete(row, ten) {
    if (!(await xacNhanXoa(`Xóa ${nhan} "${ten}"?`))) return
    try {
      await api.remove(row.id)
      ElMessage.success(`Đã xóa ${nhan}`)
      tableRef.value?.toggleRowSelection(row, false)
      if (rows.value.length === 1 && page.value > 1) {
        page.value -= 1
        return
      }
      await load()
    } catch (error) {
      ElMessage.error(errorMessage(error, `Không xóa được ${nhan}`))
    }
  }

  async function onDeleteSelected() {
    const ids = selectedRows.value.map((row) => row.id)
    if (!ids.length) return
    if (!(await xacNhanXoa(`Xóa ${ids.length} ${nhan} đã chọn?`))) return

    deleting.value = true
    try {
      const removedOnPage = rows.value.filter((row) => ids.includes(row.id)).length
      const result = await api.removeMany(ids)
      ElMessage.success(`Đã xóa ${result.deleted} ${nhan}`)
      clearSelection()
      if (removedOnPage >= rows.value.length && page.value > 1) {
        page.value -= 1
        return
      }
      await load()
    } catch (error) {
      ElMessage.error(errorMessage(error, `Không xóa được các ${nhan} đã chọn`))
    } finally {
      deleting.value = false
    }
  }

  return {
    loading,
    deleting,
    rows,
    selectedRows,
    tableRef,
    total,
    page,
    pageSize,
    load,
    clearSelection,
    onSelectionChange,
    rowIndex,
    onSearch,
    onDelete,
    onDeleteSelected,
  }
}
