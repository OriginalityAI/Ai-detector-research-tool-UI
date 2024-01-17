import type { Ref } from 'vue'
import type { Folder, OrderSelect, Pending } from '@/assets/types'
import { computed, reactive, ref } from 'vue'
import { defineStore } from 'pinia'
import { RATE_LABELS } from '@/assets/global'

export const useResultsStore = defineStore('resultsStore', () => {
  const results: Ref<Folder[]> = ref([])

  const updateResults = (newResults: Folder[]) => {
    results.value = newResults;
  } 

  const orderBy: Ref<OrderSelect> = ref({
    selected: 'F1 score',
    options: RATE_LABELS,
    descending: true
  })

  const toggleDirection = () => {
    orderBy.value.descending = !orderBy.value.descending
  }

  const feed = computed(() =>
    results.value.sort((resultA: Folder, resultB: Folder) =>
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
    msg: null,
  })

  const zipBlob: Ref<Blob | null> = ref(null)

  return {
    feed,
    orderBy,
    pending,
    results,
    zipBlob,
    toggleDirection,
    updateResults,
  }
})
