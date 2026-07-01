<script setup lang="ts">
import { computed } from 'vue'
import { ElTable, ElTableColumn } from 'element-plus'
import type { LineItemComparison } from '@/types/comparison'

const props = defineProps<{
  frontContent: string
  backContent: string
  items?: LineItemComparison[]
}>()

const hasItems = computed(() => (props.items?.length ?? 0) > 0)
</script>

<template>
  <div class="diff-display">
    <div class="row">
      <div class="cell front">
        <div class="label">前项</div>
        <div class="content">{{ frontContent }}</div>
      </div>
      <div class="cell back">
        <div class="label">后项</div>
        <div class="content">{{ backContent }}</div>
      </div>
    </div>
    <ElTable v-if="hasItems" :data="items" border size="small">
      <ElTableColumn prop="item_name" label="分项" />
      <ElTableColumn prop="front_quantity" label="前项数量" />
      <ElTableColumn prop="back_quantity" label="后项数量" />
      <ElTableColumn prop="match_status" label="匹配状态" />
    </ElTable>
  </div>
</template>

<style scoped>
.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}
.cell {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
.label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}
.content {
  white-space: pre-wrap;
  color: #606266;
}
</style>
