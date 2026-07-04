<script setup lang="ts">
import { ElTag } from 'element-plus'

defineProps<{ status?: string }>()

function tagType(status?: string): 'success' | 'warning' | 'danger' | 'info' {
  if (status === '已确认' || status === '审查完成') return 'success'
  if (status === '待确认' || status === '待审查') return 'warning'
  if (status === '高风险') return 'danger'
  if (status === '已完成') return 'success'
  return 'info'
}
</script>

<template>
  <ElTag :type="tagType(status)" effect="light" size="small" class="status-tag">
    {{ status }}
  </ElTag>
</template>

<style scoped>
.status-tag {
  font-weight: 500;
  border-radius: 4px;
}
</style>
