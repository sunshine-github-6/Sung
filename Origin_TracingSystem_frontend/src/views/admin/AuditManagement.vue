<template>
  <div class="audit-management">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="迁徙提交审核" name="submissions">
        <div class="audit-section">
          <div class="page-header">
            <h2>迁徙提交审核</h2>
            <div class="header-actions">
              <el-button type="primary" @click="loadMigrationSubmissions" :icon="Refresh">
                刷新
              </el-button>
            </div>
          </div>

          <div class="filter-bar">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input
                  v-model="submissionFilters.username"
                  placeholder="提交用户名"
                  clearable
                  @input="handleSubmissionFilter"
                />
              </el-col>
              <el-col :span="6">
                <el-input
                  v-model="submissionFilters.branch_name"
                  placeholder="分支名称"
                  clearable
                  @input="handleSubmissionFilter"
                />
              </el-col>
              <el-col :span="6">
                <el-select
                  v-model="submissionFilters.status"
                  placeholder="审核状态"
                  clearable
                  @change="handleSubmissionFilter"
                >
                  <el-option label="待审核" value="pending" />
                  <el-option label="已通过" value="approved" />
                  <el-option label="已拒绝" value="rejected" />
                </el-select>
              </el-col>
            </el-row>
          </div>

          <el-table
            :data="paginatedSubmissions"
            stripe
            style="width: 100%"
            v-loading="submissionLoading"
            row-key="submission_id"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
            :cell-style="{ padding: '10px 0' }"
            height="calc(100vh - 380px)"
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
      </el-tab-pane>

      <el-tab-pane label="密码重置审核" name="password-reset">
        <div class="audit-section">
          <div class="page-header">
            <h2>密码重置审核</h2>
            <div class="header-actions">
              <el-button type="primary" @click="loadPasswordResetRequests" :icon="Refresh">
                刷新
              </el-button>
            </div>
          </div>

          <div class="filter-bar">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-select
                  v-model="passwordResetStatus"
                  placeholder="审核状态"
                  clearable
                  @change="loadPasswordResetRequests"
                >
                  <el-option label="待处理" value="pending" />
                  <el-option label="已批准" value="approved" />
                  <el-option label="已拒绝" value="rejected" />
                </el-select>
              </el-col>
            </el-row>
          </div>

          <el-table
            :data="paginatedPasswordResets"
            stripe
            style="width: 100%"
            v-loading="passwordResetLoading"
            row-key="request_id"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
            :cell-style="{ padding: '10px 0' }"
            height="calc(100vh - 380px)"
          >
            <el-table-column prop="request_id" label="请求ID" width="100" />
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="real_name" label="真实姓名" width="120" />
            <el-table-column prop="phone" label="电话" width="150" />
            <el-table-column prop="requested_at" label="申请时间" width="180">
              <template #default="{ row }">
                <Clock />
                {{ formatDateTime(row.requested_at) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getPasswordResetStatusType(row.status)" size="small">
                  {{ getPasswordResetStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reviewer_name" label="处理人" width="120">
              <template #default="{ row }">
                <span v-if="row.reviewer_name">{{ row.reviewer_name }}</span>
                <span v-else class="text-gray">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="reviewed_at" label="处理时间" width="160">
              <template #default="{ row }">
                <span v-if="row.reviewed_at">{{ row.reviewed_at }}</span>
                <span v-else class="text-gray">-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'pending'"
                  size="small"
                  type="success"
                  @click="approvePasswordReset(row)"
                >
                  批准
                </el-button>
                <el-button
                  v-if="row.status === 'pending'"
                  size="small"
                  type="danger"
                  @click="rejectPasswordReset(row)"
                >
                  拒绝
                </el-button>
                <span v-else class="text-gray">已处理</span>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="passwordResetCurrentPage"
              v-model:page-size="passwordResetPageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="passwordResetRequests.length"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handlePasswordResetSizeChange"
              @current-change="handlePasswordResetCurrentChange"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Clock } from '@element-plus/icons-vue'
import { getAllMigrationSubmissions, reviewMigrationSubmission, getPasswordResetRequests, reviewPasswordResetRequest } from '@/api/admin'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'submissions'
  }
})

const emit = defineEmits(['update:activeTab'])

const activeTab = computed({
  get: () => props.activeTab,
  set: (val) => emit('update:activeTab', val)
})

const submissionFilters = ref({
  username: '',
  branch_name: '',
  status: ''
})
const submissions = ref([])
const filteredSubmissions = ref([])
const submissionLoading = ref(false)
const submissionCurrentPage = ref(1)
const submissionPageSize = ref(10)

const passwordResetStatus = ref('pending')
const passwordResetRequests = ref([])
const passwordResetLoading = ref(false)
const passwordResetCurrentPage = ref(1)
const passwordResetPageSize = ref(10)

const paginatedSubmissions = computed(() => {
  const start = (submissionCurrentPage.value - 1) * submissionPageSize.value
  const end = start + submissionPageSize.value
  return filteredSubmissions.value.slice(start, end)
})

const paginatedPasswordResets = computed(() => {
  const start = (passwordResetCurrentPage.value - 1) * passwordResetPageSize.value
  const end = start + passwordResetPageSize.value
  return passwordResetRequests.value.slice(start, end)
})

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleSubmissionFilter = () => {
  let result = submissions.value

  if (submissionFilters.value.username) {
    result = result.filter(submission =>
      submission.username.toLowerCase().includes(submissionFilters.value.username.toLowerCase())
    )
  }

  if (submissionFilters.value.branch_name) {
    result = result.filter(submission =>
      submission.branch_name.toLowerCase().includes(submissionFilters.value.branch_name.toLowerCase())
    )
  }

  if (submissionFilters.value.status) {
    result = result.filter(submission =>
      submission.status === submissionFilters.value.status
    )
  }

  filteredSubmissions.value = result
  submissionCurrentPage.value = 1
}

const handleSubmissionSizeChange = (size) => {
  submissionPageSize.value = size
  submissionCurrentPage.value = 1
}

const handleSubmissionCurrentChange = (page) => {
  submissionCurrentPage.value = page
}

const handlePasswordResetSizeChange = (size) => {
  passwordResetPageSize.value = size
  passwordResetCurrentPage.value = 1
}

const handlePasswordResetCurrentChange = (page) => {
  passwordResetCurrentPage.value = page
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

const getPasswordResetStatusType = (status) => {
  switch (status) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

const getPasswordResetStatusText = (status) => {
  switch (status) {
    case 'approved': return '已批准'
    case 'rejected': return '已拒绝'
    case 'pending': return '待处理'
    default: return status
  }
}

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
      <p><strong>提交时间：</strong>${formatDateTime(submission.submitted_at)}</p>
      <p><strong>状态：</strong>${getSubmissionStatusText(submission.status)}</p>
      ${submission.review_comment ? `<p><strong>审核意见：</strong>${submission.review_comment}</p>` : ''}
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
    await loadMigrationSubmissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '审核失败')
    }
  }
}

const rejectSubmission = async (submission) => {
  try {
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
    await loadMigrationSubmissions()
  } catch (error) {
    if (error !== 'cancel' && error.message) {
      ElMessage.error(error.message || '审核失败')
    }
  }
}

const loadPasswordResetRequests = async () => {
  passwordResetLoading.value = true
  try {
    const response = await getPasswordResetRequests(passwordResetStatus.value)
    passwordResetRequests.value = response
  } catch (error) {
    ElMessage.error(error.message || '加载密码重置请求列表失败')
  } finally {
    passwordResetLoading.value = false
  }
}

const approvePasswordReset = async (request) => {
  try {
    const { value: newPassword } = await ElMessageBox.prompt(
      `确定要批准 ${request.username} 的密码重置请求吗？`,
      '批准密码重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入新密码（默认：123456）',
        inputValue: '123456'
      }
    )

    await reviewPasswordResetRequest(request.request_id, {
      action: 'approve',
      new_password: newPassword,
      reviewer_id: JSON.parse(sessionStorage.getItem('userInfo') || '{}').user_id
    })

    ElMessage.success(`密码重置成功，新密码为：${newPassword}`)
    await loadPasswordResetRequests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '处理失败')
    }
  }
}

const rejectPasswordReset = async (request) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      `确定要拒绝 ${request.username} 的密码重置请求吗？`,
      '拒绝密码重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入拒绝原因',
        inputPattern: /^.{1,200}$/,
        inputErrorMessage: '拒绝原因长度为1-200个字符'
      }
    )

    await reviewPasswordResetRequest(request.request_id, {
      action: 'reject',
      review_comment: reason,
      reviewer_id: JSON.parse(sessionStorage.getItem('userInfo') || '{}').user_id
    })

    ElMessage.success('已拒绝密码重置请求')
    await loadPasswordResetRequests()
  } catch (error) {
    if (error !== 'cancel' && error.message) {
      ElMessage.error(error.message || '处理失败')
    }
  }
}

onMounted(() => {
  loadMigrationSubmissions()
})

watch(() => props.activeTab, (newVal) => {
  if (newVal === 'submissions') {
    loadMigrationSubmissions()
  } else if (newVal === 'password-reset') {
    loadPasswordResetRequests()
  }
})
</script>

<style scoped>
.audit-management {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  height: 100%;
}

.audit-section {
  padding: 0 10px;
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.text-gray {
  color: #999;
}

:deep(.el-tabs__content) {
  overflow: auto;
}
</style>
