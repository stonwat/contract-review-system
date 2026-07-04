<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElCard, ElRow, ElCol, ElInput, ElSelect, ElOption, ElButton, ElTag, ElEmpty, ElDivider, ElTooltip } from 'element-plus'
import { useContractStore } from '@/stores/contracts'
import { formatAmount } from '@/utils/format'
import SvgIcon from '@/components/SvgIcon.vue'

const store = useContractStore()
const router = useRouter()

const filters = reactive({
  keyword: '',
  city: '' as string,
})

async function loadData(): Promise<void> {
  await store.fetchCards({
    keyword: filters.keyword || undefined,
    city: filters.city || undefined,
  })
}

function handleSearch(): void {
  loadData()
}

function openDetail(contractNo: string): void {
  router.push(`/projects/${contractNo}`)
}

function getRiskTagType(risk?: string): 'success' | 'warning' | 'danger' | 'info' {
  if (risk === '高风险') return 'danger'
  if (risk === '低风险') return 'success'
  return 'info'
}

function riskClass(risk?: string): string {
  if (risk === '高风险') return 'risk-high'
  if (risk === '低风险') return 'risk-low'
  return 'risk-none'
}

onMounted(loadData)
</script>

<template>
  <div class="project-card-list page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">项目管理</h1>
      <span class="header-count" v-if="!store.loading">
        共 {{ store.cards?.length || 0 }} 个项目
      </span>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <ElInput
        v-model="filters.keyword"
        placeholder="合同编号 / 项目名称搜索"
        style="width: 260px"
        clearable
      >
        <template #prefix><SvgIcon name="search" :size="16" color="info" /></template>
      </ElInput>
      <ElSelect v-model="filters.city" placeholder="地市筛选" style="width: 140px" clearable>
        <ElOption label="鹤岗" value="鹤岗" />
        <ElOption label="伊春" value="伊春" />
        <ElOption label="齐齐哈尔" value="齐齐哈尔" />
        <ElOption label="哈尔滨" value="哈尔滨" />
      </ElSelect>
      <ElButton type="primary" @click="handleSearch">查询</ElButton>
    </div>

    <!-- 空状态 -->
    <ElEmpty v-if="!store.loading && (!store.cards || store.cards.length === 0)" description="暂无项目数据" />

    <!-- 卡片网格 -->
    <div v-loading="store.loading" class="card-grid">
      <ElCard
        v-for="(card, idx) in store.cards"
        :key="card.contract_no"
        class="project-card fade-in-up"
        :class="[
          `delay-${Math.min(idx + 1, 6)}`,
          riskClass(card.project_risk),
        ]"
        shadow="never"
        @click="openDetail(card.contract_no)"
      >
        <!-- 卡片顶部：项目名 + 合同编号 + 地市 -->
        <div class="card-header">
          <div class="card-title-area">
            <span class="project-name">{{ card.project_name || card.contract_no }}</span>
            <span class="contract-no nums">{{ card.contract_no }}</span>
          </div>
          <ElTag v-if="card.city" size="small" class="city-tag" effect="plain">
            {{ card.city }}
          </ElTag>
        </div>

        <ElDivider style="margin: 12px 0" />

        <!-- 卡片中部：前后项信息 -->
        <ElRow :gutter="16">
          <ElCol :span="12">
            <div class="contract-side">
              <div class="side-title">
                <SvgIcon name="file" :size="14" color="primary" />
                前项合同
              </div>
              <template v-if="card.front_contract">
                <div class="side-row"><span class="label">甲方</span><span class="value">{{ card.front_contract.party_a || '—' }}</span></div>
                <div class="side-row"><span class="label">乙方</span><span class="value">{{ card.front_contract.party_b || '—' }}</span></div>
                <div class="side-row"><span class="label">金额</span><span class="value amount nums">{{ formatAmount(card.front_contract.total_amount) }}</span></div>
              </template>
              <div v-else class="not-uploaded">未上传</div>
            </div>
          </ElCol>
          <ElCol :span="12">
            <div class="contract-side">
              <div class="side-title">
                <SvgIcon name="file-copy" :size="14" color="gold" />
                后项合同
              </div>
              <template v-if="card.back_contract">
                <div class="side-row"><span class="label">甲方</span><span class="value">{{ card.back_contract.party_a || '—' }}</span></div>
                <div class="side-row"><span class="label">乙方</span><span class="value">{{ card.back_contract.party_b || '—' }}</span></div>
                <div class="side-row"><span class="label">金额</span><span class="value amount nums">{{ formatAmount(card.back_contract.total_amount) }}</span></div>
              </template>
              <div v-else class="not-uploaded">未上传</div>
            </div>
          </ElCol>
        </ElRow>

        <ElDivider style="margin: 12px 0" />

        <!-- 卡片底部 -->
        <div class="card-footer">
          <div class="footer-left">
            <span class="footer-label">风险</span>
            <ElTag
              v-if="card.project_risk"
              :type="getRiskTagType(card.project_risk)"
              size="small"
              effect="dark"
            >
              {{ card.project_risk }}
            </ElTag>
            <span v-else class="unanalyzed">未分析</span>
            <ElTag
              v-if="card.llm_analyzed"
              size="small"
              type="success"
              effect="plain"
              style="margin-left: 6px"
            >
              AI 已分析
            </ElTag>
          </div>
          <div class="footer-right">
            <ElTooltip content="前项合同" placement="top">
              <span class="mat-dot" :class="{ active: card.has_front_contract }">
                <SvgIcon name="file" :size="12" />
              </span>
            </ElTooltip>
            <ElTooltip content="后项合同" placement="top">
              <span class="mat-dot" :class="{ active: card.has_back_contract }">
                <SvgIcon name="file-copy" :size="12" />
              </span>
            </ElTooltip>
            <ElTooltip content="前项验收报告" placement="top">
              <span class="mat-dot" :class="{ active: card.has_front_acceptance }">
                <SvgIcon name="acceptance" :size="12" />
              </span>
            </ElTooltip>
            <ElTooltip content="后项验收报告" placement="top">
              <span class="mat-dot" :class="{ active: card.has_back_acceptance }">
                <SvgIcon name="acceptance" :size="12" />
              </span>
            </ElTooltip>
          </div>
        </div>
      </ElCard>
    </div>
  </div>
</template>

<style scoped>
.project-card-list {
  max-width: 1400px;
}

/* 页面头部 */
.header-count {
  font-size: 13px;
  color: var(--color-text-placeholder);
}

/* 筛选栏 */
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

/* 卡片网格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(520px, 1fr));
  gap: 16px;
}

.project-card {
  position: relative;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: box-shadow 0.25s ease, transform 0.25s ease;
  overflow: hidden;
}
.project-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  transition: width 0.25s ease;
}
.project-card.risk-high::before { background: var(--color-danger); }
.project-card.risk-low::before { background: var(--color-success); }
.project-card.risk-none::before { background: var(--color-border); }
.project-card:hover {
  box-shadow: var(--shadow-md) !important;
  transform: translateY(-2px);
}
.project-card:hover::before { width: 4px; }

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.card-title-area {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.project-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 260px;
}

.contract-no {
  font-size: 12px;
  color: var(--color-text-placeholder);
  white-space: nowrap;
}

.city-tag {
  flex-shrink: 0;
}
.city-tag.el-tag--plain {
  background: rgba(196, 29, 52, 0.06);
  border-color: rgba(196, 29, 52, 0.2);
  color: var(--color-primary);
}

/* 合同侧栏 */
.contract-side {
  padding: 4px 0;
}

.side-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-ink-2);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.side-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.side-dot.front {
  background: var(--color-primary);
}
.side-dot.back {
  background: var(--color-gold);
}

.side-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  line-height: 1.8;
}
.side-row .label {
  color: var(--color-text-placeholder);
  flex-shrink: 0;
}
.side-row .value {
  color: var(--color-text-regular);
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-left: 8px;
}
.side-row .value.amount {
  font-weight: 600;
  color: var(--color-gold);
}

.not-uploaded {
  color: var(--color-text-disabled);
  font-size: 13px;
  text-align: center;
  padding: 16px 0;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.footer-label {
  font-size: 13px;
  color: var(--color-text-placeholder);
}

.unanalyzed {
  font-size: 13px;
  color: var(--color-text-disabled);
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mat-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--color-canvas);
  color: var(--color-ink-4);
  cursor: default;
  transition: all 0.2s;
}
.mat-dot.active {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}
</style>
