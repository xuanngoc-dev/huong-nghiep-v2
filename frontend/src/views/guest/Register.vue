<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref()
const submitting = ref(false)
const form = reactive({
  ho_ten: '',
  email: '',
  so_dien_thoai: '',
  mat_khau: '',
  xac_nhan_mat_khau: '',
})

const rules = {
  ho_ten: [
    { required: true, message: 'Vui lòng nhập họ tên', trigger: 'blur' },
    { min: 2, message: 'Họ tên phải có ít nhất 2 ký tự', trigger: 'blur' },
  ],
  email: [
    { required: true, message: 'Vui lòng nhập email', trigger: 'blur' },
    { type: 'email', message: 'Email không hợp lệ', trigger: 'blur' },
  ],
  so_dien_thoai: [
    {
      validator: (_rule, value, callback) => {
        if (!value) return callback()
        if (!/^[0-9+\-\s]{8,20}$/.test(value)) {
          return callback(new Error('Số điện thoại không hợp lệ'))
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  mat_khau: [
    { required: true, message: 'Vui lòng nhập mật khẩu', trigger: 'blur' },
    { min: 6, message: 'Mật khẩu tối thiểu 6 ký tự', trigger: 'blur' },
  ],
  xac_nhan_mat_khau: [
    { required: true, message: 'Vui lòng xác nhận mật khẩu', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.mat_khau) {
          callback(new Error('Mật khẩu xác nhận không khớp'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await auth.register({
      ho_ten: form.ho_ten.trim(),
      email: form.email.trim(),
      so_dien_thoai: form.so_dien_thoai.trim() || null,
      mat_khau: form.mat_khau,
    })
    ElMessage.success('Đăng ký thành công')
    await router.replace('/')
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Đăng ký thất bại')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="hover">
      <div class="auth-brand">
        <el-icon :size="28" color="var(--el-color-primary)"><UserFilled /></el-icon>
        <h1>Đăng ký</h1>
        <p>Tạo tài khoản Định hướng nghề</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        size="large"
        @submit.prevent="onSubmit"
      >
        <el-form-item label="Họ tên" prop="ho_ten">
          <el-input v-model="form.ho_ten" placeholder="Nguyễn Văn A" clearable />
        </el-form-item>

        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" placeholder="you@example.com" clearable />
        </el-form-item>

        <el-form-item label="Số điện thoại" prop="so_dien_thoai">
          <el-input v-model="form.so_dien_thoai" placeholder="Tùy chọn" clearable />
        </el-form-item>

        <el-form-item label="Mật khẩu" prop="mat_khau">
          <el-input
            v-model="form.mat_khau"
            type="password"
            placeholder="Tối thiểu 6 ký tự"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item label="Xác nhận mật khẩu" prop="xac_nhan_mat_khau">
          <el-input
            v-model="form.xac_nhan_mat_khau"
            type="password"
            placeholder="Nhập lại mật khẩu"
            show-password
            clearable
            @keyup.enter="onSubmit"
          />
        </el-form-item>

        <el-button type="primary" class="submit-btn" :loading="submitting" @click="onSubmit">
          Tạo tài khoản
        </el-button>
      </el-form>

      <p class="auth-footer">
        Đã có tài khoản?
        <RouterLink to="/login">Đăng nhập</RouterLink>
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
    radial-gradient(circle at top right, rgba(31, 122, 77, 0.12), transparent 40%),
    var(--el-bg-color-page);
}

.auth-card {
  width: min(480px, 100%);
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
