<template>
    

          <v-card border flat>
            <v-card-title>
              <span class="text-h5">今日任务提交</span>
            </v-card-title>
            <v-card-text>
              <v-alert
                v-if="!activities.length && !loading"
                type="red"
              >
                没有提交
              </v-alert>
              <v-list v-if="activities.length">
                <v-list-item-group>
                  <v-list-item
                    v-for="activity in activities"
                    :key="activity.activity_id"
                  >
                    <v-list-item-content>
                      <v-list-item-title>
                        {{ activity.activity_name }}
                        <v-chip color="primary" text-color="white" class="ml-2">
                          {{ activity.submission_count }} 提交
                        </v-chip>
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        <v-list dense>
                          <v-list-item-group>
                            <v-list-item
                              v-for="submission in activity.submissions"
                              :key="submission.sno"
                            >
                              <v-list-item-content>
                                <v-list-item-title>{{ submission.name }} (SNO: {{ submission.sno }})</v-list-item-title>
                                <!-- <v-list-item-subtitle>Class ID: {{ submission.ClassID }}</v-list-item-subtitle> -->
                              </v-list-item-content>
                            </v-list-item>
                          </v-list-item-group>
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
  
  const activities = ref([]);
  const loading = ref(true);
  const error = ref(null);
  
  const fetchActivities = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/todayActivities`);
      activities.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.error || 'An error occurred while fetching the data.';
    } finally {
      loading.value = false;
    }
  };
  
  onMounted(() => {
    fetchActivities();
  });
  </script>
  
  <style scoped>
  .v-card {
    margin-top: 20px;
  }
  .v-chip {
    margin-left: 8px;
  }
  </style>
  