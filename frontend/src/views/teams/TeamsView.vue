<template>
  <div class="teams-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>团队管理</span>
          <el-button type="primary" @click="showDialog()">
            <el-icon><Plus /></el-icon>
            新增团队
          </el-button>
        </div>
      </template>

      <el-table :data="teams" v-loading="loading" stripe>
        <el-table-column prop="name" label="团队名称" width="200" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-popconfirm
              title="确定删除该团队吗？"
              @confirm="handleDelete(row.id)"
            >
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
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑团队' : '新增团队'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入团队描述" />
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
import { teamsApi } from '@/api/teams'
import type { Team } from '@/types'

const teams = ref<Team[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const editId = ref('')
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  description: '',
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入团队名称', trigger: 'blur' },
  ],
}

// Load teams
async function loadTeams() {
  loading.value = true
  try {
    const { data } = await teamsApi.getTeams()
    teams.value = data
  } catch (error) {
    console.error('Failed to load teams:', error)
  } finally {
    loading.value = false
  }
}

// Show dialog
function showDialog(team?: Team) {
  if (team) {
    isEdit.value = true
    editId.value = team.id
    form.name = team.name
    form.description = team.description || ''
  } else {
    isEdit.value = false
    editId.value = ''
    form.name = ''
    form.description = ''
  }
  dialogVisible.value = true
}

// Submit form
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value) {
        await teamsApi.updateTeam(editId.value, { name: form.name, description: form.description })
        ElMessage.success('更新成功')
      } else {
        await teamsApi.createTeam({ name: form.name, description: form.description })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadTeams()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// Delete team
async function handleDelete(teamId: string) {
  try {
    await teamsApi.deleteTeam(teamId)
    ElMessage.success('删除成功')
    loadTeams()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadTeams()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
