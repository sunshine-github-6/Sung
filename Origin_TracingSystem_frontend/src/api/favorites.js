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
 * 获取用户收藏的分支列表
 * @param {number} userId - 用户ID
 * @returns {Promise<Array>} 收藏列表
 */
export async function getUserFavorites(userId) {
  try {
    const response = await apiClient.get('/api/user/favorites', {
      params: { user_id: userId }
    })
    return response.data.data || []
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取收藏列表失败')
  }
}

/**
 * 添加分支到收藏
 * @param {number} userId - 用户ID
 * @param {number} branchId - 分支ID
 * @returns {Promise<Object>} 收藏结果
 */
export async function addFavorite(userId, branchId) {
  try {
    const response = await apiClient.post('/api/user/favorites', {
      user_id: userId,
      branch_id: branchId
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '收藏失败')
  }
}

/**
 * 取消收藏分支
 * @param {number} userId - 用户ID
 * @param {number} branchId - 分支ID
 * @returns {Promise<Object>} 取消收藏结果
 */
export async function removeFavorite(userId, branchId) {
  try {
    const response = await apiClient.delete(`/api/user/favorites/${branchId}`, {
      params: { user_id: userId }
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '取消收藏失败')
  }
}

/**
 * 检查用户是否已收藏某个分支
 * @param {number} userId - 用户ID
 * @param {number} branchId - 分支ID
 * @returns {Promise<boolean>} 是否已收藏
 */
export async function checkIsFavorite(userId, branchId) {
  try {
    const response = await apiClient.get('/api/user/favorites/check', {
      params: { 
        user_id: userId,
        branch_id: branchId
      }
    })
    return response.data.data?.is_favorite || false
  } catch (error) {
    return false
  }
}

/**
 * 切换收藏状态（收藏/取消收藏）
 * @param {number} userId - 用户ID
 * @param {number} branchId - 分支ID
 * @param {boolean} isFavorite - 当前是否已收藏
 * @returns {Promise<Object>} 操作结果
 */
export async function toggleFavorite(userId, branchId, isFavorite) {
  if (isFavorite) {
    return await removeFavorite(userId, branchId)
  } else {
    return await addFavorite(userId, branchId)
  }
}
