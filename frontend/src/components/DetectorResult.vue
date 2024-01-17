<template>
  <v-container class="result">
    <v-row no-gutters justify="center" class="pb-6">
      <v-col cols="auto" class="">
        <span class="text-h4 font-weight-black">{{ formattedName }}</span>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-6">
      <ResultTable :trueRates="result.trueRates!" />
    </v-row>
    <v-row no-gutters justify="center" class="pb-16">
        <v-img class="matrix" :src="(result.pngUrl!)"></v-img>
    </v-row>
    <v-row no-gutters justify="center" class="">
      <v-col cols="auto">
          <v-btn color="primary" size="x-large" rounded="lg" class="text-none"><span
                class="text-h6 font-weight-black pr-2">Download</span><font-awesome-icon class="text-h6"
                icon="fa-solid fa-download"></font-awesome-icon></v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup lang="ts">
import type { Folder, } from '@/assets/types';
import ResultTable from './ResultTable.vue';

const props = defineProps<{
  result: Folder
}>()

const formattedName = `${props.result.name[0] + props.result.name.slice(1).toLowerCase()}`

</script>
<style>
.matrix {
  border-radius: 16px;
  margin-right: 100px;
  margin-left: 100px;
}
</style>