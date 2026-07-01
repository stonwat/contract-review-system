/** 验收报告相关类型 */

export interface AcceptanceReport {
  id: string
  acceptance_no?: string
  contract_no: string
  acceptance_type?: string
  acceptance_content?: string
  acceptance_date?: string
  acceptance_result?: string
  verified: boolean
  verified_by?: string
  comparison_result?: string
  content_diff_detail?: string
  date_logic?: string
}
