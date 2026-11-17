<template>
  <CustomDialog v-model="visible" title="Xác nhận xóa" width="640px" append-to-body @closed="onClosed">
    <div v-loading="dangTai" class="xac-nhan">
      <p class="xac-nhan__cau-hoi">
        <CustomIcon class="xac-nhan__icon"><WarningFilled /></CustomIcon>
        <span>
          {{ tieuDe }}?
          <template v-if="dong.length">Thao tác này sẽ xóa luôn các dữ liệu liên quan dưới đây.</template>
        </span>
      </p>

      <template v-if="dong.length">
        <CustomTable :data="dong" border size="small" class="xac-nhan__bang">
          <CustomTableColumn label="Dữ liệu" min-width="160" prop="du_lieu" />
          <CustomTableColumn label="Số lượng" width="100" align="right">
            <template #default="{ row }">
              <strong>{{ Number(row.so_luong).toLocaleString('vi-VN') }}</strong>
            </template>
          </CustomTableColumn>
          <CustomTableColumn label="Ghi chú" min-width="200" prop="ghi_chu" />
        </CustomTable>
        <p class="xac-nhan__canh-bao">Dữ liệu đã xóa không thể khôi phục.</p>
      </template>
    </div>

    <template #footer>
      <CustomButton @click="visible = false">Hủy</CustomButton>
      <CustomButton type="danger" :disabled="dangTai" @click="dongY">
        {{ dong.length ? 'Đồng ý xóa tất cả' : 'Xóa' }}
      </CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/**
 * Dialog xác nhận xóa, xem trước dữ liệu liên quan sẽ bị xóa kèm (dạng bảng).
 *
 * Dùng: `const ketQua = await xacNhanRef.value.mo({ tieuDe, taiAnhHuong, dongLienQuan })`
 * - `taiAnhHuong()`: gọi API xem trước số lượng (anh-huong-xoa);
 * - `dongLienQuan(anhHuong)`: các dòng `{ du_lieu, so_luong, ghi_chu }` của bảng; mảng rỗng = không có gì liên quan.
 * Trả `null` nếu hủy / không xem trước được, ngược lại `{ xoaLienQuan }` để gửi kèm lệnh xóa.
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const visible = ref(false)
const dangTai = ref(false)
const tieuDe = ref('')
const dong = ref([])
let traLoi = null

async function mo({ tieuDe: tieuDeMoi, taiAnhHuong, dongLienQuan }) {
  traLoi?.(null)
  tieuDe.value = tieuDeMoi
  dong.value = []
  dangTai.value = true
  visible.value = true
  const ketQua = new Promise((resolve) => {
    traLoi = resolve
  })
  try {
    dong.value = dongLienQuan(await taiAnhHuong())
  } catch (error) {
    const detail = error?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Không kiểm tra được dữ liệu liên quan')
    visible.value = false
  } finally {
    dangTai.value = false
  }
  return ketQua
}

function dongY() {
  traLoi?.({ xoaLienQuan: dong.value.length > 0 })
  traLoi = null
  visible.value = false
}

// Đóng dialog bằng Hủy / dấu X / Esc đều là hủy; đồng ý thì đã trả lời trước khi đóng.
function onClosed() {
  traLoi?.(null)
  traLoi = null
}

defineExpose({ mo })
</script>

<style scoped>
.xac-nhan {
  min-height: 60px;
}

.xac-nhan__cau-hoi {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 0 0 12px;
  line-height: 1.5;
}

.xac-nhan__icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: var(--el-color-warning);
  font-size: 20px;
}

.xac-nhan__canh-bao {
  margin: 12px 0 0;
  color: var(--el-color-danger);
}
</style>
