<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElTabs, ElTabPane, ElCard, ElTable, ElTableColumn, ElButton, ElTag, ElEmpty, ElSelect, ElOption } from 'element-plus'
import SvgIcon from '@/components/SvgIcon.vue'
import { fetchReport } from '@/api/reports'
import { fetchCities } from '@/api/cities'
import { useAuthStore } from '@/stores/auth'
import { formatAmount, formatPercent } from '@/utils/format'

const authStore = useAuthStore()
const activeTab = ref('contract-consistency')
const rawData = ref<Record<string, unknown> | null>(null)
const data = ref<Record<string, unknown>[]>([])
const loading = ref(false)
const selectedCity = ref('')
const cities = ref<string[]>([])

const tabs = [
  { name: 'contract-consistency', label: '合同一致性' },
  { name: 'acceptance-consistency', label: '验收一致性' },
  { name: 'low-margin', label: '低毛利项目' },
  { name: 'high-risk', label: '高风险项目' },
]

// 汇总指标条：从返回数据中提取 summary
const summaryItems = computed<{ label: string; value: string | number; tone?: string }[]>(() => {
  const r = rawData.value
  if (!r) return []
  if (activeTab.value === 'low-margin') {
    const s = r.summary as { total?: number; low_margin?: number; inverted?: number } | undefined
    return [
      { label: '低毛利项目总数', value: s?.total ?? 0, tone: 'warning' },
      { label: '低毛利', value: s?.low_margin ?? 0, tone: 'warning' },
      { label: '利润倒挂', value: s?.inverted ?? 0, tone: 'danger' },
    ]
  }
  if (activeTab.value === 'high-risk') {
    return [{ label: '高风险项目数', value: r.total as number ?? 0, tone: 'danger' }]
  }
  // 一致性报表
  const s = (r.summary as { city?: string; total?: number; '完全一致'?: number; '有一致性风险'?: number; '完全不一致'?: number }[]) || []
  const total = s.reduce((a, b) => a + (b.total || 0), 0)
  const ok = s.reduce((a, b) => a + (b['完全一致'] || 0), 0)
  const risk = s.reduce((a, b) => a + (b['有一致性风险'] || 0), 0)
  const diff = s.reduce((a, b) => a + (b['完全不一致'] || 0), 0)
  return [
    { label: '项目数', value: total },
    { label: '完全一致', value: ok, tone: 'success' },
    { label: '一致性风险', value: risk, tone: 'warning' },
    { label: '完全不一致', value: diff, tone: 'danger' },
  ]
})

async function loadTab(name: string): Promise<void> {
  loading.value = true
  try {
    const params: Record<string, unknown> = {}
    if (selectedCity.value) {
      params.city = selectedCity.value
    }
    const result = (await fetchReport(name, params)) as { details?: Record<string, unknown>[]; items?: Record<string, unknown>[]; summary?: unknown; total?: number }
    rawData.value = result as Record<string, unknown>
    data.value = result?.details ?? result?.items ?? []
  } finally {
    loading.value = false
  }
}

async function handleExport(): Promise<void> {
  const params = new URLSearchParams({ report_type: activeTab.value })
  if (selectedCity.value) params.set('city', selectedCity.value)
  window.open(`${import.meta.env.VITE_API_BASE || '/api/v1'}/reports/export?${params}`, '_blank')
}

function handleTabChange(name: string | number): void {
  loadTab(String(name))
}

function handleCityChange(): void {
  loadTab(activeTab.value)
}

function getRateLevelTagType(level?: string): 'success' | 'warning' | 'danger' {
  if (level === '利润倒挂') return 'danger'
  if (level === '低毛利') return 'warning'
  return 'success'
}

onMounted(async () => {
  cities.value = await fetchCities()
  loadTab(activeTab.value)
})
</script>

<template>
  <div class="report-center page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">报表中心</h1>
      <ElButton type="primary" @click="handleExport">
        <SvgIcon name="export" :size="16" color="inherit" style="margin-right: 4px" />
        导出 Excel
      </ElButton>
    </div>

    <!-- 地市筛选 (仅超管可见) -->
    <div v-if="authStore.isSuperAdmin" class="city-filter-bar">
      <span class="filter-label">地市</span>
      <ElSelect v-model="selectedCity" placeholder="全部地市" clearable style="width: 180px" @change="handleCityChange">
        <ElOption v-for="c in cities" :key="c" :label="c" :value="c" />
      </ElSelect>
    </div>

    <!-- 报表卡片 -->
    <ElCard shadow="never" class="report-card">
      <ElTabs v-model="activeTab" @tab-change="handleTabChange" class="report-tabs">
        <ElTabPane v-for="t in tabs" :key="t.name" :label="t.label" :name="t.name" />
      </ElTabs>

      <!-- 汇总指标条 -->
      <div v-if="summaryItems.length" class="summary-bar">
        <div
          v-for="item in summaryItems"
          :key="item.label"
          class="summary-item"
          :class="item.tone ? `tone-${item.tone}` : ''"
        >
          <span class="sum-value nums">{{ item.value }}</span>
          <span class="sum-label">{{ item.label }}</span>
        </div>
      </div>

      <ElTable :data="data" border v-loading="loading" stripe class="report-table">
        <!-- 合同一致性报表 -->
        <template v-if="activeTab === 'contract-consistency'">
          <ElTableColumn prop="contract_no" label="合同编号" min-width="160" />
          <ElTableColumn prop="city" label="地市" min-width="100" />
          <ElTableColumn prop="project_name" label="项目名称" min-width="160" />
          <ElTableColumn label="前项金额" min-width="120" align="right">
            <template #default="{ row }">{{ formatAmount(row.front_amount as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="后项金额" min-width="120" align="right">
            <template #default="{ row }">{{ formatAmount(row.back_amount as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="毛利率" min-width="100" align="right">
            <template #default="{ row }">{{ formatPercent(row.rate as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="等级" min-width="100" align="center">
            <template #default="{ row }">
              <ElTag v-if="row.rate_level" :type="getRateLevelTagType(row.rate_level as string)" size="small" effect="dark">{{ row.rate_level }}</ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn label="一致性" min-width="120" align="center">
            <template #default="{ row }">
              <ElTag
                v-if="row.similarity"
                :type="row.similarity === '完全一致' ? 'success' : row.similarity === '有一致性风险' ? 'warning' : 'danger'"
                size="small"
                effect="dark"
              >{{ row.similarity }}</ElTag>
            </template>
          </ElTableColumn>
        </template>

        <!-- 验收一致性报表 -->
        <template v-else-if="activeTab === 'acceptance-consistency'">
          <ElTableColumn prop="contract_no" label="合同编号" min-width="160" />
          <ElTableColumn prop="city" label="地市" min-width="100" />
          <ElTableColumn prop="project_name" label="项目名称" min-width="160" />
          <ElTableColumn label="一致性" min-width="120" align="center">
            <template #default="{ row }">
              <ElTag
                v-if="row.similarity"
                :type="row.similarity === '完全一致' ? 'success' : row.similarity === '有一致性风险' ? 'warning' : 'danger'"
                size="small"
                effect="dark"
              >{{ row.similarity }}</ElTag>
            </template>
          </ElTableColumn>
        </template>

        <!-- 低毛利报表 -->
        <template v-else-if="activeTab === 'low-margin'">
          <ElTableColumn prop="contract_no" label="合同编号" min-width="160" />
          <ElTableColumn prop="city" label="地市" min-width="100" />
          <ElTableColumn prop="project_name" label="项目名称" min-width="160" />
          <ElTableColumn label="前项金额" min-width="120" align="right">
            <template #default="{ row }">{{ formatAmount(row.front_amount as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="后项金额" min-width="120" align="right">
            <template #default="{ row }">{{ formatAmount(row.back_amount as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="毛利率" min-width="100" align="right">
            <template #default="{ row }">{{ formatPercent(row.rate as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="等级" min-width="100" align="center">
            <template #default="{ row }">
              <ElTag v-if="row.rate_level" :type="getRateLevelTagType(row.rate_level as string)" size="small" effect="dark">{{ row.rate_level }}</ElTag>
            </template>
          </ElTableColumn>
        </template>

        <!-- 高风险报表 -->
        <template v-else>
          <ElTableColumn prop="contract_no" label="合同编号" min-width="160" />
          <ElTableColumn prop="city" label="地市" min-width="100" />
          <ElTableColumn prop="project_name" label="项目名称" min-width="160" />
          <ElTableColumn label="前项金额" min-width="120" align="right">
            <template #default="{ row }">{{ formatAmount(row.front_amount as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="后项金额" min-width="120" align="right">
            <template #default="{ row }">{{ formatAmount(row.back_amount as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="毛利率" min-width="100" align="right">
            <template #default="{ row }">{{ formatPercent(row.rate as number) }}</template>
          </ElTableColumn>
          <ElTableColumn label="等级" min-width="100" align="center">
            <template #default="{ row }">
              <ElTag v-if="row.rate_level" :type="getRateLevelTagType(row.rate_level as string)" size="small" effect="dark">{{ row.rate_level }}</ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn label="合同一致性" min-width="120" align="center">
            <template #default="{ row }">{{ row.contract_similarity || '—' }}</template>
          </ElTableColumn>
          <ElTableColumn label="验收一致性" min-width="120" align="center">
            <template #default="{ row }">{{ row.acceptance_similarity || '—' }}</template>
          </ElTableColumn>
          <ElTableColumn label="项目风险" min-width="100" align="center">
            <template #default="{ row }">
              <ElTag v-if="row.project_risk" type="danger" size="small" effect="dark">{{ row.project_risk }}</ElTag>
            </template>
          </ElTableColumn>
        </template>
      </ElTable>

      <ElEmpty v-if="!loading && data.length === 0" description="暂无报表数据" />
    </ElCard>
  </div>
</template>

<style scoped>
.report-center {
  max-width: 100%;
}

.city-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 0 2px;
}
.city-filter-bar .filter-label {
  font-size: 14px;
  color: var(--color-ink-2);
  white-space: nowrap;
}

.report-card {
  border-radius: var(--radius-md) !important;
}
.report-card :deep(.el-card__body) {
  padding: 0;
}

.report-tabs {
  padding: 0 20px;
  padding-top: 4px;
}
.report-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

/* 汇总指标条 */
.summary-bar {
  display: flex;
  gap: 24px;
  padding: 16px 20px;
  background: var(--color-paper-2);
  border-bottom: 1px solid var(--color-border-soft);
  flex-wrap: wrap;
}
.summary-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 80px;
}
.summary-item .sum-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-ink);
  line-height: 1.2;
}
.summary-item .sum-label {
  font-size: 12px;
  color: var(--color-ink-3);
}
.summary-item.tone-success .sum-value { color: var(--color-success); }
.summary-item.tone-warning .sum-value { color: var(--color-warning); }
.summary-item.tone-danger .sum-value { color: var(--color-danger); }

.report-table {
  border-top: none;
}

/* ── 响应式 ── */
@media (max-width: 1280px) {
  .report-center { max-width: 100%; }
}
@media (min-width: 1920px) {
  .report-center { max-width: 100%; }
  .summary-bar { gap: 40px; padding: 20px 28px; }
  .summary-item .sum-value { font-size: 26px; }
}
@media (max-width: 768px) {
  .summary-bar { gap: 16px; padding: 12px 16px; }
  .summary-item { min-width: 60px; }
  .summary-item .sum-value { font-size: 18px; }
  .report-tabs { padding: 0 12px; }
  .report-table { overflow-x: auto; }
  .report-table .el-table { min-width: 680px; }
}
</style>
