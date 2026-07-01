import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchContracts, type ContractListParams } from '@/api/contracts'
import type { Contract } from '@/types/contract'

export const useContractStore = defineStore('contracts', () => {
  const list = ref<Contract[]>([])
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

  return { list, total, loading, fetchList }
})
