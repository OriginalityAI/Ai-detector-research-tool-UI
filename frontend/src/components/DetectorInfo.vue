<template>
  <v-row v-if="item.additionalKey" no-gutters align="center" class="px-16 pb-4">
    <v-col cols="auto">
      <v-btn :color="btnColor" size="x-large" rounded="pill" class="detector-btn text-none text-h6 font-weight-black mr-6"
        @click="toggleDetector">{{ item.name }}</v-btn>
    </v-col>
    <v-col cols="7" class="flex-grow-1 pr-6">
      <v-text-field rounded="lg" variant="solo" prepend-inner-icon="mdi-key" hide-details="auto"></v-text-field>
    </v-col>
    <v-col cols="auto" class="flex-grow-1">
      <v-text-field rounded="lg" variant="solo" prepend-inner-icon="mdi-key" hide-details="auto"></v-text-field>
    </v-col>
  </v-row>
  <v-row v-else no-gutters align="center" class="px-16 pb-4">
    <v-col cols="auto">
      <v-btn :color="btnColor" size="x-large" rounded="pill"
        class="detector-btn text-none text-h6 font-weight-black mr-6" @click="toggleDetector">{{ item.name }}</v-btn>
    </v-col>
    <v-col cols="auto" colspan="2" class="flex-grow-1">
      <v-text-field rounded="lg" variant="solo" prepend-inner-icon="mdi-key" hide-details="auto"></v-text-field>
    </v-col>
  </v-row>
</template>
<script setup lang="ts">
import { computed, defineEmits } from 'vue';

type DetectorItem = {
  name: string
  selected: boolean;
  key: string;
  additionalKey?: {
    name: string,
    value: string
  } | undefined;
}
const props = defineProps<{
  item: DetectorItem
}>()

const btnColor = computed(() => props.item.selected ? 'secondary' : '#a3a3a3')

const emit = defineEmits(['update-item'])

const toggleDetector = () => {
  // Create a copy of the item with the updated 'selected' value
  const updatedItem = { ...props.item, selected: !props.item.selected };
  // Emit the updated item
  emit('update-item', updatedItem);
}

</script>
<style>
.detector-btn {
  width: 200px;
}</style>