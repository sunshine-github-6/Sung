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
 * 用户登录
 */
export async function login(username, password) {
  try {
    const response = await apiClient.post('/api/auth/login', {
      username,
      password
    })
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '登录失败')
  }
}

/**
 * 用户注册
 */
export async function register(userData) {
  try {
    const response = await apiClient.post('/api/auth/register', userData)
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '注册失败')
  }
}

/**
 * 获取当前用户信息
 */
export async function getUserInfo() {
  try {
    const response = await apiClient.get('/api/auth/user-info')
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '获取用户信息失败')
  }
}

/**
 * 退出登录
 */
export function logout() {
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('userInfo')
  window.location.href = '/login'
}
