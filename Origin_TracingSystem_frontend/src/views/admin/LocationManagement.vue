<template>
  <div class="location-management">
    <div class="page-header">
      <h2>地点管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="loadLocations" :icon="Refresh">
          刷新
        </el-button>
        <el-button type="success" @click="addLocation" :icon="Plus">
          新增地点
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="filters.name"
            placeholder="地名"
            clearable
            @input="handleFilter"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.modern_name"
            placeholder="现代地名"
            clearable
            @input="handleFilter"
          />
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="filters.type"
            placeholder="地点类型"
            clearable
            @change="handleFilter"
          >
            <el-option label="起源地" value="origin" />
            <el-option label="聚居地" value="settlement" />
            <el-option label="途经地" value="node" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <el-table
      :data="paginatedData"
      stripe
      style="width: 100%"
      v-loading="loading"
      row-key="id"
      :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
      :cell-style="{ padding: '10px 0' }"
      height="calc(100vh - 280px)"
    >
      <el-table-column prop="historical_name" label="历史地名" width="200" fixed="left" sortable>
        <template #default="{ row }">
          <div class="location-cell">
            <Location />
            <span>{{ row.historical_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="modern_name" label="现代地名" width="200" sortable />
      <el-table-column prop="longitude" label="经度" width="150" sortable>
        <template #default="{ row }">
          {{ row.longitude ? row.longitude.toFixed(6) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="latitude" label="纬度" width="150" sortable>
        <template #default="{ row }">
          {{ row.latitude ? row.latitude.toFixed(6) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="type" label="地点类型" width="120" sortable>
        <template #default="{ row }">
          <el-tag :type="getLocationTypeTag(row.type)">
            {{ getLocationTypeName(row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="region" label="行政区域" width="200" show-overflow-tooltip />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            @click="editLocation(row)"
            :icon="Edit"
          >
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="deleteLocation(row)"
            :icon="Delete"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredLocations.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="currentLocation.id ? '编辑地点' : '新增地点'"
      width="900px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form :model="currentLocation" label-width="100px">
            <el-form-item label="历史地名" :required="true">
              <el-input v-model="currentLocation.historical_name" placeholder="请输入历史地名" />
            </el-form-item>
            <el-form-item label="现代地名">
              <el-input v-model="currentLocation.modern_name" placeholder="请输入现代地名" />
            </el-form-item>
            <el-form-item label="经度">
              <el-input v-model="currentLocation.longitude" placeholder="请输入经度" type="number" />
            </el-form-item>
            <el-form-item label="纬度">
              <el-input v-model="currentLocation.latitude" placeholder="请输入纬度" type="number" />
            </el-form-item>
            <el-form-item label="地点类型">
              <el-select v-model="currentLocation.type" placeholder="请选择地点类型">
                <el-option label="起源地" value="origin" />
                <el-option label="定居点" value="settlement" />
                <el-option label="途经地" value="node" />
              </el-select>
            </el-form-item>
            <el-form-item label="行政区域">
              <el-input v-model="currentLocation.region" placeholder="请输入行政区域" />
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12">
          <LocationPicker
            :longitude="currentLocation.longitude ? parseFloat(currentLocation.longitude) : null"
            :latitude="currentLocation.latitude ? parseFloat(currentLocation.latitude) : null"
            :address="currentLocation.modern_name"
            @confirm="handleLocationPicked"
          />
        </el-col>
      </el-row>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveLocation">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Delete, Location } from '@element-plus/icons-vue'
import { getAllLocations, createLocation, updateLocation, deleteLocation as deleteLocationApi } from '@/api/admin'
import LocationPicker from '@/components/LocationPicker.vue'

const locations = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentLocation = ref({})
const currentPage = ref(1)
const pageSize = ref(10)
const filters = ref({
  name: '',
  modern_name: '',
  type: ''
})

const filteredLocations = computed(() => {
  let result = locations.value

  if (filters.value.name) {
    result = result.filter(location =>
      location.historical_name.toLowerCase().includes(filters.value.name.toLowerCase()) ||
      location.modern_name.toLowerCase().includes(filters.value.name.toLowerCase())
    )
  }

  if (filters.value.modern_name) {
    result = result.filter(location =>
      (location.modern_name || '').toLowerCase().includes(filters.value.modern_name.toLowerCase())
    )
  }

  if (filters.value.type) {
    result = result.filter(location => location.type === filters.value.type)
  }

  return result
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLocations.value.slice(start, end)
})

const handleFilter = () => {
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const getLocationTypeName = (type) => {
  const typeMap = {
    'origin': '起源地',
    'settlement': '聚居地',
    'node': '途经地'
  }
  return typeMap[type] || type
}

const getLocationTypeTag = (type) => {
  const typeMap = {
    'origin': 'warning',
    'settlement': 'success',
    'node': 'info'
  }
  return typeMap[type] || 'default'
}

const loadLocations = async () => {
  loading.value = true
  try {
    const response = await getAllLocations()
    locations.value = response.map(location => ({
      ...location,
      historical_name: location.historical_name || '',
      modern_name: location.modern_name || '',
      longitude: location.longitude || null,
      latitude: location.latitude || null,
      type: location.type || 'settlement',
      region: location.region || ''
    }))
  } catch (error) {
    ElMessage.error(error.message || '加载地点列表失败')
  } finally {
    loading.value = false
  }
}

const addLocation = () => {
  currentLocation.value = {
    id: null,
    historical_name: '',
    modern_name: '',
    longitude: null,
    latitude: null,
    type: 'settlement',
    region: ''
  }
  dialogVisible.value = true
}

const editLocation = (location) => {
  currentLocation.value = { ...location }
  dialogVisible.value = true
}

const saveLocation = async () => {
  try {
    if (currentLocation.value.id) {
      await updateLocation(currentLocation.value.id, {
        historical_name: currentLocation.value.historical_name,
        modern_name: currentLocation.value.modern_name,
        longitude: currentLocation.value.longitude,
        latitude: currentLocation.value.latitude,
        type: currentLocation.value.type,
        region: currentLocation.value.region
      })
      ElMessage.success('地点信息更新成功')
    } else {
      await createLocation({
        historical_name: currentLocation.value.historical_name,
        modern_name: currentLocation.value.modern_name,
        longitude: currentLocation.value.longitude,
        latitude: currentLocation.value.latitude,
        type: currentLocation.value.type,
        region: currentLocation.value.region
      })
      ElMessage.success('地点创建成功')
    }

    dialogVisible.value = false
    await loadLocations()
  } catch (error) {
    ElMessage.error(error.message || '保存地点失败')
  }
}

const deleteLocation = async (location) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除地点 "${location.historical_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await deleteLocationApi(location.id)
    ElMessage.success('地点删除成功')
    await loadLocations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除地点失败')
    }
  }
}

const handleLocationPicked = (data) => {
  currentLocation.value.longitude = data.longitude
  currentLocation.value.latitude = data.latitude
  if (data.address && !currentLocation.value.modern_name) {
    currentLocation.value.modern_name = data.address
  }
  if (data.address && !currentLocation.value.region) {
    currentLocation.value.region = data.address
  }
  ElMessage.success('位置已更新')
}

onMounted(() => {
  loadLocations()
})
</script>

<style scoped>
.location-management {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.page-header h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-bar {
  margin-bottom: 20px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
  border: 1px solid #eee;
}

.location-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
