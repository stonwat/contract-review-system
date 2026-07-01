<script setup lang="ts">
import { ElTag } from 'element-plus'
import type { RiskLevel } from '@/types/risk'

defineProps<{ level?: RiskLevel | string; dismissed?: boolean }>()

function tagType(level?: string, dismissed?: boolean): 'success' | 'warning' | 'danger' | 'info' {
  if (dismissed) return 'success'
  if (level === '高') return 'danger'
  if (level === '中') return 'warning'
  if (level === '低') return 'info'
  return 'info'
}
</script>

<template>
  <ElTag :type="tagType(level, dismissed)" effect="light">
    {{ dismissed ? '已忽略' : level }}
  </ElTag>
</template>
