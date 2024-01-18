<template>
  <v-btn class="text-none font-weight-black text-h6" size="large" color="secondary" rounded="pill"
              @click="downloadTemplate">
              <span class="pr-2">Download Template</span><font-awesome-icon
                icon="fa-solid fa-download"></font-awesome-icon>
            </v-btn>
</template>
<script setup lang="ts">

const templateCSV = `text,dataset,label
"Hello World, this is some example text for AI",gpt-4,ai-generated
"Hello World, this is some example human generated text",human,human-generated`

const downloadTemplate = () => {
  const url = window.URL.createObjectURL(new Blob([templateCSV]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'template.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

</script>
<style lang="">
  
</style>