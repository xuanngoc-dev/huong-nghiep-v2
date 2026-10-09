<template>
  <el-drawer
    :model-value="modelValue"
    title="Cấu hình"
    direction="rtl"
    size="380px"
    append-to-body
    class="settings-drawer"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="settings">
      <section class="settings__section">
        <h3>Giao diện</h3>

        <div class="setting-field">
          <span class="setting-field__label">Màu chủ đạo</span>
          <div class="color-row">
            <button
              v-for="preset in PRIMARY_PRESETS"
              :key="preset.value"
              type="button"
              class="color-swatch"
              :class="{ 'is-active': sameColor(primaryColor, preset.value) }"
              :style="{ background: preset.value }"
              :title="preset.label"
              :aria-label="preset.label"
              @click="primaryColor = preset.value"
            />
            <el-color-picker v-model="primaryColor" color-format="hex" :predefine="presetColors" />
          </div>
        </div>

        <div class="setting-field">
          <span class="setting-field__label">Phông chữ</span>
          <el-select v-model="fontFamily" class="setting-control">
            <el-option
              v-for="font in FONT_OPTIONS"
              :key="font.value"
              :label="font.label"
              :value="font.value"
              :style="{ fontFamily: font.stack }"
            />
          </el-select>
        </div>

        <div class="setting-field">
          <div class="setting-field__label">
            <span>Cỡ chữ</span>
            <strong>{{ fontSize }}px</strong>
          </div>
          <el-slider v-model="fontSize" :min="13" :max="18" :step="1" show-stops />
        </div>

        <div class="preview" :style="previewStyle">
          <p>Định hướng nghề — mẫu chữ và màu</p>
          <el-button type="primary">Nút màu chủ đạo</el-button>
        </div>
      </section>

      <section class="settings__section">
        <h3>Bố cục</h3>
        <div class="switch-row">
          <span>Cố định thanh trên</span>
          <el-switch v-model="navbarFixed" />
        </div>
        <div class="switch-row">
          <span>Cố định menu trái</span>
          <el-switch v-model="sidebarFixed" />
        </div>
        <div class="switch-row">
          <span>Menu đẩy nội dung</span>
          <el-switch v-model="sidebarPushContent" />
        </div>
        <div class="switch-row">
          <span>Hiện tiêu đề nhóm</span>
          <el-switch v-model="menuGroupHeaderVisible" />
        </div>
        <div class="switch-row">
          <span>Thu gọn nhóm menu</span>
          <el-switch v-model="menuGroupCollapsible" />
        </div>
        <div class="switch-row">
          <span>Chỉ mở một nhóm</span>
          <el-switch v-model="menuUniqueOpened" />
        </div>
      </section>
    </div>

    <template #footer>
      <el-button class="reset-btn" @click="onReset">Đặt lại mặc định</el-button>
    </template>
  </el-drawer>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessageBox } from 'element-plus'
import { useLayoutStore } from '@/stores/layout'
import { FONT_OPTIONS, PRIMARY_PRESETS, fontStack } from '@/utils/theme'

defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const layoutStore = useLayoutStore()
const {
  primaryColor,
  fontFamily,
  fontSize,
  navbarFixed,
  sidebarFixed,
  sidebarPushContent,
  menuGroupHeaderVisible,
  menuGroupCollapsible,
  menuUniqueOpened,
} = storeToRefs(layoutStore)

const presetColors = PRIMARY_PRESETS.map((item) => item.value)

const previewStyle = computed(() => ({
  fontFamily: fontStack(fontFamily.value),
  fontSize: `${fontSize.value}px`,
}))

function sameColor(left, right) {
  return String(left || '').toLowerCase() === String(right || '').toLowerCase()
}

async function onReset() {
  try {
    await ElMessageBox.confirm(
      'Đưa màu, phông chữ, cỡ chữ và bố cục về mặc định?',
      'Đặt lại cấu hình',
      {
        confirmButtonText: 'Đặt lại',
        cancelButtonText: 'Hủy',
        type: 'warning',
      },
    )
  } catch {
    return
  }
  layoutStore.reset()
}
</script>

<style scoped lang="scss">
.settings {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.settings__section {
  display: flex;
  flex-direction: column;
  gap: 16px;

  h3 {
    margin: 0;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--layout-text-muted, var(--el-text-color-regular));
  }
}

.setting-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-field__label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.setting-control {
  width: 100%;
}

.color-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.color-swatch {
  width: 28px;
  height: 28px;
  padding: 0;
  border: 1px solid color-mix(in srgb, var(--el-text-color-primary) 25%, transparent);
  border-radius: 50%;
  cursor: pointer;

  &.is-active {
    outline: 2px solid var(--el-text-color-primary);
    outline-offset: 2px;
  }
}

.preview {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--el-border-color);
  border-radius: 10px;
  background: var(--el-fill-color-light);

  p {
    margin: 0;
    color: var(--el-text-color-primary);
  }
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 32px;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.reset-btn {
  width: 100%;
}
</style>
