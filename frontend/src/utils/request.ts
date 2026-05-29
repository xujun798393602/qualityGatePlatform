import axios, { type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()

    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // Try to refresh token
      if (authStore.refreshToken) {
        try {
          await authStore.refreshAccessToken()
          originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`
          return service(originalRequest)
        } catch (refreshError) {
          // Refresh failed, logout
          authStore.logout()
          router.push('/login')
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, logout
        authStore.logout()
        router.push('/login')
      }
    }

    // Show error message
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)

    return Promise.reject(error)
  }
)

export default service
