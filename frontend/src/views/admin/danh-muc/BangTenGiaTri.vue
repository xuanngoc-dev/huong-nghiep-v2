<script setup>
defineOptions({ name: 'BangTenGiaTri' })

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  nameLabel: { type: String, required: true },
  valueLabel: { type: String, required: true },
  namePlaceholder: { type: String, default: '' },
  valuePlaceholder: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

function capNhat(index, key, value) {
  const next = props.modelValue.map((item, i) => (i === index ? { ...item, [key]: value } : { ...item }))
  emit('update:modelValue', next)
}

function themDong() {
  emit('update:modelValue', [...props.modelValue.map((item) => ({ ...item })), { name: '', value: '', ghi_chu: '' }])
}

function xoaDong(index) {
  emit(
    'update:modelValue',
    props.modelValue.filter((_, i) => i !== index).map((item) => ({ ...item })),
  )
}
</script>

<template>
  <CustomTable :data="modelValue" class="cap-table">
    <CustomTableColumn :label="nameLabel" min-width="180">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.name"
          maxlength="255"
          :placeholder="namePlaceholder"
          :aria-label="nameLabel"
          @update:model-value="capNhat($index, 'name', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn :label="valueLabel" min-width="220">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.value"
          maxlength="2000"
          :placeholder="valuePlaceholder"
          :aria-label="valueLabel"
          @update:model-value="capNhat($index, 'value', $event)"
        />
      </template>
    </CustomTableColumn>
    <CustomTableColumn label="Ghi chú" min-width="180">
      <template #default="{ row, $index }">
        <CustomInput
          :model-value="row.ghi_chu"
          maxlength="2000"
          placeholder="Ghi chú thêm (nếu có)"
          aria-label="Ghi chú"
          @update:model-value="capNhat($index, 'ghi_chu', $event)"
        />
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
        <!-- <span>Không có dữ liệu</span> -->
        <CustomButton type="primary" link aria-label="Thêm dòng" @click="themDong">
          <CustomIcon><Plus /></CustomIcon>
        </CustomButton>
      </div>
    </template>
  </CustomTable>
</template>

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
  /* min-height: 72px; */
  color: var(--el-text-color-secondary);
  font-size: var(--app-font-size);
  font-weight: 400;
}
</style>
