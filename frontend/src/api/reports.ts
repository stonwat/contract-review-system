import { get } from './request'

export async function fetchReport(reportType: string, params?: Record<string, unknown>): Promise<unknown> {
  return get(`/reports/${reportType}`, { params })
}

export async function exportReport(reportType: string): Promise<Blob> {
  const resp = await fetch(`${import.meta.env.VITE_API_BASE}/reports/export?report_type=${reportType}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
  })
  return resp.blob()
}
