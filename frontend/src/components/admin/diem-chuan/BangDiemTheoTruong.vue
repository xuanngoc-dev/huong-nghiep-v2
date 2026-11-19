<template>
  <CustomTable :loading="loading" :data="bang.hang" row-key="khoa" stripe border class="bang-diem">
    <el-table-column label="STT" width="64" align="center">
      <template #default="{ $index }">{{ $index + 1 }}</template>
    </el-table-column>
    <el-table-column label="Chương trình/ngành đào tạo" min-width="260">
      <template #default="{ row }">{{ row.ten_chuong_trinh || '—' }}</template>
    </el-table-column>
    <el-table-column label="Chỉ tiêu dự kiến" width="160" align="center">
      <template #default="{ row }">{{ row.chi_tieu == null ? '—' : Number(row.chi_tieu).toLocaleString('vi-VN') }}</template>
    </el-table-column>
    <el-table-column label="Mã xét tuyển" width="130" align="center">
      <template #default="{ row }">{{ row.ma_xet_tuyen || '—' }}</template>
    </el-table-column>
    <el-table-column
      v-if="bang.cotPhuongThuc.length"
      label="Phương thức tuyển sinh/Tổ hợp xét tuyển"
      align="center"
    >
      <el-table-column
        v-for="cot in bang.cotPhuongThuc"
        :key="cot.ma"
        :label="cot.nhan"
        :min-width="180"
        align="center"
        class-name="o-diem-cell"
      >
        <template #header>
          <CustomTooltip placement="top">
            <template #content>
              <div class="chi-tiet">
                <div class="chi-tiet__tieu-de">
                  {{ cot.ma ? `Phương thức ${cot.ma}` : 'Mọi phương thức' }}<template v-if="cot.ma && cot.chiTiet.ten"> — {{ cot.chiTiet.ten }}</template>
                </div>
                <div v-if="!cot.ma" class="chi-tiet__dong">{{ cot.chiTiet.ten }}</div>
                <div v-if="cot.chiTiet.maTruong.length" class="chi-tiet__dong">
                  Mã của trường: {{ cot.chiTiet.maTruong.join(', ') }}
                </div>
                <ul v-if="cot.chiTiet.tenTruong.length" class="chi-tiet__ds">
                  <li v-for="ten in cot.chiTiet.tenTruong" :key="ten">{{ ten }}</li>
                </ul>
              </div>
            </template>
            <span class="ten-phuong-thuc">{{ cot.nhan }}</span>
          </CustomTooltip>
        </template>
        <template #default="{ row }">
          <div v-if="row.o[cot.ma]" class="o-diem">
            <button
              v-for="item in row.o[cot.ma].diem"
              :key="item.id"
              type="button"
              class="o-diem__muc"
              :title="moTa(item)"
              @click="emit('sua', item)"
            >
              <span v-if="item.ma_to_hop" class="o-diem__phu">{{ item.ma_to_hop }}</span>
              <strong>{{ soDiem(item.diem_chuan) }}</strong>
              <span v-if="Number(item.thang_diem) !== 30" class="o-diem__phu">/{{ soDiem(item.thang_diem) }}</span>
            </button>
            <span v-if="row.o[cot.ma].toHop.length" class="o-diem__to-hop">{{ row.o[cot.ma].toHop.join(', ') }}</span>
            <CustomIcon
              v-else-if="!row.o[cot.ma].diem.length"
              class="mark mark--yes"
              aria-label="Có sử dụng"
            >
              <Check />
            </CustomIcon>
          </div>
          <CustomIcon v-else class="mark mark--no" aria-label="Không sử dụng">
            <Close />
          </CustomIcon>
        </template>
      </el-table-column>
    </el-table-column>
    <el-table-column label="Tiêu chí phụ" min-width="220" class-name="o-diem-cell">
      <template #default="{ row }">
        <!-- Ô rút gọn (mỗi tiêu chí một dòng, tối đa SO_TIEU_CHI_HIEN dòng), rê chuột xem đầy đủ.
             Chỉ một nội dung thì không ghi phương thức; nhiều nội dung thì ghi mã phương thức đứng trước. -->
        <CustomTooltip v-if="row.tieuChiPhu.length" placement="top">
          <template #content>
            <ul class="tieu-chi-phu__day-du">
              <li v-for="tc in row.tieuChiPhu" :key="tc.noiDung">
                <strong v-if="row.tieuChiPhu.length > 1">{{ tenPhuongThucTieuChi(tc) }}: </strong>{{ tc.noiDung }}
              </li>
            </ul>
          </template>
          <div class="tieu-chi-phu">
            <div v-for="tc in row.tieuChiPhu.slice(0, SO_TIEU_CHI_HIEN)" :key="tc.noiDung" class="tieu-chi-phu__dong">
              <span v-if="row.tieuChiPhu.length > 1" class="o-diem__phu">{{ tenPhuongThucTieuChi(tc) }}: </span>{{ tc.noiDung }}
            </div>
            <div v-if="row.tieuChiPhu.length > SO_TIEU_CHI_HIEN" class="o-diem__phu">
              +{{ row.tieuChiPhu.length - SO_TIEU_CHI_HIEN }} tiêu chí khác
            </div>
          </div>
        </CustomTooltip>
        <span v-else class="o-diem__trong">—</span>
      </template>
    </el-table-column>
    <template #empty>
      <CustomEmpty :description="emptyText" />
    </template>
  </CustomTable>
</template>

<script setup>
/**
 * Bảng điểm chuẩn của một trường trong một năm, theo bố cục bảng chương trình của đề án
 * (xem chi-tiet/ChuongTrinh.vue): mỗi phương thức một cột, ô gồm điểm chuẩn và tổ hợp xét tuyển.
 * Bấm vào một điểm để sửa dòng đó (phát sự kiện `sua`).
 */
import { computed } from 'vue'
import { bangDiemTheoTruong } from '@/utils/diemChuanTheoTruong'

defineOptions({ name: 'BangDiemTheoTruong' })

const props = defineProps({
  // Chương trình đào tạo của năm, lấy kèm phương thức.
  chuongTrinh: { type: Array, default: () => [] },
  diemChuan: { type: Array, default: () => [] },
  danhMucPhuongThuc: { type: Array, default: () => [] },
  q: { type: String, default: '' },
  maPhuongThuc: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Chưa có điểm chuẩn nào.' },
})

const emit = defineEmits(['sua'])

const SO_TIEU_CHI_HIEN = 2

const bang = computed(() => bangDiemTheoTruong(props))

function tenPhuongThucTieuChi(tc) {
  return tc.phuongThuc.map((ma) => ma || 'Mọi PT').join(', ')
}

function soDiem(value) {
  return Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 2 })
}

function moTa(item) {
  const phan = [
    `Điểm chuẩn ${soDiem(item.diem_chuan)} / ${soDiem(item.thang_diem)}`,
    item.ma_to_hop ? `Tổ hợp ${item.ma_to_hop}` : 'Mọi tổ hợp',
  ]
  if (item.tieu_chi_phu) phan.push(`Tiêu chí phụ: ${item.tieu_chi_phu}`)
  if (item.ghi_chu) phan.push(`Ghi chú: ${item.ghi_chu}`)
  phan.push('Bấm để sửa')
  return phan.join('\n')
}
</script>

<style scoped>
.bang-diem :deep(thead.is-group th.el-table__cell) {
  background: var(--el-table-header-bg-color);
  color: var(--el-table-header-text-color);
}

.bang-diem :deep(.el-table__header .cell) {
  white-space: normal;
  line-height: 1.35;
  text-align: center;
}

.bang-diem :deep(td.o-diem-cell .cell) {
  white-space: normal;
  line-height: 1.4;
}

.ten-phuong-thuc {
  cursor: help;
  text-transform: capitalize;
}

.chi-tiet {
  max-width: 360px;
  line-height: 1.45;
}

.chi-tiet__tieu-de {
  font-weight: 600;
}

.chi-tiet__dong {
  margin-top: 4px;
}

.chi-tiet__ds {
  margin: 4px 0 0;
  padding-left: 16px;
}

.o-diem {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.o-diem__muc {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  padding: 1px 6px;
  border: 0;
  border-radius: 4px;
  background: transparent;
  color: inherit;
  font: inherit;
  cursor: pointer;
}

.o-diem__muc:hover {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.o-diem__phu,
.o-diem__to-hop {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.tieu-chi-phu {
  min-width: 0;
  cursor: help;
}

.tieu-chi-phu__dong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tieu-chi-phu__day-du {
  max-width: 420px;
  margin: 0;
  padding-left: 16px;
  line-height: 1.45;
}

.tieu-chi-phu__day-du li + li {
  margin-top: 4px;
}

.o-diem__trong {
  color: var(--el-text-color-placeholder);
}

.mark {
  font-size: 18px;
  vertical-align: middle;
}

.mark--yes {
  color: var(--el-color-success);
}

.mark--no {
  color: var(--el-color-danger);
}
</style>
