<template>
  <div class="admin-page">
    <!-- 顶部导航栏 -->
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

    <!-- 主要内容区 -->
    <div class="admin-content">
      <!-- 侧边栏 -->
      <div class="admin-sidebar">
        <el-menu
          :default-active="activeMenu"
          @select="handleMenuSelect"
          class="admin-menu"
        >
          <el-menu-item index="dashboard">
            <span>📊 数据概览</span>
          </el-menu-item>
          <el-menu-item index="branches">
            <span>🏯 家族分支管理</span>
          </el-menu-item>
          <el-menu-item index="locations">
            <span>📍 地点管理</span>
          </el-menu-item>
          <el-menu-item index="migrations">
            <span>🗺️ 迁徙记录管理</span>
          </el-menu-item>
          <el-menu-item index="submissions">
            <span>📝 提交审核</span>
          </el-menu-item>
          <el-menu-item index="users">
            <span>👥 用户管理</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容区 -->
      <div class="admin-main">
        <!-- 数据概览 -->
        <div v-if="activeMenu === 'dashboard'" class="dashboard">
          <div class="page-header">
            <h2>📊 数据概览</h2>
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

        <!-- 用户管理 -->
        <div v-else-if="activeMenu === 'users'" class="user-management">
          <div class="page-header">
            <h2>👥 用户管理</h2>
            <div class="header-actions">
              <el-button type="primary" @click="loadUsers" :icon="Refresh">
                刷新
              </el-button>
              <el-button type="success" @click="addUser" :icon="Plus">
                新增用户
              </el-button>
            </div>
          </div>
          
          <!-- 搜索和筛选区域 -->
          <div class="filter-bar">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input 
                  v-model="userSearch.username" 
                  placeholder="用户名" 
                  clearable
                  @input="filterUsers"
                />
              </el-col>
              <el-col :span="6">
                <el-input 
                  v-model="userSearch.real_name" 
                  placeholder="真实姓名" 
                  clearable
                  @input="filterUsers"
                />
              </el-col>
              <el-col :span="6">
                <el-select 
                  v-model="userSearch.role" 
                  placeholder="角色" 
                  clearable
                  @change="filterUsers"
                >
                  <el-option label="管理员" value="admin" />
                  <el-option label="普通用户" value="user" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-select 
                  v-model="userSearch.status" 
                  placeholder="状态" 
                  clearable
                  @change="filterUsers"
                >
                  <el-option label="启用" value="1" />
                  <el-option label="禁用" value="0" />
                </el-select>
              </el-col>
            </el-row>
          </div>
          
          <el-table 
            :data="filteredUsers.slice((currentPage - 1) * pageSize, currentPage * pageSize)" 
            stripe 
            style="width: 100%" 
            v-loading="loading"
            row-key="user_id"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
            :cell-style="{ padding: '10px 0' }"
            height="calc(100vh - 280px)"
          >
            <el-table-column prop="username" label="用户名" width="150" fixed="left" sortable>
              <template #default="{ row }">
                <div class="user-cell">
                  <el-avatar size="small" :style="{ backgroundColor: getAvatarColor(row.username) }">
                    {{ getInitial(row.username) }}
                  </el-avatar>
                  <span>{{ row.username }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="real_name" label="真实姓名" width="120" sortable />
            <el-table-column prop="phone" label="电话" width="150" sortable />
            <el-table-column label="角色" width="120" sortable>
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
                  <User />
                  {{ row.role === 'admin' ? '管理员' : '普通用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120" sortable>
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                    <CircleCheck v-if="row.is_active" />
                  <CircleClose v-else />
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="180" sortable>
              <template #default="{ row }">
                <Clock />
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="last_login" label="最后登录" width="180" sortable>
              <template #default="{ row }">
                <User />
                {{ row.last_login ? formatDateTime(row.last_login) : '从未登录' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="350" fixed="right">
              <template #default="{ row }">
                <el-button 
                  size="small" 
                  @click="editUser(row)"
                  :icon="Edit"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="resetPassword(row)"
                  :icon="Key"
                >
                  重置密码
                </el-button>
                <el-button 
                  size="small" 
                  :type="row.is_active ? 'warning' : 'success'"
                  @click="toggleUserStatus(row)"
                  :icon="row.is_active ? Minus : CircleCheck"
                >
                  {{ row.is_active ? '禁用' : '启用' }}
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteUserRow(row)"
                  :icon="Delete"
                  v-if="row.user_id !== userInfo.user_id"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredUsers.length"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>

        <!-- 分支管理 -->
        <div v-else-if="activeMenu === 'branches'" class="branch-management">
          <div class="page-header">
            <h2>🏯 家族分支管理</h2>
            <div class="header-actions">
              <el-button type="primary" @click="loadBranches" :icon="Refresh">
                刷新
              </el-button>
              <el-button type="success" @click="addBranch" :icon="Plus">
                新增分支
              </el-button>
            </div>
          </div>
          
          <!-- 搜索和筛选区域 -->
          <div class="filter-bar">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input 
                  v-model="branchSearch.name" 
                  placeholder="分支名称" 
                  clearable
                  @input="filterBranches"
                />
              </el-col>
              <el-col :span="6">
                <el-input 
                  v-model="branchSearch.surname" 
                  placeholder="姓氏" 
                  clearable
                  @input="filterBranches"
                />
              </el-col>
              <el-col :span="6">
                <el-input 
                  v-model="branchSearch.ancestral_home" 
                  placeholder="祖源地" 
                  clearable
                  @input="filterBranches"
                />
              </el-col>
              <el-col :span="6">
                <el-button type="primary" @click="loadBranches">
                  搜索
                </el-button>
              </el-col>
            </el-row>
          </div>
          
          <el-table 
            :data="filteredBranches.slice((branchCurrentPage - 1) * branchPageSize, branchCurrentPage * branchPageSize)" 
            stripe 
            style="width: 100%" 
            v-loading="branchLoading"
            row-key="id"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
            :cell-style="{ padding: '10px 0' }"
            height="calc(100vh - 280px)"
          >
            <el-table-column prop="name" label="分支名称" width="200" fixed="left" sortable>
              <template #default="{ row }">
                <div class="branch-cell">
                  <User />
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="surname" label="姓氏" width="120" sortable />
            <el-table-column prop="ancestral_home" label="祖源地" width="200" sortable />
            <el-table-column prop="first_ancestor" label="开基祖" width="200" sortable />
            <el-table-column prop="historical_summary" label="历史摘要" min-width="300" show-overflow-tooltip />
            <el-table-column prop="source_reference" label="资料来源" width="200" show-overflow-tooltip />
            <el-table-column prop="created_at" label="创建时间" width="180" sortable>
              <template #default="{ row }">
                <Clock />
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button 
                  size="small" 
                  @click="editBranch(row)"
                  :icon="Edit"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteBranch(row)"
                  :icon="Delete"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="branchCurrentPage"
              v-model:page-size="branchPageSize"
              :page-sizes="[10, 20, 50, 100]"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredBranches.length"
              @size-change="branchHandleSizeChange"
              @current-change="branchHandleCurrentChange"
            />
          </div>
        </div>

        <!-- 地点管理 -->
        <div v-else-if="activeMenu === 'locations'" class="location-management">
          <div class="page-header">
            <h2>📍 地点管理</h2>
            <div class="header-actions">
              <el-button type="primary" @click="loadLocations" :icon="Refresh">
                刷新
              </el-button>
              <el-button type="success" @click="addLocation" :icon="Plus">
                新增地点
              </el-button>
            </div>
          </div>
          
          <!-- 搜索和筛选区域 -->
          <div class="filter-bar">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input 
                  v-model="locationSearch.name" 
                  placeholder="地名" 
                  clearable
                  @input="filterLocations"
                />
              </el-col>
              <el-col :span="6">
                <el-input 
                  v-model="locationSearch.modern_name" 
                  placeholder="现代地名" 
                  clearable
                  @input="filterLocations"
                />
              </el-col>
              <el-col :span="6">
                <el-select 
                  v-model="locationSearch.type" 
                  placeholder="地点类型" 
                  clearable
                  @change="filterLocations"
                >
                  <el-option label="起源地" value="origin" />
                  <el-option label="聚居地" value="settlement" />
                  <el-option label="途经地" value="node" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-button type="primary" @click="loadLocations">
                  搜索
                </el-button>
              </el-col>
            </el-row>
          </div>
          
          <el-table 
            :data="filteredLocations.slice((locationCurrentPage - 1) * locationPageSize, locationCurrentPage * locationPageSize)" 
            stripe 
            style="width: 100%" 
            v-loading="locationLoading"
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
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="locationCurrentPage"
              v-model:page-size="locationPageSize"
              :page-sizes="[10, 20, 50, 100]"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredLocations.length"
              @size-change="locationHandleSizeChange"
              @current-change="locationHandleCurrentChange"
            />
          </div>
        </div>

        <!-- 迁徙记录管理 -->
        <div v-else-if="activeMenu === 'migrations'" class="migrations-section">
          <div class="page-header">
            <h2>🗺️ 迁徙记录管理</h2>
            <div class="header-actions">
              <el-button type="primary" @click="loadMigrations" :icon="Refresh">
                刷新
              </el-button>
              <el-button type="success" @click="addMigration" :icon="Plus">
                新增迁徙记录
              </el-button>
            </div>
          </div>
          
          <!-- 搜索和筛选区域 -->
          <div class="filter-bar">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input 
                  v-model="migrationSearch.branch_name" 
                  placeholder="分支名称" 
                  clearable
                  @input="filterMigrations"
                />
              </el-col>
              <el-col :span="6">
                <el-input 
                  v-model="migrationSearch.period" 
                  placeholder="迁徙时期" 
                  clearable
                  @input="filterMigrations"
                />
              </el-col>
              <el-col :span="6">
                <el-input 
                  v-model="migrationSearch.reason" 
                  placeholder="迁徙原因" 
                  clearable
                  @input="filterMigrations"
                />
              </el-col>
              <el-col :span="6">
                <el-button type="primary" @click="loadMigrations">
                  搜索
                </el-button>
              </el-col>
            </el-row>
          </div>
          
          <el-table 
            :data="filteredMigrations.slice((migrationCurrentPage - 1) * migrationPageSize, migrationCurrentPage * migrationPageSize)" 
            stripe 
            style="width: 100%" 
            v-loading="migrationLoading"
            row-key="id"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
            :cell-style="{ padding: '10px 0' }"
            height="calc(100vh - 280px)"
          >
            <el-table-column prop="branch_name" label="所属分支" width="200" fixed="left" sortable>
              <template #default="{ row }">
                <div class="migration-cell">
                  <User />
                  <span>{{ row.branch_name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="from_location_name" label="起始地点" width="150" sortable />
            <el-table-column prop="to_location_name" label="目的地" width="150" sortable />
            <el-table-column prop="period" label="迁徙时期" width="150" sortable />
            <el-table-column prop="reason" label="迁徙原因" width="200" show-overflow-tooltip />
            <el-table-column prop="key_figure" label="关键人物" width="150" sortable />
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button 
                  size="small" 
                  @click="editMigration(row)"
                  :icon="Edit"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteMigration(row)"
                  :icon="Delete"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="migrationCurrentPage"
              v-model:page-size="migrationPageSize"
              :page-sizes="[10, 20, 50, 100]"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredMigrations.length"
              @size-change="migrationHandleSizeChange"
              @current-change="migrationHandleCurrentChange"
            />
          </div>
        </div>

        <!-- 提交审核 -->
        <div v-else-if="activeMenu === 'submissions'" class="submissions-section">
          <div class="page-header">
            <h2>📝 提交审核</h2>
            <div class="header-actions">
              <el-button type="primary" @click="loadMigrationSubmissions" :icon="Refresh">
                刷新
              </el-button>
            </div>
          </div>
          
          <!-- 搜索和筛选 -->
          <div class="search-section">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input 
                  v-model="submissionSearch.username" 
                  placeholder="提交用户名" 
                  clearable
                  @input="filterSubmissions"
                />
              </el-col>
              <el-col :span="6">
                <el-input 
                  v-model="submissionSearch.branch_name" 
                  placeholder="分支名称" 
                  clearable
                  @input="filterSubmissions"
                />
              </el-col>
              <el-col :span="6">
                <el-select 
                  v-model="submissionSearch.status" 
                  placeholder="审核状态" 
                  clearable
                  @change="filterSubmissions"
                >
                  <el-option label="待审核" value="pending"></el-option>
                  <el-option label="已通过" value="approved"></el-option>
                  <el-option label="已拒绝" value="rejected"></el-option>
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-button type="primary" @click="loadMigrationSubmissions">
                  搜索
                </el-button>
              </el-col>
            </el-row>
          </div>
          
          <!-- 提交列表 -->
          <el-table 
            :data="filteredSubmissions.slice((submissionCurrentPage - 1) * submissionPageSize, submissionCurrentPage * submissionPageSize)" 
            stripe 
            style="width: 100%" 
            v-loading="submissionLoading"
            row-key="submission_id"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
            :cell-style="{ padding: '10px 0' }"
            height="calc(100vh - 280px)"
          >
            <el-table-column prop="submission_id" label="提交ID" width="100" />
            <el-table-column prop="branch_name" label="分支名称" width="150" />
            <el-table-column prop="username" label="提交用户" width="120" />
            <el-table-column prop="migration_description" label="口述史描述" min-width="300" show-overflow-tooltip />
            <el-table-column prop="migration_period" label="迁徙年代" width="120" />
            <el-table-column prop="estimated_year" label="估算年份" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag 
                  :type="getSubmissionStatusType(row.status)" 
                  size="small"
                >
                  {{ getSubmissionStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="submitted_at" label="提交时间" width="180">
              <template #default="{ row }">
                <Clock />
                {{ formatDateTime(row.submitted_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="reviewer_name" label="审核员" width="120" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button 
                  size="small" 
                  type="primary"
                  @click="viewSubmissionDetails(row)"
                >
                  查看详情
                </el-button>
                <el-button 
                  size="small" 
                  type="success"
                  :disabled="row.status !== 'pending'"
                  @click="approveSubmission(row)"
                >
                  通过
                </el-button>
                <el-button 
                  size="small" 
                  type="danger"
                  :disabled="row.status !== 'pending'"
                  @click="rejectSubmission(row)"
                >
                  拒绝
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="submissionCurrentPage"
              v-model:page-size="submissionPageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="filteredSubmissions.length"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSubmissionSizeChange"
              @current-change="handleSubmissionCurrentChange"
            />
          </div>
        </div>

        <!-- 编辑/新增用户对话框 -->
        <el-dialog v-model="editDialogVisible" :title="currentEditUser.user_id ? '编辑用户' : '新增用户'" width="500px">
          <el-form :model="currentEditUser" label-width="100px">
            <el-form-item label="用户名" :required="true">
              <el-input v-model="currentEditUser.username" :disabled="!!currentEditUser.user_id" />
            </el-form-item>
            <el-form-item label="密码" v-if="!currentEditUser.user_id">
              <el-input v-model="currentEditUser.password" type="password" show-password />
            </el-form-item>
            <el-form-item label="真实姓名">
              <el-input v-model="currentEditUser.real_name" />
            </el-form-item>
            <el-form-item label="电话">
              <el-input v-model="currentEditUser.phone" />
            </el-form-item>
            <el-form-item label="角色">
              <el-select v-model="currentEditUser.role" placeholder="请选择角色">
                <el-option label="普通用户" value="user" />
                <el-option label="管理员" value="admin" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-switch
                v-model="currentEditUser.is_active"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="editDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="saveUser">保存</el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 编辑/新增分支对话框 -->
        <el-dialog v-model="branchDialogVisible" :title="currentBranch.id ? '编辑分支' : '新增分支'" width="600px">
          <el-form :model="currentBranch" label-width="100px">
            <el-form-item label="分支名称" :required="true">
              <el-input v-model="currentBranch.name" placeholder="请输入分支名称" />
            </el-form-item>
            <el-form-item label="姓氏">
              <el-input v-model="currentBranch.surname" placeholder="请输入姓氏" />
            </el-form-item>
            <el-form-item label="祖源地">
              <el-input v-model="currentBranch.ancestral_home" placeholder="请输入祖源地" />
            </el-form-item>
            <el-form-item label="开基祖">
              <el-input v-model="currentBranch.first_ancestor" placeholder="请输入开基祖" />
            </el-form-item>
            <el-form-item label="历史摘要">
              <el-input 
                v-model="currentBranch.historical_summary" 
                type="textarea" 
                :rows="4"
                placeholder="请输入历史摘要" 
              />
            </el-form-item>
            <el-form-item label="资料来源">
              <el-input v-model="currentBranch.source_reference" placeholder="请输入资料来源" />
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="branchDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="saveBranch">保存</el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 编辑/新增地点对话框 -->
        <el-dialog v-model="locationDialogVisible" :title="currentLocation.id ? '编辑地点' : '新增地点'" width="600px">
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
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="locationDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="saveLocation">保存</el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 编辑/新增迁徙记录对话框 -->
        <el-dialog v-model="migrationDialogVisible" :title="currentMigration.id ? '编辑迁徙记录' : '新增迁徙记录'" width="700px">
          <el-form :model="currentMigration" label-width="120px">
            <el-form-item label="所属分支" :required="true">
              <el-select v-model="currentMigration.branch_id" placeholder="请选择分支">
                <el-option 
                  v-for="branch in branches" 
                  :key="branch.id" 
                  :label="branch.name" 
                  :value="branch.id" 
                />
              </el-select>
            </el-form-item>
            <el-form-item label="起始地点" :required="true">
              <el-select v-model="currentMigration.from_location_id" placeholder="请选择起始地点">
                <el-option 
                  v-for="location in locations" 
                  :key="location.id" 
                  :label="location.historical_name" 
                  :value="location.id" 
                />
              </el-select>
            </el-form-item>
            <el-form-item label="目的地" :required="true">
              <el-select v-model="currentMigration.to_location_id" placeholder="请选择目的地">
                <el-option 
                  v-for="location in locations" 
                  :key="location.id" 
                  :label="location.historical_name" 
                  :value="location.id" 
                />
              </el-select>
            </el-form-item>
            <el-form-item label="迁徙时期" :required="true">
              <el-input v-model="currentMigration.period" placeholder="请输入迁徙时期" />
            </el-form-item>
            <el-form-item label="迁徙原因">
              <el-input v-model="currentMigration.reason" placeholder="请输入迁徙原因" />
            </el-form-item>
            <el-form-item label="关键人物">
              <el-input v-model="currentMigration.key_figure" placeholder="请输入关键人物" />
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="migrationDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="saveMigration">保存</el-button>
            </span>
          </template>
        </el-dialog>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { logout } from '@/api/auth'
import { fetchStatistics } from '@/api/genealogy'
import { getAllUsers, updateUser, deleteUser, resetUserPassword, getAllBranches, createBranch, updateBranch, deleteBranch as deleteBranchApi, getAllLocations, createLocation, updateLocation, deleteLocation as deleteLocationApi, getAllMigrations, createMigration, updateMigration, deleteMigration as deleteMigrationApi, getAllMigrationSubmissions, reviewMigrationSubmission } from '@/api/admin'
import { Refresh, Plus, Edit, Key, Minus, CircleCheck, Delete, User, Clock, CircleClose, Location } from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('dashboard')
const userInfo = ref(JSON.parse(sessionStorage.getItem('userInfo') || '{}'))
const statistics = ref({
  branches: 0,
  locations: 0,
  migrations: 0,
  valid_migrations: 0
})
const users = ref([])
const loading = ref(false)
const editDialogVisible = ref(false)
const currentEditUser = ref({})

// 添加用户管理相关的数据定义
const currentPage = ref(1)
const pageSize = ref(10)
const userSearch = ref({
  username: '',
  real_name: '',
  role: '',
  status: ''
})

// 计算属性：过滤后的用户列表
const filteredUsers = computed(() => {
  let result = users.value
  
  // 根据搜索条件过滤
  if (userSearch.value.username) {
    result = result.filter(user => 
      user.username.toLowerCase().includes(userSearch.value.username.toLowerCase())
    )
  }
  
  if (userSearch.value.real_name) {
    result = result.filter(user => 
      user.real_name.toLowerCase().includes(userSearch.value.real_name.toLowerCase())
    )
  }
  
  if (userSearch.value.role) {
    result = result.filter(user => user.role === userSearch.value.role)
  }
  
  if (userSearch.value.status !== '') {
    result = result.filter(user => user.is_active.toString() === userSearch.value.status)
  }
  
  return result
})

// 分页相关函数
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 搜索函数
const filterUsers = () => {
  currentPage.value = 1
}

// 获取用户名首字母
const getInitial = (name) => {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

// 根据用户名生成头像背景色
const getAvatarColor = (name) => {
  if (!name) return '#409eff'
  
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  const colors = [
    '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', 
    '#9013FE', '#007AFF', '#5AC8FA', '#00C7BE',
    '#4CD964', '#FFCC00', '#FF9500', '#FF3B30'
  ]
  
  return colors[Math.abs(hash) % colors.length]
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 添加分支管理相关的数据定义
const branches = ref([])
const branchLoading = ref(false)
const branchDialogVisible = ref(false)
const currentBranch = ref({})
const branchSearch = ref({
  name: '',
  surname: '',
  ancestral_home: ''
})
const branchCurrentPage = ref(1)
const branchPageSize = ref(10)

// 计算属性：过滤后的分支列表
const filteredBranches = computed(() => {
  let result = branches.value
  
  // 根据搜索条件过滤
  if (branchSearch.value.name) {
    result = result.filter(branch => 
      branch.name.toLowerCase().includes(branchSearch.value.name.toLowerCase())
    )
  }
  
  if (branchSearch.value.surname) {
    result = result.filter(branch => 
      branch.surname.toLowerCase().includes(branchSearch.value.surname.toLowerCase())
    )
  }
  
  if (branchSearch.value.ancestral_home) {
    result = result.filter(branch => 
      branch.ancestral_home.toLowerCase().includes(branchSearch.value.ancestral_home.toLowerCase())
    )
  }
  
  return result
})

// 分支管理相关函数
const loadBranches = async () => {
  branchLoading.value = true
  try {
    const response = await getAllBranches()
    // 确保所有分支都有完整的字段
    branches.value = response.map(branch => ({
      ...branch,
      historical_summary: branch.historical_summary || '',
      source_reference: branch.source_reference || '',
      first_ancestor: branch.first_ancestor || '',
      ancestral_home: branch.ancestral_home || '',
      surname: branch.surname || '姜'
    }))
  } catch (error) {
    ElMessage.error(error.message || '加载分支列表失败')
  } finally {
    branchLoading.value = false
  }
}

const editBranch = (branch) => {
  currentBranch.value = { ...branch }
  branchDialogVisible.value = true
}

const addBranch = () => {
  currentBranch.value = {
    id: null,
    name: '',
    surname: '姜',
    ancestral_home: '',
    first_ancestor: '',
    historical_summary: '',
    source_reference: ''
  }
  branchDialogVisible.value = true
}

const saveBranch = async () => {
  try {
    if (currentBranch.value.id) {
      // 更新分支
      await updateBranch(currentBranch.value.id, {
        name: currentBranch.value.name,
        surname: currentBranch.value.surname,
        ancestral_home: currentBranch.value.ancestral_home,
        first_ancestor: currentBranch.value.first_ancestor,
        historical_summary: currentBranch.value.historical_summary,
        source_reference: currentBranch.value.source_reference
      })
      ElMessage.success('分支信息更新成功')
    } else {
      // 新增分支
      await createBranch({
        name: currentBranch.value.name,
        surname: currentBranch.value.surname,
        ancestral_home: currentBranch.value.ancestral_home,
        first_ancestor: currentBranch.value.first_ancestor,
        historical_summary: currentBranch.value.historical_summary,
        source_reference: currentBranch.value.source_reference
      })
      ElMessage.success('分支创建成功')
    }
    
    branchDialogVisible.value = false
    await loadBranches()
  } catch (error) {
    ElMessage.error(error.message || '保存分支失败')
  }
}

const deleteBranch = async (branch) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分支 "${branch.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteBranchApi(branch.id)
    ElMessage.success('分支删除成功')
    await loadBranches()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除分支失败')
    }
  }
}

const filterBranches = () => {
  branchCurrentPage.value = 1
}

const branchHandleSizeChange = (size) => {
  branchPageSize.value = size
  branchCurrentPage.value = 1
}

const branchHandleCurrentChange = (page) => {
  branchCurrentPage.value = page
}

// 添加地点管理相关的数据定义
const locations = ref([])
const locationLoading = ref(false)
const locationDialogVisible = ref(false)
const currentLocation = ref({})
const locationSearch = ref({
  name: '',
  modern_name: '',
  type: ''
})
const locationCurrentPage = ref(1)
const locationPageSize = ref(10)

// 计算属性：过滤后的地点列表
const filteredLocations = computed(() => {
  let result = locations.value
  
  // 根据搜索条件过滤
  if (locationSearch.value.name) {
    result = result.filter(location => 
      location.historical_name.toLowerCase().includes(locationSearch.value.name.toLowerCase()) ||
      location.modern_name.toLowerCase().includes(locationSearch.value.name.toLowerCase())
    )
  }
  
  if (locationSearch.value.modern_name) {
    result = result.filter(location => 
      location.modern_name.toLowerCase().includes(locationSearch.value.modern_name.toLowerCase())
    )
  }
  
  if (locationSearch.value.type) {
    result = result.filter(location => location.type === locationSearch.value.type)
  }
  
  return result
})

// 地点管理相关函数
const loadLocations = async () => {
  locationLoading.value = true
  try {
    const response = await getAllLocations()
    // 确保所有地点都有完整的字段
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
    locationLoading.value = false
  }
}

const editLocation = (location) => {
  currentLocation.value = { ...location }
  locationDialogVisible.value = true
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
  locationDialogVisible.value = true
}

const saveLocation = async () => {
  try {
    if (currentLocation.value.id) {
      // 更新地点
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
      // 新增地点
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
    
    locationDialogVisible.value = false
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

const filterLocations = () => {
  locationCurrentPage.value = 1
}

const locationHandleSizeChange = (size) => {
  locationPageSize.value = size
  locationCurrentPage.value = 1
}

const locationHandleCurrentChange = (page) => {
  locationCurrentPage.value = page
}

// 添加迁徙记录管理相关的数据定义
const migrations = ref([])
const migrationLoading = ref(false)
const migrationDialogVisible = ref(false)
const currentMigration = ref({})
const migrationSearch = ref({
  branch_name: '',
  period: '',
  reason: ''
})
const migrationCurrentPage = ref(1)
const migrationPageSize = ref(10)

// 计算属性：过滤后的迁徙记录列表
const filteredMigrations = computed(() => {
  let result = migrations.value
  
  // 根据搜索条件过滤
  if (migrationSearch.value.branch_name) {
    result = result.filter(migration => 
      migration.branch_name.toLowerCase().includes(migrationSearch.value.branch_name.toLowerCase())
    )
  }
  
  if (migrationSearch.value.period) {
    result = result.filter(migration => 
      migration.period.toLowerCase().includes(migrationSearch.value.period.toLowerCase())
    )
  }
  
  if (migrationSearch.value.reason) {
    result = result.filter(migration => 
      migration.reason.toLowerCase().includes(migrationSearch.value.reason.toLowerCase())
    )
  }
  
  return result
})

// 迁徙记录管理相关函数
const loadMigrations = async () => {
  migrationLoading.value = true
  try {
    // 确保分支和地点数据已加载
    if (branches.value.length === 0) {
      await loadBranches()
    }
    if (locations.value.length === 0) {
      await loadLocations()
    }
    
    const response = await getAllMigrations()
    
    // 创建分支和地点的映射，以便快速查找名称
    const branchMap = {}
    branches.value.forEach(branch => {
      branchMap[branch.id] = branch.name
    })
    
    const locationMap = {}
    locations.value.forEach(location => {
      locationMap[location.id] = location.historical_name
    })
    
    // 确保所有迁徙记录都有完整的字段，并添加名称
    migrations.value = response.map(migration => ({
      ...migration,
      branch_name: branchMap[migration.branch_id] || `分支ID: ${migration.branch_id}`,
      from_location_name: locationMap[migration.from_location_id] || `地点ID: ${migration.from_location_id}`,
      to_location_name: locationMap[migration.to_location_id] || `地点ID: ${migration.to_location_id}`,
      period: migration.period || '',
      reason: migration.reason || '',
      date: migration.date || '',
      source: migration.source || '',
      key_figure: migration.key_figure || ''
    }))
  } catch (error) {
    ElMessage.error(error.message || '加载迁徙记录列表失败')
  } finally {
    migrationLoading.value = false
  }
}

const editMigration = (migration) => {
  currentMigration.value = { ...migration }
  migrationDialogVisible.value = true
}

const addMigration = () => {
  currentMigration.value = {
    id: null,
    branch_id: null,
    from_location_id: null,
    to_location_id: null,
    period: '',
    reason: '',
    key_figure: ''
  }
  migrationDialogVisible.value = true
}

const saveMigration = async () => {
  try {
    if (currentMigration.value.id) {
      // 更新迁徙记录
      await updateMigration(currentMigration.value.id, {
        branch_id: currentMigration.value.branch_id,
        from_location_id: currentMigration.value.from_location_id,
        to_location_id: currentMigration.value.to_location_id,
        period: currentMigration.value.period,
        reason: currentMigration.value.reason,
        key_figure: currentMigration.value.key_figure
      })
      ElMessage.success('迁徙记录更新成功')
    } else {
      // 新增迁徙记录
      await createMigration({
        branch_id: currentMigration.value.branch_id,
        from_location_id: currentMigration.value.from_location_id,
        to_location_id: currentMigration.value.to_location_id,
        period: currentMigration.value.period,
        reason: currentMigration.value.reason,
        key_figure: currentMigration.value.key_figure
      })
      ElMessage.success('迁徙记录创建成功')
    }
    
    migrationDialogVisible.value = false
    await loadMigrations()
  } catch (error) {
    ElMessage.error(error.message || '保存迁徙记录失败')
  }
}

const deleteMigration = async (migration) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除迁徙记录 "${migration.period}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteMigrationApi(migration.id)
    ElMessage.success('迁徙记录删除成功')
    await loadMigrations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除迁徙记录失败')
    }
  }
}

const filterMigrations = () => {
  migrationCurrentPage.value = 1
}

const migrationHandleSizeChange = (size) => {
  migrationPageSize.value = size
  migrationCurrentPage.value = 1
}

const migrationHandleCurrentChange = (page) => {
  migrationCurrentPage.value = page
}

// 添加提交审核相关的数据定义
const submissions = ref([])
const filteredSubmissions = ref([])
const submissionLoading = ref(false)
const submissionSearch = ref({
  username: '',
  branch_name: '',
  status: ''
})
const submissionCurrentPage = ref(1)
const submissionPageSize = ref(10)

// 提交审核相关函数
const loadMigrationSubmissions = async () => {
  submissionLoading.value = true
  try {
    const response = await getAllMigrationSubmissions()
    submissions.value = response
    filteredSubmissions.value = response
  } catch (error) {
    ElMessage.error(error.message || '加载提交审核列表失败')
  } finally {
    submissionLoading.value = false
  }
}

const filterSubmissions = () => {
  let result = submissions.value
  
  if (submissionSearch.value.username) {
    result = result.filter(submission => 
      submission.username.toLowerCase().includes(submissionSearch.value.username.toLowerCase())
    )
  }
  
  if (submissionSearch.value.branch_name) {
    result = result.filter(submission => 
      submission.branch_name.toLowerCase().includes(submissionSearch.value.branch_name.toLowerCase())
    )
  }
  
  if (submissionSearch.value.status) {
    result = result.filter(submission => 
      submission.status === submissionSearch.value.status
    )
  }
  
  filteredSubmissions.value = result
  submissionCurrentPage.value = 1
}

const getSubmissionStatusType = (status) => {
  switch (status) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

const getSubmissionStatusText = (status) => {
  switch (status) {
    case 'approved': return '已通过'
    case 'rejected': return '已拒绝'
    case 'pending': return '待审核'
    default: return status
  }
}

const viewSubmissionDetails = (submission) => {
  ElMessageBox.alert(`
    <div class="submission-details">
      <h4>提交详情</h4>
      <p><strong>提交ID：</strong>${submission.submission_id}</p>
      <p><strong>分支名称：</strong>${submission.branch_name}</p>
      <p><strong>姓氏：</strong>${submission.surname || '姜'}</p>
      <p><strong>提交用户：</strong>${submission.username} (${submission.real_name || '未知'})</p>
      <p><strong>口述史描述：</strong>${submission.migration_description}</p>
      <p><strong>迁徙年代：</strong>${submission.migration_period || '未知'}</p>
      <p><strong>估算年份：</strong>${submission.estimated_year || '未知'}</p>
      <p><strong>迁徙路线：</strong>${submission.migration_route || '未知'}</p>
      <p><strong>迁徙原因：</strong>${submission.migration_reason || '未知'}</p>
      <p><strong>关键人物：</strong>${submission.key_figures || '未知'}</p>
      <p><strong>资料来源：</strong>${submission.source_reference || '未知'}</p>
      <p><strong>提交时间：</strong>${formatDateTime(submission.submitted_at)}</p>
      <p><strong>审核状态：</strong><span class="status-${submission.status}">${getSubmissionStatusText(submission.status)}</span></p>
      ${submission.review_comment ? `<p><strong>审核意见：</strong>${submission.review_comment}</p>` : ''}
      ${submission.reviewer_name ? `<p><strong>审核员：</strong>${submission.reviewer_name}</p>` : ''}
      ${submission.reviewed_at ? `<p><strong>审核时间：</strong>${formatDateTime(submission.reviewed_at)}</p>` : ''}
    </div>
  `, '提交详情', {
    dangerouslyUseHTMLString: true,
    customClass: 'submission-detail-dialog',
    showConfirmButton: false,
    callback: action => {}
  })
}

const approveSubmission = async (submission) => {
  try {
    await ElMessageBox.confirm(
      `确定要通过此提交吗？分支名称：${submission.branch_name}`,
      '审核确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    
    await reviewMigrationSubmission(submission.submission_id, {
      status: 'approved',
      review_comment: '审核通过'
    })
    
    ElMessage.success('审核通过成功')
    await loadMigrationSubmissions() // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '审核失败')
    }
  }
}

const rejectSubmission = async (submission) => {
  try {
    // 弹出对话框获取拒绝原因
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '审核拒绝', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^.{1,200}$/,
      inputErrorMessage: '拒绝原因长度为1-200个字符',
      inputPlaceholder: '请输入拒绝原因...'
    })
    
    await reviewMigrationSubmission(submission.submission_id, {
      status: 'rejected',
      review_comment: value
    })
    
    ElMessage.success('审核拒绝成功')
    await loadMigrationSubmissions() // 重新加载列表
  } catch (error) {
    if (error !== 'cancel' && error.message) {
      ElMessage.error(error.message || '审核失败')
    }
  }
}

const handleSubmissionSizeChange = (size) => {
  submissionPageSize.value = size
  submissionCurrentPage.value = 1
}

const handleSubmissionCurrentChange = (page) => {
  submissionCurrentPage.value = page
}

// 辅助函数：获取地点类型名称
const getLocationTypeName = (type) => {
  const typeMap = {
    'origin': '起源地',
    'settlement': '聚居地',
    'node': '途经地'
  }
  return typeMap[type] || type
}

// 辅助函数：获取地点类型标签样式
const getLocationTypeTag = (type) => {
  const typeMap = {
    'origin': 'warning',
    'settlement': 'success',
    'node': 'info'
  }
  return typeMap[type] || 'default'
}

const userCount = computed(() => users.value.length)

onMounted(async () => {
  try {
    statistics.value = await fetchStatistics()
    
    // 如果当前菜单是用户管理，加载用户列表
    if (activeMenu.value === 'users') {
      await loadUsers()
    }
    // 如果当前菜单是分支管理，加载分支列表
    else if (activeMenu.value === 'branches') {
      await loadBranches()
    }
    // 如果当前菜单是地点管理，加载地点列表
    else if (activeMenu.value === 'locations') {
      await loadLocations()
    }
    // 如果当前菜单是迁徙记录管理，加载迁徙记录列表
    else if (activeMenu.value === 'migrations') {
      await loadMigrations()
      // 确保分支和地点数据已加载，以便新增/编辑迁徙记录时使用
      if (branches.value.length === 0) {
        await loadBranches()
      }
      if (locations.value.length === 0) {
        await loadLocations()
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
})

const handleMenuSelect = async (index) => {
  activeMenu.value = index
  if (index === 'users') {
    await loadUsers()
  } else if (index === 'branches') {
    await loadBranches()
  } else if (index === 'locations') {
    await loadLocations()
  } else if (index === 'migrations') {
    await loadMigrations()
    // 确保分支和地点数据已加载，以便新增/编辑迁徙记录时使用
    if (branches.value.length === 0) {
      await loadBranches()
    }
    if (locations.value.length === 0) {
      await loadLocations()
    }
  } else if (index === 'submissions') {
    await loadMigrationSubmissions()
  }
}

const getMenuTitle = (menu) => {
  const titles = {
    dashboard: '数据概览',
    branches: '家族分支管理',
    locations: '地点管理',
    migrations: '迁徙记录管理',
    users: '用户管理'
  }
  return titles[menu] || ''
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

const loadUsers = async () => {
  loading.value = true
  try {
    users.value = await getAllUsers()
  } catch (error) {
    ElMessage.error(error.message || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const editUser = (user) => {
  currentEditUser.value = { ...user }
  editDialogVisible.value = true
}

const addUser = () => {
  currentEditUser.value = {
    username: '',
    password: '',
    real_name: '',
    phone: '',
    role: 'user',
    is_active: true
  }
  editDialogVisible.value = true
}

const saveUser = async () => {
  try {
    if (currentEditUser.value.user_id) {
      // 更新用户
      await updateUser(currentEditUser.value.user_id, {
        real_name: currentEditUser.value.real_name,
        phone: currentEditUser.value.phone,
        role: currentEditUser.value.role,
        is_active: currentEditUser.value.is_active
      })
      ElMessage.success('用户信息更新成功')
    } else {
      // 新增用户
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({
          username: currentEditUser.value.username,
          password: currentEditUser.value.password,
          real_name: currentEditUser.value.real_name,
          phone: currentEditUser.value.phone
        })
      })
      
      const result = await response.json()
      if (response.ok) {
        ElMessage.success('用户创建成功')
      } else {
        throw new Error(result.message || '创建用户失败')
      }
    }
    
    editDialogVisible.value = false
    await loadUsers()
  } catch (error) {
    ElMessage.error(error.message || '保存用户失败')
  }
}

const deleteUserRow = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteUser(user.user_id)
    ElMessage.success('用户删除成功')
    await loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除用户失败')
    }
  }
}

const resetPassword = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户 "${user.username}" 的密码吗？`,
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const result = await resetUserPassword(user.user_id)
    ElMessage.success(result.message)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '重置密码失败')
    }
  }
}

const toggleUserStatus = async (user) => {
  try {
    const newStatus = !user.is_active
    await updateUser(user.user_id, { is_active: newStatus })
    ElMessage.success(newStatus ? '用户启用成功' : '用户禁用成功')
    await loadUsers()
  } catch (error) {
    ElMessage.error(error.message || '更新用户状态失败')
  }
}
</script>

<style scoped>
.admin-page {
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

.admin-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.dashboard h2 {
  margin-bottom: 20px;
  color: #333;
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
  gap: 16px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 48px;
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

.placeholder {
  background: white;
  padding: 40px;
  border-radius: 8px;
  text-align: center;
}

.placeholder h2 {
  color: #333;
  margin-bottom: 16px;
}

.placeholder p {
  color: #999;
  font-size: 16px;
}

/* 用户管理页面样式 */
.user-management {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  height: 100%;
}

.branch-management {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  height: 100%;
}

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

.filter-bar {
  margin-bottom: 20px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
  border: 1px solid #eee;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.branch-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.location-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.migration-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 表格样式 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

::v-deep(.el-table__row:hover > td) {
  background-color: #f5f7fa;
}

:deep(.el-table td) {
  border-bottom: 1px solid #eee;
}

:deep(.el-table th.is-leaf) {
  border-bottom: 1px solid #dfe4ed;
}

.submissions-section {
  padding: 20px;
}

.submissions-section h2 {
  margin-bottom: 20px;
  color: #303133;
  font-size: 20px;
}

.search-section {
  margin-bottom: 20px;
}

.submission-details h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.submission-details p {
  margin: 5px 0;
  line-height: 1.5;
}

.submission-detail-dialog :deep(.el-message-box__message) {
  max-height: 500px;
  overflow-y: auto;
}
</style>