<template>
  <v-container class="pa-0">
    <v-sheet color="#fafafa" class="sheet">
      <v-row no-gutters align="center" class="pt-6 px-6 pb-6">
        <v-col cols="auto">
          <span class="text-h4 text-grey font-weight-bold">Input</span>
        </v-col>
        <v-col>
          <v-divider thickness="2" class="ml-4 mr-2"></v-divider>
        </v-col>
      </v-row>
      <v-row no-gutters class="px-12 pb-6">
          <v-file-input class="flex align-start" prepend-icon="" append-inner-icon="mdi-paperclip" hide-details="auto" rounded="lg" variant="solo" bg-color="#d4d4d4"></v-file-input>
      </v-row>
      <v-row no-gutters justify="space-evenly" class="px-4 pb-6">
        <v-col cols="auto">
          <v-btn class="text-none font-weight-black text-h6" size="large" color="secondary" rounded="pill">
            <span class="pr-2">Download Default</span><font-awesome-icon icon="fa-solid fa-download"></font-awesome-icon>
          </v-btn>
        </v-col>
        <v-col cols="auto">
          <v-btn class="text-none font-weight-black text-h6" size="large" color="secondary" rounded="pill">
            <span class="pr-2">Download Template</span><font-awesome-icon icon="fa-solid fa-download"></font-awesome-icon>
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
    </v-sheet>
  </v-container>
</template>
<script setup lang="ts">
</script>
<style>
</style>