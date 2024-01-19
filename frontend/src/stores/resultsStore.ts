import type { Ref } from 'vue'
import type { Folder, MainResults, OrderSelect, Pending, OtherResult } from '@/assets/types'
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { RATE_LABELS } from '@/assets/global'

export const useResultsStore = defineStore('resultsStore', () => {
  const results: Ref<MainResults> = ref({
    folders: [],
    blob: null
  })

  const orderBy: Ref<OrderSelect> = ref({
    selected: 'F1 score',
    options: RATE_LABELS,
    descending: true
  })

  const toggleDirection = () => {
    orderBy.value.descending = !orderBy.value.descending
  }

  const feed = computed(() =>
    results.value.folders.sort((resultA: Folder, resultB: Folder) =>
      orderBy.value.descending
        ? Number(resultB.trueRates![orderBy.value.selected as (typeof RATE_LABELS)[number]]) -
          Number(resultA.trueRates![orderBy.value.selected as (typeof RATE_LABELS)[number]])
        : Number(resultA.trueRates![orderBy.value.selected as (typeof RATE_LABELS)[number]]) -
          Number(resultB.trueRates![orderBy.value.selected as (typeof RATE_LABELS)[number]])
    )
  )

  const pending: Ref<Pending> = ref({
    status: false,
    progress: null,
    msg: null
  })

  const errorResult: Ref<OtherResult> = ref({
    status: false,
    msg: null,
    blob: null
  })

  const resetAll = () => {
    // Reset main results
    results.value = {
      folders: [],
      blob: null
    }
    
    // Reset test results
    testResult.value = {
      status: false,
      msg: null,
      blob: null,
    }
    
    // Reset error results
    errorResult.value = {
      status: false,
      msg: null,
      blob: null
    }
  }

  const testResult: Ref<OtherResult> = ref({
    status: false,
    msg: null,
    blob: null,
  })

  return {
    errorResult,
    feed,
    orderBy,
    pending,
    results,
    testResult,
    resetAll,
    toggleDirection,
  }
})
