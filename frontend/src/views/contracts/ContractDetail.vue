<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElDescriptions, ElDescriptionsItem, ElCollapse, ElCollapseItem, ElTable, ElTableColumn, ElButton, ElMessage } from 'element-plus'
import { fetchContractDetail, verifyContract } from '@/api/contracts'
import { useAuthStore } from '@/stores/auth'
import { formatAmount, formatDate } from '@/utils/format'
import StatusTag from '@/components/StatusTag.vue'
import type { ContractDetail } from '@/types/contract'

const route = useRoute()
const authStore = useAuthStore()
const detail = ref<ContractDetail | null>(null)
const loading = ref(false)

async function loadDetail(): Promise<void> {
  loading.value = true
  try {
    detail.value = await fetchContractDetail(route.params.id as string)
  } finally {
    loading.value = false
  }
}

async function handleVerify(): Promise<void> {
  if (!detail.value) return
  await verifyContract(detail.value.id, authStore.adminInfo?.username || 'admin')
  ElMessage.success('已确认')
  loadDetail()
}

onMounted(loadDetail)
</script>

<template>
  <div v-loading="loading" class="contract-detail">
    <template v-if="detail">
      <h3>合同详情 - {{ detail.contract_no }} {{ detail.contract_type }}</h3>

      <ElDescriptions :column="2" border>
        <ElDescriptionsItem label="合同编号">{{ detail.contract_no }}</ElDescriptionsItem>
        <ElDescriptionsItem label="合同类型">{{ detail.contract_type }}</ElDescriptionsItem>
        <ElDescriptionsItem label="甲方">{{ detail.party_a }}</ElDescriptionsItem>
        <ElDescriptionsItem label="乙方">{{ detail.party_b }}</ElDescriptionsItem>
        <ElDescriptionsItem label="签约日期">{{ formatDate(detail.signing_date) }}</ElDescriptionsItem>
        <ElDescriptionsItem label="总金额">{{ formatAmount(detail.total_amount) }}</ElDescriptionsItem>
        <ElDescriptionsItem label="工期">{{ detail.contract_period }}</ElDescriptionsItem>
        <ElDescriptionsItem label="税率">{{ detail.tax_rate }}</ElDescriptionsItem>
        <ElDescriptionsItem label="状态">
          <StatusTag :status="detail.verified ? '已确认' : '待确认'" />
        </ElDescriptionsItem>
      </ElDescriptions>

      <ElCollapse class="mt-16">
        <ElCollapseItem title="付款条款" name="1">{{ detail.payment_terms || '—' }}</ElCollapseItem>
        <ElCollapseItem title="交付条款" name="2">{{ detail.delivery_terms || '—' }}</ElCollapseItem>
        <ElCollapseItem title="验收条款" name="3">{{ detail.acceptance_terms || '—' }}</ElCollapseItem>
        <ElCollapseItem title="违约责任" name="4">{{ detail.breach_terms || '—' }}</ElCollapseItem>
        <ElCollapseItem title="质保条款" name="5">{{ detail.warranty_terms || '—' }}</ElCollapseItem>
      </ElCollapse>

      <h4 class="mt-16">分项清单</h4>
      <ElTable :data="detail.line_items" border size="small">
        <ElTableColumn prop="item_no" label="序号" width="70" />
        <ElTableColumn prop="item_name" label="名称" />
        <ElTableColumn prop="unit" label="单位" width="80" />
        <ElTableColumn prop="quantity" label="数量" />
        <ElTableColumn prop="unit_price" label="单价" />
        <ElTableColumn label="金额">
          <template #default="{ row }">{{ formatAmount(row.amount) }}</template>
        </ElTableColumn>
      </ElTable>

      <div class="actions mt-16">
        <ElButton type="primary" :disabled="detail.verified" @click="handleVerify">确认无误</ElButton>
        <ElButton>编辑修正</ElButton>
      </div>
    </template>
  </div>
</template>

<style scoped>
.mt-16 {
  margin-top: 16px;
}
.actions {
  display: flex;
  gap: 12px;
}
</style>
