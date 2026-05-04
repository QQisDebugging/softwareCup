<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card class="demo-card">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-information</v-icon>
            拍照答题功能使用指南
          </v-card-title>
          <v-card-text>
            <h3>🎯 功能特色</h3>
            <v-list>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>📸 多种拍照方式</v-list-item-title>
                  <v-list-item-subtitle>支持直接拍照和文件上传两种方式</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>🤖 AI智能识别</v-list-item-title>
                  <v-list-item-subtitle>使用讯飞API进行图像识别和文字提取</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>💡 智能解答</v-list-item-title>
                  <v-list-item-subtitle>AI分析题目并提供详细解答步骤</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>📚 知识点推荐</v-list-item-title>
                  <v-list-item-subtitle>根据题目内容推荐相关学习资源</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            
            <h3 class="mt-4">📱 使用步骤</h3>
            <v-stepper v-model="currentStep" alt-labels>
              <v-stepper-header>
                <v-stepper-item value="1" title="上传图片">
                  <template v-slot:icon>
                    <v-icon>mdi-camera</v-icon>
                  </template>
                </v-stepper-item>
                <v-divider></v-divider>
                <v-stepper-item value="2" title="AI识别">
                  <template v-slot:icon>
                    <v-icon>mdi-eye</v-icon>
                  </template>
                </v-stepper-item>
                <v-divider></v-divider>
                <v-stepper-item value="3" title="获取解答">
                  <template v-slot:icon>
                    <v-icon>mdi-robot</v-icon>
                  </template>
                </v-stepper-item>
                <v-divider></v-divider>
                <v-stepper-item value="4" title="知识拓展">
                  <template v-slot:icon>
                    <v-icon>mdi-book-open</v-icon>
                  </template>
                </v-stepper-item>
              </v-stepper-header>
              
              <v-stepper-window>
                <v-stepper-window-item value="1">
                  <v-card flat>
                    <v-card-text>
                      <div class="text-center">
                        <v-icon size="48" color="primary">mdi-camera</v-icon>
                        <h4 class="mt-2">第一步：上传题目图片</h4>
                        <p>点击「拍照」按钮直接拍摄，或点击「选择图片」从相册选择</p>
                        <p class="text-caption text-error">* 请确保图片清晰，文件大小不超过3MB</p>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-stepper-window-item>
                
                <v-stepper-window-item value="2">
                  <v-card flat>
                    <v-card-text>
                      <div class="text-center">
                        <v-icon size="48" color="success">mdi-eye</v-icon>
                        <h4 class="mt-2">第二步：AI识别题目</h4>
                        <p>点击「开始识别」按钮，AI将自动识别图片中的文字内容</p>
                        <p class="text-caption text-info">* 识别过程需要几秒钟，请耐心等待</p>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-stepper-window-item>
                
                <v-stepper-window-item value="3">
                  <v-card flat>
                    <v-card-text>
                      <div class="text-center">
                        <v-icon size="48" color="warning">mdi-robot</v-icon>
                        <h4 class="mt-2">第三步：获取AI解答</h4>
                        <p>识别完成后，点击「AI解答」按钮获取详细的解题步骤</p>
                        <p class="text-caption text-success">* AI将提供题目分析、解题思路和详细步骤</p>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-stepper-window-item>
                
                <v-stepper-window-item value="4">
                  <v-card flat>
                    <v-card-text>
                      <div class="text-center">
                        <v-icon size="48" color="info">mdi-book-open</v-icon>
                        <h4 class="mt-2">第四步：知识点推荐</h4>
                        <p>点击「知识点推荐」按钮，获取相关学习资源和视频教程</p>
                        <p class="text-caption text-primary">* 帮助你深入理解相关知识点</p>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-stepper-window-item>
              </v-stepper-window>
            </v-stepper>
            
            <div class="text-center mt-4">
              <v-btn 
                color="primary" 
                size="large" 
                @click="goToImageSolve"
                class="mx-2"
              >
                <v-icon class="mr-2">mdi-camera</v-icon>
                开始使用
              </v-btn>
              <v-btn 
                color="success" 
                size="large" 
                @click="nextStep"
                class="mx-2"
              >
                <v-icon class="mr-2">mdi-arrow-right</v-icon>
                下一步
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'ImageProblemSolveDemo',
  data() {
    return {
      currentStep: 1
    }
  },
  methods: {
    goToImageSolve() {
      this.$router.push({ name: 'ImageProblemSolve' });
    },
    nextStep() {
      if (this.currentStep < 4) {
        this.currentStep++;
      } else {
        this.currentStep = 1;
      }
    }
  }
}
</script>

<style scoped>
.demo-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.v-stepper {
  box-shadow: none;
}

.v-stepper-header {
  box-shadow: none;
}
</style> 