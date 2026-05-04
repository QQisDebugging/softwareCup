<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8">
        <v-card>
          <v-card-title>
            <span class="text-h5">Today's Contest Submissions</span>
          </v-card-title>
          <v-card-text>
            <v-alert
              v-if="!contests.length"
              type="info"
            >
              No submissions found for today.
            </v-alert>
            <v-list v-if="contests.length">
              <v-list-item-group>
                <v-list-item
                  v-for="contest in contests"
                  :key="contest.contest_id"
                >
                  <v-list-item-content>
                    <v-list-item-title>{{ contest.contest_name }} ({{ contest.submissions.length }} submissions)</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-list>
                        <v-list-item
                          v-for="submission in contest.submissions"
                          :key="submission.sno"
                        >
                          <v-list-item-content>
                            <v-list-item-title>{{ submission.name }} (SNO: {{ submission.sno }})</v-list-item-title>
                          </v-list-item-content>
                        </v-list-item>
                      </v-list>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const contests = ref([
  {
    contest_id: 1,
    contest_name: 'Contest 1',
    submissions: [
      {
        sno: 'SNO1',
        name: 'Name1'
      },
      {
        sno: 'SNO2',
        name: 'Name2'
      }
    ]
  }
]);
const loading = ref(true);
const error = ref(null);

const fetchContests = async () => {
  try {
    const response = await axios.get(`${backendUrl}/todayContestSubmissions`);
    contests.value = response.data;
  } catch (err) {
    error.value = err.response?.data?.error || 'An error occurred while fetching the data.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchContests();
});
</script>

<style scoped>
.v-card {
  margin-top: 20px;
}
</style>
