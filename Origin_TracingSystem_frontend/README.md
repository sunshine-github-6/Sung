# Origin Tracing System Frontend

族谱迁徙轨迹可视化系统前端

## 项目介绍

这是一个基于 Vue 3 + Vite + 高德地图 API 构建的族谱迁徙轨迹可视化系统。该系统可以展示家族成员在不同历史时期的迁徙路线，并提供相关的详细信息查看功能。

## 技术栈

- Vue 3 (Composition API)
- Vite
- Element Plus
- 高德地图 JS API
- Axios

## 项目结构

```
src/
├── api/              # API 接口封装
├── components/       # 公共组件
├── config/           # 配置文件
├── router/           # 路由配置
├── utils/            # 工具函数
├── App.vue           # 根组件
└── main.js           # 入口文件
```

## 环境要求

- Node.js >= 20.19.0

## 安装与启动

1. 安装依赖：
   ```bash
   npm install
   ```

2. 启动开发服务器：
   ```bash
   npm run dev
   ```

3. 构建生产版本：
   ```bash
   npm run build
   ```

## 配置说明

### 高德地图配置

在 `src/config/index.js` 中配置高德地图的密钥和版本：

```javascript
amap: {
  key: 'your-amap-key',
  version: '2.0',
  plugins: ['AMap.ToolBar', 'AMap.Scale']
}
```

### 后端 API 地址

可以通过环境变量 `VITE_API_BASE_URL` 设置后端 API 地址，默认为 `http://localhost:5000`。

## 功能特性

- 基于高德地图的迁徙轨迹可视化
- 交互式信息展示
- 响应式设计适配不同屏幕尺寸

## 注意事项

1. 需要在高德地图开放平台申请 Web 服务密钥
2. 确保后端服务正常运行并与前端配置的地址一致