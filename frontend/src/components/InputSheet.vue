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
        <v-row no gutters justify="space-between" class="pb-12 px-16" align="center">
          <v-col cols="auto" class="invisible">
            <v-btn color="secondary" size="x-large" icon rounded="pill" class="text-none"></v-btn>
          </v-col>

          <v-col cols="auto">
            <v-btn color="primary" size="x-large" rounded="lg" class="text-none" @click="handleSubmit()"><span
                class="text-h6 font-weight-black pr-2">Evaluate</span><font-awesome-icon class="text-h6"
                icon="fa-solid fa-wand-magic-sparkles"></font-awesome-icon></v-btn>
          </v-col>

          <v-col cols="auto">

            <v-btn color="secondary" size="x-large" icon rounded="pill" class="text-none" @click="handleTest()"><span
                class="text-h6 font-weight-black" @click="handleTest">Test</span></v-btn>
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
import type { DetectorItem, OtherResult, MainResults, PollResolve } from '@/assets/types';
import { formatDetectorPayload } from '@/utils/formatDetectorPayload';
import { loadZip } from '@/utils/loadZip'
import { PENDING_MSG, BAD_RESULT_MSG, TEST_RESULT_MSG } from '@/assets/global'
import { toRaw } from 'vue';
import { ref } from 'vue';
import type { Ref } from 'vue';

import Papa from 'papaparse'

const inputStore = useInputStore();
const resultsStore = useResultsStore()

const { input } = storeToRefs(inputStore);
const { pending, errorResult, testResult, results } = storeToRefs(resultsStore);

const form: Ref<HTMLFormElement | null> = ref(null);

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

const testPoll = async (taskId: string): Promise<PollResolve> => {
  return new Promise((resolve) => {
    const chain = async () => {
      try {
        const response = await fetch(`/api/results/${taskId}/`);
        // const response = await fetch(`http://0.0.0.0:8000/results/${taskId}/`); // docker route
        let data;
        data = response.headers.get('Content-Type')?.endsWith('octet-stream') ? { blob: await response.blob() } : await response.json();
        console.log('headers', response.headers.get('Content-Type'))
        console.log('data', data)
        if (data.blob) {
          let filename = ''
          if (response.headers.get('Content-Disposition')) {
            filename = response.headers.get('Content-Disposition')!.match(/filename=([^;]+)/)![1];
          }
          if (filename.startsWith('output')) {
            const result = {
              kind: 'Test',
              content: {
                status: true,
                msg: TEST_RESULT_MSG.pass,
                blob: data.blob
              }
            }
            pending.value.status = false;
            resolve(result);
          } else if (filename.startsWith('error_log')) {
            const result = {
              kind: 'Error',
              content: {
                status: true,
                msg: BAD_RESULT_MSG.testFailed,
                blob: data.blob
              }
            }
            pending.value.status = false;
            resolve(result);
          } else {
            console.error('An unknown error occured on file response.')
            const result = {
              kind: 'Error',
              content: {
                status: true,
                msg: BAD_RESULT_MSG.unknown,
                blob: null
              }
            }
            pending.value.status = false;
            resolve(result);
          }
        } else if (data[taskId].status === 'running') {
          pending.value.msg = PENDING_MSG.testing;
          setTimeout(() => resolve(testPoll(taskId)), 5000);
        } else if (data.error) {
          if (data.error === 'No error log found') {
            console.error('An unknown error occured but no error log was found.')
            const result = {
              kind: 'Error',
              content: {
                status: true,
                msg: BAD_RESULT_MSG.loglessError,
                blob: null
              }
            }
            pending.value.status = false;
            resolve(result);
          }
        } else if (data.error === 'No results found') {
          console.error('No results found.')
          const result = {
            kind: 'Error',
            content: {
              status: true,
              msg: BAD_RESULT_MSG.noResults,
              blob: null
            }
          }
          pending.value.status = false;
          resolve(result);
        } else {
          console.error('An unknown error occured.')
          const result = {
            kind: 'Error',
            content: {
              status: true,
              msg: BAD_RESULT_MSG.unknown,
              blob: null
            }
          }
          pending.value.status = false;
          resolve(result);
        }
      } catch (error) {
        console.error('An error occurred while polling:', error);
      }
    };
    chain(); // Initiate promise chain
  });
};

const poll = async (taskId: string): Promise<PollResolve> => {
  return new Promise((resolve) => {
    const chain = async () => {
      try {
        const response = await fetch(`/api/results/${taskId}/`);
        // const response = await fetch(`http://0.0.0.0:8000/results/${taskId}/`); // docker route
        let data;
        data = response.headers.get('Content-Type')?.endsWith('octet-stream') ? { blob: await response.blob() } : await response.json();
        console.log('headers', response.headers.get('Content-Type'))
        console.log('data', data)
        if (data.blob) {
          let filename = ''
          if (response.headers.get('Content-Disposition')) {
            filename = response.headers.get('Content-Disposition')!.match(/filename=([^;]+)/)![1];
          }
          // Success state
          if (filename.startsWith('output')) {
            pending.value.msg = PENDING_MSG.completed;
            const folders = await loadZip(data.blob)
            if (folders) {
              const result = {
                kind: 'Results',
                content: {
                  folders,
                  blob: data.blob
                }
              }
              pending.value.status = false
              pending.value.progress = null
              resolve(result)
            } else {
              const result = {
                kind: 'Error',
                content: {
                  status: true,
                  msg: BAD_RESULT_MSG.zipFailure,
                  blob: null
                }

              }
              pending.value.status = false
              pending.value.progress = null
              resolve(result)
            }
            // Logged error state
          } else if (filename.startsWith('error_log')) {
            const result = {
              kind: 'Error',
              content: {
                status: true,
                msg: BAD_RESULT_MSG.analysisFailed,
                blob: data.blob
              }

            }
            pending.value.status = false;
            resolve(result);
            // Unknown file error state
          } else {
            console.error('An unknown error occured on file response.')
            const result = {
              kind: 'Error',
              content: {
                status: true,
                msg: BAD_RESULT_MSG.unknown,
                blob: null
              }

            }
            pending.value.status = false;
            resolve(result);
          }

          // Running state
        } else if (data[taskId].status === 'running') {
          console.log(PENDING_MSG.running);
          pending.value.msg = PENDING_MSG.running;
          pending.value.progress = Number(data[taskId].progress).toFixed(0);
          setTimeout(() => resolve(poll(taskId)), 5000);

          // Logless error states
        } else if (data.error) {
          if (data.error === 'No error log found') {
            console.error('An unknown error occured but no error log was found.')
            const result = {
              kind: 'Error',
              content: {
                status: true,
                msg: BAD_RESULT_MSG.loglessError,
                blob: null
              }
            }
            pending.value.status = false;
            resolve(result);
          }
        } else if (data.error === 'No results found') {
          console.error('No results found.')
          const result = {
            kind: 'Error',
            content: {
              status: true,
              msg: BAD_RESULT_MSG.noResults,
              blob: null
            }
          }
          pending.value.status = false;
          resolve(result);
        } else {
          console.error('An unknown error occured.')
          const result = {
            kind: 'Error',
            content: {
              status: true,
              msg: BAD_RESULT_MSG.unknown,
              blob: null
            }
          }
          pending.value.status = false;
          resolve(result);
        }

      } catch (error) {
        // If there's a network or server error, log the error and retry after 30 seconds
        console.error('An error occurred while polling:', error);
      }
    }
    chain(); // Initiate promise chain
  })
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
      error: function (err) {
        reject(err);
      }
    })
  })
}

const scrollToResults = () => {
  var element = document.getElementById('results-container');
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
  }
}

// Call this function with the ID of the element you want to scroll to

const handleTest = async (): Promise<void> => {
  
  // validate input
  const valid = await form.value!.validate()
  
  if (valid.valid) {
    // reset error state
    resultsStore.resetAll()
    
    scrollToResults();

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

      // If test passes, present results for download, else present appropriate error
      const result = await testPoll(testData.task_id);
      console.log(result)
      result?.kind === 'Test' ? testResult.value = result.content as OtherResult : errorResult.value = result.content as OtherResult
    } catch (err) {
      console.error('Error during test fetch', err);
    }
  }
}

const handleSubmit = async (): Promise<void> => {
  // validate input
  const valid = await form.value!.validate()
  if (valid.valid) {
    
    // reset error state
    resultsStore.resetAll()

    scrollToResults();

    // format input values for payload
    const detectorPayload = formatDetectorPayload(input.value);
    const rawFile = toRaw(input.value.csv![0])
    const formdata = new FormData();

    formdata.append("csvFile", rawFile, input.value.csv![0].name);
    formdata.append("api_keys", JSON.stringify(detectorPayload));

    const requestOptions: RequestInit = {
      method: 'POST',
      body: formdata,
      redirect: 'follow'
    };

    try {
      pending.value.status = true;
      const response = await fetch("/api/analyze/", requestOptions)
      // const response = await fetch("http://0.0.0.0:8000/analyze/", requestOptions) // docker route
      const data = await response.json()
      console.log(data)
      const result = await poll(data.task_id)
      console.log(result)
      result?.kind === "Results" ? results.value = result.content as MainResults : errorResult.value = result.content as OtherResult
    } catch (err) {
      console.error('Error during main fetch', err);
    }
  }
}

</script>
<style></style>