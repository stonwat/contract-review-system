<script setup lang="ts">
/**
 * EChart —— ECharts 轻量封装
 * - 按需引入图表与组件，减小打包体积
 * - 自动 resize，组件卸载时清理
 */
import { ref, onMounted, onBeforeUnmount, watch, shallowRef } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart, PieChart, LineChart,
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
  CanvasRenderer,
])

const props = defineProps<{
  option: echarts.EChartsCoreOption
  height?: string
}>()

const elRef = ref<HTMLDivElement | null>(null)
const chart = shallowRef<echarts.ECharts | null>(null)

function render(): void {
  if (!elRef.value) return
  if (!chart.value) {
    chart.value = echarts.init(elRef.value)
  }
  chart.value.setOption(props.option, true)
}

function resize(): void {
  chart.value?.resize()
}

onMounted(() => {
  render()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart.value?.dispose()
  chart.value = null
})

watch(() => props.option, render, { deep: true })
</script>

<template>
  <div ref="elRef" class="echart" :style="{ height: height || '300px' }" />
</template>

<style scoped>
.echart {
  width: 100%;
}
</style>
