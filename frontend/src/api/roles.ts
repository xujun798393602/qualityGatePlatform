import request from '@/utils/request'
import type { Role } from '@/types'

export const rolesApi = {
  // Get all roles
  getRoles() {
    return request.get<Role[]>('/v1/roles/')
  },

  // Get role by ID
  getRole(roleId: string) {
    return request.get<Role>(`/v1/roles/${roleId}`)
  },

  // Create role
  createRole(data: Partial<Role>) {
    return request.post<Role>('/v1/roles/', data)
  },

  // Update role
  updateRole(roleId: string, data: Partial<Role>) {
    return request.put<Role>(`/v1/roles/${roleId}`, data)
  },

  // Delete role
  deleteRole(roleId: string) {
    return request.delete<{ message: string }>(`/v1/roles/${roleId}`)
  },
}
