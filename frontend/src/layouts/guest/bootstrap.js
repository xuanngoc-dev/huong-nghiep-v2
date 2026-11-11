import bootstrapCss from 'bootstrap/dist/css/bootstrap.min.css?inline'

const STYLE_ID = 'guest-bootstrap'

// Nhiều component cùng dùng một thẻ <style> (GuestLayout, Login, Register), nên đếm số nơi đang dùng
// và chỉ gỡ khi không còn ai. Khi chuyển route, Vue chạy setup của trang mới trước onUnmounted của
// trang cũ; nếu không đếm, trang cũ sẽ gỡ mất CSS mà trang mới đang cần.
// Bộ đếm lưu trên chính thẻ <style> để không bị reset khi module được nạp lại (HMR).
export function mountGuestBootstrap() {
  let style = document.getElementById(STYLE_ID)
  if (!style) {
    style = document.createElement('style')
    style.id = STYLE_ID
    style.textContent = bootstrapCss
    document.head.appendChild(style)
  }
  style.dataset.users = String(Number(style.dataset.users || 0) + 1)
}

export function unmountGuestBootstrap() {
  const style = document.getElementById(STYLE_ID)
  if (!style) return
  const users = Number(style.dataset.users || 0) - 1
  if (users > 0) style.dataset.users = String(users)
  else style.remove()
}
