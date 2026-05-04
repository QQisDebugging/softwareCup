<template>
  <div class="student-account-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <div class="title-wrapper">
            <div class="title-decoration">
              <div class="decoration-line"></div>
              <v-icon class="title-icon" color="white" size="40">mdi-account</v-icon>
              <div class="decoration-line"></div>
            </div>
            <h1 class="page-title gradient-text">我的主页</h1>
            <p class="page-subtitle">管理您的个人信息和学习进度</p>
          </div>
        </div>
        <div class="header-decoration">
          <div class="floating-elements">
            <div class="element element-1">
              <v-icon color="white" size="24">mdi-star</v-icon>
            </div>
            <div class="element element-2">
              <v-icon color="white" size="20">mdi-trophy</v-icon>
            </div>
            <div class="element element-3">
              <v-icon color="white" size="18">mdi-chart-line</v-icon>
            </div>
            <div class="element element-4">
              <v-icon color="white" size="22">mdi-school</v-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <v-container class="main-content">
      <!-- 个人信息卡片 -->
      <v-card class="info-card modern-card mb-6" elevation="0">
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon">
              <v-icon color="white" size="28">mdi-account-circle</v-icon>
            </div>
            <div>
              <h2 class="card-title">个人信息</h2>
              <p class="card-subtitle">您的基本信息和学习数据</p>
            </div>
          </div>
          <div class="header-actions">
            <v-btn
              variant="elevated"
              color="white"
              size="small"
              prepend-icon="mdi-pencil"
              @click="showChangePasswordDialog"
              class="action-btn"
            >
              修改密码
            </v-btn>
          </div>
        </div>

        <v-card-text class="info-content">
          <v-row>
            <!-- 左侧信息列表 -->
            <v-col cols="12" md="8">
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">
                    <v-icon color="primary" size="20">mdi-card-account-details</v-icon>
                    <span>学号</span>
                  </div>
                  <div class="info-value">{{ studentInfo.sno }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">
                    <v-icon color="primary" size="20">mdi-account</v-icon>
                    <span>姓名</span>
                  </div>
                  <div class="info-value">{{ studentInfo.name }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">
                    <v-icon color="warning" size="20">mdi-coin</v-icon>
                    <span>逗币</span>
                  </div>
                  <div class="info-value coin-value">{{ studentInfo.request_times }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">
                    <v-icon color="pink" size="20">mdi-gender-male-female</v-icon>
                    <span>性别</span>
                  </div>
                  <div class="info-value">{{ studentInfo.gender }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">
                    <v-icon color="success" size="20">mdi-comment-text</v-icon>
                    <span>签名</span>
                  </div>
                  <div class="info-value signature-value">
                    {{ studentInfo.description || '暂无签名' }}
                    <v-btn
                      variant="text"
                      size="small"
                      icon="mdi-pencil"
                      @click="showChangeDescriptionDialog"
                      class="edit-btn"
                    />
                  </div>
                </div>

                <div class="info-item">
                  <div class="info-label">
                    <v-icon color="info" size="20">mdi-school</v-icon>
                    <span>班级</span>
                  </div>
                  <div class="info-value">{{ studentInfo.major }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">
                    <v-icon color="purple" size="20">mdi-clock</v-icon>
                    <span>学习时长</span>
                  </div>
                  <div class="info-value">{{ studentInfo.study_time }}分钟</div>
                </div>

                <div class="info-item">
                  <div class="info-label">
                    <v-icon color="orange" size="20">mdi-trophy</v-icon>
                    <span>全站排行</span>
                  </div>
                  <div class="info-value rank-value">第{{ studentInfo.rank }}名</div>
                </div>

                <div class="info-item full-width">
                  <div class="info-label">
                    <v-icon color="teal" size="20">mdi-tag-multiple</v-icon>
                    <span>标签</span>
                  </div>
                  <div class="info-value tags-container">
                    <div class="tags-wrapper">
                      <v-chip
                        v-for="tag in studentInfo.tags"
                        :key="tag"
                        class="tag-chip"
                        variant="elevated"
                        size="small"
                      >
                        {{ tag }}
                      </v-chip>
                    </div>
                    <v-btn
                      variant="outlined"
                      size="small"
                      prepend-icon="mdi-plus"
                      @click="showAddTagDialog"
                      class="add-tag-btn"
                    >
                      添加标签
                    </v-btn>
                  </div>
                </div>
              </div>
            </v-col>

            <!-- 右侧图表 -->
            <v-col cols="12" md="4">
              <div class="chart-container">
                <h3 class="chart-title">学习活跃度</h3>
                <div class="gauge-wrapper">
                  <div id="gauge" ref="gauge" class="gauge-chart"></div>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>

        <!-- 社交信息 -->
        <v-card-actions class="social-actions">
          <v-spacer></v-spacer>
          <v-btn
            variant="elevated"
            color="primary"
            prepend-icon="mdi-account-heart"
            @click="showFollowingDialog"
            class="social-btn"
          >
            {{ followingNum }} 关注
          </v-btn>
          <v-btn
            variant="elevated"
            color="secondary"
            prepend-icon="mdi-account-group"
            @click="showFollowersDialog"
            class="social-btn"
          >
            {{ followerNum }} 粉丝
          </v-btn>
        </v-card-actions>
      </v-card>

      <!-- 学习热力图卡片 -->
      <v-card class="heatmap-card modern-card mb-6" elevation="0">
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon">
              <v-icon color="white" size="28">mdi-chart-box</v-icon>
            </div>
            <div>
              <h2 class="card-title">学习热力图</h2>
              <p class="card-subtitle">追踪您的学习活跃度</p>
            </div>
          </div>
        </div>
        <v-card-text class="heatmap-content">
          <div class="heatmap-wrapper">
            <CalendarHeatmap
              :values="heatmapData"
              :start-date="startDate"
              :end-date="endDate"
              :round="2"
              tooltip-unit="活跃度"
              class="modern-heatmap"
            />
          </div>
        </v-card-text>
      </v-card>

      <!-- Bio卡片 -->
      <v-card class="bio-card modern-card mb-6" elevation="0">
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon">
              <v-icon color="white" size="28">mdi-file-document-edit</v-icon>
            </div>
            <div>
              <h2 class="card-title">个人简介</h2>
              <p class="card-subtitle">展示您的个人介绍和专长</p>
            </div>
          </div>
          <div class="header-actions">
            <v-btn
              variant="elevated"
              color="white"
              size="small"
              prepend-icon="mdi-pencil"
              @click="showChangeBioDialog"
              class="action-btn"
            >
              编辑简介
            </v-btn>
          </div>
        </div>
        <v-card-text class="bio-content">
          <div class="bio-wrapper">
            <v-md-preview 
              :text="studentInfo.bio || '# 欢迎访问我的主页！\n\n## 关于我\n\n还没有填写个人简介，点击上方编辑按钮添加您的个人介绍吧！'"
              class="bio-preview"
            />
          </div>
        </v-card-text>
      </v-card>
    </v-container>

    <!-- 修改密码对话框 -->
    <v-dialog v-model="changePasswordDialog" max-width="500" persistent>
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon color="primary" class="mr-2">mdi-lock</v-icon>
          修改密码
        </v-card-title>
        <v-card-text class="dialog-content">
          <v-form ref="passwordForm">
            <v-text-field
              v-model="oldPassword"
              label="原密码"
              type="password"
              prepend-inner-icon="mdi-lock-outline"
              variant="outlined"
              :error="passwordError"
              :error-messages="passwordError ? '原密码错误' : ''"
              class="mb-3"
            />
            <v-text-field
              v-model="newPassword"
              label="新密码"
              type="password"
              prepend-inner-icon="mdi-lock-plus"
              variant="outlined"
              :error="passwordTooShort"
              :error-messages="passwordTooShort ? '密码长度至少6位' : ''"
              class="mb-3"
            />
            <v-text-field
              v-model="confirmNewPassword"
              label="确认新密码"
              type="password"
              prepend-inner-icon="mdi-lock-check"
              variant="outlined"
              :error="newPasswordMismatch"
              :error-messages="newPasswordMismatch ? '两次密码不一致' : ''"
              class="mb-3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer />
          <v-btn
            variant="text"
            @click="changePasswordDialog = false"
            class="cancel-btn"
          >
            取消
          </v-btn>
          <v-btn
            variant="elevated"
            color="primary"
            @click="changePassword"
            class="confirm-btn"
          >
            确认修改
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 修改签名对话框 -->
    <v-dialog v-model="changeDescriptionDialog" max-width="500" persistent>
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon color="success" class="mr-2">mdi-comment-text</v-icon>
          修改签名
        </v-card-title>
        <v-card-text class="dialog-content">
          <v-textarea
            v-model="newDescription"
            label="个人签名"
            placeholder="写下您的个人签名..."
            prepend-inner-icon="mdi-pencil"
            variant="outlined"
            rows="3"
            counter="100"
            maxlength="100"
          />
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer />
          <v-btn
            variant="text"
            @click="changeDescriptionDialog = false"
            class="cancel-btn"
          >
            取消
          </v-btn>
          <v-btn
            variant="elevated"
            color="success"
            @click="changeDescription"
            class="confirm-btn"
          >
            确认修改
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 修改Bio对话框 -->
    <v-dialog v-model="changeBioDialog" max-width="100%" fullscreen>
      <v-card class="bio-dialog-card">
        <v-toolbar color="primary" class="bio-toolbar">
          <v-toolbar-title class="bio-toolbar-title">
            <v-icon class="mr-2">mdi-file-document-edit</v-icon>
            编辑个人简介
          </v-toolbar-title>
          <v-spacer />
          <v-btn
            icon="mdi-close"
            @click="changeBioDialog = false"
            class="close-btn"
          />
        </v-toolbar>
        <v-card-text class="bio-dialog-content">
          <v-md-editor
            v-model="newBio"
            height="calc(100vh - 200px)"
            class="bio-editor"
          />
        </v-card-text>
        <v-card-actions class="bio-dialog-actions">
          <v-spacer />
          <v-btn
            variant="text"
            @click="changeBioDialog = false"
            class="cancel-btn"
          >
            取消
          </v-btn>
          <v-btn
            variant="elevated"
            color="primary"
            @click="changeBio"
            class="confirm-btn"
          >
            保存更改
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 添加标签对话框 -->
    <v-dialog v-model="addTagDialog" max-width="500" persistent>
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon color="teal" class="mr-2">mdi-tag-multiple</v-icon>
          管理标签
        </v-card-title>
        <v-card-text class="dialog-content">
          <div class="current-tags">
            <p class="tags-subtitle">当前标签：</p>
            <div class="tags-list">
              <v-chip
                v-for="(tag, index) in studentInfo.tags"
                :key="index"
                closable
                @click:close="removeTag(index)"
                class="tag-chip ma-1"
                color="teal"
                variant="elevated"
              >
                {{ tag }}
              </v-chip>
            </div>
          </div>
          <v-text-field
            v-model="newTag"
            label="添加新标签"
            placeholder="输入标签名称..."
            prepend-inner-icon="mdi-tag-plus"
            variant="outlined"
            @keyup.enter="addTag"
            class="mt-4"
          />
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer />
          <v-btn
            variant="text"
            @click="addTagDialog = false"
            class="cancel-btn"
          >
            完成
          </v-btn>
          <v-btn
            variant="elevated"
            color="teal"
            @click="addTag"
            :disabled="!newTag.trim()"
            class="confirm-btn"
          >
            添加标签
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 关注/粉丝对话框 -->
    <v-dialog v-model="followingDialog" max-width="600">
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon color="primary" class="mr-2">mdi-account-heart</v-icon>
          我的关注 ({{ followingNum }})
        </v-card-title>
        <v-card-text class="dialog-content">
          <v-list class="social-list">
            <v-list-item
              v-for="user in followingList"
              :key="user.sno"
              @click="goToHomePage(user.sno)"
              class="social-item"
            >
              <template v-slot:prepend>
                <v-avatar color="primary" size="40">
                  <span class="avatar-text">{{ user.name?.charAt(0) }}</span>
                </v-avatar>
              </template>
              <v-list-item-title>{{ user.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ user.sno }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer />
          <v-btn
            variant="text"
            @click="followingDialog = false"
            class="cancel-btn"
          >
            关闭
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="followersDialog" max-width="600">
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon color="secondary" class="mr-2">mdi-account-group</v-icon>
          我的粉丝 ({{ followerNum }})
        </v-card-title>
        <v-card-text class="dialog-content">
          <v-list class="social-list">
            <v-list-item
              v-for="user in followersList"
              :key="user.sno"
              @click="goToHomePage(user.sno)"
              class="social-item"
            >
              <template v-slot:prepend>
                <v-avatar color="secondary" size="40">
                  <span class="avatar-text">{{ user.name?.charAt(0) }}</span>
                </v-avatar>
              </template>
              <v-list-item-title>{{ user.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ user.sno }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer />
          <v-btn
            variant="text"
            @click="followersDialog = false"
            class="cancel-btn"
          >
            关闭
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 消息提示对话框 -->
    <v-dialog v-model="messageDialog" max-width="400" persistent>
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon color="info" class="mr-2">mdi-information</v-icon>
          {{ messageTitle }}
        </v-card-title>
        <v-card-text class="dialog-content">
          {{ messageContent }}
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer />
          <v-btn
            variant="elevated"
            color="info"
            @click="messageDialog = false"
            class="confirm-btn"
          >
            确定
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { CalendarHeatmap } from "vue3-calendar-heatmap";
import "vue3-calendar-heatmap/dist/style.css";
import { addRequests } from "@/utils/commonUtil";
import axios from "axios";
import * as echarts from 'echarts';
import { defineComponent } from 'vue';

export default defineComponent({
  components: {
    CalendarHeatmap,
  },
  data() {
    return {
      sno: localStorage.getItem("username"),
      studentInfo: {
        tags: [],
      },
      changePasswordDialog: false,
      oldPassword: "",
      newPassword: "",
      confirmNewPassword: "",
      passwordError: false,
      passwordTooShort: false,
      newPasswordMismatch: false,
      newPasswordSameAsOld: false,
      changeDescriptionDialog: false,
      changeBioDialog: false,
      newDescription: "",
      newBio: "",
      messageDialog: false,
      messageTitle: "",
      messageContent: "",
      heatmapData: [],
      startDate: new Date("2024-01-01"),
      endDate: new Date().toISOString().split("T")[0],
      addTagDialog: false,
      newTag: "",
      followingDialog: false,
      followersDialog: false,
      followingList: [],
      followersList: [],
      followerNum: 0,
      followingNum: 0,
      gaugeChart: null,
    };
  },
  created() {
    this.getStudentInfo();
    this.getHeatmapData();
    this.checkSocialStatus();
    addRequests();
  },
  mounted() {
    this.initGaugeChart();
  },
  methods: {
    goToHomePage(studentId) {
      this.$router.push({ name: "User", params: { user_id: studentId } });
    },
    removeTag(index) {
      this.studentInfo.tags.splice(index, 1);
      this.updateTags();
    },
    checkSocialStatus() {
      axios
        .post(
          `${this.$backendUrl}/api/checkSocialStatus`,
          {
            follower_id: localStorage.getItem("username"),
            following_id: this.sno,
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        )
        .then((response) => {
          this.followingNum = response.data.following_count;
          this.followerNum = response.data.followers_count;
        })
        .catch((error) => {
          console.error("Error ", error);
        });
    },
    getStudentInfo() {
      axios
        .get(`${this.$backendUrl}/api/getStudentInfo?sno=${this.sno}`)
        .then((response) => {
          this.studentInfo = response.data;
          if (this.studentInfo.bio == null) {
            this.studentInfo.bio = "";
          }
          if (!this.studentInfo.tags) {
            this.studentInfo.tags = [];
          }
          this.newBio = this.studentInfo.bio;
          this.updateGaugeChart();
        })
        .catch((error) => {
          this.showMessageDialog("错误", "获取学生信息失败");
        });
    },
    getHeatmapData() {
      axios
        .get(`${this.$backendUrl}/api/getActiviteMap?sno=${this.sno}`)
        .then((response) => {
          this.heatmapData = response.data.map((entry) => ({
            date: entry.date,
            count: entry.count,
          }));
        })
        .catch((error) => {
          this.showMessageDialog("错误", "获取热力图数据失败");
        });
    },
    getFollowingList() {
      axios
        .get(`${this.$backendUrl}/api/following?sno=${this.sno}`)
        .then((response) => {
          this.followingList = response.data;
          this.followingDialog = true;
        })
        .catch((error) => {
          console.error("获取关注列表失败", error);
        });
    },
    getFollowersList() {
      axios
        .get(`${this.$backendUrl}/api/followers?sno=${this.sno}`)
        .then((response) => {
          this.followersList = response.data;
          this.followersDialog = true;
        })
        .catch((error) => {
          console.error("获取粉丝列表失败", error);
        });
    },
    showFollowingDialog() {
      this.getFollowingList();
    },
    showFollowersDialog() {
      this.getFollowersList();
    },
    showChangePasswordDialog() {
      this.changePasswordDialog = true;
    },
    showChangeDescriptionDialog() {
      this.newDescription = this.studentInfo.description || "";
      this.changeDescriptionDialog = true;
    },
    showChangeBioDialog() {
      this.newBio = this.studentInfo.bio || "";
      this.changeBioDialog = true;
    },
    changePassword() {
      this.passwordError = false;
      this.passwordTooShort = false;
      this.newPasswordMismatch = false;
      this.newPasswordSameAsOld = false;

      if (this.newPassword.length < 6) {
        this.passwordTooShort = true;
        return;
      }

      if (this.newPassword !== this.confirmNewPassword) {
        this.newPasswordMismatch = true;
        return;
      }

      if (this.oldPassword === this.newPassword) {
        this.newPasswordSameAsOld = true;
        return;
      }

      axios
        .post(
          `${this.$backendUrl}/api/changePassword`,
          {
            sno: this.sno,
            old_password: this.oldPassword,
            new_password: this.newPassword,
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        )
        .then((response) => {
          this.showMessageDialog("成功", "密码已成功更新");
          this.changePasswordDialog = false;
          this.oldPassword = "";
          this.newPassword = "";
          this.confirmNewPassword = "";
        })
        .catch((error) => {
          if (error.response && error.response.status === 401) {
            this.passwordError = true;
          } else {
            this.showMessageDialog("错误", "密码更新失败");
          }
        });
    },
    changeBio() {
      axios
        .post(
          `${this.$backendUrl}/api/updateBio`,
          {
            sno: this.sno,
            bio: this.newBio,
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        )
        .then((response) => {
          this.changeBioDialog = false;
          this.getStudentInfo();
          this.showMessageDialog("成功", "个人简介已成功更新");
        })
        .catch((error) => {
          this.showMessageDialog("错误", "更新失败");
        });
    },
    changeDescription() {
      axios
        .post(
          `${this.$backendUrl}/api/updateDescription`,
          {
            sno: this.sno,
            new_description: this.newDescription,
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        )
        .then((response) => {
          this.changeDescriptionDialog = false;
          this.getStudentInfo();
          this.showMessageDialog("成功", "签名已成功更新");
        })
        .catch((error) => {
          this.showMessageDialog("错误", "签名更新失败");
        });
    },
    showAddTagDialog() {
      this.addTagDialog = true;
    },
    addTag() {
      if (this.newTag && !this.studentInfo.tags.includes(this.newTag)) {
        this.studentInfo.tags.push(this.newTag);
        this.newTag = "";
        this.updateTags();
      }
    },
    updateTags() {
      axios
        .post(
          `${this.$backendUrl}/api/updateTags`,
          {
            sno: this.sno,
            tags: this.studentInfo.tags,
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        )
        .then((response) => {
          // 标签更新成功
        })
        .catch((error) => {
          this.showMessageDialog("错误", "标签更新失败");
        });
    },
    showMessageDialog(title, content) {
      this.messageTitle = title;
      this.messageContent = content;
      this.messageDialog = true;
    },
    initGaugeChart() {
      this.gaugeChart = echarts.init(this.$refs.gauge);
      this.updateGaugeChart();
    },
    updateGaugeChart() {
      if (this.gaugeChart) {
        const option = {
          series: [
            {
              type: 'gauge',
              progress: {
                show: true,
                width: 18
              },
              axisLine: {
                lineStyle: {
                  width: 18,
                  color: [
                    [0.3, '#FF6B6B'],
                    [0.7, '#4ECDC4'],
                    [1, '#45B7D1']
                  ]
                }
              },
              axisTick: {
                show: false
              },
              splitLine: {
                length: 15,
                lineStyle: {
                  width: 2,
                  color: '#999'
                }
              },
              axisLabel: {
                distance: 25,
                color: '#999',
                fontSize: 12
              },
              anchor: {
                show: true,
                showAbove: true,
                size: 20,
                itemStyle: {
                  borderWidth: 10,
                  borderColor: '#45B7D1'
                }
              },
              title: {
                show: false
              },
              detail: {
                valueAnimation: true,
                fontSize: 32,
                offsetCenter: [0, '70%'],
                color: '#45B7D1',
                fontWeight: 'bold'
              },
              max: 200,
              data: [
                {
                  value: this.studentInfo.request_times || 0,
                  name: '逗币'
                }
              ]
            }
          ]
        };
        this.gaugeChart.setOption(option);
      }
    }
  },
  watch: {
    studentInfo: {
      handler() {
        this.updateGaugeChart();
      },
      deep: true
    }
  }
});
</script>

<style scoped>
.student-account-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
}

/* 页面头部样式 */
.page-header {
  position: relative;
  padding: 6rem 0 4rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 2;
}

.header-main {
  text-align: center;
  margin-bottom: 2rem;
}

.title-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.title-decoration {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.decoration-line {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
}

.title-icon {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  padding: 0.5rem;
  backdrop-filter: blur(10px);
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.page-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.floating-elements {
  position: absolute;
  width: 100%;
  height: 100%;
}

.element {
  position: absolute;
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  animation: float 6s ease-in-out infinite;
}

.element-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.element-2 {
  top: 60%;
  left: 85%;
  animation-delay: 2s;
}

.element-3 {
  top: 80%;
  left: 15%;
  animation-delay: 4s;
}

.element-4 {
  top: 30%;
  left: 90%;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

/* 主要内容区域 */
.main-content {
  position: relative;
  z-index: 1;
  margin-top: -2rem;
  padding-bottom: 4rem;
}

.modern-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  overflow: hidden;
}

.modern-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

/* 卡片头部 */
.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.card-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  z-index: 2;
}

.header-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
}

.card-subtitle {
  font-size: 0.9rem;
  opacity: 0.8;
  margin: 0;
}

.header-actions {
  position: relative;
  z-index: 2;
}

.action-btn {
  background: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(10px);
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3) !important;
  transform: translateY(-2px);
}

/* 信息内容区域 */
.info-content {
  padding: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.info-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.info-item.full-width {
  grid-column: 1 / -1;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #4a5568;
}

.info-value {
  font-weight: 600;
  color: #1a202c;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.coin-value {
  color: #f59e0b;
  font-size: 1.1rem;
}

.rank-value {
  color: #ea580c;
  font-size: 1.1rem;
}

.signature-value {
  max-width: 200px;
  text-align: right;
}

.edit-btn {
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.edit-btn:hover {
  opacity: 1;
}

.tags-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-chip {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%) !important;
  color: white !important;
  transition: all 0.3s ease;
}

.tag-chip:hover {
  transform: scale(1.05);
}

.add-tag-btn {
  align-self: flex-start;
  border-radius: 12px !important;
  border: 2px dashed rgba(102, 126, 234, 0.3) !important;
  color: #667eea !important;
  transition: all 0.3s ease;
}

.add-tag-btn:hover {
  border-color: #667eea !important;
  background: rgba(102, 126, 234, 0.1) !important;
}

/* 图表区域 */
.chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 16px;
  height: 100%;
}

.chart-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 1rem;
  text-align: center;
}

.gauge-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 200px;
}

.gauge-chart {
  width: 100%;
  height: 250px;
}

/* 社交操作区域 */
.social-actions {
  padding: 1.5rem 2rem;
  background: rgba(248, 250, 252, 0.8);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.social-btn {
  border-radius: 12px !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.social-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 热力图区域 */
.heatmap-content {
  padding: 2rem;
}

.heatmap-wrapper {
  display: flex;
  justify-content: center;
  padding: 1rem;
  background: rgba(248, 250, 252, 0.5);
  border-radius: 16px;
}

.modern-heatmap {
  border-radius: 8px;
  overflow: hidden;
}

/* Bio区域 */
.bio-content {
  padding: 2rem;
}

.bio-wrapper {
  background: rgba(248, 250, 252, 0.5);
  border-radius: 16px;
  padding: 2rem;
  min-height: 200px;
}

.bio-preview {
  background: transparent !important;
}

/* 对话框样式 */
.dialog-card {
  border-radius: 20px !important;
  overflow: hidden;
}

.dialog-title {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.dialog-content {
  padding: 2rem;
}

.dialog-actions {
  padding: 1rem 2rem 1.5rem;
  background: rgba(248, 250, 252, 0.5);
}

.cancel-btn {
  color: #6b7280 !important;
  border-radius: 12px !important;
}

.confirm-btn {
  border-radius: 12px !important;
  font-weight: 500;
}

/* Bio编辑器对话框 */
.bio-dialog-card {
  border-radius: 0 !important;
}

.bio-toolbar {
  border-radius: 0 !important;
}

.bio-toolbar-title {
  font-size: 1.2rem;
  font-weight: 600;
}

.bio-dialog-content {
  padding: 0 !important;
}

.bio-editor {
  border-radius: 0 !important;
}

.bio-dialog-actions {
  padding: 1rem 2rem;
  background: rgba(248, 250, 252, 0.9);
}

/* 标签管理对话框 */
.current-tags {
  margin-bottom: 1.5rem;
}

.tags-subtitle {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 40px;
  padding: 0.5rem;
  background: rgba(248, 250, 252, 0.5);
  border-radius: 8px;
}

/* 社交列表 */
.social-list {
  max-height: 400px;
  overflow-y: auto;
}

.social-item {
  border-radius: 12px;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
}

.social-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateX(4px);
}

.avatar-text {
  font-weight: 600;
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 4rem 0 2rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .card-header {
    padding: 1.5rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .info-content {
    padding: 1.5rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .signature-value {
    max-width: 100%;
    text-align: left;
  }
  
  .social-actions {
    padding: 1rem;
  }
  
  .heatmap-content,
  .bio-content {
    padding: 1.5rem;
  }
  
  .dialog-content {
    padding: 1.5rem;
  }
  
  .element {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .card-header {
    padding: 1rem;
  }
  
  .info-content {
    padding: 1rem;
  }
  
  .chart-container {
    padding: 0.5rem;
  }
  
  .gauge-chart {
    height: 200px;
  }
}
</style>
