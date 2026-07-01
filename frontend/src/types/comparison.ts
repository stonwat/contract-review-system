/** 比对相关类型 */

export interface Comparison {
  id: string
  contract_no: string
  city?: string
  front_amount?: number
  back_amount?: number
  amount_diff?: number
  margin_rate?: number
  amount_match?: string
  payment_match?: string
  delivery_match?: string
  acceptance_match?: string
  other_match?: string
  compared_at?: string
}

export interface LineItemComparison {
  id: string
  item_name?: string
  front_quantity?: number
  back_quantity?: number
  quantity_diff?: number
  front_unit_price?: number
  back_unit_price?: number
  price_diff?: number
  match_status?: string
  risk_level?: string
  risk_reason?: string
}

export interface ComparisonDetail extends Comparison {
  payment_diff_detail?: string
  delivery_diff_detail?: string
  acceptance_diff_detail?: string
  other_diff_detail?: string
  llm_model?: string
  line_items: LineItemComparison[]
}
