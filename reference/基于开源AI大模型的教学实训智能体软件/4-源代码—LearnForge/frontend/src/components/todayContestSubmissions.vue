<template>
    

          <v-card border flat>
            <v-card-title>
              <span class="text-h5">今日作业提交</span>
            </v-card-title>
            <v-card-text>
              <v-alert
                v-if="!contests.length"
                type="success"
              >
                没有提交
              </v-alert>
              <v-list v-if="contests.length">
                <v-list-item-group>
                  <v-list-item
                    v-for="contest in contests"
                    :key="contest.contest_id"
                  >
                    <v-list-item-content>
                      <v-list-item-title>{{ contest.contest_name }}<v-chip color="primary" text-color="white" class="ml-2">
                          {{ contest.submissions.length }} 提交
                        </v-chip></v-list-item-title>
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
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  import { backendUrl } from '@/main';
  const contests = ref([]);
  const loading = ref(true);
  const error = ref(null);
  
  const fetchContests = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/todayContestSubmissions`);
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
  