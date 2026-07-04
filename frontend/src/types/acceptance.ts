/** 验收报告相关类型 */

export interface AcceptanceReport {
  id: string
  acceptance_no?: string
  contract_no: string
  acceptance_type?: string
  type_judge_basis?: string
  acceptance_content?: string
  acceptance_date?: string
  acceptance_result?: string
  source_file_name?: string
  verified: boolean
  verified_by?: string
  verified_at?: string
}
