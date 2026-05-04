<template>
    <v-app>
      <v-main>
        <v-container fluid>
          <v-row>
            <v-col cols="6">
              <codemirror
                v-model="code"
                :extensions="extensions"
                @ready="handleReady"
              />
            </v-col>
            <v-col cols="6">
              <v-btn @click="generateDiagram" color="blue" class="mt-3">生成流程图</v-btn>
              <v-btn v-if="diagram" @click="downloadDiagram" color="green" class="mt-3">下载流程图</v-btn>
              <div class="mt-3">
                <vue-mermaid-string :value="diagram" />
              </div>
            </v-col>
          </v-row>
          <v-dialog v-model="loading" hide-overlay persistent width="300">
        <v-card>
          <v-card-text>正在生成流程图中，请坐和放宽......</v-card-text>
          <v-progress-linear indeterminate color="primary"></v-progress-linear>
        </v-card>
      </v-dialog>
        </v-container>
      </v-main>
    </v-app>
  </template>
  
  <script>
  import { defineComponent, ref } from 'vue';
  import { Codemirror } from 'vue-codemirror';
  import { javascript } from '@codemirror/lang-javascript';
  import { oneDark } from '@codemirror/theme-one-dark';
  import VueMermaidString from 'vue-mermaid-string';
  import axios from 'axios';
  
  import { backendUrl } from '@/main';
  
  export default defineComponent({
    components: {
      Codemirror,
      VueMermaidString,
    },
    setup() {
      const code = ref(`//这里输入代码`);
      const extensions = [javascript(), oneDark];
      const view = ref(null);
      const diagram = ref('');
      const loading = ref(false);
  
      const handleReady = (payload) => {
        view.value = payload.view;
      };
  
      const generateDiagram = async () => {
        const url = `${backendUrl}/api/flowchart`; 
        loading.value = true;
        try {
          const response = await axios.post(url, {
            code: code.value,
          });
  
          const result = response.data.replace(/```json/g, '').replace(/```/g, '');
          console.log(result)
          const d = JSON.parse(result).code;
          console.log(d);
          if (result) {
            diagram.value = d;
          } else {
            console.error('生成失败');
          }
        } catch (error) {
          console.error('生成失败:', error);
        } finally {
          loading.value = false;
        }
      };
  
      const downloadDiagram = () => {
        const svg = document.querySelector('svg');
        if (svg) {
          const svgData = new XMLSerializer().serializeToString(svg);
          const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
          const svgUrl = URL.createObjectURL(svgBlob);
          const downloadLink = document.createElement('a');
          downloadLink.href = svgUrl;
          downloadLink.download = 'diagram.svg';
          document.body.appendChild(downloadLink);
          downloadLink.click();
          document.body.removeChild(downloadLink);
        }
      };
  
      return {
        code,
        extensions,
        handleReady,
        generateDiagram,
        downloadDiagram,
        diagram,
        loading,
      };
    },
  });
  </script>
  
  <style scoped>
  /* 根据需要添加样式 */
  </style>
  