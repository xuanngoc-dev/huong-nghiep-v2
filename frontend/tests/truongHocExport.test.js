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
    truongHocListParams({ q: ' bách ', khu_vuc: ' Hà Nội ', loai_hinh_dao_tao: 'Công lập', trang_thai: 0 }, { page: 2, pageSize: 20 }),
    { page: 2, page_size: 20, q: 'bách', khu_vuc: 'Hà Nội', loai_hinh_dao_tao: 'Công lập', trang_thai: 0 },
  )
  assert.deepEqual(truongHocListParams({ q: ' ', khu_vuc: '', loai_hinh_dao_tao: '', trang_thai: '' }), {})
})

test('export walks every filtered page instead of the page on screen', async () => {
  const calls = []
  const all = [
    { ma_truong: 'BKA', ten_truong: 'Bách khoa', trang_thai: 1, khu_vuc: 'Hà Nội' },
    { ma_truong: 'KHA', ten_truong: 'Kinh tế', trang_thai: 0, ten_viet_tat: null },
    { ma_truong: 'NEU', ten_truong: 'Ngoại thương', trang_thai: 1 },
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
  assert.equal(rows[0].trang_thai, 'Hoạt động')
  assert.equal(rows[1].trang_thai, 'Khóa')
  assert.equal(rows[1].ten_viet_tat, '')
  assert.equal(rows[2].stt, 3)
})

test('excel file contains the filtered schools beyond the first page', async () => {
  const rows = truongHocExportRows([
    { ma_truong: 'BKA', ten_truong: 'Đại học Bách khoa Hà Nội', trang_thai: 1, nam_thanh_lap: 1956 },
    { ma_truong: 'KHA', ten_truong: 'Đại học Kinh tế Quốc dân', trang_thai: 0 },
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
  assert.equal(sheet.getRow(1).getCell(2).value, 'Mã trường')
  assert.equal(sheet.getRow(2).getCell(2).value, 'BKA')
  assert.equal(sheet.getRow(2).getCell(14).value, 1956)
  assert.equal(sheet.getRow(3).getCell(2).value, 'KHA')
  assert.equal(sheet.getRow(3).getCell(15).value, 'Khóa')
  assert.equal(truongHocExportFilename(new Date(2026, 9, 15)), 'truong-dai-hoc-2026-10-15.xlsx')
})
