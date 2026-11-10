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
      if (route.name === 'thpt-thi-dai-hoc-truong-phu-hop') {
        return [
          ...goc,
          thiDaiHoc,
          daCoNganh,
          {
            label: 'Chọn trường',
            to: { name: 'thpt-thi-dai-hoc-chon-truong', params: { maNganh: route.params.maNganh } },
          },
          hienTai,
        ]
      }
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
