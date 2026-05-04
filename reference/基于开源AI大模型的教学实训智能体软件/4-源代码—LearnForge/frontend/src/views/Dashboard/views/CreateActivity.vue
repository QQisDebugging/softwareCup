<template>
    <v-app>
        <v-main>
            <v-container>
                <v-card>
                    <v-card-title>创建任务</v-card-title>
                    <v-card-text>
                        <v-form ref="form" v-model="valid" lazy-validation>
                            <v-text-field v-model="activity_name" label="任务名称" :rules="[rules.required]"
                                required></v-text-field>
                            <v-select v-model="selectedClasses" :items="classes" item-title="ClassName"
                                item-value="ClassID" label="选择班级" multiple chips dense></v-select>

                            <v-textarea v-model="description" label="题目" auto-grow></v-textarea>
                           
                            <v-btn color="primary" @click="showAiDialog = true">
                                AI辅助出题
                            </v-btn>
                            <v-btn :disabled="!valid" color="success" @click="submitForm">
                                提交
                            </v-btn>
                        </v-form>
                    </v-card-text>
                </v-card>
            </v-container>
        </v-main>

        <!-- AI辅助出题对话框 -->
        <v-dialog v-model="showAiDialog" max-width="600px">
            <v-card>
                <v-card-title class="headline">AI辅助出题</v-card-title>
                <v-card-text>
                    <v-text-field v-model="requirement" label="题目要求" auto-grow required></v-text-field>
                    <v-btn color="primary" @click="generateQuestion">
                        生成题目
                    </v-btn>
                    <v-md-preview :text="aiGeneratedQuestion"></v-md-preview>
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" @click="pasteAiQuestion">
                        粘贴到题目输入框
                    </v-btn>
                    <v-spacer></v-spacer>
                    <v-btn color="secondary" @click="showAiDialog = false">
                        关闭
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-app>
</template>

<script>
import axios from '@/utils/axiosConfig';
import { ref } from 'vue';
export default {
    data() {
        return {
            valid: false,
            showAiDialog: false,
            activity_name: '',
            creator_tno: localStorage.getItem('username'),
            description: '',
            date: new Date().toISOString(),
            created_date: new Date().toISOString().substr(0, 10),
            selectedClasses: [],
            classes: [],
            requirement: '',
            aiGeneratedQuestion: ref(''),
            isStreaming:false,
            rules: {
                required: value => !!value || '此字段为必填项',
                number: value => !isNaN(value) || '必须是数字'
            }
        };
    },
    mounted() {
        this.getClasses(); // 获取班级列表
    },
    methods: {
        getClasses() {
            axios.get(`${this.$backendUrl}/api/getClasses`)
                .then(response => {
                    this.classes = response.data; // 设置班级列表
                    console.log(response.data);
                })
                .catch(error => {
                    console.error('获取班级列表失败', error);
                });
        },
        pasteAiQuestion() {
            this.description = this.aiGeneratedQuestion;
            this.showAiDialog = false;
        },
        submitForm() {
            if (this.$refs.form.validate()) {
                axios.post(`${this.$backendUrl}/api/createActivity`, {
                    activity_name: this.activity_name,
                    creator_tno: this.creator_tno,
                    description: this.description,
                    created_date: this.created_date,
                    selectedClasses: this.selectedClasses // 将选定的班级列表传递到后端
                })
                    .then(response => {
                        alert('任务创建成功');
                        this.$refs.form.reset();
                    })
                    .catch(error => {
                        alert(`错误: ${error.response.data.error}`);
                    });
            }
        },
        async generateQuestion() {
 

            this.isStreaming = true;
            this.aiGeneratedQuestion = '';

            const url = `${this.$backendUrl}/api/spark/generateProblem`;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ demand:this.requirement})
                });

                if (!response.body) {
                    throw new Error('Failed to get readable stream.');
                }

                const reader = response.body.getReader();
                while (this.isStreaming) {
                    const { done, value } = await reader.read();
                    if (done) {
                        break;
                    }
                    this.aiGeneratedQuestion += new TextDecoder().decode(value);
                    console.log(this.aiGeneratedQuestion)
                }
                console.log('AI响应:', this.aiGeneratedQuestion); // 添加日志
            } catch (error) {
                console.error("Failed to send query: ", error);
                this.aiGeneratedQuestion = "响应失败.";
            } finally {
                this.isStreaming = false;
            }

        }
    }
};
</script>

<style scoped>
/* 添加自定义样式（如果有） */
</style>
