<template>
  <v-container class="px-0 pb-12">
    <!-- <v-row no-gutters justify="center" class="pb-12">
      <v-col cols="auto">
        <v-btn class="text-black" size="x-large" @click="handleUnzip">Unzip</v-btn>
      </v-col>
    </v-row> -->
    <v-sheet color="#f5f5f5" class="results-sheet sheet d-flex-col">
      <v-row no-gutters align="center" justify="space-between" class="px-8 py-6">
        <v-col cols="auto" class="d-flex align-center">
          <v-col cols="auto" class="pa-0 ma-0">
            <v-select v-model="orderBy.selected" :items="orderBy.options" variant="outlined" density="compact"
              hide-details></v-select>
          </v-col>
          <v-col cols="auto" class="pa-0 ma-0">
            <v-btn icon flat :ripple="false" class="order-direction" @click="resultStore.toggleDirection">
              <font-awesome-icon v-if="orderBy.descending" class="text-h6"
                icon="fa-solid fa-arrow-down"></font-awesome-icon>
              <font-awesome-icon v-else class="text-h6" icon="fa-solid fa-arrow-up"></font-awesome-icon>
            </v-btn>
          </v-col>
        </v-col>
        <v-col>
          <v-divider thickness="2" class="mr-4"></v-divider>
        </v-col>
        <v-col cols="auto">
          <span class="text-h4 text-grey font-weight-bold">Results</span>
        </v-col>
        <v-col>
          <v-divider thickness="2" class="mx-4"></v-divider>
        </v-col>
        <v-col cols="auto">
          <v-btn class="text-none font-weight-black text-body-1" color="secondary" rounded="pill"
            @click="handleDownloadAll">
            <span class="pr-2">Download All</span><font-awesome-icon icon="fa-solid fa-download"></font-awesome-icon>
          </v-btn>
        </v-col>
      </v-row>
      <v-row no-gutters v-if="!pending.status && !results.length" justify="center" class="brain">
        <v-col cols="auto">
          <OriginalitySVG />
        </v-col>
      </v-row>
      <div v-if="pending.status">
        <v-row no-gutters justify="center" class="brain">
          <v-col cols="auto">
            <v-progress-circular indeterminate color="secondary" :width="14" :size="265"></v-progress-circular>
          </v-col>
        </v-row>
        <v-row no-gutters justify="center" class="pt-8">
          <v-col cols="auto">
            <span class="text-h6 font-weight-black">{{ pending.msg }}</span>
          </v-col>
        </v-row>
        <v-row v-if="pending.progress" no-gutters justify="center" class="pt-6">
          <v-col cols="auto">
            <span class="text-h6 font-weight-black">{{ `Progress: ${pending.progress}%`}}</span>
          </v-col>
        </v-row>
      </div>
      <div v-else-if="errorResult.status">
        <v-row no-gutters justify="center" class="pt-6">
          <v-col cols="auto">
            <span class="text-h4 font-weight-black">Error</span>
          </v-col>
        </v-row>
        <v-row v-if="errorResult.blob" no-gutters justify="center" class="pt-6">
          <v-col cols="auto">
            <v-btn color="primary" size="x-large" rounded="lg" class="text-none" @click="handleDownloadLog"><span
                  class="text-h6 font-weight-black pr-2">Download Log</span></v-btn>
          </v-col>
        </v-row>
      </div>
      <v-row v-else v-for="folder in resultStore.feed" :key="folder.name" no-gutters class="pb-12">
        <DetectorResult :result="folder" />
      </v-row>
    </v-sheet>
  </v-container>
</template>

<script setup lang="ts">
import DetectorResult from './DetectorResult.vue';
import OriginalitySVG from './OriginalitySVG.vue';
import { useResultsStore } from '@/stores/resultsStore'
import { storeToRefs } from 'pinia';
// import { loadZip } from '@/utils/loadZip'

const resultStore = useResultsStore()
const { orderBy, zipBlob, pending, results, errorResult } = storeToRefs(resultStore)

const handleDownloadAll = () => {
  if (zipBlob.value) {
    const url = window.URL.createObjectURL(zipBlob.value);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'output.zip';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  } else {
    console.error('No file is available for download.');
  }
}

const handleDownloadLog = () => {
  if (errorResult.value.blob) {
    const url = window.URL.createObjectURL(errorResult.value.blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'output.zip';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  } else {
    console.error('No file is available for download.');
  }
}

// const handleUnzip = async () => {
//   const unzipped = await loadZip()
//   if (unzipped) {
//     resultStore.updateResults(unzipped)
//   }
// }

</script>
<style>
.order-direction {
  margin: 0px;
  padding: 0px;
  background-color: inherit;
}

.results-sheet {
  min-height: 600px;
}
.brain {
  padding-top: 70px;
}
</style>