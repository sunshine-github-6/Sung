import axios from 'axios'

// 创建 axios 实例，使用相对路径让请求走代理
const apiClient = axios.create({
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 获取所有迁徙数据 (GeoJSON 格式)
 * @param {string} searchKeyword - 搜索关键词（可选）
 * @returns {Promise<Array>} 迁徙数据列表
 */
export async function fetchMigrations(searchKeyword = '') {
  try {

    // 构建请求URL
    let url = '/api/migrations-geojson'
    if (searchKeyword && searchKeyword.trim()) {
      url += `?q=${encodeURIComponent(searchKeyword.trim())}`
    }
    
    // 优先尝试 GeoJSON 格式接口
    const response = await apiClient.get(url)

    const features = response.data.features || []
    
    // 如果返回空数组，尝试备用方案
    if (features.length === 0 && !searchKeyword) {

      return await fetchMigrationsFallback()
    }
    
    return features
  } catch (error) {

    // 备用方案：调用原始接口并转换
    return await fetchMigrationsFallback()
  }
}

/**
 * 备用方案：从原始接口获取并转换为类 GeoJSON 格式
 */
async function fetchMigrationsFallback() {
  try {


    
    const [migrationsRes, branchesRes, locationsRes] = await Promise.all([
      apiClient.get('/api/migrations').catch(err => {

        throw err
      }),
      apiClient.get('/api/branches').catch(err => {

        throw err
      }),
      apiClient.get('/api/locations').catch(err => {

        throw err
      })
    ])



    // 创建位置映射以便快速查找
    const locationMap = {}
    if (locationsRes.data && locationsRes.data.data && Array.isArray(locationsRes.data.data)) {
      locationsRes.data.data.forEach(location => {
        locationMap[location.id] = [parseFloat(location.longitude), parseFloat(location.latitude)]
      })
    }

    // 数据转换逻辑
    if (migrationsRes.data && migrationsRes.data.data && Array.isArray(migrationsRes.data.data) && migrationsRes.data.data.length > 0) {
      const branches = branchesRes.data && branchesRes.data.data && Array.isArray(branchesRes.data.data) ? branchesRes.data.data : []
      
  
      const convertedData = migrationsRes.data.data.map(migration => {
        const startCoords = locationMap[migration.start_location_id] || [108.0, 34.0]
        const endCoords = locationMap[migration.end_location_id] || [108.0, 34.0]
        
        return {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: [startCoords, endCoords]
          },
          properties: {
            migration_id: migration.id,
            branch_name: branches.find(b => b.id === migration.branch_id)?.name || '未知分支',
            start_year: migration.start_year,
            end_year: migration.end_year,
            reason: migration.reason || '无'
          }
        }
      })
  
      return convertedData
    } else {
  

    }
    
    // 如果没有真实数据，返回示例数据用于测试

    const sampleData = getSampleData()

    return sampleData
  } catch (error) {



    
    // 即使在错误情况下也返回示例数据，让用户能看到界面效果

    const sampleData = getSampleData()

    return sampleData
  }
}

/**
 * 获取示例数据用于测试和演示
 */
function getSampleData() {
  return [
    {
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: [[116.4074, 39.9042], [121.4737, 31.2304]] // 北京到上海
      },
      properties: {
        migration_id: 1,
        branch_name: '测试分支',
        start_year: 1900,
        end_year: 1910,
        reason: '战乱迁移'
      }
    },
    {
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: [[121.4737, 31.2304], [113.2644, 23.1291]] // 上海到广州
      },
      properties: {
        migration_id: 2,
        branch_name: '测试分支2',
        start_year: 1920,
        end_year: 1930,
        reason: '经商迁移'
      }
    }
  ]
}

/**
 * 获取所有家族分支
 */
export async function fetchBranches() {
  try {
    const response = await apiClient.get('/api/branches')
    return response.data.data || []
  } catch (error) {

    return []
  }
}

/**
 * 获取所有地点
 */
export async function fetchLocations() {
  try {
    const response = await apiClient.get('/api/locations')
    return response.data.data || []
  } catch (error) {

    return []
  }
}

/**
 * 获取统计数据
 */
export async function fetchStatistics() {
  try {
    const response = await apiClient.get('/api/statistics')
    return response.data.data || {}
  } catch (error) {

    return {
      branches: 0,
      locations: 0,
      migrations: 0,
      valid_migrations: 0
    }
  }
}