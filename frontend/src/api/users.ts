import request from '@/utils/request'
import type { User, UserCreate, UserUpdate } from '@/types'

export const usersApi = {
  // Get all users
  getUsers() {
    return request.get<User[]>('/v1/users/')
  },

  // Get user by ID
  getUser(userId: string) {
    return request.get<User>(`/v1/users/${userId}`)
  },

  // Create user
  createUser(data: UserCreate) {
    return request.post<User>('/v1/users/', data)
  },

  // Update user
  updateUser(userId: string, data: UserUpdate) {
    return request.put<User>(`/v1/users/${userId}`, data)
  },

  // Delete user
  deleteUser(userId: string) {
    return request.delete<{ message: string }>(`/v1/users/${userId}`)
  },
}
