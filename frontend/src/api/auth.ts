import { get, post } from './request'
import type { ApiResponse } from '@/types/api'

export interface AdminInfo {
  id: string
  username: string
  display_name?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  admin: AdminInfo
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  return post<LoginResponse>('/auth/login', { username, password })
}

export function saveToken(resp: LoginResponse): void {
  localStorage.setItem('access_token', resp.access_token)
  localStorage.setItem('admin_info', JSON.stringify(resp.admin))
}

export function logout(): void {
  localStorage.removeItem('access_token')
  localStorage.removeItem('admin_info')
}

export function getAdminInfo(): AdminInfo | null {
  const raw = localStorage.getItem('admin_info')
  return raw ? (JSON.parse(raw) as AdminInfo) : null
}

export async function checkHealth(): Promise<ApiResponse<{ status: string }>> {
  return get('/health') as unknown as Promise<ApiResponse<{ status: string }>>
}
