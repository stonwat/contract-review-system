/** 风险相关类型 */

export type RiskLevel = '高' | '中' | '低'

export interface RiskRecord {
  id: string
  contract_no: string
  risk_type: string
  risk_level: RiskLevel
  source_type: string
  detail?: string
  dismissed: boolean
  dismissed_by?: string
  dismissed_at?: string
  created_at: string
}

export interface RiskSummary {
  total: number
  by_level: Record<string, number>
  by_city: Array<Record<string, unknown>>
}
