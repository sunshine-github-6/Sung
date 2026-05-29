<template>
  <div class="login-page">
    <div class="login-box">
      <h1>🌐 姜姓迁徙溯源系统</h1>
      
      <!-- 切换按钮 -->
      <div class="toggle-buttons">
        <button 
          :class="['toggle-btn', { active: !isRegister }]"
          @click="isRegister = false"
        >
          登录
        </button>
        <button 
          :class="['toggle-btn', { active: isRegister }]"
          @click="isRegister = true"
        >
          注册
        </button>
      </div>
      
      <!-- 登录表单 -->
      <el-form v-if="!isRegister" :model="loginForm" class="login-form">
        <el-form-item>
          <el-input 
            v-model="loginForm.username" 
            placeholder="用户名"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="loginForm.password" 
            type="password"
            placeholder="密码"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button 
          type="primary" 
          @click="handleLogin"
          :loading="loading"
          size="large"
          style="width: 100%"
        >
          登录
        </el-button>
      </el-form>
      
      <!-- 注册表单 -->
      <el-form v-else :model="registerForm" class="login-form">
        <el-form-item>
          <el-input 
            v-model="registerForm.username" 
            placeholder="用户名"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="registerForm.password" 
            type="password"
            placeholder="密码"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password"
            placeholder="确认密码"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="registerForm.phone" 
            placeholder="电话号码（可选）"
            size="large"
          />
        </el-form-item>
        <el-button 
          type="primary" 
          @click="handleRegister"
          :loading="loading"
          size="large"
          style="width: 100%"
        >
          注册
        </el-button>
      </el-form>
      
      <div class="tips" v-if="!isRegister">
        <p>默认管理员账号: admin / admin</p>
        <p>默认用户账号: user / user</p>
        <p><el-link type="primary" @click="goToForgotPassword">忘记密码？</el-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, register } from '@/api/auth'

const router = useRouter()
const isRegister = ref(false)
const loginForm = ref({
  username: '',
  password: ''
})
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  phone: ''
})
const loading = ref(false)

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  
  loading.value = true
  try {
    const result = await login(loginForm.value.username, loginForm.value.password)
    // 后端目前没有返回token，使用user_id作为标识
    sessionStorage.setItem('token', result.user_id.toString())
    sessionStorage.setItem('userInfo', JSON.stringify(result))
    
    ElMessage.success('登录成功')
    
    // 根据角色跳转
    if (result.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/')
    }
  } catch (error) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    ElMessage.warning('两次密码输入不一致')
    return
  }

  loading.value = true
  try {
    await register({
      username: registerForm.value.username,
      password: registerForm.value.password,
      phone: registerForm.value.phone
    })

    ElMessage.success('注册成功，请登录')
    isRegister.value = false
    loginForm.value.username = registerForm.value.username
    loginForm.value.password = ''
    registerForm.value = {
      username: '',
      password: '',
      confirmPassword: '',
      phone: ''
    }
  } catch (error) {
    ElMessage.error(error.message || '注册失败')
  } finally {
    loading.value = false
  }
}

const goToForgotPassword = () => {
  router.push('/forgot-password')
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(165deg, #fbf9f7 0%, #f5f3f0 50%, #ede9e3 100%);
  position: relative;
  overflow: hidden;
}

/* 微妙的背景纹理 */
.login-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  opacity: 0.025;
  pointer-events: none;
}

/* 装饰性渐变光晕 */
.login-page::after {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(196, 112, 90, 0.08) 0%, transparent 70%);
  top: -200px;
  right: -200px;
  pointer-events: none;
}

.login-box {
  background: rgba(255, 255, 255, 0.92);
  padding: 56px 48px;
  border-radius: 24px;
  box-shadow: 
    0 4px 6px -2px rgba(0, 0, 0, 0.02),
    0 10px 15px -3px rgba(0, 0, 0, 0.03),
    0 20px 40px -10px rgba(0, 0, 0, 0.04);
  width: 440px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
}

.login-box h1 {
  text-align: center;
  margin-bottom: 40px;
  color: #1a1a1a;
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.toggle-buttons {
  display: flex;
  gap: 4px;
  margin-bottom: 32px;
  background: #f5f3f0;
  padding: 4px;
  border-radius: 12px;
}

.toggle-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease-out;
  font-size: 14px;
  font-weight: 500;
  color: #6b6b6b;
  letter-spacing: 0.01em;
}

.toggle-btn.active {
  background: #ffffff;
  color: #1a1a1a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.toggle-btn:hover:not(.active) {
  color: #4a4a4a;
}

.login-form {
  margin-top: 32px;
}

.tips {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  text-align: center;
  font-size: 13px;
  color: #8a8a8a;
}

.tips p {
  margin: 8px 0;
  line-height: 1.6;
}

/* 响应式调整 - 保持桌面端优先 */
@media (max-width: 480px) {
  .login-box {
    width: 90%;
    padding: 40px 32px;
    margin: 20px;
    border-radius: 20px;
  }
  
  .login-box h1 {
    font-size: 24px;
  }
}
</style>
