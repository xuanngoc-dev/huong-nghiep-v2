// Mã thiết bị của khách vãng lai, lưu trên trình duyệt; dùng chung khóa với tính năng Tìm trường phù hợp
// để một trình duyệt chỉ có một mã. Trình duyệt chặn lưu trữ thì dùng mã tạm trong phiên làm việc này.
const KHOA_THIET_BI = 'thpt-tim-truong-phu-hop-thiet-bi'
let maTam = ''

function taoMa() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID()
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`
}

export function maThietBi(storage = globalThis.localStorage) {
  try {
    let ma = storage.getItem(KHOA_THIET_BI)
    if (!ma) {
      ma = taoMa()
      storage.setItem(KHOA_THIET_BI, ma)
    }
    return ma
  } catch {
    maTam ||= taoMa()
    return maTam
  }
}
