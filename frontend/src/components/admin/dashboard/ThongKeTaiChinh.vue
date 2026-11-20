<template>
  <section v-loading="dangTai" class="tai-chinh">
    <div class="tai-chinh__head">
      <h2 class="tai-chinh__title">Tài chính</h2>
      <span class="tai-chinh__desc">Doanh thu từ giao dịch nạp tiền thành công, so với cùng kỳ trước</span>
    </div>

    <el-row :gutter="16" class="tai-chinh__row tai-chinh__row--the">
      <el-col v-for="item in theTien" :key="item.key" :xs="12" :sm="12" :lg="6">
        <TheThongKe v-bind="item" />
      </el-col>
    </el-row>

    <el-row :gutter="16" class="tai-chinh__row">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="tai-chinh__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Doanh thu nạp tiền</span>
                <span class="card-header__desc">Theo tháng, năm {{ namNay }}</span>
              </div>
            </div>
          </template>
          <BieuDoCot :series="doanhThu.series" :categories="doanhThu.categories" :height="230" donVi="đ" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="tai-chinh__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Doanh thu theo loại gói</span>
                <span class="card-header__desc">Năm {{ namNay }}</span>
              </div>
            </div>
          </template>
          <BieuDoTron
            v-if="theoLoai.values.length"
            :labels="theoLoai.labels"
            :values="theoLoai.values"
            :height="200"
            nhanTong="Tổng (đ)"
            donVi="đ"
          />
          <el-empty v-else description="Chưa có doanh thu năm nay" :image-size="80" />

          <button type="button" class="cho-xac-nhan" @click="router.push({ name: 'admin-lich-su-nap-tien' })">
            <el-icon class="cho-xac-nhan__icon"><Clock /></el-icon>
            <span class="cho-xac-nhan__body">
              <span class="cho-xac-nhan__label">Đang chờ thanh toán</span>
              <span class="cho-xac-nhan__value">
                {{ choXacNhan.so_giao_dich.toLocaleString('vi-VN') }} giao dịch ·
                {{ formatInteger(choXacNhan.so_tien) }} đ
              </span>
            </span>
            <el-icon><ArrowRight /></el-icon>
          </button>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup>
/**
 * ThongKeTaiChinh — khối thống kê tài chính trên dashboard quản trị: thẻ doanh thu hôm nay/tuần/tháng/năm,
 * biểu đồ doanh thu 12 tháng trong năm, tỷ trọng theo loại gói và giao dịch đang chờ.
 */
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Clock } from '@element-plus/icons-vue'
import { fetchThongKeNapTien } from '@/api/napTien'
import BieuDoCot from '@/components/admin/charts/BieuDoCot.vue'
import BieuDoTron from '@/components/admin/charts/BieuDoTron.vue'
import TheThongKe from '@/components/admin/dashboard/TheThongKe.vue'
import { formatInteger, tienRutGon } from '@/utils/number'

const KY = {
  hom_nay: { title: 'Doanh thu hôm nay', icon: 'Wallet', color: '#1f7a4d', so: 'hôm qua' },
  tuan_nay: { title: 'Doanh thu tuần này', icon: 'Calendar', color: '#2f6fdb', so: 'tuần trước' },
  thang_nay: { title: 'Doanh thu tháng này', icon: 'Money', color: '#e0a526', so: 'tháng trước' },
  nam_nay: { title: 'Doanh thu năm nay', icon: 'TrendCharts', color: '#7b61c9', so: 'năm trước' },
}
const LOAI = {
  edu_coin: 'Edu coin',
  tra_cuu: 'Tra cứu',
  khao_sat: 'Khảo sát',
  hoi_dap: 'Hỏi đáp',
  token: 'Token',
}

const router = useRouter()
const dangTai = ref(false)
const namNay = new Date().getFullYear()
const thongKe = ref({
  ky: [],
  theo_ngay: [],
  theo_thang: [],
  theo_loai: [],
  cho_xac_nhan: { so_tien: 0, so_giao_dich: 0 },
})

function phanTram(nay, truoc) {
  if (!truoc) return null
  return Math.round(((nay - truoc) / truoc) * 1000) / 10
}

const theTien = computed(() => {
  const ngay = thongKe.value.theo_ngay.map((d) => d.so_tien)
  const thangDaQua = thongKe.value.theo_thang.slice(0, new Date().getMonth() + 1).map((d) => d.so_tien)
  const xuHuong = { hom_nay: ngay.slice(-7), tuan_nay: ngay.slice(-14), thang_nay: ngay, nam_nay: thangDaQua }
  return thongKe.value.ky.map((k) => {
    const { so, donVi } = tienRutGon(k.so_tien)
    return {
      key: k.ma,
      title: KY[k.ma].title,
      icon: KY[k.ma].icon,
      color: KY[k.ma].color,
      value: so,
      donVi: donVi === 'đ' ? donVi : ` ${donVi}`,
      trend: phanTram(k.so_tien, k.so_tien_ky_truoc),
      trendLabel: `${k.so_giao_dich.toLocaleString('vi-VN')} GD · so với ${KY[k.ma].so}`,
      xuHuong: xuHuong[k.ma],
    }
  })
})

const doanhThu = computed(() => ({
  categories: thongKe.value.theo_thang.map((d) => `T${d.thang}`),
  series: [{ name: 'Doanh thu', data: thongKe.value.theo_thang.map((d) => d.so_tien) }],
}))

const theoLoai = computed(() => ({
  labels: thongKe.value.theo_loai.map((d) => LOAI[d.loai_ap_dung] || d.loai_ap_dung),
  values: thongKe.value.theo_loai.map((d) => d.so_tien),
}))

const choXacNhan = computed(() => thongKe.value.cho_xac_nhan)

async function taiLai() {
  dangTai.value = true
  try {
    thongKe.value = await fetchThongKeNapTien()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Không tải được thống kê tài chính')
  } finally {
    dangTai.value = false
  }
}

taiLai()

defineExpose({ taiLai })
</script>

<style scoped>
.tai-chinh {
  margin-bottom: 8px;
}

.tai-chinh__head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 12px;
  margin-bottom: 10px;
}

.tai-chinh__title {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.tai-chinh__desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.tai-chinh__row > .el-col {
  margin-bottom: 12px;
}

.tai-chinh__card {
  height: 100%;
  border-radius: 12px;
}

/* Thẻ gọn để nhìn được nhiều số liệu hơn trên một màn hình. */
.tai-chinh__card :deep(.el-card__header) {
  padding: 10px 16px;
}

.tai-chinh__card :deep(.el-card__body) {
  padding: 10px 14px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-header__title {
  display: block;
  font-size: 15px;
  font-weight: 400;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.card-header__desc {
  display: block;
  margin-top: 2px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.cho-xac-nhan {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  margin-top: 8px;
  padding: 8px 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  background: var(--el-fill-color-lighter);
  color: var(--el-text-color-regular);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s ease;
}

.cho-xac-nhan:hover {
  border-color: var(--el-color-warning);
}

.cho-xac-nhan__icon {
  flex-shrink: 0;
  font-size: 18px;
  color: var(--el-color-warning);
}

.cho-xac-nhan__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.cho-xac-nhan__label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.cho-xac-nhan__value {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  font-variant-numeric: tabular-nums;
}

@media (max-width: 640px) {
  .tai-chinh__row--the {
    margin-right: -5px !important;
    margin-left: -5px !important;
  }

  .tai-chinh__row--the > .el-col {
    padding-right: 5px !important;
    padding-left: 5px !important;
    margin-bottom: 10px;
  }
}
</style>
