<template>
  <router-view />
</template>

<script setup>
// 主应用入口，使用 router-view 来显示不同的页面
</script>

<style>
/* 基础重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #1a202c;
  background-color: #faf9f7;
}

/* 全局过渡效果 */
* {
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

/* 排除不需要过渡的元素 */
.el-slider__button,
.el-switch__core,
.el-checkbox__inner,
.el-radio__inner {
  transition: all 0.2s ease;
}
</style>
