import type { Ref } from 'vue'
import type { Folder, OrderSelect } from '@/assets/types'
import { computed, reactive, ref } from 'vue'
import { defineStore } from 'pinia'
import { RATE_LABELS } from '@/assets/global'

export const useResultsStore = defineStore('resultsStore', () => {
  const results: Ref<Folder[]> = ref([])

  const addResult = (result: Folder) => {
    results.value.push(result)
  }

  const orderBy: Ref<OrderSelect> = ref({
    selected: 'F1 score',
    options: RATE_LABELS,
    descending: true
  })

  const feed = computed(() =>
    results.value.sort((resultA: Folder, resultB: Folder) =>
      orderBy.value.descending
        ? Number(resultA.trueRates![orderBy.value.selected as (typeof RATE_LABELS)[number]]) -
          Number(resultB.trueRates![orderBy.value.selected as (typeof RATE_LABELS)[number]])
        : Number(resultB.trueRates![orderBy.value.selected as (typeof RATE_LABELS)[number]]) -
          Number(resultA.trueRates![orderBy.value.selected as (typeof RATE_LABELS)[number]])
    )
  )
  return {
    orderBy,
    results,
    feed
  }
})
