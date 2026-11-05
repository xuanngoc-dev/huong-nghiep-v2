<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { doiTuongList } from '@/data/doiTuong'
import { routeNameDinhHuongThpt } from '@/components/guest/doi-tuong/HocSinhThpt/routes'

const route = useRoute()

const trangChu = { label: 'Trang chủ', to: { name: 'home' } }
const chonDoiTuong = { label: 'Chọn đối tượng', to: { name: 'chon-doi-tuong' } }
const hocSinhThpt = { label: 'Học sinh THPT', to: { name: 'hoc-sinh-thpt' } }
const thiDaiHoc = { label: 'Thi Đại học & cao đẳng', to: { name: 'thpt-thi-dai-hoc' } }
const daCoNganh = { label: 'Đã có ngành nghề mong muốn', to: { name: 'thpt-thi-dai-hoc-da-co' } }

const muc = computed(() => {
  if (route.name === 'home') return []

  const hienTai = { label: route.meta.title || 'Trang hiện tại' }

  if (route.name === 'chon-doi-tuong') return [trangChu, hienTai]

  if (route.meta.doiTuong) {
    const doiTuong = doiTuongList.find((item) => item.code === route.meta.doiTuong)
    return [trangChu, chonDoiTuong, { label: doiTuong?.name || hienTai.label }]
  }

  if (route.meta.dinhHuong) {
    const goc = [trangChu, hocSinhThpt]
    if (route.name === routeNameDinhHuongThpt(route.meta.dinhHuong)) return [...goc, hienTai]
    if (route.meta.dinhHuong === 'thi-dai-hoc') {
      if (route.name === 'thpt-thi-dai-hoc-chon-truong') return [...goc, thiDaiHoc, daCoNganh, hienTai]
      return [...goc, thiDaiHoc, hienTai]
    }
    return [...goc, hienTai]
  }

  return [trangChu, hienTai]
})
</script>

<template>
  <nav v-if="muc.length" class="guest-breadcrumb" aria-label="Đường dẫn">
    <div class="container-fluid">
      <ol>
        <li v-for="(item, index) in muc" :key="`${item.label}-${index}`">
          <RouterLink v-if="item.to" :to="item.to">{{ item.label }}</RouterLink>
          <span v-else aria-current="page">{{ item.label }}</span>
        </li>
      </ol>
    </div>
  </nav>
</template>

<style scoped>
.guest-breadcrumb {
  border-bottom: 1px solid rgba(var(--guest-primary-rgb), 0.16);
  background: #f6fbf7;
}

.guest-breadcrumb ol {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0;
  margin: 0;
  padding: 10px 0;
  list-style: none;
  font-size: 0.92rem;
  line-height: 1.4;
}

.guest-breadcrumb li:not(:last-child)::after {
  content: '/';
  margin: 0 8px;
  color: #8aa394;
}

.guest-breadcrumb a {
  color: var(--guest-primary);
  font-weight: 400;
  text-decoration: none;
}

.guest-breadcrumb a:hover {
  text-decoration: underline;
}

.guest-breadcrumb [aria-current='page'] {
  padding: 2px 8px;
  border-radius: 999px;
  /* background: rgba(var(--guest-primary-rgb), 0.14); */
  color: var(--guest-primary);
  font-weight: 600;
}
</style>
