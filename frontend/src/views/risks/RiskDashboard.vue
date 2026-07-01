<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElTable, ElTableColumn, ElTabs, ElTabPane, ElButton, ElCard, ElMessage } from 'element-plus'
import { fetchRisks, fetchRiskSummary, dismissRisk } from '@/api/risks'
import { useAuthStore } from '@/stores/auth'
import RiskTag from '@/components/RiskTag.vue'
import type { RiskRecord, RiskSummary } from '@/types/risk'

const authStore = useAuthStore()
const list = ref<RiskRecord[]>([])
const summary = ref<RiskSummary | null>(null)
const activeLevel = ref('全部')
const loading = ref(false)

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const level = activeLevel.value === '全部' ? undefined : activeLevel.value
    const data = await fetchRisks({ page: 1, page_size: 100, risk_level: level, dismissed: false })
    list.value = data.items
    summary.value = await fetchRiskSummary()
  } finally {
    loading.value = false
  }
}

async function handleDismiss(id: string): Promise<void> {
  await dismissRisk(id, authStore.adminInfo?.username || 'admin')
  ElMessage.success('已忽略')
  loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="risk-dashboard">
    <ElCard class="summary" shadow="never">
      <span>总风险：{{ summary?.total || 0 }}</span>
      <span v-for="(count, level) in summary?.by_level" :key="level" :class="['badge', `level-${level}`]">
        {{ level }}风险 {{ count }}
      </span>
    </ElCard>

    <ElTabs v-model="activeLevel" @tab-change="loadData">
      <ElTabPane label="全部风险" name="全部" />
      <ElTabPane label="高风险" name="高" />
      <ElTabPane label="中风险" name="中" />
      <ElTabPane label="低风险" name="低" />
    </ElTabs>

    <ElTable :data="list" v-loading="loading" border>
      <ElTableColumn prop="contract_no" label="合同编号" />
      <ElTableColumn prop="risk_type" label="风险类型" />
      <ElTableColumn label="等级" width="100">
        <template #default="{ row }"><RiskTag :level="row.risk_level" /></template>
      </ElTableColumn>
      <ElTableColumn prop="source_type" label="来源" width="120" />
      <ElTableColumn prop="detail" label="详情" show-overflow-tooltip />
      <ElTableColumn label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <ElButton link type="primary" @click="handleDismiss(row.id)">忽略</ElButton>
        </template>
      </ElTableColumn>
    </ElTable>
  </div>
</template>

<style scoped>
.summary {
  margin-bottom: 16px;
}
.summary :deep(span) {
  margin-right: 16px;
}
.badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
}
.level-高 {
  color: #f56c6c;
  background: #fef0f0;
}
.level-中 {
  color: #e6a23c;
  background: #fdf6ec;
}
.level-低 {
  color: #909399;
  background: #f4f4f5;
}
</style>
