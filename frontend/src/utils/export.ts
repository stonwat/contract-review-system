/** Excel 导出辅助 */
import * as XLSX from 'xlsx'

export function exportToExcel(data: Record<string, unknown>[], fileName: string, sheetName = 'Sheet1'): void {
  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)
  XLSX.writeFile(workbook, `${fileName}.xlsx`)
}
