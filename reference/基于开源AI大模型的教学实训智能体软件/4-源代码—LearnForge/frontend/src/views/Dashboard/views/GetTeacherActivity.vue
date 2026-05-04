<template>
  <v-container>
    <v-alert v-if="error" type="error" dismissible>
      {{ error }}
    </v-alert>

    <v-row>
      <v-col v-for="activity in activities" :key="activity.activity_id" cols="12">
        <v-card class="mb-3 " >
          <v-card-title>
            {{ activity.activity_name }}
            <v-btn icon @click="confirmDelete(activity)" size="small" variant="flat">
              <v-icon color="red">mdi-delete</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div><strong>任务编号:</strong> {{ activity.activity_id }}</div>
            <div><strong>创建日期:</strong> {{ formattedSubmissionDate(activity.created_date) }}</div> 
            <v-md-preview 
    :text="activity.description" 
    class="md-preview-container"
  ></v-md-preview>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="goToDetail(activity.activity_id)">查看提交情况</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">确认删除</v-card-title>
        <v-card-text>您确定要删除任务 "{{ selectedActivityToDelete?.activity_name }}" 吗？</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red" @click="deleteActivity">删除</v-btn>
          <v-btn color="grey" @click="closeDeleteDialog">取消</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
<script>
import axios from '@/utils/axiosConfig';
import moment from 'moment';
export default {
  data() {
    return {
      tno: localStorage.getItem('username'),
      activities: [],
      error: '',
      deleteDialog: false,
      selectedActivityToDelete: null
    };
  },
  created() {
    this.fetchActivities();
  },
  methods: {
    formattedSubmissionDate(submissionDate) {
      return moment(submissionDate).format('YYYY-MM-DD HH:mm');
    },
    async fetchActivities() {
      this.error = '';
      try {
        const response = await axios.get(`${this.$backendUrl}/api/getTeacherActivities`, {
          params: { tno: this.tno }
        });
        this.activities = response.data;
      } catch (error) {
        if (error.response && error.response.data) {
          this.error = error.response.data.error;
        } else {
          this.error = '请求失败，请稍后再试';
        }
      }
    },
    goToDetail(activityId) {
      this.$router.push({ name: 'ActivityDetail', params: { activity_id: activityId } });
    },
    confirmDelete(activity) {
      this.selectedActivityToDelete = activity;
      this.deleteDialog = true;
    },
    closeDeleteDialog() {
      this.deleteDialog = false;
      this.selectedActivityToDelete = null;
    },
    async deleteActivity() {
      try {
        await axios.post(`${this.$backendUrl}/api/deleteActivity`, {
          activity_id: this.selectedActivityToDelete.activity_id,
          tno: localStorage.getItem('username')
        },{
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
        this.activities = this.activities.filter(activity => activity.activity_id !== this.selectedActivityToDelete.activity_id);
        this.closeDeleteDialog();
      } catch (error) {
        this.error = '删除任务失败，请稍后再试';
        this.closeDeleteDialog();
      }
    }
  }
};
</script>
<style scoped>
.v-container {
  max-width: 800px;
  margin: auto;
}
.v-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}
.v-card-title {
  border-bottom: 1px solid #e0e0e0;
  padding: 10px;
}
.v-card-text > div {
  margin-bottom: 5px;
  padding: 5px 10px;
}
.md-preview-container {
  max-height: 300px; /* 设置特定高度 */
  overflow-y: auto;  /* 超过高度时可以垂直滚动 */
  padding-right: 8px; /* 为滚动条预留空间，避免遮挡文本 */
}
</style>
