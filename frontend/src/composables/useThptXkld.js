import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { nhomNgheApi, thiTruongApi } from '@/api/thptXkld'
import { errorMessage, loadAll } from '@/composables/useThptDuHoc'

// Bảng danh sách, đọc JSON, chuẩn hóa giá trị dùng chung với danh mục du học THPT.
export {
  docMangJson,
  errorMessage,
  giaTriTuyChon,
  useBangDuHoc as useBangXkld,
} from '@/composables/useThptDuHoc'

/**
 * Danh sách nhóm nghề và thị trường để chọn/lọc ở các trang danh mục xuất khẩu lao động THPT.
 * Bảng con gắn với một nhóm nghề; thị trường bỏ trống nghĩa là áp dụng chung cho cả nhóm nghề.
 */
export function useLienKetXkld({ coThiTruong = true } = {}) {
  const nhomOptions = ref([])
  const thiTruongOptions = ref([])

  async function loadOptions() {
    try {
      const [nhom, thiTruong] = await Promise.all([
        loadAll(nhomNgheApi.fetch),
        coThiTruong ? loadAll(thiTruongApi.fetch) : [],
      ])
      nhomOptions.value = nhom
      thiTruongOptions.value = thiTruong
    } catch (error) {
      ElMessage.error(errorMessage(error, 'Không tải được danh sách nhóm nghề, thị trường'))
    }
  }

  function thiTruongCuaNhom(nhomId) {
    if (!nhomId) return thiTruongOptions.value
    return thiTruongOptions.value.filter((item) => item.thpt_xkld_nhom_nghe_id === nhomId)
  }

  function nhanNhom(item) {
    return `${item.ten_nhom} (${item.ma_nhom})`
  }

  function nhanThiTruong(item, kemNhom = false) {
    const ten = `${item.ten_quoc_gia} (${item.ma_quoc_gia})`
    return kemNhom ? `${ten} - ${item.ten_nhom}` : ten
  }

  // Đổi nhóm nghề trong form/bộ lọc thì bỏ thị trường không thuộc nhóm nghề mới.
  function boThiTruongSaiNhom(target, nhomKey = 'thpt_xkld_nhom_nghe_id', ttKey = 'thpt_xkld_thi_truong_id') {
    const ttId = target[ttKey]
    if (ttId && !thiTruongCuaNhom(target[nhomKey]).some((item) => item.id === ttId)) {
      target[ttKey] = null
    }
  }

  /** Đọc liên kết của một phần tử JSON: nhận id hoặc mã (ma_nhom, ma_quoc_gia). */
  function lienKetTuJson(item, line) {
    let nhomId = Number(item.thpt_xkld_nhom_nghe_id) || null
    if (!nhomId && item.ma_nhom) {
      const ma = String(item.ma_nhom).trim().toUpperCase()
      nhomId = nhomOptions.value.find((h) => h.ma_nhom === ma)?.id
      if (!nhomId) throw new Error(`Phần tử thứ ${line}: không tìm thấy nhóm nghề có mã ${ma}`)
    }
    if (!nhomId) throw new Error(`Phần tử thứ ${line} thiếu ma_nhom hoặc thpt_xkld_nhom_nghe_id`)
    if (!coThiTruong) return { thpt_xkld_nhom_nghe_id: nhomId }

    let ttId = Number(item.thpt_xkld_thi_truong_id) || null
    if (!ttId && item.ma_quoc_gia) {
      const ma = String(item.ma_quoc_gia).trim().toUpperCase()
      ttId = thiTruongCuaNhom(nhomId).find((t) => t.ma_quoc_gia === ma)?.id
      if (!ttId) throw new Error(`Phần tử thứ ${line}: nhóm nghề không có thị trường mã ${ma}`)
    }
    return { thpt_xkld_nhom_nghe_id: nhomId, thpt_xkld_thi_truong_id: ttId }
  }

  return {
    nhomOptions,
    thiTruongOptions,
    loadOptions,
    thiTruongCuaNhom,
    nhanNhom,
    nhanThiTruong,
    boThiTruongSaiNhom,
    lienKetTuJson,
  }
}
