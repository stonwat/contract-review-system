import { get, post } from './request'
import type { PaginatedData, PaginationParams } from '@/types/api'
import type { RiskRecord, RiskSummary } from '@/types/risk'

export interface RiskListParams extends PaginationParams {
  risk_level?: string
  dismissed?: boolean
}

export async function fetchRisks(params: RiskListParams): Promise<PaginatedData<RiskRecord>> {
  return get<PaginatedData<RiskRecord>>('/risks', { params })
}

export async function fetchRiskSummary(): Promise<RiskSummary> {
  return get<RiskSummary>('/risks/summary')
}

export async function dismissRisk(id: string, dismissedBy: string): Promise<unknown> {
  return post(`/risks/${id}/dismiss`, { dismissed_by: dismissedBy })
}
