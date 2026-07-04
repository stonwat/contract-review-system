<script setup lang="ts">
/**
 * SvgIcon —— iconfont symbol 模式统一组件
 *
 * 用法：<SvgIcon name="dashboard" :size="20" color="primary" />
 *
 * 优先使用 iconfont SVG symbol（已内置 20+ 线性图标），
 * 未匹配时回退到 Element Plus 线性图标。
 */
import { computed } from 'vue'
import {
  Odometer, FolderOpened, TrendCharts, UserFilled,
  Document, Clock, CircleCheck, Warning,
  Search, Download, Edit, Delete, View, Check, ArrowLeft, SwitchButton,
  CopyDocument, Tickets,
} from '@element-plus/icons-vue'

type IconName =
  | 'dashboard' | 'project' | 'report' | 'account'
  | 'contract' | 'pending' | 'ai' | 'done' | 'risk'
  | 'search' | 'export' | 'edit' | 'delete' | 'view' | 'confirm' | 'back' | 'logout'
  | 'file' | 'file-copy' | 'acceptance'

const props = withDefaults(
  defineProps<{
    name: IconName
    size?: number | string
    color?: 'primary' | 'gold' | 'success' | 'warning' | 'danger' | 'info' | 'inherit'
  }>(),
  {
    size: 18,
    color: 'inherit',
  },
)

// iconfont symbol id 映射（接入后填入实际 id，形如 'icon-dashboard'）
const SYMBOL_MAP: Partial<Record<IconName, string>> = {
  dashboard: 'icon-dashboard',
  project: 'icon-project',
  report: 'icon-report',
  account: 'icon-account',
  contract: 'icon-contract',
  pending: 'icon-pending',
  ai: 'icon-ai',
  done: 'icon-done',
  risk: 'icon-risk',
  search: 'icon-search',
  export: 'icon-export',
  edit: 'icon-edit',
  delete: 'icon-delete',
  view: 'icon-view',
  confirm: 'icon-confirm',
  back: 'icon-back',
  logout: 'icon-logout',
  file: 'icon-file',
  'file-copy': 'icon-file-copy',
  acceptance: 'icon-acceptance',
}

// Element Plus 回退图标
const EP_FALLBACK: Record<IconName, unknown> = {
  dashboard: Odometer,
  project: FolderOpened,
  report: TrendCharts,
  account: UserFilled,
  contract: Document,
  pending: Clock,
  ai: CircleCheck,
  done: CircleCheck,
  risk: Warning,
  search: Search,
  export: Download,
  edit: Edit,
  delete: Delete,
  view: View,
  confirm: Check,
  back: ArrowLeft,
  logout: SwitchButton,
  file: Document,
  'file-copy': CopyDocument,
  acceptance: Tickets,
}

const colorVar = computed(() => {
  switch (props.color) {
    case 'primary': return 'var(--color-primary)'
    case 'gold': return 'var(--color-gold)'
    case 'success': return 'var(--color-success)'
    case 'warning': return 'var(--color-warning)'
    case 'danger': return 'var(--color-danger)'
    case 'info': return 'var(--color-info)'
    default: return 'currentColor'
  }
})

const useSymbol = computed(() => !!SYMBOL_MAP[props.name])
const symbolId = computed(() => SYMBOL_MAP[props.name] || '')
const fallbackComp = computed(() => EP_FALLBACK[props.name])
const sizeStr = computed(() =>
  typeof props.size === 'number' ? `${props.size}px` : props.size,
)
</script>

<template>
  <!-- iconfont symbol 模式 -->
  <svg
    v-if="useSymbol"
    class="svg-icon"
    aria-hidden="true"
    :width="sizeStr"
    :height="sizeStr"
    :style="{ color: colorVar, fill: 'currentColor' }"
  >
    <use :xlink:href="`#${symbolId}`" />
  </svg>
  <!-- Element Plus 回退 -->
  <component
    :is="fallbackComp"
    v-else
    :size="sizeStr"
    :style="{ color: colorVar, width: sizeStr, height: sizeStr }"
  />
</template>

<style scoped>
.svg-icon {
  display: inline-block;
  vertical-align: -0.15em;
  flex-shrink: 0;
}
</style>
