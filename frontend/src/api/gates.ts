import request from '@/utils/request'

export interface Gate {
  id: string
  name: string
  description?: string
  pipeline_id: string
  pipeline_name?: string
  type: string
  conditions: GateCondition[]
  is_active: boolean
  created_by?: string
  created_at: string
  updated_at: string
}

export interface GateCondition {
  metric: string
  operator: string
  value: string
  unit?: string
}

export interface GateCreate {
  name: string
  description?: string
  pipeline_id: string
  type: string
  conditions: GateCondition[]
}

export interface GateUpdate {
  name?: string
  description?: string
  pipeline_id?: string
  type?: string
  conditions?: GateCondition[]
  is_active?: boolean
}

export interface GateCheckResult {
  gate_id: string
  gate_name: string
  passed: boolean
  conditions: {
    metric: string
    expected: string
    actual: string
    passed: boolean
  }[]
  checked_at: string
}

export const gatesApi = {
  // Get all gates
  getGates() {
    return request.get<Gate[]>('/v1/gates/')
  },

  // Get gate by ID
  getGate(gateId: string) {
    return request.get<Gate>(`/v1/gates/${gateId}`)
  },

  // Create gate
  createGate(data: GateCreate) {
    return request.post<Gate>('/v1/gates/', data)
  },

  // Update gate
  updateGate(gateId: string, data: GateUpdate) {
    return request.put<Gate>(`/v1/gates/${gateId}`, data)
  },

  // Delete gate
  deleteGate(gateId: string) {
    return request.delete<{ message: string }>(`/v1/gates/${gateId}`)
  },

  // Check gate
  checkGate(gateId: string, pipelineRunId: string) {
    return request.post<GateCheckResult>(`/v1/gates/${gateId}/check`, { pipeline_run_id: pipelineRunId })
  },

  // Get gate check history
  getGateChecks(gateId: string) {
    return request.get<GateCheckResult[]>(`/v1/gates/${gateId}/checks`)
  },
}
