<!-- src/components/TrueFalseQuestionList.vue -->
<template>
    <v-list>
      <v-list-item v-for="(item, index) in parsedQuestions" :key="index" class="question-item">
        <v-list-item-content>
          <v-list-item-title class="question-title">{{ item.题目 }}</v-list-item-title>
          <v-radio-group v-model="selectedAnswers[index]" class="answer-options" row>
            <v-radio
              label="对"
              :value="0"
            ></v-radio>
            <v-radio
              label="错"
              :value="1"
            ></v-radio>
          </v-radio-group>
          <v-alert type="info" class="correct-answer">
            正确答案: {{ item.答案 == "0" ? "对" : "错" }}
          </v-alert>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </template>
  
  <script>
  export default {
    name: 'JudgeQuestionListTeacher',
    props: {
      questionsJson: {
        type: String,
        required: true
      }
    },
    data() {
      return {
        selectedAnswers: {}
      };
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
  
  .answer-options {
    margin-top: 10px;
  }
  
  .correct-answer {
    margin-top: 10px;
  }
  </style>
  