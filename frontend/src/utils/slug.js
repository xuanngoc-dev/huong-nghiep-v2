const SLUG_TOI_DA = 255

/**
 * Chuỗi tiếng Việt → slug không dấu: "Hướng nghiệp 2026!" → "huong-nghiep-2026".
 * Cùng quy tắc với tao_slug ở backend (app/schemas/tin_tuc.py).
 */
export function taoSlug(value) {
  return String(value || '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .normalize('NFD')
    .replace(/\p{Mn}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, SLUG_TOI_DA)
    .replace(/-+$/, '')
}
