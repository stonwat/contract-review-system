import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/api'

/** 扩展 axios 配置，增加 silent 选项：静默请求不弹全局错误提示 */
export interface SilentRequestConfig extends AxiosRequestConfig {
  /** 为 true 时，跳过拦截器中的 ElMessage 弹窗（401 跳转仍生效） */
  silent?: boolean
}

const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 30000,
})

// 请求拦截器：自动附加 Token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理，返回 response 但在泛型函数中解包 data
request.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResponse
    if (res.code !== 0) {
      ElMessage.error(res.message)
      if (res.code === 4001) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('role')
        localStorage.removeItem('city')
        window.location.href = '/#/login'
      }
      return Promise.reject(new Error(res.message))
    }
    // 将解包后的 data 挂到 response 上，供泛型函数使用
    response.data = res.data
    return response
  },
  (error) => {
    const status = error.response?.status
    const msg = error.response?.data?.detail || error.message || '网络错误'
    const silent = (error.config as SilentRequestConfig)?.silent

    // 401 未认证 → 跳转登录（无论是否 silent 都要跳转）
    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('role')
      localStorage.removeItem('city')
      window.location.href = '/#/login'
      return Promise.reject(error)
    }

    // silent 请求：跳过所有弹窗，由调用方自行处理
    if (silent) {
      return Promise.reject(error)
    }

    // 403 无权限
    if (status === 403) {
      ElMessage.warning('无权限执行此操作')
      return Promise.reject(error)
    }

    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

/** 泛型 get，自动解包 data */
export async function get<T>(url: string, config?: SilentRequestConfig): Promise<T> {
  const resp = await request.get(url, config)
  return resp.data as T
}

/** 泛型 post，自动解包 data */
export async function post<T>(url: string, body?: unknown, config?: SilentRequestConfig): Promise<T> {
  const resp = await request.post(url, body, config)
  return resp.data as T
}

/** 泛型 put，自动解包 data */
export async function put<T>(url: string, body?: unknown, config?: SilentRequestConfig): Promise<T> {
  const resp = await request.put(url, body, config)
  return resp.data as T
}

/** 泛型 del，自动解包 data */
export async function del<T>(url: string, config?: SilentRequestConfig): Promise<T> {
  const resp = await request.delete(url, config)
  return resp.data as T
}

export default request
