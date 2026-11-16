<template>
  <section v-loading="dangTai" class="ket-qua-xt">
    <header class="ket-qua-xt__dau">
      <div>
        <h3 class="ket-qua-xt__tieu-de">Khả năng trúng tuyển theo đề án {{ lan?.nam_tuyen_sinh || '' }}</h3>
        <p class="ket-qua-xt__phu">
          Tính theo quy tắc xét tuyển các trường đã công bố và điểm chuẩn năm trước. Điểm chuẩn là mốc tham khảo, không
          phải dự báo.
        </p>
      </div>
      <CustomTag v-if="lan" type="primary" size="small">
        {{ lan.so_chuong_trinh }} chương trình · {{ lan.so_truong }} trường
      </CustomTag>
    </header>

    <div v-if="lan?.gia_dinh?.length" class="ket-qua-xt__gia-dinh">
      <CustomIcon><InfoFilled /></CustomIcon>
      <div>
        <strong>Kết quả dựa trên các giả định:</strong>
        <ul>
          <li v-for="(x, i) in lan.gia_dinh" :key="i">{{ x }}</li>
        </ul>
      </div>
    </div>

    <p v-if="loi" class="ket-qua-xt__loi">{{ loi }}</p>
    <CustomEmpty
      v-else-if="lan && !lan.so_chuong_trinh"
      description="Chưa có chương trình nào bạn đủ điều kiện xét tuyển theo dữ liệu hiện có. Bổ sung điểm trong hồ sơ để kết quả đầy đủ hơn."
    />

    <el-tabs v-else-if="lan" v-model="tab">
      <el-tab-pane :label="`Chương trình (${tongChuongTrinh})`" name="chuong_trinh">
        <CustomTable :data="chuongTrinh" row-key="chuong_trinh_id" border stripe>
          <el-table-column label="Hạng" width="64" align="center" prop="thu_hang" />
          <el-table-column label="Trường / chương trình" min-width="240">
            <template #default="{ row }">
              <div class="ket-qua-xt__ten">{{ row.ten_truong || row.ma_truong }}</div>
              <div class="ket-qua-xt__mo">
                {{ row.ten_chuong_trinh }}<template v-if="row.ma_xet_tuyen"> · {{ row.ma_xet_tuyen }}</template>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Phương án tốt nhất" min-width="200">
            <template #default="{ row }">
              <div>{{ row.phuong_an.ten_cong_thuc }}</div>
              <div v-if="row.phuong_an.ma_to_hop" class="ket-qua-xt__mo">Tổ hợp {{ row.phuong_an.ma_to_hop }}</div>
            </template>
          </el-table-column>
          <el-table-column label="Điểm xét" width="150" align="center">
            <template #default="{ row }">
              <span v-if="row.la_xet_thang" class="ket-qua-xt__nhan ket-qua-xt__nhan--tot">Đủ điều kiện xét tuyển thẳng</span>
              <span v-else-if="row.chua_tinh_diem" class="ket-qua-xt__mo">
                Đủ điều kiện nộp hồ sơ, hệ thống chưa tính điểm cho phương thức này
              </span>
              <span v-else>
                <strong>{{ so(row.diem_xet) }}</strong><span class="ket-qua-xt__mo">/{{ so(row.thang_diem) }}</span>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="Điểm chuẩn" width="130" align="center">
            <template #default="{ row }">
              <template v-if="row.diem_chuan">
                {{ so(row.diem_chuan.diem) }}<span class="ket-qua-xt__mo">/{{ so(row.diem_chuan.thang_diem) }}</span>
                <div class="ket-qua-xt__mo">năm {{ row.diem_chuan.nam }}</div>
              </template>
              <span v-else class="ket-qua-xt__mo">—</span>
            </template>
          </el-table-column>
          <el-table-column label="Chênh (thang 30)" width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.chenh_lech_30 == null" class="ket-qua-xt__mo">—</span>
              <span v-else :class="row.chenh_lech_30 >= 0 ? 'ket-qua-xt__duong' : 'ket-qua-xt__am'">
                {{ row.chenh_lech_30 > 0 ? '+' : '' }}{{ so(row.chenh_lech_30) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="Mức phù hợp" min-width="170">
            <template #default="{ row }">
              <CustomTag :type="mauXepLoai(row)" size="small">{{ nhanXepLoai(row) }}</CustomTag>
              <div v-if="row.diem_phu_hop != null" class="ket-qua-xt__mo">{{ so(row.diem_phu_hop) }}/100</div>
            </template>
          </el-table-column>
          <el-table-column label="Thao tác" width="80" fixed="right" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <CustomTooltip content="Xem các phương án" placement="top">
                  <CustomButton link type="primary" aria-label="Xem các phương án" @click="moPhuongAn(row)">
                    <CustomIcon><View /></CustomIcon>
                  </CustomButton>
                </CustomTooltip>
              </div>
            </template>
          </el-table-column>
        </CustomTable>
        <div v-if="tongChuongTrinh > soMoiTrang" class="ket-qua-xt__trang">
          <CustomPagination
            v-model:current-page="trang"
            :page-size="soMoiTrang"
            :total="tongChuongTrinh"
            layout="total, prev, pager, next"
            background
            @current-change="taiChuongTrinh"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="`Theo trường (${truong.length})`" name="truong">
        <CustomTable :data="truong" row-key="ma_truong" border stripe>
          <el-table-column label="Trường" min-width="220">
            <template #default="{ row }">{{ row.ten_truong || row.ma_truong }}</template>
          </el-table-column>
          <el-table-column label="Điểm trường" width="120" align="center">
            <template #default="{ row }">
              <span v-if="row.diem_truong == null" class="ket-qua-xt__mo">Chưa chấm</span>
              <strong v-else>{{ so(row.diem_truong) }}</strong>
            </template>
          </el-table-column>
          <el-table-column prop="so_chuong_trinh" label="Chương trình xét được" width="160" align="center" />
          <el-table-column prop="so_phu_hop" label="Chương trình phù hợp" width="160" align="center" />
          <el-table-column prop="hang_tot_nhat" label="Hạng cao nhất" width="120" align="center" />
        </CustomTable>
      </el-tab-pane>
    </el-tabs>

    <CustomDialog
      v-model="phuongAnMo"
      :title="chuongTrinhDangXem ? `Các phương án: ${chuongTrinhDangXem.ten_chuong_trinh}` : 'Các phương án'"
      width="90%"
      append-to-body
    >
      <CustomTable v-loading="dangTaiPhuongAn" :data="phuongAn" row-key="id" border max-height="520">
        <el-table-column label="Phương án" min-width="220">
          <template #default="{ row }">
            <div>
              {{ row.ten_cong_thuc }}
              <CustomTag v-if="row.la_tot_nhat" type="success" size="small">Tốt nhất</CustomTag>
            </div>
            <div v-if="row.ma_to_hop" class="ket-qua-xt__mo">Tổ hợp {{ row.ma_to_hop }}</div>
          </template>
        </el-table-column>
        <el-table-column label="Cách tính" min-width="240">
          <template #default="{ row }">{{ row.chi_tiet || '—' }}</template>
        </el-table-column>
        <el-table-column label="Gốc" width="80" align="center">
          <template #default="{ row }">{{ so(row.diem_goc) }}</template>
        </el-table-column>
        <el-table-column label="Cộng" width="70" align="center">
          <template #default="{ row }">{{ so(row.diem_cong) }}</template>
        </el-table-column>
        <el-table-column label="Ưu tiên" width="80" align="center">
          <template #default="{ row }">{{ so(row.diem_uu_tien) }}</template>
        </el-table-column>
        <el-table-column label="Điểm xét" width="110" align="center">
          <template #default="{ row }">
            <template v-if="row.diem_xet != null">
              <strong>{{ so(row.diem_xet) }}</strong><span class="ket-qua-xt__mo">/{{ so(row.thang_diem) }}</span>
            </template>
            <span v-else class="ket-qua-xt__mo">—</span>
          </template>
        </el-table-column>
        <el-table-column label="Kết quả" min-width="220">
          <template #default="{ row }">
            <CustomTag :type="row.du_dieu_kien ? 'success' : 'danger'" size="small">
              {{ row.du_dieu_kien ? 'Đủ điều kiện' : 'Chưa đạt' }}
            </CustomTag>
            <div v-if="row.ly_do_khong_dat" class="ket-qua-xt__mo">{{ row.ly_do_khong_dat }}</div>
          </template>
        </el-table-column>
      </CustomTable>
      <template #footer>
        <CustomButton @click="phuongAnMo = false">Đóng</CustomButton>
      </template>
    </CustomDialog>
  </section>
</template>

<script setup>
/**
 * Kết quả bộ tính xét tuyển của một lượt tìm trường (bước 3.7): xếp hạng chương trình, xếp hạng trường,
 * chi tiết từng phương án. Chỉ có khi năm tìm có đề án "đang áp dụng". Khách xem bằng mã thiết bị.
 */
import { computed, ref, watch } from 'vue'
import {
  fetchKetQuaChuongTrinh,
  fetchKetQuaTruong,
  fetchLanDanhGia,
  fetchPhuongAnChuongTrinh,
} from '@/api/xetTuyen'

const props = defineProps({
  lanDanhGiaId: { type: Number, required: true },
  maThietBi: { type: String, default: null },
})

const soMoiTrang = 10
const lan = ref(null)
const chuongTrinh = ref([])
const tongChuongTrinh = ref(0)
const truong = ref([])
const trang = ref(1)
const tab = ref('chuong_trinh')
const dangTai = ref(false)
const loi = ref('')
const phuongAnMo = ref(false)
const phuongAn = ref([])
const dangTaiPhuongAn = ref(false)
const chuongTrinhDangXem = ref(null)

const thamSoXem = computed(() => ({ ma_thiet_bi: props.maThietBi || undefined }))

function so(v) {
  return v == null ? '—' : Number(v).toLocaleString('vi-VN', { maximumFractionDigits: 2 })
}

function nhanXepLoai(row) {
  if (row.la_xet_thang) return 'Xét tuyển thẳng'
  return row.diem_phu_hop == null ? 'Chưa có điểm chuẩn tham chiếu' : row.xep_loai
}

function mauXepLoai(row) {
  if (row.la_xet_thang) return 'success'
  if (row.diem_phu_hop == null) return 'info'
  if (row.xep_loai === 'Rất phù hợp' || row.xep_loai === 'Phù hợp') return 'success'
  if (row.xep_loai === 'Có thể cân nhắc') return 'warning'
  return 'danger'
}

function thongBaoLoi(error, macDinh) {
  const detail = error?.response?.data?.detail
  return typeof detail === 'string' ? detail : macDinh
}

async function taiChuongTrinh() {
  const data = await fetchKetQuaChuongTrinh(props.lanDanhGiaId, {
    ...thamSoXem.value,
    page: trang.value,
    page_size: soMoiTrang,
  })
  chuongTrinh.value = data.items || []
  tongChuongTrinh.value = data.total || 0
}

async function tai() {
  dangTai.value = true
  loi.value = ''
  trang.value = 1
  try {
    lan.value = await fetchLanDanhGia(props.lanDanhGiaId, props.maThietBi)
    await Promise.all([
      taiChuongTrinh(),
      fetchKetQuaTruong(props.lanDanhGiaId, props.maThietBi).then((data) => {
        truong.value = data || []
      }),
    ])
  } catch (error) {
    lan.value = null
    loi.value = thongBaoLoi(error, 'Không tải được kết quả xét tuyển')
  } finally {
    dangTai.value = false
  }
}

async function moPhuongAn(row) {
  chuongTrinhDangXem.value = row
  phuongAn.value = []
  phuongAnMo.value = true
  dangTaiPhuongAn.value = true
  try {
    phuongAn.value = await fetchPhuongAnChuongTrinh(props.lanDanhGiaId, row.chuong_trinh_id, props.maThietBi)
  } catch (error) {
    loi.value = thongBaoLoi(error, 'Không tải được các phương án')
    phuongAnMo.value = false
  } finally {
    dangTaiPhuongAn.value = false
  }
}

watch(() => props.lanDanhGiaId, tai, { immediate: true })
</script>

<style scoped>
.ket-qua-xt {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
}

.ket-qua-xt__dau {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.ket-qua-xt__tieu-de {
  margin: 0 0 4px;
  font-size: 17px;
}

.ket-qua-xt__phu,
.ket-qua-xt__mo {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.5;
}

.ket-qua-xt__gia-dinh {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--el-color-warning-light-9);
  color: var(--el-text-color-regular);
  font-size: 13px;
  line-height: 1.5;
}

.ket-qua-xt__gia-dinh ul {
  margin: 4px 0 0;
  padding-left: 18px;
}

.ket-qua-xt__ten {
  font-weight: 600;
}

.ket-qua-xt__nhan--tot {
  color: var(--el-color-success);
  font-weight: 600;
}

.ket-qua-xt__duong {
  color: var(--el-color-success);
}

.ket-qua-xt__am {
  color: var(--el-color-danger);
}

.ket-qua-xt__loi {
  margin: 0;
  color: var(--el-color-danger);
}

.ket-qua-xt__trang {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>
