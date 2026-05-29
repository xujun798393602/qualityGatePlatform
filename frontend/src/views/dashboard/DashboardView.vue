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

    <!-- Charts Row 1 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>流水线执行趋势</span>
              <el-radio-group v-model="trendPeriod" size="small">
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

    <!-- Charts Row 2 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>代码质量趋势</span>
          </template>
          <v-chart class="chart" :option="qualityTrendOption" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>团队贡献统计</span>
          </template>
          <v-chart class="chart" :option="teamContribOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Activity -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近流水线运行</span>
          </template>
          <el-table :data="recentPipelines" stripe size="small">
            <el-table-column prop="name" label="流水线" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" width="180" />
          </el-table>
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
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { usersApi } from '@/api/users'
import { rolesApi } from '@/api/roles'
import { teamsApi } from '@/api/teams'
import { scriptsApi } from '@/api/scripts'
import { reposApi } from '@/api/repos'
import { pipelinesApi } from '@/api/pipelines'
import { gatesApi } from '@/api/gates'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const trendPeriod = ref('week')

const stats = ref({
  userCount: 0,
  roleCount: 0,
  teamCount: 0,
  scriptCount: 0,
  repoCount: 0,
  pipelineCount: 0,
  gateCount: 0,
})

const statsCards = computed(() => [
  { title: '用户', value: stats.value.userCount, icon: 'User', color: '#409eff' },
  { title: '角色', value: stats.value.roleCount, icon: 'UserFilled', color: '#67c23a' },
  { title: '团队', value: stats.value.teamCount, icon: 'Team', color: '#e6a23c' },
  { title: '脚本', value: stats.value.scriptCount, icon: 'Document', color: '#909399' },
  { title: '仓库', value: stats.value.repoCount, icon: 'Folder', color: '#f56c6c' },
  { title: '流水线', value: stats.value.pipelineCount, icon: 'Connection', color: '#00d100' },
  { title: '门禁', value: stats.value.gateCount, icon: 'Lock', color: '#e6a23c' },
  { title: '系统状态', value: '正常', icon: 'CircleCheck', color: '#67c23a' },
])

const recentPipelines = ref([
  { name: '构建流水线', status: 'success', time: '2024-01-15 10:30:00' },
  { name: '测试流水线', status: 'running', time: '2024-01-15 10:25:00' },
  { name: '部署流水线', status: 'failed', time: '2024-01-15 10:20:00' },
])

// Pipeline Trend Chart
const pipelineTrendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['成功', '失败', '运行中'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  },
  yAxis: { type: 'value' },
  series: [
    { name: '成功', type: 'line', smooth: true, data: [12, 15, 10, 18, 20, 14, 16], areaStyle: { color: '#67c23a20' }, lineStyle: { color: '#67c23a' } },
    { name: '失败', type: 'line', smooth: true, data: [2, 3, 1, 4, 2, 1, 3], areaStyle: { color: '#f56c6c20' }, lineStyle: { color: '#f56c6c' } },
    { name: '运行中', type: 'line', smooth: true, data: [1, 2, 1, 1, 2, 1, 1], areaStyle: { color: '#409eff20' }, lineStyle: { color: '#409eff' } },
  ],
}))

// Gate Pass Rate Chart
const gatePassRateOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', left: 'left' },
  series: [
    {
      name: '门禁通过率',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: [
        { value: 85, name: '通过', itemStyle: { color: '#67c23a' } },
        { value: 10, name: '失败', itemStyle: { color: '#f56c6c' } },
        { value: 5, name: '跳过', itemStyle: { color: '#909399' } },
      ],
    },
  ],
}))

// Quality Trend Chart
const qualityTrendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['代码覆盖率', '测试通过率', '代码重复率'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ['1月', '2月', '3月', '4月', '5月', '6月'],
  },
  yAxis: { type: 'value', max: 100 },
  series: [
    { name: '代码覆盖率', type: 'line', smooth: true, data: [72, 75, 78, 80, 82, 85], lineStyle: { color: '#409eff' } },
    { name: '测试通过率', type: 'line', smooth: true, data: [88, 90, 92, 91, 93, 95], lineStyle: { color: '#67c23a' } },
    { name: '代码重复率', type: 'line', smooth: true, data: [15, 12, 10, 8, 7, 5], lineStyle: { color: '#e6a23c' } },
  ],
}))

// Team Contribution Chart
const teamContribOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: ['提交数', 'MR 数'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: ['前端组', '后端组', '测试组', '运维组'] },
  yAxis: { type: 'value' },
  series: [
    { name: '提交数', type: 'bar', data: [120, 95, 45, 30], itemStyle: { color: '#409eff' } },
    { name: 'MR 数', type: 'bar', data: [25, 20, 10, 5], itemStyle: { color: '#67c23a' } },
  ],
}))

function getStatusType(status: string) {
  const map: Record<string, string> = { success: 'success', failed: 'danger', running: 'warning', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status: string) {
  const map: Record<string, string> = { success: '成功', failed: '失败', running: '运行中', pending: '等待中' }
  return map[status] || status
}

onMounted(async () => {
  try {
    const results = await Promise.allSettled([
      usersApi.getUsers(),
      rolesApi.getRoles(),
      teamsApi.getTeams(),
      scriptsApi.getScripts(),
      reposApi.getRepos(),
      pipelinesApi.getPipelines(),
      gatesApi.getGates(),
    ])
    const [usersRes, rolesRes, teamsRes, scriptsRes, reposRes, pipelinesRes, gatesRes] = results
    if (usersRes.status === 'fulfilled') stats.value.userCount = usersRes.value.data.length
    if (rolesRes.status === 'fulfilled') stats.value.roleCount = rolesRes.value.data.length
    if (teamsRes.status === 'fulfilled') stats.value.teamCount = teamsRes.value.data.length
    if (scriptsRes.status === 'fulfilled') stats.value.scriptCount = scriptsRes.value.data.length
    if (reposRes.status === 'fulfilled') stats.value.repoCount = reposRes.value.data.length
    if (pipelinesRes.status === 'fulfilled') stats.value.pipelineCount = pipelinesRes.value.data.length
    if (gatesRes.status === 'fulfilled') stats.value.gateCount = gatesRes.value.data.length
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}
.stat-card {
  height: 140px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  margin-top: 15px;
}
.mt-20 {
  margin-top: 20px;
}
.chart {
  height: 300px;
}
</style>
