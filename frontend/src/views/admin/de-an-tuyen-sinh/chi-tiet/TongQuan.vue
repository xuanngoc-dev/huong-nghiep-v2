<script setup>
import { computed } from 'vue'
import { STATUS_LABELS, formatDate, formatQuota } from './format'

const props = defineProps({
  deAn: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const schoolLabel = computed(() => {
  const item = props.deAn
  if (!item) return ''
  return item.ma_truong ? `${item.ma_truong} — ${item.ten_truong}` : item.ten_truong
})

const statusMeta = computed(() => {
  const value = props.deAn?.trang_thai
  if (!value) return null
  const tag = value === 'cong_bo' ? 'success' : value === 'het_hieu_luc' ? 'warning' : 'info'
  return { label: STATUS_LABELS[value] || value, tag }
})

function formatForms(value) {
  if (!Array.isArray(value) || !value.length) return '—'
  return value.join(', ')
}
</script>

<template>
  <div v-if="deAn" class="overview">
    <div>
      <span>Trường</span>
      <strong>{{ schoolLabel }}</strong>
    </div>
    <div>
      <span>Năm tuyển sinh</span>
      <strong>{{ deAn.nam_tuyen_sinh }}</strong>
    </div>
    <div>
      <span>Chỉ tiêu</span>
      <strong>{{ formatQuota(deAn.chi_tieu) }}</strong>
    </div>
    <div>
      <span>Ngày công bố</span>
      <strong>{{ formatDate(deAn.ngay_cong_bo) }}</strong>
    </div>
    <div class="is-wide">
      <span>Tên đề án</span>
      <strong>{{ deAn.ten_de_an || '—' }}</strong>
    </div>
    <div>
      <span>Trạng thái</span>
      <strong>
        <CustomTag v-if="statusMeta" :type="statusMeta.tag" effect="light">{{ statusMeta.label }}</CustomTag>
        <template v-else>—</template>
      </strong>
    </div>
    <div class="is-wide">
      <span>Hình thức đào tạo</span>
      <strong>{{ formatForms(deAn.hinh_thuc_dao_tao) }}</strong>
    </div>
    <div class="is-wide">
      <span>Nguồn dữ liệu</span>
      <strong>
        <a
          v-if="deAn.nguon_du_lieu_url"
          :href="deAn.nguon_du_lieu_url"
          target="_blank"
          rel="noopener noreferrer"
        >{{ deAn.nguon_du_lieu_url }}</a>
        <template v-else>—</template>
      </strong>
    </div>
    <div class="is-wide">
      <span>Giới thiệu</span>
      <strong class="pre">{{ deAn.gioi_thieu || '—' }}</strong>
    </div>
    <div class="is-wide">
      <span>Ghi chú</span>
      <strong class="pre">{{ deAn.ghi_chu || '—' }}</strong>
    </div>
  </div>
  <CustomEmpty v-else-if="!loading" description="Không có dữ liệu đề án." />
</template>

<style scoped>
.overview {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 20px;
}

.overview > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.overview .is-wide {
  grid-column: 1 / -1;
}

.overview span {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.overview strong {
  font-weight: 600;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.overview .pre {
  font-weight: 500;
  white-space: pre-wrap;
}

.overview a {
  color: var(--el-color-primary);
  overflow-wrap: anywhere;
}

@media (max-width: 640px) {
  .overview {
    grid-template-columns: 1fr;
  }
}
</style>
