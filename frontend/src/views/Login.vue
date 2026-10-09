<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formRef = ref()
const submitting = ref(false)
const form = reactive({
  email: '',
  mat_khau: '',
})

const rules = {
  email: [
    { required: true, message: 'Vui lòng nhập email', trigger: 'blur' },
    { type: 'email', message: 'Email không hợp lệ', trigger: 'blur' },
  ],
  mat_khau: [{ required: true, message: 'Vui lòng nhập mật khẩu', trigger: 'blur' }],
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await auth.login(form)
    ElMessage.success('Đăng nhập thành công')
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.replace(redirect || '/')
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Đăng nhập thất bại')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="hover">
      <div class="auth-brand">
        <el-icon :size="28" color="var(--el-color-primary)"><Monitor /></el-icon>
        <h1>Đăng nhập</h1>
        <p>Chào mừng trở lại Định hướng nghề</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        size="large"
        @submit.prevent="onSubmit"
      >
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" placeholder="you@example.com" clearable>
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="Mật khẩu" prop="mat_khau">
          <el-input
            v-model="form.mat_khau"
            type="password"
            placeholder="Nhập mật khẩu"
            show-password
            clearable
            @keyup.enter="onSubmit"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-button type="primary" class="submit-btn" :loading="submitting" @click="onSubmit">
          Đăng nhập
        </el-button>
      </el-form>

      <p class="auth-footer">
        Chưa có tài khoản?
        <RouterLink to="/register">Đăng ký</RouterLink>
      </p>
    </el-card>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100svh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(31, 122, 77, 0.12), transparent 40%),
    var(--el-bg-color-page);
}

.auth-card {
  width: min(420px, 100%);
  border-radius: 16px;
}

.auth-brand {
  text-align: center;
  margin-bottom: 24px;
}

.auth-brand h1 {
  margin: 12px 0 4px;
  font-size: 28px;
}

.auth-brand p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.submit-btn {
  width: 100%;
  margin-top: 8px;
}

.auth-footer {
  margin: 20px 0 0;
  text-align: center;
  color: var(--el-text-color-secondary);
}
</style>
