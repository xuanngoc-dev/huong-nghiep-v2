/** Keep a logged-in profile warm so each chat turn does not refetch /tai-khoan/ho-so. */
export const HO_SO_CACHE_TTL_MS = 10 * 60 * 1000

const PROFILE_FIELDS = [
  'gioi_tinh', 'ngay_sinh', 'dan_toc', 'ton_giao', 'tinh_thanh_id',
  'khu_vuc_uu_tien_id', 'doi_tuong_uu_tien_id', 'trinh_do_hoc_van',
  'suc_khoe_the_chat', 'kha_nang_tai_chinh',
]

const entries = new Map()
const pending = new Map()
const generation = new Map()
let epoch = 0

function hasValue(value) {
  if (value == null || value === '') return false
  if (Array.isArray(value)) return value.some(hasValue)
  if (typeof value === 'object') return Object.values(value).some(hasValue)
  return true
}

/** Academic fields only. Contact details stay out of the model prompt. */
export function toChatProfile(data) {
  if (!data || typeof data !== 'object') return null
  const profile = {}
  for (const key of PROFILE_FIELDS) {
    if (hasValue(data[key])) profile[key] = data[key]
  }
  return Object.keys(profile).length ? profile : null
}

export function clearHoSoCache(userId) {
  if (userId == null) {
    entries.clear()
    pending.clear()
    generation.clear()
    epoch += 1
    return
  }
  const key = String(userId)
  entries.delete(key)
  pending.delete(key)
  generation.set(key, (generation.get(key) || 0) + 1)
}

export function storeHoSo(userId, data) {
  if (userId == null || userId === '') return
  entries.set(String(userId), { data, at: Date.now() })
}

export function loadHoSo(userId, fetchProfile) {
  if (userId == null || userId === '') return Promise.resolve(null)
  const key = String(userId)
  const hit = entries.get(key)
  if (hit && Date.now() - hit.at < HO_SO_CACHE_TTL_MS) return Promise.resolve(hit.data)
  const running = pending.get(key)
  if (running) return running
  const gen = generation.get(key) || 0
  const seenEpoch = epoch
  const started = Date.now()
  const request = Promise.resolve()
    .then(() => fetchProfile())
    .then((data) => {
      if (seenEpoch !== epoch || (generation.get(key) || 0) !== gen) return data
      const current = entries.get(key)
      if (current && current.at >= started) return current.data
      entries.set(key, { data, at: Date.now() })
      return data
    })
    .finally(() => {
      if (pending.get(key) === request) pending.delete(key)
    })
  pending.set(key, request)
  return request
}
