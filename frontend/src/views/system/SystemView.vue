<template>
  <div class="system-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
          <el-button type="primary" :loading="saving" @click="handleSave">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="config"
        label-width="120px"
        v-loading="loading"
      >
        <el-divider content-position="left">基本配置</el-divider>
        <el-form-item label="系统名称">
          <el-input v-model="config.app_name" placeholder="请输入系统名称" />
        </el-form-item>
        <el-form-item label="系统版本">
          <el-input v-model="config.app_version" disabled />
        </el-form-item>

        <el-divider content-position="left">安全配置</el-divider>
        <el-form-item label="JWT 过期时间">
          <el-input-number v-model="config.jwt_expire_minutes" :min="5" :max="1440" />
          <span class="form-tip">分钟</span>
        </el-form-item>
        <el-form-item label="最大登录尝试">
          <el-input-number v-model="config.max_login_attempts" :min="1" :max="10" />
          <span class="form-tip">次</span>
        </el-form-item>
        <el-form-item label="锁定时间">
          <el-input-number v-model="config.lockout_duration_minutes" :min="1" :max="60" />
          <span class="form-tip">分钟</span>
        </el-form-item>

        <el-divider content-position="left">其他配置</el-divider>
        <el-form-item label="调试模式">
          <el-switch v-model="config.debug" active-text="开启" inactive-text="关闭" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { systemApi } from '@/api/system'

const loading = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()

const config = reactive({
  app_name: '代码质量门禁管理平台',
  app_version: '0.1.0',
  jwt_expire_minutes: 30,
  max_login_attempts: 5,
  lockout_duration_minutes: 30,
  debug: false,
})

// Load config
async function loadConfig() {
  loading.value = true
  try {
    const { data } = await systemApi.getConfig()
    if (data && Object.keys(data).length > 0) {
      Object.assign(config, data)
    }
  } catch (error) {
    console.error('Failed to load config:', error)
  } finally {
    loading.value = false
  }
}

// Save config
async function handleSave() {
  saving.value = true
  try {
    await systemApi.updateConfig(config)
    ElMessage.success('保存成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 8px;
  color: #909399;
  font-size: 13px;
}
</style>
