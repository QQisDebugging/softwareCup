<template>
    
 
          <v-card border flat>
            <v-card-title>
              <span class="text-h5">今日实训提交</span>
            </v-card-title>
            <v-card-text>
              <v-alert
                v-if="!assignments.length"
                type="info"
              >
                没有提交
              </v-alert>
              <v-list v-if="assignments.length">
                <v-list-item-group>
                  <v-list-item
                    v-for="assignment in assignments"
                    :key="assignment.assignment_id"
                  >
                    <v-list-item-content>
                      <v-list-item-title>{{ assignment.assignment_name }}
                         <v-chip color="primary" text-color="white" class="ml-2">
                          {{ assignment.submission_count }} 提交
                        </v-chip></v-list-item-title>
                      <v-list-item-subtitle>
                        <v-list>
                          <v-list-item
                            v-for="submission in assignment.submissions"
                            :key="submission.sno"
                          >
                            <v-list-item-content>
                              <v-list-item-title>{{ submission.name }} (SNO: {{ submission.sno }})</v-list-item-title>
                              <!-- <v-list-item-subtitle>ClassID: {{ submission.ClassID }}</v-list-item-subtitle> -->
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
  
  const assignments = ref([]);
  const loading = ref(true);
  const error = ref(null);
  
  const fetchAssignments = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/todayAssignments`);
      assignments.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.error || 'An error occurred while fetching the data.';
    } finally {
      loading.value = false;
    }
  };
  
  onMounted(() => {
    fetchAssignments();
  });
  </script>
  
  <style scoped>
  .v-card {
    margin-top: 20px;
  }
  </style>
  