<template>
  <div class="user-page-container">
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
            <h1 class="page-title gradient-text">
              <span v-if="studentInfo.gender === '男'">他的主页</span>
              <span v-else-if="studentInfo.gender === '女'">她的主页</span>
              <span v-else>TA的主页</span>
            </h1>
            <p class="page-subtitle">{{ studentInfo.name }}的个人信息</p>
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
      <!-- 用户信息卡片 -->
      <v-card class="info-card modern-card mb-6" elevation="0">
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon">
              <v-icon color="white" size="28">mdi-account-circle</v-icon>
            </div>
            <div>
              <h2 class="card-title">用户信息</h2>
              <p class="card-subtitle">{{ studentInfo.name }}的详细信息</p>
            </div>
          </div>
          <div class="header-actions">
            <v-btn
              variant="elevated"
              color="white"
              size="small"
              prepend-icon="mdi-coin"
              @click="openCoinDialog"
              class="action-btn"
            >
              投币
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
                  <div class="info-value">{{ studentInfo.description || '暂无签名' }}</div>
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
                    <span v-if="!studentInfo.tags || studentInfo.tags.length === 0" class="no-tags">
                      暂无标签
                    </span>
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
          <v-btn
            variant="elevated"
            :color="isFollowing ? 'error' : 'success'"
            :prepend-icon="isFollowing ? 'mdi-heart-broken' : 'mdi-heart'"
            @click="toggleFollow"
            class="social-btn"
          >
            {{ isFollowing ? '取消关注' : '关注TA' }}
          </v-btn>
          <v-btn
            v-if="isFollowing"
            variant="elevated"
            color="info"
            prepend-icon="mdi-message"
            @click="startChat(logged_sno, studentInfo.sno)"
            class="social-btn"
          >
            私信
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
              <p class="card-subtitle">{{ studentInfo.name }}的学习活跃度</p>
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
              <p class="card-subtitle">{{ studentInfo.name }}的个人介绍</p>
            </div>
          </div>
        </div>
        <v-card-text class="bio-content">
          <div class="bio-wrapper">
            <v-md-preview 
              :text="studentInfo.bio || '# 这个人很懒，什么都没写 😄'"
              class="bio-preview"
            />
          </div>
        </v-card-text>
      </v-card>
    </v-container>

    <!-- 投币对话框 -->
    <v-dialog v-model="coinDialog" max-width="400" persistent>
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon color="white" class="mr-2">mdi-coin</v-icon>
          投币给{{ studentInfo.name }}
        </v-card-title>
        <v-card-text class="dialog-content">
          <div class="coin-selection">
            <p class="selection-title">选择投币数量：</p>
            <div class="coin-buttons">
              <v-btn
                v-for="amount in [1, 5, 10, 20]"
                :key="amount"
                variant="outlined"
                size="large"
                @click="confirmCoin(amount)"
                class="coin-btn"
              >
                <v-icon class="mr-2">mdi-coin</v-icon>
                {{ amount }}
              </v-btn>
            </div>
          </div>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer />
          <v-btn
            variant="text"
            @click="coinDialog = false"
            class="cancel-btn"
          >
            取消
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 关注/粉丝对话框 -->
    <v-dialog v-model="followingDialog" max-width="600">
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon color="white" class="mr-2">mdi-account-heart</v-icon>
          {{ studentInfo.name }}的关注 ({{ followingNum }})
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
          <v-icon color="white" class="mr-2">mdi-account-group</v-icon>
          {{ studentInfo.name }}的粉丝 ({{ followerNum }})
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

    <!-- 消息提示 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      bottom
      right
      class="modern-snackbar"
    >
      <div class="snackbar-content">
        <v-icon class="mr-2">{{ snackbar.icon }}</v-icon>
        {{ snackbar.text }}
      </div>
    </v-snackbar>
  </div>
</template>

<script setup>

</script>

<script>
import { CalendarHeatmap } from 'vue3-calendar-heatmap';
import 'vue3-calendar-heatmap/dist/style.css';
import { addRequests } from "@/utils/commonUtil";
import axios from "axios";
import * as echarts from 'echarts';
import { defineComponent } from 'vue';

export default defineComponent({
  components: {
    CalendarHeatmap
  },
  props: ['user_id'],
  data() {
    return {
      coinDialog: false,
      sno: this.user_id,
      logged_sno: localStorage.getItem("username"),
      studentInfo: {
        tags: []
      },
      isFollowing: false,
      messageDialog: false,
      messageTitle: "",
      messageContent: "",
      heatmapData: [],
      startDate: new Date("2024-01-01"),
      endDate: new Date().toISOString().split('T')[0],
      followingDialog: false,
      followersDialog: false,
      followerNum: 0,
      followingNum: 0,
      followingList: [],
      followersList: [],
      snackbar: {
        show: false,
        text: '',
        color: 'success',
        icon: 'mdi-check'
      },
      gaugeChart: null
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
    openCoinDialog() {
      this.coinDialog = true;
    },
    confirmCoin(num) {
      axios.post(`${this.$backendUrl}/api/toby`, {
        sno: this.logged_sno,
        targetsno: this.studentInfo.sno,
        num: num
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })
      .then(response => {
        this.showSnackbar('投币成功！', 'success', 'mdi-check');
        this.getStudentInfo(); // 更新用户信息
      })
      .catch(error => {
        this.showSnackbar('投币失败: ' + (error.response?.data?.error || '未知错误'), 'error', 'mdi-alert');
      })
      .finally(() => {
        this.coinDialog = false;
      });
    },
    startChat(sender, receiver) {
      if (sender === receiver) {
        this.showSnackbar('不能给自己私信哦!', 'warning', 'mdi-alert');
      } else {
        this.$emit('start-chat', sender, receiver);
      }
    },
    toggleFollow() {
      if (this.isFollowing) {
        this.unfollow();
      } else {
        this.follow();
      }
    },
    follow() {
      axios.post(`${this.$backendUrl}/api/follow`, {
        follower_id: this.logged_sno,
        following_id: this.sno
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })
      .then(response => {
        this.isFollowing = true;
        this.followerNum++;
        this.showSnackbar('关注成功！', 'success', 'mdi-heart');
      })
      .catch(error => {
        this.showSnackbar('关注失败，请稍后重试', 'error', 'mdi-alert');
      });
    },
    unfollow() {
      axios.post(`${this.$backendUrl}/api/unfollow`, {
        follower_id: this.logged_sno,
        following_id: this.sno
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })
      .then(response => {
        this.isFollowing = false;
        this.followerNum--;
        this.showSnackbar('取消关注成功！', 'info', 'mdi-heart-broken');
      })
      .catch(error => {
        this.showSnackbar('取消关注失败，请稍后重试', 'error', 'mdi-alert');
      });
    },
    checkSocialStatus() {
      axios.post(`${this.$backendUrl}/api/checkSocialStatus`, {
        follower_id: this.logged_sno,
        following_id: this.sno
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })
      .then(response => {
        this.followingNum = response.data.following_count;
        this.followerNum = response.data.followers_count;
        this.isFollowing = response.data.is_following;
      })
      .catch(error => {
        console.error('Error checking social status:', error);
      });
    },
    getStudentInfo() {
      axios.get(`${this.$backendUrl}/api/getStudentInfo?sno=${this.sno}`)
        .then(response => {
          this.studentInfo = response.data;
          if (!this.studentInfo.tags) {
            this.studentInfo.tags = [];
          }
          this.updateGaugeChart();
        })
        .catch(error => {
          this.showSnackbar('获取用户信息失败', 'error', 'mdi-alert');
        });
    },
    getHeatmapData() {
      axios.get(`${this.$backendUrl}/api/getActiviteMap?sno=${this.sno}`)
        .then(response => {
          this.heatmapData = response.data.map(entry => ({
            date: entry.date,
            count: entry.count
          }));
        })
        .catch(error => {
          this.showSnackbar('获取热力图数据失败', 'error', 'mdi-alert');
        });
    },
    getFollowingList() {
      axios.get(`${this.$backendUrl}/api/following?sno=${this.sno}`)
        .then(response => {
          this.followingList = response.data;
          this.followingDialog = true;
        })
        .catch(error => {
          console.error('获取关注列表失败', error);
        });
    },
    getFollowersList() {
      axios.get(`${this.$backendUrl}/api/followers?sno=${this.sno}`)
        .then(response => {
          this.followersList = response.data;
          this.followersDialog = true;
        })
        .catch(error => {
          console.error('获取粉丝列表失败', error);
        });
    },
    showFollowingDialog() {
      this.getFollowingList();
    },
    showFollowersDialog() {
      this.getFollowersList();
    },
    showSnackbar(text, color, icon) {
      this.snackbar.text = text;
      this.snackbar.color = color;
      this.snackbar.icon = icon;
      this.snackbar.show = true;
    },
    initGaugeChart() {
      if (this.$refs.gauge) {
        this.gaugeChart = echarts.init(this.$refs.gauge);
        this.updateGaugeChart();
      }
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
.user-page-container {
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
}

.coin-value {
  color: #f59e0b;
  font-size: 1.1rem;
}

.rank-value {
  color: #ea580c;
  font-size: 1.1rem;
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

.no-tags {
  color: #9ca3af;
  font-style: italic;
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
  gap: 1rem;
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

/* 投币选择 */
.coin-selection {
  text-align: center;
}

.selection-title {
  font-size: 1.1rem;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 1.5rem;
}

.coin-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.coin-btn {
  border-radius: 16px !important;
  min-width: 80px;
  height: 60px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid rgba(102, 126, 234, 0.3) !important;
}

.coin-btn:hover {
  background: rgba(102, 126, 234, 0.1) !important;
  border-color: #667eea !important;
  transform: translateY(-2px) scale(1.05);
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
  cursor: pointer;
}

.social-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateX(4px);
}

.avatar-text {
  font-weight: 600;
  color: white;
}

/* 通知样式 */
.modern-snackbar {
  border-radius: 12px !important;
}

.snackbar-content {
  display: flex;
  align-items: center;
  font-weight: 500;
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
  
  .social-actions {
    padding: 1rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .social-btn {
    width: 100%;
  }
  
  .heatmap-content,
  .bio-content {
    padding: 1.5rem;
  }
  
  .dialog-content {
    padding: 1.5rem;
  }
  
  .coin-buttons {
    gap: 0.5rem;
  }
  
  .coin-btn {
    min-width: 60px;
    height: 50px;
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
  
  .coin-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .coin-btn {
    width: 100%;
    max-width: 200px;
  }
}
</style>
