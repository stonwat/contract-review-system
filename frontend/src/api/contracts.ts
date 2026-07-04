import { get, post, put, del } from './request'
import type { PaginatedData, PaginationParams } from '@/types/api'
import type { Contract, ContractDetail, ProjectCard } from '@/types/contract'

export interface ContractListParams extends PaginationParams {
  contract_no?: string
  contract_type?: string
  verified?: boolean
}

export interface CardListParams {
  city?: string
  verified?: boolean
  keyword?: string
}

export async function fetchContracts(params: ContractListParams): Promise<PaginatedData<Contract>> {
  return get<PaginatedData<Contract>>('/contracts', { params })
}

export async function fetchProjectCards(params?: CardListParams): Promise<{ items: ProjectCard[]; total: number }> {
  return get<{ items: ProjectCard[]; total: number }>('/contracts/cards', { params })
}

export async function checkDuplicate(contractNo: string, contractType: string): Promise<{ exists: boolean; contract_id: string | null }> {
  return get<{ exists: boolean; contract_id: string | null }>('/contracts/check', { params: { contract_no: contractNo, contract_type: contractType } })
}

export async function fetchContractDetail(id: string): Promise<ContractDetail> {
  return get<ContractDetail>(`/contracts/${id}`)
}

export async function updateContract(id: string, body: Partial<ContractDetail>): Promise<unknown> {
  return put(`/contracts/${id}`, body)
}

export async function verifyContract(id: string, verifiedBy: string): Promise<unknown> {
  return post(`/contracts/${id}/verify`, { verified_by: verifiedBy })
}

export async function deleteContract(id: string): Promise<unknown> {
  return del(`/contracts/${id}`)
}
