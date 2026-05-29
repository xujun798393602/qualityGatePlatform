import request from '@/utils/request'

export interface DashboardStats {
  user_count: number
  team_count: number
  role_count: number
  script_count: number
  repo_count: number
  pipeline_count: number
  gate_count: number
}

export interface PipelineTrend {
  dates: string[]
  success: number[]
  failed: number[]
  running: number[]
}

export interface GatePassRate {
  passed: number
  failed: number
  rate: number
}

export interface RecentPipeline {
  id: string
  pipeline_name: string
  status: string
  trigger_type: string
  started_at: string
  duration: number | null
}

export const dashboardApi = {
  // 获取统计数据
  getStats() {
    return request.get<DashboardStats>('/v1/dashboard/stats')
  },

  // 获取流水线趋势
  getPipelineTrend(period: string = 'week') {
    return request.get<PipelineTrend>(`/v1/dashboard/pipeline-trend?period=${period}`)
  },

  // 获取门禁通过率
  getGatePassRate() {
    return request.get<GatePassRate>('/v1/dashboard/gate-pass-rate')
  },

  // 获取最近流水线
  getRecentPipelines(limit: number = 10) {
    return request.get<RecentPipeline[]>(`/v1/dashboard/recent-pipelines?limit=${limit}`)
  },
}
