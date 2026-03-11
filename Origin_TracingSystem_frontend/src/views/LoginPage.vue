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
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 400px;
}

.login-box h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.toggle-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.toggle-btn {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.toggle-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.toggle-btn:hover:not(.active) {
  border-color: #667eea;
}

.login-form {
  margin-top: 20px;
}

.tips {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
  font-size: 12px;
  color: #999;
}

.tips p {
  margin: 5px 0;
}
</style>
