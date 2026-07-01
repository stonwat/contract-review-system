<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElCard, ElRow, ElCol, ElSkeleton } from 'element-plus'
import { fetchOverview, fetchCityStats } from '@/api/dashboard'
import type { DashboardOverview, CityStat } from '@/types/dashboard'

const overview = ref<DashboardOverview | null>(null)
const cityStats = ref<CityStat[]>([])
const loading = ref(true)

const cards = ref<Array<{ label: string; value: number; key: keyof DashboardOverview }>>([])

onMounted(async () => {
  try {
    overview.value = await fetchOverview()
    cards.value = [
      { label: '项目总数', value: overview.value.project_count, key: 'project_count' },
      { label: '合同总数', value: overview.value.contract_count, key: 'contract_count' },
      { label: '待确认', value: overview.value.pending_verify_count, key: 'pending_verify_count' },
      { label: '高风险', value: overview.value.high_risk_count, key: 'high_risk_count' },
      { label: '已完成', value: overview.value.completed_count, key: 'completed_count' },
    ]
    cityStats.value = await fetchCityStats()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="dashboard">
    <ElSkeleton :loading="loading" animated :rows="5">
      <ElRow :gutter="16">
        <ElCol v-for="c in cards" :key="c.key" :span="4">
          <ElCard shadow="hover">
            <div class="metric">
              <div class="value">{{ c.value }}</div>
              <div class="label">{{ c.label }}</div>
            </div>
          </ElCard>
        </ElCol>
      </ElRow>

      <ElCard class="mt-16" shadow="never">
        <template #header>各地市统计</template>
        <el-table :data="cityStats" border>
          <el-table-column prop="city" label="地市" />
          <el-table-column prop="project_count" label="项目数" />
          <el-table-column prop="high_risk" label="高风险" />
          <el-table-column prop="pending_verify" label="待确认" />
          <el-table-column prop="completed" label="已完成" />
        </el-table>
      </ElCard>
    </ElSkeleton>
  </div>
</template>

<style scoped>
.metric {
  text-align: center;
}
.value {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
}
.label {
  margin-top: 8px;
  color: #909399;
}
.mt-16 {
  margin-top: 16px;
}
</style>
