/** 仪表盘相关类型 */

export interface DashboardOverview {
  project_count: number
  contract_count: number
  pending_verify_count: number
  high_risk_count: number
  completed_count: number
}

export interface CityStat {
  city: string
  project_count: number
  high_risk: number
  pending_verify: number
  completed: number
}
