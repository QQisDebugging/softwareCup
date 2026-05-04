<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-model="requirement"
          label="请输入需求"
          outlined
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-btn color="primary" :disabled="loading" @click="generatePPT">
          <template v-if="loading">
            <v-icon class="mr-2">mdi-loading mdi-spin</v-icon>
            生成中...(大概一两分钟)
          </template>
          <template v-else>
            生成
          </template>
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-progress-linear
          v-if="loading"
      
          color="yellow-darken-2"
          indeterminate
        ></v-progress-linear>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <div v-if="pptUrl">
          <iframe :src="iframeSrc" width="100%" height="600px" frameborder="1"></iframe>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref } from 'vue';

export default {
  data() {
    return {
      requirement: '',
      loading: false,
      progress: 0,
      pptUrl: ''
    };
  },
  computed: {
    iframeSrc() {
      return `https://view.officeapps.live.com/op/view.aspx?src=${this.pptUrl}`;
    }
  },
  methods: {
    async generatePPT() {
      try {
        this.loading = true;
        this.progress = 0;
        const url = `${this.$backendUrl}/generate_ppt`;
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ requirement: this.requirement })
        });

        if (response.ok) {
          const result = await response.json();
          this.pptUrl = result.ppt_url;
        } else {
          console.error('生成失败');
        }
      } catch (error) {
        console.error('生成失败', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>
