import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as any,
  }),

  getters: {
    accessToken: () => localStorage.getItem('accessToken') || '',
    refreshToken: () => localStorage.getItem('refreshToken') || '',
    isAuthenticated: () => !!localStorage.getItem('accessToken'),
  },

  actions: {
    async login(username: string, password: string) {
      const { data } = await authApi.login(username, password)
      localStorage.setItem('accessToken', data.access_token)
      localStorage.setItem('refreshToken', data.refresh_token)
      return data
    },

    async refreshAccessToken() {
      const token = localStorage.getItem('refreshToken')
      if (!token) {
        throw new Error('No refresh token')
      }
      const { data } = await authApi.refreshToken({ refresh_token: token })
      localStorage.setItem('accessToken', data.access_token)
      localStorage.setItem('refreshToken', data.refresh_token)
      return data
    },

    logout() {
      this.user = null
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    },
  },
})
