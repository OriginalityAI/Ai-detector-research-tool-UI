<template>
  <v-dialog class="test-modal" v-model="modalTrigger.open">
    <v-card v-if="modalTrigger" class="glass-dark" rounded="xl">
      <font-awesome-icon class="lightbulb text-h2 font-weight-bold pt-6" icon="fa-solid fa-lightbulb"/>
      <v-card-text>
        <p class="text-body-1 text-center font-weight-bold">
          We recommend testing your CSV before evaluating to check whether your CSV is properly formatted,
          and whether the APIs for the detectors you would like to test are responding correctly.<br><br>
          The test button will run a short analysis on a sample of the data in your CSV to evaluate it,
          but be sure to check the error columns of the output.csv file for each detector in the test analysis folder to
          verify individual APIs.
        </p>
      </v-card-text>
      <v-row no-gutters align="center" justify="center" class="pt-4 pb-8">
        <v-col cols="auto">
          <v-btn color="secondary" size="x-large" rounded="lg" class="text-none cool-btn-dark" @click="emitTest">
            <span class="text-h6 font-weight-black">Test</span>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useModalStore } from '@/stores/modalStore'
import { storeToRefs } from 'pinia';

const modalStore = useModalStore()
const { modalTrigger } = storeToRefs(modalStore)

const emit = defineEmits(['start-test'])

const emitTest = () => {
  modalTrigger.value = {
    open: false,
    fresh: false
  }
  emit('start-test');
};

</script>

<style lang="css">
.test-modal {
  width: 600px;
  border-radius: 16px;
}

.lightbulb {
  color: #FFBB59;
}
</style>