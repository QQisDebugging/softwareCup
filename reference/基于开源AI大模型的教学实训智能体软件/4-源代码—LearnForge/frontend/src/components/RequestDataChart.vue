<template>
   <v-col cols="12">
    <v-card class="chart-card " border flat >
      <v-card-title>
        {{ option.title.text }}
      </v-card-title>
      <v-card-text>
        <v-chart class="chart" :option="option" />
      </v-card-text>
    </v-card>
  </v-col>
  </template>
  
  <script setup>
  import { use } from "echarts/core";
  import { CanvasRenderer } from "echarts/renderers";
  import { LineChart } from "echarts/charts";
  import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent
  } from "echarts/components";
  import VChart from "vue-echarts";
  import axios from "axios";
  import { ref, onMounted, watch,onBeforeUnmount } from "vue";
  import { backendUrl } from '@/main';
  
  
  use([
    CanvasRenderer,
    LineChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent
  ]);
  
  const option = ref({
    title: {
      text: "近15天请求总数",
      left: "center"
    },
    tooltip: {
      trigger: "axis",
      formatter: "<br/>{b}  {c}"
    },
    legend: {
      orient: "horizontal",
      left: "center",
      top: "top"
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      data: []
    },
    yAxis: {
      type: "value"
    },
    series: [
      {
    
        type: "line",
        data: []
      }
    ]
  });
  
  onMounted(() => {
    fetchData();
    // 监听窗口大小变化，重新渲染图表
    window.addEventListener('resize', handleResize);
  });
  
  
  async function fetchData() {
    try {
      const response = await axios.get(`${backendUrl}/api/get15days`);
      const data = response.data;
  
      // 处理数据，确保即使数据为0或没有数据，柱状图也能显示空白或0值
      option.value.xAxis.data = data.map(entry => entry.request_date);
      option.value.series[0].data = data.map(entry => entry.total_requests || 0); // 如果数据为null或undefined，显示0
    } catch (error) {
      console.error("Error fetching data:", error);
      // 处理请求错误的情况，可以选择显示空白图表或者错误提示
      option.value.xAxis.data = [];
      option.value.series[0].data = [];
    }
  }
  
  
  function handleResize() {
    // 触发 ECharts 的 resize 方法，使图表自适应容器大小
    const chart = use().getInstanceByDom(document.querySelector('.chart'));
    if (chart) {
      chart.resize();
    }
  }
  
  // 在组件销毁时移除事件监听
  watch(() => {
    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
    });
  });
  </script>
  
  <style scoped>
  .chart-card {
    width: 100%;
  }
  
  .chart {
    height: 400px;
  }
  </style>
  