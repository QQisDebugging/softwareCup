<template>
  <div 
    class="modern-feature-card" 
    :class="{ 'is-featured': featured }"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- 背景装饰 -->
    <div class="card-background">
      <div class="gradient-overlay"></div>
      <div class="pattern-overlay"></div>
    </div>

    <!-- 图片容器 -->
    <div class="card-image-container">
      <div class="image-wrapper">
        <img 
          :src="imageSrc" 
          :alt="title"
          class="card-image"
          loading="lazy"
        />
        <div class="image-overlay"></div>
      </div>
      
      <!-- 悬停时的图标 -->
      <div class="hover-icon">
        <v-icon size="32" color="white">{{ icon || 'mdi-arrow-right' }}</v-icon>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="card-content">
      <div class="content-header">
        <h3 class="card-title">{{ title }}</h3>
        <p v-if="description" class="card-description">{{ description }}</p>
      </div>
      
      <!-- 标签 -->
      <div v-if="tags && tags.length" class="card-tags">
        <span 
          v-for="tag in tags" 
          :key="tag" 
          class="tag"
        >
          {{ tag }}
        </span>
      </div>

      <!-- 进度指示器 (如果有的话) -->
      <div v-if="progress !== undefined" class="progress-section">
        <div class="progress-info">
          <span class="progress-label">完成度</span>
          <span class="progress-value">{{ progress }}%</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 悬停时的动作按钮 -->
    <div class="card-actions">
      <v-btn
        variant="elevated"
        color="primary"
        class="action-btn"
        size="small"
      >
        <v-icon left>mdi-play</v-icon>
        开始使用
      </v-btn>
    </div>

    <!-- 特色徽章 -->
    <div v-if="badge" class="feature-badge">
      {{ badge }}
    </div>

    <!-- 涟漪效果 -->
    <div ref="ripple" class="ripple-effect"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Props 定义
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  imageSrc: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: 'mdi-arrow-right'
  },
  featured: {
    type: Boolean,
    default: false
  },
  tags: {
    type: Array,
    default: () => []
  },
  progress: {
    type: Number,
    default: undefined
  },
  badge: {
    type: String,
    default: ''
  },
  to: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['click'])

// Refs
const ripple = ref(null)

// 方法
const handleClick = (event) => {
  createRipple(event)
  emit('click', props.to)
}

const handleMouseEnter = () => {
  // 可以添加额外的悬停逻辑
}

const handleMouseLeave = () => {
  // 可以添加额外的离开逻辑
}

const createRipple = (event) => {
  if (!ripple.value) return
  
  const rect = event.currentTarget.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2
  
  ripple.value.style.width = ripple.value.style.height = size + 'px'
  ripple.value.style.left = x + 'px'
  ripple.value.style.top = y + 'px'
  ripple.value.classList.add('ripple-active')
  
  setTimeout(() => {
    ripple.value?.classList.remove('ripple-active')
  }, 600)
}

onMounted(() => {
  // 组件挂载后的初始化逻辑
})
</script>

<style scoped>
.modern-feature-card {
  position: relative;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 24px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  height: 100%;
  min-height: 320px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modern-feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--primary-400), var(--secondary-400));
  transform: scaleX(0);
  transition: transform 0.3s ease-out;
  z-index: 2;
}

.modern-feature-card:hover::before {
  transform: scaleX(1);
}

.modern-feature-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.15),
    0 10px 10px -5px rgba(0, 0, 0, 0.08);
}

.modern-feature-card.is-featured {
  background: linear-gradient(145deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.modern-feature-card:hover .gradient-overlay {
  opacity: 1;
}

.pattern-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.15) 1px, transparent 0);
  background-size: 20px 20px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.modern-feature-card:hover .pattern-overlay {
  opacity: 1;
}

.card-image-container {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.image-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.modern-feature-card:hover .card-image {
  transform: scale(1.1);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.modern-feature-card:hover .image-overlay {
  opacity: 1;
}

.hover-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  backdrop-filter: blur(10px);
}

.modern-feature-card:hover .hover-icon {
  transform: translate(-50%, -50%) scale(1);
}

.card-content {
  padding: 24px;
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-header {
  flex: 1;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.3;
  margin: 0 0 8px 0;
  color: inherit;
  transition: color 0.3s ease;
}

.card-description {
  font-size: 14px;
  line-height: 1.5;
  color: rgba(107, 114, 128, 1);
  margin: 0;
  transition: color 0.3s ease;
}

.modern-feature-card.is-featured .card-description {
  color: rgba(255, 255, 255, 0.8);
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.tag {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.modern-feature-card.is-featured .tag {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.progress-section {
  margin-top: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(107, 114, 128, 1);
}

.progress-value {
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
}

.progress-bar {
  height: 4px;
  background: rgba(107, 114, 128, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.card-actions {
  position: absolute;
  bottom: 24px;
  right: 24px;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
  z-index: 2;
}

.modern-feature-card:hover .card-actions {
  opacity: 1;
  transform: translateY(0);
}

.action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border-radius: 12px !important;
  text-transform: none !important;
  font-weight: 500 !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

.feature-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
}

.ripple-effect {
  position: absolute;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.3);
  transform: scale(0);
  animation: ripple 0.6s linear;
  pointer-events: none;
}

.ripple-active {
  animation: ripple 0.6s linear;
}

@keyframes ripple {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

/* 暗色主题适配 */
[data-theme="dark"] .modern-feature-card {
  background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
  border-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .card-description {
  color: rgba(148, 163, 184, 1);
}

[data-theme="dark"] .progress-label {
  color: rgba(148, 163, 184, 1);
}

/* 响应式设计 */
@media (max-width: 640px) {
  .modern-feature-card {
    min-height: 280px;
  }
  
  .card-image-container {
    height: 140px;
  }
  
  .card-content {
    padding: 16px;
  }
  
  .card-title {
    font-size: 18px;
  }
}
</style> 