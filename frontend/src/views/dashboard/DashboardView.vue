<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { ElCard, ElTag, ElEmpty } from 'element-plus'
import EChart from '@/components/EChart.vue'
import SvgIcon from '@/components/SvgIcon.vue'
import { fetchOverview, fetchCityStats } from '@/api/dashboard'
import type { DashboardOverview, CityStat } from '@/types/dashboard'

const overview = ref<DashboardOverview | null>(null)
const cityStats = ref<CityStat[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    overview.value = await fetchOverview()
    cityStats.value = await fetchCityStats()
  } finally {
    loading.value = false
  }
})

// ── Hero 卡：高风险（唯一满色卡片，眼睛第一时间落到这里） ──
const hero = computed(() => ({
  value: overview.value?.high_risk_count ?? 0,
  label: '高风险项目',
  desc: '需优先关注',
}))

// ── 次级 KPI 卡：白底 + 左侧色条 + 线性图标，克制 ──
interface SecondaryCard {
  key: string
  label: string
  value: number
  unit?: string
  icon: 'project' | 'contract' | 'pending' | 'ai' | 'done'
  color: 'primary' | 'gold' | 'warning' | 'info' | 'success'
}

const secondaryCards = computed<SecondaryCard[]>(() => {
  const o = overview.value
  return [
    { key: 'project', label: '项目总数', value: o?.project_count ?? 0, unit: '个', icon: 'project', color: 'primary' },
    { key: 'contract', label: '合同总数', value: o?.contract_count ?? 0, unit: '份', icon: 'contract', color: 'gold' },
    { key: 'pending', label: '待确认', value: o?.pending_verify_count ?? 0, unit: '项', icon: 'pending', color: 'warning' },
    { key: 'analyzed', label: '已分析', value: o?.llm_analyzed_count ?? 0, unit: '项', icon: 'ai', color: 'info' },
    { key: 'done', label: '已完成审查', value: o?.completed_count ?? 0, unit: '项', icon: 'done', color: 'success' },
  ]
})

// ── 各地市项目/高风险对比（分组柱状图） ──
const cityBarOption = computed(() => {
  const cities = cityStats.value.map((c) => c.city)
  const projects = cityStats.value.map((c) => c.project_count)
  const risks = cityStats.value.map((c) => c.high_risk)
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(21, 25, 31, 0.92)',
      borderColor: 'transparent',
      textStyle: { color: '#fff', fontSize: 12 },
    },
    legend: {
      data: ['项目数', '高风险'],
      right: 0, top: 0,
      itemWidth: 10, itemHeight: 10,
      textStyle: { color: '#4a5160', fontSize: 12 },
    },
    grid: { left: 36, right: 16, top: 40, bottom: 28 },
    xAxis: {
      type: 'category',
      data: cities,
      axisLine: { lineStyle: { color: '#dfe4ec' } },
      axisLabel: { color: '#4a5160', fontSize: 12 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f0f3f7', type: 'dashed' } },
      axisLabel: { color: '#8893a7', fontSize: 12 },
    },
    series: [
      {
        name: '项目数',
        type: 'bar',
        barWidth: 16,
        itemStyle: {
          borderRadius: [3, 3, 0, 0],
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
            { offset: 0, color: '#c9a04a' }, { offset: 1, color: '#e6c87a' },
          ] },
        },
        data: projects,
      },
      {
        name: '高风险',
        type: 'bar',
        barWidth: 16,
        itemStyle: {
          borderRadius: [3, 3, 0, 0],
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
            { offset: 0, color: '#b41d34' }, { offset: 1, color: '#d63147' },
          ] },
        },
        data: risks,
      },
    ],
  }
})

// ── 项目状态分布（环形图） ──
const statusPieOption = computed(() => {
  const o = overview.value
  const analyzed = o?.llm_analyzed_count ?? 0
  const pending = o?.pending_verify_count ?? 0
  const completed = o?.completed_count ?? 0
  const total = o?.project_count ?? 0
  const todo = Math.max(0, total - analyzed - pending - completed)
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(21, 25, 31, 0.92)',
      borderColor: 'transparent',
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      bottom: 0, left: 'center',
      itemWidth: 10, itemHeight: 10,
      textStyle: { color: '#4a5160', fontSize: 12 },
    },
    series: [{
      type: 'pie',
      radius: ['52%', '72%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 600, color: '#1a1d24' },
      },
      data: [
        { value: completed, name: '已完成', itemStyle: { color: '#2e8b57' } },
        { value: analyzed, name: '已分析', itemStyle: { color: '#4a7bb5' } },
        { value: pending, name: '待确认', itemStyle: { color: '#d4811c' } },
        { value: todo, name: '待处理', itemStyle: { color: '#b8c0cf' } },
      ],
    }],
  }
})
</script>

<template>
  <div class="dashboard page-container" v-loading="loading">
    <template v-if="overview">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">仪表盘</h1>
        <span class="page-header-meta nums">数据截至实时</span>
      </div>

      <!-- KPI 区：左 hero + 右 5 次级 -->
      <div class="kpi-row fade-in-up">
        <!-- Hero 卡：高风险（唯一满色） -->
        <div class="hero-card">
          <div class="hero-glow"></div>
          <div class="hero-body">
            <div class="hero-top">
              <SvgIcon name="risk" :size="22" color="inherit" />
              <span class="hero-label">高风险</span>
            </div>
            <div class="hero-value nums">{{ hero.value }}</div>
            <div class="hero-desc">{{ hero.desc }}</div>
            <div class="hero-bar"></div>
          </div>
        </div>

        <!-- 5 张次级卡 -->
        <div class="secondary-grid">
          <div
            v-for="(c, i) in secondaryCards"
            :key="c.key"
            class="secondary-card"
            :class="`color-${c.color}`"
          >
            <div class="sec-side"></div>
            <div class="sec-icon">
              <SvgIcon :name="c.icon" :size="20" :color="c.color" />
            </div>
            <div class="sec-text">
              <div class="sec-value nums">{{ c.value }}<span class="sec-unit">{{ c.unit }}</span></div>
              <div class="sec-label">{{ c.label }}</div>
            </div>
            <div class="sec-index nums">{{ String(i + 1).padStart(2, '0') }}</div>
          </div>
        </div>
      </div>

      <!-- 图表区：左柱状对比 + 右环形分布 -->
      <div class="chart-row">
        <ElCard shadow="never" class="chart-card fade-in-up delay-2">
          <template #header>
            <div class="chart-header">
              <span class="section-title">各地市项目与高风险对比</span>
              <ElTag size="small" type="danger" effect="plain">{{ cityStats.length }} 地市</ElTag>
            </div>
          </template>
          <EChart v-if="cityStats.length" :option="cityBarOption" height="300px" />
          <ElEmpty v-else description="暂无地市数据" :image-size="80" />
        </ElCard>

        <ElCard shadow="never" class="chart-card fade-in-up delay-3">
          <template #header>
            <div class="chart-header">
              <span class="section-title">项目状态分布</span>
            </div>
          </template>
          <EChart :option="statusPieOption" height="300px" />
        </ElCard>
      </div>

      <!-- 地市明细表 -->
      <ElCard shadow="never" class="city-table-card fade-in-up delay-4">
        <template #header>
          <div class="chart-header">
            <span class="section-title">各地市明细</span>
          </div>
        </template>
        <el-table :data="cityStats" stripe style="width: 100%">
          <el-table-column prop="city" label="地市" min-width="120">
            <template #default="{ row }"><span class="city-name">{{ row.city }}</span></template>
          </el-table-column>
          <el-table-column prop="project_count" label="项目数" min-width="100" align="right" class-name="nums" />
          <el-table-column prop="pending_verify" label="待确认" min-width="100" align="right">
            <template #default="{ row }">
              <span v-if="row.pending_verify > 0" class="num-warn nums">{{ row.pending_verify }}</span>
              <span v-else class="num-faint nums">0</span>
            </template>
          </el-table-column>
          <el-table-column prop="completed" label="已完成" min-width="100" align="right">
            <template #default="{ row }">
              <span v-if="row.completed > 0" class="num-ok nums">{{ row.completed }}</span>
              <span v-else class="num-faint nums">0</span>
            </template>
          </el-table-column>
          <el-table-column label="高风险" min-width="100" align="right">
            <template #default="{ row }">
              <ElTag v-if="row.high_risk > 0" type="danger" size="small" effect="dark">{{ row.high_risk }}</ElTag>
              <span v-else class="num-faint nums">0</span>
            </template>
          </el-table-column>
        </el-table>
      </ElCard>
    </template>
  </div>
</template>

<style scoped>
.dashboard { max-width: 100%; }

/* ── KPI 区布局 ── */
.kpi-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: stretch;
}

/* ── Hero 卡：唯一满色红渐变 ── */
.hero-card {
  position: relative;
  width: 240px;
  flex-shrink: 0;
  border-radius: var(--radius-lg);
  background: var(--color-primary-gradient);
  box-shadow: var(--shadow-glow-red);
  overflow: hidden;
  padding: 20px;
  color: #fff;
}
.hero-glow {
  position: absolute;
  top: -40px; right: -40px;
  width: 140px; height: 140px;
  background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 70%);
  pointer-events: none;
}
.hero-body { position: relative; z-index: 1; height: 100%; display: flex; flex-direction: column; }
.hero-top { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.hero-label { font-size: 13px; opacity: 0.9; letter-spacing: 1px; }
.hero-value {
  font-size: 48px; font-weight: 700; line-height: 1;
  font-variant-numeric: tabular-nums;
}
.hero-desc { font-size: 12px; opacity: 0.75; margin-top: 8px; }
.hero-bar {
  margin-top: auto;
  height: 3px; width: 40px;
  background: rgba(255,255,255,0.5);
  border-radius: 2px;
}

/* ── 次级卡网格 ── */
.secondary-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.secondary-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 14px 16px 18px;
  background: var(--color-paper);
  border: 1px solid var(--color-border-soft);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: box-shadow 0.25s ease, transform 0.25s ease;
}
.secondary-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

/* 左侧色条 */
.sec-side {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
}
.color-primary .sec-side { background: var(--color-primary); }
.color-gold .sec-side { background: var(--color-gold); }
.color-warning .sec-side { background: var(--color-warning); }
.color-info .sec-side { background: var(--color-info); }
.color-success .sec-side { background: var(--color-success); }

/* 图标 */
.sec-icon {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
}
.color-primary .sec-icon { background: var(--color-primary-soft); }
.color-gold .sec-icon { background: var(--color-gold-soft); }
.color-warning .sec-icon { background: var(--color-warning-soft); }
.color-info .sec-icon { background: var(--color-info-soft); }
.color-success .sec-icon { background: var(--color-success-soft); }

/* 文字 */
.sec-text { flex: 1; min-width: 0; }
.sec-value {
  font-size: 22px; font-weight: 600; color: var(--color-ink);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}
.sec-unit { font-size: 12px; font-weight: 400; color: var(--color-ink-3); margin-left: 3px; }
.sec-label { font-size: 12px; color: var(--color-ink-3); margin-top: 2px; }

/* 序号水印 */
.sec-index {
  position: absolute;
  right: 10px; bottom: 6px;
  font-size: 22px; font-weight: 700;
  color: var(--color-border-light);
  line-height: 1;
}

/* ── 图表行 ── */
.chart-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}
.chart-card { border-radius: var(--radius-md) !important; }
.chart-card :deep(.el-card__body) { padding: 16px 20px 20px; }
.chart-header {
  display: flex; align-items: center; justify-content: space-between;
}

/* ── 地市表 ── */
.city-table-card { border-radius: var(--radius-md) !important; }
.city-table-card :deep(.el-card__body) { padding: 0; }
.city-name { font-weight: 500; color: var(--color-ink); }
.num-warn { color: var(--color-warning); font-weight: 600; }
.num-ok { color: var(--color-success); font-weight: 600; }
.num-faint { color: var(--color-ink-4); }

/* ── 响应式 ── */
@media (max-width: 1280px) {
  .secondary-grid { grid-template-columns: repeat(3, 1fr); }
  .secondary-card:nth-child(n+4) { grid-column: span 1; }
}
@media (max-width: 960px) {
  .kpi-row { flex-direction: column; }
  .hero-card { width: 100%; }
  .secondary-grid { grid-template-columns: repeat(2, 1fr); }
  .chart-row { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .secondary-grid { grid-template-columns: 1fr; }
  .city-table-card { overflow-x: auto; }
  .city-table-card .el-table { min-width: 600px; }
  .hero-value { font-size: 36px; }
}
@media (min-width: 1920px) {
  .kpi-row { gap: 24px; }
  .secondary-grid { gap: 16px; }
  .chart-row { gap: 24px; }
  .hero-card { padding: 28px; }
  .hero-value { font-size: 56px; }
  .secondary-card { padding: 20px 16px 20px 22px; }
  .sec-value { font-size: 26px; }
}
</style>
