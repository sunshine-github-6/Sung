<template>
  <div class="branch-management">
    <div class="page-header">
      <h2>家族分支管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="loadBranches" :icon="Refresh">
          刷新
        </el-button>
        <el-button type="success" @click="addBranch" :icon="Plus">
          新增分支
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="filters.name"
            placeholder="分支名称"
            clearable
            @input="handleFilter"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.surname"
            placeholder="姓氏"
            clearable
            @input="handleFilter"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.ancestral_home"
            placeholder="祖源地"
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

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredBranches.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="currentBranch.id ? '编辑分支' : '新增分支'" width="600px">
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
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveBranch">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Delete, User, Clock } from '@element-plus/icons-vue'
import { getAllBranches, createBranch, updateBranch, deleteBranch as deleteBranchApi } from '@/api/admin'

const branches = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentBranch = ref({})
const currentPage = ref(1)
const pageSize = ref(10)
const filters = ref({
  name: '',
  surname: '',
  ancestral_home: ''
})

const filteredBranches = computed(() => {
  let result = branches.value

  if (filters.value.name) {
    result = result.filter(branch =>
      branch.name.toLowerCase().includes(filters.value.name.toLowerCase())
    )
  }

  if (filters.value.surname) {
    result = result.filter(branch =>
      (branch.surname || '').toLowerCase().includes(filters.value.surname.toLowerCase())
    )
  }

  if (filters.value.ancestral_home) {
    result = result.filter(branch =>
      (branch.ancestral_home || '').toLowerCase().includes(filters.value.ancestral_home.toLowerCase())
    )
  }

  return result
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredBranches.value.slice(start, end)
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

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const loadBranches = async () => {
  loading.value = true
  try {
    branches.value = await getAllBranches()
  } catch (error) {
    ElMessage.error(error.message || '加载分支列表失败')
  } finally {
    loading.value = false
  }
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
  dialogVisible.value = true
}

const editBranch = (branch) => {
  currentBranch.value = { ...branch }
  dialogVisible.value = true
}

const saveBranch = async () => {
  try {
    if (currentBranch.value.id) {
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

    dialogVisible.value = false
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

onMounted(() => {
  loadBranches()
})
</script>

<style scoped>
.branch-management {
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

.branch-cell {
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
