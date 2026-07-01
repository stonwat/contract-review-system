<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElTable, ElTableColumn, ElCard } from 'element-plus'
import { fetchAcceptanceList } from '@/api/acceptance'
import { formatDate } from '@/utils/format'
import StatusTag from '@/components/StatusTag.vue'
import type { AcceptanceReport } from '@/types/acceptance'

const list = ref<AcceptanceReport[]>([])
const loading = ref(false)

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const data = await fetchAcceptanceList()
    list.value = data.items
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <ElCard shadow="never">
    <template #header>验收报告管理</template>
    <ElTable :data="list" v-loading="loading" border>
      <ElTableColumn prop="acceptance_no" label="验收编号" />
      <ElTableColumn prop="contract_no" label="合同编号" />
      <ElTableColumn prop="acceptance_type" label="类型" width="80" />
      <ElTableColumn label="验收日期">
        <template #default="{ row }">{{ formatDate(row.acceptance_date) }}</template>
      </ElTableColumn>
      <ElTableColumn prop="acceptance_result" label="验收结果" />
      <ElTableColumn prop="comparison_result" label="比对结果" />
      <ElTableColumn label="状态">
        <template #default="{ row }">
          <StatusTag :status="row.verified ? '已确认' : '待确认'" />
        </template>
      </ElTableColumn>
    </ElTable>
  </ElCard>
</template>
