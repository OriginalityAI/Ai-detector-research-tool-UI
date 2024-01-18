<template>
  <v-container class="pt-0 px-0 pb-16">
    <v-sheet color="#fafafa" class="sheet">
      <v-form ref="form" validate-on="submit lazy" @submit.prevent="handleSubmit">
        <v-row no-gutters align="center" class="pt-6 px-6 pb-6">
          <v-col cols="auto">
            <span class="text-h4 text-grey font-weight-bold">Data</span>
          </v-col>
          <v-col>
            <v-divider thickness="2" class="ml-4 mr-2"></v-divider>
          </v-col>
        </v-row>
        <v-row no-gutters class="px-12 pb-6">
          <v-file-input v-model="input.csv" :rules="fileInputRules" class="flex align-start" prepend-icon=""
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
            <v-btn color="primary" size="x-large" rounded="lg" class="text-none" @click="handleSubmit()"><span
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
import { PENDING_MSG, BAD_RESULT_MSG } from '@/assets/global'
import { nextTick } from 'vue';
import { toRaw } from 'vue';
import { ref } from 'vue';
import type { Ref } from 'vue';
import Papa from 'papaparse'

const inputStore = useInputStore();
const resultsStore = useResultsStore()

const { input } = storeToRefs(inputStore);
const { pending, zipBlob, errorResult } = storeToRefs(resultsStore);

const form: Ref<any> = ref(null);

type ValidationRule = (v: File[]) => string | boolean

const fileInputRules: ValidationRule[] = [
  (v: File[]) => {
    if (!v || !v.length) {
      return 'Please upload a CSV file to be tested.'
    }
    return true
  }
]

const handleUpdate = (name: string, updatedItem: DetectorItem) => {
  input.value.detectors[name] = updatedItem
}

const testPoll = async (taskId: string): Promise<boolean | undefined> => {
  try {
    const response = await fetch(`/api/results/${taskId}/`);
    // const response = await fetch(`http://0.0.0.0:8000/results/${taskId}/`); // docker route
    let data;
    data = response.headers.get('Content-Type')?.endsWith('octet-stream') ? { blob: await response.blob() } : await response.json();
    console.log('headers', response.headers.get('Content-Type'))
    console.log('data', data)
    if (data.blob) {
      response.headers.forEach((value, name) => {
        console.log(`${name}: ${value}`);
      });
      console.log("content disposition", response.headers.keys(), response.headers.values())
      console.log("content disposition", response.headers.get('Content-Disposition'))
      let filename = ''
      if (response.headers.get('Content-Disposition')) {
        // console.log('regexed', response.headers.get('Content-Disposition')!.match(/filename=([^;]+)/), typeof response.headers.get('Content-Disposition')!.match(/filename=([^;]+)/)[1]);
        filename = response.headers.get('Content-Disposition')!.match(/filename=([^;]+)/)![1];
      }
      // Success state
      if (filename.startsWith('output')) {
        return true

        // Logged error state
      } else if (filename.startsWith('error_log')) {
        errorResult.value.msg = BAD_RESULT_MSG.testFailed;
        errorResult.value.blob = data.blob
        errorResult.value.status = true;
        pending.value.status = false;
        return false

        // Unknown file error state
      } else {
        console.error('An unknown error occured on file response.')
        errorResult.value.msg = BAD_RESULT_MSG.unknown;
        errorResult.value.status = true;
        pending.value.status = false;
        return false
      }

      // Running state
    } else if (data[taskId].status === 'running') {
      pending.value.msg = PENDING_MSG.testing;
      setTimeout(() => testPoll(taskId), 5000);

      // Logless error states
    } else if (data.error) {
      if (data.error === 'No error log found') {
        errorResult.value.msg = BAD_RESULT_MSG.loglessError;
        errorResult.value.status = true;
        pending.value.status = false;
        return false
      } else if (data.error === 'No results found') {
        errorResult.value.msg = BAD_RESULT_MSG.noResults;
        errorResult.value.status = true;
        pending.value.status = false;
        return false
      } else {
        errorResult.value.msg = BAD_RESULT_MSG.unknown;
        errorResult.value.status = true;
        pending.value.status = false;
        return false
      }
    }
  } catch (error) {
    // If there's a network or server error, log the error and retry after 30 seconds
    console.error('An error occurred while polling:', error);
    console.log('Retrying in 30 seconds...');
    setTimeout(() => poll(taskId), 30000);
  }
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
    if (data.blob) {
      const filename = response.headers.get('Content-Disposition')!.match(/filename="([^"]+)"/)![0];
      // Success state
      if (filename.startsWith('output')) {
        pending.value.msg = PENDING_MSG.completed;
        pending.value.progress = null
        zipBlob.value = data.blob
        const unzipped = await loadZip(data.blob)
        if (unzipped) {
          resultsStore.updateResults(unzipped)
        }
        pending.value.status = false

        // Logged error state
      } else if (filename.startsWith('error_log')) {
        errorResult.value.msg = BAD_RESULT_MSG.testFailed;
        errorResult.value.blob = data.blob
        errorResult.value.status = true;
        pending.value.status = false;

        // Unknown file error state
      } else {
        console.error('An unknown error occured on file response.')
        errorResult.value.msg = BAD_RESULT_MSG.unknown;
        errorResult.value.status = true;
        pending.value.status = false;
      }

      // Running state
    } else if (data[taskId].status === 'running') {
      console.log(PENDING_MSG.running);
      pending.value.msg = PENDING_MSG.running;
      pending.value.progress = Number(data[taskId].progress).toFixed(0);
      setTimeout(() => poll(taskId), 5000);

      // Logless error states
    } else if (data.error) {
      if (data.error === 'No error log found') {
        errorResult.value.msg = BAD_RESULT_MSG.loglessError;
        errorResult.value.status = true;
        pending.value.status = false;
        return false
      } else if (data.error === 'No results found') {
        errorResult.value.msg = BAD_RESULT_MSG.noResults;
        errorResult.value.status = true;
        pending.value.status = false;
        return false
      } else {
        errorResult.value.msg = BAD_RESULT_MSG.unknown;
        errorResult.value.status = true;
        pending.value.status = false;
        return false
      }
    }

  } catch (error) {
    // If there's a network or server error, log the error and retry after 30 seconds
    console.error('An error occurred while polling:', error);
  }
}

const createTestCsv = (file: File): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      complete: function (results) {
        // Assuming the first row is headers
        const rows = results.data.slice(0, 5);
        const csvContent = Papa.unparse(rows);
        const blob = new Blob([csvContent], { type: 'text/csv' });
        // Create a link and set its href to the object URL created from the blob
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'test.csv'; // Specify the file name for download

        // Append the link to the document, trigger a click, and then remove it
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up the object URL
        URL.revokeObjectURL(url);
        resolve(blob);
      },
      error: function(err) {
        reject(err);
      }
    })
  })
}

const handleSubmit = async (): Promise<void> => {
  // validate input
  const valid = await form.value!.validate()

  if (valid.valid) {
    // reset error state
    resultsStore.resetErrorResult()

    // format input values for payload
    const detectorPayload = formatDetectorPayload(input.value);
    const rawFile = toRaw(input.value.csv![0])

    // test a small sample from the input csv to check wellf-formedness, API endpoints, etc.
    const testCsv = await createTestCsv(rawFile)
    const testForm = new FormData();
    testForm.append("csvFile", testCsv, input.value.csv![0].name);
    testForm.append("api_keys", JSON.stringify(detectorPayload));
    const testReqOptions: RequestInit = {
      method: 'POST',
      body: testForm,
      redirect: 'follow'
    };
    try {
      pending.value.status = true;
      const response = await fetch("/api/analyze/", testReqOptions)
      // const response = await fetch("http://0.0.0.0:8000/analyze/", testReqOptions) // docker route
      const testData = await response.json()
      console.log('testData', testData)

      // if the test passes proceed to main poll with full input csv
      if (await testPoll(testData.task_id)) {
        const formdata = new FormData();
        formdata.append("csvFile", rawFile, input.value.csv![0].name);
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
          poll(data.task_id)
        } catch (err) {
          console.error('Error during main fetch', err);
        }
      }
    } catch (err) {
      console.error('Error during test fetch', err);
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