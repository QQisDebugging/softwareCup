<template>
  <v-card>
    <v-card-title>
      <div class="d-flex justify-space-between align-center w-100">
        <span>所有学生</span>
        <div>
          <v-btn @click="dialog = true" color="primary">批量导入学生</v-btn>
          <v-btn @click="downloadTemplate" color="secondary">下载模板</v-btn>
        </div>
      </div>
    </v-card-title>
    <v-card-text>
      <v-text-field
        v-model="searchQuery"
        append-icon="mdi-magnify"
        label="搜索学生"
        single-line
        hide-details
      ></v-text-field>
      <v-data-table
        :headers="headers"
        :items="filteredLeaderboard"
        :items-per-page="50"
        class="elevation-1"
        no-data-text="暂无数据"
      >
        <template v-slot:item.rank="{ item, index }">
          <v-chip color="primary" variant="elevated">{{ item.idx }}</v-chip>
        </template>
        <template v-slot:item.request_times="{ item }">
          <v-chip color="green">{{ item.request_times }}</v-chip>
        </template>
      </v-data-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title class="headline">批量导入学生</v-card-title>
        <v-card-text>
          <p>请上传包含学生数据的XLS文件。默认密码为111111</p>
          <input type="file" @change="handleFileUpload" accept=".xls,.xlsx">
          <div v-if="fileData.length > 0">
            <v-btn @click="submitData" color="primary" :disabled="loading">
              导入数据
            </v-btn>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="dialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :timeout="snackbarTimeout" :color="snackbarColor">
      {{ snackbarMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="snackbar = false">关闭</v-btn>
      </template>
    </v-snackbar>
  </v-card>
</template>

<script>
import axios from '@/utils/axiosConfig';
import * as XLSX from 'xlsx';

export default {
  name: 'RankComponent',
  data() {
    return {
      leaderboard: [],
      searchQuery: '',
      dialog: false,
      fileData: [],
      loading: false,
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success',
      snackbarTimeout: 3000,
      headers: [
        { title: '排行', value: 'rank', sortable: false },
        { title: '姓名', value: 'name', sortable: true },
        { title: '班级', value: 'major', sortable: true },
        { title: '逗币', value: 'request_times', sortable: true },
        { title: '学习时长', value: 'study_time', sortable: true }
      ]
    };
  },
  mounted() {
    this.fetchLeaderboard();
  },
  methods: {
    fetchLeaderboard() {
      axios.get(`${this.$backendUrl}/api/getRank`)
        .then(response => {
          this.leaderboard = response.data;
        })
        .catch(error => {
          console.error('Error fetching leaderboard:', error);
        });
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
          const jsonData = XLSX.utils.sheet_to_json(firstSheet);
          this.fileData = jsonData;
        };
        reader.readAsArrayBuffer(file);
      }
    },
    submitData() {
      this.loading = true;
                axios.post(`${this.$backendUrl}/api/importStudents`, { 'students': this.fileData })
        .then(response => {
          this.loading = false;
          this.dialog = false;
          this.fetchLeaderboard();
          this.showSnackbar('数据提交成功', 'success');
        })
        .catch(error => {
          this.loading = false;
          this.showSnackbar('数据提交失败', 'error');
        });
    },
    showSnackbar(message, color) {
      this.snackbarMessage = message;
      this.snackbarColor = color;
      this.snackbar = true;
    },
    downloadTemplate() {
      window.location.href = 'https://aust-teachassist-system.oss-cn-hangzhou.aliyuncs.com/%E5%AD%A6%E7%94%9F%E4%BF%A1%E6%81%AF%E5%AF%BC%E5%85%A5%E6%A8%A1%E6%9D%BF.xlsx';
    }
  },
  computed: {
    filteredLeaderboard() {
      return this.leaderboard.filter(student => {
        const query = this.searchQuery.toLowerCase();
        return (
          student.name.toLowerCase().includes(query) ||
          student.major.toLowerCase().includes(query) ||
          student.description.toLowerCase().includes(query)
        );
      });
    }
  }
};
</script>

<style>
/* Add your custom styles here */
</style>
