<script setup lang="ts">
import { ElTag } from 'element-plus'

defineProps<{ status?: string }>()

function tagType(status?: string): 'success' | 'warning' | 'primary' | 'info' {
  if (status === '已确认' || status === '审查完成') return 'success'
  if (status === '待确认') return 'warning'
  if (status === '比对完成') return 'primary'
  return 'info'
}
</script>

<template>
  <ElTag :type="tagType(status)" effect="light">{{ status }}</ElTag>
</template>
