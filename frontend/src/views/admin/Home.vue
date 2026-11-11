<script setup>
import { ref } from 'vue'
import BieuDoCot from '@/components/admin/charts/BieuDoCot.vue'
import BieuDoDuong from '@/components/admin/charts/BieuDoDuong.vue'
import BieuDoTron from '@/components/admin/charts/BieuDoTron.vue'
import TheThongKe from '@/components/admin/dashboard/TheThongKe.vue'
import {
  THANG,
  hoatDong,
  luotGanDay,
  luotTheoThang,
  nhomHolland,
  theThongKe,
  theoDoiTuong,
  topNganh,
  topTinhThanh,
} from '@/data/dashboardMock'

const TRANG_THAI = {
  'hoan-thanh': { label: 'Hoàn thành', type: 'success' },
  'dang-lam': { label: 'Đang làm', type: 'warning' },
  'bo-do': { label: 'Bỏ dở', type: 'info' },
}

const khoangThoiGian = ref([])
const kieuBieuDo = ref('area')
const luotToiDa = Math.max(...topTinhThanh.map((item) => item.luot))
</script>

<template>
  <div class="dashboard">
    <div class="dashboard__header">
      <div>
        <h1 class="dashboard__title">Tổng quan</h1>
        <p class="dashboard__subtitle">Số liệu hoạt động định hướng nghề nghiệp trên toàn hệ thống</p>
      </div>
      <div class="dashboard__filters">
        <el-date-picker
          v-model="khoangThoiGian"
          type="monthrange"
          range-separator="–"
          start-placeholder="Từ tháng"
          end-placeholder="Đến tháng"
          format="MM/YYYY"
        />
        <el-button icon="Refresh">Làm mới</el-button>
        <el-button type="primary" icon="Download">Xuất báo cáo</el-button>
      </div>
    </div>

    <el-row :gutter="16" class="dashboard__row">
      <el-col v-for="item in theThongKe" :key="item.key" :xs="24" :sm="12" :lg="6">
        <TheThongKe v-bind="item" />
      </el-col>
    </el-row>

    <el-row :gutter="16" class="dashboard__row">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="dashboard__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Lượt trắc nghiệm & tài khoản mới</span>
                <span class="card-header__desc">Theo tháng, năm 2026</span>
              </div>
              <el-radio-group v-model="kieuBieuDo" size="small">
                <el-radio-button value="area">Vùng</el-radio-button>
                <el-radio-button value="line">Đường</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <BieuDoDuong :type="kieuBieuDo" :series="luotTheoThang" :categories="THANG" :height="320" donVi="lượt" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="dashboard__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Phân bố nhóm Holland</span>
                <span class="card-header__desc">Nhóm tính cách nổi trội của người làm bài</span>
              </div>
            </div>
          </template>
          <BieuDoTron
            :labels="nhomHolland.labels"
            :values="nhomHolland.values"
            :colors="nhomHolland.colors"
            :height="340"
            nhanTong="Lượt làm bài"
            donVi="lượt"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="dashboard__row">
      <el-col :xs="24" :md="12" :xl="8">
        <el-card shadow="never" class="dashboard__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Ngành được gợi ý nhiều nhất</span>
                <span class="card-header__desc">Top 8 ngành đào tạo</span>
              </div>
            </div>
          </template>
          <BieuDoCot horizontal :series="topNganh.series" :categories="topNganh.categories" :height="320" donVi="lượt" />
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12" :xl="8">
        <el-card shadow="never" class="dashboard__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Kết quả theo đối tượng</span>
                <span class="card-header__desc">Hoàn thành / bỏ dở bài trắc nghiệm</span>
              </div>
            </div>
          </template>
          <BieuDoCot
            stacked
            :series="theoDoiTuong.series"
            :categories="theoDoiTuong.categories"
            :colors="['#1f7a4d', '#c9d3cd']"
            :height="320"
            donVi="lượt"
          />
        </el-card>
      </el-col>
      <el-col :xs="24" :xl="8">
        <el-card shadow="never" class="dashboard__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Tỉnh thành hoạt động nhiều</span>
                <span class="card-header__desc">Lượt trắc nghiệm và tỷ lệ hoàn thành</span>
              </div>
            </div>
          </template>
          <ul class="top-list">
            <li v-for="(item, index) in topTinhThanh" :key="item.ten" class="top-list__item">
              <span class="top-list__rank">{{ index + 1 }}</span>
              <div class="top-list__body">
                <div class="top-list__line">
                  <span class="top-list__name">{{ item.ten }}</span>
                  <span class="top-list__value">{{ item.luot.toLocaleString('vi-VN') }}</span>
                </div>
                <el-progress :percentage="Math.round((item.luot / luotToiDa) * 100)" :show-text="false" :stroke-width="6" />
                <div class="top-list__meta">
                  <span>Miền {{ item.khuVuc }}</span>
                  <span>Hoàn thành {{ item.tyLe }}%</span>
                </div>
              </div>
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="dashboard__row">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="dashboard__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Lượt trắc nghiệm gần đây</span>
                <span class="card-header__desc">Cập nhật theo thời gian thực</span>
              </div>
              <el-button link type="primary" @click="$router.push({ name: 'admin-lich-su-trac-nghiem' })">
                Xem tất cả
              </el-button>
            </div>
          </template>
          <el-table :data="luotGanDay" style="width: 100%">
            <el-table-column label="Người làm bài" min-width="180">
              <template #default="{ row }">
                <div class="user-cell">
                  <el-avatar :size="32">{{ row.hoTen.split(' ').at(-1)[0] }}</el-avatar>
                  <div>
                    <div class="user-cell__name">{{ row.hoTen }}</div>
                    <div class="user-cell__meta">{{ row.doiTuong }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Mã Holland" width="110" align="center">
              <template #default="{ row }">
                <el-tag effect="plain" disable-transitions>{{ row.maHolland }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="nganh" label="Ngành gợi ý" min-width="170" show-overflow-tooltip />
            <el-table-column prop="thoiGian" label="Thời gian" width="150" />
            <el-table-column label="Trạng thái" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="TRANG_THAI[row.trangThai].type" disable-transitions>
                  {{ TRANG_THAI[row.trangThai].label }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="dashboard__card">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-header__title">Hoạt động hệ thống</span>
                <span class="card-header__desc">Thao tác quản trị mới nhất</span>
              </div>
            </div>
          </template>
          <el-timeline class="activity">
            <el-timeline-item
              v-for="item in hoatDong"
              :key="item.id"
              :type="item.type"
              :timestamp="`${item.thoiGian} · ${item.nguoi}`"
            >
              {{ item.noiDung }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard__header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.dashboard__title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.3;
  color: var(--el-text-color-primary);
}

.dashboard__subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.dashboard__filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.dashboard__filters :deep(.el-date-editor) {
  width: 260px;
}

.dashboard__filters .el-button + .el-button {
  margin-left: 0;
}

.dashboard__row > .el-col {
  margin-bottom: 16px;
}

.dashboard__card {
  height: 100%;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-header__title {
  display: block;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.card-header__desc {
  display: block;
  margin-top: 2px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.top-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.top-list__item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.top-list__rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-color-primary);
  background: var(--brand-accent-soft);
}

.top-list__body {
  flex: 1;
  min-width: 0;
}

.top-list__line,
.top-list__meta {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.top-list__line {
  margin-bottom: 6px;
  font-size: 14px;
}

.top-list__name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.top-list__value {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.top-list__meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-cell .el-avatar {
  flex-shrink: 0;
  color: var(--el-color-primary);
  background: var(--brand-accent-soft);
}

.user-cell__name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.user-cell__meta {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.activity {
  padding-left: 2px;
}

.activity :deep(.el-timeline-item:last-child) {
  padding-bottom: 0;
}

@media (max-width: 640px) {
  .dashboard__filters,
  .dashboard__filters :deep(.el-date-editor) {
    width: 100%;
  }
}
</style>
