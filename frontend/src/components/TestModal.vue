<template>
  <v-dialog class="metrics-modal" v-model="modalTrigger.open">
    <v-card v-if="modalTrigger">
      <v-toolbar color="white" elevation="0" class="d-flex justify-center">
        <v-toolbar-title><font-awesome-icon class="text-h4 font-weight-bold"
            icon="fa-solid fa-lightbulb" /></v-toolbar-title>
        <v-btn elevation="0" icon color="grey" @click="modalTrigger.open = false"><v-icon>mdi-close</v-icon></v-btn>
      </v-toolbar>
      <v-card-text>
        <p class="test-h6 font-weight-bold">
          We recommend testing your CSV before evaluating to check whether your CSV is properly formatted,
          and whether the APIs for the detectors you would like to test are responding correctly.
          The test button will run a short analysis on a sample of the data in your csv to evaluate it,
          but be sure to check the error columns of the output.csv file for each detector in the test analysis folder to
          verify individual APIs.
        </p>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useModalStore } from '@/stores/modalStore'
import { storeToRefs } from 'pinia';

const modalStore = useModalStore()
const { modalTrigger } = storeToRefs(modalStore)

</script>

<style lang="css"></style>