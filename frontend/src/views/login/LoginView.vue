<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElForm, ElFormItem, ElInput, ElButton, ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
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

/* ── 科技粒子背景（Canvas） ── */
const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId = 0

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  let w = (canvas.width = window.innerWidth)
  let h = (canvas.height = window.innerHeight)
  const particles: Particle[] = []
  const count = 60

  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.6,
      vy: (Math.random() - 0.5) * 0.6,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.1,
    })
  }

  function draw(): void {
    ctx!.clearRect(0, 0, w, h)
    // 连线
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x
        const dy = particles[i].y - particles[j].y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 180) {
          ctx!.beginPath()
          ctx!.moveTo(particles[i].x, particles[i].y)
          ctx!.lineTo(particles[j].x, particles[j].y)
          ctx!.strokeStyle = `rgba(255, 255, 255, ${0.08 * (1 - dist / 180)})`
          ctx!.lineWidth = 0.5
          ctx!.stroke()
        }
      }
    }
    // 粒子
    particles.forEach((p) => {
      p.x += p.vx
      p.y += p.vy
      if (p.x < 0) p.x = w
      if (p.x > w) p.x = 0
      if (p.y < 0) p.y = h
      if (p.y > h) p.y = 0
      ctx!.beginPath()
      ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
      ctx!.fillStyle = `rgba(255, 255, 255, ${p.opacity})`
      ctx!.fill()
    })
    animationId = requestAnimationFrame(draw)
  }

  function resize(): void {
    const cvs = canvas!
    w = cvs.width = window.innerWidth
    h = cvs.height = window.innerHeight
  }
  window.addEventListener('resize', resize)
  draw()

  onUnmounted(() => {
    cancelAnimationFrame(animationId)
    window.removeEventListener('resize', resize)
  })
})
</script>

<template>
  <div class="login-page">
    <!-- Canvas 粒子背景 -->
    <canvas ref="canvasRef" class="bg-canvas"></canvas>

    <!-- 红金渐变遮罩层 -->
    <div class="bg-overlay"></div>

    <!-- 网格装饰 -->
    <div class="bg-grid"></div>

    <!-- 左侧 branding -->
    <div class="brand-area">
      <div class="brand-content">
        <div class="brand-badge">AI 赋能 · 智慧审查</div>
        <h1 class="brand-title">合同审查系统</h1>
        <p class="brand-desc">
          基于人工智能技术的合同全生命周期审查管理平台，<br />
          为国央企提供高效、精准、合规的数字化审查服务
        </p>
        <div class="brand-features">
          <div class="feature-item">
            <span class="feature-icon">●</span>
            <span>AI 智能对比分析</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">●</span>
            <span>前后项合同自动关联</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">●</span>
            <span>风险预警与合规审查</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录卡片 -->
    <div class="login-card-area">
      <div class="login-card">
        <div class="card-header">
          <div class="card-logo">
            <span class="card-logo-icon">审</span>
          </div>
          <h2 class="card-title">用户登录</h2>
          <p class="card-subtitle">Contract Review System</p>
        </div>

        <ElForm
          :model="form"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <ElFormItem>
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <ElInput
                v-model="form.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
              />
            </div>
          </ElFormItem>
          <ElFormItem>
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <ElInput
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                show-password
              />
            </div>
          </ElFormItem>
          <ElFormItem>
            <ElButton
              class="login-btn btn-gradient"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </ElButton>
          </ElFormItem>
        </ElForm>

        <div class="card-footer">
          <span class="footer-text">推荐使用 Chrome / Edge 浏览器</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a0a0a 30%, #0f1923 70%, #0a0a14 100%);
}

/* ── Canvas 粒子背景 ── */
.bg-canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

/* ── 红金渐变遮罩 ── */
.bg-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(196, 29, 52, 0.25) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(212, 168, 67, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(196, 29, 52, 0.15) 0%, transparent 50%);
  pointer-events: none;
}

/* ── 科技网格 ── */
.bg-grid {
  position: absolute;
  inset: 0;
  z-index: 1;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at 50% 50%, black 30%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse at 50% 50%, black 30%, transparent 70%);
  pointer-events: none;
}

/* ── 左侧品牌区 ── */
.brand-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
  position: relative;
  padding: 40px;
}

.brand-content {
  max-width: 480px;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 14px;
  background: rgba(196, 29, 52, 0.2);
  border: 1px solid rgba(196, 29, 52, 0.3);
  border-radius: 20px;
  font-size: 12px;
  color: var(--color-gold-light);
  letter-spacing: 2px;
  margin-bottom: 24px;
}

.brand-title {
  font-size: 42px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 16px 0;
  letter-spacing: 4px;
  line-height: 1.2;
}

.brand-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.8;
  margin: 0 0 32px 0;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.feature-icon {
  color: var(--color-primary-light);
  font-size: 8px;
}

/* ── 右侧登录卡片 ── */
.login-card-area {
  width: 460px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
  position: relative;
  padding: 40px 60px 40px 0;
}

.login-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 40px 36px;
  box-shadow:
    0 8px 40px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.card-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.card-logo-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-gradient);
  border-radius: 14px;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 4px 16px rgba(196, 29, 52, 0.4);
}

.card-title {
  font-size: 22px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 6px 0;
}

.card-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
  letter-spacing: 1px;
}

/* ── 表单 ── */
.login-form {
  margin-bottom: 8px;
}

.input-wrapper {
  width: 100%;
  position: relative;
}
.input-wrapper :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  box-shadow: none;
  padding: 4px 16px 4px 38px;
  height: 46px;
  transition: all 0.3s ease;
}
.input-wrapper :deep(.el-input__wrapper:hover) {
  border-color: rgba(196, 29, 52, 0.4);
}
.input-wrapper :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary) !important;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 1px var(--color-primary) inset !important;
}
.input-wrapper :deep(.el-input__inner) {
  color: #ffffff;
  font-size: 14px;
  background: transparent;
}
.input-wrapper :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
}
.input-wrapper :deep(.el-input__prefix) {
  display: none;
}
.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.35);
  z-index: 2;
  font-size: 16px;
  pointer-events: none;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 46px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 4px;
  border-radius: 10px;
  margin-top: 4px;
}
.login-btn.btn-gradient {
  --el-button-bg-color: transparent;
  --el-button-border-color: transparent;
}

/* ── 底部 ── */
.card-footer {
  text-align: center;
  margin-top: 24px;
}
.footer-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.25);
}

/* ── 响应式 ── */
@media (max-width: 900px) {
  .brand-area {
    display: none;
  }
  .login-card-area {
    width: 100%;
    padding: 20px;
  }
  .login-card {
    max-width: 400px;
  }
}
</style>
