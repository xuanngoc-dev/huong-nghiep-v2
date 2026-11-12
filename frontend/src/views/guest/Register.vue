<template>
  <AuthShell
    :image="bannerImage"
    title="Bắt đầu khám phá bản thân miễn phí"
    text="Tạo tài khoản để lưu kết quả trắc nghiệm và nhận gợi ý định hướng phù hợp với bạn."
    :highlights="['Trắc nghiệm Holland RIASEC', 'Lưu hồ sơ và lịch sử trắc nghiệm', 'Gợi ý lộ trình học tập, nghề nghiệp']"
  >
    <div class="auth-brand">
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
        <el-input v-model="form.ho_ten" placeholder="Nguyễn Văn A" clearable>
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="Email" prop="email">
        <el-input v-model="form.email" placeholder="you@example.com" clearable>
          <template #prefix>
            <el-icon><Message /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="Số điện thoại" prop="so_dien_thoai">
        <el-input v-model="form.so_dien_thoai" placeholder="Tùy chọn" clearable>
          <template #prefix>
            <el-icon><Iphone /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <div class="row gx-3">
        <div class="col-sm-6">
          <el-form-item label="Mật khẩu" prop="mat_khau">
            <el-input
              v-model="form.mat_khau"
              type="password"
              placeholder="Ít nhất 6 ký tự"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </div>
        <div class="col-sm-6">
          <el-form-item label="Xác nhận mật khẩu" prop="xac_nhan_mat_khau">
            <el-input
              v-model="form.xac_nhan_mat_khau"
              type="password"
              placeholder="Nhập lại"
              show-password
              @keyup.enter="onSubmit"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </div>
      </div>

      <el-button type="primary" class="submit-btn" :loading="submitting" @click="onSubmit">
        Tạo tài khoản
        <el-icon aria-hidden="true"><Right /></el-icon>
      </el-button>
    </el-form>

    <p class="auth-footer">
      Đã có tài khoản?
      <RouterLink :to="{ name: 'login', query: route.query.redirect ? { redirect: route.query.redirect } : {} }">
        Đăng nhập
      </RouterLink>
    </p>
  </AuthShell>
</template>

<script setup>
import { onUnmounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { mountGuestBootstrap, unmountGuestBootstrap } from '@/layouts/guest/bootstrap'
import AuthShell from '@/components/guest/auth/AuthShell.vue'
import bannerImage from '@/assets/guest/thcs.jpg'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

// Trang đăng nhập/đăng ký nằm ngoài GuestLayout nên tự nạp CSS Bootstrap.
mountGuestBootstrap()
onUnmounted(unmountGuestBootstrap)

function safePath(value) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//')) return ''
  if (value === '/login' || value.startsWith('/login?') || value === '/register' || value.startsWith('/register?')) {
    return ''
  }
  return value
}

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
    await router.replace(safePath(route.query.redirect) || '/member')
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Đăng ký thất bại')
  } finally {
    submitting.value = false
  }
}
</script>
