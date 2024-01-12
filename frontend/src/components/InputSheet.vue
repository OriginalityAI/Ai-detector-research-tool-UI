<template>
  <v-container class="pa-0">
    <v-sheet color="#fafafa" class="sheet">
      <v-form @submit.prevent="handleSubmit(input)">
        <v-row no-gutters align="center" class="pt-6 px-6 pb-6">
          <v-col cols="auto">
            <span class="text-h4 text-grey font-weight-bold">Data</span>
          </v-col>
          <v-col>
            <v-divider thickness="2" class="ml-4 mr-2"></v-divider>
          </v-col>
        </v-row>
        <v-row no-gutters class="px-12 pb-6">
          <v-file-input v-model="input.csv" class="flex align-start" prepend-icon=""
            append-inner-icon="mdi-paperclip" hide-details="auto" rounded="lg" variant="solo" bg-color="#d4d4d4"
            accept=".csv"></v-file-input>
        </v-row>
        <v-row no-gutters justify="space-evenly" class="px-4 pb-6">
          <v-col cols="auto">
            <v-btn class="text-none font-weight-black text-h6" size="large" color="secondary" rounded="pill">
              <span class="pr-2">Download Default</span><font-awesome-icon
                icon="fa-solid fa-download"></font-awesome-icon>
            </v-btn>
          </v-col>
          <v-col cols="auto">
            <v-btn class="text-none font-weight-black text-h6" size="large" color="secondary" rounded="pill">
              <span class="pr-2">Download Template</span><font-awesome-icon
                icon="fa-solid fa-download"></font-awesome-icon>
            </v-btn>
          </v-col>
        </v-row>
        <v-row no-gutters align="center" class="px-6 pb-6">
          <v-col cols="auto">
            <span class="text-h4 text-grey font-weight-bold">Detectors</span>
          </v-col>
          <v-col>
            <v-divider thickness="2" class="ml-4 mr-2"></v-divider>
          </v-col>
        </v-row>
        <DetectorInfo v-for="(item) in inputStore.detectorTable" :key="item.name" :item="item"
          @update-item="handleUpdate(item.name, $event)" />
        <v-row no gutters class="px-6 pb-6">
          <v-col>
            <v-divider thickness="2" class="ml-4 mr-2"></v-divider>
          </v-col>
        </v-row>
        <v-row no gutters justify="center" class="pb-12">
          <v-col cols="auto">
            <v-btn color="primary" size="x-large" rounded="lg" class="text-none"><span
                class="text-h6 font-weight-black pr-2">Evaluate</span><font-awesome-icon class="text-h6"
                icon="fa-solid fa-wand-magic-sparkles"></font-awesome-icon></v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-sheet>
  </v-container>
</template>
<script setup lang="ts">
import { useInputStore } from '@/stores/inputStore'
import { storeToRefs } from 'pinia';
import DetectorInfo from './DetectorInfo.vue';
import type { DetectorItem, UserInput } from '@/assets/types';
import { formatDetectorPayload } from '@/utils/formatDetectorPayload';

const inputStore = useInputStore();

const { input } = storeToRefs(inputStore);
const { detectors } = input.value;

const handleUpdate = (name: string, updatedItem: DetectorItem) => {
  input.value.detectors[name] = updatedItem
}

const handleSubmit = async (input: UserInput): Promise<void> => {
  if (input.csv) {
    const detectorPayload = formatDetectorPayload(input);
    const formdata = new FormData();
    formdata.append("csvFile", input.csv[0], input.csv[0].name);
    formdata.append("api_keys", JSON.stringify(detectorPayload));
    const requestOptions: RequestInit = {
      method: 'POST',
      body: formdata,
      redirect: 'follow'
    };
    try {
      const response = await fetch("http://127.0.0.1:8000/analyze/", requestOptions)
      const result = await response.text()
      console.log(result)
    } catch (err) {
      console.error('Error during fetch', err);
    }
  }
}

</script>
<style></style>