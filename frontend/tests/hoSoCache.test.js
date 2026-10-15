import assert from 'node:assert/strict'
import test, { mock } from 'node:test'
import { clearHoSoCache, HO_SO_CACHE_TTL_MS, loadHoSo, storeHoSo, toChatProfile } from '../src/utils/hoSoCache.js'

const profile = {
  ho_ten: 'Nguyễn Văn An',
  email: 'an@example.com',
  so_dien_thoai: '0912345678',
  dan_toc: 'Kinh',
  trinh_do_hoc_van: { chung_chi_ngoai_ngu: [{ ma: 'IELTS', thanh_tich: '7.5' }] },
}

test('one profile fetch serves concurrent questions and later turns', async () => {
  clearHoSoCache()
  let calls = 0
  const fetchProfile = async () => {
    calls += 1
    return profile
  }
  const [first, second] = await Promise.all([loadHoSo(7, fetchProfile), loadHoSo(7, fetchProfile)])
  const later = await loadHoSo(7, fetchProfile)
  assert.equal(calls, 1)
  assert.equal(first, second)
  assert.equal(later, first)
  const chatProfile = toChatProfile(first)
  assert.equal(chatProfile.trinh_do_hoc_van.chung_chi_ngoai_ngu[0].thanh_tich, '7.5')
  assert.equal(chatProfile.dan_toc, 'Kinh')
  assert.equal(chatProfile.ho_ten, undefined)
  assert.equal(chatProfile.email, undefined)
  assert.equal(chatProfile.so_dien_thoai, undefined)
  clearHoSoCache()
})

test('saving the profile updates the cache without another fetch', async () => {
  clearHoSoCache()
  let calls = 0
  await loadHoSo(8, async () => {
    calls += 1
    return { dan_toc: 'Kinh' }
  })
  const saved = { dan_toc: 'Tày', trinh_do_hoc_van: { chung_chi_ngoai_ngu: [{ ma: 'IELTS', thanh_tich: '8.0' }] } }
  storeHoSo(8, saved)
  const data = await loadHoSo(8, async () => {
    calls += 1
    return { dan_toc: 'Kinh' }
  })
  assert.equal(calls, 1)
  assert.deepEqual(data, saved)
  clearHoSoCache()
})

test('expired, cleared, or failed profiles are fetched again', async () => {
  clearHoSoCache()
  mock.timers.enable({ apis: ['Date'], now: 1_000 })
  try {
    let calls = 0
    const fetchProfile = async () => ({ n: ++calls })
    await loadHoSo(9, fetchProfile)
    mock.timers.tick(HO_SO_CACHE_TTL_MS)
    assert.equal((await loadHoSo(9, fetchProfile)).n, 2)
    clearHoSoCache(9)
    assert.equal((await loadHoSo(9, fetchProfile)).n, 3)
    clearHoSoCache(9)
    await assert.rejects(loadHoSo(9, async () => { calls += 1; throw new Error('down') }))
    assert.equal((await loadHoSo(9, fetchProfile)).n, 5)
  } finally {
    mock.timers.reset()
    clearHoSoCache()
  }
})

test('logout during a fetch does not keep that profile', async () => {
  clearHoSoCache()
  let release
  const pending = new Promise((resolve) => { release = resolve })
  const loading = loadHoSo(10, () => pending)
  clearHoSoCache()
  release(profile)
  assert.equal(await loading, profile)
  let calls = 0
  const data = await loadHoSo(10, async () => {
    calls += 1
    return { dan_toc: 'Mới' }
  })
  assert.equal(calls, 1)
  assert.equal(data.dan_toc, 'Mới')
  clearHoSoCache()
})

test('an empty profile adds nothing to the question', () => {
  assert.equal(toChatProfile({ ho_ten: 'An', email: 'a@b.c', trinh_do_hoc_van: {} }), null)
  assert.equal(toChatProfile(null), null)
})
