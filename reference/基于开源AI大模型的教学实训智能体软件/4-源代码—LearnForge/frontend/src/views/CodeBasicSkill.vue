<template>
  <!-- <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css"> -->
  <v-card>
    <v-tabs v-model="tab" bg-color="primary">
      <v-tab value="alglorithmtest">算法竞赛入门</v-tab>
      <v-tab value="c">C语言基础</v-tab>
      <v-tab value="py">PYTHON基础</v-tab>
      <v-tab value="website">AUST计算机求生指南</v-tab> <!-- New tab -->
    </v-tabs>

    <v-card-text>
      <v-tabs-window v-model="tab">
        <v-tabs-window-item value="c">
          <v-md-preview :text="one"></v-md-preview>
          <!-- <div class="markdown-body" v-html="markdown.render(one)" /> -->
        </v-tabs-window-item>
        <v-tabs-window-item value="py">
          <v-md-preview :text="python"></v-md-preview>
          <!-- <div class="markdown-body" v-html="markdown.render(python)" /> -->
        </v-tabs-window-item>
        <v-tabs-window-item value="alglorithmtest">
          <v-md-preview :text="alglorithmtest"></v-md-preview>
          <!-- <div class="markdown-body" v-html="markdown.render(alglorithmtest)" /> -->
        </v-tabs-window-item>
        <v-tabs-window-item value="website"> <!-- New tab content -->
          <iframe src="https://aust-cs-plan.forsakendelusion.online/" width="100%" height="1000px" style="border: none;"></iframe> <!-- Embeds the website -->
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>
  </v-card>
</template>



<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/utils/axiosConfig';


const tab = ref(null);

const one = ref('');
const python = ref('');
const alglorithmtest = ref('');


onMounted(async () => {
  try {
    const [exampleModule, pythonModule, alglorithmtestModule] = await Promise.all([
      import('../assets/articles/example.md'),
      import('../assets/articles/python.md'),
      import('../assets/articles/alglorithmtest.md')
    ]);

    const [response1, response2, response3] = await Promise.all([
      axios.get(exampleModule.default),
      axios.get(pythonModule.default),
      axios.get(alglorithmtestModule.default)
    ]);

    one.value = response1.data;
    python.value = response2.data;
    alglorithmtest.value = response3.data;
  } catch (error) {
    console.error('Error fetching Markdown:', error);
  }
});
</script>
