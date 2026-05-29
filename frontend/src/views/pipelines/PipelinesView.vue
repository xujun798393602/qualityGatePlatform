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
        <el-table-column prop="repo_name" label="关联仓库" width="150" />
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
        <el-table-column prop="last_run_at" label="最后运行" width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="success" link @click="handleRun(row)">
              <el-icon><VideoPlay /></el-icon>
              运行
            </el-button>
            <el-button type="info" link @click="showRuns(row)">
              <el-icon><List /></el-icon>
              历史
            </el-button>
            <el-popconfirm title="确定删除该流水线吗？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑流水线' : '新增流水线'" width="700px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="流水线名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入流水线名称" />
        </el-form-item>
        <el-form-item label="关联仓库" prop="repo_id">
          <el-select v-model="form.repo_id" placeholder="请选择仓库">
            <el-option v-for="repo in repos" :key="repo.id" :label="repo.name" :value="repo.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分支" prop="branch">
          <el-input v-model="form.branch" placeholder="请输入分支" />
        </el-form-item>
        <el-form-item label="触发方式" prop="trigger_type">
          <el-radio-group v-model="form.trigger_type">
            <el-radio value="manual">手动触发</el-radio>
            <el-radio value="auto">自动触发</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入流水线描述" />
        </el-form-item>
        <el-divider content-position="left">流水线阶段</el-divider>
        <div v-for="(stage, index) in form.stages" :key="index" class="stage-item">
          <el-row :gutter="10">
            <el-col :span="8">
              <el-input v-model="stage.name" placeholder="阶段名称" />
            </el-col>
            <el-col :span="8">
              <el-select v-model="stage.script_id" placeholder="选择脚本">
                <el-option v-for="script in scripts" :key="script.id" :label="script.name" :value="script.id" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-input-number v-model="stage.order" :min="1" placeholder="顺序" />
            </el-col>
            <el-col :span="4">
              <el-button type="danger" @click="removeStage(index)">删除</el-button>
            </el-col>
          </el-row>
        </div>
        <el-button type="primary" @click="addStage" style="margin-top: 10px;">
          <el-icon><Plus /></el-icon>
          添加阶段
        </el-button>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Runs Dialog -->
    <el-dialog v-model="runsDialogVisible" title="运行历史" width="800px">
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
  stages: [] as { name: string; script_id: string; order: number }[],
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入流水线名称', trigger: 'blur' }],
  repo_id: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  trigger_type: [{ required: true, message: '请选择触发方式', trigger: 'change' }],
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    running: 'warning',
    pending: 'info',
  }
  return map[status] || 'info'
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    success: '成功',
    failed: '失败',
    running: '运行中',
    pending: '等待中',
  }
  return map[status] || status
}

function addStage() {
  form.stages.push({ name: '', script_id: '', order: form.stages.length + 1 })
}

function removeStage(index: number) {
  form.stages.splice(index, 1)
  form.stages.forEach((stage, i) => { stage.order = i + 1 })
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
    form.repo_id = pipeline.repo_id
    form.branch = pipeline.branch
    form.trigger_type = pipeline.trigger_type
    form.description = pipeline.description || ''
    form.stages = pipeline.stages.map(s => ({ name: s.name, script_id: s.script_id || '', order: s.order }))
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
.stage-item {
  margin-bottom: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
