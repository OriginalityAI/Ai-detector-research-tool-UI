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
        <v-row no-gutters class="px-12 pb-6" align="center">
          <v-file-input v-model="input.csv" :rules="fileInputRules" class="flex align-start" prepend-icon=""
            append-inner-icon="mdi-paperclip" hide-details="auto" rounded="lg" variant="solo" bg-color="#d4d4d4"
            accept=".csv"></v-file-input>
          <v-col cols="auto" class="pl-6">
            <v-btn color="secondary" rounded="large" class="text-none cool-btn-dark" @click="handleTest()"><span
                class="text-body-1 font-weight-black" @click="handleTest">Test</span></v-btn>
          </v-col>
        </v-row>
        <v-row no-gutters justify="space-evenly" class="px-4 pb-6">
          <v-col cols="auto">
            <DownloadDefaultVue />
          </v-col>
          <v-col cols="auto">
            <DownloadTemplateVue />
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
        <v-row no gutters justify="center" class="pb-12" align="center">
          <v-col cols="auto">
            <v-btn color="primary" size="x-large" rounded="lg" class="cool-btn-light text-none"
              @click="handleSubmit()"><span class=" text-h6 font-weight-black pr-2">Evaluate</span><font-awesome-icon
                class="text-h6" icon="fa-solid fa-wand-magic-sparkles"></font-awesome-icon></v-btn>
          </v-col>
        </v-row>
        <TestModal @start-test="handleModalEmit()" />
      </v-form>
    </v-sheet>
  </v-container>
</template>
<script setup lang="ts">
// Importing necessary libraries and components
import { useInputStore } from '@/stores/inputStore'
import { useResultsStore } from '@/stores/resultsStore'
import { storeToRefs } from 'pinia';
import DetectorInfo from './DetectorInfo.vue';
import Papa from 'papaparse'
import { ref } from 'vue';
import DownloadTemplateVue from './DownloadTemplate.vue';
import DownloadDefaultVue from './DownloadDefault.vue';

// Importing types
import type { DetectorItem, OtherResult, MainResults, PollResolve } from '@/assets/types';
import type { Ref } from 'vue';

// Importing utilities
import { formatDetectorPayload } from '@/utils/formatDetectorPayload';
import { loadZip } from '@/utils/loadZip'

// Importing constants
import { PENDING_MSG, BAD_RESULT_MSG, TEST_RESULT_MSG } from '@/assets/global'

// Importing Vue specific utilities
import { toRaw } from 'vue';
import { useModalStore } from '@/stores/modalStore';
import TestModal from './TestModal.vue';

// Initializing stores
const inputStore = useInputStore();
const resultsStore = useResultsStore()
const modalStore = useModalStore()

// Creating references to store properties
const { input } = storeToRefs(inputStore);
const { pending, errorResult, testResult, results } = storeToRefs(resultsStore);
const { modalTrigger } = storeToRefs(modalStore);

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

const handleModalEmit = () => {
  modalTrigger.value.fresh = false
  handleTest();
}

const testPoll = async (taskId: string): Promise<PollResolve> => {
  return new Promise((resolve) => {
    const chain = async () => {
      try {
        // const response = await fetch(`/api/results/${taskId}/`);
        const response = await fetch(`http://0.0.0.0:8000/api/results/${taskId}/`); // docker route
        let data;
        data = response.headers.get('Content-Type')?.endsWith('octet-stream') ? { blob: await response.blob() } : await response.json();
        if (data.blob) {
          let filename = ''
          if (response.headers.get('Content-Disposition')) {
            filename = response.headers.get('Content-Disposition')!.match(/filename=([^;]+)/)![1];
          }
          // Success state
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
            // Error with log 
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
            // Uncaught file response error
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
        } else if (data.status === 'running') {
          pending.value.msg = PENDING_MSG.testing;
          setTimeout(() => resolve(testPoll(taskId)), 5000);
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
        pending.value = {
          status: false,
          progress: null,
          msg: null
        }
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
        // const response = await fetch(`/api/results/${taskId}/`);
        const response = await fetch(`http://0.0.0.0:8000/api/results/${taskId}/`); // docker route
        let data;
        data = response.headers.get('Content-Type')?.endsWith('octet-stream') ? { blob: await response.blob() } : await response.json();
        if (data.blob) {
          let filename = ''
          if (response.headers.get('Content-Disposition')) {
            filename = response.headers.get('Content-Disposition')!.match(/filename=([^;]+)/)![1];
          }
          // output file received
          if (filename.startsWith('output')) {
            pending.value.msg = PENDING_MSG.completed;
            const folders = await loadZip(data.blob)
            if (folders) {
              // Success state
              if (folders.length) {
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
                // empty folders indicates bad api keys
              } else {
                const result = {
                  kind: 'Error',
                  content: {
                    status: true,
                    msg: BAD_RESULT_MSG.badKeys,
                    blob: null
                  }
                }
                pending.value.status = false
                pending.value.progress = null
                resolve(result)
              }
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
        } else if (data.status === 'running') {
          pending.value.msg = PENDING_MSG.running;
          pending.value.progress = Number(data.progress).toFixed(0);
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
        pending.value = {
          status: false,
          progress: null,
          msg: null
        }
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

const handleTest = async (): Promise<void> => {

  // validate input
  const valid = await form.value!.validate()

  if (valid.valid) {
    modalTrigger.value.fresh = false;
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
      // const response = await fetch("/api/analyze/", testReqOptions)
      const response = await fetch("http://0.0.0.0:8000/api/analyze/", testReqOptions) // docker route
      const testData = await response.json()

      // If test passes, present results for download, else present appropriate error
      const result = await testPoll(testData.task_id);
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
    if (modalTrigger.value.fresh) {
      modalTrigger.value = {
        open: true,
        fresh: false
      }
      return
    }
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
      // const response = await fetch("/api/analyze/", requestOptions)
      const response = await fetch("http://0.0.0.0:8000/api/analyze/", requestOptions) // docker route
      const data = await response.json()
      const result = await poll(data.task_id)
      result?.kind === "Results" ? results.value = result.content as MainResults : errorResult.value = result.content as OtherResult
    } catch (err) {
      console.error('Error during main fetch', err);
    }
  }
}

</script>
<style></style>