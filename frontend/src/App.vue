<template>
  <main>
    <v-container justify-center class="content-container">
      <v-row no-gutters justify="center" align="center" class="pt-4 pb-4">
        <img class="brand" src="/pt-logo-small.png" />
      </v-row>
      <v-row no-gutters justify="center" class="pb-16">
        <span class="text-h3 text-center font-weight-black">
          AI Detector<br>Efficacy Research Tool
        </span>
      </v-row>
      <v-row no-gutters class="pb-16 px-16">
        <div class="glass sheet">
          <p class="text-h4 font-weight-bold pt-6 pl-6 pr-6 pb-4">What is this tool?</p>
          <p class="text-h6 font-weight-medium pb-6 pl-6 pr-6">
            The tool takes a set of text files and runs them through a number of
            AI detectors. It then outputs the results to a CSV file. The tool also
            generates a confusion matrix to show the accuracy of the detectors.

            But what is a confusion matrix? A confusion matrix is a table that is
            used to describe the performance of a classification model. It shows
            the number of correct and incorrect predictions made by the
            classification model compared to the actual outcomes.

            This table is
            extremely useful for comparing the performance of different detectors
            as it will show the true positives, false positives, true negatives
            and false negatives for each detector. This allows you to see which
            detectors are the most accurate.
          </p>
        </div>
      </v-row>
      <InputSheet />
      <ResultsContainer />
      <v-row no-gutters class="pt-6 pb-16">
        <div class="glass sheet">
          <p class="text-h4 font-weight-bold pt-6 pl-6 pr-6 pb-4">How do I read a confusion matrix?</p>
          <p class="text-h6 font-weight-medium pb-8 pl-6 pr-6">
            A confusion matrix is a table that describes the performance of a detector on a particular set of text
            samples.
            The upper left cell of the table shows the true positive rate for that detector, meaning how often it was able
            to accurately identify AI written text as AI written.
            The lower right cell of the table shows the true negative rate of the model, meaning how often it was able to
            accurately identify human written text as human written.
            <span class="text-highlight">For these true rates, a higher percentage is better.</span>
            <br>
            <br>
            The lower left cell of the table shows the false positive rate, meaning how often that detector mistakenly
            identified human writing as written by AI.
            The upper right cell of the table shows the false negative rate, meaning how often that detector mistakenly
            identified AI writing as written by a human.
            <span class="text-highlight">For these false rates, a lower percentage is better.</span>
          </p>
          <v-row no-gutters justify="center">
            <v-col cols="auto">
              <img class="matrix-example" src="/confusion_matrix_example.jpg">
            </v-col>
          </v-row>
          <p class="text-h6 font-weight-medium pt-6 pb-6 pl-6 pr-6">
            If you want to learn more about confusion matrices, techniques for evaluating AI detectors, and results from
            our own research at Originality.ai, <a class="text-highlight" href="https://originality.ai/blog/ai-content-detection-accuracy">check out our blog post</a>.
          </p>
        </div>
      </v-row>
    </v-container>
  </main>
</template>

<script setup lang="ts">
import InputSheet from './components/InputSheet.vue';
import ResultsContainer from './components/ResultsContainer.vue';

</script>


<style>
main {
  background-color: var(--dark);
  /* color: var(--faint-blue); */
  color: white;
  background-image: linear-gradient(#2b2154, rgba(43, 33, 84, 0) 61%),
    linear-gradient(rgba(0, 0, 0, 0) 24%, rgba(120, 89, 255, 0.3)),
    linear-gradient(rgba(43, 33, 84, 0.4), rgba(43, 33, 84, 0.4)),
    linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.2)),
    url(https://assets-global.website-files.com/63ee996…/63ee9c9…_texture-1.webp);
  background-position:
    0 0,
    0 0,
    0 0,
    0 0,
    50% 0;
  background-size: auto, auto, auto, auto, 1600px;
  min-width: 100vw;
  min-height: 100vh;
}

.brand {
  width: 600px;
}

.glass {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.matrix-example {
  max-width: 926px;
  max-height: 629px;
}

.text-highlight {
  color: var(--bright-orange)
}

:root {
  --light-blue-text: #474c6e;
  --dark: black;
  --dark-purple: #2b2154;
  --background-tint: #f7faff;
  --faint-blue: #dadfed;
  --darker-purple: #1b1240;
  --darker-blue: #0a0d25;
  --darkest-purple: #0b0426;
  --lavender: #dfe8ff;
  --light-purple: #7859ff;
  --ice-green: #8efff2;
  --midnight-blue: #2d335d;
  --bright-orange: #ffbb59;
  --light-dimmed-text: #babcd1;
  --mid-purple: #5a4d8e;
}

@media only screen and (min-width: 1200px) {
  .content-container {
    width: 1248px;
  }
}</style>
