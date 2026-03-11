<template>
  <div class="analytics-page">
    <div class="page-header">
      <div class="brand">
        <span class="brand-icon">🌐</span>
        <div class="brand-text">
          <strong>姜姓迁徙时空洞察</strong>
          <small>数据分析与可视化</small>
        </div>
      </div>
      <div class="header-actions">
        <button class="nav-button map-button" @click="$router.push('/')">
          <div class="button-content">
            <span class="button-icon">🗺️</span>
            <span class="button-text">返回地图</span>
          </div>
          <div class="button-glow"></div>
        </button>
        <button 
          v-if="isAdmin" 
          class="nav-button admin-button" 
          @click="$router.push('/admin')"
        >
          <div class="button-content">
            <span class="button-icon">⚙️</span>
            <span class="button-text">管理后台</span>
          </div>
          <div class="button-glow"></div>
        </button>
        <button 
          class="nav-button logout-button" 
          @click="handleLogout"
        >
          <div class="button-content">
            <span class="button-icon">🚪</span>
            <span class="button-text">退出登录</span>
          </div>
          <div class="button-glow"></div>
        </button>
      </div>
    </div>
    <migration-analytics :migrations="migrations" :loading="loading" :statistics="statistics" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { fetchMigrations, fetchStatistics } from '@/api/genealogy'
import { logout } from '@/api/auth'
import MigrationAnalytics from '@/views/MigrationAnalytics.vue'
import { ElButton, ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const migrations = ref([])
const loading = ref(true)
const statistics = ref({ branches: 0, locations: 0, migrations: 0, valid_migrations: 0 })



// 获取当前用户角色
const isAdmin = computed(() => {
  const userInfoStr = sessionStorage.getItem('userInfo')
  if (!userInfoStr) return false
  try {
    const userInfo = JSON.parse(userInfoStr)
    return userInfo && userInfo.role === 'admin'
  } catch (e) {
    console.error('解析用户信息失败:', e)
    return false
  }
})

onMounted(async () => {
  try {
    loading.value = true
    // 并行加载迁徙数据和统计数据
    const [migrationsData, statsData] = await Promise.all([
      fetchMigrations(),
      fetchStatistics()
    ])
    migrations.value = migrationsData
    statistics.value = statsData
    console.log('统计数据:', statsData)
  } catch (err) {
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
})

// 退出登录
async function handleLogout() {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出登录',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }
    )
    logout()
    ElMessage.success('已退出登录')
  } catch (error) {
    // 用户取消操作
    if (error !== 'cancel') {
      console.error('退出登录失败:', error)
    }
  }
}



// 计算大圆距离的函数
function calculateHaversineDistance(start, end) {
  const [lng1, lat1] = start;
  const [lng2, lat2] = end;
  const R = 6371; // 地球半径（公里）
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}
</script>

<style scoped>
.analytics-page {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 22px;
  background: linear-gradient(135deg, #ffffff 0%, #f5f7fb 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  z-index: 200;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  font-size: 22px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-text strong {
  font-size: 18px;
  color: #1f2937;
}

.brand-text small {
  color: #6b7280;
  font-size: 12px;
}

/* 导航按钮样式 */
.nav-button {
  position: relative;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}
      
.nav-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}
      
.nav-button:hover::before {
  left: 100%;
}
      
.nav-button:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}
      
.nav-button:active {
  transform: translateY(0);
  box-shadow: 
    0 2px 10px rgba(102, 126, 234, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}
      
.button-content {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}
      
.button-icon {
  font-size: 18px;
  display: flex;
  align-items: center;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}
      
.button-text {
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
      
.button-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}
      
.nav-button:hover .button-glow {
  opacity: 1;
}
      
/* 导出按钮特殊样式 */
.export-button {
  background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
}
      
.export-button:hover {
  box-shadow: 
    0 6px 20px rgba(16, 185, 129, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}

/* 地图按钮特殊样式 */
.map-button {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}
      
.map-button:hover {
  box-shadow: 
    0 6px 20px rgba(79, 172, 254, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}
      
.admin-button {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  margin-left: 10px;
}
      
.admin-button:hover {
  box-shadow: 
        0 6px 20px rgba(255, 107, 107, 0.5),
        0 0 0 1px rgba(255, 255, 255, 0.2) inset;
    }
    
    /* 导出选项对话框样式 */
    .export-options {
      padding: 10px 0;
    }
    
    .export-options .el-checkbox {
      margin: 10px 0;
      width: 100%;
    }
    
    .option-hint {
      margin-top: 15px;
      padding: 10px;
      background-color: #f5f7fa;
      border-radius: 4px;
      font-size: 12px;
      color: #909399;
    }
    
    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
</style>

