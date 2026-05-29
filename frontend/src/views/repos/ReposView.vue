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
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_sync_at" label="最后同步" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="success" link @click="handleSync(row)">
              <el-icon><Refresh /></el-icon>
              同步
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑仓库' : '新增仓库'" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="仓库地址" prop="url">
          <el-input v-model="form.url" placeholder="请输入 Git 仓库地址" />
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
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入仓库描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
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
const submitting = ref(false)
const isEdit = ref(false)
const editId = ref('')
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  url: '',
  type: 'gitlab',
  branch: 'main',
  description: '',
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
  } else {
    isEdit.value = false
    editId.value = ''
    form.name = ''
    form.url = ''
    form.type = 'gitlab'
    form.branch = 'main'
    form.description = ''
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
        await reposApi.updateRepo(editId.value, form)
        ElMessage.success('更新成功')
      } else {
        await reposApi.createRepo(form as RepoCreate)
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

async function handleSync(repo: Repo) {
  try {
    await reposApi.syncRepo(repo.id)
    ElMessage.success('同步成功')
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
</style>
