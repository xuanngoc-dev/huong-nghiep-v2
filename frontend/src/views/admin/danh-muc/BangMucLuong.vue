<template>
  <CustomTable :data="modelValue" class="cap-table">
    <CustomTableColumn label="Kinh nghiệm" min-width="160">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.name"
          maxlength="255"
          placeholder="Ví dụ: 1 năm"
          aria-label="Kinh nghiệm"
          @update:model-value="capNhat($index, 'name', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Từ" min-width="110">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.min"
          inputmode="decimal"
          placeholder="10"
          aria-label="Lương từ"
          @update:model-value="capNhatSo($index, 'min', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Đến" min-width="110">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.max"
          inputmode="decimal"
          placeholder="15"
          aria-label="Lương đến"
          @update:model-value="capNhatSo($index, 'max', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Thời gian" min-width="130">
      <template #default="{ row, $index }">
        <CustomSelect
          :model-value="row.period || KY_LUONG_MAC_DINH"
          aria-label="Thời gian"
          @update:model-value="capNhat($index, 'period', $event)"
        >
          <CustomOption
            v-for="item in kyOptions(row.period)"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </CustomSelect>
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Đơn vị tính" min-width="140">
      <template #default="{ row, $index }">
        <CustomSelect
          :model-value="row.unit || DON_VI_TIEN_MAC_DINH"
          aria-label="Đơn vị tính"
          @update:model-value="capNhat($index, 'unit', $event)"
        >
          <CustomOption
            v-for="item in donViOptions(row.unit)"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </CustomSelect>
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Thao tác" width="96" align="center">
      <template #default="{ $index }">
        <div class="cap-table__action">
          <CustomButton
            v-if="$index === modelValue.length - 1"
            link
            type="primary"
            aria-label="Thêm dòng"
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
      <div class="cap-table__empty">
        <span>Không có dữ liệu</span>
        <CustomButton type="primary" link aria-label="Thêm dòng" @click="themDong">
          <CustomIcon><Plus /></CustomIcon>
        </CustomButton>
      </div>
    </template>
  </CustomTable>
</template>

<script setup>
import { DON_VI_TIEN, DON_VI_TIEN_MAC_DINH } from '@/constants/donViTien'
import { KY_LUONG, KY_LUONG_MAC_DINH } from '@/constants/kyLuong'

defineOptions({ name: 'BangMucLuong' })

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

function dongTrong() {
  return { name: '', min: '', max: '', unit: DON_VI_TIEN_MAC_DINH, period: KY_LUONG_MAC_DINH }
}

function capNhat(index, key, value) {
  const next = props.modelValue.map((item, i) => (i === index ? { ...item, [key]: value } : { ...item }))
  emit('update:modelValue', next)
}

function capNhatSo(index, key, value) {
  capNhat(index, key, locSoTien(value))
}

function themDong() {
  emit('update:modelValue', [...props.modelValue.map((item) => ({ ...item })), dongTrong()])
}

function xoaDong(index) {
  emit(
    'update:modelValue',
    props.modelValue.filter((_, i) => i !== index).map((item) => ({ ...item })),
  )
}

/** Chỉ giữ số không âm: chữ số và một dấu thập phân, không giới hạn độ dài. */
function locSoTien(value) {
  const cleaned = String(value ?? '').replace(',', '.').replace(/[^\d.]/g, '')
  const dot = cleaned.indexOf('.')
  const head = dot === -1 ? cleaned : cleaned.slice(0, dot)
  const intPart = head.replace(/^0+(?=\d)/, '')
  if (dot === -1) return intPart
  const decimal = cleaned.slice(dot + 1).replace(/\./g, '')
  return `${intPart || '0'}.${decimal}`
}

function donViOptions(current) {
  if (current && !DON_VI_TIEN.some((item) => item.value === current)) {
    return [...DON_VI_TIEN, { value: current, label: current }]
  }
  return DON_VI_TIEN
}

function kyOptions(current) {
  if (current && !KY_LUONG.some((item) => item.value === current)) {
    return [...KY_LUONG, { value: current, label: current }]
  }
  return KY_LUONG
}
</script>

<style scoped>
.cap-table {
  width: 100%;
  font-size: var(--app-font-size);
  font-weight: 400;
}

.cap-table :deep(th.el-table__cell),
.cap-table :deep(td.el-table__cell),
.cap-table :deep(.cell) {
  font-size: var(--app-font-size);
  font-weight: 400;
}

.cap-table :deep(.el-select) {
  width: 100%;
}

.cap-table__action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.cap-table__action :deep(.el-button) {
  margin: 0;
  padding: 4px;
}

.cap-table__action :deep(.el-icon) {
  font-size: 18px;
}

.cap-table__empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--el-text-color-secondary);
  font-size: var(--app-font-size);
  font-weight: 400;
}
</style>
