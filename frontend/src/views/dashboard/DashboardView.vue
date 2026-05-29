<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>用户</span>
              <el-icon color="#409eff"><User /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.userCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>角色</span>
              <el-icon color="#67c23a"><UserFilled /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.roleCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>团队</span>
              <el-icon color="#e6a23c"><Team /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.teamCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>脚本</span>
              <el-icon color="#909399"><Document /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.scriptCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>仓库</span>
              <el-icon color="#f56c6c"><Folder /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.repoCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>流水线</span>
              <el-icon color="#00d100"><Connection /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.pipelineCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>门禁</span>
              <el-icon color="#e6a23c"><Lock /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.gateCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
              <el-icon color="#67c23a"><CircleCheck /></el-icon>
            </div>
          </template>
          <div class="stat-value status-ok">正常</div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <el-space wrap>
            <el-button type="primary" @click="$router.push('/users')">
              <el-icon><User /></el-icon>
              用户管理
            </el-button>
            <el-button type="success" @click="$router.push('/scripts')">
              <el-icon><Document /></el-icon>
              脚本管理
            </el-button>
            <el-button type="warning" @click="$router.push('/pipelines')">
              <el-icon><Connection /></el-icon>
              流水线管理
            </el-button>
            <el-button type="danger" @click="$router.push('/gates')">
              <el-icon><Lock /></el-icon>
              门禁管理
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>系统信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统名称">代码质量门禁管理平台</el-descriptions-item>
            <el-descriptions-item label="版本">0.1.0</el-descriptions-item>
            <el-descriptions-item label="API 文档">
              <el-link type="primary" href="/docs" target="_blank">/docs</el-link>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>模块概览</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户管理">管理系统用户和权限</el-descriptions-item>
            <el-descriptions-item label="脚本管理">管理测试和构建脚本</el-descriptions-item>
            <el-descriptions-item label="仓库管理">管理 Git 仓库配置</el-descriptions-item>
            <el-descriptions-item label="流水线管理">管理 CI/CD 流水线</el-descriptions-item>
            <el-descriptions-item label="门禁管理">管理质量门禁规则</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usersApi } from '@/api/users'
import { rolesApi } from '@/api/roles'
import { teamsApi } from '@/api/teams'
import { scriptsApi } from '@/api/scripts'
import { reposApi } from '@/api/repos'
import { pipelinesApi } from '@/api/pipelines'
import { gatesApi } from '@/api/gates'

const stats = ref({
  userCount: 0,
  roleCount: 0,
  teamCount: 0,
  scriptCount: 0,
  repoCount: 0,
  pipelineCount: 0,
  gateCount: 0,
})

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
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  text-align: center;
  margin-top: 15px;
}

.status-ok {
  color: #67c23a;
  font-size: 24px;
}

.mt-20 {
  margin-top: 20px;
}
</style>
