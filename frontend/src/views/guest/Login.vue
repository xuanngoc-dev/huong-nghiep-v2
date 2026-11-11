<script setup>
import { onUnmounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { mountGuestBootstrap, unmountGuestBootstrap } from '@/layouts/guest/bootstrap'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

// Trang đăng nhập/đăng ký nằm ngoài GuestLayout nên tự nạp CSS Bootstrap.
mountGuestBootstrap()
onUnmounted(unmountGuestBootstrap)

const formRef = ref()
const submitting = ref(false)
const form = reactive({
  email: '',
  mat_khau: '',
})

function safePath(value) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//')) return ''
  if (value === '/login' || value.startsWith('/login?') || value === '/register' || value.startsWith('/register?')) {
    return ''
  }
  return value
}

function destinationAfterLogin(isAdmin, redirect) {
  const requested = safePath(redirect)
  if (isAdmin) {
    return requested.startsWith('/admin') ? requested : '/admin'
  }
  return requested && !requested.startsWith('/admin') ? requested : '/member'
}

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
    await router.replace(destinationAfterLogin(auth.isAdmin, route.query.redirect))
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Đăng nhập thất bại')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-page container-fluid d-flex align-items-center">
    <div class="row justify-content-center flex-grow-1">
      <div class="col-12 col-sm-9 col-md-7 col-lg-5 col-xl-4 col-xxl-3">
        <el-card class="auth-card w-100" shadow="hover">
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
            <RouterLink :to="{ name: 'register', query: route.query.redirect ? { redirect: route.query.redirect } : {} }">
              Đăng ký
            </RouterLink>
          </p>
        </el-card>
      </div>
    </div>
  </div>
</template>
