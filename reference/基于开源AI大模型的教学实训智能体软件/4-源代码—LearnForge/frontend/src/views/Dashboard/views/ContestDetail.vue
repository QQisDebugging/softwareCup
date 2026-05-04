<template>
  <v-container>
    <v-alert v-if="error" type="error" dismissible>
      {{ error }}
    </v-alert>

    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-information</v-icon>
        {{ contestDetails.contest_name }}
      </v-card-title>
      <v-card-text>
        <div><strong>创建者编号:</strong> {{ contestDetails.creator_tno }}</div>
        <div><strong>发布日期:</strong> {{ formattedSubmissionDate(contestDetails.publish_date) }}</div>
        <div><strong>题目类型:</strong> {{ contestDetails.question_type }}</div>
      </v-card-text>
    </v-card>

    <v-divider class="my-4"></v-divider>

    <v-card class="mb-3">
      <v-card-title>
        <v-icon left>mdi-trophy-variant</v-icon>
        排名
      </v-card-title>
      <v-card-text>

        <v-table>
          <thead>
            <tr>
              <th class="text-left">排行</th>
              <th class="text-left">学号</th>
              <th class="text-left">姓名</th>
              <th class="text-left">专业</th>
              <th class="text-left">提交时间</th>
              <th class="text-left">分数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, index) in contestDetails.student_answers" :key="index">
              <td><v-chip color="primary" variant="elevated">{{ index + 1 }}</v-chip></td>
              <td>{{ student.sno }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.major }}</td>
              <td>{{ formattedSubmissionDate_withoutYear(student.submission_date) }}</td>
              <td>{{ student.score }}</td>
            </tr>
          </tbody>
        </v-table>


        <!-- <v-list>
            <v-list-item-group>
              <v-list-item v-for="(student, index) in contestDetails.student_answers" :key="index">
                <v-list-item-content>
                  <v-list-item-title>{{ index + 1 }}</v-list-item-title>
                  <v-list-item-subtitle>学生编号: {{ student.sno }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-chip color="primary">{{ student.score }}</v-chip>
                </v-list-item-action>
              </v-list-item>
            </v-list-item-group>
          </v-list> -->
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import axios from '@/utils/axiosConfig';
import moment from 'moment';
export default {
  props: ['contest_id'],
  data() {
    return {
      contestDetails: {},
      error: ''
    };
  },
  created() {
    this.fetchContestDetails();
  },
  methods: {
    formattedSubmissionDate_withoutYear(submissionDate) {
      console.log(submissionDate)
      return moment(submissionDate).subtract(8, 'hours').format('MM-DD HH:mm');

    },
    formattedSubmissionDate(submissionDate) {
      
      return moment(submissionDate).format('YYYY-MM-DD HH:mm');
    },
    async fetchContestDetails() {
      this.error = '';
      try {
        const response = await axios.get(`${this.$backendUrl}/api/getContestDetails`, {
          params: { contest_id: this.contest_id }
        });
        this.contestDetails = response.data;
      } catch (error) {
        if (error.response && error.response.data) {
          this.error = error.response.data.error;
        } else {
          this.error = '请求失败，请稍后再试';
        }
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

/* Card styling */
.v-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.v-card-title {
 
  border-bottom: 1px solid #e0e0e0;
  padding: 10px;
}

.v-card-text>div {
  margin-bottom: 5px;
  padding: 5px 10px;
}

</style>