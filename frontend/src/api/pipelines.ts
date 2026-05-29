import request from '@/utils/request'

export interface Pipeline {
  id: string
  name: string
  description?: string
  repo_id: string
  repo_name?: string
  branch: string
  trigger_type: string
  status: string
  stages: PipelineStage[]
  is_active: boolean
  last_run_at?: string
  last_run_status?: string
  created_by?: string
  created_at: string
  updated_at: string
}

export interface PipelineStage {
  name: string
  order: number
  script_id?: string
  script_name?: string
  status?: string
}

export interface PipelineCreate {
  name: string
  description?: string
  repo_id: string
  branch?: string
  trigger_type: string
  stages: Omit<PipelineStage, 'status'>[]
}

export interface PipelineUpdate {
  name?: string
  description?: string
  repo_id?: string
  branch?: string
  trigger_type?: string
  stages?: Omit<PipelineStage, 'status'>[]
  is_active?: boolean
}

export interface PipelineRun {
  id: string
  pipeline_id: string
  status: string
  trigger_type: string
  started_at: string
  finished_at?: string
  duration?: number
  stages: PipelineRunStage[]
}

export interface PipelineRunStage {
  name: string
  status: string
  started_at?: string
  finished_at?: string
  output?: string
}

export const pipelinesApi = {
  // Get all pipelines
  getPipelines() {
    return request.get<Pipeline[]>('/v1/pipelines/')
  },

  // Get pipeline by ID
  getPipeline(pipelineId: string) {
    return request.get<Pipeline>(`/v1/pipelines/${pipelineId}`)
  },

  // Create pipeline
  createPipeline(data: PipelineCreate) {
    return request.post<Pipeline>('/v1/pipelines/', data)
  },

  // Update pipeline
  updatePipeline(pipelineId: string, data: PipelineUpdate) {
    return request.put<Pipeline>(`/v1/pipelines/${pipelineId}`, data)
  },

  // Delete pipeline
  deletePipeline(pipelineId: string) {
    return request.delete<{ message: string }>(`/v1/pipelines/${pipelineId}`)
  },

  // Run pipeline
  runPipeline(pipelineId: string) {
    return request.post<PipelineRun>(`/v1/pipelines/${pipelineId}/run`)
  },

  // Get pipeline runs
  getPipelineRuns(pipelineId: string) {
    return request.get<PipelineRun[]>(`/v1/pipelines/${pipelineId}/runs`)
  },

  // Get pipeline run details
  getPipelineRun(pipelineId: string, runId: string) {
    return request.get<PipelineRun>(`/v1/pipelines/${pipelineId}/runs/${runId}`)
  },
}
