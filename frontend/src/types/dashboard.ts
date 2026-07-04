/** 仪表盘相关类型 */

export interface DashboardOverview {
  project_count: number
  contract_count: number
  pending_verify_count: number
  high_risk_count: number
  completed_count: number
  llm_analyzed_count: number
  front_count: number
  back_count: number
  ready_count: number
}

export interface CityStat {
  city: string
  project_count: number
  pending_verify: number
  completed: number
  high_risk: number
}
