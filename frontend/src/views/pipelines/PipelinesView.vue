<template>
  <div class="pipelines-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>流水线管理</span>
          <el-button type="primary" @click="showDialog()">
            <el-icon><Plus /></el-icon>
            新增流水线
          </el-button>
        </div>
      </template>

      <el-table :data="pipelines" v-loading="loading" stripe>
        <el-table-column prop="name" label="流水线名称" width="180" />
        <el-table-column prop="branch" label="分支" width="120" />
        <el-table-column prop="trigger_type" label="触发方式" width="120">
          <template #default="{ row }">
            <el-tag :type="row.trigger_type === 'auto' ? 'success' : 'info'">
              {{ row.trigger_type === 'auto' ? '自动' : '手动' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="阶段数" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.stages?.length || 0 }} 个</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_run_at" label="最后运行" width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="success" link @click="handleRun(row)">
              <el-icon><VideoPlay /></el-icon>运行
            </el-button>
            <el-button type="info" link @click="showRuns(row)">
              <el-icon><List /></el-icon>历史
            </el-button>
            <el-popconfirm title="确定删除该流水线吗？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link><el-icon><Delete /></el-icon>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑流水线' : '新增流水线'" width="800px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="流水线名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入流水线名称" />
        </el-form-item>
        <el-form-item label="关联仓库" prop="repo_id">
          <el-select v-model="form.repo_id" placeholder="请选择仓库" clearable>
            <el-option v-for="repo in repos" :key="repo.id" :label="repo.name" :value="repo.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分支" prop="branch">
          <el-input v-model="form.branch" placeholder="请输入分支" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入流水线描述" />
        </el-form-item>

        <!-- 流水线阶段配置 -->
        <el-divider content-position="left">
          <div class="divider-title">
            <span>流水线阶段</span>
            <el-button type="primary" size="small" @click="addStage" class="add-stage-btn">
              <el-icon><Plus /></el-icon>
              添加阶段
            </el-button>
          </div>
        </el-divider>

        <div class="stages-container">
          <div v-for="(stage, index) in form.stages" :key="index" class="stage-item">
            <div class="stage-header">
              <span class="stage-number">阶段 {{ index + 1 }}</span>
              <el-button type="danger" size="small" @click="removeStage(index)" class="delete-stage-btn">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
            <el-row :gutter="15">
              <el-col :span="8">
                <el-form-item label="阶段名称" label-width="80px">
                  <el-input v-model="stage.name" placeholder="如：构建、测试、部署" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="执行脚本" label-width="80px">
                  <el-select v-model="stage.script_id" placeholder="选择脚本" clearable>
                    <el-option v-for="script in scripts" :key="script.id" :label="script.name" :value="script.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="触发方式" label-width="80px">
                  <el-select v-model="stage.trigger_type" placeholder="选择触发方式">
                    <el-option label="手动触发" value="manual" />
                    <el-option label="自动触发" value="auto" />
                    <el-option label="Webhook 触发" value="webhook" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 空状态提示 -->
          <el-empty v-if="form.stages.length === 0" description="暂无阶段，请点击上方按钮添加" :image-size="60" />
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 运行历史对话框 -->
    <el-dialog v-model="runsDialogVisible" title="运行历史" width="900px">
      <el-table :data="pipelineRuns" v-loading="runsLoading" stripe>
        <el-table-column prop="id" label="运行ID" width="280" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" label="触发方式" width="120" />
        <el-table-column prop="started_at" label="开始时间" width="180" />
        <el-table-column prop="finished_at" label="结束时间" width="180" />
        <el-table-column prop="duration" label="耗时(秒)" width="100" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { pipelinesApi, type Pipeline, type PipelineCreate, type PipelineRun } from '@/api/pipelines'
import { reposApi, type Repo } from '@/api/repos'
import { scriptsApi, type Script } from '@/api/scripts'

const pipelines = ref<Pipeline[]>([])
const repos = ref<Repo[]>([])
const scripts = ref<Script[]>([])
const pipelineRuns = ref<PipelineRun[]>([])
const loading = ref(false)
const runsLoading = ref(false)
const dialogVisible = ref(false)
const runsDialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const editId = ref('')
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  repo_id: '',
  branch: 'main',
  trigger_type: 'manual',
  description: '',
  stages: [] as { name: string; script_id: string; order: number; trigger_type: string }[],
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入流水线名称', trigger: 'blur' }],
}

function addStage() {
  form.stages.push({
    name: '',
    script_id: '',
    order: form.stages.length + 1,
    trigger_type: 'manual',
  })
}

function removeStage(index: number) {
  form.stages.splice(index, 1)
  form.stages.forEach((stage, i) => { stage.order = i + 1 })
}

function getStatusType(status: string) {
  const map: Record<string, string> = { success: 'success', failed: 'danger', running: 'warning', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status: string) {
  const map: Record<string, string> = { success: '成功', failed: '失败', running: '运行中', pending: '等待中' }
  return map[status] || status
}

async function loadData() {
  loading.value = true
  try {
    const [pipelinesRes, reposRes, scriptsRes] = await Promise.allSettled([
      pipelinesApi.getPipelines(),
      reposApi.getRepos(),
      scriptsApi.getScripts(),
    ])
    if (pipelinesRes.status === 'fulfilled') pipelines.value = pipelinesRes.value.data
    if (reposRes.status === 'fulfilled') repos.value = reposRes.value.data
    if (scriptsRes.status === 'fulfilled') scripts.value = scriptsRes.value.data
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

function showDialog(pipeline?: Pipeline) {
  if (pipeline) {
    isEdit.value = true
    editId.value = pipeline.id
    form.name = pipeline.name
    form.repo_id = pipeline.repo_id || ''
    form.branch = pipeline.branch
    form.trigger_type = pipeline.trigger_type
    form.description = pipeline.description || ''
    form.stages = (pipeline.stages || []).map(s => ({
      name: s.name,
      script_id: s.script_id || '',
      order: s.order,
      trigger_type: pipeline.trigger_type,
    }))
  } else {
    isEdit.value = false
    editId.value = ''
    form.name = ''
    form.repo_id = ''
    form.branch = 'main'
    form.trigger_type = 'manual'
    form.description = ''
    form.stages = []
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        await pipelinesApi.updatePipeline(editId.value, form)
        ElMessage.success('更新成功')
      } else {
        await pipelinesApi.createPipeline(form as PipelineCreate)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

async function handleRun(pipeline: Pipeline) {
  try {
    await pipelinesApi.runPipeline(pipeline.id)
    ElMessage.success('流水线已启动')
    loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '运行失败')
  }
}

async function showRuns(pipeline: Pipeline) {
  runsLoading.value = true
  runsDialogVisible.value = true
  try {
    const { data } = await pipelinesApi.getPipelineRuns(pipeline.id)
    pipelineRuns.value = data
  } catch (error) {
    console.error('Failed to load runs:', error)
  } finally {
    runsLoading.value = false
  }
}

async function handleDelete(pipelineId: string) {
  try {
    await pipelinesApi.deletePipeline(pipelineId)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 分隔线标题样式 */
.divider-title {
  display: flex;
  align-items: center;
  gap: 15px;
}

.add-stage-btn {
  margin-left: 10px;
}

/* 阶段容器 */
.stages-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px 0;
}

/* 单个阶段样式 */
.stage-item {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stage-number {
  font-weight: 600;
  color: #409eff;
  font-size: 14px;
}

.delete-stage-btn {
  margin-left: auto;
}
</style>
