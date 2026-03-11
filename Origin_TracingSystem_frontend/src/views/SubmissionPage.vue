<template>
  <div class="submission-page">
    <!-- 顶部导航栏 -->
    <div class="topbar">
      <div class="brand">
        <span class="brand-icon">🌐</span>
        <div class="brand-text">
          <strong>姜姓迁徙时空洞察</strong>
          <small>口述史提交</small>
        </div>
      </div>
      <!-- 顶部导航栏中的搜索框 -->
      <div class="search-container top-search">
        <div class="search-wrapper">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索分支名称或地区..."
            clearable
            class="search-input"
            @input="debouncedHandleSearch"
            @clear="handleSearchClear"
          >
            <template #prefix>
              <span class="search-icon">🔍</span>
            </template>
          </el-input>
          <div v-if="searchKeyword" class="search-results">
            <div class="results-count">
              找到 {{ filteredMigrations.length }} 条匹配结果
            </div>
          </div>
        </div>
      </div>
      <div class="view-switch">
        <button class="nav-button map-button" @click="$router.push('/')">
          <div class="button-content">
            <span class="button-icon">🗺️</span>
            <span class="button-text">返回地图</span>
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
    
    <!-- 背景图片容器 -->
    <div class="background-container">
      <img :src="backgroundImage" alt="背景" class="background-image" />
      <!-- 内容框架 -->
      <div class="content-frame">
        <div class="submission-header">
          <h1>迁徙口述史提交</h1>
          <p>分享您家族的迁徙历史，帮助我们丰富姜姓迁徙溯源数据库</p>
        </div>

        <div class="submission-container">
          <el-card class="submission-card">
            <template #header>
              <div class="card-header">
                <span>迁徙口述史信息</span>
              </div>
            </template>

            <el-form 
              :model="submissionForm" 
              :rules="rules" 
              ref="submissionFormRef"
              label-position="top"
              class="submission-form"
            >
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="分支名称" prop="branch_name">
                    <el-input 
                      v-model="submissionForm.branch_name" 
                      placeholder="请输入分支名称，如：XX堂姜氏"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="姓氏" prop="surname">
                    <el-input 
                      v-model="submissionForm.surname" 
                      placeholder="请输入姓氏"
                      :disabled="true"
                      value="姜"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="迁徙口述史描述" prop="migration_description">
                <el-input
                  v-model="submissionForm.migration_description"
                  type="textarea"
                  :rows="6"
                  placeholder="请详细描述您家族的迁徙历史，包括迁徙原因、关键人物、迁徙路线等信息"
                  maxlength="2000"
                  show-word-limit
                />
              </el-form-item>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="迁徙年代" prop="migration_period">
                    <el-input 
                      v-model="submissionForm.migration_period" 
                      placeholder="如：明朝永乐年间、清朝康熙年间等"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="估算年份" prop="estimated_year">
                    <el-input-number 
                      v-model="submissionForm.estimated_year" 
                      :min="1" 
                      :max="2024"
                      placeholder="如：1403"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="迁徙路线描述" prop="migration_route">
                <el-input
                  v-model="submissionForm.migration_route"
                  type="textarea"
                  :rows="4"
                  placeholder="请描述具体的迁徙路线，如：从XX地迁至XX地，途经XX等地"
                  maxlength="1000"
                  show-word-limit
                />
              </el-form-item>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="迁徙原因" prop="migration_reason">
                    <el-select 
                      v-model="submissionForm.migration_reason" 
                      placeholder="请选择迁徙原因"
                      clearable
                      style="width: 100%"
                    >
                      <el-option label="战乱迁徙" value="战乱迁徙" />
                      <el-option label="饥荒避难" value="饥荒避难" />
                      <el-option label="仕宦任职" value="仕宦任职" />
                      <el-option label="经商贸易" value="经商贸易" />
                      <el-option label="宗族扩张" value="宗族扩张" />
                      <el-option label="政策移民" value="政策移民" />
                      <el-option label="求学深造" value="求学深造" />
                      <el-option label="其他原因" value="其他原因" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="关键人物" prop="key_figures">
                    <el-input 
                      v-model="submissionForm.key_figures" 
                      placeholder="迁徙过程中的关键人物姓名"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="资料来源" prop="source_reference">
                <el-input
                  v-model="submissionForm.source_reference"
                  type="textarea"
                  :rows="3"
                  placeholder="请提供口述史的来源，如：长辈口述、族谱记载、文献资料等"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
            </el-form>

            <div class="form-actions">
              <el-button @click="goBack">返回</el-button>
              <el-button @click="goToAnalytics">数据分析</el-button>
              <el-button @click="resetForm">重置</el-button>
              <el-button type="primary" @click="submitForm" :loading="submitting">
                提交审核
              </el-button>
            </div>
          </el-card>

          <!-- 提交历史 -->
          <el-card class="history-card" v-if="submissionHistory.length > 0">
            <template #header>
              <div class="card-header">
                <span>我的提交历史</span>
              </div>
            </template>

            <el-table 
              :data="submissionHistory" 
              stripe 
              style="width: 100%"
              v-loading="historyLoading"
            >
              <el-table-column prop="branch_name" label="分支名称" width="200" />
              <el-table-column prop="migration_period" label="迁徙年代" width="150" />
              <el-table-column prop="estimated_year" label="估算年份" width="120" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag 
                    :type="getStatusType(row.status)" 
                    size="small"
                  >
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="submitted_at" label="提交时间" width="180" />
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button 
                    size="small" 
                    type="text"
                    @click="viewSubmission(row)"
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="提交详情"
      width="60%"
      :destroy-on-close="true"
    >
      <div class="detail-content">
        <h3>分支信息</h3>
        <p><strong>分支名称：</strong>{{ currentSubmission.branch_name }}</p>
        <p><strong>姓氏：</strong>{{ currentSubmission.surname }}</p>
        
        <h3>迁徙描述</h3>
        <p><strong>口述史描述：</strong>{{ currentSubmission.migration_description }}</p>
        <p><strong>迁徙年代：</strong>{{ currentSubmission.migration_period || '未知' }}</p>
        <p><strong>估算年份：</strong>{{ currentSubmission.estimated_year || '未知' }}</p>
        <p><strong>迁徙路线：</strong>{{ currentSubmission.migration_route || '未知' }}</p>
        <p><strong>迁徙原因：</strong>{{ currentSubmission.migration_reason || '未知' }}</p>
        <p><strong>关键人物：</strong>{{ currentSubmission.key_figures || '未知' }}</p>
        
        <h3>其他信息</h3>
        <p><strong>资料来源：</strong>{{ currentSubmission.source_reference || '未知' }}</p>
        <p><strong>提交时间：</strong>{{ currentSubmission.submitted_at }}</p>
        <p><strong>审核状态：</strong>
          <el-tag :type="getStatusType(currentSubmission.status)">
            {{ getStatusText(currentSubmission.status) }}
          </el-tag>
        </p>
        <p v-if="currentSubmission.review_comment">
          <strong>审核意见：</strong>{{ currentSubmission.review_comment }}
        </p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { submitMigration, getUserMigrationSubmissions } from '@/api/admin'
import { logout } from '@/api/auth'
import backgroundImage from '@/img/background.png'

// 表单数据
const submissionForm = ref({
  branch_name: '',
  surname: '姜',
  migration_description: '',
  migration_period: '',
  estimated_year: null,
  migration_route: '',
  migration_reason: '',
  key_figures: '',
  source_reference: ''
})

// 搜索功能相关
const searchKeyword = ref('')
const filteredMigrations = ref([])

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

// 搜索处理函数
async function handleSearch() {
  // 这里可以添加搜索逻辑，比如过滤提交历史
  console.log('搜索关键词:', searchKeyword.value)
  // 目前只是简单的日志输出，后续可以根据需求扩展
}

// 清除搜索
function handleSearchClear() {
  searchKeyword.value = ''
  console.log('清除搜索')
}

// 添加防抖的搜索函数
const debouncedHandleSearch = debounce(handleSearch, 300)

// 表单验证规则
const rules = ref({
  branch_name: [
    { required: true, message: '请输入分支名称', trigger: 'blur' },
    { min: 2, max: 100, message: '分支名称长度应在2-100个字符之间', trigger: 'blur' }
  ],
  migration_description: [
    { required: true, message: '请输入迁徙口述史描述', trigger: 'blur' },
    { min: 10, max: 2000, message: '描述内容长度应在10-2000个字符之间', trigger: 'blur' }
  ],
  migration_period: [
    { required: true, message: '请输入迁徙年代', trigger: 'blur' },
    { min: 2, max: 100, message: '迁徙年代长度应在2-100个字符之间', trigger: 'blur' }
  ],
  estimated_year: [
    { type: 'number', min: -3000, max: 2025, message: '年份应在公元前3000年到2025年之间', trigger: 'blur' }
  ],
  migration_route: [
    { required: true, message: '请输入迁徙路线', trigger: 'blur' },
    { min: 5, max: 1000, message: '迁徙路线长度应在5-1000个字符之间', trigger: 'blur' }
  ],
  migration_reason: [
    { required: true, message: '请输入迁徙原因', trigger: 'blur' },
    { min: 2, max: 500, message: '迁徙原因长度应在2-500个字符之间', trigger: 'blur' }
  ],
  key_figures: [
    { min: 2, max: 200, message: '关键人物长度应在2-200个字符之间', trigger: 'blur' }
  ],
  source_reference: [
    { required: true, message: '请输入资料来源', trigger: 'blur' },
    { min: 5, max: 500, message: '资料来源长度应在5-500个字符之间', trigger: 'blur' }
  ]
})

// 提交状态
const submitting = ref(false)
const historyLoading = ref(false)
const submissionHistory = ref([])
const detailDialogVisible = ref(false)
const currentSubmission = ref({})

// 表单引用
const submissionFormRef = ref(null)

// 导航函数
const router = useRouter()

// 获取当前用户角色
const isAdmin = computed(() => {
  const userInfoStr = sessionStorage.getItem('userInfo')
  if (!userInfoStr) return false
  try {
    const userInfo = JSON.parse(userInfoStr)
    return userInfo && userInfo.role === 'admin'
  } catch (e) {
    console.error('解析用户信息失败:', e)
    return false
  }
})

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
      console.error('退出登录失败:', error)
    }
  }
}

const goBack = () => {
  router.push('/')
}

const goToAnalytics = () => {
  router.push('/analytics')
}

// 获取提交历史
const loadSubmissionHistory = async () => {
  historyLoading.value = true
  try {
    const data = await getUserMigrationSubmissions()
    submissionHistory.value = data.map(item => ({
      ...item,
      submitted_at: formatDateTime(item.submitted_at),
      reviewed_at: formatDateTime(item.reviewed_at)
    }))
  } catch (error) {
    console.error('获取提交历史失败:', error)
    ElMessage.error(error.message || '获取提交历史失败')
  } finally {
    historyLoading.value = false
  }
}

// 提交表单
const submitForm = async () => {
  if (!submissionFormRef.value) return
  
  try {
    // 验证表单
    await submissionFormRef.value.validate()
    
    // 获取用户ID
    const userInfoStr = sessionStorage.getItem('userInfo')
    if (!userInfoStr) {
      ElMessage.error('用户未登录，请重新登录')
      return
    }
    
    let userInfo
    try {
      userInfo = JSON.parse(userInfoStr)
    } catch (e) {
      ElMessage.error('解析用户信息失败，请重新登录')
      return
    }
    
    if (!userInfo.user_id) {
      ElMessage.error('用户信息不完整，请重新登录')
      return
    }
    
    submitting.value = true
    
    // 准备提交数据，添加用户ID
    const submissionData = {
      ...submissionForm.value,
      user_id: userInfo.user_id
    }
    
    const result = await submitMigration(submissionData)
    
    ElMessage.success(result.message || '提交成功')
    
    // 重置表单
    resetForm()
    
    // 重新加载历史记录
    loadSubmissionHistory()
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message)
    } else if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      console.error('提交失败:', error)
      ElMessage.error('提交失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  submissionFormRef.value?.resetFields()
  submissionForm.value = {
    branch_name: '',
    surname: '姜',
    migration_description: '',
    migration_period: '',
    estimated_year: null,
    migration_route: '',
    migration_reason: '',
    key_figures: '',
    source_reference: ''
  }
}

// 查看提交详情
const viewSubmission = (submission) => {
  currentSubmission.value = submission
  detailDialogVisible.value = true
}

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'approved': return '已通过'
    case 'rejected': return '已拒绝'
    case 'pending': return '待审核'
    default: return status
  }
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

onMounted(() => {
  loadSubmissionHistory()
})
</script>

<style scoped>
.submission-page {
  position: relative;
  min-height: 100vh;
  width: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 */
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

.brand-text strong {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
}

.brand-text small {
  color: #6b7280;
  font-size: 0.85rem;
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

/* 背景图片容器 */
.background-container {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
  width: 100%;
  min-height: 0; /* 确保flex布局正常 */
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.85;
  z-index: 1;
}

/* 内容框架 */
.content-frame {
  position: relative;
  z-index: 2;
  width: 95%;
  max-width: 1200px;
  height: 90%;
  max-height: 900px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(252, 248, 240, 0.98) 100%);
  border-radius: 16px;
  padding: 30px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 8px 24px rgba(0, 0, 0, 0.2),
    inset 0 1px 3px rgba(255, 255, 255, 0.6),
    inset 0 -1px 3px rgba(0, 0, 0, 0.05);
  border: 4px solid #8b7355;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(8px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.content-frame:hover {
  box-shadow: 
    0 24px 72px rgba(0, 0, 0, 0.4),
    0 12px 36px rgba(0, 0, 0, 0.25),
    inset 0 1px 3px rgba(255, 255, 255, 0.6),
    inset 0 -1px 3px rgba(0, 0, 0, 0.05);
  transform: translateY(-4px);
}

.content-frame::before {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  background: linear-gradient(135deg, 
    rgba(139, 115, 85, 1) 0%, 
    rgba(101, 67, 33, 1) 50%, 
    rgba(139, 115, 85, 1) 100%);
  border-radius: 16px;
  z-index: -1;
  box-shadow: 
    inset 0 2px 8px rgba(255, 255, 255, 0.5),
    inset 0 -2px 8px rgba(0, 0, 0, 0.4),
    0 6px 20px rgba(0, 0, 0, 0.3);
}

.content-frame::after {
  content: '';
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  bottom: 12px;
  border: 1px solid rgba(139, 115, 85, 0.3);
  border-radius: 8px;
  pointer-events: none;
}

.submission-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(139, 115, 85, 0.2);
}

.submission-header h1 {
  color: #8b7355;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 12px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
  letter-spacing: -0.5px;
}

.submission-header p {
  color: #a67c52;
  font-size: 1.1rem;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
}

.submission-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
}

.submission-card {
  margin-bottom: 30px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.submission-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.history-card {
  margin-bottom: 30px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.history-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.card-header {
  font-weight: 700;
  color: #8b7355;
  font-size: 1.2rem;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(248, 243, 234, 1) 0%, rgba(240, 234, 224, 1) 100%);
  border-bottom: 2px solid rgba(139, 115, 85, 0.2);
}

.submission-form {
  margin-top: 20px;
}

/* 表单样式优化 */
.submission-form .el-form-item__label {
  color: #8b7355;
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 8px;
}

.submission-form .el-input__wrapper,
.submission-form .el-select__wrapper {
  border-radius: 8px;
  border: 1px solid rgba(139, 115, 85, 0.3);
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
}

.submission-form .el-input__wrapper:hover,
.submission-form .el-select__wrapper:hover {
  border-color: rgba(139, 115, 85, 0.6);
  box-shadow: 0 2px 8px rgba(139, 115, 85, 0.15);
}

.submission-form .el-input__wrapper.is-focus,
.submission-form .el-select__wrapper.is-focus {
  border-color: #8b7355;
  box-shadow: 0 0 0 3px rgba(139, 115, 85, 0.1);
}

.submission-form .el-textarea__inner {
  border-radius: 8px;
  border: 1px solid rgba(139, 115, 85, 0.3);
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  min-height: 120px;
}

.submission-form .el-textarea__inner:hover {
  border-color: rgba(139, 115, 85, 0.6);
  box-shadow: 0 2px 8px rgba(139, 115, 85, 0.15);
}

.submission-form .el-textarea__inner:focus {
  border-color: #8b7355;
  box-shadow: 0 0 0 3px rgba(139, 115, 85, 0.1);
}

.submission-form .el-input-number__decrease,
.submission-form .el-input-number__increase {
  border-color: rgba(139, 115, 85, 0.3);
  background: rgba(248, 243, 234, 0.8);
  color: #8b7355;
}

.submission-form .el-input-number__decrease:hover,
.submission-form .el-input-number__increase:hover {
  background: rgba(139, 115, 85, 0.1);
  color: #6b5532;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 2px solid rgba(139, 115, 85, 0.1);
  background: rgba(248, 243, 234, 0.6);
  padding: 24px 20px;
  border-radius: 0 0 12px 12px;
  margin: 30px -20px -20px -20px;
}

.form-actions .el-button {
  min-width: 100px;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.form-actions .el-button--primary {
  background: linear-gradient(135deg, #8b7355 0%, #6b5532 100%);
  border-color: #8b7355;
}

.form-actions .el-button--primary:hover {
  background: linear-gradient(135deg, #6b5532 0%, #5b4522 100%);
  border-color: #6b5532;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.3);
}

.detail-content h3 {
  margin: 20px 0 12px 0;
  color: #8b7355;
  font-size: 1.3rem;
  font-weight: 700;
  padding-bottom: 6px;
  border-bottom: 2px solid rgba(139, 115, 85, 0.2);
}

.detail-content p {
  margin: 8px 0;
  line-height: 1.8;
  color: #555;
  font-size: 0.95rem;
}

.detail-content strong {
  color: #8b7355;
  min-width: 100px;
  display: inline-block;
  font-weight: 600;
}

/* 表格样式优化 */
.history-card .el-table {
  border-radius: 8px;
  overflow: hidden;
}

.history-card .el-table__header-wrapper th {
  background: linear-gradient(135deg, rgba(248, 243, 234, 1) 0%, rgba(240, 234, 224, 1) 100%);
  color: #8b7355;
  font-weight: 700;
  border-bottom: 2px solid rgba(139, 115, 85, 0.3);
}

.history-card .el-table__body-wrapper td {
  color: #555;
  border-bottom: 1px solid rgba(139, 115, 85, 0.1);
}

.history-card .el-table__body-wrapper tr:hover > td {
  background-color: rgba(248, 243, 234, 0.8);
}

/* 滚动条样式 */
.submission-container::-webkit-scrollbar {
  width: 8px;
}

.submission-container::-webkit-scrollbar-track {
  background: rgba(248, 243, 234, 0.8);
  border-radius: 4px;
}

.submission-container::-webkit-scrollbar-thumb {
  background: rgba(139, 115, 85, 0.5);
  border-radius: 4px;
}

.submission-container::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 115, 85, 0.7);
}
</style>