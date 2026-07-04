import { get, post, put } from './request'
import type { AcceptanceReport } from '@/types/acceptance'
import type { PaginatedData, PaginationParams } from '@/types/api'

export interface AcceptanceListParams extends PaginationParams {
  contract_no?: string
  verified?: boolean
}

export async function fetchAcceptanceList(params?: AcceptanceListParams): Promise<PaginatedData<AcceptanceReport>> {
  return get<PaginatedData<AcceptanceReport>>('/acceptance', { params })
}

export async function fetchAcceptanceDetail(id: string): Promise<AcceptanceReport> {
  return get<AcceptanceReport>(`/acceptance/${id}`)
}

export async function checkDuplicate(contractNo: string, acceptanceType: string): Promise<{ exists: boolean }> {
  return get<{ exists: boolean }>('/acceptance/check', { params: { contract_no: contractNo, acceptance_type: acceptanceType } })
}

export async function updateAcceptance(id: string, body: Partial<AcceptanceReport>): Promise<unknown> {
  return put(`/acceptance/${id}`, body)
}

export async function verifyAcceptance(id: string): Promise<unknown> {
  return post(`/acceptance/${id}/verify`)
}
