import request from '@/utils/request'

export interface Script {
  id: string
  name: string
  description?: string
  type: string
  content: string
  language: string
  is_active: boolean
  created_by?: string
  created_at: string
  updated_at: string
}

export interface ScriptCreate {
  name: string
  description?: string
  type: string
  content: string
  language: string
}

export interface ScriptUpdate {
  name?: string
  description?: string
  type?: string
  content?: string
  language?: string
  is_active?: boolean
}

export const scriptsApi = {
  // Get all scripts
  getScripts() {
    return request.get<Script[]>('/v1/scripts/')
  },

  // Get script by ID
  getScript(scriptId: string) {
    return request.get<Script>(`/v1/scripts/${scriptId}`)
  },

  // Create script
  createScript(data: ScriptCreate) {
    return request.post<Script>('/v1/scripts/', data)
  },

  // Update script
  updateScript(scriptId: string, data: ScriptUpdate) {
    return request.put<Script>(`/v1/scripts/${scriptId}`, data)
  },

  // Delete script
  deleteScript(scriptId: string) {
    return request.delete<{ message: string }>(`/v1/scripts/${scriptId}`)
  },

  // Execute script
  executeScript(scriptId: string, params?: Record<string, any>) {
    return request.post<{ result: any }>(`/v1/scripts/${scriptId}/execute`, params)
  },
}
