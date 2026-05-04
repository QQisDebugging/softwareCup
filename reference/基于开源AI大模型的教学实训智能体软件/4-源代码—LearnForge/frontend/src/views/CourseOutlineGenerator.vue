<template>
    <v-container>
      <v-form @submit.prevent="submitForm" ref="form">
        <v-text-field
          label="课程名称"
          v-model="form.course_name"
          required
        ></v-text-field>
  
        <v-text-field
          label="学时"
          v-model="form.course_alltime"
          required
        ></v-text-field>
  
        <v-text-field
          label="实验学时"
          v-model="form.course_labtime"
          required
        ></v-text-field>
  
        <v-text-field
          label="适用专业"
          v-model="form.course_sub"
          required
        ></v-text-field>
  
        <v-select
          label="课程性质"
          v-model="form.course_type"
          :items="courseTypes"
          required
        ></v-select>
  
        <v-file-input
          label="上传文件（可选择）"
          v-model="form.file"
          required
        ></v-file-input>
  
        <v-btn type="submit" color="primary">提交</v-btn>
      </v-form>

      <v-divider inset></v-divider>
      <v-divider inset></v-divider>

      <v-divider inset></v-divider>
      <v-divider inset></v-divider>
  
      <v-alert v-if="successMessage" type="success">
        {{ successMessage }}
        <v-btn :href="downloadLink" download color="primary">下载文档</v-btn>
      </v-alert>
  
      <v-dialog v-model="loading" hide-overlay persistent width="300">
        <v-card color="primary" dark>
          <v-card-text>
            正在生成文档，请稍候...
            <v-progress-linear indeterminate color="white" class="mt-4"></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        form: {
          course_name: '',
          course_alltime: '',
          course_labtime: '',
          course_sub: '',
          course_type: '',
          file: null,
        },
        successMessage: '',
        downloadLink: '',
        loading: false,
        courseTypes: ['学科基础', '大类平台', '专业必修', '专业选修'],
      };
    },
    methods: {
      async submitForm() {
        const formData = new FormData();
        formData.append('course_name', this.form.course_name);
        formData.append('course_alltime', this.form.course_alltime);
        formData.append('course_labtime', this.form.course_labtime);
        formData.append('course_sub', this.form.course_sub);
        formData.append('course_type', this.form.course_type);
        formData.append('file', this.form.file);
  
        this.loading = true;
        try {
          const response = await axios.post(`${this.$backendUrl}/generateCourseOutline`, formData);
          if (response.status === 200) {
            const result = response.data;
            this.successMessage = result.message;
            this.downloadLink = `${this.$backendUrl}/result/${result.filename}`;
          } else {
            console.error('提交失败');
          }
        } catch (error) {
          console.error('提交过程中发生错误', error);
        } finally {
          this.loading = false;
        }
      },
    },
  };
  </script>
  
  <style scoped>
  /* 添加一些样式来美化表单 */
  </style>
  