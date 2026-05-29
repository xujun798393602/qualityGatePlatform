<template>
  <div class="dashboard">
    <!-- Stats Cards -->
    <el-row :gutter="20">
      <el-col :span="4" v-for="stat in statsCards" :key="stat.title">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>{{ stat.title }}</span>
              <el-icon :color="stat.color" :size="24"><component :is="stat.icon" /></el-icon>
            </div>
          </template>
          <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>流水线执行趋势</span>
              <el-radio-group v-model="trendPeriod" size="small" @change="loadPipelineTrend">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <v-chart class="chart" :option="pipelineTrendOption" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>门禁通过率</span>
          </template>
          <v-chart class="chart" :option="gatePassRateOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Pipelines -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>最近流水线运行</span>
          </template>
          <el-table :data="recentPipelines" stripe size="small">
            <el-table-column prop="pipeline_name" label="流水线" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="trigger_type" label="触发方式">
              <template #default="{ row }">
                <el-tag :type="row.trigger_type === 'webhook' ? 'success' : 'info'" size="small">
                  {{ row.trigger_type === 'webhook' ? '自动' : '手动' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="started_at" label="开始时间" width="180">
              <template #default="{ row }">
                {{ row.started_at ? new Date(row.started_at).toLocaleString() : '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- GitLab Integration Info -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>GitLab 集成说明</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="Webhook URL">
              <el-tag type="info">http://your-domain/api/v1/webhooks/gitlab/{repo_id}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="支持事件">
              <el-space>
                <el-tag>Pipeline Hook</el-tag>
                <el-tag>Merge Request Hook</el-tag>
              </el-space>
            </el-descriptions-item>
            <el-descriptions-item label="配置步骤">
              <ol style="margin: 0; padding-left: 20px;">
                <li>在仓库管理中添加仓库并填写 GitLab 访问令牌</li>
                <li>在 GitLab 项目设置中添加 Webhook</li>
                <li>创建流水线和门禁规则</li>
                <li>当 Pipeline 执行完成时自动触发门禁检查</li>
              </ol>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>系统信息</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="系统名称">代码质量门禁管理平台</el-descriptions-item>
            <el-descriptions-item label="版本">0.1.0</el-descriptions-item>
            <el-descriptions-item label="数据库">PostgreSQL</el-descriptions-item>
            <el-descriptions-item label="缓存">Redis</el-descriptions-item>
            <el-descriptions-item label="API 文档">
              <el-link type="primary" href="/docs" target="_blank">/docs</el-link>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { dashboardApi, type DashboardStats, type PipelineTrend, type GatePassRate, type RecentPipeline } from '@/api/dashboard'

use([CanvasRenderer, LineChart, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const trendPeriod = ref('week')
const stats = ref<DashboardStats>({ user_count: 0, team_count: 0, role_count: 0, script_count: 0, repo_count: 0, pipeline_count: 0, gate_count: 0 })
const pipelineTrend = ref<PipelineTrend>({ dates: [], success: [], failed: [], running: [] })
const gatePassRate = ref<GatePassRate>({ passed: 0, failed: 0, rate: 0 })
const recentPipelines = ref<RecentPipeline[]>([])

const statsCards = computed(() => [
  { title: '用户', value: stats.value.user_count, icon: 'User', color: '#409eff' },
  { title: '角色', value: stats.value.role_count, icon: 'UserFilled', color: '#67c23a' },
  { title: '团队', value: stats.value.team_count, icon: 'Team', color: '#e6a23c' },
  { title: '脚本', value: stats.value.script_count, icon: 'Document', color: '#909399' },
  { title: '仓库', value: stats.value.repo_count, icon: 'Folder', color: '#f56c6c' },
  { title: '流水线', value: stats.value.pipeline_count, icon: 'Connection', color: '#00d100' },
  { title: '门禁', value: stats.value.gate_count, icon: 'Lock', color: '#e6a23c' },
  { title: '系统状态', value: '正常', icon: 'CircleCheck', color: '#67c23a' },
])

const pipelineTrendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['成功', '失败', '运行中'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: pipelineTrend.value.dates },
  yAxis: { type: 'value' },
  series: [
    { name: '成功', type: 'line', smooth: true, data: pipelineTrend.value.success, areaStyle: { color: '#67c23a20' }, lineStyle: { color: '#67c23a' } },
    { name: '失败', type: 'line', smooth: true, data: pipelineTrend.value.failed, areaStyle: { color: '#f56c6c20' }, lineStyle: { color: '#f56c6c' } },
    { name: '运行中', type: 'line', smooth: true, data: pipelineTrend.value.running, areaStyle: { color: '#409eff20' }, lineStyle: { color: '#409eff' } },
  ],
}))

const gatePassRateOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    name: '门禁通过率',
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
    labelLine: { show: false },
    data: [
      { value: gatePassRate.value.passed, name: '通过', itemStyle: { color: '#67c23a' } },
      { value: gatePassRate.value.failed, name: '失败', itemStyle: { color: '#f56c6c' } },
    ],
  }],
}))

function getStatusType(status: string) {
  const map: Record<string, string> = { success: 'success', failed: 'danger', running: 'warning', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status: string) {
  const map: Record<string, string> = { success: '成功', failed: '失败', running: '运行中', pending: '等待中' }
  return map[status] || status
}

async function loadStats() {
  try {
    const { data } = await dashboardApi.getStats()
    stats.value = data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

async function loadPipelineTrend() {
  try {
    const { data } = await dashboardApi.getPipelineTrend(trendPeriod.value)
    pipelineTrend.value = data
  } catch (error) {
    console.error('Failed to load pipeline trend:', error)
  }
}

async function loadGatePassRate() {
  try {
    const { data } = await dashboardApi.getGatePassRate()
    gatePassRate.value = data
  } catch (error) {
    console.error('Failed to load gate pass rate:', error)
  }
}

async function loadRecentPipelines() {
  try {
    const { data } = await dashboardApi.getRecentPipelines()
    recentPipelines.value = data
  } catch (error) {
    console.error('Failed to load recent pipelines:', error)
  }
}

onMounted(() => {
  loadStats()
  loadPipelineTrend()
  loadGatePassRate()
  loadRecentPipelines()
})
</script>

<style scoped>
.dashboard { padding: 0; }
.stat-card { height: 140px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.stat-value { font-size: 28px; font-weight: bold; text-align: center; margin-top: 15px; }
.mt-20 { margin-top: 20px; }
.chart { height: 300px; }
</style>
