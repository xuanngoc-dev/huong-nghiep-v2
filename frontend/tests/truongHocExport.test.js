import assert from 'node:assert/strict'
import test from 'node:test'
import { buildExcelBuffer, collectAllPages } from '../src/utils/excelExport.js'
import {
  TRUONG_HOC_EXPORT_COLUMNS,
  truongHocExportFilename,
  truongHocExportRows,
  truongHocListParams,
} from '../src/utils/truongHocExport.js'

test('school list params keep the active filters and omit blank ones', () => {
  assert.deepEqual(
    truongHocListParams(
      {
        q: ' bách ',
        vung_mien: ' Bắc ',
        loai_hinh: 'Công lập',
        loai_co_so: 'Đại học',
        trang_thai_hoat_dong: 'Đang hoạt động',
      },
      { page: 2, pageSize: 20 },
    ),
    {
      page: 2,
      page_size: 20,
      q: 'bách',
      vung_mien: 'Bắc',
      loai_hinh: 'Công lập',
      loai_co_so: 'Đại học',
      trang_thai_hoat_dong: 'Đang hoạt động',
    },
  )
  assert.deepEqual(
    truongHocListParams({
      q: ' ',
      vung_mien: '',
      loai_hinh: '',
      loai_co_so: '',
      trang_thai_hoat_dong: '',
    }),
    {},
  )
})

test('export walks every filtered page instead of the page on screen', async () => {
  const calls = []
  const all = [
    {
      ma_truong: 'BKA',
      ten_truong: 'Bách khoa',
      trang_thai_hoat_dong: 'Đang hoạt động',
      vung_mien: 'Bắc',
      linh_vuc_dao_tao_chinh: ['Kỹ thuật', 'Công nghệ'],
    },
    { ma_truong: 'KHA', ten_truong: 'Kinh tế', trang_thai_hoat_dong: 'Ngừng hoạt động', ten_viet_tat: null },
    { ma_truong: 'NEU', ten_truong: 'Ngoại thương', trang_thai_hoat_dong: 'Đang hoạt động' },
  ]
  const items = await collectAllPages(async ({ page, pageSize }) => {
    calls.push({ page, pageSize })
    const start = (page - 1) * pageSize
    return { items: all.slice(start, start + pageSize), total: all.length }
  }, 2)
  assert.deepEqual(calls, [{ page: 1, pageSize: 2 }, { page: 2, pageSize: 2 }])
  assert.deepEqual(items.map((row) => row.ma_truong), ['BKA', 'KHA', 'NEU'])
  const rows = truongHocExportRows(items)
  assert.equal(rows[0].stt, 1)
  assert.equal(rows[0].trang_thai_hoat_dong, 'Đang hoạt động')
  assert.equal(rows[0].linh_vuc_dao_tao_chinh, 'Kỹ thuật, Công nghệ')
  assert.equal(rows[1].trang_thai_hoat_dong, 'Ngừng hoạt động')
  assert.equal(rows[1].ten_viet_tat, '')
  assert.equal(rows[2].stt, 3)
})

test('excel file contains the filtered schools beyond the first page', async () => {
  const rows = truongHocExportRows([
    {
      ma_truong: 'BKA',
      ten_truong: 'Đại học Bách khoa Hà Nội',
      trang_thai_hoat_dong: 'Đang hoạt động',
      nam_thanh_lap: 1956,
    },
    { ma_truong: 'KHA', ten_truong: 'Đại học Kinh tế Quốc dân', trang_thai_hoat_dong: 'Ngừng hoạt động' },
  ])
  const buffer = await buildExcelBuffer({
    sheetName: 'Trường đại học',
    columns: TRUONG_HOC_EXPORT_COLUMNS,
    rows,
  })
  const excel = await import('exceljs')
  const ExcelJS = excel.default ?? excel
  const workbook = new ExcelJS.Workbook()
  await workbook.xlsx.load(buffer)
  const sheet = workbook.getWorksheet('Trường đại học')
  const headerIndex = (header) => {
    const headerRow = sheet.getRow(1)
    for (let index = 1; index <= headerRow.cellCount; index += 1) {
      if (headerRow.getCell(index).value === header) return index
    }
    throw new Error(`Không thấy cột ${header}`)
  }
  assert.equal(sheet.getRow(1).getCell(2).value, 'Mã trường')
  assert.equal(sheet.getRow(2).getCell(headerIndex('Mã trường')).value, 'BKA')
  assert.equal(sheet.getRow(2).getCell(headerIndex('Năm thành lập')).value, 1956)
  assert.equal(sheet.getRow(2).getCell(headerIndex('Lĩnh vực đào tạo chính')).value, '')
  assert.equal(sheet.getRow(3).getCell(headerIndex('Mã trường')).value, 'KHA')
  assert.equal(sheet.getRow(3).getCell(headerIndex('Trạng thái')).value, 'Ngừng hoạt động')
  assert.equal(truongHocExportFilename(new Date(2026, 9, 15)), 'truong-dai-hoc-2026-10-15.xlsx')
})
