/** 合同相关类型 */

export interface LineItem {
  id: string
  contract_id: string
  item_no?: number
  item_name?: string
  spec?: string
  unit?: string
  quantity?: number
  unit_price?: number
  amount?: number
  remark?: string
}

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
  source_file_hash?: string
  ocr_engine?: string
  llm_model?: string
  extracted_at?: string
  line_items: LineItem[]
}
