import { get } from './request'
import type { DashboardOverview, CityStat } from '@/types/dashboard'

export async function fetchOverview(): Promise<DashboardOverview> {
  return get<DashboardOverview>('/dashboard/overview')
}

export async function fetchCityStats(): Promise<CityStat[]> {
  return get<CityStat[]>('/dashboard/city-stats')
}
