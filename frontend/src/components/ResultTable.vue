<template>
  <v-container fluid>
    <v-table class="rates-table mx-12">
      <thead>
        <th v-for="rate of ratesArr" :key="rate.label" class="text-center text-h6 font-weight-black">{{ rate.label }}</th>
      </thead>
      <tbody>
        <tr>
          <td v-for="rate of ratesArr" :key="rate.label" class="text-center text-h6 font-weight-black">
            {{ rate.score }}
          </td>
          </tr>
      </tbody>
    </v-table>
  </v-container>
</template>
<script setup lang="ts">
import type { TrueRates } from '@/assets/types'
import {onMounted} from 'vue';

const props = defineProps<{
  trueRates: TrueRates
}>()

const ratesArr = Object.entries(props.trueRates).map(([label, score]) => ({label, score}))

onMounted(() => console.log(props.trueRates))
</script>
<style>
.rates-table th {
  max-width: 180px;
}

.rates-table td, .rates-table th {
  border-right: 2px solid #000000;
}
.rates-table tH {
  border-bottom: 2px solid #000000;
}
.rates-table tr td:last-child, .rates-table tr th:last-child {
  border-right: none;
}
.rates-table tr:last-child {
  border-bottom: none;
}
</style>