<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElButton, ElTag } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import {
  fetchAdmins, createAdmin, updateAdmin, resetPassword, deleteAdmin, fetchCities,
  type AdminItem, type AdminCreateRequest, type AdminUpdateRequest,
} from '@/api/admins'

const authStore = useAuthStore()

// 列表
const admins = ref<AdminItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await fetchAdmins(page.value, pageSize.value)
    admins.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

// 角色标签
function roleType(role: string): 'danger' | 'warning' | 'info' {
  if (role === 'super_admin') return 'danger'
  if (role === 'city_admin') return 'warning'
  return 'info'
}

function roleText(role: string, city?: string | null): string {
  if (role === 'super_admin') return '超级管理员'
  if (role === 'city_admin') return `地市管理员（${city || ''}）`
  return '只读用户'
}

// 新建/编辑
const dialogVisible = ref(false)
const dialogTitle = ref('新建账号')
const editingId = ref<string | null>(null)
const form = ref<AdminCreateRequest>({
  username: '',
  password: '',
  display_name: '',
  role: 'viewer',
  city: null,
})
const cities = ref<string[]>([])
const saving = ref(false)

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度 3~50 字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母数字和下划线', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6~100 字符', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  city: [
    {
      validator: (_: unknown, value: string | null, callback: (e?: Error) => void) => {
        if (form.value.role === 'city_admin' && !value) {
          callback(new Error('地市管理员必须选择地市'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

async function openCreate() {
  dialogTitle.value = '新建账号'
  editingId.value = null
  form.value = { username: '', password: '', display_name: '', role: 'viewer', city: null }
  cities.value = await fetchCities()
  dialogVisible.value = true
}

async function openEdit(row: AdminItem) {
  dialogTitle.value = '编辑账号'
  editingId.value = row.id
  form.value = {
    username: row.username,
    password: '',
    display_name: row.display_name || '',
    role: row.role,
    city: row.city,
  }
  cities.value = await fetchCities()
  dialogVisible.value = true
}

const formRef = ref()

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = { ...form.value }
    if (editingId.value) {
      delete (payload as Record<string, unknown>).password
      await updateAdmin(editingId.value, payload as AdminUpdateRequest)
      ElMessage.success('更新成功')
    } else {
      await createAdmin(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await load()
  } finally {
    saving.value = false
  }
}

// 重置密码
const pwdDialogVisible = ref(false)
const pwdTargetId = ref<string>('')
const newPassword = ref('')
const pwdSaving = ref(false)

function openResetPwd(row: AdminItem) {
  pwdTargetId.value = row.id
  newPassword.value = ''
  pwdDialogVisible.value = true
}

async function handleResetPwd() {
  if (!newPassword.value || newPassword.value.length < 6) {
    ElMessage.warning('密码至少6位')
    return
  }
  pwdSaving.value = true
  try {
    await resetPassword(pwdTargetId.value, newPassword.value)
    ElMessage.success('密码重置成功')
    pwdDialogVisible.value = false
  } finally {
    pwdSaving.value = false
  }
}

// 删除
async function handleDelete(row: AdminItem) {
  if (row.id === authStore.adminInfo?.id) {
    ElMessage.warning('不能删除自己的账号')
    return
  }
  try {
    await ElMessageBox.confirm(`确定删除账号「${row.username}」？`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteAdmin(row.id)
    ElMessage.success('删除成功')
    await load()
  } catch {
    // cancelled
  }
}

onMounted(load)
</script>

<template>
  <div class="admin-manage page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">账号管理</h1>
      <ElButton type="primary" @click="openCreate">新建账号</ElButton>
    </div>    <!-- 表格 -->
    <ElCard shadow="never" class="table-card">
      <ElTable :data="admins" v-loading="loading" stripe>
        <ElTableColumn prop="username" label="用户名" min-width="120" />
        <ElTableColumn prop="display_name" label="显示名" min-width="120" />
        <ElTableColumn label="角色" min-width="180">
          <template #default="{ row }">
            <ElTag :type="roleType(row.role)" size="small" effect="plain">
              {{ roleText(row.role, row.city) }}
            </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="city" label="管辖地市" min-width="100" />
        <ElTableColumn label="状态" width="80" align="center">
          <template #default="{ row }">
            <ElTag :type="row.is_active ? 'success' : 'info'" size="small" effect="dark">
              {{ row.is_active ? '启用' : '禁用' }}
            </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="created_at" label="创建时间" min-width="160" />
        <ElTableColumn label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <ElButton link size="small" type="primary" @click="openEdit(row)">编辑</ElButton>
            <ElButton link size="small" type="primary" @click="openResetPwd(row)">重置密码</ElButton>
            <ElButton
              v-if="row.id !== authStore.adminInfo?.id"
              link
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >删除</ElButton>
          </template>
        </ElTableColumn>
      </ElTable>

      <div class="pagination-wrap">
        <ElPagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          background
          @current-change="load"
        />
      </div>
    </ElCard>

    <!-- 新建/编辑对话框 -->
    <ElDialog v-model="dialogVisible" :title="dialogTitle" width="480px" top="8vh">
      <ElForm ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <ElFormItem label="用户名" prop="username">
          <ElInput v-model="form.username" :disabled="!!editingId" placeholder="3~50位字母数字下划线" />
        </ElFormItem>
        <ElFormItem v-if="!editingId" label="密码" prop="password">
          <ElInput v-model="form.password" type="password" show-password placeholder="至少6位" />
        </ElFormItem>
        <ElFormItem label="显示名">
          <ElInput v-model="form.display_name" placeholder="选填" />
        </ElFormItem>
        <ElFormItem label="角色" prop="role">
          <ElSelect v-model="form.role" style="width: 100%">
            <ElOption label="超级管理员" value="super_admin" />
            <ElOption label="地市管理员" value="city_admin" />
            <ElOption label="只读用户" value="viewer" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem v-if="form.role === 'city_admin'" label="地市" prop="city">
          <ElSelect v-model="form.city" style="width: 100%" placeholder="请选择地市">
            <ElOption v-for="c in cities" :key="c" :label="c" :value="c" />
          </ElSelect>
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="dialogVisible = false">取消</ElButton>
        <ElButton type="primary" :loading="saving" @click="handleSave">保存</ElButton>
      </template>
    </ElDialog>

    <!-- 重置密码对话框 -->
    <ElDialog v-model="pwdDialogVisible" title="重置密码" width="400px" top="30vh">
      <ElForm label-width="100px">
        <ElFormItem label="新密码">
          <ElInput v-model="newPassword" type="password" show-password placeholder="至少6位" />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="pwdDialogVisible = false">取消</ElButton>
        <ElButton type="primary" :loading="pwdSaving" @click="handleResetPwd">确认重置</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.admin-manage {
  max-width: 1400px;
}

.table-card {
  border-radius: var(--radius-md) !important;
}
.table-card :deep(.el-card__body) {
  padding: 0;
}

.pagination-wrap {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--color-border-lighter);
}
</style>
