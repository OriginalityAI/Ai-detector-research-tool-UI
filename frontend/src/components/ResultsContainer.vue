<template>
  <v-container class="px-0 pb-12">
    <v-sheet color="#f5f5f5" class="sheet">
      <v-row no-gutters>
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
      </v-row>
      <v-row no-gutters>
        <v-btn @click="loadZip">Unzip</v-btn>
      </v-row>
    </v-sheet>
  </v-container>
</template>
<script setup lang="ts">
import JSZip from 'jszip';
import type { Ref } from 'vue';
import type { Folder, zFolders} from '@/assets/types'
import { ref } from 'vue';
import fs from 'fs';


const folders: Ref<Folder[]> = ref([]);

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
        zFolders[folderName] = { name: folderName, csv: null, txt: null, pngUrl: null };
      }

      // Assign the file content based on file type
      if (fileName!.endsWith('.csv')) {
        const csv = await file.async('text');
        zFolders[folderName].csv = csv;
      } else if (fileName!.endsWith('.txt')) {
        const txt = await file.async('text');
        zFolders[folderName].txt = txt;
      } else if (fileName!.endsWith('.png')) {
        const blob = await file.async('blob');
        const url = URL.createObjectURL(blob);
        zFolders[folderName].pngUrl = url;
      }
    }
    // Convert the zFolders object to an array
    folders.value = Object.values(zFolders);
  } catch (err) {
    console.error(err);
  }
};

</script>
<style></style>