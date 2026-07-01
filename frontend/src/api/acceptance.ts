import { get, post, put } from './request'
import type { AcceptanceReport } from '@/types/acceptance'

export async function fetchAcceptanceList(): Promise<{ items: AcceptanceReport[] }> {
  return get('/acceptance')
}

export async function fetchAcceptanceDetail(id: string): Promise<AcceptanceReport> {
  return get<AcceptanceReport>(`/acceptance/${id}`)
}

export async function updateAcceptance(id: string, body: Partial<AcceptanceReport>): Promise<unknown> {
  return put(`/acceptance/${id}`, body)
}

export async function verifyAcceptance(id: string): Promise<unknown> {
  return post(`/acceptance/${id}/verify`)
}
