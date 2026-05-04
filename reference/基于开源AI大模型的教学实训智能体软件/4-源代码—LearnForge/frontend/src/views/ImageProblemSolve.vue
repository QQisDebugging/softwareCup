<template>
    <v-container>
        <v-row>
            <v-col cols="12" md="6">
                <v-card class="upload-card">
                    <v-card-title class="d-flex align-center">
                        <v-icon class="mr-2">mdi-camera</v-icon>
                        上传题目照片
                    </v-card-title>
                    <v-card-text>
                        <div class="upload-section">
                            <!-- 拍照按钮 -->
                            <v-btn 
                                color="primary" 
                                size="large" 
                                @click="openCamera"
                                class="mb-3 mr-3"
                                :disabled="isProcessing"
                            >
                                <v-icon class="mr-2">mdi-camera</v-icon>
                                拍照
                            </v-btn>
                            
                            <!-- 选择文件按钮 -->
                            <label class="custom-file-upload">
                                <input 
                                    type="file" 
                                    accept="image/*" 
                                    @change="onFileChange"
                                    :disabled="isProcessing"
                                />
                                <v-icon class="mr-2">mdi-file-image</v-icon>
                                选择图片
                            </label>
                            
                            <!-- 图片预览 -->
                            <div v-if="imageUrl" class="image-preview-container">
                                <v-img 
                                    :src="imageUrl" 
                                    max-width="100%" 
                                    class="mt-4 image-preview"
                                    @click="enlargeImage"
                                ></v-img>
                                <v-btn 
                                    color="error" 
                                    size="small" 
                                    @click="clearImage"
                                    class="mt-2"
                                >
                                    <v-icon>mdi-delete</v-icon>
                                    清除图片
                                </v-btn>
                            </div>
                            
                            <!-- 文件大小提示 -->
                            <v-alert 
                                v-if="!imageUrl" 
                                type="info" 
                                class="mt-3"
                                density="compact"
                            >
                                <v-icon>mdi-information</v-icon>
                                请上传清晰的题目照片，文件大小不超过3MB
                            </v-alert>

                            <!-- 新增：API配置按钮 -->
                            <v-btn 
                                color="warning" 
                                size="small" 
                                @click="showApiConfig"
                                class="mt-2"
                                variant="outlined"
                            >
                                <v-icon class="mr-1">mdi-cog</v-icon>
                                API配置
                            </v-btn>
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>
            
            <v-col cols="12" md="6">
                <v-card class="result-card">
                    <v-card-title class="d-flex align-center">
                        <v-icon class="mr-2">mdi-lightbulb</v-icon>
                        解题结果
                        <!-- 显示当前使用的API -->
                        <v-spacer></v-spacer>
                        <v-chip 
                            v-if="currentApiUsed" 
                            :color="currentApiUsed.includes('科大讯飞') ? 'primary' : 'warning'"
                            size="small"
                        >
                            {{ currentApiUsed }}
                        </v-chip>
                    </v-card-title>
                    <v-card-actions>
                        <v-btn 
                            color="primary" 
                            @click="fetchApiData" 
                            :disabled="!imageUrl || isProcessing"
                            :loading="isProcessing"
                        >
                            <v-icon class="mr-2">mdi-eye</v-icon>
                            {{ isProcessing ? '识别中...' : '开始识别' }}
                        </v-btn>
                        <v-btn 
                            color="success" 
                            v-if="isDone && !isGettingAnswer" 
                            @click="getAnswer"
                            :loading="isGettingAnswer"
                        >
                            <v-icon class="mr-2">mdi-robot</v-icon>
                            AI解答
                        </v-btn>
                        <v-btn 
                            color="info" 
                            v-if="isDone" 
                            @click="toggleDrawer"
                        >
                            <v-icon class="mr-2">mdi-book-open</v-icon>
                            知识点推荐
                        </v-btn>
                    </v-card-actions>
                    <v-card-text class="scrollable-card-text">
                        <div v-if="isProcessing" class="text-center">
                            <v-progress-circular 
                                indeterminate 
                                color="primary"
                                size="64"
                            ></v-progress-circular>
                            <p class="mt-3">正在识别题目内容...</p>
                        </div>
                        <div v-else-if="isGettingAnswer" class="text-center">
                            <v-progress-circular 
                                indeterminate 
                                color="success"
                                size="64"
                            ></v-progress-circular>
                            <p class="mt-3">AI正在分析解答...</p>
                        </div>
                        <v-md-preview v-else :text="apiResponse" class="result-content"></v-md-preview>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <!-- 拍照对话框 -->
        <v-dialog v-model="cameraDialog" max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">拍照</span>
                    <v-spacer></v-spacer>
                    <v-btn icon @click="cameraDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>
                <v-card-text>
                    <div class="camera-container">
                        <video ref="video" autoplay playsinline class="camera-video"></video>
                        <canvas ref="canvas" style="display: none;"></canvas>
                    </div>
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" @click="capturePhoto">
                        <v-icon class="mr-2">mdi-camera</v-icon>
                        拍照
                    </v-btn>
                    <v-btn color="secondary" @click="closeCameraDialog">
                        取消
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- 新增：API配置对话框 -->
        <v-dialog v-model="apiConfigDialog" max-width="800px">
            <v-card>
                <v-card-title>
                    <span class="headline">图像识别API配置</span>
                    <v-spacer></v-spacer>
                    <v-btn icon @click="apiConfigDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>
                <v-card-text>
                    <v-row>
                        <v-col cols="12">
                            <v-alert type="info" density="compact">
                                <v-icon>mdi-information</v-icon>
                                配置多个API可以提高识别成功率，系统会按优先级自动选择可用的API
                            </v-alert>
                        </v-col>
                    </v-row>
                    
                    <v-row v-if="apiStatus">
                        <v-col cols="12">
                            <h3 class="mb-3">API状态检查</h3>
                            <v-list>
                                <v-list-item 
                                    v-for="(status, apiName) in apiStatus" 
                                    :key="apiName"
                                    :prepend-icon="status.enabled ? 'mdi-check-circle' : 'mdi-cancel'"
                                    :class="{'text-success': status.enabled, 'text-error': !status.enabled}"
                                >
                                    <v-list-item-title>{{ status.name }}</v-list-item-title>
                                    <v-list-item-subtitle>
                                        优先级: {{ status.priority }} | 状态: {{ status.status }}
                                    </v-list-item-subtitle>
                                    <template v-slot:append>
                                        <v-switch
                                            v-model="status.enabled"
                                            @update:model-value="updateApiConfig(apiName, 'enabled', $event)"
                                            color="primary"
                                        ></v-switch>
                                    </template>
                                </v-list-item>
                            </v-list>
                        </v-col>
                    </v-row>
                    
                    <v-row>
                        <v-col cols="12">
                            <h3 class="mb-3">API说明</h3>
                            <v-expansion-panels>
                                <v-expansion-panel>
                                    <v-expansion-panel-title>
                                        <v-icon class="mr-2">mdi-star</v-icon>
                                        科大讯飞星火 (推荐)
                                    </v-expansion-panel-title>
                                    <v-expansion-panel-text>
                                        <p>• 专门的图像理解API，识别精度高</p>
                                        <p>• 支持复杂题目的理解和分析</p>
                                        <p>• 目前可能存在连接问题</p>
                                    </v-expansion-panel-text>
                                </v-expansion-panel>
                                
                                <v-expansion-panel>
                                    <v-expansion-panel-title>
                                        <v-icon class="mr-2">mdi-eye</v-icon>
                                        百度AI图像识别
                                    </v-expansion-panel-title>
                                    <v-expansion-panel-text>
                                        <p>• 稳定的图像识别服务</p>
                                        <p>• 支持OCR文字识别</p>
                                        <p>• 适合处理清晰的文字图片</p>
                                    </v-expansion-panel-text>
                                </v-expansion-panel>
                                
                                <v-expansion-panel>
                                    <v-expansion-panel-title>
                                        <v-icon class="mr-2">mdi-cloud</v-icon>
                                        通用OCR+AI解答
                                    </v-expansion-panel-title>
                                    <v-expansion-panel-text>
                                        <p>• 使用OCR识别文字后由AI解答</p>
                                        <p>• 适合纯文字题目</p>
                                        <p>• 备用方案，保证基本功能</p>
                                    </v-expansion-panel-text>
                                </v-expansion-panel>
                            </v-expansion-panels>
                        </v-col>
                    </v-row>
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" @click="refreshApiStatus">
                        <v-icon class="mr-2">mdi-refresh</v-icon>
                        刷新状态
                    </v-btn>
                    <v-spacer></v-spacer>
                    <v-btn color="success" @click="saveApiConfig">
                        <v-icon class="mr-2">mdi-content-save</v-icon>
                        保存配置
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- 图片放大对话框 -->
        <v-dialog v-model="imageDialog" max-width="90%">
            <v-card>
                <v-card-title>
                    <span class="headline">图片预览</span>
                    <v-spacer></v-spacer>
                    <v-btn icon @click="imageDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>
                <v-card-text>
                    <v-img :src="imageUrl" max-width="100%"></v-img>
                </v-card-text>
            </v-card>
        </v-dialog>

        <!-- 知识点推荐侧边栏 -->
        <v-navigation-drawer v-model="drawer" location="right" temporary width="500">
            <v-card>
                <v-card-title class="d-flex align-center">
                    <v-icon class="mr-2">mdi-school</v-icon>
                    推荐知识点
                </v-card-title>
                <v-card-text>
                    <div v-if="!hasFetchedKnowledgePoints" class="text-center">
                        <v-progress-circular 
                            indeterminate 
                            color="primary"
                            size="48"
                        ></v-progress-circular>
                        <p class="mt-3">正在推荐相关知识点...</p>
                    </div>
                    <v-row v-else>
                        <v-col 
                            v-for="(item, index) in recommendedKnowledgePoints" 
                            :key="index" 
                            cols="12" 
                            class="mb-3"
                        >
                            <v-card class="knowledge-card" @click="navigateTo(item.video_url)">
                                <v-row no-gutters>
                                    <v-col cols="4">
                                        <v-img 
                                            :src="item.cover_url" 
                                            :alt="item.title"
                                            height="80"
                                            cover
                                        ></v-img>
                                    </v-col>
                                    <v-col cols="8">
                                        <v-card-text class="pa-2">
                                            <div class="text-subtitle-2 font-weight-bold">
                                                {{ item.title }}
                                            </div>
                                        </v-card-text>
                                    </v-col>
                                </v-row>
                            </v-card>
                        </v-col>
                    </v-row>
                </v-card-text>
            </v-card>
        </v-navigation-drawer>
    </v-container>
</template>

<script>
import axios from 'axios';
import { backendUrl } from '@/main';

export default {
    data() {
        return {
            image: null,
            imageUrl: null,
            apiResponse: '点击"开始识别"按钮上传图片并开始解题',
            isDone: false,
            isProcessing: false,
            isGettingAnswer: false,
            realcontent: '',
            questionList: [],
            drawer: false,
            cameraDialog: false,
            imageDialog: false,
            apiConfigDialog: false,
            currentApiUsed: '',
            apiStatus: null,
            recommendedKnowledgePoints: [],
            hasFetchedKnowledgePoints: false,
            cameraStream: null,
        };
    },
    methods: {
        // 打开相机
        async openCamera() {
            this.cameraDialog = true;
            this.$nextTick(async () => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ 
                        video: { 
                            facingMode: 'environment' // 使用后置摄像头
                        } 
                    });
                    this.cameraStream = stream;
                    this.$refs.video.srcObject = stream;
                } catch (error) {
                    console.error('无法访问摄像头:', error);
                    this.$toast.error('无法访问摄像头，请检查权限设置');
                    this.cameraDialog = false;
                }
            });
        },

        // 拍照
        capturePhoto() {
            const video = this.$refs.video;
            const canvas = this.$refs.canvas;
            const context = canvas.getContext('2d');
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            context.drawImage(video, 0, 0);
            
            canvas.toBlob((blob) => {
                this.image = blob;
                this.imageUrl = URL.createObjectURL(blob);
                this.prepareQuestionList(blob);
                this.closeCameraDialog();
            }, 'image/jpeg', 0.8);
        },

        // 关闭相机对话框
        closeCameraDialog() {
            if (this.cameraStream) {
                this.cameraStream.getTracks().forEach(track => track.stop());
                this.cameraStream = null;
            }
            this.cameraDialog = false;
        },

        // 准备问题列表（从文件或拍照）
        prepareQuestionList(file) {
            const reader = new FileReader();
            reader.onload = () => {
                const base64Image = reader.result.split(',')[1];
                this.questionList = [{
                    "role": "user",
                    "content": base64Image,
                    "content_type": "image"
                }];
            };
            reader.readAsDataURL(file);
        },

        // 文件选择处理
        onFileChange(event) {
            const file = event.target.files[0];
            const maxSizeInMB = 3;
            
            if (file) {
                const fileSizeInMB = file.size / (1024 * 1024);
                
                if (fileSizeInMB > maxSizeInMB) {
                    this.$toast.error(`文件大小超过 ${maxSizeInMB}MB，请选择较小的文件`);
                    event.target.value = '';
                    return;
                }

                this.image = file;
                this.imageUrl = URL.createObjectURL(file);
                this.prepareQuestionList(file);
            } else {
                this.clearImage();
            }
        },

        // 清除图片
        clearImage() {
            this.image = null;
            this.imageUrl = null;
            this.questionList = [];
            this.isDone = false;
            this.apiResponse = '点击"开始识别"按钮上传图片并开始解题';
        },

        // 放大图片
        enlargeImage() {
            this.imageDialog = true;
        },

        // 获取API数据
        async fetchApiData() {
            if (!this.image) {
                this.$toast.warning('请先上传图片');
                return;
            }

            this.isProcessing = true;
            this.apiResponse = '';
            this.currentApiUsed = '';
            this.questionList.push({ "role": "user", "content": "识别文字并输出" });

            const formData = new FormData();
            formData.append("image", this.image);
            formData.append("question", JSON.stringify(this.questionList));
            
            try {
                const response = await axios.post(`${this.$backendUrl}/api/imageUploadSolve`, formData);
                
                if (response.data.success) {
                    this.realcontent = response.data.message;
                    this.isDone = true;
                    this.apiResponse = this.realcontent;
                    this.currentApiUsed = response.data.api_used;
                    this.$toast.success('图片识别成功！');
                } else {
                    this.apiResponse = response.data.message || '识别失败，请重试';
                    this.currentApiUsed = response.data.api_used || '未知';
                    this.$toast.error('识别失败，请重试');
                }
            } catch (error) {
                this.apiResponse = '识别失败，请重试';
                this.currentApiUsed = '错误';
                this.$toast.error('识别失败，请重试');
                console.error(error);
            } finally {
                this.isProcessing = false;
            }
        },

        // 获取AI解答
        async getAnswer() {
            if (!this.realcontent) {
                this.$toast.warning('请先识别题目');
                return;
            }

            this.isGettingAnswer = true;
            this.apiResponse = "";
            
            const payload = `
                你是一个专业的学习助手。请仔细分析以下题目并给出详细解答：
                
                题目内容：${this.realcontent}
                
                请按照以下格式回答：
                1. 题目分析
                2. 解题思路
                3. 详细步骤
                4. 最终答案
                
                请确保解答准确、详细、易懂。
            `;
            
            try {
                const response = await fetch(`${this.$backendUrl}/api/spark/ask`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: payload })
                });
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    this.apiResponse += decoder.decode(value, { stream: true });
                }
                
                this.$toast.success('AI解答完成！');
            } catch (error) {
                console.error('Error fetching data:', error);
                this.apiResponse = '获取AI解答失败，请重试';
                this.$toast.error('获取AI解答失败，请重试');
            } finally {
                this.isGettingAnswer = false;
            }
        },

        // 切换知识点推荐侧边栏
        toggleDrawer() {
            this.drawer = !this.drawer;
            if (this.drawer && !this.hasFetchedKnowledgePoints) {
                this.recommendKnowledgePoints();
            }
        },

        // 推荐知识点
        async recommendKnowledgePoints() {
            if (!this.realcontent) {
                this.$toast.warning('请先识别题目');
                return;
            }

            try {
                const response = await axios.post(`${backendUrl}/getRecommendKnowledgePoints`, {
                    content: this.realcontent
                });
                
                this.recommendedKnowledgePoints = response.data.videos || [];
                this.hasFetchedKnowledgePoints = true;
                
                if (this.recommendedKnowledgePoints.length === 0) {
                    this.$toast.info('暂无相关知识点推荐');
                }
            } catch (error) {
                console.error('Error fetching knowledge points:', error);
                this.$toast.error('获取知识点推荐失败');
            }
        },

        // 导航到外部链接
        navigateTo(url) {
            window.open(url, '_blank');
        },

        // 新增：显示API配置
        async showApiConfig() {
            this.apiConfigDialog = true;
            await this.refreshApiStatus();
        },

        // 新增：刷新API状态
        async refreshApiStatus() {
            try {
                const response = await axios.get(`${this.$backendUrl}/api/imageUploadSolve/status`);
                this.apiStatus = response.data;
            } catch (error) {
                console.error('获取API状态失败:', error);
                this.$toast.error('获取API状态失败');
            }
        },

        // 新增：更新API配置
        async updateApiConfig(apiName, field, value) {
            try {
                const config = {
                    [apiName]: {
                        [field]: value
                    }
                };
                
                await axios.post(`${this.$backendUrl}/api/imageUploadSolve/config`, config);
                this.$toast.success('配置更新成功');
            } catch (error) {
                console.error('更新API配置失败:', error);
                this.$toast.error('更新API配置失败');
            }
        },

        // 新增：保存API配置
        async saveApiConfig() {
            try {
                this.$toast.success('API配置已保存');
                this.apiConfigDialog = false;
            } catch (error) {
                console.error('保存API配置失败:', error);
                this.$toast.error('保存API配置失败');
            }
        },
    },

    // 组件销毁时清理资源
    beforeUnmount() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
        }
        if (this.imageUrl) {
            URL.revokeObjectURL(this.imageUrl);
        }
    }
};
</script>

<style scoped>
.upload-card, .result-card {
    height: 100%;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.upload-section {
    text-align: center;
}

.custom-file-upload {
    display: inline-block;
    padding: 12px 24px;
    cursor: pointer;
    background-color: #2196F3;
    color: white;
    font-size: 16px;
    font-weight: 500;
    border-radius: 8px;
    text-align: center;
    transition: all 0.3s ease;
    margin-bottom: 16px;
}

.custom-file-upload:hover {
    background-color: #1976D2;
    transform: translateY(-2px);
}

.custom-file-upload input[type="file"] {
    display: none;
}

.image-preview-container {
    margin-top: 16px;
}

.image-preview {
    border-radius: 8px;
    cursor: pointer;
    border: 2px solid #e0e0e0;
    transition: all 0.3s ease;
}

.image-preview:hover {
    border-color: #2196F3;
    transform: scale(1.02);
}

.scrollable-card-text {
    max-height: 600px;
    overflow-y: auto;
    padding: 16px;
}

.result-content {
    font-size: 14px;
    line-height: 1.6;
}

.camera-container {
    text-align: center;
}

.camera-video {
    width: 100%;
    max-width: 400px;
    height: 300px;
    border-radius: 8px;
    background-color: #f5f5f5;
}

.knowledge-card {
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 8px;
}

.knowledge-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 移动端适配 */
@media (max-width: 768px) {
    .upload-section {
        padding: 16px;
    }
    
    .custom-file-upload {
        display: block;
        margin: 8px auto;
        width: 80%;
    }
    
    .camera-video {
        height: 200px;
    }
    
    .scrollable-card-text {
        max-height: 400px;
    }
}

/* 响应式设计 */
@media (max-width: 960px) {
    .v-col {
        padding: 8px;
    }
}
</style>
