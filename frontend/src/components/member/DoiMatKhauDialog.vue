<template>
  <CustomDialog v-model="visible" title="Đổi mật khẩu" width="480px" @closed="datLai">
    <CustomForm ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top" @submit.prevent="onSubmit">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__full" label="Mật khẩu hiện tại" prop="mat_khau_cu">
          <CustomInput v-model="form.mat_khau_cu" placeholder="Nhập mật khẩu hiện tại" type="password" show-password maxlength="128" autocomplete="current-password" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Mật khẩu mới" prop="mat_khau_moi">
          <CustomInput v-model="form.mat_khau_moi" placeholder="Nhập mật khẩu mới (ít nhất 6 ký tự)" type="password" show-password maxlength="128" autocomplete="new-password" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Nhập lại mật khẩu mới" prop="nhap_lai">
          <CustomInput v-model="form.nhap_lai" placeholder="Nhập lại mật khẩu mới" type="password" show-password maxlength="128" autocomplete="new-password" />
        </CustomFormItem>
      </div>
      <!-- Nút submit ẩn để Enter trong ô nhập gửi form. -->
      <button type="submit" hidden />
    </CustomForm>
    <template #footer>
      <CustomButton @click="visible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" @click="onSubmit">Đổi mật khẩu</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/**
 * Dialog đổi mật khẩu của tài khoản đang đăng nhập (POST /tai-khoan/doi-mat-khau). Dùng: `<DoiMatKhauDialog v-model="mo" />`.
 * Đóng dialog thì xóa các ô đã nhập.
 */
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { doiMatKhau } from '@/api/hoSo'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['success'])

const formRef = ref()
const saving = ref(false)
const form = reactive({ mat_khau_cu: '', mat_khau_moi: '', nhap_lai: '' })

const rules = {
  mat_khau_cu: [{ required: true, message: 'Vui lòng nhập mật khẩu hiện tại', trigger: 'blur' }],
  mat_khau_moi: [
    { required: true, message: 'Vui lòng nhập mật khẩu mới', trigger: 'blur' },
    { min: 6, message: 'Mật khẩu mới phải có ít nhất 6 ký tự', trigger: 'blur' },
    {
      validator: (_rule, value, callback) =>
        value && value === form.mat_khau_cu ? callback(new Error('Mật khẩu mới phải khác mật khẩu hiện tại')) : callback(),
      trigger: 'blur',
    },
  ],
  nhap_lai: [
    { required: true, message: 'Vui lòng nhập lại mật khẩu mới', trigger: 'blur' },
    {
      validator: (_rule, value, callback) =>
        value !== form.mat_khau_moi ? callback(new Error('Mật khẩu nhập lại không khớp')) : callback(),
      trigger: 'blur',
    },
  ],
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function datLai() {
  formRef.value?.resetFields()
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await doiMatKhau({ mat_khau_cu: form.mat_khau_cu, mat_khau_moi: form.mat_khau_moi })
    ElMessage.success('Đã đổi mật khẩu')
    emit('success')
    visible.value = false
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không đổi được mật khẩu'))
  } finally {
    saving.value = false
  }
}
</script>
