import request from '@/utils/request'

export interface Repo {
  id: string
  name: string
  url: string
  description?: string
  branch: string
  type: string
  is_active: boolean
  last_sync_at?: string
  created_by?: string
  created_at: string
  updated_at: string
}

export interface RepoCreate {
  name: string
  url: string
  description?: string
  branch?: string
  type: string
}

export interface RepoUpdate {
  name?: string
  url?: string
  description?: string
  branch?: string
  type?: string
  is_active?: boolean
}

export const reposApi = {
  // Get all repos
  getRepos() {
    return request.get<Repo[]>('/v1/repos/')
  },

  // Get repo by ID
  getRepo(repoId: string) {
    return request.get<Repo>(`/v1/repos/${repoId}`)
  },

  // Create repo
  createRepo(data: RepoCreate) {
    return request.post<Repo>('/v1/repos/', data)
  },

  // Update repo
  updateRepo(repoId: string, data: RepoUpdate) {
    return request.put<Repo>(`/v1/repos/${repoId}`, data)
  },

  // Delete repo
  deleteRepo(repoId: string) {
    return request.delete<{ message: string }>(`/v1/repos/${repoId}`)
  },

  // Sync repo
  syncRepo(repoId: string) {
    return request.post<{ message: string }>(`/v1/repos/${repoId}/sync`)
  },

  // Get repo branches
  getRepoBranches(repoId: string) {
    return request.get<string[]>(`/v1/repos/${repoId}/branches`)
  },
}
