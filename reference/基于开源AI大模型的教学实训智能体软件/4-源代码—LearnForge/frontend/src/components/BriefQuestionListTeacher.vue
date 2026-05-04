
<template>
    <v-list>
      <v-list-item v-for="(item, index) in parsedQuestions" :key="index" class="question-item">
        <v-list-item-content>
          <v-list-item-title class="question-title">{{ item.题目 }}</v-list-item-title>
          <v-list-item-subtitle class="answer">
            <strong>答案:</strong> {{ item.答案 }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </template>
  
  <script>
  export default {
    name: 'BriefQuestionListTeacher',
    props: {
      questionsJson: {
        type: String,
        required: true
      }
    },
    computed: {
      parsedQuestions() {
        return JSON.parse(this.questionsJson);
      }
    }
  };
  </script>
  
  <style>
  .question-item {
    margin-bottom: 20px;
  }
  
  .question-title {
    font-weight: bold;
  }
  
  .answer {
    margin-top: 10px;
  }
  </style>
  