// src/config/index.js
export default {
  // 高德地图配置
  amap: {
    key: '9ed83e59737c21e8703bcd241ae62400',
    version: '2.0',  // 使用最新稳定版本以获得更好性能
    plugins: [
      'AMap.Scale',        // 比例尺
      'AMap.MapType',      // 地图类型切换
      'AMap.ControlBar',   // 缩略图控件（含指南针）
      'AMap.HawkEye',      // 鹰眼概览图
      'AMap.ToolBar',      // 工具条控件
      'AMap.HeatMap'       // 热力图
    ],
    // JSAPI Loader 特定配置
    loaderConfig: {
      lazy: true,         // 启用懒加载
      useAMapUI: false,   // 禁用AMapUI，避免加载超时
      Loca: null,         // 明确禁用Loca
      timeout: 3000       // 设置加载超时时间
    }
  },
  // 后端API地址
  apiBaseUrl: ''
}