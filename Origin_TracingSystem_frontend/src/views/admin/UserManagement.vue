<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="loadUsers" :icon="Refresh">
          刷新
        </el-button>
        <el-button type="success" @click="addUser" :icon="Plus">
          新增用户
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="filters.username"
            placeholder="用户名"
            clearable
            @input="handleFilter"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.real_name"
            placeholder="真实姓名"
            clearable
            @input="handleFilter"
          />
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="filters.role"
            placeholder="角色"
            clearable
            @change="handleFilter"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="filters.status"
            placeholder="状态"
            clearable
            @change="handleFilter"
          >
            <el-option label="启用" value="1" />
            <el-option label="禁用" value="0" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <el-table
      :data="paginatedData"
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
            v-if="row.user_id !== currentUserId"
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
        :total="filteredUsers.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="currentUser.user_id ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="currentUser" label-width="100px">
        <el-form-item label="用户名" :required="true">
          <el-input v-model="currentUser.username" :disabled="!!currentUser.user_id" />
        </el-form-item>
        <el-form-item label="密码" v-if="!currentUser.user_id">
          <el-input v-model="currentUser.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="currentUser.real_name" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="currentUser.phone" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="currentUser.role" placeholder="请选择角色">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="currentUser.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Key, Minus, CircleCheck, CircleClose, Delete, User, Clock } from '@element-plus/icons-vue'
import { getAllUsers, updateUser, deleteUser, resetUserPassword } from '@/api/admin'

const users = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentUser = ref({})
const currentPage = ref(1)
const pageSize = ref(10)
const filters = ref({
  username: '',
  real_name: '',
  role: '',
  status: ''
})

const currentUserId = ref(JSON.parse(sessionStorage.getItem('userInfo') || '{}').user_id)

const filteredUsers = computed(() => {
  let result = users.value

  if (filters.value.username) {
    result = result.filter(user =>
      user.username.toLowerCase().includes(filters.value.username.toLowerCase())
    )
  }

  if (filters.value.real_name) {
    result = result.filter(user =>
      (user.real_name || '').toLowerCase().includes(filters.value.real_name.toLowerCase())
    )
  }

  if (filters.value.role) {
    result = result.filter(user => user.role === filters.value.role)
  }

  if (filters.value.status !== '') {
    result = result.filter(user => user.is_active.toString() === filters.value.status)
  }

  return result
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUsers.value.slice(start, end)
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

const getAvatarColor = (username) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getInitial = (username) => {
  return username ? username.charAt(0).toUpperCase() : '?'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
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

const addUser = () => {
  currentUser.value = {
    username: '',
    password: '',
    real_name: '',
    phone: '',
    role: 'user',
    is_active: true
  }
  dialogVisible.value = true
}

const editUser = (user) => {
  currentUser.value = { ...user }
  dialogVisible.value = true
}

const saveUser = async () => {
  try {
    if (currentUser.value.user_id) {
      await updateUser(currentUser.value.user_id, {
        real_name: currentUser.value.real_name,
        phone: currentUser.value.phone,
        role: currentUser.value.role,
        is_active: currentUser.value.is_active
      })
      ElMessage.success('用户信息更新成功')
    } else {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({
          username: currentUser.value.username,
          password: currentUser.value.password,
          real_name: currentUser.value.real_name,
          phone: currentUser.value.phone
        })
      })

      const result = await response.json()
      if (response.ok) {
        ElMessage.success('用户创建成功')
      } else {
        throw new Error(result.message || '创建用户失败')
      }
    }

    dialogVisible.value = false
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

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
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

.user-cell {
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
