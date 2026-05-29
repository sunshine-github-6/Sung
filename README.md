# Origin Tracing System

祖籍溯源系统 - 基于地理信息的家族迁徙轨迹可视化平台

## 项目简介

这是一个基于现代Web技术构建的家族迁徙轨迹可视化系统，旨在帮助用户追溯家族历史，查看家族在不同历史时期的迁徙路线，并提供交互式地图展示功能。

## 技术栈

### 后端
- **框架**: Flask 3.0.0
- **数据库**: MySQL + SQLAlchemy ORM
- **跨域处理**: Flask-CORS
- **数据处理**: Pandas, Matplotlib
- **文档生成**: ReportLab (PDF)

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **地图API**: 高德地图 JS API
- **数据可视化**: ECharts
- **HTTP客户端**: Axios
- **富文本编辑器**: WangEditor

## 项目结构

```
Origin_TracingSystem/
├── Origin_TracingSystem/          # 后端代码
│   ├── app.py                     # Flask主应用
│   ├── config.py                  # 配置文件
│   ├── models.py                  # 数据模型
│   ├── init_data.py               # 数据初始化脚本
│   ├── requirements.txt           # Python依赖
│   ├── sql/                       # SQL文件
│   │   └── Origin_Tracing.sql     # 数据库表结构
│   └── tests/                     # 测试文件
│       ├── test_api.py
│       ├── test_models.py
│       └── conftest.py
│
├── Origin_TracingSystem_frontend/ # 前端代码
│   ├── src/
│   │   ├── api/                   # API接口封装
│   │   │   ├── admin.js
│   │   │   ├── auth.js
│   │   │   ├── favorites.js
│   │   │   ├── genealogy.js
│   │   │   └── settings.js
│   │   ├── components/            # 公共组件
│   │   │   ├── common/
│   │   │   │   ├── CommonFilter.vue
│   │   │   │   ├── CommonPagination.vue
│   │   │   │   └── CommonTable.vue
│   │   │   ├── LocationPicker.vue
│   │   │   └── MigrationStepForm.vue
│   │   ├── config/                # 配置文件
│   │   ├── layouts/               # 布局组件
│   │   │   └── AdminLayout.vue
│   │   ├── router/                # 路由配置
│   │   ├── styles/                # 样式文件
│   │   ├── utils/                 # 工具函数
│   │   │   └── amap.js
│   │   ├── views/                 # 页面视图
│   │   │   ├── admin/             # 管理员页面
│   │   │   │   ├── Dashboard.vue
│   │   │   │   ├── UserManagement.vue
│   │   │   │   ├── BranchManagement.vue
│   │   │   │   ├── LocationManagement.vue
│   │   │   │   ├── MigrationManagement.vue
│   │   │   │   └── AuditManagement.vue
│   │   │   ├── LoginPage.vue
│   │   │   ├── MapPage.vue
│   │   │   ├── AnalyticsPage.vue
│   │   │   ├── MigrationAnalytics.vue
│   │   │   ├── ForgotPassword.vue
│   │   │   ├── SettingsPage.vue
│   │   │   └── SubmissionPage.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 功能特性

### 用户功能
- **用户注册/登录**: 支持用户注册和登录认证
- **地图可视化**: 在高德地图上展示家族迁徙轨迹
- **迁徙轨迹浏览**: 查看不同家族分支的迁徙历史
- **数据搜索**: 支持按姓氏、地名、迁徙原因等条件搜索
- **收藏功能**: 用户可收藏感兴趣的家族分支
- **信息提交**: 用户可提交新的迁徙口述史记录
- **密码找回**: 支持密码重置申请
- **个人设置**: 用户个人信息管理

### 管理员功能
- **仪表盘**: 系统数据统计和概览
- **用户管理**: 管理系统用户（增删改查、重置密码）
- **分支管理**: 管理家族分支信息
- **地点管理**: 管理历史地理地点及其坐标
- **迁徙管理**: 管理迁徙记录
- **审核管理**: 审核用户提交的迁徙记录
- **密码重置审核**: 处理用户密码重置申请

### 数据可视化
- **迁徙路线图**: 在地图上绘制迁徙轨迹
- **统计图表**: 使用ECharts展示数据分析结果
- **PDF报告**: 支持生成PDF格式的家族迁徙报告

## 环境要求

### 后端
- Python >= 3.8
- MySQL >= 5.7
- pip

### 前端
- Node.js >= 20.19.0
- npm

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/sunshine-github-6/Sung.git
cd Sung
```

### 2. 配置数据库

创建MySQL数据库并导入初始数据：

```bash
mysql -u root -p
CREATE DATABASE Origin_Tracing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

导入数据库结构：

```bash
mysql -u root -p Origin_Tracing < Origin_TracingSystem/sql/Origin_Tracing.sql
```

### 3. 配置环境变量

创建环境变量或修改 `config.py`：

```bash
# Windows PowerShell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="your_password"
$env:DB_NAME="Origin_Tracing"
$env:SECRET_KEY="your_secret_key"
```

### 4. 启动后端服务

```bash
cd Origin_TracingSystem
pip install -r requirements.txt
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 5. 启动前端服务

```bash
cd Origin_TracingSystem_frontend
npm install
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

### 6. 配置高德地图

在 `Origin_TracingSystem_frontend/src/config/index.js` 中配置高德地图密钥：

```javascript
export default {
  amap: {
    key: 'your-amap-api-key',
    version: '2.0',
    plugins: ['AMap.ToolBar', 'AMap.Scale', 'AMap.Geocoder']
  }
}
```

或通过环境变量 `VITE_AMAP_KEY` 设置。

## API文档

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/user-info` - 获取用户信息

### 数据接口
- `GET /api/branches` - 获取家族分支列表
- `GET /api/locations` - 获取地点列表
- `POST /api/locations` - 创建新地点
- `GET /api/migrations` - 获取迁徙记录列表
- `POST /api/migrations` - 创建迁徙记录
- `GET /api/migrations-geojson` - 获取GeoJSON格式迁徙数据

### 统计接口
- `GET /api/statistics` - 获取系统统计数据

### 管理员接口
- `GET /api/admin/users` - 获取用户列表
- `PUT /api/admin/users/:id` - 更新用户信息
- `DELETE /api/admin/users/:id` - 删除用户
- `GET /api/admin/submissions/migration` - 获取提交记录
- `PUT /api/admin/submissions/migration/:id` - 审核提交记录

## 数据库设计

### 主要表结构

| 表名 | 说明 |
|------|------|
| branches | 家族分支表 |
| locations | 地理地点表 |
| migrations | 迁徙事件表 |
| users | 用户表 |
| submissions | 用户提交记录表 |
| password_reset_requests | 密码重置请求表 |
| user_favorites | 用户收藏表 |
| system_meta | 系统元数据表 |

## 配置说明

### 后端配置

编辑 `Origin_TracingSystem/config.py` 或设置环境变量：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| DB_HOST | localhost | 数据库主机地址 |
| DB_PORT | 3306 | 数据库端口 |
| DB_USER | root | 数据库用户名 |
| DB_PASSWORD | - | 数据库密码 |
| DB_NAME | Origin_Tracing | 数据库名 |
| SECRET_KEY | - | Flask密钥 |

### 前端配置

编辑 `Origin_TracingSystem_frontend/src/config/index.js` 或设置环境变量：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| VITE_API_BASE_URL | http://localhost:5000 | 后端API地址 |
| VITE_AMAP_KEY | - | 高德地图API密钥 |

## 开发说明

### 运行测试

```bash
cd Origin_TracingSystem
pytest tests/ -v
```

### 前端构建

```bash
cd Origin_TracingSystem_frontend
npm run build
```

## 注意事项

1. **高德地图密钥**: 需在高德地图开放平台申请 Web 服务密钥
2. **数据库连接**: 确保MySQL服务正常运行并已创建数据库
3. **跨域配置**: 后端已配置CORS支持 `localhost:5173-5176` 端口
4. **中文支持**: 确保系统已安装中文字体（如SimHei）

## 致谢

特别感谢 **王晨瑜女士**，本项目的第一位用户，在开发过程中给予了宝贵的反馈和支持。❤️

## 开源协议

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request！
