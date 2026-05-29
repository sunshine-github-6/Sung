<template>
  <div class="admin-layout">
    <div class="admin-header">
      <div class="brand">
        <span class="brand-icon">🌐</span>
        <div class="brand-text">
          <strong>姜姓迁徙溯源系统</strong>
          <small>管理员后台</small>
        </div>
      </div>
      <div class="header-actions">
        <span class="user-info">欢迎，{{ userInfo.username }}</span>
        <el-button @click="goToMap">查看地图视图</el-button>
        <el-button @click="goToAnalytics">查看数据视图</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </div>

    <div class="admin-content">
      <div class="admin-sidebar">
        <el-menu
          :default-active="activeMenu"
          @select="handleMenuSelect"
          class="admin-menu"
        >
          <el-menu-item index="dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>数据概览</span>
          </el-menu-item>

          <el-sub-menu index="data-management">
            <template #title>
              <el-icon><Collection /></el-icon>
              <span>数据管理</span>
            </template>
            <el-menu-item index="branches">
              <el-icon><OfficeBuilding /></el-icon>
              <span>家族分支</span>
            </el-menu-item>
            <el-menu-item index="locations">
              <el-icon><MapLocation /></el-icon>
              <span>地点管理</span>
            </el-menu-item>
            <el-menu-item index="migrations">
              <el-icon><Share /></el-icon>
              <span>迁徙记录</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="audit-management">
            <template #title>
              <el-icon><Checked /></el-icon>
              <span>审核管理</span>
            </template>
            <el-menu-item index="submissions">
              <el-icon><DocumentChecked /></el-icon>
              <span>迁徙提交审核</span>
            </el-menu-item>
            <el-menu-item index="password-reset">
              <el-icon><Key /></el-icon>
              <span>密码重置审核</span>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="users">
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </el-menu-item>

          <el-menu-item index="settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </div>

      <div class="admin-main">
        <Dashboard v-if="activeMenu === 'dashboard'" />
        <UserManagement v-else-if="activeMenu === 'users'" />
        <BranchManagement v-else-if="activeMenu === 'branches'" />
        <LocationManagement v-else-if="activeMenu === 'locations'" />
        <MigrationManagement v-else-if="activeMenu === 'migrations'" />
        <AuditManagement v-else-if="activeMenu === 'submissions' || activeMenu === 'password-reset'" :active-tab="auditActiveTab" />
        <SettingsPage v-else-if="activeMenu === 'settings'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { logout } from '@/api/auth'
import { HomeFilled, Collection, Checked, OfficeBuilding, MapLocation, Share, DocumentChecked, Key, UserFilled, Setting } from '@element-plus/icons-vue'
import Dashboard from '@/views/admin/Dashboard.vue'
import UserManagement from '@/views/admin/UserManagement.vue'
import BranchManagement from '@/views/admin/BranchManagement.vue'
import LocationManagement from '@/views/admin/LocationManagement.vue'
import MigrationManagement from '@/views/admin/MigrationManagement.vue'
import AuditManagement from '@/views/admin/AuditManagement.vue'
import SettingsPage from '@/views/SettingsPage.vue'

const router = useRouter()
const activeMenu = ref('dashboard')
const auditActiveTab = ref('submissions')
const userInfo = ref(JSON.parse(sessionStorage.getItem('userInfo') || '{}'))

const handleMenuSelect = (index) => {
  activeMenu.value = index
  if (index === 'submissions') {
    auditActiveTab.value = 'submissions'
  } else if (index === 'password-reset') {
    auditActiveTab.value = 'password-reset'
  }
}

const goToMap = () => {
  router.push('/')
}

const goToAnalytics = () => {
  router.push('/analytics')
}

const handleLogout = () => {
  logout()
}
</script>

<style scoped>
.admin-layout {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  color: #666;
  font-size: 14px;
}

.admin-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.admin-sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #e8e8e8;
}

.admin-menu {
  border-right: none;
}

.admin-menu .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.admin-menu .el-sub-menu .el-menu-item {
  padding-left: 48px !important;
}

.admin-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
