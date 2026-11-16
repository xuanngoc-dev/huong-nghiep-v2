<template>
  <CustomDialog v-model="visible" title="Xác nhận đăng ký gói" width="480px">
    <div v-if="goi" class="xac-nhan">
      <section class="xac-nhan__goi" aria-label="Gói cước đăng ký">
        <span class="xac-nhan__loai">{{ loai.label }}</span>
        <h3 class="xac-nhan__ten">{{ goi.ten_goi_cuoc }}</h3>
        <span class="xac-nhan__gia">
          <s v-if="giaGoc !== null" class="xac-nhan__cu">{{ hienTien(giaGoc) }}</s>
          {{ hienTien(giaBan) }}
        </span>
      </section>

      <dl class="xac-nhan__luot">
        <div class="xac-nhan__dong">
          <dt>Số dư hiện tại</dt>
          <dd>
            <template v-if="soDuHienTai !== null">{{ hienSo(soDuHienTai) }} {{ loai.donVi }}</template>
            <template v-else>—</template>
          </dd>
        </div>
        <div class="xac-nhan__dong">
          <dt>Nhận thêm</dt>
          <dd class="xac-nhan__cong">
            <s v-if="luotGoc !== null" class="xac-nhan__cu">{{ hienSo(luotGoc) }}</s>
            +{{ hienSo(luotNhan) }} {{ loai.donVi }}
          </dd>
        </div>
        <div class="xac-nhan__dong xac-nhan__dong--tong">
          <dt>Số dư sau khi nạp (dự kiến)</dt>
          <dd>
            <template v-if="soDuHienTai !== null">{{ hienSo(Number(soDuHienTai) + Number(luotNhan)) }} {{ loai.donVi }}</template>
            <template v-else>—</template>
          </dd>
        </div>
      </dl>

      <p class="xac-nhan__note">Số dư được cộng ngay khi hệ thống nhận đủ tiền chuyển khoản.</p>
    </div>
    <template #footer>
      <CustomButton @click="visible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="loading" :disabled="!goi" @click="emit('thanh-toan', goi)">
        Thanh toán
      </CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
/**
 * Modal xác nhận trước khi đăng ký gói: thông tin gói, số dư hiện tại và số dư dự kiến sau khi nạp.
 * Bấm "Thanh toán" phát sự kiện `thanh-toan` để trang cha tạo giao dịch và mở modal thanh toán.
 */
import { computed } from 'vue'
import { LOAI_AP_DUNG, hienSo, hienTien, timTheoGiaTri } from '@/data/napTien'

const visible = defineModel({ type: Boolean, default: false })

const props = defineProps({
  // Gói cước đang bán (GoiCuocDangBan).
  goi: { type: Object, default: null },
  // Số dư hiện tại của loại gói (Edu coin hoặc số lượt); null khi chưa tải được.
  soDuHienTai: { type: Number, default: null },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['thanh-toan'])

const loai = computed(() => {
  const item = timTheoGiaTri(LOAI_AP_DUNG, props.goi?.loai_ap_dung)
  return { label: item.label, donVi: item.donVi || '' }
})
const giaBan = computed(() => props.goi?.gia_khuyen_mai ?? props.goi?.gia_goc)
const luotNhan = computed(() => props.goi?.so_luot_nhan_duoc_khuyen_mai ?? props.goi?.so_luot_nhan_duoc_goc ?? 0)
const giaGoc = computed(() => {
  const goc = props.goi?.gia_goc
  return goc !== undefined && goc !== null && Number(goc) !== Number(giaBan.value) ? goc : null
})
const luotGoc = computed(() => {
  const goc = props.goi?.so_luot_nhan_duoc_goc
  return goc !== undefined && goc !== null && Number(goc) !== Number(luotNhan.value) ? goc : null
})
</script>

<style scoped>
.xac-nhan {
  display: grid;
  gap: 16px;
}

.xac-nhan__goi {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--el-fill-color-lighter);
}

.xac-nhan__loai {
  margin-bottom: 4px;
  padding: 1px 8px;
  border-radius: 999px;
  background: #eef6f1;
  color: #0c5c34;
  font-size: 12px;
}

.xac-nhan__ten {
  margin: 0;
  font-size: 18px;
}

.xac-nhan__gia {
  color: #0c5c34;
  font-size: 20px;
  font-weight: 700;
}

.xac-nhan__cu {
  margin-right: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  font-weight: 400;
}

.xac-nhan__luot {
  display: grid;
  gap: 8px;
  margin: 0;
}

.xac-nhan__dong {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 4px 12px;
}

.xac-nhan__dong dt {
  color: var(--el-text-color-secondary);
  font-weight: 400;
}

.xac-nhan__dong dd {
  margin: 0;
  font-weight: 600;
  text-align: right;
}

.xac-nhan__cong {
  color: #0c5c34;
}

.xac-nhan__dong--tong {
  padding-top: 8px;
  border-top: 1px dashed var(--el-border-color);
}

.xac-nhan__dong--tong dd {
  font-size: 16px;
}

.xac-nhan__note {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
}
</style>
