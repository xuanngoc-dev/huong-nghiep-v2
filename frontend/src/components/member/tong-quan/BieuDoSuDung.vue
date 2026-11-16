<template>
  <el-card shadow="never" class="bieu-do-su-dung">
    <template #header>
      <div class="bieu-do-su-dung__dau">
        <div>
          <h2 class="bieu-do-su-dung__tieu-de">Lượt sử dụng chức năng</h2>
          <p class="bieu-do-su-dung__phu">Số lần tìm trường phù hợp và làm khảo sát theo ngày</p>
        </div>
        <div class="bieu-do-su-dung__dieu-khien">
          <el-radio-group v-model="soNgay" size="small" aria-label="Khoảng thời gian">
            <el-radio-button v-for="item in KHOANG" :key="item" :value="item">{{ item }} ngày</el-radio-button>
          </el-radio-group>
          <CustomTooltip :content="xemBang ? 'Xem biểu đồ' : 'Xem dạng bảng'" placement="top">
            <CustomButton link type="primary" :aria-label="xemBang ? 'Xem biểu đồ' : 'Xem dạng bảng'" @click="xemBang = !xemBang">
              <CustomIcon><Histogram v-if="xemBang" /><Grid v-else /></CustomIcon>
            </CustomButton>
          </CustomTooltip>
        </div>
      </div>
    </template>

    <dl class="bieu-do-su-dung__tong">
      <div>
        <dt><span class="bieu-do-su-dung__cham" :style="{ background: MAU[0] }" aria-hidden="true" />Tìm trường</dt>
        <dd>
          <strong>{{ hienSo(thongKe?.tong_tim_truong) }}</strong>
          <span>miễn phí {{ hienSo(thongKe?.tim_truong_mien_phi) }} · trả phí {{ hienSo(thongKe?.tim_truong_tra_phi) }}</span>
        </dd>
      </div>
      <div>
        <dt><span class="bieu-do-su-dung__cham" :style="{ background: MAU[1] }" aria-hidden="true" />Khảo sát</dt>
        <dd><strong>{{ hienSo(thongKe?.tong_khao_sat) }}</strong> <span>phiên</span></dd>
      </div>
    </dl>

    <p v-if="loi" class="bieu-do-su-dung__trong">{{ loi }}</p>
    <p v-else-if="dangTai && !thongKe" class="bieu-do-su-dung__trong">Đang tải thống kê…</p>
    <CustomTable v-else-if="xemBang" :data="dongCoDung" size="small" max-height="320" border>
      <CustomTableColumn label="Ngày" min-width="110">
        <template #default="{ row }">{{ hienNgay(row.ngay, true) }}</template>
      </CustomTableColumn>
      <CustomTableColumn label="Tìm trường" prop="tim_truong" align="right" min-width="100" />
      <CustomTableColumn label="Khảo sát" prop="khao_sat" align="right" min-width="100" />
      <template #empty>Chưa dùng chức năng nào trong {{ soNgay }} ngày qua.</template>
    </CustomTable>
    <template v-else>
      <BieuDoCot :series="series" :categories="ngay" :colors="MAU" :height="280" don-vi="lần" stacked so-nguyen />
      <p v-if="thongKe && !coDuLieu" class="bieu-do-su-dung__chu-thich">
        Chưa dùng chức năng nào trong {{ soNgay }} ngày qua.
      </p>
    </template>
  </el-card>
</template>

<script setup>
/**
 * Biểu đồ cột chồng lượt dùng chức năng theo ngày (GET /tai-khoan/thong-ke-su-dung), chọn 7/30/90 ngày,
 * có chế độ xem dạng bảng.
 */
import { computed, onMounted, ref, watch } from 'vue'
import { Grid, Histogram } from '@element-plus/icons-vue'
import BieuDoCot from '@/components/admin/charts/BieuDoCot.vue'
import { BANG_MAU } from '@/components/admin/charts/useApexChart'
import { fetchThongKeSuDung } from '@/api/hoSo'
import { hienSo } from '@/data/napTien'

const KHOANG = [7, 30, 90]
// Thứ tự cố định: tìm trường, khảo sát (đã kiểm tách màu cho người mù màu ở nền sáng/tối).
const MAU = BANG_MAU.slice(0, 2)

const soNgay = ref(30)
const xemBang = ref(false)
const thongKe = ref(null)
const dangTai = ref(false)
const loi = ref('')

function hienNgay(value, coNam = false) {
  const [nam, thang, ngay] = String(value).split('-')
  return coNam ? `${ngay}/${thang}/${nam}` : `${ngay}/${thang}`
}

const theoNgay = computed(() => thongKe.value?.theo_ngay || [])
const ngay = computed(() => theoNgay.value.map((item) => hienNgay(item.ngay)))
const series = computed(() => [
  { name: 'Tìm trường', data: theoNgay.value.map((item) => item.tim_truong) },
  { name: 'Khảo sát', data: theoNgay.value.map((item) => item.khao_sat) },
])
const dongCoDung = computed(() =>
  theoNgay.value.filter((item) => item.tim_truong || item.khao_sat).slice().reverse(),
)
const coDuLieu = computed(() => dongCoDung.value.length > 0)

async function tai() {
  dangTai.value = true
  loi.value = ''
  try {
    thongKe.value = await fetchThongKeSuDung({ so_ngay: soNgay.value }, { skipLoading: true })
  } catch {
    loi.value = 'Không tải được thống kê sử dụng.'
  } finally {
    dangTai.value = false
  }
}

watch(soNgay, tai)
onMounted(tai)
</script>

<style scoped>
.bieu-do-su-dung {
  border-radius: 12px;
}

.bieu-do-su-dung__dau {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.bieu-do-su-dung__tieu-de {
  margin: 0 0 2px;
  font-size: 16px;
}

.bieu-do-su-dung__phu {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.bieu-do-su-dung__dieu-khien {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bieu-do-su-dung__tong {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 32px;
  margin: 0 0 8px;
}

.bieu-do-su-dung__tong dt {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  font-weight: 400;
}

.bieu-do-su-dung__tong dd {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.bieu-do-su-dung__tong strong {
  margin-right: 4px;
  color: var(--el-text-color-primary);
  font-size: 20px;
}

.bieu-do-su-dung__cham {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.bieu-do-su-dung__trong,
.bieu-do-su-dung__chu-thich {
  margin: 0;
  padding: 24px 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  text-align: center;
}

.bieu-do-su-dung__chu-thich {
  padding: 0;
}
</style>
