<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElTable, ElTableColumn, ElButton, ElCard } from 'element-plus'
import { fetchComparisons, autoCompare } from '@/api/comparisons'
import { formatAmount, formatPercent } from '@/utils/format'
import type { Comparison } from '@/types/comparison'

const list = ref<Comparison[]>([])
const loading = ref(false)

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const data = await fetchComparisons()
    list.value = data.items
  } finally {
    loading.value = false
  }
}

async function handleAutoCompare(): Promise<void> {
  await autoCompare()
  loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="comparison-review">
    <ElCard shadow="never">
      <template #header>
        <div class="header">
          <span>比对审查</span>
          <ElButton type="primary" @click="handleAutoCompare">自动检测并比对</ElButton>
        </div>
      </template>
      <ElTable :data="list" v-loading="loading" border>
        <ElTableColumn prop="contract_no" label="合同编号" />
        <ElTableColumn label="前项金额">
          <template #default="{ row }">{{ formatAmount(row.front_amount) }}</template>
        </ElTableColumn>
        <ElTableColumn label="后项金额">
          <template #default="{ row }">{{ formatAmount(row.back_amount) }}</template>
        </ElTableColumn>
        <ElTableColumn label="金额差异">
          <template #default="{ row }">{{ formatAmount(row.amount_diff) }}</template>
        </ElTableColumn>
        <ElTableColumn label="毛利率">
          <template #default="{ row }">{{ formatPercent(row.margin_rate) }}</template>
        </ElTableColumn>
        <ElTableColumn prop="amount_match" label="金额一致" />
        <ElTableColumn prop="payment_match" label="付款一致" />
        <ElTableColumn prop="delivery_match" label="交付一致" />
        <ElTableColumn prop="acceptance_match" label="验收一致" />
      </ElTable>
    </ElCard>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
