import { get } from './request'

export async function fetchCities(): Promise<string[]> {
  return get<string[]>('/cities')
}
