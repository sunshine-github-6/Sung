// src/config/index.js
export default {
  amap: {
    key: import.meta.env.VITE_AMAP_KEY || 'YOUR_AMAP_KEY',
    version: '2.0',
    plugins: [
      'AMap.Scale',
      'AMap.MapType',
      'AMap.ControlBar',
      'AMap.HawkEye',
      'AMap.ToolBar',
      'AMap.HeatMap'
    ],
    loaderConfig: {
      lazy: true,
      useAMapUI: false,
      Loca: null,
      timeout: 3000
    }
  },
  apiBaseUrl: ''
}