<script setup lang="ts">
import { ref } from 'vue'
import { ElTabs, ElTabPane, ElCard, ElTable, ElTableColumn, ElButton, ElMessage } from 'element-plus'
import { fetchReport, exportReport } from '@/api/reports'
import { exportToExcel } from '@/utils/export'

const activeTab = ref('contract-consistency')
const data = ref<Record<string, unknown>[]>([])

const tabs = [
  { name: 'contract-consistency', label: '合同内容一致性' },
  { name: 'acceptance-consistency', label: '验收报告一致性' },
  { name: 'low-margin', label: '低毛利项目' },
  { name: 'high-risk', label: '高风险项目' },
]

async function loadTab(name: string): Promise<void> {
  const result = (await fetchReport(name)) as { details?: Record<string, unknown>[] }
  data.value = result?.details ?? []
}

async function handleExport(): Promise<void> {
  if (data.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  exportToExcel(data.value, activeTab.value)
}

function handleTabChange(name: string): void {
  loadTab(name)
}

loadTab(activeTab.value)
</script>

<template>
  <ElCard shadow="never">
    <template #header>
      <div class="header">
        <span>报表中心</span>
        <ElButton type="primary" @click="handleExport">导出 Excel</ElButton>
      </div>
    </template>
    <ElTabs v-model="activeTab" @tab-change="handleTabChange">
      <ElTabPane v-for="t in tabs" :key="t.name" :label="t.label" :name="t.name" />
    </ElTabs>
    <ElTable :data="data" border>
      <ElTableColumn prop="contract_no" label="合同编号" />
      <ElTableColumn prop="city" label="地市" />
      <ElTableColumn prop="margin_rate" label="毛利率" />
      <ElTableColumn prop="front_amount" label="前项金额" />
      <ElTableColumn prop="back_amount" label="后项金额" />
    </ElTable>
  </ElCard>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
