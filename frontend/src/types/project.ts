/** 项目相关类型 */

export interface Project {
  contract_no: string
  project_name?: string
  city?: string
  has_front_contract: boolean
  has_back_contract: boolean
  has_front_acceptance: boolean
  has_back_acceptance: boolean
  llm_analyzed: boolean
  project_risk?: string
  responsible_person?: string
  audit_status: string
  audited_by?: string
  audited_at?: string
  created_at?: string
  updated_at?: string
}
