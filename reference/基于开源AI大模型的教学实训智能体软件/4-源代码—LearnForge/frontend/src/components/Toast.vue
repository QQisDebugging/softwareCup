<template>
  <div class="toast-container">
    <transition-group name="toast" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
        @click="removeToast(toast.id)"
      >
        <div class="toast-content">
          <v-icon v-if="toast.type === 'success'" color="white" size="20">mdi-check-circle</v-icon>
          <v-icon v-else-if="toast.type === 'error'" color="white" size="20">mdi-alert-circle</v-icon>
          <v-icon v-else-if="toast.type === 'warning'" color="white" size="20">mdi-alert</v-icon>
          <v-icon v-else color="white" size="20">mdi-information</v-icon>
          <span class="toast-message">{{ toast.message }}</span>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  name: 'Toast',
  data() {
    return {
      toasts: []
    }
  },
  mounted() {
    // 监听全局toast事件
    window.addEventListener('toast-show', this.handleToastShow);
  },
  beforeUnmount() {
    // 移除事件监听
    window.removeEventListener('toast-show', this.handleToastShow);
  },
  methods: {
    handleToastShow(event) {
      const { message, type } = event.detail;
      this.addToast(message, type);
    },
    
    addToast(message, type = 'info', duration = 3000) {
      const id = Date.now() + Math.random()
      const toast = {
        id,
        message,
        type,
        duration
      }
      
      this.toasts.push(toast)
      
      setTimeout(() => {
        this.removeToast(id)
      }, duration)
    },
    
    removeToast(id) {
      const index = this.toasts.findIndex(toast => toast.id === id)
      if (index > -1) {
        this.toasts.splice(index, 1)
      }
    },
    
    success(message, duration = 3000) {
      this.addToast(message, 'success', duration)
    },
    
    error(message, duration = 4000) {
      this.addToast(message, 'error', duration)
    },
    
    warning(message, duration = 3000) {
      this.addToast(message, 'warning', duration)
    },
    
    info(message, duration = 3000) {
      this.addToast(message, 'info', duration)
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  pointer-events: none;
}

.toast {
  background: #333;
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  pointer-events: auto;
  max-width: 300px;
  word-wrap: break-word;
}

.toast-success {
  background: #4CAF50;
}

.toast-error {
  background: #f44336;
}

.toast-warning {
  background: #ff9800;
}

.toast-info {
  background: #2196F3;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toast-message {
  font-size: 14px;
  line-height: 1.4;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style> 