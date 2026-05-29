import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string>(localStorage.getItem('accessToken') || '')
  const refreshToken = ref<string>(localStorage.getItem('refreshToken') || '')
  const user = ref<User | null>(null)

  // Login
  async function login(username: string, password: string) {
    const { data } = await authApi.login(username, password)
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    localStorage.setItem('accessToken', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    return data
  }

  // Refresh access token
  async function refreshAccessToken() {
    if (!refreshToken.value) {
      throw new Error('No refresh token')
    }
    const { data } = await authApi.refreshToken({ refresh_token: refreshToken.value })
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    localStorage.setItem('accessToken', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    return data
  }

  // Logout
  function logout() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }

  // Check if authenticated
  function isAuthenticated() {
    return !!accessToken.value
  }

  return {
    accessToken,
    refreshToken,
    user,
    login,
    refreshAccessToken,
    logout,
    isAuthenticated,
  }
})
