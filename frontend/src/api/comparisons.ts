import { get, post } from './request'
import type { Comparison, ComparisonDetail } from '@/types/comparison'

export async function createComparison(frontId: string, backId: string): Promise<{ comparison_id: string; status: string }> {
  return post('/comparisons', { front_contract_id: frontId, back_contract_id: backId })
}

export async function fetchComparisons(): Promise<{ items: Comparison[] }> {
  return get('/comparisons')
}

export async function fetchComparisonDetail(id: string): Promise<ComparisonDetail> {
  return get<ComparisonDetail>(`/comparisons/${id}`)
}

export async function autoCompare(): Promise<{ total_pairs: number; new_comparisons: number; existed: number }> {
  return post('/comparisons/auto')
}
