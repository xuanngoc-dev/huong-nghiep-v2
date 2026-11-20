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

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { doiTuongList } from '@/data/doiTuong'
import {
  TIEN_TO_HOC_SINH,
  doiTenRouteThpt,
  routeNameDinhHuongThpt,
} from '@/components/guest/doi-tuong/HocSinhThpt/routes'

const route = useRoute()

const trangChu = { label: 'Trang chủ', to: { name: 'home' } }
const chonDoiTuong = { label: 'Chọn đối tượng', to: { name: 'chon-doi-tuong' } }
const hocSinhThpt = { label: 'Học sinh THPT', to: { name: 'hoc-sinh-thpt' } }
const phuHuynh = { label: 'Phụ huynh', to: { name: 'phu-huynh' } }
const phuHuynhThpt = { label: 'Con học Trung học phổ thông', to: { name: 'phu-huynh-thpt' } }
const phuHuynhLop12 = { label: 'Con học lớp 12', to: { name: 'phu-huynh-thpt-lop-12' } }

const muc = computed(() => {
  if (route.name === 'home') return []

  const hienTai = { label: route.meta.title || 'Trang hiện tại' }

  if (route.name === 'chon-doi-tuong') return [trangChu, hienTai]

  if (route.meta.doiTuong) {
    const doiTuong = doiTuongList.find((item) => item.code === route.meta.doiTuong)
    return [trangChu, chonDoiTuong, { label: doiTuong?.name || hienTai.label }]
  }

  if (route.meta.giaiDoanCon) {
    const goc = [trangChu, chonDoiTuong, phuHuynh]
    if (route.meta.capHoc === 'thpt') return [...goc, phuHuynhThpt, hienTai]
    return [...goc, hienTai]
  }

  if (route.meta.dinhHuong) {
    // Cùng một luồng định hướng THPT, gắn dưới nhánh học sinh hoặc nhánh phụ huynh (meta.tienTo).
    const tienTo = route.meta.tienTo || TIEN_TO_HOC_SINH
    const ten = (tenHocSinh) => doiTenRouteThpt(tenHocSinh, tienTo)
    const goc =
      tienTo === TIEN_TO_HOC_SINH
        ? [trangChu, hocSinhThpt]
        : [trangChu, chonDoiTuong, phuHuynh, phuHuynhThpt, phuHuynhLop12]
    const thiDaiHoc = { label: 'Thi Đại học & cao đẳng', to: { name: ten('thpt-thi-dai-hoc') } }
    const daCoNganh = { label: 'Đã có ngành nghề mong muốn', to: { name: ten('thpt-thi-dai-hoc-da-co') } }

    if (route.name === routeNameDinhHuongThpt(route.meta.dinhHuong, tienTo)) return [...goc, hienTai]
    if (route.meta.dinhHuong === 'thi-dai-hoc') {
      if (route.name === ten('thpt-thi-dai-hoc-chon-truong')) return [...goc, thiDaiHoc, daCoNganh, hienTai]
      if (route.name === ten('thpt-thi-dai-hoc-truong-phu-hop')) {
        return [
          ...goc,
          thiDaiHoc,
          daCoNganh,
          {
            label: 'Chọn trường',
            to: { name: ten('thpt-thi-dai-hoc-chon-truong'), params: { maNganh: route.params.maNganh } },
          },
          hienTai,
        ]
      }
      return [...goc, thiDaiHoc, hienTai]
    }
    if (route.meta.dinhHuong === 'di-lam') {
      return [...goc, { label: 'Đi làm ngay sau khi tốt nghiệp', to: { name: ten('thpt-di-lam') } }, hienTai]
    }
    return [...goc, hienTai]
  }

  return [trangChu, hienTai]
})
</script>
