import { get, post, put, del } from './request'
import type { PaginatedData } from '@/types/api'

export interface AdminItem {
  id: string
  username: string
  display_name: string | null
  role: string
  city: string | null
  is_active: boolean
  created_at: string | null
}

export interface AdminCreateRequest {
  username: string
  password: string
  display_name?: string
  role: string
  city?: string | null
}

export interface AdminUpdateRequest {
  display_name?: string
  role?: string
  city?: string | null
  is_active?: boolean
}

export async function fetchAdmins(page = 1, pageSize = 20): Promise<PaginatedData<AdminItem>> {
  return get<PaginatedData<AdminItem>>('/admins', { params: { page, page_size: pageSize } })
}

export async function createAdmin(body: AdminCreateRequest): Promise<{ id: string }> {
  return post<{ id: string }>('/admins', body)
}

export async function updateAdmin(id: string, body: AdminUpdateRequest): Promise<{ id: string }> {
  return put<{ id: string }>(`/admins/${id}`, body)
}

export async function resetPassword(id: string, newPassword: string): Promise<void> {
  return post(`/admins/${id}/reset-password`, { new_password: newPassword })
}

export async function deleteAdmin(id: string): Promise<void> {
  return del(`/admins/${id}`)
}

export async function fetchCities(): Promise<string[]> {
  return get<string[]>('/cities')
}
