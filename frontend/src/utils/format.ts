/** 金额/日期/百分比格式化 */

export function formatAmount(value?: number): string {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('zh-CN', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatPercent(value?: number): string {
  if (value === null || value === undefined) return '—'
  return `${(value * 100).toFixed(2)}%`
}

export function formatDate(dateStr?: string): string {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('zh-CN')
}
