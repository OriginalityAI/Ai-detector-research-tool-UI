<template>
  <v-row v-if="item.additionalKey" no-gutters align="center" class="px-16 pb-4">
    <v-col cols="auto">
      <v-btn :color="btnColor" size="x-large" rounded="pill" class="detector-btn text-none text-h6 font-weight-black mr-6"
        @click="toggleDetector">{{ item.name }}</v-btn>
    </v-col>
    <v-col cols="7" class="flex-grow-1 pr-6">
      <v-text-field v-model="localItem.key" @input="emitUpdate" rounded="lg" variant="outlined"
        prepend-inner-icon="mdi-key" clearable type="password" hide-details="auto" label="Key"></v-text-field>
    </v-col>
    <v-col cols="auto" class="flex-grow-1">
      <v-text-field v-model="localItem.additionalKey!.value" @input="emitUpdate" rounded="lg" variant="outlined"
        prepend-inner-icon="mdi-key" label="ID" clearable type="password" hide-details="auto"></v-text-field>
    </v-col>
  </v-row>
  <v-row v-else no-gutters align="center" class="px-16 pb-4">
    <v-col cols="auto">
      <v-btn :color="btnColor" size="x-large" rounded="pill" class="detector-btn text-none text-h6 font-weight-black mr-6"
        @click="toggleDetector">{{ item.name }}</v-btn>
    </v-col>
    <v-col cols="auto" colspan="2" class="flex-grow-1">
      <v-text-field v-model="localItem.key" @input="emitUpdate" rounded="lg" variant="outlined"
        prepend-inner-icon="mdi-key" label="Key" clearable type="password" hide-details="auto"></v-text-field>
    </v-col>
  </v-row>
</template>
<script setup lang="ts">
import { computed, defineEmits } from 'vue';
import type { DetectorItem } from '@/assets/types';
import { watch } from 'vue';
import { ref } from 'vue';


const props = defineProps<{
  item: DetectorItem
}>()

const btnColor = computed(() => props.item.selected ? 'secondary' : '#a3a3a3')

const emit = defineEmits(['update-item'])

// Create a local reactive copy of the item
const localItem = ref({ ...props.item });

// Watch for changes in the prop and update the local copy
watch(() => props.item, (newVal) => {
  localItem.value = { ...newVal };
});

const emitUpdate = () => {
  emit('update-item', localItem.value);
};

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