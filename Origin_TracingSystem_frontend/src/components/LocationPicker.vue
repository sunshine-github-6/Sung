<template>
  <div class="location-picker">
    <!-- 搜索框 -->
    <div v-if="showSearch" class="search-box">
      <el-input
        v-model="searchKeyword"
        placeholder="请输入地点名称搜索"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch" :icon="Search">搜索</el-button>
        </template>
      </el-input>
      
      <!-- 搜索结果列表 -->
      <div v-if="searchResults.length > 0" class="search-results">
        <el-scrollbar max-height="200px">
          <div
            v-for="(item, index) in searchResults"
            :key="index"
            class="result-item"
            :class="{ active: selectedIndex === index }"
            @click="selectLocation(item, index)"
          >
            <div class="result-name">{{ item.name }}</div>
            <div class="result-address">{{ item.address }}</div>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <!-- 地图提示信息 -->
    <div v-if="isPicking" class="pick-hint">
      <el-alert
        title="请点击地图上的目标位置"
        type="info"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 地图容器 -->
    <div ref="mapContainer" class="map-container"></div>

    <!-- 右侧工具栏 -->
    <div class="right-toolbar">
      <el-tooltip content="在地图上选择位置" placement="left">
        <el-button 
          :type="isPicking ? 'primary' : 'default'"
          :icon="MapLocation"
          @click="togglePicking"
          circle
          size="large"
        />
      </el-tooltip>
      <el-tooltip content="搜索地点" placement="left">
        <el-button 
          :type="showSearch ? 'primary' : 'default'"
          :icon="Search"
          @click="showSearch = !showSearch"
          circle
          size="large"
        />
      </el-tooltip>
      <el-tooltip content="清空标记" placement="left">
        <el-button 
          :icon="Delete"
          @click="handleClear"
          circle
          size="large"
        />
      </el-tooltip>
    </div>

    <!-- 右侧信息面板 -->
    <transition name="slide">
      <div v-if="showInfoPanel" class="info-panel">
        <div class="panel-header">
          <span class="panel-title">📍 位置信息</span>
          <el-button 
            :icon="Close" 
            circle 
            size="small"
            @click="showInfoPanel = false"
          />
        </div>
        
        <div class="panel-content">
          <!-- 坐标信息 -->
          <div class="info-section">
            <div class="section-title">坐标</div>
            <div class="coordinate-row">
              <span class="label">经度：</span>
              <span class="value">{{ currentLng || '-' }}</span>
              <el-button 
                v-if="currentLng"
                :icon="CopyDocument" 
                link
                size="small"
                @click="copyCoordinate('lng')"
              >复制</el-button>
            </div>
            <div class="coordinate-row">
              <span class="label">纬度：</span>
              <span class="value">{{ currentLat || '-' }}</span>
              <el-button 
                v-if="currentLat"
                :icon="CopyDocument" 
                link
                size="small"
                @click="copyCoordinate('lat')"
              >复制</el-button>
            </div>
          </div>

          <!-- 地址信息 -->
          <div class="info-section" v-if="currentAddress">
            <div class="section-title">地址</div>
            <div class="address-text">{{ currentAddress }}</div>
          </div>

          <!-- 行政区划信息 -->
          <div class="info-section" v-if="addressComponent">
            <div class="section-title">行政区划</div>
            <div class="address-detail">
              <div v-if="addressComponent.province">
                <span class="label">省/直辖市：</span>
                <span class="value">{{ addressComponent.province }}</span>
              </div>
              <div v-if="addressComponent.city">
                <span class="label">城市：</span>
                <span class="value">{{ addressComponent.city }}</span>
              </div>
              <div v-if="addressComponent.district">
                <span class="label">区县：</span>
                <span class="value">{{ addressComponent.district }}</span>
              </div>
              <div v-if="addressComponent.township">
                <span class="label">乡镇：</span>
                <span class="value">{{ addressComponent.township }}</span>
              </div>
              <div v-if="addressComponent.street">
                <span class="label">街道：</span>
                <span class="value">{{ addressComponent.street }}</span>
              </div>
            </div>
          </div>

          <!-- POI信息 -->
          <div class="info-section" v-if="pois && pois.length > 0">
            <div class="section-title">附近POI</div>
            <el-scrollbar max-height="150px">
              <div 
                v-for="(poi, index) in pois.slice(0, 5)" 
                :key="index"
                class="poi-item"
              >
                <span class="poi-name">{{ poi.name }}</span>
                <span class="poi-distance" v-if="poi.distance">{{ poi.distance }}米</span>
              </div>
            </el-scrollbar>
          </div>
        </div>

        <!-- 面板底部操作 -->
        <div class="panel-footer">
          <el-button @click="showInfoPanel = false">关闭</el-button>
          <el-button type="primary" @click="handleConfirm">使用此位置</el-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { MapLocation, Search, Delete, CopyDocument, Close } from '@element-plus/icons-vue'
import { load } from '@amap/amap-jsapi-loader'
import config from '@/config/index'

const props = defineProps({
  // 初始坐标
  longitude: {
    type: Number,
    default: null
  },
  latitude: {
    type: Number,
    default: null
  },
  // 初始地址/名称
  address: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['confirm', 'cancel'])

// 地图相关
const mapContainer = ref(null)
let map = null
let AMap = null
let marker = null
let geocoder = null
let placeSearch = null

// 状态控制
const isPicking = ref(false)
const showSearch = ref(false)
const showInfoPanel = ref(false)

// 搜索相关
const searchKeyword = ref('')
const searchResults = ref([])
const selectedIndex = ref(-1)

// 坐标和地址信息
const currentLng = ref('')
const currentLat = ref('')
const currentAddress = ref('')
const addressComponent = ref(null)
const pois = ref([])

// 初始化地图
const initMap = async () => {
  try {
    // 加载高德地图
    AMap = await load({
      key: config.amap.key,
      version: config.amap.version || '2.0',
      plugins: ['AMap.Geocoder', 'AMap.PlaceSearch', 'AMap.Marker']
    })

    // 创建地图实例
    const center = props.longitude && props.latitude
      ? [props.longitude, props.latitude]
      : [108.0, 34.0] // 默认中心点

    map = new AMap.Map(mapContainer.value, {
      zoom: 12,
      center: center,
      resizeEnable: true
    })

    // 初始化地理编码服务
    geocoder = new AMap.Geocoder({
      radius: 1000,
      extensions: 'all'
    })

    // 初始化POI搜索服务
    placeSearch = new AMap.PlaceSearch({
      pageSize: 10,
      pageIndex: 1,
      extensions: 'all'
    })

    // 如果有初始坐标，添加标记
    if (props.longitude && props.latitude) {
      addMarker([props.longitude, props.latitude])
      currentLng.value = props.longitude.toFixed(6)
      currentLat.value = props.latitude.toFixed(6)
      
      // 进行逆地理编码获取地址信息
      reverseGeocode([props.longitude, props.latitude])
    }

    // 监听地图点击事件
    map.on('click', handleMapClick)

  } catch (error) {
    console.error('地图初始化失败:', error)
    ElMessage.error('地图初始化失败，请检查网络连接')
  }
}

// 切换选择模式
const togglePicking = () => {
  isPicking.value = !isPicking.value
  if (isPicking.value) {
    showSearch.value = false
    searchResults.value = []
    // 改变鼠标样式
    if (map) {
      map.setDefaultCursor('crosshair')
    }
    ElMessage.info('请在地图上点击选择位置')
  } else {
    if (map) {
      map.setDefaultCursor('default')
    }
  }
}

// 处理地图点击
const handleMapClick = (e) => {
  const lng = e.lnglat.getLng()
  const lat = e.lnglat.getLat()
  
  currentLng.value = lng.toFixed(6)
  currentLat.value = lat.toFixed(6)
  
  // 添加或更新标记
  addMarker([lng, lat])
  
  // 进行逆地理编码
  reverseGeocode([lng, lat])
  
  // 显示信息面板
  showInfoPanel.value = true
  
  // 清空搜索结果
  searchResults.value = []
  selectedIndex.value = -1
  
  // 退出选择模式
  isPicking.value = false
  if (map) {
    map.setDefaultCursor('default')
  }
}

// 添加标记
const addMarker = (position) => {
  // 移除已有标记
  if (marker) {
    map.remove(marker)
  }
  
  // 创建新标记
  marker = new AMap.Marker({
    position: position,
    draggable: true,
    cursor: 'move'
  })
  
  // 监听标记拖拽事件
  marker.on('dragend', (e) => {
    const lng = e.lnglat.getLng()
    const lat = e.lnglat.getLat()
    currentLng.value = lng.toFixed(6)
    currentLat.value = lat.toFixed(6)
    reverseGeocode([lng, lat])
  })
  
  map.add(marker)
  map.setCenter(position)
}

// 逆地理编码
const reverseGeocode = (position) => {
  if (!geocoder) return
  
  geocoder.getAddress(position, (status, result) => {
    if (status === 'complete' && result.regeocode) {
      const regeocode = result.regeocode
      currentAddress.value = regeocode.formattedAddress
      
      // 保存地址组件信息
      if (regeocode.addressComponent) {
        addressComponent.value = {
          province: regeocode.addressComponent.province,
          city: regeocode.addressComponent.city,
          district: regeocode.addressComponent.district,
          township: regeocode.addressComponent.township,
          street: regeocode.addressComponent.street,
          streetNumber: regeocode.addressComponent.streetNumber
        }
      }
      
      // 保存附近POI信息
      if (regeocode.pois && regeocode.pois.length > 0) {
        pois.value = regeocode.pois.map(poi => ({
          name: poi.name,
          distance: poi.distance,
          type: poi.type
        }))
      } else {
        pois.value = []
      }
    } else {
      currentAddress.value = ''
      addressComponent.value = null
      pois.value = []
    }
  })
}

// POI搜索
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  if (!placeSearch) {
    ElMessage.error('搜索服务未初始化')
    return
  }
  
  placeSearch.search(searchKeyword.value, (status, result) => {
    if (status === 'complete' && result.info === 'OK') {
      searchResults.value = result.poiList.pois.map(poi => ({
        name: poi.name,
        address: poi.address || '暂无地址',
        location: poi.location,
        adcode: poi.adcode,
        city: poi.cityname,
        district: poi.adname
      }))
      selectedIndex.value = -1
    } else {
      searchResults.value = []
      ElMessage.info('未找到相关地点')
    }
  })
}

// 选择搜索结果
const selectLocation = (item, index) => {
  selectedIndex.value = index
  
  const lng = item.location.lng
  const lat = item.location.lat
  
  currentLng.value = lng.toFixed(6)
  currentLat.value = lat.toFixed(6)
  currentAddress.value = `${item.city}${item.district}${item.address}`
  
  // 添加标记并居中
  addMarker([lng, lat])
  map.setZoom(15)
  
  // 显示信息面板
  showInfoPanel.value = true
  
  // 进行逆地理编码获取详细信息
  reverseGeocode([lng, lat])
  
  // 清空搜索结果
  searchResults.value = []
}

// 复制坐标
const copyCoordinate = (type) => {
  const value = type === 'lng' ? currentLng.value : currentLat.value
  if (!value) {
    ElMessage.warning('没有可复制的坐标')
    return
  }
  
  navigator.clipboard.writeText(value).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 清空选择
const handleClear = () => {
  currentLng.value = ''
  currentLat.value = ''
  currentAddress.value = ''
  addressComponent.value = null
  pois.value = []
  searchKeyword.value = ''
  searchResults.value = []
  selectedIndex.value = -1
  showInfoPanel.value = false
  isPicking.value = false
  
  if (marker) {
    map.remove(marker)
    marker = null
  }
  
  if (map) {
    map.setDefaultCursor('default')
  }
}

// 确认选择
const handleConfirm = () => {
  if (!currentLng.value || !currentLat.value) {
    ElMessage.warning('请先在地图上选择位置')
    return
  }
  
  emit('confirm', {
    longitude: parseFloat(currentLng.value),
    latitude: parseFloat(currentLat.value),
    address: currentAddress.value,
    addressComponent: addressComponent.value
  })
  
  showInfoPanel.value = false
}

// 监听props变化
watch(() => [props.longitude, props.latitude], ([newLng, newLat]) => {
  if (newLng && newLat && map) {
    currentLng.value = newLng.toFixed(6)
    currentLat.value = newLat.toFixed(6)
    addMarker([newLng, newLat])
    reverseGeocode([newLng, newLat])
  }
}, { immediate: true })

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (map) {
    map.destroy()
  }
})
</script>

<style scoped>
.location-picker {
  position: relative;
  width: 100%;
  height: 450px;
  min-height: 450px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

/* 搜索框 */
.search-box {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 100px;
  z-index: 998;
  background: white;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e4e7ed;
}

/* 右侧工具栏 */
.right-toolbar {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: white;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e4e7ed;
}

.search-results {
  margin-top: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
  max-height: 200px;
  overflow-y: auto;
}

.result-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #ebeef5;
  transition: background-color 0.3s;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item:hover,
.result-item.active {
  background-color: #f5f7fa;
}

.result-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.result-address {
  font-size: 12px;
  color: #909399;
}

/* 提示信息 */
.pick-hint {
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 997;
  width: 320px;
}

/* 地图容器 */
.map-container {
  width: 100%;
  height: 450px;
  border-radius: 4px;
}

/* 信息面板 */
.info-panel {
  position: absolute;
  top: 160px;
  right: 15px;
  width: 280px;
  max-height: calc(100% - 180px);
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
}

.panel-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.panel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px;
  border-top: 1px solid #ebeef5;
}

/* 信息区块 */
.info-section {
  margin-bottom: 20px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #606266;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.coordinate-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.coordinate-row .label {
  width: 60px;
  color: #909399;
  font-size: 13px;
}

.coordinate-row .value {
  flex: 1;
  font-family: monospace;
  font-size: 14px;
  color: #303133;
}

.address-text {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.address-detail {
  font-size: 13px;
}

.address-detail > div {
  margin-bottom: 6px;
}

.address-detail .label {
  color: #909399;
}

.address-detail .value {
  color: #303133;
}

.poi-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.poi-item:last-child {
  border-bottom: none;
}

.poi-name {
  font-size: 13px;
  color: #303133;
}

.poi-distance {
  font-size: 12px;
  color: #909399;
}

/* 滑动动画 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
