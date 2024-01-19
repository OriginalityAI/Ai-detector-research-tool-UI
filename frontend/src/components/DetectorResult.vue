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
        <v-btn color="primary" size="x-large" rounded="lg" class="text-none"
          @click="downloadFolder(results.blob!, result.name)"><span
            class="text-h6 font-weight-black pr-2">Download</span><font-awesome-icon class="text-h6"
            icon="fa-solid fa-download"></font-awesome-icon></v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup lang="ts">
import type { Folder, } from '@/assets/types';
import ResultTable from './ResultTable.vue';
import JSZip from 'jszip'
import { useResultsStore } from '@/stores/resultsStore'
import { storeToRefs } from 'pinia';

const resultStore = useResultsStore()
const { results } = storeToRefs(resultStore)



const props = defineProps<{
  result: Folder
}>()

const formattedName = `${props.result.name[0] + props.result.name.slice(1).toLowerCase()}`

async function downloadFolder(resultsBlob: Blob, folderName: string) {
  const zip = await new JSZip().loadAsync(resultsBlob)
  const newZip = new JSZip();

  // Read the provided zip file
  try {
    let folderFound = false;
    const filePromises: any = [];

    zip.forEach((relativePath, file) => {
      if (relativePath.startsWith(`${folderName}/`)) {
        folderFound = true;
        const newPath = relativePath.substring(folderName.length + 1);
        const filePromise = file.async('blob').then(blob => {
          newZip.file(newPath, blob);
        });
        filePromises.push(filePromise);

      }
    });

    if (!folderFound) {
      console.log('Folder not found:', folderName);
      return null;
    }

    await Promise.all(filePromises);
    
    newZip.generateAsync({ type: "blob" }).then(function (blob: Blob) {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = folderName + ".zip";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });

  } catch (err) {
    console.error('Error reading zip file:', err);
  }
}

</script>
<style>
.matrix {
  border-radius: 16px;
  margin-right: 100px;
  margin-left: 100px;
}
</style>