export const NAM_HOC_BAT_DAU = 2020

export function danhSachNamHoc(namHienTai = new Date().getFullYear(), them = null) {
  const ketThuc = Math.max(namHienTai, NAM_HOC_BAT_DAU)
  const danhSach = []
  for (let nam = ketThuc; nam >= NAM_HOC_BAT_DAU; nam -= 1) danhSach.push(nam)
  const namThem = Number(them)
  if (Number.isInteger(namThem) && namThem > 0 && !danhSach.includes(namThem)) {
    danhSach.push(namThem)
    danhSach.sort((a, b) => b - a)
  }
  return danhSach
}

export const NAM_HOC = danhSachNamHoc()

export function nhanNamHoc(nam) {
  const year = Number(nam)
  return `${year}-${year + 1}`
}

export function laNamHoc(value) {
  const year = Number(value)
  if (!NAM_HOC.includes(year)) return null
  return year
}
