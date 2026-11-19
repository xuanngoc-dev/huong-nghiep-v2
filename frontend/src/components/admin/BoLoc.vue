<template>
  <CustomRow ref="hang" class="bo-loc" :gutter="gutter">
    <template v-for="(o, i) in oLoc()" :key="o.key ?? i">
      <component :is="o" v-if="laCol(o)" />
      <CustomCol v-else v-bind="laRong(o) ? cotRong : cot">
        <component :is="o" />
      </CustomCol>
    </template>
    <CustomCol v-if="$slots.nut" ref="nut" class="bo-loc__nut">
      <slot name="nut" />
    </CustomCol>
  </CustomRow>
</template>

<script setup>
/**
 * BoLoc — bộ lọc của các màn quản trị, dựng bằng CustomRow/CustomCol (lưới 24 cột của Element Plus).
 * Mỗi ô lọc trong slot mặc định được bọc vào CustomCol với span theo breakpoint ở prop `cot`
 * (mặc định 2 → 3 → 4 → 6 ô/hàng). Ô có class `bo-loc__rong` (khoảng ngày, khoảng giá) dùng `cotRong`.
 * Ô cần span riêng thì tự bọc <CustomCol ...> trong slot, BoLoc giữ nguyên.
 * Nút (slot #nut) đứng ngay sau ô cuối nếu còn chỗ trên hàng; bị đẩy xuống hàng mới thì căn giữa.
 */
import { Comment, Fragment, onBeforeUnmount, onMounted, ref, useSlots } from 'vue'

defineOptions({ name: 'BoLoc' })

defineProps({
  cot: { type: Object, default: () => ({ xs: 12, sm: 8, md: 6, lg: 4 }) },
  cotRong: { type: Object, default: () => ({ xs: 24, sm: 16, md: 12, lg: 8 }) },
  gutter: { type: Number, default: 12 },
})

const slots = useSlots()
const hang = ref(null)
const nut = ref(null)
let quanSat = null

// Trải phẳng slot (v-for sinh Fragment, v-if false sinh Comment) thành danh sách ô lọc.
function trai(vnodes) {
  return vnodes.flatMap((o) => {
    if (o.type === Fragment) return trai(o.children || [])
    if (o.type === Comment) return []
    return [o]
  })
}

function oLoc() {
  return trai(slots.default?.() || [])
}

function laCol(o) {
  return o.type?.name === 'CustomCol'
}

function laRong(o) {
  return /\bbo-loc__rong\b/.test(String(o.props?.class || ''))
}

// Bỏ class trước khi đo: nút đang giãn hết hàng thì luôn nằm hàng riêng, đo vậy sẽ sai.
function kiemTraXuongHang() {
  const el = nut.value?.$el
  if (!el) return
  el.classList.remove('is-xuong-hang')
  const truoc = el.previousElementSibling
  const xuongHang = !!truoc && el.getBoundingClientRect().top >= truoc.getBoundingClientRect().bottom - 1
  el.classList.toggle('is-xuong-hang', xuongHang)
}

onMounted(() => {
  kiemTraXuongHang()
  quanSat = new ResizeObserver(kiemTraXuongHang)
  quanSat.observe(hang.value.$el)
})

onBeforeUnmount(() => quanSat?.disconnect())
</script>

<style scoped>
.bo-loc {
  row-gap: 12px;
  align-items: center;
}

/* Ô lọc giãn hết bề rộng cột. */
.bo-loc :deep(.el-col > .el-input),
.bo-loc :deep(.el-col > .el-select),
.bo-loc :deep(.el-col > .el-input-number),
.bo-loc :deep(.el-col > .el-date-editor) {
  width: 100%;
}

/* Cột nút rộng theo nội dung (đè span 24 mặc định của el-col). */
.bo-loc__nut.el-col {
  display: flex;
  flex: 0 0 auto;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  max-width: none;
}

.bo-loc__nut.el-col.is-xuong-hang {
  flex-basis: 100%;
  justify-content: center;
}

.bo-loc__nut :deep(.el-button + .el-button) {
  margin-left: 0;
}
</style>
