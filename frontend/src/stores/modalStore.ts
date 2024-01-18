import { ref } from 'vue'
import type { Ref } from 'vue'
import { defineStore } from 'pinia'
import type { ModalTrigger } from '@/assets/types'

export const useModalStore = defineStore('modalStore', () => {
  const modalTrigger: Ref<ModalTrigger> = ref({
    open: false,
    fresh: true
  })

  return {
    modalTrigger
  }
})