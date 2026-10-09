export const PRIMARY_PRESETS = [
  { label: 'Xanh lá', value: '#1f7a4d' },
  { label: 'Xanh dương', value: '#1d6fbf' },
  { label: 'Tím', value: '#5b4dbe' },
  { label: 'Cam', value: '#d97816' },
  { label: 'Đỏ', value: '#c23b3b' },
]

export const FONT_OPTIONS = [
  {
    value: 'default',
    label: 'Mặc định',
    stack: "'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif",
  },
  {
    value: 'system',
    label: 'Hệ thống',
    stack: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  },
  {
    value: 'arial',
    label: 'Arial',
    stack: "Arial, 'Helvetica Neue', sans-serif",
  },
  {
    value: 'serif',
    label: 'Serif',
    stack: "Georgia, 'Times New Roman', Times, serif",
  },
]

export const APPEARANCE_DEFAULTS = {
  primaryColor: '#1f7a4d',
  fontFamily: 'default',
  fontSize: 15,
}

const FONT_SIZE_MIN = 13
const FONT_SIZE_MAX = 18

export function normalizeHex(value) {
  const raw = String(value || '').trim()
  const hex = raw.startsWith('#') ? raw : `#${raw}`
  if (/^#[0-9a-fA-F]{6}$/.test(hex)) return hex.toLowerCase()
  return ''
}

export function normalizeFontFamily(value) {
  return FONT_OPTIONS.some((item) => item.value === value) ? value : APPEARANCE_DEFAULTS.fontFamily
}

export function normalizeFontSize(value) {
  const size = Number(value)
  if (!Number.isFinite(size)) return APPEARANCE_DEFAULTS.fontSize
  return Math.min(FONT_SIZE_MAX, Math.max(FONT_SIZE_MIN, Math.round(size)))
}

export function fontStack(value) {
  const match = FONT_OPTIONS.find((item) => item.value === normalizeFontFamily(value))
  return match.stack
}

export function applyAppearance({ primaryColor, fontFamily, fontSize }) {
  const root = document.documentElement
  const color = normalizeHex(primaryColor) || APPEARANCE_DEFAULTS.primaryColor
  const size = normalizeFontSize(fontSize)
  const family = fontStack(fontFamily)

  root.style.setProperty('--el-color-primary', color)
  for (let level = 1; level <= 9; level += 1) {
    const weight = 100 - level * 10
    root.style.setProperty(
      `--el-color-primary-light-${level}`,
      `color-mix(in srgb, ${color} ${weight}%, var(--el-bg-color))`,
    )
  }
  root.style.setProperty('--el-color-primary-dark-2', `color-mix(in srgb, ${color} 80%, #000)`)
  root.style.setProperty('--brand-accent-soft', `color-mix(in srgb, ${color} 14%, var(--el-bg-color))`)

  root.style.setProperty('--app-font-family', family)
  root.style.setProperty('--app-font-size', `${size}px`)
  root.style.setProperty('--el-font-size-base', `${size}px`)
  root.style.setProperty('--el-menu-item-font-size', `${size}px`)
  root.style.setProperty('--el-font-size-extra-small', `${Math.round((size * 12) / 15)}px`)
  root.style.setProperty('--el-font-size-small', `${Math.round((size * 13) / 15)}px`)
  root.style.setProperty('--el-font-size-medium', `${Math.round((size * 16) / 15)}px`)
  root.style.setProperty('--el-font-size-large', `${Math.round((size * 18) / 15)}px`)
  root.style.setProperty('--el-font-size-extra-large', `${Math.round((size * 20) / 15)}px`)
}
