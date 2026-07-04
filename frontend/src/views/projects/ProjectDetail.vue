<script setup lang="ts">
import { onMounted, ref, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElTabs,
  ElTabPane,
  ElDescriptions,
  ElDescriptionsItem,
  ElButton,
  ElMessage,
  ElTag,
  ElEmpty,
} from 'element-plus'
import SvgIcon from '@/components/SvgIcon.vue'
import { fetchContracts, fetchContractDetail, verifyContract } from '@/api/contracts'
import { fetchAcceptanceList, fetchAcceptanceDetail, verifyAcceptance } from '@/api/acceptance'
import { fetchContractAnalysis, fetchAcceptanceAnalysis, verifyContractAnalysis, verifyAcceptanceAnalysis } from '@/api/analysis'
import { useAuthStore } from '@/stores/auth'
import { formatAmount, formatDate, formatPercent } from '@/utils/format'
import type { ContractDetail } from '@/types/contract'
import type { AcceptanceReport } from '@/types/acceptance'
import type { ContractAnalysis, AcceptanceAnalysis } from '@/types/analysis'
import type { PaginatedData } from '@/types/api'
import type { AxiosError } from 'axios'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const contractNo = computed(() => route.params.contractNo as string)
const activeTab = ref('front-contract')
const loading = ref(false)

// 四份材料数据
const frontContract = ref<ContractDetail | null>(null)
const backContract = ref<ContractDetail | null>(null)
const frontAcceptance = ref<AcceptanceReport | null>(null)
const backAcceptance = ref<AcceptanceReport | null>(null)

// 两份分析数据
const contractAnalysis = ref<ContractAnalysis | null>(null)
const acceptanceAnalysis = ref<AcceptanceAnalysis | null>(null)

// 确认按钮 loading
const verifying = reactive<Record<string, boolean>>({
  'front-contract': false,
  'back-contract': false,
  'front-acceptance': false,
  'back-acceptance': false,
  'contract-analysis': false,
  'acceptance-analysis': false,
})

// 毛利率等级颜色
function getRateLevelTagType(level?: string): 'success' | 'warning' | 'danger' | 'info' {
  if (level === '利润倒挂') return 'danger'
  if (level === '低毛利') return 'warning'
  if (level === '正常') return 'success'
  return 'info'
}

// 一致性颜色
function getSimilarityTagType(similarity?: string): 'success' | 'warning' | 'danger' | 'info' {
  if (similarity === '完全一致') return 'success'
  if (similarity === '有一致性风险') return 'warning'
  if (similarity === '完全不一致') return 'danger'
  return 'info'
}

function isPermissionError(e: unknown): boolean {
  return (e as AxiosError)?.response?.status === 403
}

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const contractData = await fetchContracts({ contract_no: contractNo.value, page_size: 50 })
    const items = contractData.items
    const front = items.find((c) => c.contract_type === '前项')
    const back = items.find((c) => c.contract_type === '后项')

    const tasks: Promise<void>[] = []

    if (front) {
      tasks.push(
        fetchContractDetail(front.id).then((d) => { frontContract.value = d }).catch(() => {}),
      )
    }
    if (back) {
      tasks.push(
        fetchContractDetail(back.id).then((d) => { backContract.value = d }).catch(() => {}),
      )
    }

    tasks.push(
      fetchAcceptanceList({ contract_no: contractNo.value, page_size: 50 })
        .then(async (data: PaginatedData<AcceptanceReport>) => {
          const accs = data.items
          const frontAcc = accs.find((a) => a.acceptance_type === '前项')
          const backAcc = accs.find((a) => a.acceptance_type === '后项')
          const subTasks: Promise<void>[] = []
          if (frontAcc) {
            subTasks.push(
              fetchAcceptanceDetail(frontAcc.id).then((d) => { frontAcceptance.value = d }).catch(() => {}),
            )
          }
          if (backAcc) {
            subTasks.push(
              fetchAcceptanceDetail(backAcc.id).then((d) => { backAcceptance.value = d }).catch(() => {}),
            )
          }
          await Promise.all(subTasks)
        })
        .catch(() => {}),
    )

    tasks.push(
      fetchContractAnalysis(contractNo.value)
        .then((d) => { contractAnalysis.value = d })
        .catch(() => { contractAnalysis.value = null }),
    )
    tasks.push(
      fetchAcceptanceAnalysis(contractNo.value)
        .then((d) => { acceptanceAnalysis.value = d })
        .catch(() => { acceptanceAnalysis.value = null }),
    )

    await Promise.all(tasks)
  } finally {
    loading.value = false
  }
}

async function handleVerifyContract(type: 'front' | 'back'): Promise<void> {
  const target = type === 'front' ? frontContract.value : backContract.value
  if (!target) return
  const key = `${type}-contract`
  verifying[key] = true
  try {
    await verifyContract(target.id, authStore.adminInfo?.username || 'admin')
    ElMessage.success(`${type === 'front' ? '前项' : '后项'}合同已确认`)
    await loadData()
  } catch (e) {
    if (!isPermissionError(e)) ElMessage.error('确认失败')
  } finally {
    verifying[key] = false
  }
}

async function handleVerifyAcceptance(type: 'front' | 'back'): Promise<void> {
  const target = type === 'front' ? frontAcceptance.value : backAcceptance.value
  if (!target) return
  const key = `${type}-acceptance`
  verifying[key] = true
  try {
    await verifyAcceptance(target.id)
    ElMessage.success(`${type === 'front' ? '前项' : '后项'}验收报告已确认`)
    await loadData()
  } catch (e) {
    if (!isPermissionError(e)) ElMessage.error('确认失败')
  } finally {
    verifying[key] = false
  }
}

async function handleVerifyContractAnalysis(): Promise<void> {
  verifying['contract-analysis'] = true
  try {
    await verifyContractAnalysis(contractNo.value, authStore.adminInfo?.username || 'admin')
    ElMessage.success('合同分析已确认')
    await loadData()
  } catch (e) {
    if (!isPermissionError(e)) ElMessage.error('确认失败')
  } finally {
    verifying['contract-analysis'] = false
  }
}

async function handleVerifyAcceptanceAnalysis(): Promise<void> {
  verifying['acceptance-analysis'] = true
  try {
    await verifyAcceptanceAnalysis(contractNo.value, authStore.adminInfo?.username || 'admin')
    ElMessage.success('验收分析已确认')
    await loadData()
  } catch (e) {
    if (!isPermissionError(e)) ElMessage.error('确认失败')
  } finally {
    verifying['acceptance-analysis'] = false
  }
}

function goBack(): void {
  router.push('/projects')
}

onMounted(loadData)
</script>

<template>
  <div v-loading="loading" class="project-detail page-container">
    <!-- 顶部标题栏 -->
    <div class="detail-header">
      <ElButton text class="back-btn" @click="goBack">
        <SvgIcon name="back" :size="16" color="inherit" style="margin-right: 4px" />
        返回
      </ElButton>
      <div class="header-divider"></div>
      <h3 class="title nums">{{ contractNo }}</h3>
      <ElTag v-if="frontContract" size="small" type="danger" effect="plain" class="project-tag">
        项目详情
      </ElTag>
    </div>

    <!-- Tab 导航 -->
    <ElTabs v-model="activeTab" class="detail-tabs" type="border-card">
      <!-- ── 前项合同 ── -->
      <ElTabPane label="前项合同" name="front-contract">
        <template v-if="frontContract">
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="合同编号">{{ frontContract.contract_no }}</ElDescriptionsItem>
            <ElDescriptionsItem label="合同类型">{{ frontContract.contract_type }}</ElDescriptionsItem>
            <ElDescriptionsItem label="甲方">{{ frontContract.party_a || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="乙方">{{ frontContract.party_b || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="我方角色">{{ frontContract.our_role || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="签约日期">{{ formatDate(frontContract.signing_date) }}</ElDescriptionsItem>
            <ElDescriptionsItem label="工期">{{ frontContract.contract_period || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="合同金额"><span class="amount-value">{{ formatAmount(frontContract.total_amount) }}</span></ElDescriptionsItem>
            <ElDescriptionsItem label="大写金额">{{ frontContract.amount_uppercase || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="税率">{{ frontContract.tax_rate != null ? formatPercent(frontContract.tax_rate) : '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="付款条款" :span="2">{{ frontContract.payment_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="交付条款" :span="2">{{ frontContract.delivery_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收条款" :span="2">{{ frontContract.acceptance_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="违约责任" :span="2">{{ frontContract.breach_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="质保条款" :span="2">{{ frontContract.warranty_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="知识产权条款" :span="2">{{ frontContract.ip_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="其他关键条款" :span="2">{{ frontContract.other_key_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="源文件">{{ frontContract.source_file_name || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="确认状态">
              <ElTag :type="frontContract.verified ? 'success' : 'warning'" size="small" effect="dark">
                {{ frontContract.verified ? '已确认' : '待确认' }}
              </ElTag>
            </ElDescriptionsItem>
          </ElDescriptions>
          <div class="tab-footer">
            <ElButton
              type="primary"
              :disabled="frontContract.verified"
              :loading="verifying['front-contract']"
              @click="handleVerifyContract('front')"
            >
              {{ frontContract.verified ? '已确认' : '确认无误' }}
            </ElButton>
          </div>
        </template>
        <ElEmpty v-else description="前项合同未上传" />
      </ElTabPane>

      <!-- ── 后项合同 ── -->
      <ElTabPane label="后项合同" name="back-contract">
        <template v-if="backContract">
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="合同编号">{{ backContract.contract_no }}</ElDescriptionsItem>
            <ElDescriptionsItem label="合同类型">{{ backContract.contract_type }}</ElDescriptionsItem>
            <ElDescriptionsItem label="甲方">{{ backContract.party_a || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="乙方">{{ backContract.party_b || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="我方角色">{{ backContract.our_role || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="签约日期">{{ formatDate(backContract.signing_date) }}</ElDescriptionsItem>
            <ElDescriptionsItem label="工期">{{ backContract.contract_period || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="合同金额"><span class="amount-value">{{ formatAmount(backContract.total_amount) }}</span></ElDescriptionsItem>
            <ElDescriptionsItem label="大写金额">{{ backContract.amount_uppercase || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="税率">{{ backContract.tax_rate != null ? formatPercent(backContract.tax_rate) : '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="付款条款" :span="2">{{ backContract.payment_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="交付条款" :span="2">{{ backContract.delivery_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收条款" :span="2">{{ backContract.acceptance_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="违约责任" :span="2">{{ backContract.breach_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="质保条款" :span="2">{{ backContract.warranty_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="知识产权条款" :span="2">{{ backContract.ip_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="其他关键条款" :span="2">{{ backContract.other_key_terms || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="源文件">{{ backContract.source_file_name || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="确认状态">
              <ElTag :type="backContract.verified ? 'success' : 'warning'" size="small" effect="dark">
                {{ backContract.verified ? '已确认' : '待确认' }}
              </ElTag>
            </ElDescriptionsItem>
          </ElDescriptions>
          <div class="tab-footer">
            <ElButton
              type="primary"
              :disabled="backContract.verified"
              :loading="verifying['back-contract']"
              @click="handleVerifyContract('back')"
            >
              {{ backContract.verified ? '已确认' : '确认无误' }}
            </ElButton>
          </div>
        </template>
        <ElEmpty v-else description="后项合同未上传" />
      </ElTabPane>

      <!-- ── 前项验收报告 ── -->
      <ElTabPane label="前项验收报告" name="front-acceptance">
        <template v-if="frontAcceptance">
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="验收编号">{{ frontAcceptance.acceptance_no || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="合同编号">{{ frontAcceptance.contract_no }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收类型">{{ frontAcceptance.acceptance_type || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收日期">{{ formatDate(frontAcceptance.acceptance_date) }}</ElDescriptionsItem>
            <ElDescriptionsItem label="类型判定依据" :span="2">{{ frontAcceptance.type_judge_basis || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收内容" :span="2">{{ frontAcceptance.acceptance_content || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收结果" :span="2">
              <ElTag :type="frontAcceptance.acceptance_result === '合格' ? 'success' : 'warning'" size="small" effect="dark">
                {{ frontAcceptance.acceptance_result || '—' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="源文件">{{ frontAcceptance.source_file_name || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="确认状态">
              <ElTag :type="frontAcceptance.verified ? 'success' : 'warning'" size="small" effect="dark">
                {{ frontAcceptance.verified ? '已确认' : '待确认' }}
              </ElTag>
            </ElDescriptionsItem>
          </ElDescriptions>
          <div class="tab-footer">
            <ElButton
              type="primary"
              :disabled="frontAcceptance.verified"
              :loading="verifying['front-acceptance']"
              @click="handleVerifyAcceptance('front')"
            >
              {{ frontAcceptance.verified ? '已确认' : '确认无误' }}
            </ElButton>
          </div>
        </template>
        <ElEmpty v-else description="前项验收报告未上传" />
      </ElTabPane>

      <!-- ── 后项验收报告 ── -->
      <ElTabPane label="后项验收报告" name="back-acceptance">
        <template v-if="backAcceptance">
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="验收编号">{{ backAcceptance.acceptance_no || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="合同编号">{{ backAcceptance.contract_no }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收类型">{{ backAcceptance.acceptance_type || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收日期">{{ formatDate(backAcceptance.acceptance_date) }}</ElDescriptionsItem>
            <ElDescriptionsItem label="类型判定依据" :span="2">{{ backAcceptance.type_judge_basis || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收内容" :span="2">{{ backAcceptance.acceptance_content || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="验收结果" :span="2">
              <ElTag :type="backAcceptance.acceptance_result === '合格' ? 'success' : 'warning'" size="small" effect="dark">
                {{ backAcceptance.acceptance_result || '—' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="源文件">{{ backAcceptance.source_file_name || '—' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="确认状态">
              <ElTag :type="backAcceptance.verified ? 'success' : 'warning'" size="small" effect="dark">
                {{ backAcceptance.verified ? '已确认' : '待确认' }}
              </ElTag>
            </ElDescriptionsItem>
          </ElDescriptions>
          <div class="tab-footer">
            <ElButton
              type="primary"
              :disabled="backAcceptance.verified"
              :loading="verifying['back-acceptance']"
              @click="handleVerifyAcceptance('back')"
            >
              {{ backAcceptance.verified ? '已确认' : '确认无误' }}
            </ElButton>
          </div>
        </template>
        <ElEmpty v-else description="后项验收报告未上传" />
      </ElTabPane>

      <!-- ── 合同分析 ── -->
      <ElTabPane label="合同分析" name="contract-analysis">
        <template v-if="contractAnalysis">
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="毛利率">
              <span class="rate-value">{{ contractAnalysis.rate != null ? formatPercent(contractAnalysis.rate) : '—' }}</span>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="毛利率等级">
              <ElTag :type="getRateLevelTagType(contractAnalysis.rate_level)" size="small" effect="dark">
                {{ contractAnalysis.rate_level || '—' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="条款一致性" :span="2">
              <ElTag :type="getSimilarityTagType(contractAnalysis.similarity)" size="small" effect="dark">
                {{ contractAnalysis.similarity || '—' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="分析详情" :span="2">
              <div class="analysis-text">{{ contractAnalysis.analysis || '—' }}</div>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="确认状态">
              <ElTag :type="contractAnalysis.verified ? 'success' : 'warning'" size="small" effect="dark">
                {{ contractAnalysis.verified ? '已确认' : '待确认' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="确认人">{{ contractAnalysis.verified_by || '—' }}</ElDescriptionsItem>
          </ElDescriptions>
          <div class="tab-footer">
            <ElButton
              type="primary"
              :disabled="contractAnalysis.verified"
              :loading="verifying['contract-analysis']"
              @click="handleVerifyContractAnalysis()"
            >
              {{ contractAnalysis.verified ? '已确认' : '确认无误' }}
            </ElButton>
          </div>
        </template>
        <ElEmpty v-else description="合同分析尚未执行，请通过 Agent 发起风险分析" />
      </ElTabPane>

      <!-- ── 验收分析 ── -->
      <ElTabPane label="验收分析" name="acceptance-analysis">
        <template v-if="acceptanceAnalysis">
          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="一致性" :span="2">
              <ElTag :type="getSimilarityTagType(acceptanceAnalysis.similarity)" size="small" effect="dark">
                {{ acceptanceAnalysis.similarity || '—' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="分析详情" :span="2">
              <div class="analysis-text">{{ acceptanceAnalysis.analysis || '—' }}</div>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="确认状态">
              <ElTag :type="acceptanceAnalysis.verified ? 'success' : 'warning'" size="small" effect="dark">
                {{ acceptanceAnalysis.verified ? '已确认' : '待确认' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="确认人">{{ acceptanceAnalysis.verified_by || '—' }}</ElDescriptionsItem>
          </ElDescriptions>
          <div class="tab-footer">
            <ElButton
              type="primary"
              :disabled="acceptanceAnalysis.verified"
              :loading="verifying['acceptance-analysis']"
              @click="handleVerifyAcceptanceAnalysis()"
            >
              {{ acceptanceAnalysis.verified ? '已确认' : '确认无误' }}
            </ElButton>
          </div>
        </template>
        <ElEmpty v-else description="验收分析尚未执行，请通过 Agent 发起风险分析" />
      </ElTabPane>
    </ElTabs>
  </div>
</template>

<style scoped>
.project-detail {
  max-width: 1200px;
}

/* 顶部标题 */
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.back-btn {
  font-size: 14px;
  color: var(--color-ink-2);
}
.back-btn:hover {
  color: var(--color-primary);
}

.header-divider {
  width: 1px;
  height: 20px;
  background: var(--color-border);
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-ink);
}

.project-tag {
  font-weight: 500;
}

/* Tab 导航 */
.detail-tabs {
  margin-top: 8px;
}
.detail-tabs :deep(.el-tabs__header) {
  background: var(--color-paper);
  border-bottom: 1px solid var(--color-border-soft);
}
.detail-tabs :deep(.el-tabs__item.is-active) {
  color: var(--color-primary) !important;
  font-weight: 600;
}

/* 底部操作区 */
.tab-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 金额 */
.amount-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-gold);
  font-variant-numeric: tabular-nums;
}

/* 毛利率数值 */
.rate-value {
  font-size: 16px;
  font-weight: 700;
  background: var(--color-primary-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-variant-numeric: tabular-nums;
}

/* 分析文本 */
.analysis-text {
  white-space: pre-wrap;
  line-height: 1.8;
  color: var(--color-ink);
  background: var(--color-paper-2);
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-primary);
  font-size: 13px;
}
</style>
