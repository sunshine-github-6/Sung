<template>
  <div class="settings-container">
    <!-- 左侧配置菜单 -->
    <div class="settings-sidebar">
      <el-menu
        :default-active="activeMenu"
        @select="handleMenuSelect"
        class="settings-menu"
      >
        <el-menu-item index="general">
          <el-icon><Tools /></el-icon>
          <span>通用配置</span>
        </el-menu-item>

        <el-menu-item index="database">
          <el-icon><Coin /></el-icon>
          <span>数据库配置</span>
        </el-menu-item>

        <el-menu-item index="map">
          <el-icon><MapLocation /></el-icon>
          <span>地图配置</span>
        </el-menu-item>

        <el-menu-item index="security">
          <el-icon><Lock /></el-icon>
          <span>安全配置</span>
        </el-menu-item>

        <el-menu-item index="display">
          <el-icon><Brush /></el-icon>
          <span>显示配置</span>
        </el-menu-item>

        <el-menu-item index="backup">
          <el-icon><Download /></el-icon>
          <span>备份恢复</span>
        </el-menu-item>

        <el-menu-item index="logs">
          <el-icon><List /></el-icon>
          <span>系统日志</span>
        </el-menu-item>
      </el-menu>
    </div>

      <!-- 右侧配置内容区 -->
      <div class="settings-main">
        <!-- 通用配置 -->
        <div v-if="activeMenu === 'general'" class="config-section">
          <div class="section-header">
            <h2>⚙️ 通用配置</h2>
            <p class="section-desc">配置系统的基本参数和运行设置</p>
          </div>
          
          <el-form :model="generalConfig" label-position="top" class="config-form">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="系统名称">
                  <el-input v-model="generalConfig.systemName" placeholder="请输入系统名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="系统版本">
                  <el-input v-model="generalConfig.systemVersion" disabled />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="系统描述">
              <el-input 
                v-model="generalConfig.systemDescription" 
                type="textarea" 
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="默认分页大小">
                  <el-input-number v-model="generalConfig.pageSize" :min="10" :max="100" :step="5" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="数据缓存时间(分钟)">
                  <el-input-number v-model="generalConfig.cacheTime" :min="5" :max="120" :step="5" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="系统维护模式">
              <el-switch
                v-model="generalConfig.maintenanceMode"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveGeneralConfig" :loading="saving">
                <span class="btn-icon">💾</span> 保存配置
              </el-button>
              <el-button @click="resetGeneralConfig">
                <span class="btn-icon">🔄</span> 重置
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 数据库配置 -->
        <div v-else-if="activeMenu === 'database'" class="config-section">
          <div class="section-header">
            <h2>🗄️ 数据库配置</h2>
            <p class="section-desc">配置数据库连接参数（修改后需要重启服务）</p>
          </div>
          
          <el-alert
            title="警告：修改数据库配置可能导致系统无法正常运行，请谨慎操作！"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          />
          
          <el-form :model="databaseConfig" label-position="top" class="config-form">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="数据库主机">
                  <el-input v-model="databaseConfig.host" placeholder="localhost" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="数据库端口">
                  <el-input-number v-model="databaseConfig.port" :min="1" :max="65535" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="数据库名称">
                  <el-input v-model="databaseConfig.database" placeholder="Origin_Tracing" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="数据库用户">
                  <el-input v-model="databaseConfig.username" placeholder="root" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="数据库密码">
              <el-input 
                v-model="databaseConfig.password" 
                type="password" 
                show-password
                placeholder="请输入数据库密码"
              />
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="连接池大小">
                  <el-input-number v-model="databaseConfig.poolSize" :min="1" :max="50" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="连接超时时间(秒)">
                  <el-input-number v-model="databaseConfig.timeout" :min="5" :max="300" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button type="primary" @click="handleTestDatabaseConnection" :loading="testing">
                <span class="btn-icon">🔗</span> 测试连接
              </el-button>
              <el-button type="success" @click="saveDatabaseConfig" :loading="saving">
                <span class="btn-icon">💾</span> 保存配置
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 地图配置 -->
        <div v-else-if="activeMenu === 'map'" class="config-section">
          <div class="section-header">
            <h2>🗺️ 地图配置</h2>
            <p class="section-desc">配置高德地图API和其他地图相关参数</p>
          </div>
          
          <el-form :model="mapConfig" label-position="top" class="config-form">
            <el-form-item label="高德地图API Key">
              <el-input v-model="mapConfig.amapKey" placeholder="请输入高德地图API Key">
                <template #append>
                  <el-button @click="openAmapDev">获取Key</el-button>
                </template>
              </el-input>
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="默认经度">
                  <el-input-number v-model="mapConfig.defaultLng" :precision="6" :step="0.1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="默认纬度">
                  <el-input-number v-model="mapConfig.defaultLat" :precision="6" :step="0.1" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="默认缩放级别">
              <el-slider v-model="mapConfig.defaultZoom" :min="3" :max="18" show-stops />
            </el-form-item>
            
            <el-form-item label="地图样式">
              <el-radio-group v-model="mapConfig.mapStyle">
                <el-radio label="normal">标准</el-radio>
                <el-radio label="dark">暗色</el-radio>
                <el-radio label="light">浅色</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="启用热力图">
              <el-switch v-model="mapConfig.enableHeatmap" />
            </el-form-item>
            
            <el-form-item label="热力图半径">
              <el-slider v-model="mapConfig.heatmapRadius" :min="5" :max="50" :disabled="!mapConfig.enableHeatmap" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveMapConfig" :loading="saving">
                <span class="btn-icon">💾</span> 保存配置
              </el-button>
              <el-button @click="resetMapConfig">
                <span class="btn-icon">🔄</span> 重置
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 安全配置 -->
        <div v-else-if="activeMenu === 'security'" class="config-section">
          <div class="section-header">
            <h2>🔐 安全配置</h2>
            <p class="section-desc">配置系统安全相关参数</p>
          </div>
          
          <el-form :model="securityConfig" label-position="top" class="config-form">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Token过期时间(小时)">
                  <el-input-number v-model="securityConfig.tokenExpireHours" :min="1" :max="168" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="最大登录失败次数">
                  <el-input-number v-model="securityConfig.maxLoginAttempts" :min="3" :max="10" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="密码最小长度">
                  <el-input-number v-model="securityConfig.passwordMinLength" :min="6" :max="20" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="登录锁定时间(分钟)">
                  <el-input-number v-model="securityConfig.lockoutDuration" :min="5" :max="60" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="启用登录验证码">
              <el-switch v-model="securityConfig.enableCaptcha" />
            </el-form-item>
            
            <el-form-item label="允许跨域访问">
              <el-switch v-model="securityConfig.enableCors" />
            </el-form-item>
            
            <el-form-item label="允许的域名" v-if="securityConfig.enableCors">
              <el-select
                v-model="securityConfig.allowedOrigins"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="请输入允许的域名"
                style="width: 100%;"
              >
                <el-option
                  v-for="origin in defaultOrigins"
                  :key="origin"
                  :label="origin"
                  :value="origin"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveSecurityConfig" :loading="saving">
                <span class="btn-icon">💾</span> 保存配置
              </el-button>
              <el-button @click="resetSecurityConfig">
                <span class="btn-icon">🔄</span> 重置
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 显示配置 -->
        <div v-else-if="activeMenu === 'display'" class="config-section">
          <div class="section-header">
            <h2>🎨 显示配置</h2>
            <p class="section-desc">配置系统的显示样式和主题</p>
          </div>
          
          <el-form :model="displayConfig" label-position="top" class="config-form">
            <el-form-item label="主题颜色">
              <el-color-picker v-model="displayConfig.primaryColor" show-alpha />
            </el-form-item>
            
            <el-form-item label="侧边栏主题">
              <el-radio-group v-model="displayConfig.sidebarTheme">
                <el-radio label="light">浅色</el-radio>
                <el-radio label="dark">深色</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="导航栏主题">
              <el-radio-group v-model="displayConfig.headerTheme">
                <el-radio label="light">浅色</el-radio>
                <el-radio label="dark">深色</el-radio>
                <el-radio label="primary">主色</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="每页显示记录数">
              <el-select v-model="displayConfig.pageSizeOptions" multiple style="width: 100%;">
                <el-option label="10条" :value="10" />
                <el-option label="20条" :value="20" />
                <el-option label="50条" :value="50" />
                <el-option label="100条" :value="100" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="启用动画效果">
              <el-switch v-model="displayConfig.enableAnimation" />
            </el-form-item>
            
            <el-form-item label="显示面包屑导航">
              <el-switch v-model="displayConfig.showBreadcrumb" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveDisplayConfig" :loading="saving">
                <span class="btn-icon">💾</span> 保存配置
              </el-button>
              <el-button @click="resetDisplayConfig">
                <span class="btn-icon">🔄</span> 重置
              </el-button>
              <el-button type="success" @click="applyDisplayConfig">
                <span class="btn-icon">✨</span> 立即应用
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 备份恢复 -->
        <div v-else-if="activeMenu === 'backup'" class="config-section">
          <div class="section-header">
            <h2>💾 备份恢复</h2>
            <p class="section-desc">管理系统数据备份和恢复</p>
          </div>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="backup-card">
                <template #header>
                  <div class="card-header">
                    <span>📦 数据备份</span>
                  </div>
                </template>
                <div class="backup-content">
                  <p>备份系统所有数据，包括：</p>
                  <ul>
                    <li>家族分支数据</li>
                    <li>地理地点数据</li>
                    <li>迁徙记录数据</li>
                    <li>用户数据</li>
                    <li>系统配置</li>
                  </ul>
                  <el-button type="primary" @click="handleCreateBackup" :loading="backingUp" style="width: 100%; margin-top: 15px;">
                    <span class="btn-icon">📦</span> 立即备份
                  </el-button>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card class="backup-card">
                <template #header>
                  <div class="card-header">
                    <span>🔄 数据恢复</span>
                  </div>
                </template>
                <div class="backup-content">
                  <p>从备份文件恢复数据：</p>
                  <el-upload
                    class="upload-demo"
                    drag
                    action="/api/settings/restore"
                    :on-success="handleRestoreSuccess"
                    :on-error="handleRestoreError"
                    accept=".sql,.json,.zip"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      拖拽文件到此处或 <em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 .sql, .json, .zip 格式的备份文件
                      </div>
                    </template>
                  </el-upload>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-divider />
          
          <div class="backup-list">
            <h3>📋 备份历史</h3>
            <el-table :data="backupList" style="width: 100%">
              <el-table-column prop="filename" label="文件名" />
              <el-table-column prop="size" label="大小" width="120" />
              <el-table-column prop="createdAt" label="创建时间" width="180" />
              <el-table-column label="操作" width="200">
                <template #default="scope">
                  <el-button size="small" @click="handleDownloadBackup(scope.row)">下载</el-button>
                      <el-button size="small" type="danger" @click="handleDeleteBackup(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 系统日志 -->
        <div v-else-if="activeMenu === 'logs'" class="config-section">
          <div class="section-header">
            <h2>📋 系统日志</h2>
            <p class="section-desc">查看系统运行日志和操作记录</p>
          </div>
          
          <div class="logs-filter">
            <el-row :gutter="15">
              <el-col :span="6">
                <el-select v-model="logFilter.level" placeholder="日志级别">
                  <el-option label="全部" value="" />
                  <el-option label="DEBUG" value="debug" />
                  <el-option label="INFO" value="info" />
                  <el-option label="WARNING" value="warning" />
                  <el-option label="ERROR" value="error" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-select v-model="logFilter.type" placeholder="日志类型">
                  <el-option label="全部" value="" />
                  <el-option label="系统" value="system" />
                  <el-option label="操作" value="operation" />
                  <el-option label="安全" value="security" />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-date-picker
                  v-model="logFilter.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  style="width: 100%;"
                />
              </el-col>
              <el-col :span="4">
                <el-button type="primary" @click="searchLogs">
                  <span class="btn-icon">🔍</span> 查询
                </el-button>
                <el-button @click="exportLogs">
                  <span class="btn-icon">📤</span> 导出
                </el-button>
              </el-col>
            </el-row>
          </div>
          
          <el-table :data="logList" style="width: 100%; margin-top: 20px;" height="500">
            <el-table-column type="index" width="50" />
            <el-table-column prop="timestamp" label="时间" width="180" />
            <el-table-column prop="level" label="级别" width="100">
              <template #default="scope">
                <el-tag :type="getLogLevelType(scope.row.level)">{{ scope.row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="message" label="内容" show-overflow-tooltip />
            <el-table-column prop="user" label="用户" width="120" />
            <el-table-column prop="ip" label="IP地址" width="140" />
          </el-table>
          
          <el-pagination
            v-model:current-page="logPage"
            v-model:page-size="logPageSize"
            :total="logTotal"
            layout="total, sizes, prev, pager, next"
            @size-change="handleLogSizeChange"
            @current-change="handleLogPageChange"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Tools, Coin, Lock, Brush, Download, List } from '@element-plus/icons-vue'
import {
  getSettings,
  updateSettings,
  testDatabaseConnection,
  createBackup,
  getBackups,
  deleteBackup,
  downloadBackup,
  getSystemLogs,
  restoreBackup
} from '@/api/settings.js'

// 当前激活的菜单
const activeMenu = ref('general')

// 加载状态
const saving = ref(false)
const testing = ref(false)
const backingUp = ref(false)

// 通用配置
const generalConfig = reactive({
  systemName: '姜姓迁徙溯源系统',
  systemVersion: '1.0.0',
  systemDescription: '用于记录和分析姜姓家族迁徙历史的系统',
  pageSize: 20,
  cacheTime: 30,
  maintenanceMode: false
})

// 数据库配置
const databaseConfig = reactive({
  host: 'localhost',
  port: 3306,
  database: 'Origin_Tracing',
  username: 'root',
  password: '',
  poolSize: 10,
  timeout: 30
})

// 地图配置
const mapConfig = reactive({
  amapKey: '',
  defaultLng: 108.0,
  defaultLat: 34.0,
  defaultZoom: 5,
  mapStyle: 'normal',
  enableHeatmap: true,
  heatmapRadius: 25
})

// 安全配置
const securityConfig = reactive({
  tokenExpireHours: 24,
  maxLoginAttempts: 5,
  passwordMinLength: 6,
  lockoutDuration: 30,
  enableCaptcha: false,
  enableCors: true,
  allowedOrigins: ['http://localhost:5173', 'http://localhost:5174']
})

const defaultOrigins = [
  'http://localhost:5173',
  'http://localhost:5174',
  'http://localhost:5175'
]

// 显示配置
const displayConfig = reactive({
  primaryColor: '#409EFF',
  sidebarTheme: 'dark',
  headerTheme: 'light',
  pageSizeOptions: [10, 20, 50, 100],
  enableAnimation: true,
  showBreadcrumb: true
})

// 备份列表
const backupList = ref([
  { filename: 'backup_20260317_120000.sql', size: '2.5MB', createdAt: '2026-03-17 12:00:00' },
  { filename: 'backup_20260316_120000.sql', size: '2.4MB', createdAt: '2026-03-16 12:00:00' }
])

// 日志相关
const logFilter = reactive({
  level: '',
  type: '',
  dateRange: []
})

const logList = ref([
  { timestamp: '2026-03-17 10:30:00', level: 'INFO', type: '操作', message: '用户 admin 登录系统', user: 'admin', ip: '127.0.0.1' },
  { timestamp: '2026-03-17 10:25:00', level: 'INFO', type: '系统', message: '系统启动成功', user: 'system', ip: '-' },
  { timestamp: '2026-03-17 10:20:00', level: 'WARNING', type: '安全', message: '登录失败次数过多，IP已锁定', user: '-', ip: '192.168.1.100' }
])

const logPage = ref(1)
const logPageSize = ref(20)
const logTotal = ref(100)

// 菜单选择
const handleMenuSelect = (index) => {
  activeMenu.value = index
}

// 通用配置方法
const saveGeneralConfig = async () => {
  saving.value = true
  try {
    await updateSettings('general', generalConfig)
    ElMessage.success('通用配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

const resetGeneralConfig = () => {
  generalConfig.systemName = '姜姓迁徙溯源系统'
  generalConfig.pageSize = 20
  generalConfig.cacheTime = 30
  generalConfig.maintenanceMode = false
  ElMessage.info('已重置为默认值')
}

// 数据库配置方法
const handleTestDatabaseConnection = async () => {
  testing.value = true
  try {
    const result = await testDatabaseConnection(databaseConfig)
    ElMessage.success(result.message || '数据库连接测试成功')
  } catch (error) {
    ElMessage.error('连接失败：' + error.message)
  } finally {
    testing.value = false
  }
}

const saveDatabaseConfig = async () => {
  saving.value = true
  try {
    await updateSettings('database', databaseConfig)
    ElMessage.success('数据库配置保存成功，重启后生效')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

// 地图配置方法
const openAmapDev = () => {
  window.open('https://lbs.amap.com/dev/', '_blank')
}

const saveMapConfig = async () => {
  saving.value = true
  try {
    await updateSettings('map', mapConfig)
    ElMessage.success('地图配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

const resetMapConfig = () => {
  mapConfig.amapKey = import.meta.env.VITE_AMAP_KEY || ''
  mapConfig.defaultLng = 108.0
  mapConfig.defaultLat = 34.0
  mapConfig.defaultZoom = 5
  mapConfig.mapStyle = 'normal'
  mapConfig.enableHeatmap = true
  mapConfig.heatmapRadius = 25
  ElMessage.info('已重置为默认值')
}

// 安全配置方法
const saveSecurityConfig = async () => {
  saving.value = true
  try {
    await updateSettings('security', securityConfig)
    ElMessage.success('安全配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

const resetSecurityConfig = () => {
  securityConfig.tokenExpireHours = 24
  securityConfig.maxLoginAttempts = 5
  securityConfig.passwordMinLength = 6
  securityConfig.lockoutDuration = 30
  securityConfig.enableCaptcha = false
  securityConfig.enableCors = true
  ElMessage.info('已重置为默认值')
}

// 显示配置方法
const saveDisplayConfig = async () => {
  saving.value = true
  try {
    await updateSettings('display', displayConfig)
    ElMessage.success('显示配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

const resetDisplayConfig = () => {
  displayConfig.primaryColor = '#409EFF'
  displayConfig.sidebarTheme = 'dark'
  displayConfig.headerTheme = 'light'
  displayConfig.pageSizeOptions = [10, 20, 50, 100]
  displayConfig.enableAnimation = true
  displayConfig.showBreadcrumb = true
  ElMessage.info('已重置为默认值')
}

const applyDisplayConfig = () => {
  ElMessage.success('显示配置已应用')
}

// 备份恢复方法
const handleCreateBackup = async () => {
  backingUp.value = true
  try {
    const result = await createBackup()
    ElMessage.success(result.message || '备份创建成功')
    // 刷新备份列表
    await loadBackups()
  } catch (error) {
    ElMessage.error('备份失败：' + error.message)
  } finally {
    backingUp.value = false
  }
}

// 加载备份列表
const loadBackups = async () => {
  try {
    const backups = await getBackups()
    backupList.value = backups
  } catch (error) {
    console.error('加载备份列表失败:', error)
  }
}

const handleRestoreSuccess = () => {
  ElMessage.success('数据恢复成功')
}

const handleRestoreError = () => {
  ElMessage.error('数据恢复失败')
}

const handleDownloadBackup = (backup) => {
  downloadBackup(backup.filename)
  ElMessage.success(`开始下载：${backup.filename}`)
}

const handleDeleteBackup = async (backup) => {
  try {
    await ElMessageBox.confirm(`确定要删除备份 ${backup.filename} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteBackup(backup.filename)
    ElMessage.success('备份已删除')
    // 刷新备份列表
    await loadBackups()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

// 日志方法
const getLogLevelType = (level) => {
  const types = {
    'DEBUG': 'info',
    'INFO': 'success',
    'WARNING': 'warning',
    'ERROR': 'danger'
  }
  return types[level] || 'info'
}

const searchLogs = async () => {
  try {
    const params = {
      level: logFilter.level,
      type: logFilter.type,
      page: logPage.value,
      pageSize: logPageSize.value
    }
    
    if (logFilter.dateRange && logFilter.dateRange.length === 2) {
      params.startDate = logFilter.dateRange[0].toISOString().split('T')[0]
      params.endDate = logFilter.dateRange[1].toISOString().split('T')[0]
    }
    
    const result = await getSystemLogs(params)
    logList.value = result.logs || []
    logTotal.value = result.total || 0
  } catch (error) {
    ElMessage.error('查询日志失败：' + error.message)
  }
}

const exportLogs = () => {
  const params = {
    level: logFilter.level,
    type: logFilter.type
  }
  
  if (logFilter.dateRange && logFilter.dateRange.length === 2) {
    params.startDate = logFilter.dateRange[0].toISOString().split('T')[0]
    params.endDate = logFilter.dateRange[1].toISOString().split('T')[0]
  }
  
  exportLogs(params)
  ElMessage.success('日志导出成功')
}

const handleLogSizeChange = (size) => {
  logPageSize.value = size
  searchLogs()
}

const handleLogPageChange = (page) => {
  logPage.value = page
  searchLogs()
}

// 加载配置
const loadSettings = async () => {
  try {
    const settings = await getSettings()
    
    // 更新各配置
    if (settings.general) {
      Object.assign(generalConfig, settings.general)
    }
    if (settings.database) {
      Object.assign(databaseConfig, settings.database)
    }
    if (settings.map) {
      Object.assign(mapConfig, settings.map)
    }
    if (settings.security) {
      Object.assign(securityConfig, settings.security)
    }
    if (settings.display) {
      Object.assign(displayConfig, settings.display)
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.warning('加载配置失败，使用默认配置')
  }
}

onMounted(() => {
  // 加载配置数据
  loadSettings()
  loadBackups()
  searchLogs()
})
</script>

<style scoped>
.settings-container {
  display: flex;
  height: 100%;
  background: white;
}

.settings-sidebar {
  width: 220px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  padding: 15px 0;
  flex-shrink: 0;
}

.settings-menu {
  border-right: none;
  background: transparent;
}

.settings-menu .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.settings-menu :deep(.el-menu-item) {
  font-size: 14px;
  height: 50px;
  line-height: 50px;
}

.settings-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #667eea15 0%, #764ba215 100%);
  color: #667eea;
  border-right: 3px solid #667eea;
}

.settings-main {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background: white;
}

.config-section {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.section-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.section-desc {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.config-form {
  max-width: 800px;
}

.config-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.backup-card {
  height: 100%;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.backup-content {
  padding: 10px 0;
}

.backup-content p {
  margin: 0 0 10px 0;
  color: #606266;
}

.backup-content ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.backup-content li {
  margin: 5px 0;
}

.backup-list {
  margin-top: 30px;
}

.backup-list h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
}

.logs-filter {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

@media (max-width: 768px) {
  .settings-container {
    flex-direction: column;
  }
  
  .settings-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .settings-main {
    padding: 20px;
  }
}
</style>
