<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>数据概览</h2>
    </div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🏯</div>
        <div class="stat-info">
          <div class="stat-value">{{ statistics.branches }}</div>
          <div class="stat-label">家族分支</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📍</div>
        <div class="stat-info">
          <div class="stat-value">{{ statistics.locations }}</div>
          <div class="stat-label">地理地点</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🗺️</div>
        <div class="stat-info">
          <div class="stat-value">{{ statistics.migrations }}</div>
          <div class="stat-label">迁徙记录</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <div class="stat-value">{{ userCount }}</div>
          <div class="stat-label">注册用户</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchStatistics } from '@/api/genealogy'
import { getAllUsers } from '@/api/admin'

const statistics = ref({
  branches: 0,
  locations: 0,
  migrations: 0,
  valid_migrations: 0
})

const userCount = ref(0)

const loadStatistics = async () => {
  try {
    statistics.value = await fetchStatistics()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadUserCount = async () => {
  try {
    const users = await getAllUsers()
    userCount.value = users.length
  } catch (error) {
    console.error('加载用户数量失败:', error)
  }
}

onMounted(() => {
  loadStatistics()
  loadUserCount()
})
</script>

<style scoped>
.dashboard {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  height: 100%;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.page-header h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 48px;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}
</style>
