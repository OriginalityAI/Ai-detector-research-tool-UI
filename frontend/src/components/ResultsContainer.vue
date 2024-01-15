<template>
  <v-container class="px-0 pb-12">
    <v-row no-gutters justify="center" class="pb-12">
      <v-col cols="auto">
        <v-btn class="text-black" size="x-large" @click="handleUnzip">Unzip</v-btn>
      </v-col>
    </v-row>
    <v-sheet color="#f5f5f5" class="sheet">
      <!-- <v-row no-gutters>
        <v-col v-for="folder in folders" :key="folder.name">
          <v-card>
            <v-card-title>{{ folder.name }}</v-card-title>
            <v-card-text>
              {{ folder.txt }}
            </v-card-text>
            <v-card-text>
              {{ folder.csv }}
            </v-card-text>
            <v-img :src="(folder.pngUrl as string)"></v-img>
          </v-card>
        </v-col>
      </v-row>  -->
      <v-row no-gutters align="center" justify="space-between" class="px-8 py-6">
        <v-col cols="auto" class="d-flex align-center">
          <v-col cols="auto" class="pa-0 ma-0">
            <v-select v-model="orderBy.selected" :items="orderBy.options" variant="outlined" density="compact"
              hide-details></v-select>
          </v-col>
          <v-col cols="auto" class="pa-0 ma-0">
            <v-btn icon flat :ripple="false" class="order-direction" @click="resultStore.toggleDirection">
              <font-awesome-icon v-if="orderBy.descending" class="text-h6" icon="fa-solid fa-arrow-down"></font-awesome-icon>
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
          <v-btn class="text-none font-weight-black text-body-1" color="secondary" rounded="pill">
            <span class="pr-2">Download All</span><font-awesome-icon icon="fa-solid fa-download"></font-awesome-icon>
          </v-btn>
        </v-col>
      </v-row>
      <v-row v-for="folder in resultStore.feed" :key="folder.name" no-gutters class="pb-12">
        <DetectorResult :result="folder" />
      </v-row>
    </v-sheet>
  </v-container>
</template>

<script setup lang="ts">
import DetectorResult from './DetectorResult.vue';
import type { Ref } from 'vue';
import { ref } from 'vue';
import type { Folder, zFolders, TrueRates } from '@/assets/types'
import JSZip from 'jszip';
import { useResultsStore } from '@/stores/resultsStore'
import { storeToRefs } from 'pinia';

const folders: Ref<Folder[]> = ref([]);

const resultStore = useResultsStore()
const { results, orderBy } = storeToRefs(resultStore)

const loadZip = async () => {
try {
  const response = await fetch('/test_output.zip');
    const blob = await response.blob();
    console.log(blob)
    const zip = await new JSZip().loadAsync(blob);

    const zFolders: zFolders = {};

    // Iterate through each file
    for (const [relativePath, file] of Object.entries(zip.files)) {
      if (file.dir) continue;

      // Extract folder name and file name
      const folderName = relativePath.split('/')[0];
      const fileName = relativePath.split('/').pop();

      // Initialize the folder object if it doesn't exist
      if (!zFolders[folderName]) {
        zFolders[folderName] = { name: folderName, trueRates: null, csv: null, txt: null, pngUrl: null };
      }

      // Assign the file content based on file type
      if (fileName!.endsWith('.csv')) {
        const csv = await file.async('text');
        zFolders[folderName].csv = csv;
      } else if (fileName!.endsWith('.txt')) {
        const txt = await file.async('text');
        zFolders[folderName].txt = txt;
        const trueRates = (txt.trim().split('\n').map(s => (([label, score]) => ({ label, score }))(s.split(':')))).reduce((acc: TrueRates, curr): TrueRates => ({ ...acc, [curr.label]: curr.score }), {});
        zFolders[folderName].trueRates = trueRates
      } else if (fileName!.endsWith('.png')) {
        const blob = await file.async('blob');
        const url = URL.createObjectURL(blob);
        zFolders[folderName].pngUrl = url;
      }
    }
    // Convert the zFolders object to an array
    return Object.values(zFolders);
  } catch (err) {
    console.error(err);
  }
};

const handleUnzip = async () => {
  const unzipped = await loadZip()
  if (unzipped) {
    resultStore.updateResults(unzipped)
  }
}

</script>
<style>
.order-direction {
  margin: 0px;
  padding: 0px;
  background-color: inherit;
  
}
</style>