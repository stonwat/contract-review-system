<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElTable, ElTableColumn, ElButton, ElInput, ElSelect, ElOption, ElPagination } from 'element-plus'
import { useContractStore } from '@/stores/contracts'
import { formatAmount, formatDate } from '@/utils/format'
import StatusTag from '@/components/StatusTag.vue'

const router = useRouter()
const store = useContractStore()

const filters = reactive({
  contract_no: '',
  contract_type: '' as string,
  verified: '' as string,
})

const pagination = reactive({ page: 1, page_size: 20 })

async function loadData(): Promise<void> {
  await store.fetchList({
    page: pagination.page,
    page_size: pagination.page_size,
    contract_no: filters.contract_no || undefined,
    contract_type: filters.contract_type || undefined,
    verified: filters.verified === '' ? undefined : filters.verified === 'true',
  })
}

function handleSearch(): void {
  pagination.page = 1
  loadData()
}

function goDetail(id: string): void {
  router.push(`/contracts/${id}`)
}

onMounted(loadData)
</script>

<template>
  <div class="contract-list">
    <div class="filters">
      <ElInput v-model="filters.contract_no" placeholder="合同编号搜索" style="width: 200px" clearable />
      <ElSelect v-model="filters.contract_type" placeholder="合同类型" style="width: 120px" clearable>
        <ElOption label="前项" value="前项" />
        <ElOption label="后项" value="后项" />
      </ElSelect>
      <ElSelect v-model="filters.verified" placeholder="确认状态" style="width: 120px" clearable>
        <ElOption label="待确认" value="false" />
        <ElOption label="已确认" value="true" />
      </ElSelect>
      <ElButton type="primary" @click="handleSearch">查询</ElButton>
    </div>

    <ElTable :data="store.list" v-loading="store.loading" border>
      <ElTableColumn prop="contract_no" label="合同编号" />
      <ElTableColumn prop="contract_type" label="类型" width="80" />
      <ElTableColumn prop="party_a" label="甲方" />
      <ElTableColumn prop="party_b" label="乙方" />
      <ElTableColumn label="金额" width="140">
        <template #default="{ row }">{{ formatAmount(row.total_amount) }}</template>
      </ElTableColumn>
      <ElTableColumn label="状态" width="100">
        <template #default="{ row }">
          <StatusTag :status="row.verified ? '已确认' : '待确认'" />
        </template>
      </ElTableColumn>
      <ElTableColumn label="确认时间" width="160">
        <template #default="{ row }">{{ formatDate(row.verified_at) }}</template>
      </ElTableColumn>
      <ElTableColumn label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <ElButton link type="primary" @click="goDetail(row.id)">查看</ElButton>
          <ElButton link type="primary" @click="goDetail(row.id)">编辑</ElButton>
        </template>
      </ElTableColumn>
    </ElTable>

    <ElPagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.page_size"
      :total="store.total"
      layout="total, prev, pager, next"
      @current-change="loadData"
      style="margin-top: 16px"
    />
  </div>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
</style>
