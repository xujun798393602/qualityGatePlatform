import request from '@/utils/request'
import type { SystemConfig } from '@/types'

export const systemApi = {
  // Get system config
  getConfig() {
    return request.get<SystemConfig>('/v1/system/config')
  },

  // Update system config
  updateConfig(data: SystemConfig) {
    return request.put<SystemConfig>('/v1/system/config', data)
  },
}
