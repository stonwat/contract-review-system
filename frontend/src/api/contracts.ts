import { get, post, put, del } from './request'
import type { PaginatedData, PaginationParams } from '@/types/api'
import type { Contract, ContractDetail } from '@/types/contract'

export interface ContractListParams extends PaginationParams {
  contract_no?: string
  contract_type?: string
  verified?: boolean
}

export async function fetchContracts(params: ContractListParams): Promise<PaginatedData<Contract>> {
  return get<PaginatedData<Contract>>('/contracts', { params })
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
