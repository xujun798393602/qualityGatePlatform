<template>
  <div class="scripts-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>脚本管理</span>
          <el-button type="primary" @click="showDialog()">
            <el-icon><Plus /></el-icon>
            新增脚本
          </el-button>
        </div>
      </template>

      <el-table :data="scripts" v-loading="loading" stripe>
        <el-table-column prop="name" label="脚本名称" width="180" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="language" label="语言" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
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
            <el-button type="success" link @click="handleExecute(row)">
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-popconfirm title="确定删除该脚本吗？" @confirm="handleDelete(row.id)">
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑脚本' : '新增脚本'" width="700px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="脚本名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入脚本名称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型">
            <el-option label="测试脚本" value="test" />
            <el-option label="构建脚本" value="build" />
            <el-option label="部署脚本" value="deploy" />
            <el-option label="检查脚本" value="check" />
          </el-select>
        </el-form-item>
        <el-form-item label="语言" prop="language">
          <el-select v-model="form.language" placeholder="请选择语言">
            <el-option label="Shell" value="shell" />
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
            <el-option label="Groovy" value="groovy" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入脚本描述" />
        </el-form-item>
        <el-form-item label="脚本内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="10" placeholder="请输入脚本内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Execute Dialog -->
    <el-dialog v-model="executeDialogVisible" title="执行结果" width="600px">
      <pre class="execute-output">{{ executeResult }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { scriptsApi, type Script, type ScriptCreate } from '@/api/scripts'

const scripts = ref<Script[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const executeDialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const editId = ref('')
const executeResult = ref('')
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  type: '',
  language: '',
  description: '',
  content: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入脚本名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  language: [{ required: true, message: '请选择语言', trigger: 'change' }],
  content: [{ required: true, message: '请输入脚本内容', trigger: 'blur' }],
}

function getTypeTag(type: string) {
  const map: Record<string, string> = {
    test: '',
    build: 'success',
    deploy: 'warning',
    check: 'info',
  }
  return map[type] || ''
}

async function loadScripts() {
  loading.value = true
  try {
    const { data } = await scriptsApi.getScripts()
    scripts.value = data
  } catch (error) {
    console.error('Failed to load scripts:', error)
  } finally {
    loading.value = false
  }
}

function showDialog(script?: Script) {
  if (script) {
    isEdit.value = true
    editId.value = script.id
    form.name = script.name
    form.type = script.type
    form.language = script.language
    form.description = script.description || ''
    form.content = script.content
  } else {
    isEdit.value = false
    editId.value = ''
    form.name = ''
    form.type = ''
    form.language = ''
    form.description = ''
    form.content = ''
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
        await scriptsApi.updateScript(editId.value, form)
        ElMessage.success('更新成功')
      } else {
        await scriptsApi.createScript(form as ScriptCreate)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadScripts()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

async function handleExecute(script: Script) {
  try {
    const { data } = await scriptsApi.executeScript(script.id)
    executeResult.value = JSON.stringify(data.result, null, 2)
    executeDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '执行失败')
  }
}

async function handleDelete(scriptId: string) {
  try {
    await scriptsApi.deleteScript(scriptId)
    ElMessage.success('删除成功')
    loadScripts()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadScripts()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.execute-output {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}
</style>
