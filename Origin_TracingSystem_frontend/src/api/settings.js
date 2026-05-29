import axios from 'axios'

// 创建 axios 实例
const apiClient = axios.create({
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 获取系统配置
 * @returns {Promise<Object>} 系统配置对象
 */
export async function getSettings() {
  try {
    const response = await apiClient.get('/api/settings')
    return response.data.data || {}
  } catch (error) {
    console.error('获取系统配置失败:', error)
    throw error
  }
}

/**
 * 更新系统配置
 * @param {string} type - 配置类型 (general/database/map/security/display)
 * @param {Object} data - 配置数据
 * @returns {Promise<Object>} 更新结果
 */
export async function updateSettings(type, data) {
  try {
    const response = await apiClient.put('/api/settings', {
      type,
      data
    })
    return response.data
  } catch (error) {
    console.error('保存系统配置失败:', error)
    throw error
  }
}

/**
 * 测试数据库连接
 * @param {Object} config - 数据库配置
 * @returns {Promise<Object>} 测试结果
 */
export async function testDatabaseConnection(config) {
  try {
    const response = await apiClient.post('/api/settings/test-database', config)
    return response.data
  } catch (error) {
    console.error('数据库连接测试失败:', error)
    throw error
  }
}

/**
 * 创建数据库备份
 * @returns {Promise<Object>} 备份结果
 */
export async function createBackup() {
  try {
    const response = await apiClient.post('/api/settings/backup')
    return response.data
  } catch (error) {
    console.error('创建备份失败:', error)
    throw error
  }
}

/**
 * 获取备份列表
 * @returns {Promise<Array>} 备份列表
 */
export async function getBackups() {
  try {
    const response = await apiClient.get('/api/settings/backups')
    return response.data.data || []
  } catch (error) {
    console.error('获取备份列表失败:', error)
    throw error
  }
}

/**
 * 删除备份文件
 * @param {string} filename - 备份文件名
 * @returns {Promise<Object>} 删除结果
 */
export async function deleteBackup(filename) {
  try {
    const response = await apiClient.delete(`/api/settings/backup/${filename}`)
    return response.data
  } catch (error) {
    console.error('删除备份失败:', error)
    throw error
  }
}

/**
 * 下载备份文件
 * @param {string} filename - 备份文件名
 */
export function downloadBackup(filename) {
  const link = document.createElement('a')
  link.href = `/api/settings/backup/${filename}`
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 获取系统日志
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 日志数据和分页信息
 */
export async function getSystemLogs(params = {}) {
  try {
    const response = await apiClient.get('/api/settings/logs', { params })
    return response.data.data || { logs: [], total: 0 }
  } catch (error) {
    console.error('获取系统日志失败:', error)
    throw error
  }
}

/**
 * 导出系统日志
 * @param {Object} params - 查询参数
 */
export function exportLogs(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const link = document.createElement('a')
  link.href = `/api/settings/logs/export?${queryString}`
  link.download = `system_logs_${new Date().getTime()}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 恢复备份
 * @param {File} file - 备份文件
 * @returns {Promise<Object>} 恢复结果
 */
export async function restoreBackup(file) {
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/api/settings/restore', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  } catch (error) {
    console.error('恢复备份失败:', error)
    throw error
  }
}
