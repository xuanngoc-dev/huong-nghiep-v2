import { computed, onBeforeUnmount, onMounted, ref, unref, useAttrs } from 'vue'

/**
 * Breakpoint compact cho form controls — khớp CustomTable / BulkActionBar.
 * max-width 767px ≈ dưới 768px.
 */
export const COMPONENT_MOBILE_MQ = '(max-width: 767px)'

/**
 * Theo dõi viewport mobile qua matchMedia.
 * @param {string} [mq]
 */
export function useIsMobile(mq = COMPONENT_MOBILE_MQ) {
  const isMobile = ref(false)
  let mediaQuery = null

  function sync() {
    isMobile.value = !!mediaQuery?.matches
  }

  onMounted(() => {
    mediaQuery = window.matchMedia(mq)
    sync()
    mediaQuery.addEventListener('change', sync)
  })

  onBeforeUnmount(() => {
    mediaQuery?.removeEventListener('change', sync)
    mediaQuery = null
  })

  return isMobile
}

/**
 * Size Element Plus: desktop mặc định; mobile → `small`.
 * Ưu tiên: attrs.size (truyền tường minh) > inherited > mobile small > undefined.
 *
 * @param {{ inherited?: import('vue').MaybeRefOrGetter<string|undefined>, mobileSize?: string, mq?: string }} [options]
 */
export function useResponsiveComponentSize(options = {}) {
  const attrs = useAttrs()
  const isMobile = useIsMobile(options.mq)
  const mobileSize = options.mobileSize ?? 'small'

  const resolvedSize = computed(() => {
    const explicit = attrs.size
    if (explicit != null && explicit !== '') return explicit

    const fromParent = unref(options.inherited)
    if (fromParent != null && fromParent !== '') return fromParent

    if (isMobile.value) return mobileSize
    return undefined
  })

  return { isMobile, resolvedSize }
}
