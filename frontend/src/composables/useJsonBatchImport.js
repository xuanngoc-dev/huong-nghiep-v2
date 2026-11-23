import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

export const JSON_BATCH_SIZE = 20
export const JSON_BATCH_TIMEOUT = 120000

function errorDetail(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function isRequestTimeout(error) {
  return error?.code === 'ECONNABORTED' || /timeout/i.test(error?.message || '')
}

function capitalize(text) {
  if (!text) return text
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export function useJsonBatchImport({ label }) {
  const progress = reactive({
    total: 0,
    done: 0,
    active: false,
    failed: false,
  })

  function reset() {
    progress.total = 0
    progress.done = 0
    progress.active = false
    progress.failed = false
  }

  async function run({ items, createBatch, jsonText, saving, dialogVisible, reload }) {
    saving.value = true
    progress.total = items.length
    progress.done = 0
    progress.active = items.length > 1
    progress.failed = false
    let saved = 0
    let created = 0
    let updated = 0
    try {
      for (let index = 0; index < items.length; index += JSON_BATCH_SIZE) {
        const batch = items.slice(index, index + JSON_BATCH_SIZE)
        const result = await createBatch(batch, {
          skipLoading: true,
          timeout: JSON_BATCH_TIMEOUT,
        })
        const batchCreated = Number(result?.created ?? batch.length)
        const batchUpdated = Number(result?.updated ?? 0)
        created += batchCreated
        updated += batchUpdated
        saved += (batchCreated + batchUpdated) || batch.length
        progress.done = saved
      }
    } catch (error) {
      progress.failed = true
      if (saved > 0) {
        jsonText.value = JSON.stringify(items.slice(saved), null, 2)
      }
      const detail = errorDetail(error, `Không thêm được danh sách ${label}`)
      if (isRequestTimeout(error)) {
        ElMessage.error(
          saved > 0
            ? `Đã xác nhận lưu ${saved}/${items.length} ${label}. Lô đang gửi có thể đã được lưu dù hết thời gian chờ. Hãy kiểm tra danh sách trước khi lưu tiếp phần còn lại trong ô JSON.`
            : `Hết thời gian chờ. ${capitalize(label)} có thể đã được lưu — hãy kiểm tra danh sách trước khi gửi lại.`,
        )
      } else if (saved > 0) {
        ElMessage.error(
          `Đã lưu ${saved}/${items.length} ${label}. ${detail} Phần chưa lưu vẫn nằm trong ô JSON.`,
        )
      } else {
        ElMessage.error(detail)
      }
      if (saved > 0 || isRequestTimeout(error)) {
        await reload().catch(() => {})
      }
      return
    } finally {
      saving.value = false
      progress.active = false
    }

    const parts = []
    if (created > 0) parts.push(`thêm ${created}`)
    if (updated > 0) parts.push(`cập nhật ${updated}`)
    ElMessage.success(
      parts.length > 1
        ? `Đã ${parts.join(', ')} ${label}`
        : parts.length === 1 && updated > 0
          ? `Đã cập nhật ${updated} ${label}`
          : `Đã thêm ${created || saved} ${label}`,
    )
    dialogVisible.value = false
    try {
      await reload()
    } catch (error) {
      ElMessage.error(errorDetail(error, `Đã lưu ${label} nhưng không tải lại được danh sách`))
    }
  }

  return {
    progress,
    label,
    batchSize: JSON_BATCH_SIZE,
    reset,
    run,
  }
}
