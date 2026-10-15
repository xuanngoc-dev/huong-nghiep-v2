const EXCEL_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

/** Walk every page until the filtered total is collected. */
export async function collectAllPages(fetchPage, pageSize = 1000) {
  const items = []
  for (let page = 1; page <= 100; page += 1) {
    const data = await fetchPage({ page, pageSize })
    const batch = Array.isArray(data?.items) ? data.items : []
    items.push(...batch)
    const total = Number(data?.total)
    if (!batch.length || batch.length < pageSize || (Number.isFinite(total) && items.length >= total)) break
  }
  return items
}

export async function buildExcelBuffer({ sheetName, columns, rows }) {
  const excel = await import('exceljs')
  const ExcelJS = excel.default ?? excel
  const workbook = new ExcelJS.Workbook()
  const sheet = workbook.addWorksheet(String(sheetName || 'Dữ liệu').slice(0, 31))
  sheet.columns = columns.map((column) => ({
    header: column.header,
    key: column.key,
    width: column.width,
  }))
  for (const row of rows) sheet.addRow(row)
  const header = sheet.getRow(1)
  header.font = { bold: true }
  header.alignment = { vertical: 'middle' }
  sheet.views = [{ state: 'frozen', ySplit: 1 }]
  if (columns.length) {
    sheet.autoFilter = {
      from: { row: 1, column: 1 },
      to: { row: 1, column: columns.length },
    }
  }
  return workbook.xlsx.writeBuffer()
}

export async function downloadExcel({ filename, ...workbook }) {
  const buffer = await buildExcelBuffer(workbook)
  const blob = new Blob([buffer], { type: EXCEL_TYPE })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
