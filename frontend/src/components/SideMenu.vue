<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="collapsed"
    router
    class="side-menu"
  >
    <div
      v-for="(group, groupIndex) in menuGroups"
      :key="group.header || `group-${groupIndex}`"
      class="menu-group"
      :class="{ 'is-collapsible': isGroupCollapsible(group) }"
    >
      <button
        v-if="showGroupHeader(group) && layoutStore.menuGroupCollapsible"
        type="button"
        class="menu-group__toggle"
        :class="{ 'is-collapsed': collapsed }"
        :tabindex="collapsed ? -1 : undefined"
        @click="!collapsed && toggleGroup(groupIndex)"
      >
        <el-tooltip
          :content="group.header"
          placement="right"
          :disabled="!collapsed"
          :show-after="200"
        >
          <span class="menu-group__face">
            <span class="menu-group__abbr">{{ group.abbr || groupAbbr(group.header) }}</span>
            <span class="menu-group__header">{{ group.header }}</span>
          </span>
        </el-tooltip>
        <el-icon
          class="menu-group__arrow"
          :class="{ 'is-open': isGroupOpen(groupIndex) }"
        >
          <ArrowDown />
        </el-icon>
      </button>

      <div
        v-else-if="showGroupHeader(group)"
        class="menu-group__header menu-group__header--static"
        :class="{ 'is-collapsed': collapsed }"
      >
        <el-tooltip
          :content="group.header"
          placement="right"
          :disabled="!collapsed"
          :show-after="200"
        >
          <span class="menu-group__face">
            <span class="menu-group__abbr">{{ group.abbr || groupAbbr(group.header) }}</span>
            <span class="menu-group__title">{{ group.header }}</span>
          </span>
        </el-tooltip>
      </div>

      <div
        v-show="!showGroupHeader(group) || !layoutStore.menuGroupCollapsible || isGroupOpen(groupIndex) || collapsed"
        class="menu-group__items"
      >
        <template v-for="item in group.items" :key="item.index">
          <el-tooltip
            :content="item.title"
            placement="right"
            :disabled="!collapsed"
            :show-after="280"
          >
            <el-menu-item :index="item.index">
              <el-icon>
                <component :is="resolveIcon(item.icon)" />
              </el-icon>
              <span class="menu-label" :class="{ 'is-hidden': collapsed }">{{ item.title }}</span>
            </el-menu-item>
          </el-tooltip>
        </template>
      </div>
    </div>
  </el-menu>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as Icons from '@element-plus/icons-vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useLayoutStore } from '@/stores/layout'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const route = useRoute()
const authStore = useAuthStore()
const layoutStore = useLayoutStore()

const menuGroups = computed(() => authStore.menuGroups)
const activeMenu = computed(() => route.path)
const collapsed = computed(() => props.collapsed)
const openGroups = ref(new Set())

function initOpenGroups() {
  const next = new Set()
  menuGroups.value.forEach((group, index) => {
    if (!group.header) return
    const hasActive = group.items?.some((item) => item.index === route.path)
    if (hasActive || !layoutStore.menuGroupCollapsible) {
      next.add(index)
    }
  })
  if (layoutStore.menuGroupCollapsible && next.size === 0) {
    const first = menuGroups.value.findIndex((g) => g.header)
    if (first >= 0) next.add(first)
  }
  openGroups.value = next
}

initOpenGroups()

watch(menuGroups, () => initOpenGroups(), { deep: true })

watch(
  () => layoutStore.menuGroupCollapsible,
  (enabled) => {
    if (!enabled) {
      openGroups.value = new Set(menuGroups.value.map((_, i) => i))
    } else {
      initOpenGroups()
    }
  },
)

watch(
  () => route.path,
  () => {
    if (!layoutStore.menuGroupCollapsible) return
    const activeIndex = menuGroups.value.findIndex((group) =>
      group.items?.some((item) => item.index === route.path),
    )
    if (activeIndex < 0) return
    if (layoutStore.menuUniqueOpened) {
      openGroups.value = new Set([activeIndex])
    } else {
      const next = new Set(openGroups.value)
      next.add(activeIndex)
      openGroups.value = next
    }
  },
)

function isGroupCollapsible(group) {
  return !!(
    group.header &&
    layoutStore.menuGroupHeaderVisible &&
    layoutStore.menuGroupCollapsible
  )
}

function showGroupHeader(group) {
  return !!(group.header && layoutStore.menuGroupHeaderVisible)
}

function groupAbbr(header) {
  const words = String(header || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
  if (!words.length) return ''
  if (words.length === 1) return words[0].slice(0, 3).toUpperCase()
  return words
    .map((w) => w.charAt(0))
    .join('')
    .slice(0, 3)
    .toUpperCase()
}

function isGroupOpen(groupIndex) {
  return openGroups.value.has(groupIndex)
}

function toggleGroup(groupIndex) {
  const next = new Set(layoutStore.menuUniqueOpened ? [] : openGroups.value)
  if (openGroups.value.has(groupIndex) && !layoutStore.menuUniqueOpened) {
    next.delete(groupIndex)
  } else if (!(openGroups.value.has(groupIndex) && layoutStore.menuUniqueOpened)) {
    next.add(groupIndex)
  }
  openGroups.value = next
}

function resolveIcon(name) {
  return Icons[name] || Icons.Menu
}
</script>

<style scoped lang="scss">
.side-menu {
  border-right: none;
  width: 100%;
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 40px;
    line-height: 40px;
    transition: padding 0.28s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s ease;
  }

  .menu-label {
    display: inline-block;
    max-width: 180px;
    opacity: 1;
    white-space: nowrap;
    overflow: hidden;
    vertical-align: middle;
    transition:
      opacity 0.2s ease 0.05s,
      max-width 0.28s cubic-bezier(0.4, 0, 0.2, 1);

    &.is-hidden {
      max-width: 0;
      opacity: 0;
      margin: 0;
      transition:
        opacity 0.12s ease,
        max-width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    }
  }

  &.el-menu--collapse {
    width: 64px;

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      padding: 0 !important;
      justify-content: center;
    }

    :deep(.el-menu-item .el-icon),
    :deep(.el-sub-menu__title .el-icon) {
      margin: 0;
      width: 24px;
      text-align: center;
    }

    :deep(.el-menu-item span),
    :deep(.el-sub-menu__title span),
    :deep(.el-sub-menu__icon-arrow) {
      display: none !important;
      width: 0;
      height: 0;
      overflow: hidden;
      visibility: hidden;
    }
  }
}

.menu-group {
  & + & {
    margin-top: 4px;
  }

  &__face {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 0;
    max-width: 100%;
  }

  &__abbr {
    display: none;
    flex-shrink: 0;
    min-width: 28px;
    padding: 2px 0;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.04em;
    line-height: 1;
    text-align: center;
    color: var(--el-text-color-secondary);
    user-select: none;
  }

  &__title {
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__toggle {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    min-height: 35px;
    padding: 14px 16px 6px 20px;
    border: none;
    background: transparent;
    cursor: pointer;
    color: inherit;
    text-align: left;
    box-sizing: border-box;

    &:hover:not(.is-collapsed) .menu-group__header {
      color: var(--el-color-primary);
    }

    &.is-collapsed {
      justify-content: center;
      padding: 10px 0 6px;
      cursor: default;

      .menu-group__abbr {
        display: inline-block;
      }

      .menu-group__header,
      .menu-group__arrow {
        display: none;
      }
    }
  }

  &__header {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: var(--el-text-color-secondary);
    line-height: 1.2;
    user-select: none;
    transition: color 0.15s ease;

    &--static {
      display: flex;
      align-items: center;
      min-height: 35px;
      padding: 16px 20px 6px;
      overflow: hidden;
      white-space: nowrap;
      box-sizing: border-box;

      &.is-collapsed {
        justify-content: center;
        padding: 10px 0 6px;

        .menu-group__abbr {
          display: inline-block;
        }

        .menu-group__title {
          display: none;
        }
      }
    }
  }

  &__arrow {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    transition: transform 0.2s ease;
    flex-shrink: 0;

    &.is-open {
      transform: rotate(180deg);
    }
  }
}
</style>
