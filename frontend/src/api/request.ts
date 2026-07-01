import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/api'

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

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResponse
    if (res.code !== 0) {
      ElMessage.error(res.message)
      if (res.code === 4001) {
        localStorage.removeItem('access_token')
        window.location.href = '/#/login'
      }
      return Promise.reject(new Error(res.message))
    }
    return res.data
  },
  (error) => {
    const msg = error.response?.data?.detail || error.message || '网络错误'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

/** 泛型 get，自动解包 data */
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return (await request.get(url, config)) as unknown as T
}

export async function post<T>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> {
  return (await request.post(url, body, config)) as unknown as T
}

export async function put<T>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> {
  return (await request.put(url, body, config)) as unknown as T
}

export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return (await request.delete(url, config)) as unknown as T
}

export default request
