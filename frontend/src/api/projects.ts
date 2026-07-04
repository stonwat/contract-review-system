import { get, put } from './request'
import type { Project } from '@/types/project'

export async function fetchProjects(params?: {
  city?: string
  audit_status?: string
  llm_analyzed?: boolean
  project_risk?: string
}): Promise<{ items: Project[]; total: number }> {
  return get('/projects', { params })
}

export async function fetchProject(contractNo: string): Promise<Project> {
  return get<Project>(`/projects/${contractNo}`)
}

export async function updateProject(contractNo: string, body: Partial<Project>): Promise<unknown> {
  return put(`/projects/${contractNo}`, body)
}
