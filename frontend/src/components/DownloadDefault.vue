<template>
 <v-btn class="text-none font-weight-black text-h6 cool-btn-dark" size="large" rounded="pill">
    <span class="pr-2" @click=fetchDefaultCSV>Download Default</span><font-awesome-icon icon="fa-solid fa-download"></font-awesome-icon>
  </v-btn>
</template>
<script setup lang="ts">

const fetchDefaultCSV = async () => {
  const response = await fetch('http://localhost:8000/api/download/default_csv')
  const data = await response.blob()
  downloadDefaultCSV(data)
}

const downloadDefaultCSV = (csv_file: Blob) => {
  const url = window.URL.createObjectURL(csv_file)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'default_sample.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

</script>
<style lang="">

</style>