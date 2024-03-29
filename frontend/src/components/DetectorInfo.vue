<template>
  <v-row v-if="item.additionalKey" no-gutters align="start" class="px-16 pb-4">
    <v-col cols="12" md="auto" >
      <v-btn :color="btnColor" size="x-large" rounded="pill" class="detector-btn text-none text-h6 font-weight-black mr-6"
        @click="toggleDetector">{{ item.name }}</v-btn>
    </v-col>
    <v-col cols="12" md="6" class="flex-grow-1 pr-6">
      <v-text-field :rules="item.selected ? detectorKeyRules : []" :disabled="!item.selected" v-model="localItem.key" @input="emitUpdate" rounded="lg" variant="outlined"
        prepend-inner-icon="mdi-key" clearable :type="showKey ? 'text' : 'password'" :append-icon="showKey ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showKey = !showKey" hide-details="auto" label="Key"></v-text-field>
    </v-col>
    <v-col cols="12" md="auto" class="flex-grow-1">
      <v-text-field :rules="item.selected ? detectorIdRules : []" :disabled="!item.selected" v-model="localItem.additionalKey!.value" @input="emitUpdate" rounded="lg" variant="outlined"
        prepend-inner-icon="mdi-key" label="ID" clearable :type="showAdditionalKey ? 'text' : 'password'" :append-icon="showAdditionalKey ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showAdditionalKey = !showAdditionalKey" hide-details="auto"></v-text-field>
    </v-col>
  </v-row>
  <v-row v-else no-gutters align="start" class="px-16 pb-4">
    <v-col cols="12" md="auto">
      <v-btn :color="btnColor" size="x-large" rounded="pill" class="detector-btn text-none text-h6 font-weight-black mr-6"
        @click="toggleDetector">{{ item.name }}</v-btn>
    </v-col>
    <v-col cols="12" md="auto" class="flex-grow-1">
      <v-text-field :rules="item.selected ? detectorKeyRules : []" :disabled="!item.selected" v-model="localItem.key" @input="emitUpdate" rounded="lg" variant="outlined"
        prepend-inner-icon="mdi-key" label="Key" clearable :type="showKey ? 'text' : 'password'" :append-icon="showKey ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showKey = !showKey" hide-details="auto"></v-text-field>
    </v-col>
  </v-row>
</template>
<script setup lang="ts">
import { computed, defineEmits } from 'vue';
import type { DetectorItem } from '@/assets/types';
import { watch } from 'vue';
import { ref } from 'vue';


const showKey = ref(false)
const showAdditionalKey = ref(false)

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

type ValidationRule = (v: string) => string | boolean

const detectorKeyRules: ValidationRule[] = [
  (v: string) => !!v || 'Please include a key for API access.'
]

const detectorIdRules: ValidationRule[] = [
  (v: string) => !!v || 'Please include a scan ID for API access.'
]

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
}
</style>