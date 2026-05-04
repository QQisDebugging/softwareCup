<template>
    <v-app>
      <v-main>
        <v-container fluid>
          <v-row>
            <v-col cols="12" md="12">
              <RankCompoent></RankCompoent>
            </v-col>
            <!-- <v-col cols="12" md="">
              <v-card>
                <v-card-title>
                  Card 2
                </v-card-title>
                <v-card-text>
                  Some text for card 2.
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>
                  Card 3
                </v-card-title>
                <v-card-text>
                  Some text for card 3.
                </v-card-text>
              </v-card>
            </v-col> -->
          </v-row>
          <!-- Add more rows and cards as needed -->
        </v-container>
      </v-main>
    </v-app>
  </template>
  
  <script>
  import RankCompoent from './StudentList.vue';
  export default {
    name: 'user',
    components: {
        RankCompoent
  }
  }
  </script>
  
  <style>
  /* Add any custom styles here */
  </style>
  