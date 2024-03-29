import { computed, ref } from 'vue'
import type { Ref } from 'vue'
import { defineStore } from 'pinia'
import type { UserInput } from '@/assets/types'

export const useInputStore = defineStore('inputStore', () => {
  const input: Ref<UserInput> = ref({
    csv: undefined,
    detectors: {
      Originality: {
        selected: true,
        key: ''
      },
      GPTZero: {
        selected: false,
        key: ''
      },
      Sapling: {
        selected: false,
        key: ''
      },
      Copyleaks: {
        selected: false,
        key: '',
        additionalKey: {
          name: 'Scan ID',
          value: ''
        }
      },
    }
  })

  const detectorTable = computed(() => {
    return Object.entries(input.value.detectors).map(([detectorName, detectorDetails]) => {
      return {
        name: detectorName,
        ...detectorDetails
      }
    })
  })

  return {
    input,
    detectorTable
  }
})
