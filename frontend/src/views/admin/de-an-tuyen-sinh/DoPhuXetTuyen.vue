<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInputNumber
          v-model="filters.nam"
          class="filter-year"
          :min="2000"
          :max="2100"
          :controls="false"
          placeholder="Nhập năm tuyển sinh"
          @change="onSearch"
        />
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo mã, tên trường"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect v-model="filters.trang_thai" class="filter-status" placeholder="Chọn trạng thái" clearable @change="onSearch">
          <CustomOption v-for="(tt, ma) in TRANG_THAI" :key="ma" :label="tt.label" :value="Number(ma)" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <section v-if="tong" class="do-phu__tong" aria-label="Tổng quan">
      <div class="do-phu__o">
        <span class="do-phu__nhan">Đề án năm {{ nam }}</span>
        <strong class="do-phu__so">{{ tong.so_de_an }}</strong>
        <span class="do-phu__phu">
          {{ tong.theo_trang_thai['2'] || 0 }} đang áp dụng · {{ tong.theo_trang_thai['1'] || 0 }} thử nghiệm ·
          {{ tong.theo_trang_thai['0'] || 0 }} chưa chuẩn hóa
        </span>
      </div>
      <div v-for="cs in CHI_SO" :key="cs.key" class="do-phu__o">
        <span class="do-phu__nhan">{{ cs.label }}</span>
        <strong class="do-phu__so">{{ phanTram(tong[cs.key], tong.so_chuong_trinh) }}</strong>
        <span class="do-phu__phu">{{ tong[cs.key] }} / {{ tong.so_chuong_trinh }} chương trình</span>
      </div>
      <div class="do-phu__o">
        <span class="do-phu__nhan">Quy định chưa mô hình hóa</span>
        <strong class="do-phu__so">{{ tong.so_quy_dinh_chua_mo_hinh_hoa }}</strong>
        <span class="do-phu__phu">theo lần import quy tắc gần nhất</span>
      </div>
    </section>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Độ phủ theo trường</h2>
      </div>
      <CustomTable :loading="loading" :data="rows" row-key="de_an_id" border stripe>
        <el-table-column type="expand" width="40">
          <template #default="{ row }">
            <div class="do-phu__chi-tiet">
              <p v-if="!row.lan_import_cuoi">Chưa import quy tắc xét tuyển.</p>
              <template v-else>
                <p>Import quy tắc gần nhất: {{ hienThoiGian(row.lan_import_cuoi) }} · {{ row.so_cong_thuc }} công thức</p>
                <p v-if="!row.quy_dinh_chua_mo_hinh_hoa.length">Mọi quy định đã mô hình hóa.</p>
                <template v-else>
                  <p><strong>Quy định chưa mô hình hóa ({{ row.quy_dinh_chua_mo_hinh_hoa.length }}):</strong></p>
                  <ul>
                    <li v-for="(qd, i) in row.quy_dinh_chua_mo_hinh_hoa" :key="i">
                      <template v-if="qd.ma">{{ qd.ma }}: </template>{{ qd.mo_ta }}
                    </li>
                  </ul>
                </template>
              </template>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Trường" min-width="220">
          <template #default="{ row }">
            <strong>{{ row.ma_truong }}</strong><span v-if="row.ten_truong"> — {{ row.ten_truong }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Trạng thái" width="140" align="center">
          <template #default="{ row }">
            <CustomTag :type="TRANG_THAI[row.trang_thai_xet_tuyen]?.tag" size="small">
              {{ TRANG_THAI[row.trang_thai_xet_tuyen]?.label }}
            </CustomTag>
          </template>
        </el-table-column>
        <el-table-column prop="so_chuong_trinh" label="Chương trình" width="110" align="center" />
        <el-table-column v-for="cs in CHI_SO" :key="cs.key" :label="cs.label" min-width="140">
          <template #default="{ row }">
            <div class="do-phu__thanh">
              <el-progress
                :percentage="soPhanTram(row[cs.key], row.so_chuong_trinh)"
                :stroke-width="8"
                :show-text="false"
                :aria-label="`${cs.label}: ${row[cs.key]} / ${row.so_chuong_trinh}`"
              />
              <span>{{ row[cs.key] }}/{{ row.so_chuong_trinh }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Chưa mô hình hóa" width="140" align="center">
          <template #default="{ row }">{{ row.lan_import_cuoi ? row.quy_dinh_chua_mo_hinh_hoa.length : '—' }}</template>
        </el-table-column>
        <template #empty>
          <CustomEmpty :description="`Không có đề án tuyển sinh năm ${nam || ''} khớp bộ lọc.`" />
        </template>
      </CustomTable>

      <div class="pager">
        <CustomPagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="load"
          @size-change="onSearch"
        />
      </div>
    </CustomCard>
  </div>
</template>

<script setup>
/**
 * Độ phủ dữ liệu xét tuyển (bước 5.5): tiến độ nhập liệu theo năm — đề án theo trạng thái, tỷ lệ chương trình có
 * mã ngành, điểm chuẩn, học phí, vị trí (đúng cách bộ tính dùng), quy định chưa mô hình hóa theo trường.
 */
import { onMounted, reactive, ref } from 'vue'
import { baoLoi } from '@/utils/baoLoi'
import { fetchDoPhuXetTuyen } from '@/api/xetTuyen'
import { hienThoiGian } from '@/data/napTien'

const TRANG_THAI = {
  0: { label: 'Chưa chuẩn hóa', tag: 'info' },
  1: { label: 'Thử nghiệm', tag: 'warning' },
  2: { label: 'Đang áp dụng', tag: 'success' },
}
const CHI_SO = [
  { key: 'co_ma_nganh', label: 'Có mã ngành' },
  { key: 'co_diem_chuan', label: 'Có điểm chuẩn' },
  { key: 'co_hoc_phi', label: 'Có học phí' },
  { key: 'co_vi_tri', label: 'Có vị trí (tỉnh)' },
]

const loading = ref(false)
const rows = ref([])
const tong = ref(null)
const nam = ref(null)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filters = reactive({ nam: null, q: '', trang_thai: '' })

function soPhanTram(phan, toan) {
  return toan ? Math.round((phan / toan) * 100) : 0
}

function phanTram(phan, toan) {
  return toan ? `${soPhanTram(phan, toan)}%` : '—'
}

function thongBaoLoi(error, macDinh) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return macDinh
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.nam) params.nam = filters.nam
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.trang_thai !== '' && filters.trang_thai !== null) params.trang_thai_xet_tuyen = filters.trang_thai
    const data = await fetchDoPhuXetTuyen(params)
    rows.value = data.items
    total.value = data.total
    tong.value = data.tong
    nam.value = data.nam
    if (!filters.nam) filters.nam = data.nam
  } catch (error) {
    baoLoi(thongBaoLoi(error, 'Không tải được độ phủ dữ liệu xét tuyển'))
  } finally {
    loading.value = false
  }
}

function onSearch() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  load()
}

onMounted(load)
</script>

<style scoped>
.do-phu__tong {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.do-phu__o {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-bg-color);
}

.do-phu__nhan,
.do-phu__phu {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.do-phu__so {
  color: var(--el-text-color-primary);
  font-size: 24px;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.do-phu__thanh {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}

.do-phu__thanh .el-progress {
  flex: 1;
  min-width: 48px;
}

.do-phu__chi-tiet {
  padding: 4px 16px;
  font-size: 13px;
  line-height: 1.6;
}

.do-phu__chi-tiet p {
  margin: 0 0 4px;
}

.do-phu__chi-tiet ul {
  margin: 0;
  padding-left: 18px;
}
</style>
