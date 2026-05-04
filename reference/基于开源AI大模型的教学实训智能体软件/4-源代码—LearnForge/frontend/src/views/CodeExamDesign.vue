<template>
  <div>
    <link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
    <v-app>
      <v-main>
        <v-container>
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field label="针对什么知识点出题，动态规划？贪心算法？" v-model="keyword" outlined></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-btn color="primary" @click="getAnswer" :disabled="isFetching">出题</v-btn>
              <v-btn color="success" @click="downloadDoc" :disabled="!answer">下载 Word 文档</v-btn>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-card>
                <v-card-title class="headline">题目</v-card-title>
                <v-card-text>
                  <div class="markdown-body" v-html="renderedMarkdown"></div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-main>
    </v-app>
  </div>
</template>

<script>
import { defineComponent, getCurrentInstance, ref, computed } from 'vue';
import MarkdownIt from 'markdown-it';
import { Document, Packer, Paragraph, TextRun } from 'docx';

export default defineComponent({
  setup() {
    const instance = getCurrentInstance();
    const backendUrl = instance.appContext.config.globalProperties.$backendUrl;

  },
  data() {
    return {
      keyword: '',
      answer: '',
      isFetching: false,
      md: new MarkdownIt()
    };
  },
  computed: {
    renderedMarkdown() {
      return this.md.render(this.answer);
    }
  },
  methods: {
    async getAnswer() {
      if (!this.keyword) {
        alert('请输入一个关键词');
        return;
      }

      this.isFetching = true;
      this.answer = '';
      const url = `${this.$backendUrl}/api/spark/ask`;
      let payload = `
           #你是一位资深的计算机老师，现在需要你出一套代码填空题型的试卷，需要按照以下要求执行：
       
1. 根据${this.keyword}来出题，一共出4道题目，每道题目一个待补充完整的代码
2. 生成代码填空题后，需要给出【标准答案】，【标准答案】中要注明词性转换的结果
3. 根据生成的【试题】和【标准答案】逐步思考，输出对应的[试题解析]内容，输出内容尽量简洁明了

##参考以下试卷出题形式，按同样格式输出
【参考试题】 ：


【标准答案】：


【试题解析】：

请注意以标准markdown格式输出
            `

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: payload })
        });
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          this.answer += decoder.decode(value, { stream: true });
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        this.answer = '获取数据失败.';
      } finally {
        this.isFetching = false;
      }
    },
    downloadDoc() {
      const doc = new Document({
        sections: [{
          children: [
            new Paragraph({
              children: [
                new TextRun("题目内容:"),
                new TextRun({
                  text: this.answer,
                  bold: true,
                }),
              ],
            }),
          ],
        }],
      });

      Packer.toBlob(doc).then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "GeneratedDocument.docx";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
    }
  }
})
</script>

<style scoped>
/* 样式 */
</style>