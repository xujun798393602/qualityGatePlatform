import request from '@/utils/request'
import type { Team } from '@/types'

export const teamsApi = {
  // Get all teams
  getTeams() {
    return request.get<Team[]>('/v1/teams/')
  },

  // Get team by ID
  getTeam(teamId: string) {
    return request.get<Team>(`/v1/teams/${teamId}`)
  },

  // Create team
  createTeam(data: Partial<Team>) {
    return request.post<Team>('/v1/teams/', data)
  },

  // Update team
  updateTeam(teamId: string, data: Partial<Team>) {
    return request.put<Team>(`/v1/teams/${teamId}`, data)
  },

  // Delete team
  deleteTeam(teamId: string) {
    return request.delete<{ message: string }>(`/v1/teams/${teamId}`)
  },
}
