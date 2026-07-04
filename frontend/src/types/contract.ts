/** 合同相关类型 */

export interface Contract {
  id: string
  contract_no: string
  contract_type: string
  party_a?: string
  party_b?: string
  total_amount?: number
  city?: string
  project_name?: string
  verified: boolean
  verified_by?: string
  verified_at?: string
}

export interface ContractDetail extends Contract {
  type_judge_basis?: string
  our_role?: string
  signing_date?: string
  contract_period?: string
  amount_uppercase?: string
  tax_rate?: number
  payment_terms?: string
  delivery_terms?: string
  acceptance_terms?: string
  breach_terms?: string
  warranty_terms?: string
  ip_terms?: string
  other_key_terms?: string
  source_file_name?: string
  extracted_at?: string
}

/** 项目卡片数据：前后项并排展示 */
export interface ProjectCard {
  contract_no: string
  project_name?: string
  city?: string
  has_front_contract: boolean
  has_back_contract: boolean
  has_front_acceptance: boolean
  has_back_acceptance: boolean
  llm_analyzed: boolean
  project_risk?: string
  audit_status?: string
  front_contract: Contract | null
  back_contract: Contract | null
}
