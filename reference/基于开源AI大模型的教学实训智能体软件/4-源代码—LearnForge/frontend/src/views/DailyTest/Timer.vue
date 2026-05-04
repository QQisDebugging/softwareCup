<template>
    <div class="timer-container">
      <div class="timer-display">
        <div class="timer-label">
          <v-icon color="white" size="20" class="mr-1">mdi-clock-outline</v-icon>
          答题用时
        </div>
        <div class="timer-time">
          <span class="time-number">{{ formatTime(minutes) }}</span>
          <span class="time-separator">:</span>
          <span class="time-number">{{ formatTime(seconds) }}</span>
        </div>
        <div class="timer-units">
          <span class="time-unit">分</span>
          <span class="time-unit-separator"></span>
          <span class="time-unit">秒</span>
        </div>
      </div>
      <div class="timer-progress">
        <v-progress-linear
          :model-value="(currentTime / totalTime) * 100"
          height="4"
          color="white"
          bg-color="rgba(255,255,255,0.3)"
          rounded
        ></v-progress-linear>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        timer: null,
        totalTime: 600, // 总时间，单位：秒
        currentTime: 0, // 当前时间，单位：秒
      };
    },
    computed: {
      minutes() {
        return Math.floor(this.currentTime / 60);
      },
      seconds() {
        return this.currentTime % 60;
      },
    },
    created() {
      this.timer = setInterval(this.tick, 1000);
    },
    methods: {
      tick() {
        if (this.currentTime < this.totalTime) {
          this.currentTime++;
        } else {
          clearInterval(this.timer);
          // 在计时结束时触发 timeout 事件
          this.$emit('timeout');
        }
      },
      formatTime(time) {
        return time.toString().padStart(2, '0');
      },
    },
    beforeDestroy() {
      clearInterval(this.timer);
    },
  };
  </script>
  
  <style scoped>
  .timer-container {
    text-align: center;
    color: white;
  }
  
  .timer-display {
    margin-bottom: 16px;
  }
  
  .timer-label {
    font-size: 0.9rem;
    font-weight: 500;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.9;
  }
  
  .timer-time {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Roboto Mono', monospace;
  }
  
  .time-number {
    display: inline-block;
    min-width: 2ch;
    text-align: center;
  }
  
  .time-separator {
    margin: 0 8px;
    opacity: 0.8;
    animation: blink 1s infinite;
  }
  
  .timer-units {
    font-size: 0.75rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.8;
  }
  
  .time-unit {
    min-width: 2ch;
    text-align: center;
  }
  
  .time-unit-separator {
    margin: 0 8px;
  }
  
  .timer-progress {
    margin-top: 12px;
  }
  
  @keyframes blink {
    0%, 50% {
      opacity: 1;
    }
    51%, 100% {
      opacity: 0.3;
    }
  }
  
  @media (max-width: 480px) {
    .timer-time {
      font-size: 1.5rem;
    }
    
    .timer-label {
      font-size: 0.8rem;
    }
  }
  </style>
  