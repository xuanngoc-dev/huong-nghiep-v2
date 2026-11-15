<template>
  <el-card v-loading="loading" shadow="never" class="profile-card">
    <template #header>
      <div>
        <h1 class="profile-card__title">Thông tin cá nhân</h1>
        <p class="profile-card__lead">
          Họ tên, liên hệ và diện ưu tiên tuyển sinh của bạn. Hồ sơ học tập cập nhật ở mục Hồ sơ năng lực.
        </p>
      </div>
    </template>

    <CustomForm ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top" @submit.prevent="onSubmit">
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Họ tên" prop="ho_ten">
          <CustomInput v-model="form.ho_ten" maxlength="150" placeholder="Nguyễn Văn A" clearable />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Email">
          <CustomInput :model-value="email" disabled />
        </CustomFormItem>
        <CustomFormItem label="Số điện thoại" prop="so_dien_thoai">
          <CustomInput v-model="form.so_dien_thoai" maxlength="20" placeholder="Tùy chọn" clearable />
        </CustomFormItem>
        <CustomFormItem label="Giới tính">
          <CustomSelect v-model="form.gioi_tinh" placeholder="Chọn" clearable>
            <CustomOption v-for="item in GIOI_TINH" :key="item.value" :label="item.label" :value="item.value" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Ngày sinh">
          <CustomDatePicker
            v-model="form.ngay_sinh"
            type="date"
            value-format="YYYY-MM-DD"
            format="DD/MM/YYYY"
            placeholder="Chọn ngày"
            clearable
            :disabled-date="disableFutureDate"
          />
        </CustomFormItem>
        <CustomFormItem label="Tỉnh thành">
          <CustomSelect v-model="form.tinh_thanh_id" placeholder="Chọn" clearable filterable>
            <CustomOption v-for="item in provinceOptions" :key="item.id" :label="item.ten_tinh" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Dân tộc">
          <CustomSelect v-model="form.dan_toc" placeholder="Chọn" clearable filterable allow-create default-first-option>
            <CustomOption v-for="item in ethnicSelectOptions" :key="item" :label="item" :value="item" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Tôn giáo">
          <CustomSelect v-model="form.ton_giao" placeholder="Chọn" clearable filterable allow-create default-first-option>
            <CustomOption v-for="item in religionSelectOptions" :key="item" :label="item" :value="item" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Khu vực ưu tiên">
          <CustomSelect v-model="form.khu_vuc_uu_tien_id" placeholder="Chọn" clearable filterable>
            <CustomOption v-for="item in khuVucSelectOptions" :key="item.id" :label="item.label" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Đối tượng ưu tiên">
          <CustomSelect v-model="form.doi_tuong_uu_tien_id" placeholder="Chọn" clearable filterable>
            <CustomOption v-for="item in doiTuongSelectOptions" :key="item.id" :label="item.label" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
      </div>

      <div class="profile-actions">
        <CustomButton native-type="button" :disabled="loading || saving" @click="load">Hoàn tác</CustomButton>
        <CustomButton type="primary" :loading="saving" @click="onSubmit">Lưu thông tin</CustomButton>
      </div>
    </CustomForm>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchDanToc } from '@/api/danToc'
import { fetchDoiTuongUuTien } from '@/api/doiTuongUuTien'
import { fetchHoSo, updateThongTinCaNhan } from '@/api/hoSo'
import { fetchKhuVucUuTien } from '@/api/khuVucUuTien'
import { fetchTinhThanh } from '@/api/tinhThanh'
import { fetchTonGiao } from '@/api/tonGiao'
import { useAuthStore } from '@/stores/auth'
import { storeHoSo } from '@/utils/hoSoCache'

const GIOI_TINH = [
  { value: 1, label: 'Nam' },
  { value: 2, label: 'Nữ' },
  { value: 3, label: 'Khác' },
]

const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)
const email = ref('')
const provinceOptions = ref([])
const ethnicOptions = ref([])
const religionOptions = ref([])
const khuVucRows = ref([])
const doiTuongRows = ref([])

const form = reactive({
  ho_ten: '',
  so_dien_thoai: '',
  gioi_tinh: null,
  ngay_sinh: '',
  dan_toc: null,
  ton_giao: null,
  tinh_thanh_id: null,
  khu_vuc_uu_tien_id: null,
  doi_tuong_uu_tien_id: null,
})

const rules = {
  ho_ten: [
    { required: true, message: 'Vui lòng nhập họ tên', trigger: 'blur' },
    { min: 2, message: 'Họ tên phải có ít nhất 2 ký tự', trigger: 'blur' },
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
}

// Giữ giá trị đang lưu trong lựa chọn kể cả khi danh mục không còn mục đó.
function withCurrent(options, current) {
  const value = String(current || '').trim()
  if (!value || options.includes(value)) return options
  return [value, ...options]
}

const ethnicSelectOptions = computed(() => withCurrent(ethnicOptions.value, form.dan_toc))
const religionSelectOptions = computed(() => withCurrent(religionOptions.value, form.ton_giao))
const khuVucSelectOptions = computed(() =>
  khuVucRows.value
    .filter((item) => item.trang_thai === 1 || item.id === form.khu_vuc_uu_tien_id)
    .sort((a, b) => a.ten_khu_vuc.localeCompare(b.ten_khu_vuc, 'vi'))
    .map((item) => ({ id: item.id, label: `${item.ten_khu_vuc} (${item.ma_khu_vuc})` })),
)
const doiTuongSelectOptions = computed(() =>
  doiTuongRows.value
    .filter((item) => item.trang_thai === 1 || item.id === form.doi_tuong_uu_tien_id)
    .sort((a, b) => a.ten_doi_tuong.localeCompare(b.ten_doi_tuong, 'vi'))
    .map((item) => ({ id: item.id, label: `${item.ten_doi_tuong} (${item.ma_doi_tuong})` })),
)

function blank(value) {
  const cleaned = String(value ?? '').trim()
  return cleaned || null
}

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function disableFutureDate(value) {
  const today = new Date()
  today.setHours(23, 59, 59, 999)
  return value.getTime() > today.getTime()
}

async function loadAll(fetchFn) {
  const size = 100
  let current = 1
  const items = []
  while (current <= 20) {
    const data = await fetchFn({ page: current, page_size: size })
    items.push(...(data.items || []))
    if (items.length >= data.total || !data.items?.length) break
    current += 1
  }
  return items
}

function applyProfile(data) {
  email.value = data.email || ''
  form.ho_ten = data.ho_ten || ''
  form.so_dien_thoai = data.so_dien_thoai || ''
  form.gioi_tinh = data.gioi_tinh ?? null
  form.ngay_sinh = data.ngay_sinh || ''
  form.dan_toc = data.dan_toc || null
  form.ton_giao = data.ton_giao || null
  form.tinh_thanh_id = data.tinh_thanh_id ?? null
  form.khu_vuc_uu_tien_id = data.khu_vuc_uu_tien_id ?? null
  form.doi_tuong_uu_tien_id = data.doi_tuong_uu_tien_id ?? null
  formRef.value?.clearValidate()
}

async function load() {
  loading.value = true
  try {
    const [profile, provinces, ethnics, religions, areas, priorities] = await Promise.all([
      fetchHoSo(),
      loadAll(fetchTinhThanh),
      loadAll(fetchDanToc),
      loadAll(fetchTonGiao),
      loadAll(fetchKhuVucUuTien),
      loadAll(fetchDoiTuongUuTien),
    ])
    provinceOptions.value = provinces
      .filter((item) => item.trang_thai === 1 || item.id === profile.tinh_thanh_id)
      .sort((a, b) => a.ten_tinh.localeCompare(b.ten_tinh, 'vi'))
    ethnicOptions.value = ethnics
      .filter((item) => item.trang_thai === 1)
      .map((item) => item.ten_dan_toc)
      .sort((a, b) => a.localeCompare(b, 'vi'))
    religionOptions.value = religions
      .filter((item) => item.trang_thai === 1)
      .map((item) => item.ten_ton_giao)
      .sort((a, b) => a.localeCompare(b, 'vi'))
    khuVucRows.value = areas
    doiTuongRows.value = priorities
    applyProfile(profile)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được thông tin cá nhân'))
  } finally {
    loading.value = false
  }
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const data = await updateThongTinCaNhan({
      ho_ten: form.ho_ten.trim(),
      so_dien_thoai: blank(form.so_dien_thoai),
      gioi_tinh: form.gioi_tinh ?? null,
      ngay_sinh: form.ngay_sinh || null,
      dan_toc: blank(form.dan_toc),
      ton_giao: blank(form.ton_giao),
      tinh_thanh_id: form.tinh_thanh_id ?? null,
      khu_vuc_uu_tien_id: form.khu_vuc_uu_tien_id ?? null,
      doi_tuong_uu_tien_id: form.doi_tuong_uu_tien_id ?? null,
    })
    applyProfile(data)
    if (auth.user) {
      auth.setUser({ ...auth.user, ho_ten: data.ho_ten, so_dien_thoai: data.so_dien_thoai })
      storeHoSo(auth.user.id, data)
    }
    ElMessage.success('Đã cập nhật thông tin cá nhân')
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được thông tin cá nhân'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.profile-card {
  border-radius: 12px;
}

.profile-card__title {
  margin: 0 0 4px;
  font-size: 20px;
  line-height: 1.4;
}

.profile-card__lead {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.4;
}

.profile-actions {
  padding-top: 8px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
