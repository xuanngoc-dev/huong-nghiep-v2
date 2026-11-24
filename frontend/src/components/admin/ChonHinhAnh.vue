<template>
  <div v-loading="dangTai" class="chon-hinh-anh">
    <div class="chon-hinh-anh__xem-truoc" aria-label="Xem trước hình ảnh">
      <img v-if="model && !anhLoi" :src="apiAssetUrl(model)" :alt="alt" @error="anhLoi = true" />
      <span v-else>{{ anhLoi ? 'Không tải được ảnh' : 'Chưa có ảnh' }}</span>
    </div>
    <div class="chon-hinh-anh__nhap">
      <CustomInput
        v-model="model"
        maxlength="500"
        :placeholder="placeholder"
        clearable
        @input="anhLoi = false"
      />
      <div class="chon-hinh-anh__thao-tac">
        <CustomButton type="primary" plain :loading="dangTai" @click="chonTep">
          <CustomIcon><Upload /></CustomIcon>
          <span>Tải ảnh lên</span>
        </CustomButton>
        <CustomButton v-if="model" link type="danger" @click="boAnh">Bỏ ảnh</CustomButton>
        <span class="chon-hinh-anh__goi-y">PNG, JPG, WEBP hoặc GIF, tối đa {{ toiDaMb }}MB.</span>
      </div>
      <input ref="tepInput" type="file" :accept="LOAI_ANH.join(',')" hidden @change="onChonTep" />
    </div>
  </div>
</template>

<script setup>
/**
 * ChonHinhAnh — ô chọn hình ảnh: dán URL hoặc tải ảnh từ thiết bị lên Thư viện (thư mục `thuMuc`).
 * v-model là URL tuyệt đối hoặc đường dẫn tệp thư viện (hiển thị qua apiAssetUrl).
 */
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { apiAssetUrl } from '@/api/apiUrl'
import { uploadThuVienTaoThuMuc } from '@/api/thuVien'

defineOptions({ name: 'ChonHinhAnh' })

const LOAI_ANH = ['image/png', 'image/jpeg', 'image/webp', 'image/gif']

const props = defineProps({
  /** Thư mục trong Thư viện để lưu ảnh tải lên; chưa có thì tự tạo. */
  thuMuc: { type: String, required: true },
  toiDaMb: { type: Number, default: 2 },
  alt: { type: String, default: 'Xem trước hình ảnh' },
  placeholder: { type: String, default: 'Dán URL hình ảnh, ví dụ https://…/anh.jpg' },
})

const model = defineModel({ type: String, default: '' })

const tepInput = ref(null)
const dangTai = ref(false)
const anhLoi = ref(false)

watch(model, () => {
  anhLoi.value = false
})

function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

function chonTep() {
  tepInput.value?.click()
}

async function onChonTep(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (!LOAI_ANH.includes(file.type)) {
    ElMessage.error('Chỉ nhận ảnh PNG, JPG, WEBP hoặc GIF')
    return
  }
  if (file.size > props.toiDaMb * 1024 * 1024) {
    ElMessage.error(`Ảnh tối đa ${props.toiDaMb}MB`)
    return
  }
  dangTai.value = true
  try {
    const item = await uploadThuVienTaoThuMuc(file, props.thuMuc)
    model.value = item.duong_dan
    ElMessage.success('Đã tải ảnh lên')
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được ảnh lên'))
  } finally {
    dangTai.value = false
  }
}

function boAnh() {
  model.value = ''
}
</script>

<style scoped>
.chon-hinh-anh {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  background: var(--el-fill-color-lighter);
}

.chon-hinh-anh__xem-truoc {
  display: flex;
  flex: 0 0 160px;
  align-items: center;
  justify-content: center;
  height: 100px;
  padding: 4px;
  overflow: hidden;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  background: #fff;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  text-align: center;
}

.chon-hinh-anh__xem-truoc img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.chon-hinh-anh__nhap {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.chon-hinh-anh__thao-tac {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
}

.chon-hinh-anh__thao-tac :deep(.el-button + .el-button) {
  margin-left: 0;
}

.chon-hinh-anh__goi-y {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.4;
}

/* Khung hẹp (mobile, dialog kéo nhỏ): ảnh xem trước nằm trên, ô nhập bên dưới. */
@media (max-width: 575.98px) {
  .chon-hinh-anh {
    align-items: stretch;
    flex-direction: column;
  }

  .chon-hinh-anh__xem-truoc {
    flex-basis: auto;
    height: 140px;
  }
}
</style>
