import bootstrapCss from 'bootstrap/dist/css/bootstrap.min.css?inline'

const STYLE_ID = 'guest-bootstrap'

export function mountGuestBootstrap() {
  if (document.getElementById(STYLE_ID)) return
  const style = document.createElement('style')
  style.id = STYLE_ID
  style.textContent = bootstrapCss
  document.head.appendChild(style)
}

export function unmountGuestBootstrap() {
  document.getElementById(STYLE_ID)?.remove()
}
