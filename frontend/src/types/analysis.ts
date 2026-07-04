/** 分析结果相关类型 */

export interface ContractAnalysis {
  id: string
  contract_no: string
  rate?: number
  rate_level?: string
  similarity?: string
  analysis?: string
  verified: boolean
  verified_by?: string
  verified_at?: string
}

export interface AcceptanceAnalysis {
  id: string
  contract_no: string
  similarity?: string
  analysis?: string
  verified: boolean
  verified_by?: string
  verified_at?: string
}
