// 导入与 auth.js 相同的 axios 配置以确保认证令牌被正确发送
import axios from 'axios'

const apiClient = axios.create({
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token
apiClient.interceptors.request.use(config => {
  const token = sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('userInfo')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * 获取所有用户
 */
export async function getAllUsers() {
  try {
    const response = await apiClient.get('/api/admin/users')
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取用户列表失败')
  }
}

/**
 * 更新用户
 */
export async function updateUser(userId, userData) {
  try {
    const response = await apiClient.put(`/api/admin/users/${userId}`, userData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '更新用户失败')
  }
}

/**
 * 删除用户
 */
export async function deleteUser(userId) {
  try {
    const response = await apiClient.delete(`/api/admin/users/${userId}`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '删除用户失败')
  }
}

/**
 * 重置用户密码
 */
export async function resetUserPassword(userId, newPassword = '123456') {
  try {
    const response = await apiClient.post(`/api/admin/users/${userId}/reset-password`, {
      new_password: newPassword
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '重置用户密码失败')
  }
}

/**
 * 获取所有家族分支
 */
export async function getAllBranches() {
  try {
    const response = await apiClient.get('/api/branches')
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取家族分支列表失败')
  }
}

/**
 * 创建家族分支
 */
export async function createBranch(branchData) {
  try {
    const response = await apiClient.post('/api/branches', branchData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '创建家族分支失败')
  }
}

/**
 * 更新家族分支
 */
export async function updateBranch(branchId, branchData) {
  try {
    const response = await apiClient.put(`/api/branches/${branchId}`, branchData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '更新家族分支失败')
  }
}

/**
 * 删除家族分支
 */
export async function deleteBranch(branchId) {
  try {
    const response = await apiClient.delete(`/api/branches/${branchId}`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '删除家族分支失败')
  }
}

/**
 * 获取所有地点
 */
export async function getAllLocations() {
  try {
    const response = await apiClient.get('/api/locations')
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取地点列表失败')
  }
}

/**
 * 创建地点
 */
export async function createLocation(locationData) {
  try {
    const response = await apiClient.post('/api/locations', locationData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '创建地点失败')
  }
}

/**
 * 更新地点
 */
export async function updateLocation(locationId, locationData) {
  try {
    const response = await apiClient.put(`/api/locations/${locationId}`, locationData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '更新地点失败')
  }
}

/**
 * 删除地点
 */
export async function deleteLocation(locationId) {
  try {
    const response = await apiClient.delete(`/api/locations/${locationId}`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '删除地点失败')
  }
}

/**
 * 获取所有迁徙记录
 */
export async function getAllMigrations() {
  try {
    const response = await apiClient.get('/api/migrations')
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取迁徙记录失败')
  }
}

/**
 * 创建迁徙记录
 */
export async function createMigration(migrationData) {
  try {
    const response = await apiClient.post('/api/migrations', migrationData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '创建迁徙记录失败')
  }
}

/**
 * 更新迁徙记录
 */
export async function updateMigration(migrationId, migrationData) {
  try {
    const response = await apiClient.put(`/api/migrations/${migrationId}`, migrationData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '更新迁徙记录失败')
  }
}

/**
 * 删除迁徙记录
 */
export async function deleteMigration(migrationId) {
  try {
    const response = await apiClient.delete(`/api/migrations/${migrationId}`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '删除迁徙记录失败')
  }
}

/**
 * 用户提交迁徙口述史
 */
export async function submitMigration(submissionData) {
  try {
    const response = await apiClient.post('/api/submissions/migration', submissionData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '提交迁徙口述史失败')
  }
}

/**
 * 获取当前用户的迁徙口述史提交记录
 */
export async function getUserMigrationSubmissions() {
  try {
    // 从 sessionStorage 获取用户 ID
    const userInfoStr = sessionStorage.getItem('userInfo')
    if (!userInfoStr) {
      throw new Error('用户未登录，请重新登录')
    }
    
    let userInfo
    try {
      userInfo = JSON.parse(userInfoStr)
    } catch (e) {
      throw new Error('解析用户信息失败，请重新登录')
    }
    
    if (!userInfo.user_id) {
      throw new Error('用户信息不完整，请重新登录')
    }
    
    // 调用后端接口，传递用户 ID
    const response = await apiClient.get(`/api/submissions/migration?user_id=${userInfo.user_id}`)
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || error.message || '获取迁徙口述史提交记录失败')
  }
}

/**
 * 获取所有迁徙口述史提交记录（管理员）
 */
export async function getAllMigrationSubmissions() {
  try {
    const response = await apiClient.get('/api/admin/submissions/migration')
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取迁徙口述史提交记录失败')
  }
}

/**
 * 审核迁徙口述史提交记录（管理员）
 */
export async function reviewMigrationSubmission(submissionId, reviewData) {
  try {
    const response = await apiClient.put(`/api/admin/submissions/migration/${submissionId}`, reviewData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '审核迁徙口述史提交记录失败')
  }
}

/**
 * 获取用户活跃度报表
 */
export async function getUserActivityReport(params = {}) {
  try {
    const response = await apiClient.get('/api/admin/reports/user-activity', { params })
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取用户活跃度报表失败')
  }
}

/**
 * 获取数据增长报表
 */
export async function getDataGrowthReport(params = {}) {
  try {
    const response = await apiClient.get('/api/admin/reports/data-growth', { params })
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取数据增长报表失败')
  }
}

/**
 * 获取审核工作量报表
 */
export async function getReviewWorkloadReport(params = {}) {
  try {
    const response = await apiClient.get('/api/admin/reports/review-workload', { params })
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取审核工作量报表失败')
  }
}

/**
 * 导出报表
 */
export async function exportReport(params = {}) {
  try {
    const response = await apiClient.get('/api/admin/reports/export', {
      params,
      responseType: 'blob'
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '导出报表失败')
  }
}

/**
 * 获取密码重置请求列表（管理员）
 */
export async function getPasswordResetRequests(status = 'pending') {
  try {
    const response = await apiClient.get('/api/admin/password-reset-requests', {
      params: { status }
    })
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取密码重置请求列表失败')
  }
}

/**
 * 审核密码重置请求（管理员）
 */
export async function reviewPasswordResetRequest(requestId, reviewData) {
  try {
    const response = await apiClient.post(`/api/admin/password-reset-requests/${requestId}/review`, reviewData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '审核密码重置请求失败')
  }
}