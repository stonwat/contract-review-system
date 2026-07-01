<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElForm, ElFormItem, ElInput, ElButton, ElCard, ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', password: '' })
const loading = ref(false)

async function handleLogin(): Promise<void> {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    router.push('/dashboard')
  } catch {
    // 错误已在拦截器中提示
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <ElCard class="login-card">
      <template #header>
        <h2>合同审查系统</h2>
      </template>
      <ElForm :model="form" label-width="80px" @keyup.enter="handleLogin">
        <ElFormItem label="用户名">
          <ElInput v-model="form.username" placeholder="请输入用户名" />
        </ElFormItem>
        <ElFormItem label="密码">
          <ElInput v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" :loading="loading" @click="handleLogin">登录</ElButton>
        </ElFormItem>
      </ElForm>
    </ElCard>
  </div>
</template>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.login-card {
  width: 400px;
}
</style>
