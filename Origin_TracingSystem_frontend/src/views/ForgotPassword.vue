<template>
  <div class="forgot-password-page">
    <div class="forgot-password-container">
      <div class="header">
        <h2>🔐 密码找回</h2>
        <p>通过管理员重置密码</p>
      </div>

      <!-- 步骤条 -->
      <el-steps :active="currentStep" finish-status="success" simple>
        <el-step title="填写信息" />
        <el-step title="等待审核" />
        <el-step title="重置完成" />
      </el-steps>

      <!-- 步骤1：填写申请信息 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="form.username" 
              placeholder="请输入您的用户名"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item label="重置原因" prop="reason">
            <el-input 
              v-model="form.reason" 
              type="textarea" 
              :rows="3"
              placeholder="请简要说明需要重置密码的原因（如：忘记密码、密码泄露等）"
            />
          </el-form-item>

          <el-alert
            title="提示"
            type="info"
            :closable="false"
            show-icon
            class="info-alert"
          >
            <p>提交申请后，管理员会在24小时内处理您的请求。</p>
            <p>重置后的新密码将通过系统通知告知您。</p>
          </el-alert>

          <div class="form-actions">
            <el-button @click="goToLogin">返回登录</el-button>
            <el-button type="primary" @click="submitRequest" :loading="submitting">
              提交申请
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- 步骤2：等待审核 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="status-display">
          <el-result
            icon="info"
            title="申请已提交"
            sub-title="您的密码重置申请已提交，请耐心等待管理员处理"
          >
            <template #extra>
              <div class="status-details">
                <p><strong>申请时间：</strong>{{ requestInfo.requested_at }}</p>
                <p><strong>当前状态：</strong>
                  <el-tag type="warning">待处理</el-tag>
                </p>
                <p v-if="requestInfo.reason"><strong>申请原因：</strong>{{ requestInfo.reason }}</p>
              </div>
              
              <div class="action-buttons">
                <el-button @click="goToLogin">返回登录</el-button>
                <el-button type="primary" @click="checkStatus">刷新状态</el-button>
              </div>
            </template>
          </el-result>
        </div>
      </div>

      <!-- 步骤3：处理结果 -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="status-display">
          <!-- 已批准 -->
          <el-result
            v-if="requestInfo.status === 'approved'"
            icon="success"
            title="密码已重置"
            :sub-title="`您的新密码是：${requestInfo.new_password}，请尽快登录并修改密码`"
          >
            <template #extra>
              <div class="status-details">
                <p><strong>处理时间：</strong>{{ requestInfo.reviewed_at }}</p>
                <p v-if="requestInfo.review_comment"><strong>管理员备注：</strong>{{ requestInfo.review_comment }}</p>
              </div>
              <el-button type="primary" @click="goToLogin">立即登录</el-button>
            </template>
          </el-result>

          <!-- 已拒绝 -->
          <el-result
            v-else-if="requestInfo.status === 'rejected'"
            icon="error"
            title="申请被拒绝"
            sub-title="您的密码重置申请未通过审核"
          >
            <template #extra>
              <div class="status-details">
                <p><strong>处理时间：</strong>{{ requestInfo.reviewed_at }}</p>
                <p v-if="requestInfo.review_comment"><strong>拒绝原因：</strong>{{ requestInfo.review_comment }}</p>
              </div>
              <div class="action-buttons">
                <el-button @click="goToLogin">返回登录</el-button>
                <el-button type="primary" @click="resetForm">重新申请</el-button>
              </div>
            </template>
          </el-result>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { requestPasswordReset, checkPasswordResetStatus } from '@/api/auth'

const router = useRouter()
const formRef = ref(null)
const currentStep = ref(0)
const submitting = ref(false)
const requestInfo = ref({})

const form = reactive({
  username: '',
  reason: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请输入重置原因', trigger: 'blur' },
    { min: 5, max: 200, message: '长度在 5 到 200 个字符', trigger: 'blur' }
  ]
}

// 提交密码重置申请
const submitRequest = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    const response = await requestPasswordReset(form.username, form.reason)
    
    ElMessage.success(response.message)
    
    // 保存申请信息
    requestInfo.value = {
      username: form.username,
      reason: form.reason,
      requested_at: response.data.requested_at,
      status: 'pending'
    }
    
    // 进入下一步
    currentStep.value = 1
  } catch (error) {
    ElMessage.error(error.message || '提交申请失败')
  } finally {
    submitting.value = false
  }
}

// 查询申请状态
const checkStatus = async () => {
  try {
    const data = await checkPasswordResetStatus(requestInfo.value.username)
    
    if (data.has_request) {
      requestInfo.value = {
        ...requestInfo.value,
        ...data
      }
      
      // 如果已处理，进入结果页面
      if (data.status === 'approved' || data.status === 'rejected') {
        currentStep.value = 2
      }
      
      ElMessage.success('状态已更新')
    }
  } catch (error) {
    ElMessage.error(error.message || '查询状态失败')
  }
}

// 重置表单
const resetForm = () => {
  form.username = ''
  form.reason = ''
  requestInfo.value = {}
  currentStep.value = 0
}

// 返回登录页
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.forgot-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.forgot-password-container {
  width: 100%;
  max-width: 600px;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 28px;
}

.header p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.step-content {
  margin-top: 30px;
}

.info-alert {
  margin: 20px 0;
}

.info-alert p {
  margin: 5px 0;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}

.status-display {
  padding: 20px 0;
}

.status-details {
  text-align: left;
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.status-details p {
  margin: 10px 0;
  color: #606266;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

:deep(.el-result__extra) {
  width: 100%;
}
</style>
