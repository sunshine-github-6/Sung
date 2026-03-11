<template>
  <div class="map-wrapper">
    <div class="topbar">
      <div class="brand">
        <span class="brand-icon">🌐</span>
        <div class="brand-text">
          <strong>姜姓迁徙时空洞察</strong>
          <small>地图与数据分析</small>
        </div>
      </div>
      <!-- 顶部导航栏中的搜索框 -->
      <div class="search-container top-search">
        <div class="search-wrapper">
          <el-select
            v-model="selectedSearchResult"
            filterable
            remote
            reserve-keyword
            placeholder="搜索分支名称或地区..."
            :remote-method="handleRemoteSearch"
            :loading="searchLoading"
            clearable
            class="search-input"
            @clear="handleSearchClear"
            @change="handleSearchResultSelect"
          >
            <template #prefix>
              <span class="search-icon">🔍</span>
            </template>
            <el-option
              v-for="item in searchResults"
              :key="item.id"
              :label="item.label"
              :value="item.value"
              class="search-option"
            >
              <div class="option-content">
                <div class="option-title">{{ item.title }}</div>
                <div class="option-subtitle">{{ item.subtitle }}</div>
              </div>
            </el-option>
          </el-select>
        </div>
      </div>
      <div class="view-switch">
        <button class="nav-button submission-button" @click="$router.push('/submission')">
          <div class="button-content">
            <span class="button-icon">📝</span>
            <span class="button-text">提交口述史</span>
          </div>
          <div class="button-glow"></div>
        </button>
        <button class="nav-button analytics-button" @click="$router.push('/analytics')">
          <div class="button-content">
            <span class="button-icon">📊</span>
            <span class="button-text">迁徙分析</span>
          </div>
          <div class="button-glow"></div>
        </button>
        <button class="nav-button pdf-button" @click="exportPDFReport">
          <div class="button-content">
            <span class="button-icon">📄</span>
            <span class="button-text">导出报告</span>
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

    <div class="map-view">
      <!-- 背景图片容器 -->
      <div class="background-container">
        <img :src="backgroundImage" alt="背景" class="background-image" />
        <!-- 地图容器 - 嵌入在背景图片中 -->
        <div class="map-frame">
          <div ref="mapContainer" class="map-container"></div>
        </div>
      </div>

      <!-- 信息面板 -->
      <transition name="slide-fade">
        <div v-if="selectedMigration" class="info-card">
          <div class="card-wrapper">
            <!-- 卡片头部 -->
            <div class="card-header">
              <div class="header-gradient"></div>
              <div class="header-content">
                <div class="card-title">
                  <div class="title-icon-wrapper">
                    <span class="title-icon">🗺️</span>
                  </div>
                  <div class="title-text">
                    <h3>迁徙详情</h3>
                    <p class="title-subtitle">Migration Details</p>
                  </div>
                </div>
                <el-button 
                  class="close-btn" 
                  text 
                  circle
                  @click="closeInfoCard"
                >
                  <span class="close-icon">✕</span>
                </el-button>
              </div>
            </div>
            
            <!-- 卡片内容 -->
            <div class="card-body">
              <div class="migration-info">
                <!-- 分支名称 -->
                <div class="info-item highlight-item">
                  <div class="info-icon-wrapper branch-icon">
                    <span class="info-icon">🏯</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">分支名称</span>
                    <span class="info-value highlight-value">
                      {{ selectedMigration.properties.branch_name || selectedMigration.properties.surname || '未知' }}
                    </span>
                  </div>
                </div>
                
                <!-- 迁徙年代 -->
                <div class="info-item" v-if="selectedMigration.properties.estimated_year || selectedMigration.properties.migration_period || selectedMigration.properties.start_year">
                  <div class="info-icon-wrapper time-icon">
                    <span class="info-icon">📅</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">迁徙年代</span>
                    <span class="info-value">
                      {{ selectedMigration.properties.estimated_year ? 
                         `${selectedMigration.properties.estimated_year}年` :
                         (selectedMigration.properties.migration_period || 
                         (selectedMigration.properties.start_year && selectedMigration.properties.end_year ? 
                          `${selectedMigration.properties.start_year} - ${selectedMigration.properties.end_year}` : 
                          selectedMigration.properties.start_year || '未知')) }}
                    </span>
                  </div>
                </div>
                
                <!-- 起止地点 -->
                <div class="info-item route-item" v-if="selectedMigration.properties.from_name || selectedMigration.properties.migration_reason">
                  <div class="info-icon-wrapper location-icon">
                    <span class="info-icon">📍</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">迁徙路线</span>
                    <div class="route-path">
                      <span class="route-start">{{ selectedMigration.properties.from_name || '未知' }}</span>
                      <div class="route-arrow">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </div>
                      <span class="route-end">{{ selectedMigration.properties.to_name || '未知' }}</span>
                    </div>
                    <!-- 途径地显示 -->
                    <div v-if="waypoints.length > 0" class="waypoints-section">
                      <div class="waypoints-label">途径地：</div>
                      <div class="waypoints-list">
                        <span 
                          v-for="(waypoint, idx) in waypoints" 
                          :key="idx" 
                          class="waypoint-tag"
                        >
                          {{ waypoint }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 迁徙原因 -->
                <div class="info-item" v-if="selectedMigration.properties.migration_reason || selectedMigration.properties.reason">
                  <div class="info-icon-wrapper reason-icon">
                    <span class="info-icon">📝</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">迁徙原因</span>
                    <span class="info-value reason-text">
                      {{ selectedMigration.properties.migration_reason || selectedMigration.properties.reason || '无记录' }}
                    </span>
                  </div>
                </div>
                
                <!-- 关键人物 -->
                <div class="info-item" v-if="selectedMigration.properties.key_figure">
                  <div class="info-icon-wrapper person-icon">
                    <span class="info-icon">👤</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">关键人物</span>
                    <span class="info-value">{{ selectedMigration.properties.key_figure }}</span>
                  </div>
                </div>
                
                <!-- 详细描述 -->
                <div class="info-item description-item" v-if="selectedMigration.properties.description || selectedMigration.properties.historical_summary">
                  <div class="info-icon-wrapper description-icon">
                    <span class="info-icon">📖</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">详细描述</span>
                    <div class="description-content">
                      <div class="description-text">
                        {{ selectedMigration.properties.description || selectedMigration.properties.historical_summary || '暂无详细描述' }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 祖源地信息 -->
                <div class="info-item" v-if="selectedMigration.properties.ancestral_home">
                  <div class="info-icon-wrapper origin-icon">
                    <span class="info-icon">🏛️</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">祖源地</span>
                    <span class="info-value">{{ selectedMigration.properties.ancestral_home }}</span>
                  </div>
                </div>
                
                <!-- 得姓始祖或开基祖 -->
                <div class="info-item" v-if="selectedMigration.properties.first_ancestor">
                  <div class="info-icon-wrapper ancestor-icon">
                    <span class="info-icon">👑</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">得姓始祖/开基祖</span>
                    <span class="info-value">{{ selectedMigration.properties.first_ancestor }}</span>
                  </div>
                </div>
                
                <!-- 资料来源 -->
                <div class="info-item source-item" v-if="selectedMigration.properties.source_reference">
                  <div class="info-icon-wrapper source-icon">
                    <span class="info-icon">📚</span>
                  </div>
                  <div class="info-content">
                    <span class="info-label">资料来源</span>
                    <span class="info-value source-text">{{ selectedMigration.properties.source_reference }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>

    <!-- 时间轴遮罩层 -->
    <transition name="fade">
      <div 
        v-if="showTimeline" 
        class="timeline-overlay"
        @click="showTimeline = false"
      ></div>
    </transition>

    <!-- 时间轴面板 -->
    <transition name="slide-left">
      <div v-if="showTimeline" class="timeline-container">
        <div class="timeline-card">
          <!-- 时间轴头部 -->
          <div class="timeline-header">
            <div class="timeline-header-content">
              <div class="timeline-title-wrapper">
                <div class="timeline-icon-wrapper">
                  <span class="timeline-icon">⏱️</span>
                </div>
                <div class="timeline-title-text">
                  <h3 class="timeline-title">迁徙时间轴</h3>
                  <p class="timeline-subtitle">Migration Timeline</p>
                </div>
              </div>
              <el-button 
                text 
                circle
                class="timeline-close-btn"
                @click="showTimeline = false"
              >
                <span class="close-icon">✕</span>
              </el-button>
            </div>
          </div>
          
          <!-- 时间轴内容 -->
          <div class="timeline-content">
            <div v-if="sortedMigrations.length === 0" class="timeline-empty">
              <div class="empty-icon">📅</div>
              <p>暂无迁移数据</p>
            </div>
            <div v-else class="timeline-wrapper">
              <div 
                v-for="(migration, index) in sortedMigrations" 
                :key="migration.properties.migration_id || index"
                class="timeline-item"
                :class="{ 'active': selectedMigration && selectedMigration.properties.migration_id === migration.properties.migration_id }"
                @click="selectMigrationFromTimeline(migration)"
              >
                <div class="timeline-dot-wrapper">
                  <div class="timeline-dot"></div>
                  <div class="timeline-dot-ring"></div>
                </div>
                <div class="timeline-line" v-if="index < sortedMigrations.length - 1"></div>
                <div class="timeline-content-wrapper">
                  <div class="timeline-year-badge">
                    {{ getMigrationYear(migration) }}
                  </div>
                  <div class="timeline-info">
                    <div class="timeline-branch">
                      <span class="branch-icon">🏯</span>
                      {{ migration.properties.branch_name || migration.properties.surname || '未知分支' }}
                    </div>
                    <div class="timeline-route">
                      <span class="route-from">{{ migration.properties.from_name || '未知' }}</span>
                      <div class="route-arrow-wrapper">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </div>
                      <span class="route-to">{{ migration.properties.to_name || '未知' }}</span>
                    </div>
                    <div v-if="migration.properties.migration_reason" class="timeline-reason">
                      <span class="reason-icon">📝</span>
                      {{ migration.properties.migration_reason }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 时间轴切换开关 -->
    <div class="timeline-toggle">
      <div 
        class="timeline-switch"
        :class="{ 'active': showTimeline }"
        @click="showTimeline = !showTimeline"
      >
        <div class="switch-handle">
          <span class="switch-icon">{{ showTimeline ? '✕' : '⏱️' }}</span>
        </div>
        <span class="switch-label">{{ showTimeline ? '关闭' : '时间轴' }}</span>
      </div>
    </div>

      <!-- 图例 -->
      <div class="legend">
        <el-card shadow="never" class="legend-card">
          <div class="legend-title">图例</div>
          <div class="legend-items">
            <div class="legend-item">
              <div class="legend-marker origin-marker"></div>
              <span>起源点</span>
            </div>
            <div class="legend-item">
              <div class="legend-marker settlement-marker"></div>
              <span>定居点</span>
            </div>
            <div class="legend-item">
              <div class="legend-marker start-marker"></div>
              <span>起点</span>
            </div>
            <div class="legend-item">
              <div class="legend-marker end-marker"></div>
              <span>终点</span>
            </div>
            <div class="legend-item">
              <div class="legend-marker waypoint-marker"></div>
              <span>途径地</span>
            </div>
            <div class="legend-item">
              <div class="legend-line"></div>
              <span>迁徙路线</span>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 地图样式面板切换开关 -->
      <div class="style-toggle">
        <div 
          class="style-switch"
          :class="{ 'active': showStylePanel }"
          @click="showStylePanel = !showStylePanel"
        >
          <div class="switch-handle">
            <span class="switch-icon">{{ showStylePanel ? '✕' : '🎨' }}</span>
          </div>
          <span class="switch-label">{{ showStylePanel ? '关闭' : '样式' }}</span>
        </div>
      </div>
      
      <!-- 筛选面板切换开关 -->
      <div class="filter-toggle" style="margin-top: 10px;">
        <div 
          class="filter-switch"
          :class="{ 'active': showFilterPanel }"
          @click="showFilterPanel = !showFilterPanel"
        >
          <div class="switch-handle">
            <span class="switch-icon">{{ showFilterPanel ? '✕' : '🔍' }}</span>
          </div>
          <span class="switch-label">{{ showFilterPanel ? '关闭' : '筛选' }}</span>
        </div>
      </div>
      
      <!-- 地图样式面板遮罩层 -->
      <transition name="fade">
        <div 
          v-if="showStylePanel" 
          class="style-overlay"
          @click="showStylePanel = false"
        ></div>
      </transition>
      
      <!-- 地图样式面板 -->
      <transition name="slide-left">
        <div v-if="showStylePanel" class="style-container">
          <div class="style-card">
            <!-- 地图样式面板头部 -->
            <div class="style-header">
              <div class="style-header-content">
                <div class="style-title-wrapper">
                  <div class="style-icon-wrapper">
                    <span class="style-icon">🎨</span>
                  </div>
                  <div class="style-title-text">
                    <h3 class="style-title">地图样式</h3>
                    <p class="style-subtitle">Map Style</p>
                  </div>
                </div>
                <el-button 
                  text 
                  circle
                  class="style-close-btn"
                  @click="showStylePanel = false"
                >
                  <span class="close-icon">✕</span>
                </el-button>
              </div>
            </div>
            
            <!-- 地图样式面板内容 -->
            <div class="style-content">
              <div class="style-wrapper">
                <div class="style-buttons">
                  <el-button 
                    size="large" 
                    :type="mapStyle === 'normal' ? 'primary' : 'default'"
                    @click="handleMapStyleChange('normal')"
                    title="标准地图"
                    class="style-option-btn"
                  >
                    🗺️ 标准
                  </el-button>
                  <el-button 
                    size="large" 
                    :type="mapStyle === 'dark' ? 'primary' : 'default'"
                    @click="handleMapStyleChange('dark')"
                    title="暗色地图"
                    class="style-option-btn"
                  >
                    🌙 暗色
                  </el-button>
                </div>
                <div class="style-hint">
                  <small>提示：地图样式切换可能会出现短暂错误，不会影响地图基本功能</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 筛选面板遮罩层 -->
      <transition name="fade">
        <div 
          v-if="showFilterPanel" 
          class="filter-overlay"
          @click="showFilterPanel = false"
        ></div>
      </transition>
      
      <!-- 筛选面板 -->
      <transition name="slide-left">
        <div v-if="showFilterPanel" class="filter-container">
          <div class="filter-card">
            <!-- 筛选面板头部 -->
            <div class="filter-header">
              <div class="filter-header-content">
                <div class="filter-title-wrapper">
                  <div class="filter-icon-wrapper">
                    <span class="filter-icon">🔍</span>
                  </div>
                  <div class="filter-title-text">
                    <h3 class="filter-title">地图筛选</h3>
                    <p class="filter-subtitle">Map Filters</p>
                  </div>
                </div>
                <el-button 
                  text 
                  circle
                  class="filter-close-btn"
                  @click="showFilterPanel = false"
                >
                  <span class="close-icon">✕</span>
                </el-button>
              </div>
            </div>
            
            <!-- 筛选面板内容 -->
            <div class="filter-content">
              <div class="filter-wrapper">
                <!-- 显示控制 -->
                <div class="filter-section">
                  <div class="section-title">显示控制</div>
                  <div class="filter-controls">
                  <el-checkbox
                    v-model="showMigrations"
                    label="迁徙线"
                    size="default"
                    @change="applyFilters"
                    class="filter-checkbox"
                  />
                  <el-checkbox
                    v-model="showSettlements"
                    label="定居点"
                    size="default"
                    @change="applyFilters"
                    class="filter-checkbox"
                  />
                </div>
                </div>
                
                <!-- 分支筛选 -->
                <div class="filter-section">
                  <div class="section-title">分支筛选</div>
                  <el-select
                    v-model="filterBranches"
                    multiple
                    placeholder="选择分支（可多选）"
                    size="small"
                    clearable
                    collapse-tags
                    collapse-tags-tooltip
                    @change="applyFilters"
                    class="filter-select"
                  >
                    <el-option
                      v-for="branch in availableBranches"
                      :key="branch"
                      :label="branch"
                      :value="branch"
                    />
                  </el-select>
                </div>
                
                <!-- 时间段筛选 -->
                <div class="filter-section">
                  <div class="section-title">时间段筛选</div>
                  <div class="year-range">
                    <el-input-number
                      v-model="filterYearStart"
                      :min="0"
                      :max="9999"
                      :precision="0"
                      placeholder="起始年份"
                      size="small"
                      @change="applyFilters"
                      class="year-input"
                    />
                    <span class="year-separator">至</span>
                    <el-input-number
                      v-model="filterYearEnd"
                      :min="0"
                      :max="9999"
                      :precision="0"
                      placeholder="结束年份"
                      size="small"
                      @change="applyFilters"
                      class="year-input"
                    />
                  </div>
                </div>
                
                <!-- 迁徙原因筛选 -->
                <div class="filter-section">
                  <div class="section-title">迁徙原因</div>
                  <el-select
                    v-model="filterReasons"
                    multiple
                    placeholder="选择原因（可多选）"
                    size="small"
                    clearable
                    collapse-tags
                    collapse-tags-tooltip
                    @change="applyFilters"
                    class="filter-select"
                  >
                    <el-option
                      v-for="reason in availableReasons"
                      :key="reason"
                      :label="reason"
                      :value="reason"
                    />
                  </el-select>
                </div>
                
                <!-- 地点筛选 -->
                <div class="filter-section">
                  <div class="section-title">起止地点</div>
                  <el-input
                    v-model="filterLocation"
                    placeholder="输入起止地点关键词"
                    size="small"
                    clearable
                    @input="applyFilters"
                    class="filter-input"
                  >
                    <template #prefix>
                      <span class="input-icon">📍</span>
                    </template>
                  </el-input>
                </div>
                
                <!-- 筛选结果统计和重置按钮 -->
                <div class="filter-stats">
                  <div class="stats-item">
                    <span class="stats-label">筛选结果：</span>
                    <span class="stats-value">{{ filteredMigrations.length }}</span>
                    <span class="stats-total">/ {{ allMigrations.length }}</span>
                  </div>
                  <el-button 
                    text 
                    size="small" 
                    @click="resetFilters"
                    class="reset-btn"
                    :disabled="!hasActiveFilters"
                  >
                    重置
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
      

      
      <!-- 缩放控制按钮 -->
      <div class="zoom-controls">
        <el-button 
          class="zoom-btn zoom-in-btn" 
          @click="zoomIn"
          :disabled="!mapInstance"
        >
          <span class="zoom-icon">+</span>
        </el-button>
        <el-button 
          class="zoom-btn zoom-out-btn" 
          @click="zoomOut"
          :disabled="!mapInstance"
        >
          <span class="zoom-icon">-</span>
        </el-button>
        <el-button 
          class="zoom-btn reset-zoom-btn" 
          @click="resetZoom"
          :disabled="!mapInstance"
        >
          <span class="zoom-icon">↺</span>
        </el-button>
      </div>
      
      <!-- 全屏控制按钮 -->
      <div class="fullscreen-control">
        <el-button 
          class="fullscreen-btn" 
          @click="toggleFullscreen"
          :title="isFullscreen ? '退出全屏' : '进入全屏'"
        >
          <span class="fullscreen-icon">{{ isFullscreen ? '✕' : '⛶' }}</span>
        </el-button>
      </div>
      
      
      
      <!-- 行政区统计按钮 -->
      <div class="district-statistics-control">
        <el-button 
          class="district-statistics-btn" 
          @click="openDistrictSelector"
          title="行政区统计"
        >
          <span class="district-statistics-icon">🗺️</span>
        </el-button>
      </div>
      
      <!-- 栅格图层控制按钮 -->
      <div class="raster-layer-control">
        <el-button 
          class="raster-layer-btn" 
          @click="showRasterLayerPanel = !showRasterLayerPanel"
          title="栅格图层"
          :type="showRasterLayerPanel ? 'primary' : 'default'"
        >
          <span class="raster-layer-icon">📊</span>
        </el-button>
      </div>
      
      <!-- 栅格图层面板遮罩层 -->
      <transition name="fade">
        <div 
          v-if="showRasterLayerPanel" 
          class="raster-layer-overlay"
          @click="showRasterLayerPanel = false"
        ></div>
      </transition>
      
      <!-- 栅格图层面板 -->
      <transition name="slide-left">
        <div v-if="showRasterLayerPanel" class="raster-layer-container">
          <div class="raster-layer-card">
            <!-- 栅格图层面板头部 -->
            <div class="raster-layer-header">
              <div class="raster-layer-header-content">
                <div class="raster-layer-title-wrapper">
                  <div class="raster-layer-icon-wrapper">
                    <span class="raster-layer-icon">📊</span>
                  </div>
                  <div class="raster-layer-title-text">
                    <h3 class="raster-layer-title">栅格图层管理</h3>
                    <p class="raster-layer-subtitle">Raster Layer Management</p>
                  </div>
                </div>
                <el-button 
                  text 
                  circle
                  class="raster-layer-close-btn"
                  @click="showRasterLayerPanel = false"
                >
                  <span class="close-icon">✕</span>
                </el-button>
              </div>
            </div>
            
            <!-- 栅格图层面板内容 -->
            <div class="raster-layer-content">
              <div class="raster-layer-wrapper">
                <!-- 图层类型选择 -->
                <div class="raster-layer-section">
                  <div class="section-title">图层类型</div>
                  <el-radio-group v-model="rasterLayerType" class="layer-type-selector">
                    <el-radio label="tile">瓦片图层</el-radio>
                    <el-radio label="image">单张图片</el-radio>
                    <el-radio label="heatmap">热力图</el-radio>
                  </el-radio-group>
                </div>
                
                <!-- 瓦片图层配置 -->
                <div v-if="rasterLayerType === 'tile'" class="raster-layer-section">
                  <el-input
                    v-model="tileLayerUrl"
                    placeholder="瓦片图层URL模板..."
                    clearable
                    style="margin-bottom: 15px;"
                  >
                    <template #prefix>
                      <span>🔗</span>
                    </template>
                  </el-input>
                  <el-input-number
                    v-model="tileLayerOpacity"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    placeholder="透明度"
                    style="width: 100%; margin-bottom: 15px;"
                  />
                  <el-button 
                    type="primary" 
                    @click="addTileLayer"
                    :disabled="!tileLayerUrl"
                    style="width: 100%;"
                  >
                    添加瓦片图层
                  </el-button>
                </div>
                
                <!-- 单张图片图层配置 -->
                <div v-else-if="rasterLayerType === 'image'" class="raster-layer-section">
                  <el-input
                    v-model="imageLayerUrl"
                    placeholder="图片URL..."
                    clearable
                    style="margin-bottom: 15px;"
                  >
                    <template #prefix>
                      <span>🖼️</span>
                    </template>
                  </el-input>
                  <el-input-number
                    v-model="imageLayerOpacity"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    placeholder="透明度"
                    style="width: 100%; margin-bottom: 15px;"
                  />
                  <el-button 
                    type="primary" 
                    @click="addImageLayer"
                    :disabled="!imageLayerUrl"
                    style="width: 100%;"
                  >
                    添加图片图层
                  </el-button>
                </div>
                
                <!-- 热力图配置 -->
                <div v-else-if="rasterLayerType === 'heatmap'" class="raster-layer-section">
                  <el-input-number
                    v-model="heatmapRadius"
                    :min="5"
                    :max="100"
                    placeholder="热力图半径"
                    style="width: 100%; margin-bottom: 15px;"
                  />
                  <el-input-number
                    v-model="heatmapOpacity"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    placeholder="透明度"
                    style="width: 100%; margin-bottom: 15px;"
                  />
                  <el-button 
                    type="primary" 
                    @click="toggleHeatMap"
                    style="width: 100%;"
                  >
                    {{ showHeatMap ? '关闭热力图' : '显示热力图' }}
                  </el-button>
                </div>
                
                <!-- 已添加图层列表 -->
                <div class="raster-layer-section">
                  <div class="section-title">已添加图层</div>
                  <div class="layers-list">
                    <el-scrollbar height="200px">
                      <div v-if="addedLayers.length === 0" class="empty-hint">
                        暂无添加的图层
                      </div>
                      <el-checkbox-group v-model="checkedLayers" class="layers-checkbox-group">
                        <el-checkbox 
                          v-for="layer in addedLayers" 
                          :key="layer.id" 
                          :label="layer.id"
                          class="layer-checkbox"
                        >
                          <div class="layer-item-container">
                            <div class="layer-info">
                              <div class="layer-name">{{ layer.name }}</div>
                              <div class="layer-type">{{ layer.type }}</div>
                            </div>
                            
                            <!-- 图层透明度调整 -->
                            <div class="layer-opacity-control" v-if="layer.type !== 'heatmap'">
                              <el-slider
                                v-model="layer.opacity"
                                :min="0"
                                :max="1"
                                :step="0.1"
                                @change="updateLayerOpacity(layer.id, layer.opacity)"
                                style="width: 100px;"
                              />
                              <span class="opacity-value">{{ Math.round(layer.opacity * 100) }}%</span>
                            </div>
                            
                            <!-- 图层操作按钮 -->
                            <div class="layer-actions">
                              <el-button 
                                text 
                                size="small" 
                                @click.stop="renameLayer(layer.id)"
                                class="layer-action-btn"
                                title="重命名"
                              >
                                ✏️
                              </el-button>
                              <el-button 
                                text 
                                size="small" 
                                @click.stop="moveLayerUp(layer.id)"
                                class="layer-action-btn"
                                title="上移"
                                :disabled="addedLayers.indexOf(layer) === 0"
                              >
                                ⬆️
                              </el-button>
                              <el-button 
                                text 
                                size="small" 
                                @click.stop="moveLayerDown(layer.id)"
                                class="layer-action-btn"
                                title="下移"
                                :disabled="addedLayers.indexOf(layer) === addedLayers.length - 1"
                              >
                                ⬇️
                              </el-button>
                              <el-button 
                                text 
                                size="small" 
                                @click.stop="copyLayer(layer.id)"
                                class="layer-action-btn"
                                title="复制"
                              >
                                📋
                              </el-button>
                              <el-button 
                                text 
                                size="small" 
                                @click.stop="removeLayer(layer.id)"
                                class="layer-action-btn remove-btn"
                                title="删除"
                              >
                                ❌
                              </el-button>
                            </div>
                          </div>
                        </el-checkbox>
                      </el-checkbox-group>
                    </el-scrollbar>
                  </div>
                </div>
                
                <!-- 图层导出功能 -->
                <div class="raster-layer-section">
                  <div class="section-title">图层导出</div>
                  <el-button 
                    type="success" 
                    @click="exportLayers" 
                    :disabled="addedLayers.length === 0"
                    style="width: 100%; margin-bottom: 10px;"
                  >
                    <span>📤</span> 导出所有图层配置
                  </el-button>
                  <el-button 
                    type="primary" 
                    @click="exportSelectedLayers" 
                    :disabled="checkedLayers.length === 0"
                    style="width: 100%; margin-bottom: 10px;"
                  >
                    <span>📋</span> 导出选中图层配置
                  </el-button>
                  <el-button 
                    type="info" 
                    @click="exportMigrationRasterData"
                    :disabled="!allMigrations || !allMigrations.value || allMigrations.value.length === 0"
                    style="width: 100%;"
                  >
                    <span>🌐</span> 导出迁移栅格数据
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 行政区选择弹窗 -->
      <el-dialog
        v-model="showDistrictSelector"
        title="行政区选择"
        width="600px"
        :modal-append-to-body="false"
      >
        <div class="province-selector">
          <el-input
            v-model="provinceSearch"
            placeholder="搜索省份..."
            clearable
            style="margin-bottom: 15px;"
          >
            <template #prefix>
              <span>🔍</span>
            </template>
          </el-input>
          <el-scrollbar height="400px">
            <el-row :gutter="10">
              <el-col 
                v-for="province in filteredProvinces" 
                :key="province.adcode" 
                :span="8" 
                style="margin-bottom: 10px;"
              >
                <el-button
                  type="primary"
                  plain
                  @click="selectProvince(province)"
                  style="width: 100%;"
                >
                  {{ province.name }}
                </el-button>
              </el-col>
            </el-row>
          </el-scrollbar>
        </div>
      </el-dialog>
      
      <!-- 行政区统计面板（与筛选面板样式一致） -->
      <transition name="slide-left">
        <div v-if="showDistrictStats" class="filter-container">
          <div class="filter-card">
            <!-- 统计面板头部 -->
            <div class="filter-header">
              <div class="filter-header-content">
                <div class="filter-title-wrapper">
                  <div class="filter-icon-wrapper">
                    <span class="filter-icon">📊</span>
                  </div>
                  <div class="filter-title-text">
                    <h3 class="filter-title">{{ districtStats.province }} 地点统计</h3>
                    <p class="filter-subtitle">District Statistics</p>
                  </div>
                </div>
                <el-button 
                  text 
                  circle
                  class="filter-close-btn"
                  @click="showDistrictStats = false"
                >
                  <span class="close-icon">✕</span>
                </el-button>
              </div>
            </div>
            
            <!-- 统计面板内容 -->
            <div class="filter-content">
              <div class="filter-wrapper">
                <!-- 统计概览 -->
                <div class="filter-section">
                  <div class="section-title">统计概览</div>
                  <div class="stats-overview">
                    <el-card shadow="hover" class="stat-card">
                      <div class="stat-value">{{ districtStats.totalLocations }}</div>
                      <div class="stat-label">地点总数</div>
                    </el-card>
                    <el-card shadow="hover" class="stat-card">
                      <div class="stat-value">{{ districtStats.originCount }}</div>
                      <div class="stat-label">起源地</div>
                    </el-card>
                    <el-card shadow="hover" class="stat-card">
                      <div class="stat-value">{{ districtStats.settlementCount }}</div>
                      <div class="stat-label">聚居地</div>
                    </el-card>
                    <el-card shadow="hover" class="stat-card">
                      <div class="stat-value">{{ districtStats.nodeCount }}</div>
                      <div class="stat-label">途经地</div>
                    </el-card>
                  </div>
                </div>
                
                <!-- 地点列表 -->
                <div class="filter-section">
                  <div class="section-title">地点列表</div>
                  <div class="locations-list">
                    <el-scrollbar height="400px">
                      <el-table :data="districtStats.locations" stripe style="width: 100%">
                        <el-table-column prop="historical_name" label="历史地名" width="200" />
                        <el-table-column prop="modern_name" label="现代地名" width="200" />
                        <el-table-column prop="type" label="地点类型" width="120">
                          <template #default="{ row }">
                            <el-tag :type="row.type === 'origin' ? 'warning' : row.type === 'settlement' ? 'success' : 'info'">
                              {{ row.type === 'origin' ? '起源地' : row.type === 'settlement' ? '聚居地' : '途经地' }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="region" label="行政区域" width="200" show-overflow-tooltip />
                      </el-table>
                      <div v-if="districtStats.locations.length === 0" class="empty-hint">
                        该省份暂无地点数据
                      </div>
                    </el-scrollbar>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 错误提示 -->
      <transition name="fade">
        <div v-if="error" class="error-overlay">
          <el-alert
            :title="error"
            type="error"
            :description="errorDescription"
            show-icon
            closable
            @close="error = null"
            class="error-alert"
          />
        </div>
      </transition>
      
      <!-- 加载提示 -->
      <transition name="fade">
        <div v-if="loading" class="loading-overlay">
          <div class="loading-content">
            <div class="loading-spinner"></div>
            <p class="loading-text">正在加载地图和数据...</p>
          </div>
        </div>
      </transition>
    </div>

    <!-- 路径对比面板 -->
    <transition name="slide-fade">
      <div v-if="showComparisonPanel" class="comparison-card">
        <div class="card-wrapper">
          <!-- 卡片头部 -->
          <div class="card-header">
            <div class="header-gradient"></div>
            <div class="header-content">
              <div class="card-title">
                <div class="title-icon-wrapper">
                  <span class="title-icon">⚖️</span>
                </div>
                <div class="title-text">
                  <h3>迁徙路线对比</h3>
                  <p class="title-subtitle">Migration Route Comparison</p>
                </div>
              </div>
              <el-button 
                class="close-btn" 
                text 
                circle
                @click="closeComparisonPanel"
              >
                <span class="close-icon">✕</span>
              </el-button>
            </div>
          </div>
          
          <!-- 卡片内容 -->
          <div class="card-body">
            <div class="comparison-info">
              <!-- 路线1信息 -->
              <div class="info-item highlight-item" v-if="selectedMigrationsForComparison.length > 0">
                <div class="info-icon-wrapper branch-icon">
                  <span class="info-icon">🔵</span>
                </div>
                <div class="info-content">
                  <span class="info-label">路线1</span>
                  <div class="comparison-details">
                    <div class="detail-row">
                      <span class="detail-label">分支：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[0]).branch }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">路线：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[0]).from }} → {{ getRouteInfo(selectedMigrationsForComparison[0]).to }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">长度：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[0]).length }} km</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">方向：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[0]).direction }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">原因：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[0]).reason }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">年代：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[0]).year }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 分隔线 -->
              <div class="divider">
                <div class="divider-line"></div>
                <div class="divider-text">VS</div>
                <div class="divider-line"></div>
              </div>
              
              <!-- 路线2信息 -->
              <div class="info-item highlight-item" v-if="selectedMigrationsForComparison.length > 1">
                <div class="info-icon-wrapper branch-icon">
                  <span class="info-icon">🔴</span>
                </div>
                <div class="info-content">
                  <span class="info-label">路线2</span>
                  <div class="comparison-details">
                    <div class="detail-row">
                      <span class="detail-label">分支：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[1]).branch }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">路线：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[1]).from }} → {{ getRouteInfo(selectedMigrationsForComparison[1]).to }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">长度：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[1]).length }} km</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">方向：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[1]).direction }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">原因：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[1]).reason }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">年代：</span>
                      <span class="detail-value">{{ getRouteInfo(selectedMigrationsForComparison[1]).year }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 对比摘要 -->
              <div class="info-item" v-if="selectedMigrationsForComparison.length === 2">
                <div class="info-icon-wrapper location-icon">
                  <span class="info-icon">📋</span>
                </div>
                <div class="info-content">
                  <span class="info-label">对比摘要</span>
                  <div class="summary-details">
                    <div class="summary-row">
                      <span class="summary-label">长度差异：</span>
                      <span class="summary-value">
                        {{ Math.abs(parseFloat(getRouteInfo(selectedMigrationsForComparison[0]).length) - parseFloat(getRouteInfo(selectedMigrationsForComparison[1]).length)).toFixed(2) }} km
                      </span>
                    </div>
                    <div class="summary-row">
                      <span class="summary-label">方向差异：</span>
                      <span class="summary-value">
                        {{ getRouteInfo(selectedMigrationsForComparison[0]).direction }} vs {{ getRouteInfo(selectedMigrationsForComparison[1]).direction }}
                      </span>
                    </div>
                    <div class="summary-row">
                      <span class="summary-label">分支差异：</span>
                      <span class="summary-value">
                        {{ getRouteInfo(selectedMigrationsForComparison[0]).branch }} vs {{ getRouteInfo(selectedMigrationsForComparison[1]).branch }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 取消按钮 -->
              <div class="cancel-button-container">
                <el-button 
                  class="cancel-comparison-btn" 
                  @click="clearComparisonSelectionAndClosePanel"
                  type="danger"
                  plain
                >
                  取消对比
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { initAMap, addOverlays, removeOverlays, fitView, cleanupCustomControls, createRasterLayer, createHeatMap } from '@/utils/amap'
import { fetchMigrations, fetchStatistics, fetchLocations } from '@/api/genealogy'
import { logout } from '@/api/auth'
import { ElCard, ElButton, ElAlert, ElIcon, ElInput, ElSelect, ElOption, ElCheckbox, ElInputNumber, ElMessageBox, ElMessage, ElDialog, ElRow, ElCol, ElScrollbar, ElRadio, ElRadioGroup, ElCheckboxGroup } from 'element-plus'
import backgroundImage from '@/img/background.png'

const router = useRouter()

// 获取当前用户角色
const isAdmin = computed(() => {
  const userInfoStr = sessionStorage.getItem('userInfo')
  if (!userInfoStr) return false
  try {
    const userInfo = JSON.parse(userInfoStr)
    return userInfo && userInfo.role === 'admin'
  } catch (e) {
    
    return false
  }
})

// 地图实例和状态
const mapContainer = ref(null)
const mapInstance = ref(null)
const amap = ref(null) // AMap 命名空间
const migrations = ref([])
const locations = ref([]) // 存储所有定居点数据
const locationMarkers = ref([]) // 存储定居点标记
const infoWindow = ref(null) // 信息窗体实例
const selectedMigration = ref(null)
const loading = ref(true)
const error = ref(null)
const errorDescription = ref("")
const polylines = ref([]) // 搜索关键词
const searchKeyword = ref('') // 搜索关键词
const filteredMigrations = ref([]) // 过滤后的迁徙数据
const allMigrations = ref([]) // 存储所有原始数据
const searchResults = ref([]) // 搜索结果列表
const searchLoading = ref(false) // 搜索加载状态
const selectedSearchResult = ref(null) // 选中的搜索结果
const waypointMarkers = ref([]) // 存储途径地标记
const showTimeline = ref(false) // 控制时间轴显示
const migrationLineMap = new Map() // 存储migration和polyline的映射关系
const statistics = ref({ branches: 0, locations: 0, migrations: 0, valid_migrations: 0 }) // 统计数据
const isFullscreen = ref(false) // 全屏状态

// 行政区选择相关状态
const showDistrictSelector = ref(false)
const provinceSearch = ref('')
const provinces = ref([
  { name: '北京市', adcode: '110000' },
  { name: '天津市', adcode: '120000' },
  { name: '河北省', adcode: '130000' },
  { name: '山西省', adcode: '140000' },
  { name: '内蒙古自治区', adcode: '150000' },
  { name: '辽宁省', adcode: '210000' },
  { name: '吉林省', adcode: '220000' },
  { name: '黑龙江省', adcode: '230000' },
  { name: '上海市', adcode: '310000' },
  { name: '江苏省', adcode: '320000' },
  { name: '浙江省', adcode: '330000' },
  { name: '安徽省', adcode: '340000' },
  { name: '福建省', adcode: '350000' },
  { name: '江西省', adcode: '360000' },
  { name: '山东省', adcode: '370000' },
  { name: '河南省', adcode: '410000' },
  { name: '湖北省', adcode: '420000' },
  { name: '湖南省', adcode: '430000' },
  { name: '广东省', adcode: '440000' },
  { name: '广西壮族自治区', adcode: '450000' },
  { name: '海南省', adcode: '460000' },
  { name: '重庆市', adcode: '500000' },
  { name: '四川省', adcode: '510000' },
  { name: '贵州省', adcode: '520000' },
  { name: '云南省', adcode: '530000' },
  { name: '西藏自治区', adcode: '540000' },
  { name: '陕西省', adcode: '610000' },
  { name: '甘肃省', adcode: '620000' },
  { name: '青海省', adcode: '630000' },
  { name: '宁夏回族自治区', adcode: '640000' },
  { name: '新疆维吾尔自治区', adcode: '650000' }
])

// 行政区统计相关状态
const showDistrictStats = ref(false)
const districtStats = ref({
  province: '',
  totalLocations: 0,
  originCount: 0,
  settlementCount: 0,
  nodeCount: 0,
  locations: []
})

// 路径对比功能相关状态
const comparisonMode = ref(false) // 是否处于对比模式
const selectedMigrationsForComparison = ref([]) // 存储选中的两条用于对比的迁徙路线
const showComparisonPanel = ref(false) // 控制对比面板显示

// 地图显示筛选状态
const showMigrations = ref(true) // 是否显示迁徙线
const showSettlements = ref(true) // 是否显示定居点
const mapStyle = ref('normal') // 当前地图样式
const showFilterPanel = ref(false) // 控制筛选面板显示
const showStylePanel = ref(false) // 控制地图样式面板显示

// 栅格图层相关状态
const showRasterLayerPanel = ref(false) // 控制栅格图层面板显示
const rasterLayerType = ref('tile') // 栅格图层类型：tile/image/heatmap
const tileLayerUrl = ref('') // 瓦片图层URL
const tileLayerOpacity = ref(0.7) // 瓦片图层透明度
const imageLayerUrl = ref('') // 单张图片URL
const imageLayerOpacity = ref(0.7) // 单张图片透明度
const heatmapRadius = ref(25) // 热力图半径
const heatmapOpacity = ref(0.7) // 热力图透明度
const showHeatMap = ref(false) // 是否显示热力图
const addedLayers = ref([]) // 已添加的图层列表
const checkedLayers = ref([]) // 已选中的图层
const layerIdCounter = ref(1) // 图层ID计数器
const rasterLayers = ref([]) // 栅格图层实例列表
const heatmapLayer = ref(null) // 热力图层实例

// 筛选条件
const filterBranches = ref([]) // 选中的分支
const filterYearStart = ref(null) // 起始年份
const filterYearEnd = ref(null) // 结束年份
const filterReasons = ref([]) // 选中的迁徙原因
const filterLocation = ref('') // 地点关键词

// 可用的筛选选项（从数据中提取）
const availableBranches = computed(() => {
  const branches = new Set()
  allMigrations.value.forEach(migration => {
    const branchName = migration.properties?.branch_name || migration.properties?.surname
    if (branchName) {
      branches.add(branchName)
    }
  })
  return Array.from(branches).sort()
})

const availableReasons = computed(() => {
  const reasons = new Set()
  allMigrations.value.forEach(migration => {
    const reason = migration.properties?.migration_reason || migration.properties?.reason
    if (reason && reason.trim() && reason !== '无' && reason !== '无记录') {
      reasons.add(reason.trim())
    }
  })
  return Array.from(reasons).sort()
})

// 检查是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return filterBranches.value.length > 0 ||
         filterYearStart.value !== null ||
         filterYearEnd.value !== null ||
         filterReasons.value.length > 0 ||
         filterLocation.value.trim() !== ''
})

// 计算分支数量
const uniqueBranchesCount = computed(() => {
  return statistics.value.branches || 0
})

// 计算过滤后的省份
const filteredProvinces = computed(() => {
  if (!provinceSearch.value.trim()) {
    return provinces.value
  }
  return provinces.value.filter(province => 
    province.name.includes(provinceSearch.value.trim()) || 
    province.adcode.includes(provinceSearch.value.trim())
  )
})

// 行政区选择相关方法
function openDistrictSelector() {
  showDistrictSelector.value = true
}

async function selectProvince(province) {

  showDistrictSelector.value = false
  
  // 计算并显示统计数据
  calculateDistrictStats(province.name)
  showDistrictStats.value = true
  
  // 调用省份边界显示功能
  if (amap.value && mapInstance.value) {
    try {
      await showProvinceBoundary(province)
    } catch (error) {

      ElMessage.error('显示省份边界失败');
    }
  } else {

    ElMessage.error('地图尚未初始化完成，请稍后重试');
  }
}

// 计算行政区统计数据
function calculateDistrictStats(provinceName) {
  // 过滤出该省份的所有地点
  const provinceLocations = locations.value.filter(location => {
    // 检查地点的region是否包含省份名称
    return location.region && location.region.includes(provinceName)
  })
  
  // 统计不同类型的地点数量
  const originCount = provinceLocations.filter(location => location.type === 'origin').length
  const settlementCount = provinceLocations.filter(location => location.type === 'settlement').length
  const nodeCount = provinceLocations.filter(location => location.type === 'node').length
  
  // 更新统计结果
  districtStats.value = {
    province: provinceName,
    totalLocations: provinceLocations.length,
    originCount,
    settlementCount,
    nodeCount,
    locations: provinceLocations
  }
  

}

// 显示省份边界
async function showProvinceBoundary(province) {


  
  try {
    // 确保地图实例存在
    if (!mapInstance.value || !window.AMapUI) {

      ElMessage.error('地图未初始化，无法显示省份边界');
      return;
    }
    
    // 清除已有的多边形
    clearExistingPolygons();
    
    // 使用AMapUI DistrictExplorer（配置中已启用，专门用于行政区划可视化）
    const polygons = await new Promise((resolve, reject) => {
      window.AMapUI.loadUI(['geo/DistrictExplorer'], (DistrictExplorer) => {

        
        // 创建DistrictExplorer实例
        const districtExplorer = new DistrictExplorer({
          map: mapInstance.value
        });
        
        // 加载行政区划数据
        districtExplorer.loadAreaNode(province.adcode, (error, areaNode) => {
          if (error) {

            reject(new Error('加载行政区划数据失败'));
            return;
          }
          

          
          // 获取边界数据并创建多边形
          const polys = [];
          const subFeatures = areaNode.getSubFeatures();
          

          
          // 定义处理坐标和创建多边形的通用方法
          function createPolygonFromGeometry(geometry) {
            if (!geometry || !geometry.coordinates) {
              return null;
            }
            
            const coordinates = geometry.coordinates;
            let polygons = [];
            
            // 处理多级坐标结构
            function processCoords(coords, level = 0) {
              if (typeof coords[0][0] === 'number') {
                // 单个多边形
                const path = coords.map(coord => new window.AMap.LngLat(coord[0], coord[1]));
                const polygon = new window.AMap.Polygon({
                  path: path,
                  strokeColor: '#FFA500', // 橙色边框，更柔和
                  strokeWeight: 3, // 适中的边框宽度
                  strokeOpacity: 0.8, // 轻微的边框透明度
                  fillColor: 'rgba(255, 165, 0, 0.3)', // 更浅的填充色
                  fillOpacity: 0.3, // 降低填充透明度，让底层内容可见
                  zIndex: 50 // 降低层级，确保迁移路线在上方
                });
                polygons.push(polygon);
              } else {
                // 多个多边形
                coords.forEach(subCoord => {
                  processCoords(subCoord, level + 1);
                });
              }
            }
            
            processCoords(coordinates);
            return polygons;
          }
          
          // 处理子区域
          if (subFeatures.length > 0) {
            subFeatures.forEach((feature, index) => {

              
              if (feature && feature.geometry) {
                const newPolygons = createPolygonFromGeometry(feature.geometry);
                if (newPolygons && newPolygons.length > 0) {
                  polys.push(...newPolygons);

                }
              }
            });
          } else {
            // 尝试获取当前区域的几何数据

            
            // 获取当前区域的feature
            const currentFeature = areaNode.getFeature();
            if (currentFeature && currentFeature.geometry) {
              const newPolygons = createPolygonFromGeometry(currentFeature.geometry);
              if (newPolygons && newPolygons.length > 0) {
                polys.push(...newPolygons);

              }
            } else {
              // 尝试直接从areaNode获取几何数据

              if (areaNode._data && areaNode._data.topo) {

                // 这里可以添加更复杂的拓扑数据解析逻辑
              }
            }
          }
          
          // 将创建的多边形添加到地图上
          polys.forEach(polygon => {
            polygon.setMap(mapInstance.value);
          });
          
          resolve(polys);
        });
      }, (error) => {

        reject(new Error('加载行政区划探索器失败'));
      });
    });
    

    
    if (polygons.length > 0) {
      // 保存引用以便后续清理
      window.provinceBoundaries = polygons;
      
      // 调整视图到该区域
      mapInstance.value.setFitView(polygons);
      

      ElMessage.success(`成功显示${province.name}边界`);
    } else {

      ElMessage.error('无法绘制省份边界');
    }
  } catch (error) {


    ElMessage.error('加载省份边界数据失败: ' + error.message);
  } finally {

  }
}

// 清除现有的省份边界多边形
function clearExistingPolygons() {
  if (window.provinceBoundaries && window.provinceBoundaries.length > 0) {
    try {
      // 如果是单个多边形对象
      if (mapInstance.value && typeof window.provinceBoundaries.remove === 'function') {
        window.provinceBoundaries.remove();
      } else if (Array.isArray(window.provinceBoundaries)) {
        // 如果是多边形数组
        mapInstance.value.remove(window.provinceBoundaries);
      }
    } catch (error) {

    }
  }
  window.provinceBoundaries = [];
}

// 导出PDF报告
async function exportPDFReport() {
  try {
    ElMessage({ message: '正在生成PDF报告，请稍候...', type: 'info' });
    
    // 发送请求到后端API
    const response = await fetch('http://localhost:5000/api/export/migration-report');
    
    if (!response.ok) {
      throw new Error('导出PDF失败');
    }
    
    // 获取PDF blob数据
    const blob = await response.blob();
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `migration_report_${new Date().toISOString().slice(0, 19).replace(/[-:]/g, '')}.pdf`;
    document.body.appendChild(a);
    a.click();
    
    // 清理
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    }, 100);
    
    ElMessage({ message: 'PDF报告导出成功', type: 'success' });
  } catch (error) {
    console.error('导出PDF失败:', error);
    ElMessage({ message: '导出PDF失败，请稍后重试', type: 'error' });
  }
}

// 增强的资源清理函数
function enhancedCleanup() {
  try {
    // 清理省份边界
    clearExistingPolygons();
    
    // 清理其他地图覆盖物
    if (mapInstance.value) {
      // 清理迁徙路径
      if (polylines.value && polylines.value.length > 0) {
        mapInstance.value.remove(polylines.value);
        polylines.value = [];
      }
      
      // 清理定居点标记
      if (locationMarkers.value && locationMarkers.value.length > 0) {
        mapInstance.value.remove(locationMarkers.value);
        locationMarkers.value = [];
      }
      
      // 清理途径地标记
      if (waypointMarkers.value && waypointMarkers.value.length > 0) {
        mapInstance.value.remove(waypointMarkers.value);
        waypointMarkers.value = [];
      }
      

    }
    
    // 清理全局变量
    if (window.provinceBoundaries) {
      window.provinceBoundaries = [];
    }
    
    // 清理映射关系
    migrationLineMap.clear();
    
  } catch (error) {

  }
}

// 初始化行政区划服务
async function initDistrictServices() {
  try {
    // 检查是否已加载必要的插件
    if (amap.value && amap.value.DistrictSearch) {

    } else {

      // 在需要的时候再加载插件
    }
    
    // 确保 AMapUI 已加载（AMapUI 需要单独加载，且加载顺序很重要：先加载 AMap，再加载 AMapUI）
    if (window.AMapUI) {

    } else {

      // 确保 AMap 已经加载完成
      if (window.AMap) {
        await loadAMapUI();
      } else {

      }
    }
    
  } catch (error) {

  }
}

// 加载 AMapUI
function loadAMapUI() {
  return new Promise((resolve, reject) => {
    if (window.AMapUI) {

      resolve(window.AMapUI);
      return;
    }
    
    // AMapUI 有自己的加载器
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://webapi.amap.com/ui/1.1/main.js';
    script.async = true;
    
    script.onload = () => {
      if (window.AMapUI) {

        resolve(window.AMapUI);
      } else {

        reject(new Error('AMapUI 加载失败'));
      }
    };
    
    script.onerror = () => {

      reject(new Error('AMapUI 脚本加载失败'));
    };
    
    document.head.appendChild(script);
  });
}



// 计算当前选中迁徙的途径地
const waypoints = computed(() => {
  if (!selectedMigration.value || !selectedMigration.value.geometry) {
    return []
  }
  const coords = selectedMigration.value.geometry.coordinates
  if (!coords || coords.length <= 2) {
    return []
  }
  // 提取中间点作为途径地
  const waypointNames = []
  for (let i = 1; i < coords.length - 1; i++) {
    // 尝试从properties中获取途径地名称
    const waypointName = selectedMigration.value.properties?.[`waypoint_${i}`] || 
                         selectedMigration.value.properties?.[`waypoint_name_${i}`] ||
                         selectedMigration.value.properties?.[`intermediate_${i}`] ||
                         `途径地 ${i}`
    waypointNames.push(waypointName)
  }
  return waypointNames
})

// 按时间排序的迁徙数据
const sortedMigrations = computed(() => {
  return [...allMigrations.value].sort((a, b) => {
    const yearA = a.properties?.estimated_year || a.properties?.start_year || 0
    const yearB = b.properties?.estimated_year || b.properties?.start_year || 0
    return yearA - yearB
  })
})

// 获取迁徙年份显示
function getMigrationYear(migration) {
  const estimatedYear = migration.properties?.estimated_year
  const startYear = migration.properties?.start_year
  const migrationPeriod = migration.properties?.migration_period
  
  if (estimatedYear) {
    return `${estimatedYear}年`
  } else if (startYear) {
    return `${startYear}年`
  } else if (migrationPeriod && migrationPeriod !== '未知') {
    return migrationPeriod
  } else {
    return '未知年代'
  }
}

// 从时间轴选择迁徙
function selectMigrationFromTimeline(migration) {
  selectedMigration.value = migration
  
  // 高亮选中的线路
  const selectedLine = migrationLineMap.get(migration.properties.migration_id)
  polylines.value.forEach(line => {
    if (line === selectedLine) {
      // 高亮选中的线路
      line.setOptions({ 
        strokeOpacity: 1, 
        strokeWeight: 6,
        zIndex: 200
      })
    } else {
      // 淡化其他线路
      line.setOptions({ strokeOpacity: 0.3, strokeWeight: 3 })
    }
  })
  
  // 定位到选中的迁徙路线
  if (mapInstance.value && migration.geometry && migration.geometry.coordinates) {
    const coords = migration.geometry.coordinates
    if (coords.length >= 2) {
      const centerPoint = [
        (coords[0][0] + coords[coords.length - 1][0]) / 2,
        (coords[0][1] + coords[coords.length - 1][1]) / 2
      ]
      mapInstance.value.setCenter(centerPoint)
      mapInstance.value.setZoom(8)
    }
  }
}

// 地图缩放控制
function zoomIn() {
  if (mapInstance.value) {
    const currentZoom = mapInstance.value.getZoom();
    mapInstance.value.setZoom(currentZoom + 1);
  }
}

function zoomOut() {
  if (mapInstance.value) {
    const currentZoom = mapInstance.value.getZoom();
    mapInstance.value.setZoom(currentZoom - 1);
  }
}

function resetZoom() {
  if (mapInstance.value) {
    mapInstance.value.setZoom(5); // 默认缩放级别
    mapInstance.value.setCenter([108.0, 34.0]); // 默认中心点
  }
}

// 全屏功能
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    enterFullscreen();
  } else {
    exitFullscreen();
  }
}

function enterFullscreen() {
  const elem = document.documentElement;
  if (elem.requestFullscreen) {
    elem.requestFullscreen().then(() => {
      isFullscreen.value = true;
    }).catch(err => {

    });
  } else if (elem.mozRequestFullScreen) { /* Firefox */
    elem.mozRequestFullScreen();
    isFullscreen.value = true;
  } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
    elem.webkitRequestFullscreen();
    isFullscreen.value = true;
  } else if (elem.msRequestFullscreen) { /* IE/Edge */
    elem.msRequestFullscreen();
    isFullscreen.value = true;
  }
}

function exitFullscreen() {
  if (document.exitFullscreen) {
    document.exitFullscreen().then(() => {
      isFullscreen.value = false;
    }).catch(err => {

    });
  } else if (document.mozCancelFullScreen) { /* Firefox */
    document.mozCancelFullScreen();
    isFullscreen.value = false;
  } else if (document.webkitExitFullscreen) { /* Chrome, Safari & Opera */
    document.webkitExitFullscreen();
    isFullscreen.value = false;
  } else if (document.msExitFullscreen) { /* IE/Edge */
    document.msExitFullscreen();
    isFullscreen.value = false;
  }
}

// 监听全屏变化事件
function handleFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement;
}

// 监听键盘事件，用于路径对比功能
function handleKeyDown(event) {
  if (event.key === 'Shift') {
    comparisonMode.value = true;
  }
}

function handleKeyUp(event) {
  if (event.key === 'Shift') {
    comparisonMode.value = false;
    
    // 如果已经选择了两条路线，显示对比面板
    if (selectedMigrationsForComparison.value.length === 2) {
      showComparisonPanel.value = true;
    }
  }
}

document.addEventListener('keydown', handleKeyDown);
document.addEventListener('keyup', handleKeyUp);

document.addEventListener('fullscreenchange', handleFullscreenChange);
document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
document.addEventListener('mozfullscreenchange', handleFullscreenChange);
document.addEventListener('MSFullscreenChange', handleFullscreenChange);



// 初始化
onMounted(async () => {
  // 等待 DOM 渲染完成
  await nextTick()
  
  if (!mapContainer.value) {
    error.value = '地图容器未正确初始化'
    errorDescription.value = '请检查控制台了解详细信息'
    loading.value = false
    return
  }
  
  // 加载统计数据
  try {
    statistics.value = await fetchStatistics()

  } catch (err) {

  }
  
  // 加载所有定居点数据
  try {
    locations.value = await fetchLocations()

  } catch (err) {

  }
  
  // 初始化地图
  await initMap()
})


// 初始化地图的函数
async function initMap() {
  if (!mapContainer.value) {

    return
  }
  
  try {
    // 如果已有地图实例，先销毁
    if (mapInstance.value) {
      mapInstance.value.destroy()
      mapInstance.value = null
    }
    

    
    // 初始化地图
    const { map, AMap } = await initAMap(mapContainer.value, {})
    mapInstance.value = map
    amap.value = AMap
    

    
    // 初始化行政区划服务
    await initDistrictServices();
    
    // 获取迁徙数据并渲染
    if (allMigrations && allMigrations.value && allMigrations.value.length > 0) {
      renderMigrationsOnMap()
      // 渲染定居点
      renderSettlements()
      // 渲染热力图

    } else {
      await loadAndRenderData()
    }
    
    // 确保筛选状态正确应用
    updateMapDisplay()
    
    // 延迟设置地图视野，确保所有元素都已添加（使用优化后的方法）
    setTimeout(() => {
      if (mapInstance.value) {
        const allOverlays = [...polylines.value, ...locationMarkers.value]
        if (allOverlays.length > 0) {
          fitView(mapInstance.value, allOverlays, {
            immediately: false,
            avoid: [50, 50, 50, 50],
            maxZoom: 18
          })
        } else {
          // 如果没有数据，设置默认视野
          mapInstance.value.setCenter([108.0, 34.0])
          mapInstance.value.setZoom(5)
        }
      }
    }, 500)
  } catch (err) {

    
    // 根据错误类型提供更友好的提示
    if (err.message && err.message.includes('USERKEY_PLAT_NOMATCH')) {
      error.value = '地图API Key配置错误'
      errorDescription.value = '当前API Key的平台类型不匹配。请检查高德地图控制台，确保API Key是为"Web端(JS API)"平台创建的。'
    } else if (err.message && err.message.includes('Unimplemented type')) {
      error.value = '地图加载警告'
      errorDescription.value = '地图已加载，但某些高级功能可能不可用。这不会影响基本的地图显示和交互功能。'
      // 对于这个错误，我们仍然尝试继续使用地图
      loading.value = false
      return
    } else {
      error.value = `地图初始化失败`
      errorDescription.value = err.message || '未知错误，请检查控制台了解详细信息'
    }
    loading.value = false
  }
}

// 清理
onUnmounted(() => {
  // 清理键盘事件监听器
  document.removeEventListener('keydown', handleKeyDown);
  document.removeEventListener('keyup', handleKeyUp);
  
  // 使用增强的清理函数
  enhancedCleanup();
  
  // 清理地图实例
  if (mapInstance.value) {
    try {
      // 清理自定义控件
      cleanupCustomControls(mapInstance.value);
      
      mapInstance.value.destroy()
    } catch (error) {

    }
    mapInstance.value = null
  }
  
  // 清理信息窗体
  if (infoWindow.value) {
    try {
      infoWindow.value.close()
    } catch (error) {

    }
    infoWindow.value = null
  }
  
  // 清理对比相关状态
  selectedMigrationsForComparison.value = [];
  showComparisonPanel.value = false;
})

function closeInfoCard() {
  selectedMigration.value = null
  // 恢复所有路径的透明度
  polylines.value.forEach(line => {
    line.setOptions({ strokeOpacity: 0.7, strokeWeight: 4 })
  })
}

// 关闭对比面板
function closeComparisonPanel() {
  showComparisonPanel.value = false;
  
  // 清除选中的对比路线并恢复样式
  selectedMigrationsForComparison.value.forEach(migration => {
    const line = migrationLineMap.get(migration.properties.migration_id);
    if (line) {
      // 查找原始颜色
      const originalIndex = migrations.value.findIndex(
        m => m.properties.migration_id === migration.properties.migration_id
      );
      if (originalIndex > -1) {
        const colorPalette = [
          { main: '#FF6B6B', light: '#FF8E8E' }, // 珊瑚红
          { main: '#4ECDC4', light: '#6EDDD6' }, // 青绿色
          { main: '#45B7D1', light: '#6BC5DB' }, // 天蓝色
          { main: '#FFBE0B', light: '#FFD04D' }, // 金黄色
          { main: '#FB5607', light: '#FC7A3A' }, // 橙红色
          { main: '#8338EC', light: '#9D5FED' }, // 紫色
          { main: '#3A86FF', light: '#5DA0FF' }, // 蓝色
          { main: '#38B000', light: '#5BC020' }, // 绿色
          { main: '#9EF01A', light: '#B3F34A' }, // 黄绿色
          { main: '#FF006E', light: '#FF3399' }  // 粉红色
        ];
        const colorScheme = colorPalette[originalIndex % colorPalette.length];
        line.setOptions({ 
          strokeOpacity: 0.7, 
          strokeWeight: 4,
          strokeColor: colorScheme.main,
          zIndex: 50
        });
      }
    }
  });
  
  selectedMigrationsForComparison.value = [];
}

// 清除所有选中的对比路线
function clearComparisonSelection() {
  selectedMigrationsForComparison.value = [];
  
  // 恢复所有线路的原始样式
  polylines.value.forEach((line, index) => {
    const colorPalette = [
      { main: '#FF6B6B', light: '#FF8E8E' }, // 珊瑚红
      { main: '#4ECDC4', light: '#6EDDD6' }, // 青绿色
      { main: '#45B7D1', light: '#6BC5DB' }, // 天蓝色
      { main: '#FFBE0B', light: '#FFD04D' }, // 金黄色
      { main: '#FB5607', light: '#FC7A3A' }, // 橙红色
      { main: '#8338EC', light: '#9D5FED' }, // 紫色
      { main: '#3A86FF', light: '#5DA0FF' }, // 蓝色
      { main: '#38B000', light: '#5BC020' }, // 绿色
      { main: '#9EF01A', light: '#B3F34A' }, // 黄绿色
      { main: '#FF006E', light: '#FF3399' }  // 粉红色
    ];
    const colorScheme = colorPalette[index % colorPalette.length];
    line.setOptions({ 
      strokeOpacity: 0.7, 
      strokeWeight: 4,
      strokeColor: colorScheme.main,
      zIndex: 50
    });
  });
}

// 清除对比选择并关闭面板
function clearComparisonSelectionAndClosePanel() {
  clearComparisonSelection();
  showComparisonPanel.value = false;
}

// 应用筛选条件
function applyFilters() {
  // 筛选迁徙数据
  filteredMigrations.value = allMigrations.value.filter(migration => {
    const props = migration.properties || {}
    
    // 分支筛选
    if (filterBranches.value.length > 0) {
      const branchName = props.branch_name || props.surname
      if (!branchName || !filterBranches.value.includes(branchName)) {
        return false
      }
    }
    
    // 时间段筛选
    const year = props.estimated_year || props.start_year
    if (year) {
      if (filterYearStart.value !== null && year < filterYearStart.value) {
        return false
      }
      if (filterYearEnd.value !== null && year > filterYearEnd.value) {
        return false
      }
    } else {
      // 如果没有年份信息，但设置了年份筛选，则排除
      if (filterYearStart.value !== null || filterYearEnd.value !== null) {
        return false
      }
    }
    
    // 迁徙原因筛选
    if (filterReasons.value.length > 0) {
      const reason = props.migration_reason || props.reason
      if (!reason || !filterReasons.value.includes(reason.trim())) {
        return false
      }
    }
    
    // 地点筛选
    if (filterLocation.value.trim()) {
      const locationKeyword = filterLocation.value.trim().toLowerCase()
      const fromName = (props.from_name || '').toLowerCase()
      const toName = (props.to_name || '').toLowerCase()
      if (!fromName.includes(locationKeyword) && !toName.includes(locationKeyword)) {
        return false
      }
    }
    
    return true
  })
  
  // 更新显示的迁徙数据
  migrations.value = filteredMigrations.value
  

  
  // 重新渲染地图
  if (amap.value && mapInstance.value) {
    renderMigrationsOnMap()
    updateMapDisplay()
  }
}

// 重置所有筛选条件
function resetFilters() {
  filterBranches.value = []
  filterYearStart.value = null
  filterYearEnd.value = null
  filterReasons.value = []
  filterLocation.value = ''
  showMigrations.value = true
  showSettlements.value = true
  
  // 应用重置后的筛选（即显示所有数据）
  applyFilters()
}

// 地图样式切换
function handleMapStyleChange(style) {
  if (mapInstance.value) {
    try {
      // 高德地图支持的标准样式名称
      mapInstance.value.setMapStyle(style);
      mapStyle.value = style;
      

    } catch (error) {

      // 如果 setMapStyle 失败，使用默认样式
      try {
        mapInstance.value.setMapStyle('normal');
        mapStyle.value = 'normal';

      } catch (fallbackError) {

      }
    }
  }
}

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

    }
  }
}

// 根据筛选状态更新地图显示
function updateMapDisplay() {
  if (!mapInstance.value) return
  
  // 控制迁徙线显示
  if (polylines.value && polylines.value.length > 0) {
    polylines.value.forEach(line => {
      if (showMigrations.value) {
        // 检查线路是否已在地图上，如果不在则添加
        try {
          const overlays = mapInstance.value.getAllOverlays ? mapInstance.value.getAllOverlays('polyline') : [];
          if (!overlays.includes(line)) {
            mapInstance.value.add(line)
          }
        } catch {
          // 如果无法检查，直接添加
          mapInstance.value.add(line);
        }
      } else {
        // 移除线路
        try {
          mapInstance.value.remove(line)
        } catch {
          // 忽略移除错误
        }
      }
    })
  }
  
  // 控制定居点显示
  if (locationMarkers.value && locationMarkers.value.length > 0) {
    locationMarkers.value.forEach(marker => {
      if (showSettlements.value) {
        // 检查标记是否已在地图上，如果不在则添加
        try {
          const overlays = mapInstance.value.getAllOverlays ? mapInstance.value.getAllOverlays('marker') : [];
          if (!overlays.includes(marker)) {
            mapInstance.value.add(marker)
          }
        } catch {
          // 如果无法检查，直接添加
          mapInstance.value.add(marker);
        }
      } else {
        // 移除标记
        try {
          mapInstance.value.remove(marker)
        } catch {
          // 忽略移除错误
        }
      }
    })
  }
  
  // 重新调整地图视野以适应所有可见内容
  if (showMigrations.value || showSettlements.value) {
    const visibleOverlays = []
    if (showMigrations.value && polylines.value.length > 0) {
      visibleOverlays.push(...polylines.value)
    }
    if (showSettlements.value && locationMarkers.value.length > 0) {
      visibleOverlays.push(...locationMarkers.value)
    }
    
    if (visibleOverlays.length > 0) {
      // 延迟执行以确保所有覆盖物都已添加到地图上（使用优化后的方法）
      setTimeout(() => {
        fitView(mapInstance.value, visibleOverlays, {
          immediately: false,
          avoid: [50, 50, 50, 50],
          maxZoom: 18
        })
      }, 100)
    }
  }
}

async function loadAndRenderData(searchKeyword = '') {
  try {

    
    // 始终获取数据，无论是否有搜索关键词
    const searchResults = await fetchMigrations(searchKeyword)

    
    // 更新所有相关状态
    allMigrations.value = searchResults
    migrations.value = searchResults
    filteredMigrations.value = searchResults
    
    // 应用筛选条件
    applyFilters()
    


    
    // 初始化筛选选项后应用筛选
    if (amap.value && migrations.value.length) {
      renderMigrationsOnMap()
      // 渲染定居点
      renderSettlements()
      // 渲染热力图

      // 确保筛选状态正确应用
      updateMapDisplay()
      // 清除错误信息
      error.value = null
    } else {
      // 根据情况显示不同的信息
      if (searchKeyword && searchKeyword.trim()) {

        error.value = null // 搜索时不显示错误，只在控制台提示
      } else if (allMigrations && allMigrations.value && allMigrations.value.length === 0) {

        error.value = '未获取到迁徙数据'
        errorDescription.value = '请确保后端服务正常运行，并且数据库中有相关数据'
      } else {

        error.value = null // 筛选时不显示错误，只在控制台提示
      }
    }
  } catch (err) {

    error.value = `加载数据失败`
    errorDescription.value = err.message
  } finally {
    loading.value = false
  }
}

// 防抖函数
function debounce(func, delay) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      func.apply(this, args)
    }, delay)
  }
}

// 远程搜索函数，用于el-select的remote-method
async function handleRemoteSearch(query) {
  if (!query || query.trim() === '') {
    searchResults.value = []
    // 清空搜索时显示所有数据
    await loadAndRenderData('')
    return
  }

  searchLoading.value = true
  try {
    const results = await fetchMigrations(query)

    
    // 格式化搜索结果
    searchResults.value = results.map((migration, index) => {
      const props = migration.properties
      return {
        id: index + 1,
        value: query + '-' + index, // 唯一值
        label: props.branch_name || props.surname, // 用于搜索匹配
        title: props.branch_name || props.surname,
        subtitle: `${props.from_location} → ${props.to_location} (${props.migration_period || '未知时期'})`,
        migration: migration // 存储完整的迁徙数据
      }
    })
    
    // 立即显示搜索结果，确保所有相关状态都被更新
    searchKeyword.value = query
    allMigrations.value = results
    filteredMigrations.value = results
    migrations.value = results
    
    // 应用筛选条件
    applyFilters()
    
    // 渲染到地图
    renderMigrationsOnMap()
    renderSettlements()
    updateMapDisplay()
  } catch (err) {

    searchResults.value = []
    allMigrations.value = []
    migrations.value = []
    filteredMigrations.value = []
    renderMigrationsOnMap()
    renderSettlements()
    updateMapDisplay()
  } finally {
    searchLoading.value = false
  }
}

// 搜索结果选择处理函数
async function handleSearchResultSelect(value) {
  if (!value) return
  
  // 查找选中的搜索结果
  const selectedItem = searchResults.value.find(item => item.value === value)
  if (selectedItem && selectedItem.migration) {
    // 显示选中的迁徙数据
    searchKeyword.value = selectedItem.title
    migrations.value = [selectedItem.migration]
    filteredMigrations.value = [selectedItem.migration]
    
    // 渲染到地图
    renderMigrationsOnMap()
    renderSettlements()
    updateMapDisplay()
    
    // 定位到该迁徙路线
    if (amap.value && mapInstance.value && selectedItem.migration.geometry && selectedItem.migration.geometry.coordinates) {
      const coords = selectedItem.migration.geometry.coordinates
      const centerPoint = [
        (coords[0][0] + coords[coords.length - 1][0]) / 2,
        (coords[0][1] + coords[coords.length - 1][1]) / 2
      ]
      mapInstance.value.setCenter(centerPoint)
      mapInstance.value.setZoom(8)
    }
  }
}

// 搜索功能
async function handleSearch() {
  const keyword = searchKeyword.value.trim()

  try {
    // 使用loadAndRenderData函数处理搜索，保持逻辑一致性
    await loadAndRenderData(keyword)
    
    // 如果有搜索关键词且有匹配结果，定位到第一条
    if (keyword && filteredMigrations.value.length > 0 && amap.value && mapInstance.value) {
      const firstMatch = filteredMigrations.value[0]
      if (firstMatch.geometry && firstMatch.geometry.coordinates && firstMatch.geometry.coordinates.length >= 2) {
        const coords = firstMatch.geometry.coordinates
        const centerPoint = [
          (coords[0][0] + coords[coords.length - 1][0]) / 2,
          (coords[0][1] + coords[coords.length - 1][1]) / 2
        ]
        mapInstance.value.setCenter(centerPoint)
        mapInstance.value.setZoom(8)
      }
    }
  } catch (err) {

    error.value = '搜索失败'
    errorDescription.value = err.message
  }
}

// 添加防抖的搜索函数
const debouncedHandleSearch = debounce(handleSearch, 300)

async function handleSearchClear() {
  searchKeyword.value = ''
  selectedSearchResult.value = null
  // 重新加载所有数据
  await loadAndRenderData('')
}


function renderMigrationsOnMap() {
  if (!amap.value || !mapInstance.value) {
    error.value = '地图API未正确初始化'
    errorDescription.value = '请检查控制台了解详细信息'
    return
  }
  
  try {
    // 移除之前添加的迁徙线路和相关标记，而不是清除整个地图
    if (polylines.value.length > 0) {
      removeOverlays(mapInstance.value, polylines.value)
    }
    if (waypointMarkers.value.length > 0) {
      removeOverlays(mapInstance.value, waypointMarkers.value)
    }
    if (locationMarkers.value.length > 0) {
      removeOverlays(mapInstance.value, locationMarkers.value)
    }
    
    // 清空本地数组和映射关系
    polylines.value = []
    waypointMarkers.value = []
    locationMarkers.value = []
    migrationLineMap.clear() // 清空映射关系
    
    // 创建迁徙线路集合
    const lines = []
    const markers = []
    
    // 定义美观的颜色方案
    const colorPalette = [
      { main: '#FF6B6B', light: '#FF8E8E' }, // 珊瑚红
      { main: '#4ECDC4', light: '#6EDDD6' }, // 青绿色
      { main: '#45B7D1', light: '#6BC5DB' }, // 天蓝色
      { main: '#FFBE0B', light: '#FFD04D' }, // 金黄色
      { main: '#FB5607', light: '#FC7A3A' }, // 橙红色
      { main: '#8338EC', light: '#9D5FED' }, // 紫色
      { main: '#3A86FF', light: '#5DA0FF' }, // 蓝色
      { main: '#38B000', light: '#5BC020' }, // 绿色
      { main: '#9EF01A', light: '#B3F34A' }, // 黄绿色
      { main: '#FF006E', light: '#FF3399' }  // 粉红色
    ]
    
    // 过滤出有效的迁徙数据
    const validMigrations = migrations.value.filter(migration => {
      return migration.geometry && 
             migration.geometry.coordinates && 
             migration.geometry.coordinates.length >= 2
    })
    
    // 批量创建图标，避免重复计算
    const iconCache = new Map()
    
    validMigrations.forEach((migration, index) => {
      try {
        const coords = migration.geometry.coordinates
        const startPoint = [coords[0][0], coords[0][1]]
        const endPoint = coords.length > 1 ? [coords[coords.length - 1][0], coords[coords.length - 1][1]] : startPoint
        
        // 选择颜色（循环使用）
        const colorScheme = colorPalette[index % colorPalette.length]
        
        // 如果有多个坐标点，使用实际路径；否则创建平滑的曲线路径
        let path
        if (coords.length > 2) {
          // 使用实际的坐标点作为路径
          path = coords.map(coord => [coord[0], coord[1]])
        } else {
          // 创建平滑的曲线路径
          path = createCurvedPath(startPoint, endPoint)
        }
        
        // 创建迁徙线路 - 使用 Polyline 并添加样式
        const line = new amap.value.Polyline({
          path: path,
          strokeColor: colorScheme.main,
          strokeWeight: 4,
          strokeOpacity: 0.7,
          strokeStyle: 'solid',
          lineJoin: 'round',
          lineCap: 'round',
          isOutline: true,
          outlineColor: 'rgba(255, 255, 255, 0.8)',
          borderWeight: 2,
          zIndex: 50
        })
        
        // 添加悬停效果
        line.on('mouseover', () => {
          if (!mapInstance.value) return
          line.setOptions({ 
            strokeWeight: 6, 
            strokeOpacity: 1,
            zIndex: 100
          })
        })
        
        line.on('mouseout', () => {
          if (!mapInstance.value || !migration) return
          if (selectedMigration.value !== migration) {
            line.setOptions({ 
              strokeWeight: 4, 
              strokeOpacity: 0.7,
              zIndex: 50
            })
          }
        })
        
        // 绑定点击事件
        line.on('click', () => {
          if (!mapInstance.value) return
          
          // 如果处于对比模式，添加到对比列表
          if (comparisonMode.value) {
            // 检查是否已存在这条线路
            const existingIndex = selectedMigrationsForComparison.value.findIndex(
              m => m.properties.migration_id === migration.properties.migration_id
            );
            
            if (existingIndex > -1) {
              // 如果已存在，则移除
              selectedMigrationsForComparison.value.splice(existingIndex, 1);
              // 恢复线路原有样式
              const originalIndex = migrations.value.findIndex(
                m => m.properties.migration_id === migration.properties.migration_id
              );
              const colorScheme = colorPalette[originalIndex % colorPalette.length];
              line.setOptions({ 
                strokeOpacity: 0.7, 
                strokeWeight: 4,
                strokeColor: colorScheme.main,
                zIndex: 50
              });
            } else if (selectedMigrationsForComparison.value.length < 2) {
              // 如果未达到两条，添加到对比列表
              selectedMigrationsForComparison.value.push(migration);
              // 高亮选中的线路
              line.setOptions({ 
                strokeOpacity: 1, 
                strokeWeight: 8,
                strokeColor: '#FFD700', // 黄色高亮
                zIndex: 300
              })
              
              // 如果已选两条，自动显示对比面板
              if (selectedMigrationsForComparison.value.length === 2) {
                showComparisonPanel.value = true;
              }
            } else {
              // 如果已经有两条线路被选中，不允许再添加
              ElMessage.warning('最多只能选择两条路线进行对比');
            }
          } else {
            // 非对比模式，保持原有行为
            selectedMigration.value = migration
            
            // 高亮选中的线路
            polylines.value.forEach(l => {
              if (l !== line) {
                l.setOptions({ strokeOpacity: 0.3, strokeWeight: 3 })
              }
            })
            line.setOptions({ 
              strokeOpacity: 1, 
              strokeWeight: 6,
              zIndex: 200
            })
          }
        })
        
        lines.push(line)
        polylines.value.push(line)
        
        // 将migration和line关联起来
        if (migration.properties.migration_id) {
          migrationLineMap.set(migration.properties.migration_id, line)
        }
        
        // 创建途径地标记
        if (coords.length > 2) {
          for (let i = 1; i < coords.length - 1; i++) {
            try {
              const waypointCoord = [coords[i][0], coords[i][1]]
              
              // 缓存图标，避免重复创建
              const waypointIconKey = `waypoint_${colorScheme.main}`
              let waypointIcon
              if (iconCache.has(waypointIconKey)) {
                waypointIcon = iconCache.get(waypointIconKey)
              } else {
                waypointIcon = createCustomIcon('waypoint', colorScheme.main)
                iconCache.set(waypointIconKey, waypointIcon)
              }
              
              const waypointMarker = new amap.value.Marker({
                position: new amap.value.LngLat(waypointCoord[0], waypointCoord[1]),
                icon: waypointIcon,
                zIndex: 90,
                title: migration.properties[`waypoint_${i}`] || migration.properties[`waypoint_name_${i}`] || `途径地 ${i}`
              })
              
              // 添加途径地标记点击事件
              waypointMarker.on('click', () => {
                if (!mapInstance.value) return
                selectedMigration.value = {
                  properties: {
                    ...migration.properties,
                    waypoint_index: i
                  },
                  geometry: migration.geometry
                }
                
                // 高亮选中的线路
                polylines.value.forEach(l => {
                  if (l !== line) {
                    l.setOptions({ strokeOpacity: 0.3, strokeWeight: 3 })
                  }
                })
                line.setOptions({ 
                  strokeOpacity: 1, 
                  strokeWeight: 6,
                  zIndex: 200
                })
              })
              
              markers.push(waypointMarker)
              waypointMarkers.value.push(waypointMarker)
            } catch (markerError) {
              console.error('创建途径地标记失败:', markerError)
            }
          }
        }
        
        // 创建起点标记 
        const startIconKey = `start_${colorScheme.main}`
        let startIcon
        if (iconCache.has(startIconKey)) {
          startIcon = iconCache.get(startIconKey)
        } else {
          startIcon = createCustomIcon('start', colorScheme.main)
          iconCache.set(startIconKey, startIcon)
        }
        
        const startMarker = new amap.value.Marker({
          position: new amap.value.LngLat(startPoint[0], startPoint[1]),
          icon: startIcon,
          zIndex: 100,
          title: migration.properties.from_name || '起点'
        })
        
        // 添加起点标记点击事件
        startMarker.on('click', () => {
          if (!mapInstance.value) return
          selectedMigration.value = {
            properties: {
              branch_name: migration.properties.branch_name,
              surname: migration.properties.surname,
              migration_period: migration.properties.migration_period,
              migration_reason: migration.properties.migration_reason,
              key_figure: migration.properties.key_figure,
              from_name: migration.properties.from_name,
              to_name: migration.properties.to_name
            },
            geometry: {
              coordinates: [startPoint]
            }
          }
          
          // 高亮选中的线路
          polylines.value.forEach(l => {
            if (l !== line) {
              l.setOptions({ strokeOpacity: 0.3, strokeWeight: 3 })
            }
          })
          line.setOptions({ 
            strokeOpacity: 1, 
            strokeWeight: 6,
            zIndex: 200
          })
        })
        
        // 创建终点标记
        const endIconKey = `end_${colorScheme.main}`
        let endIcon
        if (iconCache.has(endIconKey)) {
          endIcon = iconCache.get(endIconKey)
        } else {
          endIcon = createCustomIcon('end', colorScheme.main)
          iconCache.set(endIconKey, endIcon)
        }
        
        const endMarker = new amap.value.Marker({
          position: new amap.value.LngLat(endPoint[0], endPoint[1]),
          icon: endIcon,
          zIndex: 100,
          title: migration.properties.to_name || '终点'
        })
        
        // 添加终点标记点击事件
        endMarker.on('click', () => {
          if (!mapInstance.value) return
          selectedMigration.value = {
            properties: {
              branch_name: migration.properties.branch_name,
              surname: migration.properties.surname,
              migration_period: migration.properties.migration_period,
              migration_reason: migration.properties.migration_reason,
              key_figure: migration.properties.key_figure,
              from_name: migration.properties.from_name,
              to_name: migration.properties.to_name
            },
            geometry: {
              coordinates: [endPoint]
            }
          }
          
          // 高亮选中的线路
          polylines.value.forEach(l => {
            if (l !== line) {
              l.setOptions({ strokeOpacity: 0.3, strokeWeight: 3 })
            }
          })
          line.setOptions({ 
            strokeOpacity: 1, 
            strokeWeight: 6,
            zIndex: 200
          })
        })
        
        // 将起点和终点标记添加到地图上
        markers.push(startMarker)
        markers.push(endMarker)
        locationMarkers.value.push(startMarker)
        locationMarkers.value.push(endMarker)
      } catch (itemError) {
        console.error('渲染迁徙数据项失败:', itemError)
      }
    })
    
    // 批量添加线路到地图
    if (lines.length > 0) {
      addOverlays(mapInstance.value, lines)
    }
    
    // 批量添加标记到地图
    if (markers.length > 0) {
      addOverlays(mapInstance.value, markers)
    }
  } catch (renderError) {
    console.error('渲染迁徙数据失败:', renderError)
    error.value = '渲染迁徙数据失败'
    errorDescription.value = renderError.message
  }
}

// 创建曲线路径（模拟贝塞尔曲线效果）
function createCurvedPath(start, end) {
  const midLng = (start[0] + end[0]) / 2
  const midLat = (start[1] + end[1]) / 2
  
  // 计算控制点，使路径呈现弧形
  const distance = Math.sqrt(
    Math.pow(end[0] - start[0], 2) + Math.pow(end[1] - start[1], 2)
  )
  
  // 根据距离调整弧度
  const curvature = Math.min(distance * 0.3, 2)
  const controlLng = midLng + (Math.random() - 0.5) * curvature
  const controlLat = midLat + curvature
  
  // 生成平滑的曲线点
  const points = []
  const segments = 20
  
  for (let i = 0; i <= segments; i++) {
    const t = i / segments
    const lng = (1 - t) * (1 - t) * start[0] + 2 * (1 - t) * t * controlLng + t * t * end[0]
    const lat = (1 - t) * (1 - t) * start[1] + 2 * (1 - t) * t * controlLat + t * t * end[1]
    points.push([lng, lat])
  }
  
  return points
}

// 创建自定义图标
function createCustomIcon(type, color) {
  const size = type === 'start' ? 24 : type === 'waypoint' ? 20 : 24
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')
  
  // 绘制圆形背景
  ctx.beginPath()
  ctx.arc(size / 2, size / 2, size / 2 - 2, 0, Math.PI * 2)
  ctx.fillStyle = color
  ctx.fill()
  
  // 绘制白色边框
  ctx.strokeStyle = '#FFFFFF'
  ctx.lineWidth = 2
  ctx.stroke()
  
  // 绘制内部图标
  ctx.fillStyle = '#FFFFFF'
  if (type === 'start') {
    // 起点：实心圆
    ctx.beginPath()
    ctx.arc(size / 2, size / 2, size / 4, 0, Math.PI * 2)
    ctx.fill()
  } else if (type === 'waypoint') {
    // 途径地：菱形
    ctx.beginPath()
    ctx.moveTo(size / 2, size / 2 - size / 4)
    ctx.lineTo(size / 2 + size / 4, size / 2)
    ctx.lineTo(size / 2, size / 2 + size / 4)
    ctx.lineTo(size / 2 - size / 4, size / 2)
    ctx.closePath()
    ctx.fill()
  } else if (type === 'end') {
    // 终点：星形
    drawStar(ctx, size / 2, size / 2, size / 4, 5)
    ctx.fill()
  }
  
  return new amap.value.Icon({
    size: new amap.value.Size(size, size),
    image: canvas.toDataURL(),
    imageSize: new amap.value.Size(size, size)
  })
}

// 创建定居点图标
function createSettlementIcon(isOrigin = false) {
  const size = isOrigin ? 32 : 28 // 起源点更大
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')
  
  if (isOrigin) {
    // 起源点：金色星形加光环
    // 绘制光环
    const gradient = ctx.createRadialGradient(size / 2, size / 2, size / 4, size / 2, size / 2, size / 2)
    gradient.addColorStop(0, 'rgba(255, 215, 0, 0.5)')
    gradient.addColorStop(1, 'rgba(255, 215, 0, 0)')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, size, size)
    
    // 绘制外圆
    ctx.beginPath()
    ctx.arc(size / 2, size / 2, size / 2 - 4, 0, Math.PI * 2)
    ctx.fillStyle = '#FFD700' // 金色
    ctx.fill()
    ctx.strokeStyle = '#FFA500' // 深金色边框
    ctx.lineWidth = 2
    ctx.stroke()
    
    // 绘制内部星形
    ctx.fillStyle = '#FFF'
    drawStar(ctx, size / 2, size / 2, size / 3, 5)
    ctx.fill()
    
    // 绘制内圆
    ctx.beginPath()
    ctx.arc(size / 2, size / 2, size / 8, 0, Math.PI * 2)
    ctx.fillStyle = '#FFD700'
    ctx.fill()
  } else {
    // 普通定居点：绿色房子图标
    // 绘制外圆
    ctx.beginPath()
    ctx.arc(size / 2, size / 2, size / 2 - 3, 0, Math.PI * 2)
    ctx.fillStyle = '#10B981' // 绿色
    ctx.fill()
    ctx.strokeStyle = '#059669' // 深绿色边框
    ctx.lineWidth = 2
    ctx.stroke()
    
    // 绘制房子图标
    ctx.fillStyle = '#FFF'
    const houseSize = size / 3
    const houseX = size / 2 - houseSize / 2
    const houseY = size / 2 - houseSize / 4
    
    // 房顶
    ctx.beginPath()
    ctx.moveTo(size / 2, houseY - houseSize / 3)
    ctx.lineTo(houseX + houseSize, houseY + houseSize / 6)
    ctx.lineTo(houseX, houseY + houseSize / 6)
    ctx.closePath()
    ctx.fill()
    
    // 房身
    ctx.fillRect(houseX, houseY + houseSize / 6, houseSize, houseSize / 2)
  }
  
  return new amap.value.Icon({
    size: new amap.value.Size(size, size),
    image: canvas.toDataURL(),
    imageSize: new amap.value.Size(size, size)
  })
}



// 监听图层选中状态变化
watch(checkedLayers, (newChecked, oldChecked) => {
  // 找出新增的选中项
  const added = newChecked.filter(item => !oldChecked.includes(item));
  added.forEach(layerId => {
    const layer = addedLayers.value.find(l => l.id === layerId);
    if (layer && layer.instance) {
      layer.instance.setMap(mapInstance.value);
      layer.visible = true;
    }
  });
  
  // 找出取消选中的项
  const removed = oldChecked.filter(item => !newChecked.includes(item));
  removed.forEach(layerId => {
    const layer = addedLayers.value.find(l => l.id === layerId);
    if (layer && layer.instance) {
      layer.instance.setMap(null);
      layer.visible = false;
    }
  });
}, { deep: true });

// 添加瓦片图层
function addTileLayer() {
  if (!amap.value || !mapInstance.value || !tileLayerUrl.value) {
    ElMessage.error('请输入有效的瓦片图层URL');
    return;
  }
  
  try {
    const layerId = layerIdCounter.value++;
    const tileLayer = createRasterLayer(amap.value, {
      type: 'tile',
      tileUrl: tileLayerUrl.value,
      opacity: tileLayerOpacity.value,
      zIndex: 20
    });
    
    if (tileLayer) {
      tileLayer.setMap(mapInstance.value);
      
      // 添加到图层列表
      addedLayers.value.push({
        id: layerId,
        name: '瓦片图层-' + layerId,
        type: '瓦片图层',
        url: tileLayerUrl.value,
        opacity: tileLayerOpacity.value,
        instance: tileLayer,
        visible: true
      });
      
      // 默认选中
      checkedLayers.value.push(layerId);
      
      ElMessage.success('瓦片图层添加成功');
      tileLayerUrl.value = ''; // 清空输入框
    }
  } catch (error) {
    console.error('添加瓦片图层失败:', error);
    ElMessage.error('添加瓦片图层失败');
  }
}

// 添加单张图片图层
function addImageLayer() {
  if (!amap.value || !mapInstance.value || !imageLayerUrl.value) {
    ElMessage.error('请输入有效的图片URL');
    return;
  }
  
  try {
    // 这里简化处理，实际应用中需要用户指定图片的地理范围
    // 示例：使用中国大致范围作为默认边界
    const bounds = new amap.value.Bounds(
      [73.5, 18.1], // 西南角
      [135.1, 53.5]  // 东北角
    );
    
    const layerId = layerIdCounter.value++;
    const imageLayer = createRasterLayer(amap.value, {
      type: 'image',
      url: imageLayerUrl.value,
      bounds: bounds,
      opacity: imageLayerOpacity.value,
      zIndex: 20
    });
    
    if (imageLayer) {
      imageLayer.setMap(mapInstance.value);
      
      // 添加到图层列表
      addedLayers.value.push({
        id: layerId,
        name: '图片图层-' + layerId,
        type: '单张图片',
        url: imageLayerUrl.value,
        opacity: imageLayerOpacity.value,
        bounds: bounds,
        instance: imageLayer,
        visible: true
      });
      
      // 默认选中
      checkedLayers.value.push(layerId);
      
      ElMessage.success('单张图片图层添加成功');
      imageLayerUrl.value = ''; // 清空输入框
    }
  } catch (error) {
    console.error('添加单张图片图层失败:', error);
    ElMessage.error('添加单张图片图层失败');
  }
}

// 切换热力图显示
function toggleHeatMap() {
  if (!amap.value || !mapInstance.value) {
    ElMessage.error('地图尚未初始化');
    return;
  }
  
  try {
    if (showHeatMap.value) {
      // 关闭热力图
      if (heatmapLayer.value) {
        heatmapLayer.value.setMap(null);
        heatmapLayer.value = null;
      }
      showHeatMap.value = false;
      
      // 从图层列表中移除热力图
      const heatmapIndex = addedLayers.value.findIndex(layer => layer.type === '热力图');
      if (heatmapIndex !== -1) {
        const heatmapLayer = addedLayers.value[heatmapIndex];
        // 从选中列表中移除
        const checkedIndex = checkedLayers.value.indexOf(heatmapLayer.id);
        if (checkedIndex !== -1) {
          checkedLayers.value.splice(checkedIndex, 1);
        }
        // 从列表中移除
        addedLayers.value.splice(heatmapIndex, 1);
      }
      
      ElMessage.success('热力图已关闭');
    } else {
      // 显示热力图
      // 从迁徙数据和定居点数据生成热力图数据
      const heatmapData = generateHeatmapData();
      
      if (heatmapData.length === 0) {
        ElMessage.warning('没有足够的数据生成热力图');
        return;
      }
      
      // 创建热力图，并直接关联到地图
      const heatmap = createHeatMap(amap.value, mapInstance.value, heatmapData, {
        radius: heatmapRadius.value,
        opacity: heatmapOpacity.value,
        zIndex: 30
      });
      
      if (heatmap) {
        heatmapLayer.value = heatmap;
        showHeatMap.value = true;
        
        // 添加到图层列表
        const layerId = layerIdCounter.value++;
        addedLayers.value.push({
          id: layerId,
          name: '热力图-' + layerId,
          type: '热力图',
          radius: heatmapRadius.value,
          opacity: heatmapOpacity.value,
          instance: heatmap,
          visible: true
        });
        
        // 默认选中
        checkedLayers.value.push(layerId);
        
        ElMessage.success('热力图显示成功');
      }
    }
  } catch (error) {
    console.error('切换热力图失败:', error);
    ElMessage.error('切换热力图失败');
  }
}

// 生成热力图数据
function generateHeatmapData() {
  const data = [];
  
  // 从迁徙数据中提取起点和终点
  if (allMigrations && allMigrations.value) {
    allMigrations.value.forEach(migration => {
      if (migration && migration.geometry && migration.geometry.coordinates) {
        const coords = migration.geometry.coordinates;
        
        // 添加起点
        if (coords[0]) {
          data.push([
            coords[0][0],
            coords[0][1],
            3 // 权重
          ]);
        }
        
        // 添加终点
        if (coords[coords.length - 1]) {
          data.push([
            coords[coords.length - 1][0],
            coords[coords.length - 1][1],
            3 // 权重
          ]);
        }
        
        // 添加途径点
        for (let i = 1; i < coords.length - 1; i++) {
          if (coords[i]) {
            data.push([
              coords[i][0],
              coords[i][1],
              2 // 途经点权重稍低
            ]);
          }
        }
      }
    });
  }
  
  // 从定居点数据中提取点
  if (locations && locations.value) {
    locations.value.forEach(location => {
      if (location && location.longitude && location.latitude) {
        const weight = location.type === 'origin' ? 5 : location.type === 'settlement' ? 4 : 2;
        data.push([
          parseFloat(location.longitude),
          parseFloat(location.latitude),
          weight
        ]);
      }
    });
  }
  
  return data;
}

// 移除图层
function removeLayer(layerId) {
  const layerIndex = addedLayers.value.findIndex(layer => layer.id === layerId);
  if (layerIndex === -1) return;
  
  try {
    const layer = addedLayers.value[layerIndex];
    layer.instance.setMap(null);
    
    // 从列表中移除
    addedLayers.value.splice(layerIndex, 1);
    
    // 从选中列表中移除
    const checkedIndex = checkedLayers.value.indexOf(layerId);
    if (checkedIndex !== -1) {
      checkedLayers.value.splice(checkedIndex, 1);
    }
    
    ElMessage.success('图层移除成功');
  } catch (error) {
    console.error('移除图层失败:', error);
    ElMessage.error('移除图层失败');
  }
}

// 更新图层透明度
function updateLayerOpacity(layerId, opacity) {
  const layer = addedLayers.value.find(layer => layer.id === layerId);
  if (layer && layer.instance) {
    try {
      layer.instance.setOptions({ opacity: opacity });
    } catch (error) {
      console.error('更新图层透明度失败:', error);
    }
  }
}

// 重命名图层
function renameLayer(layerId) {
  const layer = addedLayers.value.find(layer => layer.id === layerId);
  if (!layer) return;
  
  ElMessageBox.prompt('请输入新的图层名称', '重命名图层', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: layer.name,
    inputPlaceholder: '图层名称'
  }).then(({ value }) => {
    if (value.trim()) {
      layer.name = value.trim();
      ElMessage.success('图层重命名成功');
    }
  }).catch(() => {
    // 用户取消操作
  });
}

// 上移图层
function moveLayerUp(layerId) {
  const layerIndex = addedLayers.value.findIndex(layer => layer.id === layerId);
  if (layerIndex <= 0) return;
  
  // 交换图层顺序
  const temp = addedLayers.value[layerIndex - 1];
  addedLayers.value[layerIndex - 1] = addedLayers.value[layerIndex];
  addedLayers.value[layerIndex] = temp;
  
  // 更新图层的zIndex
  updateLayerZIndex();
  
  ElMessage.success('图层上移成功');
}

// 下移图层
function moveLayerDown(layerId) {
  const layerIndex = addedLayers.value.findIndex(layer => layer.id === layerId);
  if (layerIndex >= addedLayers.value.length - 1) return;
  
  // 交换图层顺序
  const temp = addedLayers.value[layerIndex + 1];
  addedLayers.value[layerIndex + 1] = addedLayers.value[layerIndex];
  addedLayers.value[layerIndex] = temp;
  
  // 更新图层的zIndex
  updateLayerZIndex();
  
  ElMessage.success('图层下移成功');
}

// 复制图层
function copyLayer(layerId) {
  const layer = addedLayers.value.find(layer => layer.id === layerId);
  if (!layer) return;
  
  try {
    const newLayerId = layerIdCounter.value++;
    let newLayerInstance;
    
    // 根据图层类型创建新实例
    if (layer.type === '瓦片图层') {
      newLayerInstance = createRasterLayer(amap.value, {
        type: 'tile',
        tileUrl: layer.url,
        opacity: layer.opacity,
        zIndex: layer.instance.getOptions().zIndex
      });
    } else if (layer.type === '单张图片') {
      newLayerInstance = createRasterLayer(amap.value, {
        type: 'image',
        url: layer.url,
        bounds: layer.bounds,
        opacity: layer.opacity,
        zIndex: layer.instance.getOptions().zIndex
      });
    } else if (layer.type === '热力图') {
      // 热力图不支持复制
      ElMessage.warning('热力图不支持复制');
      return;
    }
    
    if (newLayerInstance) {
      newLayerInstance.setMap(mapInstance.value);
      
      // 添加到图层列表
      const newLayer = {
        id: newLayerId,
        name: layer.name + ' (副本)',
        type: layer.type,
        url: layer.url,
        opacity: layer.opacity,
        bounds: layer.bounds,
        instance: newLayerInstance,
        visible: layer.visible
      };
      
      addedLayers.value.push(newLayer);
      checkedLayers.value.push(newLayerId);
      
      // 更新zIndex
      updateLayerZIndex();
      
      ElMessage.success('图层复制成功');
    }
  } catch (error) {
    console.error('复制图层失败:', error);
    ElMessage.error('复制图层失败');
  }
}

// 更新图层的zIndex
function updateLayerZIndex() {
  addedLayers.value.forEach((layer, index) => {
    if (layer.instance) {
      try {
        // 根据图层在列表中的位置设置zIndex
        // 列表顶部的图层zIndex更高，显示在更上层
        const zIndex = 100 + (addedLayers.value.length - index);
        layer.instance.setOptions({ zIndex: zIndex });
      } catch (error) {
        console.error('更新图层zIndex失败:', error);
      }
    }
  });
}

// 导出所有图层配置
function exportLayers() {
  if (addedLayers.value.length === 0) {
    ElMessage.warning('暂无图层可导出');
    return;
  }
  
  try {
    // 准备导出的数据，过滤掉实例对象
    const exportData = {
      timestamp: new Date().toISOString(),
      totalLayers: addedLayers.value.length,
      layers: addedLayers.value.map(layer => ({
        id: layer.id,
        name: layer.name,
        type: layer.type,
        url: layer.url,
        opacity: layer.opacity,
        bounds: layer.bounds,
        // 可以根据需要添加更多属性
      }))
    };
    
    // 将数据转换为JSON字符串
    const jsonStr = JSON.stringify(exportData, null, 2);
    
    // 创建下载链接
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `raster_layers_${new Date().getTime()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    ElMessage.success('图层配置导出成功');
  } catch (error) {
    console.error('导出图层配置失败:', error);
    ElMessage.error('导出图层配置失败');
  }
}

// 导出选中图层配置
function exportSelectedLayers() {
  if (checkedLayers.value.length === 0) {
    ElMessage.warning('请先选择要导出的图层');
    return;
  }
  
  try {
    // 过滤出选中的图层
    const selectedLayers = addedLayers.value.filter(layer => 
      checkedLayers.value.includes(layer.id)
    );
    
    // 准备导出的数据，过滤掉实例对象
    const exportData = {
      timestamp: new Date().toISOString(),
      totalLayers: selectedLayers.length,
      layers: selectedLayers.map(layer => ({
        id: layer.id,
        name: layer.name,
        type: layer.type,
        url: layer.url,
        opacity: layer.opacity,
        bounds: layer.bounds,
        // 可以根据需要添加更多属性
      }))
    };
    
    // 将数据转换为JSON字符串
    const jsonStr = JSON.stringify(exportData, null, 2);
    
    // 创建下载链接
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `selected_raster_layers_${new Date().getTime()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    ElMessage.success('选中图层配置导出成功');
  } catch (error) {
    console.error('导出选中图层配置失败:', error);
    ElMessage.error('导出选中图层配置失败');
  }
}

// 导出迁移栅格数据
function exportMigrationRasterData() {
  if (!allMigrations || !allMigrations.value || allMigrations.value.length === 0) {
    ElMessage.warning('暂无迁移数据可导出');
    return;
  }
  
  try {
    // 生成迁移栅格数据
    const rasterData = generateHeatmapData();
    
    if (!rasterData || rasterData.length === 0) {
      ElMessage.warning('没有足够的数据生成迁移栅格');
      return;
    }
    
    // 导出为GeoJSON格式
    exportRasterDataAsGeoJSON(rasterData);
    
    // 导出为CSV格式
    exportRasterDataAsCSV(rasterData);
    
    ElMessage.success('迁移栅格数据导出成功');
  } catch (error) {
    console.error('导出迁移栅格数据失败:', error);
    ElMessage.error('导出迁移栅格数据失败');
  }
}

// 将栅格数据导出为GeoJSON格式
function exportRasterDataAsGeoJSON(rasterData) {
  // 创建GeoJSON对象
  const geojson = {
    type: 'FeatureCollection',
    features: rasterData.map((point, index) => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [point[0], point[1]]
      },
      properties: {
        id: index + 1,
        count: point[2],
        weight: point[2]
      }
    }))
  };
  
  // 将数据转换为JSON字符串
  const jsonStr = JSON.stringify(geojson, null, 2);
  
  // 创建下载链接
  const blob = new Blob([jsonStr], { type: 'application/geo+json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `migration_raster_${new Date().getTime()}.geojson`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// 将栅格数据导出为CSV格式
function exportRasterDataAsCSV(rasterData) {
  // 创建CSV标题行
  const headers = ['id', 'longitude', 'latitude', 'count', 'weight'];
  
  // 创建CSV数据行
  const rows = rasterData.map((point, index) => [
    index + 1,
    point[0],
    point[1],
    point[2],
    point[2]
  ]);
  
  // 组合CSV内容
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');
  
  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `migration_raster_${new Date().getTime()}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// 监听图层选中状态变化
watch(checkedLayers, (newChecked, oldChecked) => {
  // 找出新增的选中项
  const added = newChecked.filter(item => !oldChecked.includes(item));
  added.forEach(layerId => {
    const layer = addedLayers.value.find(l => l.id === layerId);
    if (layer && layer.instance) {
      layer.instance.setMap(mapInstance.value);
      layer.visible = true;
    }
  });
  
  // 找出取消选中的项
  const removed = oldChecked.filter(item => !newChecked.includes(item));
  removed.forEach(layerId => {
    const layer = addedLayers.value.find(l => l.id === layerId);
    if (layer && layer.instance) {
      layer.instance.setMap(null);
      layer.visible = false;
    }
  });
}, { deep: true });

// 渲染定居点
function renderSettlements() {
  if (!amap.value || !mapInstance.value || !locations.value || locations.value.length === 0) {
    return
  }
  
  try {
    // 清除之前的定居点标记
    if (locationMarkers.value.length > 0) {
      removeOverlays(mapInstance.value, locationMarkers.value)
    }
    locationMarkers.value = []
    
    // 创建信息窗体（如果还没有创建）
    if (!infoWindow.value) {
      infoWindow.value = new amap.value.InfoWindow({
        isCustom: false,
        offset: new amap.value.Pixel(0, -30),
        autoMove: true
      })
    }
    
    // 缓存图标，避免重复创建
    const iconCache = new Map()
    const markers = []
    
    // 渲染所有定居点
    locations.value.forEach((location, index) => {
      if (location.longitude && location.latitude) {
        try {
          const isOrigin = location.location_type === 'origin' || location.type === 'origin'
          
          // 缓存图标
          const iconKey = `settlement_${isOrigin ? 'origin' : 'normal'}`
          let icon
          if (iconCache.has(iconKey)) {
            icon = iconCache.get(iconKey)
          } else {
            icon = createSettlementIcon(isOrigin)
            iconCache.set(iconKey, icon)
          }
          
          const marker = new amap.value.Marker({
            position: new amap.value.LngLat(parseFloat(location.longitude), parseFloat(location.latitude)),
            icon: icon,
            zIndex: isOrigin ? 150 : 80, // 起源点的 zIndex 更高
            title: location.historical_name || location.modern_name || '定居点',
            extData: {
              location: location,
              isOrigin: isOrigin
            }
          })
          
          // 添加点击事件 - 显示信息窗体
          marker.on('click', () => {
            if (mapInstance.value) {
              showLocationInfo(marker, location, isOrigin)
            }
          })
          
          locationMarkers.value.push(marker)
          markers.push(marker)
        } catch (markerError) {
          console.error('创建定居点标记失败:', markerError)
        }
      }
    })
    
    // 批量添加标记到地图
    if (markers.length > 0 && showSettlements.value) {
      addOverlays(mapInstance.value, markers)
    }
  } catch (renderError) {
    console.error('渲染定居点失败:', renderError)
  }
}



// 显示定居点信息窗体
function showLocationInfo(marker, location, isOrigin) {
  const historicalName = location.historical_name || location.modern_name || '未知'
  const modernName = location.modern_name && location.historical_name !== location.modern_name 
    ? location.modern_name 
    : ''
  const locationType = location.location_type || location.type || 'settlement'
  const adminRegion = location.admin_region || location.region || ''
  
  // 构建信息窗体内容
  let content = `
    <div style="
      padding: 16px;
      min-width: 260px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
      <div style="
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
        padding-bottom: 12px;
        border-bottom: 2px solid ${isOrigin ? '#FFD700' : '#10B981'};
      ">
        <span style="font-size: 24px;">${isOrigin ? '⭐' : '🏠'}</span>
        <div>
          <h3 style="
            margin: 0;
            font-size: 18px;
            font-weight: 700;
            color: ${isOrigin ? '#F59E0B' : '#059669'};
          ">${isOrigin ? '起源地' : '定居点'}</h3>
          <p style="
            margin: 2px 0 0 0;
            font-size: 11px;
            color: #9CA3AF;
            font-weight: 500;
          ">${isOrigin ? 'Origin Point' : 'Settlement'}</p>
        </div>
      </div>
      
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <div style="display: flex; align-items: flex-start; gap: 8px;">
          <span style="
            font-size: 14px;
            color: #6B7280;
            min-width: 60px;
            font-weight: 600;
          ">地名：</span>
          <span style="
            font-size: 15px;
            color: #1F2937;
            font-weight: 600;
            flex: 1;
          ">${historicalName}</span>
        </div>
        
        ${modernName ? `
        <div style="display: flex; align-items: flex-start; gap: 8px;">
          <span style="
            font-size: 14px;
            color: #6B7280;
            min-width: 60px;
            font-weight: 600;
          ">今名：</span>
          <span style="
            font-size: 14px;
            color: #4B5563;
            font-weight: 500;
            flex: 1;
          ">${modernName}</span>
        </div>
        ` : ''}
        
        ${locationType ? `
        <div style="display: flex; align-items: flex-start; gap: 8px;">
          <span style="
            font-size: 14px;
            color: #6B7280;
            min-width: 60px;
            font-weight: 600;
          ">类型：</span>
          <span style="
            font-size: 14px;
            color: #4B5563;
            padding: 2px 8px;
            background: #F3F4F6;
            border-radius: 4px;
            font-weight: 500;
          ">${getLocationTypeName(locationType)}</span>
        </div>
        ` : ''}
        
        ${adminRegion ? `
        <div style="display: flex; align-items: flex-start; gap: 8px;">
          <span style="
            font-size: 14px;
            color: #6B7280;
            min-width: 60px;
            font-weight: 600;
          ">区域：</span>
          <span style="
            font-size: 14px;
            color: #4B5563;
            font-weight: 500;
            flex: 1;
          ">${adminRegion}</span>
        </div>
        ` : ''}
        
        ${isOrigin ? `
        <div style="
          margin-top: 8px;
          padding: 10px;
          background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
          border-radius: 8px;
          border-left: 3px solid #F59E0B;
        ">
          <p style="
            margin: 0;
            font-size: 13px;
            color: #92400E;
            line-height: 1.6;
            font-weight: 500;
          ">这是姜姓的起源地，是家族历史的开端。</p>
        </div>
        ` : ''}
      </div>
    </div>
  `
  
  // 设置内容并打开信息窗体
  infoWindow.value.setContent(content)
  infoWindow.value.open(mapInstance.value, marker.getPosition())
}

// 将地点类型转换为中文名称
function getLocationTypeName(type) {
  const typeMap = {
    'origin': '起源地',
    'settlement': '定居点',
    'node': '节点',
    'capital': '都城',
    'fortress': '要塞',
    'market': '集市',
    'temple': '寺庙',
    'other': '其他'
  };
  return typeMap[type] || typeMap[type.toLowerCase()] || type || '定居点';
}

// 绘制星形
function drawStar(ctx, x, y, radius, points) {
  ctx.beginPath()
  for (let i = 0; i < points * 2; i++) {
    const angle = (i * Math.PI) / points
    const r = i % 2 === 0 ? radius : radius / 2
    const px = x + Math.cos(angle) * r
    const py = y + Math.sin(angle) * r
    if (i === 0) {
      ctx.moveTo(px, py)
    } else {
      ctx.lineTo(px, py)
    }
  }
  ctx.closePath()
}

// 计算两点之间的距离（单位：公里）
function calculateDistance(point1, point2) {
  const R = 6371; // 地球半径（公里）
  const dLat = (point2[1] - point1[1]) * Math.PI / 180;
  const dLon = (point2[0] - point1[0]) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(point1[1] * Math.PI / 180) * Math.cos(point2[1] * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  return R * c; // 距离（公里）
}

// 计算路线总长度
function calculateRouteLength(coordinates) {
  let totalDistance = 0;
  for (let i = 1; i < coordinates.length; i++) {
    totalDistance += calculateDistance(coordinates[i-1], coordinates[i]);
  }
  return totalDistance;
}

// 计算路线方向
function calculateDirection(start, end) {
  const deltaX = end[0] - start[0];
  const deltaY = end[1] - start[1];
  
  // 计算角度（弧度转角度）
  let angle = Math.atan2(deltaY, deltaX) * 180 / Math.PI;
  
  // 转换为0-360度范围
  if (angle < 0) angle += 360;
  
  // 根据角度返回方向
  if (angle >= 337.5 || angle < 22.5) return '东';
  if (angle >= 22.5 && angle < 67.5) return '东北';
  if (angle >= 67.5 && angle < 112.5) return '北';
  if (angle >= 112.5 && angle < 157.5) return '西北';
  if (angle >= 157.5 && angle < 202.5) return '西';
  if (angle >= 202.5 && angle < 247.5) return '西南';
  if (angle >= 247.5 && angle < 292.5) return '南';
  if (angle >= 292.5 && angle < 337.5) return '东南';
  
  return '未知';
}

// 获取路线信息用于对比
function getRouteInfo(migration) {
  const coords = migration.geometry.coordinates;
  const start = coords[0];
  const end = coords[coords.length - 1];
  
  return {
    id: migration.properties.migration_id,
    branch: migration.properties.branch_name || migration.properties.surname || '未知',
    from: migration.properties.from_name || '未知',
    to: migration.properties.to_name || '未知',
    reason: migration.properties.migration_reason || migration.properties.reason || '未知',
    year: getMigrationYear(migration),
    length: calculateRouteLength(coords).toFixed(2),
    direction: calculateDirection(start, end),
    startCoordinate: start,
    endCoordinate: end,
    numWaypoints: coords.length - 2 // 减去起点和终点
  };
}
</script>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #f5f3e7;
  display: flex;
  flex-direction: column;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 12px 22px;
  background: linear-gradient(135deg, #ffffff 0%, #f3f6fc 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  z-index: 200;
}

.topbar .search-container.top-search {
  position: relative;
  top: auto;
  left: auto;
  flex: 0 1 480px;
  margin-left: 32px;
  margin-right: 16px;
  display: flex;
  justify-content: center;
  max-width: 520px;
  order: 1;
}

@media (max-width: 1024px) {
  .topbar .search-container.top-search {
    flex: 1 1 auto;
    margin: 0 16px;
    max-width: 420px;
  }
}

@media (max-width: 768px) {
  .topbar .search-container.top-search {
    width: calc(100vw - 40px);
  }
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

.brand-text small {
  color: #6b7280;
}

.view-switch {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-left: auto;
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

/* 分析按钮特殊样式 */
.analytics-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.analytics-button:hover {
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.5),
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


.map-view {
  flex: 1;
  position: relative;
  min-height: 0;
}

/* 背景图片容器 */
.background-container {
  position: relative;
  width: 100%;
  height: calc(100vh - 72px);
  margin-top: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.9;
  z-index: 1;
}

/* 地图框架 */
.map-frame {
  position: relative;
  z-index: 2;
  width: 85%;
  max-width: 1800px;
  height: 90%;
  max-height: 900px;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 
    0 12px 40px rgba(0, 0, 0, 0.4),
    inset 0 2px 12px rgba(0, 0, 0, 0.1),
    inset 0 -2px 8px rgba(0, 0, 0, 0.05);
  border: 4px solid #8b7355;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(3px);
  transition: all 0.3s ease;
}

.map-frame:hover {
  box-shadow: 
    0 16px 48px rgba(0, 0, 0, 0.5),
    inset 0 2px 12px rgba(0, 0, 0, 0.1),
    inset 0 -2px 8px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.map-frame::before {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  background: linear-gradient(135deg, 
    rgba(139, 115, 85, 0.9) 0%, 
    rgba(101, 67, 33, 0.9) 50%, 
    rgba(139, 115, 85, 0.9) 100%);
  border-radius: 12px;
  z-index: -1;
  box-shadow: 
    inset 0 2px 6px rgba(255, 255, 255, 0.4),
    inset 0 -2px 6px rgba(0, 0, 0, 0.3),
    0 4px 12px rgba(0, 0, 0, 0.2);
}

.map-frame::after {
  content: '';
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  bottom: 8px;
  border: 1px solid rgba(139, 115, 85, 0.2);
  border-radius: 4px;
  pointer-events: none;
}

.map-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 
    inset 0 2px 8px rgba(0, 0, 0, 0.1),
    0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(139, 115, 85, 0.3);
}

.info-card {
  position: absolute;
  top: 20px;
  right: 30px;
  z-index: 100;
  width: 400px;
  max-width: calc(100vw - 750px);
  max-height: calc(100vh - 40px);
  overflow: hidden;
}

.card-wrapper {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 20px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-wrapper:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 25px 70px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
}

/* 卡片头部 */
.card-header {
  position: relative;
  padding: 0;
  overflow: hidden;
}

.header-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  opacity: 0.95;
  background-size: 200% 200%;
  animation: gradientShift 8s ease infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.header-content {
  position: relative;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon-wrapper {
  width: 52px;
  height: 52px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.3) inset;
  transition: all 0.3s ease;
}

.title-icon-wrapper:hover {
  transform: rotate(5deg) scale(1.05);
  background: rgba(255, 255, 255, 0.35);
}

.title-icon {
  font-size: 24px;
}

.title-text h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
}

.title-subtitle {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.close-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  border: none;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.15) rotate(90deg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.close-icon {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  line-height: 1;
}

/* 卡片内容 */
.card-body {
  flex: 1;
  overflow-y: auto;
  padding: 28px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
  position: relative;
}

.migration-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  gap: 16px;
  padding: 18px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.info-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.info-item:hover::before {
  opacity: 1;
}

.info-item:hover {
  background: linear-gradient(135deg, #ffffff 0%, #f0f2f5 100%);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
}

.info-item.highlight-item {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-color: rgba(102, 126, 234, 0.3);
}

.info-item.route-item {
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.1), rgba(80, 200, 120, 0.1));
}

.info-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.3) inset;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.info-icon-wrapper::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.3s ease, height 0.3s ease;
}

.info-item:hover .info-icon-wrapper::before {
  width: 100%;
  height: 100%;
}

.info-item:hover .info-icon-wrapper {
  transform: rotate(5deg) scale(1.1);
  box-shadow: 
    0 6px 16px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.4) inset;
}

.info-icon-wrapper.branch-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.info-icon-wrapper.time-icon {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.info-icon-wrapper.location-icon {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.info-icon-wrapper.reason-icon {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}

.info-icon-wrapper.person-icon {
  background: linear-gradient(135deg, #fa709a, #fee140);
}

.info-icon-wrapper.description-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.info-icon-wrapper.origin-icon {
  background: linear-gradient(135deg, #8B4513, #A0522D);
}

.info-icon-wrapper.ancestor-icon {
  background: linear-gradient(135deg, #FFD700, #FFA500);
}

.info-icon-wrapper.source-icon {
  background: linear-gradient(135deg, #6c757d, #495057);
}

.info-icon {
  font-size: 24px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 15px;
  color: #2c3e50;
  font-weight: 600;
  line-height: 1.5;
}

.highlight-value {
  font-size: 18px;
  color: #667eea;
  font-weight: 700;
}

.reason-text {
  color: #555;
  font-weight: 500;
  line-height: 1.6;
}

/* 详细描述样式 */
.info-item.description-item {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-color: rgba(102, 126, 234, 0.2);
}

.description-content {
  margin-top: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  border-left: 3px solid rgba(102, 126, 234, 0.3);
}

.description-text {
  margin: 0;
  font-size: 14px;
  color: #555;
  font-weight: 400;
  line-height: 1.8;
  text-align: justify;
  white-space: pre-wrap;
  word-wrap: break-word;
  text-indent: 2em;
  position: relative;
}

.description-text::first-letter {
  font-size: 1.3em;
  font-weight: 700;
  color: #667eea;
  float: left;
  line-height: 1;
  margin-right: 4px;
  margin-top: 2px;
}

.source-text {
  color: #6c757d;
  font-weight: 500;
  line-height: 1.6;
  font-size: 13px;
}

.info-item.source-item {
  background: linear-gradient(135deg, rgba(108, 117, 125, 0.05), rgba(73, 80, 87, 0.05));
  border-color: rgba(108, 117, 125, 0.2);
}

/* 路线显示 */
.route-path {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.route-start,
.route-end {
  flex: 1;
  padding: 10px 14px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  box-shadow: 
    0 2px 6px rgba(0, 0, 0, 0.08),
    inset 0 1px 2px rgba(255, 255, 255, 0.8);
  text-align: center;
  transition: all 0.3s ease;
}

.route-start:hover,
.route-end:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 4px 10px rgba(0, 0, 0, 0.12),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.route-start {
  border-left: 4px solid #4facfe;
  position: relative;
}

.route-start::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #4facfe, #00f2fe);
  border-radius: 2px 0 0 2px;
}

.route-end {
  border-right: 4px solid #00f2fe;
  position: relative;
}

.route-end::before {
  content: '';
  position: absolute;
  right: -4px;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #00f2fe, #4facfe);
  border-radius: 0 2px 2px 0;
}

.route-arrow {
  width: 24px;
  height: 24px;
  color: #667eea;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.route-arrow svg {
  width: 100%;
  height: 100%;
}

/* 途径地样式 */
.waypoints-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(102, 126, 234, 0.2);
}

.waypoints-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 600;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.waypoints-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.waypoint-tag {
  display: inline-block;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #667eea;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.waypoint-tag:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.15);
}

.comparison-card {
  position: absolute;
  top: 20px;
  right: 450px;
  z-index: 100;
  width: 350px;
  max-width: calc(100vw - 750px);
  max-height: calc(100vh - 40px);
  overflow: hidden;
}

.comparison-card .card-wrapper {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  box-shadow: 
    0 16px 48px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.comparison-card .card-wrapper:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 20px 56px rgba(0, 0, 0, 0.16),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
}

.divider {
  display: flex;
  align-items: center;
  margin: 16px 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
}

.divider-text {
  padding: 0 12px;
  color: #667eea;
  font-weight: 700;
  font-size: 14px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
}

.comparison-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 3px 0;
  border-bottom: 1px dashed rgba(102, 126, 234, 0.1);
}

.detail-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 600;
}

.detail-value {
  font-size: 12px;
  color: #2c3e50;
  font-weight: 500;
  text-align: right;
  flex: 1;
  margin-left: 6px;
}

.summary-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 6px;
  padding: 6px;
}

.summary-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 600;
}

.summary-value {
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
  text-align: right;
  flex: 1;
  margin-left: 6px;
}

.cancel-button-container {
  display: flex;
  justify-content: center;
  padding: 12px;
  margin-top: 8px;
  border-top: 1px solid rgba(102, 126, 234, 0.2);
}

.cancel-comparison-btn {
  width: 100%;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  border: none;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
}

.cancel-comparison-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
}

.legend {
  position: absolute;
  bottom: 30px;
  right: 30px;
  z-index: 100;
  max-width: 280px;
}

.legend-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 12px;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.legend-card:hover {
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.18),
    0 0 0 1px rgba(102, 126, 234, 0.2) inset;
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.3);
}

.legend-title {
  font-size: 14px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #555;
  font-weight: 500;
  transition: all 0.2s ease;
  padding: 2px 0;
}

.legend-item:hover {
  color: #667eea;
  transform: translateX(3px);
}

/* 图例标记样式 - 与地图标记一致 */
.legend-marker {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
  position: relative;
  flex-shrink: 0;
}

.legend-item:hover .legend-marker {
  transform: scale(1.15);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

/* 地图样式选择器样式 */
.map-style-selector {
  position: absolute;
  bottom: 30px;
  left: 30px;
  z-index: 100;
}

.style-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 200px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.style-card:hover {
  box-shadow: 
    0 6px 24px rgba(102, 126, 234, 0.2),
    0 0 0 1px rgba(102, 126, 234, 0.2) inset;
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.3);
}

.style-title {
  font-size: 15px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.style-select {
  width: 100%;
}

.style-select :deep(.el-input__wrapper) {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.06),
    inset 0 1px 2px rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  padding: 8px 12px;
}

.style-select :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.15),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.style-select :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 
    0 4px 16px rgba(102, 126, 234, 0.25),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.filter-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-card:hover {
  box-shadow: 
    0 6px 24px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
  transform: translateY(-2px);
}

.filter-title {
  font-size: 15px;
  font-weight: 700;
  color: #4a148c; /* 深紫色，提高可读性 */
  margin-bottom: 12px;
  letter-spacing: 0.5px;
}

.filter-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.filter-checkbox:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  transform: translateX(4px);
}

/* 筛选面板样式 */
.map-filter-panel {
  position: absolute;
  top: 100px;
  left: 30px;
  z-index: 100;
  width: 320px;
  max-width: calc(100vw - 60px);
  max-height: calc(100vh - 200px);
}

.filter-panel-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.filter-panel-card:hover {
  box-shadow: 
    0 12px 40px rgba(102, 126, 234, 0.2),
    0 0 0 1px rgba(102, 126, 234, 0.2) inset;
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.3);
}

.filter-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.filter-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #2c3e50;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.filter-icon {
  font-size: 18px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.reset-btn {
  color: #667eea;
  font-weight: 600;
  padding: 4px 12px;
  transition: all 0.2s ease;
}

.reset-btn:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.1);
  color: #5568d3;
}

.reset-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.filter-panel-content {
  padding: 16px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #4B5563;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.filter-select,
.filter-input {
  width: 100%;
}

.filter-select :deep(.el-input__wrapper),
.filter-input :deep(.el-input__wrapper) {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.06),
    inset 0 1px 2px rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.filter-select :deep(.el-input__wrapper:hover),
.filter-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.15),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.filter-select :deep(.el-input__wrapper.is-focus),
.filter-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 
    0 4px 16px rgba(102, 126, 234, 0.25),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.year-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.year-input {
  flex: 1;
}

.year-input :deep(.el-input__wrapper) {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.06),
    inset 0 1px 2px rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.year-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.15),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.year-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 
    0 4px 16px rgba(102, 126, 234, 0.25),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.year-separator {
  font-size: 13px;
  color: #6B7280;
  font-weight: 500;
  white-space: nowrap;
}

.input-icon {
  font-size: 14px;
  color: #9CA3AF;
}

.filter-stats {
  margin-top: 8px;
  padding: 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.stats-label {
  color: #6B7280;
  font-weight: 600;
}

.stats-value {
  color: #667eea;
  font-weight: 700;
  font-size: 16px;
}

.stats-total {
  color: #9CA3AF;
  font-size: 12px;
}

/* 筛选面板滚动条样式 */
.filter-panel-content::-webkit-scrollbar {
  width: 6px;
}

.filter-panel-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.filter-panel-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 3px;
}

.filter-panel-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5568d3, #653a8f);
}

/* 起源点标记 - 金色星形 */
.origin-marker {
  background: #FFD700;
  border-color: #FFA500;
  width: 20px;
  height: 20px;
  box-shadow: 0 0 8px rgba(255, 215, 0, 0.5);
}

.origin-marker::before {
  content: '★';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-size: 10px;
  line-height: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 定居点标记 - 绿色房子 */
.settlement-marker {
  background: #10B981;
  border-color: #059669;
  width: 18px;
  height: 18px;
}

.settlement-marker::before {
  content: '🏠';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 10px;
  line-height: 1;
}

/* 起点标记 - 圆形内部实心圆 */
.start-marker {
  background: #FF6B6B;
}

.start-marker::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 4px;
  height: 4px;
  background: #fff;
  border-radius: 50%;
}

/* 终点标记 - 星形 */
.end-marker {
  background: #4ECDC4;
  position: relative;
}

.end-marker::before {
  content: '★';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-size: 10px;
  line-height: 1;
}

/* 途径地标记 - 菱形 */
.waypoint-marker {
  background: #FFBE0B;
  transform: rotate(45deg);
  width: 16px;
  height: 16px;
  border-radius: 2px;
}

.legend-item:hover .waypoint-marker {
  transform: rotate(45deg) scale(1.15);
}

.legend-line {
  width: 24px;
  height: 3px;
  background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
  border-radius: 2px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}

.legend-item:hover .legend-line {
  width: 28px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 200;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.loading-text {
  color: #ffffff;
  font-size: 16px;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-overlay {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  display: flex;
  justify-content: center;
}

.error-alert {
  min-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
}


/* 滚动条样式 */
.card-body::-webkit-scrollbar {
  width: 6px;
}

.card-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.card-body::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 3px;
}

.card-body::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5568d3, #653a8f);
}

/* 搜索框样式 */
.search-container {
  position: absolute;
  top: 5px;
  left: 370px;
  z-index: 100;
  width: 380px;
  max-width: calc(100vw - 400px);
}

.top-search {
  position: static;
  margin: 0 20px;
  width: 380px;
  max-width: 400px;
  order: 1;
}

.top-search .search-wrapper {
  width: 100%;
}

.top-search .search-input :deep(.el-input__wrapper) {
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.96) 0%, rgba(255, 255, 255, 0.98) 100%);
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 
    inset 0 1px 1px rgba(255, 255, 255, 0.9),
    0 1px 3px rgba(15, 23, 42, 0.12);
  padding: 8px 18px;
}

.top-search .search-input :deep(.el-input__wrapper:hover) {
  background: linear-gradient(135deg, rgba(248, 250, 252, 1) 0%, rgba(255, 255, 255, 1) 100%);
  border-color: rgba(129, 140, 248, 0.6);
  box-shadow: 
    inset 0 1px 2px rgba(255, 255, 255, 1),
    0 3px 10px rgba(129, 140, 248, 0.3);
}

.top-search .search-input :deep(.el-input__wrapper.is-focus) {
  background: linear-gradient(135deg, rgba(239, 246, 255, 1) 0%, rgba(255, 255, 255, 1) 100%);
  border-color: #6366f1;
  box-shadow: 
    inset 0 1px 2px rgba(255, 255, 255, 1),
    0 4px 14px rgba(79, 70, 229, 0.4);
  transform: translateY(-0.5px);
}

@media (max-width: 768px) {
  .top-search {
    position: absolute;
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
    width: calc(100vw - 40px);
    max-width: 500px;
    margin: 0;
  }
}

.search-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-card:hover {
  box-shadow: 
    0 12px 40px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
  transform: translateY(-2px);
}

.search-wrapper {
  padding: 16px;
}

.search-input {
  width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 12px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.06),
    inset 0 1px 2px rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  padding: 12px 16px;
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.15),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 
    0 4px 16px rgba(102, 126, 234, 0.25),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.search-input :deep(.el-input__inner) {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 500;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: #95a5a6;
}

.search-icon {
  font-size: 18px;
  margin-right: 8px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.search-results {
  margin-top: 12px;
  padding: 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.results-count {
  font-size: 13px;
  color: #667eea;
  font-weight: 600;
  text-align: center;
  padding: 4px 0;
}

/* 时间轴遮罩层 */
.timeline-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  z-index: 145;
}

/* 时间轴容器 */
.timeline-container {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 420px;
  max-width: 90vw;
  z-index: 150;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  box-shadow: 
    4px 0 24px rgba(0, 0, 0, 0.15),
    inset 1px 0 0 rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.timeline-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* 时间轴头部 */
.timeline-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.timeline-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), transparent);
  pointer-events: none;
}

.timeline-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.timeline-title-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.timeline-icon-wrapper {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.timeline-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.timeline-title-text h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
}

.timeline-subtitle {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.timeline-close-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.timeline-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.close-icon {
  font-size: 18px;
  font-weight: 600;
  line-height: 1;
}

/* 时间轴内容 */
.timeline-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
}

.timeline-empty {
  text-align: center;
  color: #95a5a6;
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.5;
}

.timeline-empty p {
  margin: 0;
  font-size: 14px;
}

.timeline-wrapper {
  position: relative;
  padding-left: 40px;
}

.timeline-item {
  position: relative;
  padding-bottom: 28px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.timeline-item:hover {
  transform: translateX(6px);
}

.timeline-item.active {
  transform: translateX(6px);
}

.timeline-item.active .timeline-dot {
  background: linear-gradient(135deg, #667eea, #764ba2);
  transform: scale(1.4);
  box-shadow: 
    0 0 0 6px rgba(102, 126, 234, 0.2),
    0 4px 16px rgba(102, 126, 234, 0.3);
}

.timeline-item.active .timeline-dot-ring {
  opacity: 1;
  transform: scale(1.8);
}

.timeline-dot-wrapper {
  position: absolute;
  left: -33px;
  top: 12px;
  z-index: 2;
}

.timeline-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #cbd5e0;
  border: 4px solid #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.timeline-dot-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(1);
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(102, 126, 234, 0.4);
  opacity: 0;
  transition: all 0.3s ease;
}

.timeline-line {
  position: absolute;
  left: -25px;
  top: 28px;
  width: 3px;
  height: calc(100% - 12px);
  background: linear-gradient(180deg, 
    rgba(102, 126, 234, 0.2) 0%, 
    rgba(118, 75, 162, 0.1) 50%,
    rgba(203, 213, 224, 0.3) 100%);
  border-radius: 2px;
  z-index: 1;
}

.timeline-content-wrapper {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 14px;
  padding: 18px;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.timeline-content-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.timeline-item:hover .timeline-content-wrapper::before,
.timeline-item.active .timeline-content-wrapper::before {
  opacity: 1;
}

.timeline-item:hover .timeline-content-wrapper,
.timeline-item.active .timeline-content-wrapper {
  background: linear-gradient(135deg, #ffffff 0%, #f0f2f5 100%);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
  transform: translateY(-3px);
}

.timeline-year-badge {
  display: inline-block;
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 6px 14px;
  border-radius: 20px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  letter-spacing: 0.5px;
}

.timeline-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.timeline-branch {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.branch-icon {
  font-size: 18px;
}

.timeline-route {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  flex-wrap: wrap;
}

.route-from,
.route-to {
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-radius: 8px;
  font-weight: 500;
  color: #555;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s ease;
}

.timeline-item:hover .route-from,
.timeline-item:hover .route-to {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-1px);
}

.route-arrow-wrapper {
  width: 20px;
  height: 20px;
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.route-arrow-wrapper svg {
  width: 100%;
  height: 100%;
}

.timeline-reason {
  font-size: 12px;
  color: #7f8c8d;
  line-height: 1.6;
  margin-top: 4px;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.reason-icon {
  font-size: 14px;
  flex-shrink: 0;
  margin-top: 2px;
}

/* 时间轴开关样式 */
.timeline-toggle {
  position: fixed;
  left: 380px;
  bottom: 30px;
  z-index: 140;
}

.timeline-switch {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  padding: 12px 20px;
  border-radius: 50px;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
}

.timeline-switch:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
}

.timeline-switch.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(255, 255, 255, 0.3);
}

.timeline-switch.active .switch-label {
  color: #ffffff;
}

.switch-handle {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.4),
    inset 0 1px 2px rgba(255, 255, 255, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.switch-handle::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.3s ease, height 0.3s ease;
}

.timeline-switch:hover .switch-handle::before {
  width: 100%;
  height: 100%;
}

.timeline-switch.active .switch-handle {
  background: linear-gradient(135deg, #ffffff, #f0f2f5);
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.2),
    inset 0 1px 2px rgba(0, 0, 0, 0.1);
}

.switch-icon {
  font-size: 20px;
  color: #ffffff;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.timeline-switch.active .switch-icon {
  color: #667eea;
  transform: rotate(90deg);
}

.switch-label {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  transition: color 0.3s ease;
  white-space: nowrap;
}

/* 时间轴滚动条样式 */
.timeline-content::-webkit-scrollbar {
  width: 6px;
}

.timeline-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.timeline-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 3px;
}

.timeline-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5568d3, #653a8f);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .map-filter-panel {
    width: 280px;
    max-height: calc(100vh - 180px);
  }
  
  .search-container {
    left: 320px;
    width: 320px;
  }
  
  .info-card {
    width: 350px;
    max-width: calc(100vw - 680px);
  }

  .timeline-toggle {
    left: 340px;
  }
}

@media (max-width: 1200px) {
  .map-filter-panel {
    width: 260px;
    top: 80px;
  }
  
  .search-container {
    left: 300px;
    width: 300px;
  }
  
  .info-card {
    width: 320px;
    max-width: calc(100vw - 640px);
  }
  
  .timeline-toggle {
    left: 320px;
  }
}

@media (max-width: 1024px) {
  .map-filter-panel {
    width: 240px;
    top: 70px;
    max-height: calc(100vh - 160px);
  }
  
  .search-container {
    left: 280px;
    width: 280px;
  }
  
  .info-card {
    width: 300px;
    max-width: calc(100vw - 580px);
  }
  
  .timeline-toggle {
    left: 300px;
  }
  
  .legend {
    max-width: calc(100vw - 580px);
  }
  
  .comparison-card {
    width: 300px;
    right: 380px;
  }
}

@media (max-width: 768px) {
  .map-filter-panel {
    position: fixed;
    top: 80px;
    left: 10px;
    width: calc(100vw - 20px);
    max-width: 300px;
    max-height: calc(100vh - 100px);
    z-index: 200;
  }
  
  .search-container {
    position: fixed;
    top: 10px;
    left: 10px;
    right: 10px;
    width: auto;
    max-width: none;
    z-index: 200;
  }
  
  .info-card {
    position: fixed;
    top: 70px;
    right: 10px;
    left: 10px;
    width: auto;
    max-width: none;
    max-height: calc(100vh - 90px);
    z-index: 200;
  }
  
  .legend {
    position: fixed;
    bottom: 160px;
    right: 10px;
    left: auto;
    max-width: 220px;
    z-index: 200;
  }
  
  .legend-card {
    padding: 10px;
  }

  .style-buttons {
    display: flex;
    gap: 6px;
    justify-content: center;
    flex-wrap: wrap;
    padding: 6px;
  }
  
  .timeline-container {
    width: 100%;
    max-width: 100vw;
    left: 0;
    right: 0;
  }
  
  .timeline-toggle {
    position: fixed;
    left: 10px;
    bottom: 80px;
    z-index: 200;
  }
  
  .timeline-switch {
    padding: 10px 16px;
  }
  
  .switch-handle {
    width: 40px;
    height: 40px;
  }
  
  .switch-label {
    font-size: 13px;
  }
  
  .timeline-header {
    padding: 20px;
  }
  
  .timeline-icon-wrapper {
    width: 48px;
    height: 48px;
  }
  
  .timeline-content {
    padding: 20px;
  }
  
  .timeline-wrapper {
    padding-left: 32px;
  }
  
  .timeline-dot-wrapper {
    left: -25px;
  }
  
  .filter-panel-content {
    max-height: calc(100vh - 200px);
  }
  
  .comparison-card {
    position: fixed;
    top: 70px;
    right: 10px;
    left: 10px;
    width: auto;
    max-width: none;
    max-height: calc(100vh - 160px);
    z-index: 200;
  }
  
  .cancel-button-container {
    padding: 10px;
    margin-top: 6px;
  }
}

/* 筛选面板切换开关 */
.filter-toggle {
  position: absolute;
  top: 150px;
  left: 20px;
  z-index: 300;
}

.filter-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9);
}

.filter-switch:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: rgba(102, 126, 234, 0.6);
}

.filter-switch.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(102, 126, 234, 0.5);
}

.filter-switch.active .switch-handle {
  background: rgba(255, 255, 255, 0.2);
}

.filter-switch.active .switch-icon {
  color: white;
}

.filter-switch.active .switch-label {
  color: white;
}

.switch-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 50%;
  transition: all 0.3s ease;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.switch-icon {
  font-size: 16px;
  transition: all 0.3s ease;
  color: #4B5563;
}

.switch-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  transition: all 0.3s ease;
}

/* 筛选面板遮罩层 */
.filter-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 400;
  animation: fadeIn 0.3s ease;
}

/* 筛选面板容器 */
.filter-container {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 420px;
  max-width: calc(100vw - 40px);
  z-index: 500;
  display: flex;
  flex-direction: column;
  background: transparent;
}

/* 筛选卡片 */
.filter-card {
  flex: 1;
  margin: 20px 20px 20px 0;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
}

/* 筛选头部 */
.filter-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  position: relative;
}

.filter-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
}

.filter-title-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.filter-icon {
  font-size: 24px;
}

.filter-title-text h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.filter-title-text p {
  margin: 0;
  font-size: 12px;
  opacity: 0.8;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.filter-close-btn {
  width: 40px;
  height: 40px;
  min-height: 40px;
  padding: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s ease;
}

.filter-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.close-icon {
  font-size: 18px;
}

/* 筛选内容 */
.filter-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.filter-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 地图样式面板切换开关 */
.style-toggle {
  position: absolute;
  top: 80px;
  left: 20px;
  z-index: 300;
}

.style-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9);
}

.style-switch:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: rgba(102, 126, 234, 0.6);
}

.style-switch.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(102, 126, 234, 0.5);
}

.style-switch.active .switch-handle {
  background: rgba(255, 255, 255, 0.2);
}

.style-switch.active .switch-icon {
  color: white;
}

.style-switch.active .switch-label {
  color: white;
}

/* 地图样式面板遮罩层 */
.style-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 400;
  animation: fadeIn 0.3s ease;
}

/* 地图样式面板容器 */
.style-container {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 420px;
  max-width: calc(100vw - 40px);
  z-index: 500;
  display: flex;
  flex-direction: column;
  background: transparent;
}

/* 地图样式卡片 */
.style-card {
  flex: 1;
  margin: 20px 20px 20px 0;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
}

/* 地图样式头部 */
.style-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  position: relative;
}

.style-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
}

.style-title-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.style-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.style-icon {
  font-size: 24px;
}

.style-title-text h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.style-title-text p {
  margin: 0;
  font-size: 12px;
  opacity: 0.8;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.style-close-btn {
  width: 40px;
  height: 40px;
  min-height: 40px;
  padding: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s ease;
}

.style-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* 地图样式内容 */
.style-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.style-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.style-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 10px;
}

.style-option-btn {
  width: 100%;
  justify-content: flex-start;
  gap: 12px;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s ease;
}

/* 缩放控制按钮样式 */
.zoom-controls {
  position: absolute;
  right: 30px;
  top: 100px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.fullscreen-control {
  position: absolute;
  right: 30px;
  top: 260px;
  z-index: 100;
}

.fullscreen-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.3);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.fullscreen-btn:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(102, 126, 234, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.fullscreen-icon {
  font-size: 18px;
  font-weight: bold;
  color: #4B5563;
}

.fullscreen-btn:hover .fullscreen-icon {
  color: white;
}

.animation-control {
  position: absolute;
  right: 30px;
  top: 320px;
  z-index: 100;
}

.animation-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.3);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.animation-btn:hover {
  background: linear-gradient(135deg, #4ecdc4 0%, #55a630 100%);
  border-color: rgba(78, 205, 196, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.animation-icon {
  font-size: 16px;
  font-weight: bold;
  color: #4B5563;
}

.animation-btn:hover .animation-icon {
  color: white;
}

.zoom-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.3);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.zoom-btn:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(102, 126, 234, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.zoom-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.zoom-icon {
  font-size: 20px;
  font-weight: bold;
  color: #4B5563;
}

.zoom-in-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(102, 126, 234, 0.5);
}

.zoom-in-btn:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.zoom-in-btn .zoom-icon {
  color: white;
}

.zoom-out-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-color: rgba(245, 87, 108, 0.5);
}

.zoom-out-btn:hover {
  background: linear-gradient(135deg, #e083eb 0%, #e5475c 100%);
}

.zoom-out-btn .zoom-icon {
  color: white;
}

.reset-zoom-btn {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: rgba(79, 172, 254, 0.5);
}

.reset-zoom-btn:hover {
  background: linear-gradient(135deg, #3eadfd 0%, #00d2e0 100%);
}

.reset-zoom-btn .zoom-icon {
  color: white;
}

/* 行政区统计按钮样式 */
.district-statistics-control {
  position: absolute;
  right: 30px;
  top: 380px;
  z-index: 100;
}

.district-statistics-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(255, 165, 0, 0.5); /* 橙色边框 */
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.district-statistics-btn:hover {
  background: linear-gradient(135deg, #ffa500 0%, #ff8c00 100%); /* 橙色渐变 */
  border-color: rgba(255, 165, 0, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 165, 0, 0.4);
}

.district-statistics-icon {
  font-size: 18px;
  font-weight: bold;
  color: #4B5563;
}

.district-statistics-btn:hover .district-statistics-icon {
  color: white;
}

/* 栅格图层控制按钮样式 */
.raster-layer-control {
  position: absolute;
  right: 30px;
  top: 440px;
  z-index: 100;
}

.raster-layer-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.5); /* 紫色边框 */
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.raster-layer-btn:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* 紫色渐变 */
  border-color: rgba(102, 126, 234, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.raster-layer-icon {
  font-size: 18px;
  font-weight: bold;
  color: #4B5563;
}

.raster-layer-btn:hover .raster-layer-icon {
  color: white;
}

.raster-layer-btn.is-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(102, 126, 234, 0.8);
}

.raster-layer-btn.is-primary .raster-layer-icon {
  color: white;
}

/* 栅格图层面板样式 */
.raster-layer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.raster-layer-container {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  z-index: 1000;
  background: #ffffff;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.raster-layer-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.raster-layer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.raster-layer-header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.raster-layer-title-wrapper {
  display: flex;
  flex-direction: column;
}

.raster-layer-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.raster-layer-subtitle {
  margin: 0;
  font-size: 12px;
  opacity: 0.9;
}

.raster-layer-icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
  padding: 8px;
  border-radius: 8px;
}

.raster-layer-close-btn {
  color: white;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.raster-layer-close-btn:hover {
  opacity: 1;
}

.raster-layer-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.raster-layer-type-selector {
  margin-bottom: 20px;
}

.raster-layer-config {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.raster-layer-config h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.raster-layer-config .el-input {
  margin-bottom: 12px;
}

.raster-layer-config .el-slider {
  margin-bottom: 16px;
}

.raster-layer-list {
  margin-top: 20px;
}

.raster-layer-list h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.layer-item {
  margin-bottom: 10px;
}

.layer-checkbox {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: white;
}

.layer-checkbox:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.layer-item-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.layer-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.layer-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.layer-type {
  font-size: 12px;
  color: #666;
}

.layer-opacity-control {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 5px 0;
}

.opacity-value {
  font-size: 12px;
  color: #666;
  width: 40px;
  text-align: right;
}

.layer-actions {
  display: flex;
  gap: 5px;
  margin-top: 5px;
}

.layer-action-btn {
  padding: 4px;
  min-width: auto;
}

.layer-action-btn:hover {
  background-color: rgba(102, 126, 234, 0.1);
}

.layer-action-btn.remove-btn:hover {
  background-color: rgba(255, 77, 79, 0.1);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(100%);
}

/* 行政区统计弹窗样式 */
.district-stats-container {
  padding: 10px;
}

.stats-overview {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 120px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.locations-list {
  margin-top: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.empty-hint {
  text-align: center;
  padding: 20px;
  color: #999;
  font-style: italic;
}

/* 省份选择器样式 */
.province-selector {
  padding: 10px 0;
}
</style>
