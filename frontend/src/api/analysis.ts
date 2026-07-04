import { get, post } from './request'
import type { ContractAnalysis, AcceptanceAnalysis } from '@/types/analysis'

export async function fetchContractAnalysis(contractNo: string): Promise<ContractAnalysis> {
  return get<ContractAnalysis>(`/contract-analysis/${contractNo}`, { silent: true })
}

export async function fetchContractAnalysisList(verified?: boolean): Promise<{ items: ContractAnalysis[]; total: number }> {
  return get('/contract-analysis', { params: verified === undefined ? {} : { verified } })
}

export async function upsertContractAnalysis(body: Partial<ContractAnalysis> & { contract_no: string }): Promise<unknown> {
  return post('/contract-analysis', body)
}

export async function verifyContractAnalysis(contractNo: string, verifiedBy?: string): Promise<unknown> {
  return post(`/contract-analysis/${contractNo}/verify`, { verified_by: verifiedBy })
}

export async function fetchAcceptanceAnalysis(contractNo: string): Promise<AcceptanceAnalysis> {
  return get<AcceptanceAnalysis>(`/acceptance-analysis/${contractNo}`, { silent: true })
}

export async function fetchAcceptanceAnalysisList(verified?: boolean): Promise<{ items: AcceptanceAnalysis[]; total: number }> {
  return get('/acceptance-analysis', { params: verified === undefined ? {} : { verified } })
}

export async function upsertAcceptanceAnalysis(body: Partial<AcceptanceAnalysis> & { contract_no: string }): Promise<unknown> {
  return post('/acceptance-analysis', body)
}

export async function verifyAcceptanceAnalysis(contractNo: string, verifiedBy?: string): Promise<unknown> {
  return post(`/acceptance-analysis/${contractNo}/verify`, { verified_by: verifiedBy })
}
