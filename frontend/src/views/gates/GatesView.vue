<template>
  <div class="gates-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>门禁管理</span>
          <el-button type="primary" @click="showDialog()">
            <el-icon><Plus /></el-icon>
            新增门禁
          </el-button>
        </div>
      </template>

      <el-table :data="gates" v-loading="loading" stripe>
        <el-table-column prop="name" label="门禁名称" width="180" />
        <el-table-column prop="pipeline_name" label="关联流水线" width="180" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="条件数量" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.conditions?.length || 0 }} 个</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="info" link @click="showChecks(row)">
              <el-icon><List /></el-icon>
              历史
            </el-button>
            <el-popconfirm title="确定删除该门禁吗？" @confirm="handleDelete(row.id)">
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑门禁' : '新增门禁'" width="700px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="门禁名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入门禁名称" />
        </el-form-item>
        <el-form-item label="关联流水线" prop="pipeline_id">
          <el-select v-model="form.pipeline_id" placeholder="请选择流水线">
            <el-option v-for="pipeline in pipelines" :key="pipeline.id" :label="pipeline.name" :value="pipeline.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型">
            <el-option label="质量门禁" value="quality" />
            <el-option label="安全门禁" value="security" />
            <el-option label="性能门禁" value="performance" />
            <el-option label="覆盖率门禁" value="coverage" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入门禁描述" />
        </el-form-item>
        <el-divider content-position="left">门禁条件</el-divider>
        <div v-for="(condition, index) in form.conditions" :key="index" class="condition-item">
          <el-row :gutter="10">
            <el-col :span="6">
              <el-select v-model="condition.metric" placeholder="指标">
                <el-option label="代码覆盖率" value="coverage" />
                <el-option label="测试通过率" value="test_pass_rate" />
                <el-option label="代码重复率" value="duplication" />
                <el-option label="圈复杂度" value="complexity" />
                <el-option label="漏洞数量" value="vulnerabilities" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-select v-model="condition.operator" placeholder="运算符">
                <el-option label=">=" value=">=" />
                <el-option label="<=" value="<=" />
                <el-option label="==" value="==" />
                <el-option label="!=" value="!=" />
                <el-option label=">" value=">" />
                <el-option label="<" value="<" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-input v-model="condition.value" placeholder="阈值" />
            </el-col>
            <el-col :span="4">
              <el-input v-model="condition.unit" placeholder="单位" />
            </el-col>
            <el-col :span="4">
              <el-button type="danger" @click="removeCondition(index)">删除</el-button>
            </el-col>
          </el-row>
        </div>
        <el-button type="primary" @click="addCondition" style="margin-top: 10px;">
          <el-icon><Plus /></el-icon>
          添加条件
        </el-button>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Checks Dialog -->
    <el-dialog v-model="checksDialogVisible" title="检查历史" width="800px">
      <el-table :data="gateChecks" v-loading="checksLoading" stripe>
        <el-table-column prop="checked_at" label="检查时间" width="180" />
        <el-table-column prop="passed" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.passed ? 'success' : 'danger'">
              {{ row.passed ? '通过' : '未通过' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="条件详情" min-width="400">
          <template #default="{ row }">
            <div v-for="(cond, index) in row.conditions" :key="index" class="check-condition">
              <el-tag :type="cond.passed ? 'success' : 'danger'" size="small">
                {{ cond.metric }}: {{ cond.actual }} {{ cond.operator }} {{ cond.expected }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { gatesApi, type Gate, type GateCreate, type GateCheckResult } from '@/api/gates'
import { pipelinesApi, type Pipeline } from '@/api/pipelines'

const gates = ref<Gate[]>([])
const pipelines = ref<Pipeline[]>([])
const gateChecks = ref<GateCheckResult[]>([])
const loading = ref(false)
const checksLoading = ref(false)
const dialogVisible = ref(false)
const checksDialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const editId = ref('')
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  pipeline_id: '',
  type: 'quality',
  description: '',
  conditions: [] as { metric: string; operator: string; value: string; unit: string }[],
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入门禁名称', trigger: 'blur' }],
  pipeline_id: [{ required: true, message: '请选择流水线', trigger: 'change' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

function getTypeTag(type: string) {
  const map: Record<string, string> = {
    quality: '',
    security: 'danger',
    performance: 'warning',
    coverage: 'success',
  }
  return map[type] || ''
}

function getTypeText(type: string) {
  const map: Record<string, string> = {
    quality: '质量',
    security: '安全',
    performance: '性能',
    coverage: '覆盖率',
  }
  return map[type] || type
}

function addCondition() {
  form.conditions.push({ metric: '', operator: '>=', value: '', unit: '' })
}

function removeCondition(index: number) {
  form.conditions.splice(index, 1)
}

async function loadData() {
  loading.value = true
  try {
    const [gatesRes, pipelinesRes] = await Promise.allSettled([
      gatesApi.getGates(),
      pipelinesApi.getPipelines(),
    ])
    if (gatesRes.status === 'fulfilled') gates.value = gatesRes.value.data
    if (pipelinesRes.status === 'fulfilled') pipelines.value = pipelinesRes.value.data
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

function showDialog(gate?: Gate) {
  if (gate) {
    isEdit.value = true
    editId.value = gate.id
    form.name = gate.name
    form.pipeline_id = gate.pipeline_id
    form.type = gate.type
    form.description = gate.description || ''
    form.conditions = gate.conditions.map(c => ({ ...c, unit: c.unit || '' }))
  } else {
    isEdit.value = false
    editId.value = ''
    form.name = ''
    form.pipeline_id = ''
    form.type = 'quality'
    form.description = ''
    form.conditions = []
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
        await gatesApi.updateGate(editId.value, form)
        ElMessage.success('更新成功')
      } else {
        await gatesApi.createGate(form as GateCreate)
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

async function showChecks(gate: Gate) {
  checksLoading.value = true
  checksDialogVisible.value = true
  try {
    const { data } = await gatesApi.getGateChecks(gate.id)
    gateChecks.value = data
  } catch (error) {
    console.error('Failed to load checks:', error)
  } finally {
    checksLoading.value = false
  }
}

async function handleDelete(gateId: string) {
  try {
    await gatesApi.deleteGate(gateId)
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
.condition-item {
  margin-bottom: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}
.check-condition {
  margin-bottom: 5px;
}
</style>
