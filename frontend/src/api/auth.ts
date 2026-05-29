import request from '@/utils/request'
import type { Token, TokenRefresh } from '@/types'

export const authApi = {
  // Login
  login(username: string, password: string) {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    return request.post<Token>('/v1/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },

  // Refresh token
  refreshToken(data: TokenRefresh) {
    return request.post<Token>('/v1/auth/refresh', data)
  },
}
