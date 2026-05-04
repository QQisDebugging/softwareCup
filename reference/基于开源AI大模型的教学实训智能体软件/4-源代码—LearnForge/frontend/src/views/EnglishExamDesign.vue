<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field label="针对什么单词出题？" v-model="keyword" outlined></v-text-field>
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
              <v-card-text class="text-body-2" style="margin-left: 5ch;" v-html="renderedMarkdown"></v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { defineComponent, ref, computed, getCurrentInstance } from 'vue';
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
      const url = `${this.$backendUrl}/api/ask`;
      let payload = `
            #你是一位资深的英语老师，现在需要你出一套单词填空题型的试卷，需要按照以下要求执行：
1. 根据${this.keyword}来出题，一共出10道题目，每道题目一个选填单词。选填单词需要根据<单词>来做【词性转换】，保证大部分[标准答案]都需要对{单词}做词性转换
2. 词性转换需要覆盖时态语态、主谓一致、动词不定式、过去分词、现在分词、名词化、副词化、形容词化等。确保每类题目最少出现一次
3. 难度要略高于【参考试题】，生成的题目不能和【参考试题】类似
4. 生成单词填空题后，需要给出【标准答案】，【标准答案】中要注明词性转换的结果
5. 根据生成的【试题】和【标准答案】逐步思考，输出对应的[试题解析]内容，输出内容尽量简洁明了

##参考以下试卷出题形式，按同样格式输出
【参考试题】 ：
// {questions}

【标准答案】：
// {answers}

【试题解析】：
// {analysis}

###按以下单词来出题
${this.keyword}:${this.keyword}
【试题】：\`XXX\`
【标准答案】：\`XXX\`
【试题解析】：\`XXX\`
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
        this.answer = 'Failed to fetch data.';
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
/* 你的样式 */
</style>