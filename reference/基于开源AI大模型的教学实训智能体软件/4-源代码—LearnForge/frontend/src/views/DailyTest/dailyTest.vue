<template>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
    <div class="daily-test-container">
        <v-container class="main-container">
            <!-- 页面标题 -->
            <v-row justify="center" class="mb-6">
                <v-col cols="12" class="text-center">
                    <h1 class="page-title">
                        <v-icon color="primary" size="32" class="mr-2">mdi-brain</v-icon>
                        每日一测
                    </h1>
                    <p class="page-subtitle">挑战今日题目，提升编程能力</p>
                </v-col>
            </v-row>

            <!-- 计时器卡片 -->
            <v-row justify="center" class="mb-4">
                <v-col cols="12" sm="8" md="6" lg="4">
                    <v-card class="timer-card" elevation="8">
                        <v-card-text class="text-center">
                            <v-icon color="success" size="24" class="mb-2">mdi-timer</v-icon>
                            <div class="timer-display">
                                <Timer></Timer>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- 题目卡片 -->
            <v-row justify="center" class="mb-4">
                <v-col cols="12" sm="10" md="8" lg="6">
                    <v-card class="question-card" elevation="12">
                        <v-card-title class="question-title">
                            <v-icon color="primary" class="mr-2">mdi-help-circle</v-icon>
                            题目 {{ currentQuestionIndex + 1 }} / {{ questions.length }}
                            <v-spacer></v-spacer>
                            <v-chip color="primary" variant="outlined" size="small">
                                {{ Math.round(((currentQuestionIndex + 1) / questions.length) * 100) }}%
                            </v-chip>
                        </v-card-title>
                        <v-divider></v-divider>
                        <v-card-text class="question-content">
                            <div class="question-text">{{ questions[currentQuestionIndex].question }}</div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- 答题区域 -->
            <v-row justify="center" class="mb-4">
                <v-col cols="12" sm="10" md="8" lg="6">
                    <v-card class="answer-card" elevation="8">
                        <v-card-title class="answer-title">
                            <v-icon color="secondary" class="mr-2">mdi-pencil</v-icon>
                            答题区域
                        </v-card-title>
                        <v-divider></v-divider>
                        <v-card-text>
                            <v-textarea
                                v-model="userAnswer"
                                label="请输入你的答案"
                                rows="4"
                                variant="outlined"
                                counter
                                clearable
                                class="answer-input"
                            ></v-textarea>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- 操作按钮组 -->
            <v-row justify="center" class="mb-4">
                <v-col cols="12" class="text-center">
                    <div class="action-buttons">
                        <v-btn-group variant="outlined" class="mb-2">
                            <v-btn 
                                @click="prevQuestion" 
                                color="primary" 
                                :disabled="currentQuestionIndex === 0"
                                prepend-icon="mdi-chevron-left"
                            >
                                上一题
                            </v-btn>
                            <v-btn 
                                @click="nextQuestion" 
                                color="primary"
                                :disabled="currentQuestionIndex === questions.length - 1"
                                append-icon="mdi-chevron-right"
                            >
                                下一题
                            </v-btn>
                        </v-btn-group>
                        
                        <v-btn
                            color="deep-purple"
                            variant="elevated"
                            size="large"
                            class="ai-button"
                            @click="dialog = true"
                        >
                            <v-icon start>mdi-robot</v-icon>
                            AI智能解答
                        </v-btn>
                    </div>
                </v-col>
            </v-row>

            <!-- AI解答对话框 -->
            <v-dialog v-model="dialog" max-width="900px" class="ai-dialog">
                <v-card class="ai-card">
                    <v-card-title class="ai-header">
                        <v-avatar color="deep-purple" class="mr-3">
                            <v-icon color="white">mdi-robot</v-icon>
                        </v-avatar>
                        <div>
                            <h3 class="ai-title">AI智能解答</h3>
                            <p class="ai-subtitle">让AI帮你理解题目</p>
                        </div>
                        <v-spacer></v-spacer>
                        <v-btn icon="mdi-close" @click="dialog = false" size="small"></v-btn>
                    </v-card-title>
                    
                    <v-divider></v-divider>
                    
                    <v-card-text class="ai-content">
                        <!-- 题目展示 -->
                        <v-card variant="outlined" class="mb-4">
                            <v-card-title class="text-h6">
                                <v-icon color="primary" class="mr-2">mdi-help-circle</v-icon>
                                题目 {{ currentQuestionIndex + 1 }}
                            </v-card-title>
                            <v-card-text>
                                <div class="question-display" ref="questionP">
                                    {{ questions[currentQuestionIndex].question }}
                                </div>
                            </v-card-text>
                        </v-card>

                        <!-- 获取解答按钮 -->
                        <div class="text-center mb-4">
                            <v-btn 
                                @click="showAssistant = true; getFigureout()" 
                                color="success" 
                                size="large"
                                :loading="isStreaming"
                                :disabled="isStreaming"
                            >
                                <v-icon start>mdi-lightbulb</v-icon>
                                {{ isStreaming ? '正在分析...' : '获取智能解答' }}
                            </v-btn>
                        </div>

                        <!-- AI回答展示 -->
                        <v-card v-if="showAssistant" class="ai-response-card" elevation="2">
                            <v-card-title class="response-title">
                                <v-icon color="success" class="mr-2">mdi-comment-text</v-icon>
                                AI解答
                            </v-card-title>
                            <v-divider></v-divider>
                            <v-card-text class="response-content">
                                <div v-if="isStreaming" class="text-center">
                                    <v-progress-circular indeterminate color="primary" class="mb-2"></v-progress-circular>
                                    <p class="text-body-2">AI正在思考中...</p>
                                </div>
                                <v-md-preview v-else :text="renderedMarkdown" class="ai-markdown"></v-md-preview>
                            </v-card-text>
                        </v-card>
                    </v-card-text>
                </v-card>
            </v-dialog>

            <!-- 提交按钮（在没有下一题时显示）-->
            <v-row v-if="currentQuestionIndex === questions.length - 1" justify="center" class="mt-6">
                <v-col cols="12" class="text-center">
                    <v-btn 
                        @click="submitTest" 
                        color="success" 
                        size="x-large"
                        class="submit-button"
                        elevation="4"
                    >
                        <v-icon start>mdi-checkbox-marked-circle</v-icon>
                        提交试卷
                    </v-btn>
                </v-col>
            </v-row>

            <!-- 答案汇总 -->
            <v-row v-if="currentQuestionIndex === questions.length - 1" justify="center" class="mt-4">
                <v-col cols="12" sm="10" md="8" lg="6">
                    <v-card class="summary-card" elevation="8">
                        <v-card-title class="summary-title">
                            <v-icon color="info" class="mr-2">mdi-clipboard-list</v-icon>
                            答案汇总
                        </v-card-title>
                        <v-divider></v-divider>
                        <v-card-text>
                            <v-list class="answer-summary">
                                <v-list-item v-for="(answer, index) in answers" :key="index" class="answer-item">
                                    <template v-slot:prepend>
                                        <v-avatar color="primary" size="small">
                                            {{ index + 1 }}
                                        </v-avatar>
                                    </template>
                                    <v-list-item-title class="answer-label">第 {{ index + 1 }} 题</v-list-item-title>
                                    <v-list-item-subtitle class="answer-content">
                                        {{ answer || '未作答' }}
                                    </v-list-item-subtitle>
                                </v-list-item>
                            </v-list>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </div>
</template>

<script>
import {  ref, computed, getCurrentInstance } from 'vue';
// import MarkdownIt from 'markdown-it';
import Timer from './Timer.vue'; // 导入自定义计时器组件
import questionsData from './questions.json'; // 导入题目数据
import axios from '@/utils/axiosConfig';
export default {
    components: {
        Timer,
    },
    setup() {
      
        const questionP = ref('');
        const instance = getCurrentInstance();
        const backendUrl = instance.appContext.config.globalProperties.$backendUrl;
        const isStreaming = ref(false);
        const aiResponse = ref("Hello, **world**! 你好！我将竭力回答你的问题");


        // const md = new MarkdownIt();
        const renderedMarkdown = computed(() => aiResponse.value);


        const getFigureout = async () => {
        
            isStreaming.value = true;
            aiResponse.value = '';
            const userQuery =  questionP.value.innerText;
                // console.log(userQuery.replace(/<[^>]+>/g, ''))
                // console.log("Sending query: ", userQuery);

            // const queryParams = new URLSearchParams({ query: userQuery }).toString();
            const url = `${backendUrl}/api/ask`;


            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: "要求使用代码简短清晰的解答这个问题,输出内容越短越好：" + userQuery })
                });

                if (!response.body) {
                    throw new Error('Failed to get readable stream.');
                }

                const reader = response.body.getReader();
                while (isStreaming.value) {
                    const { done, value } = await reader.read();
                    if (done) {
                        break;
                    }
                    aiResponse.value += new TextDecoder().decode(value);
                }
            } catch (error) {
                console.error("Failed to send query: ", error);
                aiResponse.value = "响应失败.";
            } finally {
                isStreaming.value = false;
            }
        };
    //     onMounted(() => {
    //   // 组件渲染完成后执行获取用户输入的操作
    // //   getFigureout();
    //   questionP.value = questionP.value.innerText;
    // });

    // watchEffect(() => {
    //     if (showAssistant) {
    //         renderedMarkdown.value = ''; // 每次显示编程助手时清空内容
    //         getFigureout(); // 获取解答
    //     }
    // });

        return {
            getFigureout,
            renderedMarkdown,
            questionP
        }


    },
    data() {
        return {
            currentQuestionIndex: 0, // 当前题目索引
            questions: [], // 题目数组
            userAnswer: '', // 用户答案
            answers: [], // 保存用户答案的数组
            startTime: 0, // 开始答题时间
            endTime: 0, // 结束答题时间
            dialog: false,
            notifications: false,
            sound: true,
            widgets: false,
            showAssistant: false
        };
    },
    methods: {
        getRandomQuestions() {
            // 复制题目数据
            const allQuestions = [...questionsData];
            // 随机排序题目数据
            allQuestions.sort(() => Math.random() - 0.5);
            // 选取前5个题目
            this.questions = allQuestions.slice(0, 5);
        },
        prevQuestion() {
            if (this.currentQuestionIndex > 0) {
                this.submitAnswer();
                this.currentQuestionIndex--;
                this.userAnswer = this.answers[this.currentQuestionIndex] || '';
            }
        },
        nextQuestion() {
            if (this.currentQuestionIndex < this.questions.length - 1) {
                this.submitAnswer();
                this.currentQuestionIndex++;
                this.userAnswer = this.answers[this.currentQuestionIndex] || '';
            } else {
                this.submitAnswer();
            }
        },
        submitAnswer() {
            this.answers[this.currentQuestionIndex] = this.userAnswer;
        },
        async pushStudyTime(addtime) {
            try {
                const username = localStorage.getItem('username');

                const response = await axios.post(`${this.$backendUrl}/pushStudyTime`, {
                    username: username,
                    studytime: addtime
                });

                // 处理响应
                console.log(response.data);

                // 根据响应处理逻辑
            } catch (error) {
                // 处理错误
                console.error('发生错误：', error);
            }
        },
        submitTest() {
            this.submitAnswer();



            //         const totalQuestions = this.questions.length;
            //   const answeredQuestions = this.answers.filter(answer => answer !== '').length;
            //   if (answeredQuestions < totalQuestions) {
            //     // 如果还有未回答的题目，显示 Snackbar 提示用户
            //     this.$refs.snackbar.open();
            //     return; // 终止方法执行，不进行路由跳转
            //   }


            this.endTime = new Date().getTime();
            const timeUsed = Math.floor((this.endTime - this.startTime) / 1000 / 60);
            console.log('答题所用时间：', timeUsed, '分钟');
            this.pushStudyTime(timeUsed);


            this.$router.push({
                name: 'done',
                params: { timeSpent: timeUsed }
            });
        },
        handleTimeout() {

        },
    },
    created() {
        this.startTime = new Date().getTime();
        this.getRandomQuestions();
    },
};
</script>

<style scoped>
.daily-test-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px 0;
}

.main-container {
    max-width: 1200px;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    margin-bottom: 8px;
}

.page-subtitle {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.9);
    margin-bottom: 0;
}

.timer-card {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    border-radius: 16px;
    color: white;
    transition: all 0.3s ease;
}

.timer-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.timer-display {
    font-size: 1.2rem;
    font-weight: 600;
}

.question-card {
    background: white;
    border-radius: 16px;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.question-card:hover {
    transform: translateY(-3px);
    border-color: #667eea;
}

.question-title {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 16px 16px 0 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.question-content {
    padding: 24px;
}

.question-text {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #333;
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.answer-card {
    background: white;
    border-radius: 16px;
    transition: all 0.3s ease;
}

.answer-card:hover {
    transform: translateY(-3px);
}

.answer-title {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
    color: white;
    padding: 20px;
    border-radius: 16px 16px 0 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.answer-input {
    margin-top: 16px;
}

.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 16px;
    align-items: center;
}

.ai-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.ai-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.ai-dialog .v-card {
    border-radius: 16px;
}

.ai-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
}

.ai-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 24px;
}

.ai-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
    color: white;
}

.ai-subtitle {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.8);
    margin: 0;
}

.ai-content {
    padding: 24px;
}

.question-display {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #333;
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.ai-response-card {
    border-radius: 12px;
    border: 2px solid #e8f5e8;
    background: #f8fff8;
}

.response-title {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    color: white;
    padding: 16px;
    font-size: 1.1rem;
    font-weight: 600;
}

.response-content {
    padding: 20px;
}

.ai-markdown {
    background: white;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #e0e0e0;
}

.submit-button {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    color: white;
    border-radius: 12px;
    padding: 16px 32px;
    font-weight: 600;
    font-size: 1.1rem;
    transition: all 0.3s ease;
}

.submit-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(67, 233, 123, 0.4);
}

.summary-card {
    background: white;
    border-radius: 16px;
    transition: all 0.3s ease;
}

.summary-title {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 16px 16px 0 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.answer-summary {
    padding: 8px 0;
}

.answer-item {
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
}

.answer-item:last-child {
    border-bottom: none;
}

.answer-label {
    font-weight: 600;
    color: #333;
}

.answer-content {
    color: #666;
    font-size: 0.9rem;
    margin-top: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
    }
    
    .action-buttons {
        flex-direction: column;
        gap: 12px;
    }
    
    .ai-content {
        padding: 16px;
    }
    
    .question-content, .answer-card .v-card-text {
        padding: 16px;
    }
}

/* 动画效果 */
.v-card {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.v-btn {
    transition: all 0.3s ease;
}

.v-btn:hover {
    transform: translateY(-2px);
}

/* 加载动画 */
.v-progress-circular {
    animation: pulse 2s ease-in-out infinite alternate;
}

@keyframes pulse {
    0% {
        opacity: 1;
    }
    100% {
        opacity: 0.5;
    }
}
</style>