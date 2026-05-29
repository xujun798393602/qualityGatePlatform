<template>
  <div class="repos-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>仓库管理</span>
          <el-button type="primary" @click="showDialog()">
            <el-icon><Plus /></el-icon>
            新增仓库
          </el-button>
        </div>
      </template>

      <el-table :data="repos" v-loading="loading" stripe>
        <el-table-column prop="name" label="仓库名称" width="180" />
        <el-table-column prop="url" label="仓库地址" min-width="250" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="branch" label="分支" width="120" />
        <el-table-column label="令牌状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.access_token ? 'success' : 'danger'">
              {{ row.access_token ? '已配置' : '未配置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="350" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="success" link @click="handleSync(row)">
              <el-icon><Refresh /></el-icon>
              同步
            </el-button>
            <el-button type="info" link @click="handleTest(row)">
              <el-icon><Connection /></el-icon>
              测试连接
            </el-button>
            <el-popconfirm title="确定删除该仓库吗？" @confirm="handleDelete(row.id)">
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑仓库' : '新增仓库'" width="700px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="仓库地址" prop="url">
          <el-input v-model="form.url" placeholder="请输入 Git 仓库地址，如 https://gitlab.com" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型">
            <el-option label="GitLab" value="gitlab" />
            <el-option label="GitHub" value="github" />
            <el-option label="Gitee" value="gitee" />
          </el-select>
        </el-form-item>
        <el-form-item label="默认分支" prop="branch">
          <el-input v-model="form.branch" placeholder="请输入默认分支" />
        </el-form-item>
        <el-form-item label="GitLab 项目 ID" prop="gitlab_project_id">
          <el-input v-model="form.gitlab_project_id" placeholder="请输入 GitLab 项目 ID（数字）" />
        </el-form-item>
        <el-form-item label="访问令牌" prop="access_token">
          <el-input v-model="form.access_token" type="password" show-password placeholder="请输入 GitLab Personal Access Token" />
          <div class="form-tip">
            <el-link type="primary" href="https://gitlab.com/-/profile/personal_access_tokens" target="_blank">
              点击这里创建 GitLab Personal Access Token
            </el-link>
            <br>
            <span>需要勾选: read_api, read_repository, read_repository</span>
          </div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入仓库描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="success" @click="handleTestConnection" :loading="testing">
          测试连接
        </el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- GitLab Projects Dialog -->
    <el-dialog v-model="projectsDialogVisible" title="选择 GitLab 项目" width="600px">
      <el-input v-model="projectSearch" placeholder="搜索项目" @input="searchProjects" clearable />
      <el-table :data="gitlabProjects" v-loading="searchingProjects" stripe style="margin-top: 15px;">
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="path" label="路径" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="selectProject(row)">选择</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { reposApi, type Repo, type RepoCreate } from '@/api/repos'

const repos = ref<Repo[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const projectsDialogVisible = ref(false)
const submitting = ref(false)
const testing = ref(false)
const searchingProjects = ref(false)
const isEdit = ref(false)
const editId = ref('')
const formRef = ref<FormInstance>()
const projectSearch = ref('')
const gitlabProjects = ref<any[]>([])

const form = reactive({
  name: '',
  url: '',
  type: 'gitlab',
  branch: 'main',
  description: '',
  gitlab_project_id: '',
  access_token: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }],
  url: [{ required: true, message: '请输入仓库地址', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

async function loadRepos() {
  loading.value = true
  try {
    const { data } = await reposApi.getRepos()
    repos.value = data
  } catch (error) {
    console.error('Failed to load repos:', error)
  } finally {
    loading.value = false
  }
}

function showDialog(repo?: Repo) {
  if (repo) {
    isEdit.value = true
    editId.value = repo.id
    form.name = repo.name
    form.url = repo.url
    form.type = repo.type
    form.branch = repo.branch
    form.description = repo.description || ''
    form.gitlab_project_id = String(repo.gitlab_project_id || '')
    form.access_token = '' // 不回显令牌
  } else {
    isEdit.value = false
    editId.value = ''
    form.name = ''
    form.url = ''
    form.type = 'gitlab'
    form.branch = 'main'
    form.description = ''
    form.gitlab_project_id = ''
    form.access_token = ''
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const submitData: any = {
        ...form,
        gitlab_project_id: form.gitlab_project_id ? parseInt(form.gitlab_project_id) : null,
      }
      if (isEdit.value) {
        if (!submitData.access_token) delete submitData.access_token
        await reposApi.updateRepo(editId.value, submitData)
        ElMessage.success('更新成功')
      } else {
        await reposApi.createRepo(submitData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadRepos()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

async function handleTestConnection() {
  testing.value = true
  try {
    const submitData: any = {
      ...form,
      gitlab_project_id: form.gitlab_project_id ? parseInt(form.gitlab_project_id) : null,
    }
    if (isEdit.value) {
      await reposApi.updateRepo(editId.value, submitData)
    } else {
      await reposApi.createRepo(submitData)
    }
    ElMessage.success('连接测试成功！')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '连接测试失败')
  } finally {
    testing.value = false
  }
}

async function handleTest(repo: Repo) {
  try {
    await reposApi.syncRepo(repo.id)
    ElMessage.success('连接正常')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '连接失败')
  }
}

async function handleSync(repo: Repo) {
  try {
    const { data } = await reposApi.syncRepo(repo.id)
    ElMessage.success(data.message || '同步成功')
    loadRepos()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '同步失败')
  }
}

async function handleDelete(repoId: string) {
  try {
    await reposApi.deleteRepo(repoId)
    ElMessage.success('删除成功')
    loadRepos()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

async function searchProjects() {
  if (!editId.value) return
  searchingProjects.value = true
  try {
    const { data } = await reposApi.getGitlabProjects(editId.value, projectSearch.value)
    gitlabProjects.value = data
  } catch (error) {
    console.error('Failed to search projects:', error)
  } finally {
    searchingProjects.value = false
  }
}

function selectProject(project: any) {
  form.gitlab_project_id = String(project.id)
  form.name = project.name
  projectsDialogVisible.value = false
}

onMounted(() => {
  loadRepos()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.form-tip {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style>
