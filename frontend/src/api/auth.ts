import { get, post } from './request'

export type Role = 'super_admin' | 'city_admin' | 'viewer'

export interface AdminInfo {
  id: string
  username: string
  display_name?: string
  role: Role
  city: string | null
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
  localStorage.setItem('role', resp.admin.role)
  if (resp.admin.city) {
    localStorage.setItem('city', resp.admin.city)
  } else {
    localStorage.removeItem('city')
  }
}

export function logout(): void {
  localStorage.removeItem('access_token')
  localStorage.removeItem('admin_info')
  localStorage.removeItem('role')
  localStorage.removeItem('city')
}

export function getAdminInfo(): AdminInfo | null {
  const raw = localStorage.getItem('admin_info')
  return raw ? (JSON.parse(raw) as AdminInfo) : null
}

export function getRole(): Role {
  return (localStorage.getItem('role') || 'viewer') as Role
}

export function getCity(): string | null {
  return localStorage.getItem('city')
}

export async function checkHealth(): Promise<{ status: string }> {
  return get<{ status: string }>('/health')
}
