<script setup>
import { computed, ref } from 'vue'
import KhoiDuLieu from './KhoiDuLieu.vue'
import {
  KHOA_PHUONG_THUC_KHOI,
  KHOA_PHUONG_THUC_META,
  coGiaTri,
  heSoMon,
  khoaConLai,
  nhan,
  tenMon,
} from './nhanDuLieu'

const props = defineProps({
  phuongThuc: { type: Object, required: true },
})

const hienJson = ref(false)

const meta = computed(() =>
  KHOA_PHUONG_THUC_META.filter((key) => key in props.phuongThuc).map((key) => ({
    key,
    label: nhan(key),
    value: props.phuongThuc[key],
  })),
)

const khoi = computed(() =>
  KHOA_PHUONG_THUC_KHOI.filter(([key]) => coGiaTri(props.phuongThuc[key])).map(([key, label]) => ({
    key,
    label,
    value: props.phuongThuc[key],
  })),
)

const toHop = computed(() => (Array.isArray(props.phuongThuc.to_hop_mon) ? props.phuongThuc.to_hop_mon : null))

const conLai = computed(() =>
  khoaConLai(props.phuongThuc, [...KHOA_PHUONG_THUC_META, ...KHOA_PHUONG_THUC_KHOI.map(([key]) => key), 'ghi_chu']),
)

const json = computed(() => JSON.stringify(props.phuongThuc, null, 2))

function hien(value) {
  if (value == null || value === '') return 'Không có'
  if (typeof value === 'boolean') return value ? 'Có' : 'Không'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
</script>

<template>
  <section class="phuong-thuc">
    <div class="phuong-thuc__bar">
      <h3>{{ phuongThuc.ten_phuong_thuc || 'Phương thức' }}</h3>
      <el-switch v-model="hienJson" active-text="JSON gốc" />
    </div>

    <pre v-if="hienJson" class="phuong-thuc__json">{{ json }}</pre>
    <template v-else>
      <dl v-if="meta.length" class="meta">
        <div v-for="field in meta" :key="field.key">
          <dt>{{ field.label }}</dt>
          <dd>{{ hien(field.value) }}</dd>
        </div>
      </dl>

      <p v-if="coGiaTri(phuongThuc.ghi_chu)" class="ghi-chu">{{ phuongThuc.ghi_chu }}</p>

      <article v-for="block in khoi" :key="block.key" class="block">
        <h4>{{ block.label }}</h4>
        <el-table v-if="block.key === 'to_hop_mon' && toHop" :data="toHop" size="small" border empty-text="Không có tổ hợp">
          <el-table-column type="expand">
            <template #default="{ row }">
              <KhoiDuLieu :value="row" />
            </template>
          </el-table-column>
          <el-table-column prop="ma_to_hap" label="Mã" width="90" />
          <el-table-column prop="ten_to_hap" label="Tổ hợp" min-width="180" />
          <el-table-column label="Môn" min-width="180">
            <template #default="{ row }">{{ tenMon(row.danh_sach_mon) || 'Không có' }}</template>
          </el-table-column>
          <el-table-column label="Hệ số" min-width="140">
            <template #default="{ row }">{{ heSoMon(row.he_so_mon) || 'Không có' }}</template>
          </el-table-column>
          <el-table-column label="Chỉ tiêu" width="100">
            <template #default="{ row }">{{ hien(row.chi_tieu_to_hap) }}</template>
          </el-table-column>
          <el-table-column label="Điểm chuẩn" width="110">
            <template #default="{ row }">{{ hien(row.diem_chuan) }}</template>
          </el-table-column>
          <el-table-column label="Điểm sàn" width="100">
            <template #default="{ row }">{{ hien(row.diem_san) }}</template>
          </el-table-column>
        </el-table>
        <KhoiDuLieu v-else :value="block.value" />
      </article>

      <article v-if="coGiaTri(conLai)" class="block">
        <h4>Thông tin khác</h4>
        <KhoiDuLieu :value="conLai" />
      </article>
    </template>
  </section>
</template>

<style scoped>
.phuong-thuc__bar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.phuong-thuc__bar h3,
.block h4 {
  margin: 0;
}

.block {
  margin-top: 16px;
}

.block h4 {
  margin-bottom: 8px;
  font-size: 16px;
}

.meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px 16px;
  margin: 0;
}

.meta dt {
  margin: 0;
  color: #5c6b62;
  font-size: 13px;
}

.meta dd {
  margin: 2px 0 0;
  font-weight: 600;
  word-break: break-word;
}

.ghi-chu {
  margin: 12px 0 0;
  white-space: pre-wrap;
}

.phuong-thuc__json {
  margin: 0;
  max-height: 70vh;
  overflow: auto;
  padding: 12px;
  border-radius: 8px;
  background: #f4f7f5;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
}
</style>
