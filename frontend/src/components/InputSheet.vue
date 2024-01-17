<template>
  <v-container class="pt-0 px-0 pb-16">
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
          <v-file-input v-model="input.csv" class="flex align-start" prepend-icon="" append-inner-icon="mdi-paperclip"
            hide-details="auto" rounded="lg" variant="solo" bg-color="#d4d4d4" accept=".csv"></v-file-input>
        </v-row>
        <v-row no-gutters justify="space-evenly" class="px-4 pb-6">
          <v-col cols="auto">
            <v-btn class="text-none font-weight-black text-h6" size="large" color="secondary" rounded="pill">
              <span class="pr-2">Download Default</span><font-awesome-icon
                icon="fa-solid fa-download"></font-awesome-icon>
            </v-btn>
          </v-col>
          <v-col cols="auto">
            <v-btn class="text-none font-weight-black text-h6" size="large" color="secondary" rounded="pill"
              @click="downloadTemplate">
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
            <v-btn color="primary" size="x-large" rounded="lg" class="text-none" @click="handleSubmit(input)"><span
                class="text-h6 font-weight-black pr-2">Evaluate</span><font-awesome-icon class="text-h6"
                icon="fa-solid fa-wand-magic-sparkles"></font-awesome-icon></v-btn>
          </v-col>
        </v-row>
        <v-row no gutters justify="center" class="pb-12">
          <v-col cols="auto">
            <v-btn color="primary" size="x-large" rounded="lg" class="text-none" @click="probe(input)"><span
                class="text-h6 font-weight-black pr-2">Probe</span><font-awesome-icon class="text-h6"
                icon="fa-solid fa-wand-magic-sparkles"></font-awesome-icon></v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-sheet>
  </v-container>
</template>
<script setup lang="ts">
import { useInputStore } from '@/stores/inputStore'
import { useResultsStore } from '@/stores/resultsStore'
import { storeToRefs } from 'pinia';
import DetectorInfo from './DetectorInfo.vue';
import type { DetectorItem, UserInput } from '@/assets/types';
import { formatDetectorPayload } from '@/utils/formatDetectorPayload';
import { loadZip } from '@/utils/loadZip'
import { PENDING_MSG } from '@/assets/global'
import { nextTick } from 'vue';
import { toRaw } from 'vue';

const inputStore = useInputStore();
const resultsStore = useResultsStore()

const { input } = storeToRefs(inputStore);
const { pending, zipBlob } = storeToRefs(resultsStore);

const handleUpdate = (name: string, updatedItem: DetectorItem) => {
  input.value.detectors[name] = updatedItem
}

const poll = async (taskId: string) => {
  try {
    const response = await fetch(`/api/results/${taskId}/`);
    // const response = await fetch(`http://0.0.0.0:8000/results/${taskId}/`); // docker route
    let data;
    data = response.headers.get('Content-Type')?.endsWith('octet-stream') ? { blob: await response.blob() } : await response.json();
    console.log('headers', response.headers.get('Content-Type'))
    console.log('data', data)
    // running state
    if (data[taskId] === 'running') {
      console.log(PENDING_MSG.running);
      pending.value.msg = PENDING_MSG.running;
      setTimeout(() => poll(taskId), 30000);
    // success state
    } else if (data.blob) {
      console.log(PENDING_MSG.completed);
      pending.value.msg = PENDING_MSG.completed;
      zipBlob.value = data.blob
      const unzipped = await loadZip(data.blob)
      if (unzipped) {
        nextTick(() => pending.value.status = false)
        resultsStore.updateResults(unzipped)
      }
    // fail state
    } else if (data.status === 'failed') {
      console.log(PENDING_MSG.failed);
      pending.value.msg = PENDING_MSG.failed;
      nextTick(() => pending.value.status = false)
    // error state
    } else if (data.error) {
      nextTick(() => pending.value.status = false)
      pending.value.msg = `${data.error}`;
      console.error(`Error from server: ${data.error}`);
    }
    // } else {
    //   nextTick(() => pending.value.status = false)
    //   pending.value.msg = `${data.error}`;
    //   console.error('Unrecognized response status, stopping polling.');
    // }
  } catch (error) {
    // If there's a network or server error, log the error and retry after 30 seconds
    console.error('An error occurred while polling:', error);
    console.log('Retrying in 30 seconds...');
    setTimeout(() => poll(taskId), 30000);
  }
}

const handleSubmit = async (input: UserInput): Promise<void> => {
  if (input.csv) {
    const detectorPayload = formatDetectorPayload(input);
    const rawFile = toRaw(input.csv[0])
    const formdata = new FormData();
    formdata.append("csvFile", rawFile, input.csv[0].name);
    formdata.append("api_keys", JSON.stringify(detectorPayload));
    const requestOptions: RequestInit = {
      method: 'POST',
      body: formdata,
      redirect: 'follow'
    };
    try {
      const response = await fetch("/api/analyze/", requestOptions)
      // const response = await fetch("http://0.0.0.0:8000/analyze/", requestOptions) // docker route
      const data = await response.json()
      console.log(data)
      pending.value.status = true;
      poll(data.task_id)
    } catch (err) {
      console.error('Error during fetch', err);
    }
  }
}

const downloadTemplate = async () => {
  const headers = ["text", "dataset", "label"]
  let csvContent = "data:text/csv;charset=utf-8," + headers.join(",");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "detector_tool_template.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const probe = async (input: UserInput) => {
  console.log(input)
}

</script>
<style></style>