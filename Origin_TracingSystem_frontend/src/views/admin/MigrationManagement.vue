<template>
  <div class="migration-management">
    <div class="page-header">
      <h2>迁徙记录管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="loadMigrations" :icon="Refresh">
          刷新
        </el-button>
        <el-button type="success" @click="addMigration" :icon="Plus">
          新增迁徙记录
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="filters.branch_name"
            placeholder="分支名称"
            clearable
            @input="handleFilter"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.period"
            placeholder="迁徙时期"
            clearable
            @input="handleFilter"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.reason"
            placeholder="迁徙原因"
            clearable
            @input="handleFilter"
          />
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

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredMigrations.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <MigrationStepForm
      v-model="dialogVisible"
      :migration-data="currentMigration"
      @success="loadMigrations"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Delete, User } from '@element-plus/icons-vue'
import { getAllMigrations, createMigration, updateMigration, deleteMigration as deleteMigrationApi, getAllBranches, getAllLocations } from '@/api/admin'
import MigrationStepForm from '../../components/MigrationStepForm.vue'

const migrations = ref([])
const branches = ref([])
const locations = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentMigration = ref({})
const currentPage = ref(1)
const pageSize = ref(10)
const filters = ref({
  branch_name: '',
  period: '',
  reason: ''
})

const filteredMigrations = computed(() => {
  let result = migrations.value

  if (filters.value.branch_name) {
    result = result.filter(migration =>
      (migration.branch_name || '').toLowerCase().includes(filters.value.branch_name.toLowerCase())
    )
  }

  if (filters.value.period) {
    result = result.filter(migration =>
      (migration.period || '').toLowerCase().includes(filters.value.period.toLowerCase())
    )
  }

  if (filters.value.reason) {
    result = result.filter(migration =>
      (migration.reason || '').toLowerCase().includes(filters.value.reason.toLowerCase())
    )
  }

  return result
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMigrations.value.slice(start, end)
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

const loadBranches = async () => {
  try {
    branches.value = await getAllBranches()
  } catch (error) {
    ElMessage.error(error.message || '加载分支列表失败')
  }
}

const loadLocations = async () => {
  try {
    locations.value = await getAllLocations()
  } catch (error) {
    ElMessage.error(error.message || '加载地点列表失败')
  }
}

const loadMigrations = async () => {
  loading.value = true
  try {
    if (branches.value.length === 0) {
      await loadBranches()
    }
    if (locations.value.length === 0) {
      await loadLocations()
    }

    const response = await getAllMigrations()

    const branchMap = {}
    branches.value.forEach(branch => {
      branchMap[branch.id] = branch.name
    })

    const locationMap = {}
    locations.value.forEach(location => {
      locationMap[location.id] = location.historical_name
    })

    migrations.value = response.map(migration => ({
      ...migration,
      branch_name: branchMap[migration.branch_id] || '未知',
      from_location_name: locationMap[migration.from_location_id] || '未知',
      to_location_name: locationMap[migration.to_location_id] || '未知'
    }))
  } catch (error) {
    ElMessage.error(error.message || '加载迁徙记录列表失败')
  } finally {
    loading.value = false
  }
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
  dialogVisible.value = true
}

const editMigration = (migration) => {
  currentMigration.value = { ...migration }
  dialogVisible.value = true
}

const saveMigration = async () => {
  try {
    if (currentMigration.value.id) {
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

    dialogVisible.value = false
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

onMounted(() => {
  loadMigrations()
})
</script>

<style scoped>
.migration-management {
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
</style>
