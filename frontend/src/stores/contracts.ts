import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchContracts, fetchProjectCards, type ContractListParams, type CardListParams } from '@/api/contracts'
import type { Contract, ProjectCard } from '@/types/contract'

export const useContractStore = defineStore('contracts', () => {
  const list = ref<Contract[]>([])
  const cards = ref<ProjectCard[]>([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchList(params: ContractListParams): Promise<void> {
    loading.value = true
    try {
      const data = await fetchContracts(params)
      list.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchCards(params?: CardListParams): Promise<void> {
    loading.value = true
    try {
      const data = await fetchProjectCards(params)
      cards.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  return { list, cards, total, loading, fetchList, fetchCards }
})
