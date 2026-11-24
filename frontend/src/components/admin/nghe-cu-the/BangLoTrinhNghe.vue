<template>
  <CustomTable :data="modelValue" class="bang-lo-trinh">
    <CustomTableColumn label="#" width="48" align="center">
      <template #default="{ $index }">{{ $index + 1 }}</template>
    </CustomTableColumn>
    <CustomTableColumn label="Giai đoạn" min-width="180">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.giai_doan"
          maxlength="255"
          placeholder="Ví dụ: Thợ phụ"
          aria-label="Giai đoạn"
          @update:model-value="capNhat($index, 'giai_doan', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Mô tả công việc" min-width="240">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.mo_ta_cong_viec"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          maxlength="2000"
          placeholder="Công việc ở giai đoạn này"
          aria-label="Mô tả công việc"
          @update:model-value="capNhat($index, 'mo_ta_cong_viec', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Lương TB từ" min-width="140">
      <template #default="{ row, $index }">
        <MoneyInput
          :model-value="row.luong_trung_binh_min"
          placeholder="VND"
          aria-label="Lương trung bình từ"
          @update:model-value="capNhat($index, 'luong_trung_binh_min', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Lương TB đến" min-width="140">
      <template #default="{ row, $index }">
        <MoneyInput
          :model-value="row.luong_trung_binh_max"
          placeholder="VND"
          aria-label="Lương trung bình đến"
          @update:model-value="capNhat($index, 'luong_trung_binh_max', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Ghi chú" min-width="180">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.ghi_chu"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          maxlength="1000"
          placeholder="Ghi chú thêm (nếu có)"
          aria-label="Ghi chú"
          @update:model-value="capNhat($index, 'ghi_chu', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Thao tác" width="132" align="center">
      <template #default="{ $index }">
        <div class="bang-lo-trinh__action">
          <CustomButton link type="primary" aria-label="Lên" :disabled="$index === 0" @click="doiCho($index, -1)">
            <CustomIcon><Top /></CustomIcon>
          </CustomButton>
          <CustomButton
            link
            type="primary"
            aria-label="Xuống"
            :disabled="$index === modelValue.length - 1"
            @click="doiCho($index, 1)"
          >
            <CustomIcon><Bottom /></CustomIcon>
          </CustomButton>
          <CustomButton
            v-if="$index === modelValue.length - 1"
            link
            type="primary"
            aria-label="Thêm giai đoạn"
            @click="themDong"
          >
            <CustomIcon><Plus /></CustomIcon>
          </CustomButton>
          <CustomButton link type="danger" aria-label="Xóa" @click="xoaDong($index)">
            <CustomIcon><Delete /></CustomIcon>
          </CustomButton>
        </div>
      </template>
    </CustomTableColumn>
    <template #empty>
      <div class="bang-lo-trinh__empty">
        <CustomButton type="primary" link aria-label="Thêm giai đoạn" @click="themDong">
          <CustomIcon><Plus /></CustomIcon>
          <span>Thêm giai đoạn</span>
        </CustomButton>
      </div>
    </template>
  </CustomTable>
</template>

<script setup>
/**
 * Bảng nhập lộ trình phát triển của nghề cụ thể (khu quản trị): mỗi dòng một giai đoạn theo thứ tự,
 * gồm tên giai đoạn, mô tả công việc, lương trung bình (VND, từ – đến) và ghi chú.
 */
import { Bottom, Delete, Plus, Top } from '@element-plus/icons-vue'
import { buocLoTrinhRong } from './truongNghe'

defineOptions({ name: 'BangLoTrinhNghe' })

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

function capNhat(index, key, value) {
  emit(
    'update:modelValue',
    props.modelValue.map((item, i) => (i === index ? { ...item, [key]: value } : { ...item })),
  )
}

function themDong() {
  emit('update:modelValue', [...props.modelValue.map((item) => ({ ...item })), buocLoTrinhRong()])
}

function xoaDong(index) {
  emit(
    'update:modelValue',
    props.modelValue.filter((_, i) => i !== index).map((item) => ({ ...item })),
  )
}

function doiCho(index, buoc) {
  const ds = props.modelValue.map((item) => ({ ...item }))
  const dich = index + buoc
  if (dich < 0 || dich >= ds.length) return
  ;[ds[index], ds[dich]] = [ds[dich], ds[index]]
  emit('update:modelValue', ds)
}
</script>

<style scoped>
.bang-lo-trinh {
  width: 100%;
  font-size: var(--app-font-size);
  font-weight: 400;
}

.bang-lo-trinh :deep(th.el-table__cell),
.bang-lo-trinh :deep(td.el-table__cell),
.bang-lo-trinh :deep(.cell) {
  font-size: var(--app-font-size);
  font-weight: 400;
}

.bang-lo-trinh__action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.bang-lo-trinh__action :deep(.el-button) {
  margin: 0;
  padding: 4px;
}

.bang-lo-trinh__action :deep(.el-icon) {
  font-size: 18px;
}

.bang-lo-trinh__empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  font-size: var(--app-font-size);
}
</style>
