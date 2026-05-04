<template>
    <div class="tree-container">
      <div class="tree" :style="{ transform: `scaleY(${growthFactor})` }"></div>
    </div>
  </template>
  
  <script>
  import anime from 'animejs';
  
  export default {
    data() {
      return {
        growthFactor: 1, // 初始成长因子
      };
    },
    methods: {
      growTree(factor) {
        anime({
          targets: this.$data,
          growthFactor: factor,
          easing: 'easeInOutQuad',
          duration: 2000,
        });
      },
    },
  };
  </script>
  
  <style scoped>
  .tree-container {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    height: 300px;
    border: 1px solid #ddd;
  }
  
  .tree {
    width: 50px;
    height: 50px;
    background-color: green;
    transform-origin: bottom;
  }
  </style>
  