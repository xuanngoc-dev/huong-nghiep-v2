<template>
  <div class="tong-quan">
    <header class="tong-quan__dau">
      <div>
        <h1 class="tong-quan__tieu-de">Xin chào, {{ auth.displayName || 'bạn' }}</h1>
        <p class="tong-quan__phu">Tổng quan số dư và hoạt động gần đây của tài khoản.</p>
      </div>
      <div class="tong-quan__hanh-dong">
        <CustomButton @click="router.push({ name: 'ho-so' })">
          <CustomIcon><Postcard /></CustomIcon>
          <span>Hồ sơ năng lực</span>
        </CustomButton>
        <CustomButton type="primary" @click="router.push({ name: 'nap-tien' })">
          <CustomIcon><Wallet /></CustomIcon>
          <span>Nạp tiền</span>
        </CustomButton>
      </div>
    </header>

    <TheSoDuTongQuan :so-du="soDu" :luot-mien-phi="luotMienPhi" />
    <p v-if="loiSoDu" class="tong-quan__loi">{{ loiSoDu }}</p>

    <BieuDoSuDung />

    <div class="tong-quan__gan-day">
      <DanhSachGanDay
        tieu-de="Tìm trường gần đây"
        :icon="School"
        :items="timTruong.items"
        :dang-tai="timTruong.dangTai"
        :loi="timTruong.loi"
        :xem-tat-ca="{ name: 'lich-su-tim-truong' }"
        trong="Bạn chưa tìm trường phù hợp lần nào."
      />
      <DanhSachGanDay
        tieu-de="Khảo sát gần đây"
        :icon="DataAnalysis"
        :items="khaoSat.items"
        :dang-tai="khaoSat.dangTai"
        :loi="khaoSat.loi"
        :xem-tat-ca="{ name: 'lich-su-trac-nghiem' }"
        trong="Bạn chưa làm khảo sát nào."
      />
      <DanhSachGanDay
        tieu-de="Nạp tiền gần đây"
        :icon="Tickets"
        :items="napTien.items"
        :dang-tai="napTien.dangTai"
        :loi="napTien.loi"
        :xem-tat-ca="{ name: 'lich-su-nap-tien' }"
        trong="Bạn chưa có giao dịch nạp tiền nào."
      />
    </div>
  </div>
</template>

<script setup>
/**
 * Trang tổng quan thành viên: thẻ số dư, biểu đồ lượt dùng chức năng và các hoạt động gần đây
 * (tìm trường, khảo sát, nạp tiền).
 */
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { DataAnalysis, Postcard, School, Tickets, Wallet } from '@element-plus/icons-vue'
import BieuDoSuDung from '@/components/member/tong-quan/BieuDoSuDung.vue'
import DanhSachGanDay from '@/components/member/tong-quan/DanhSachGanDay.vue'
import TheSoDuTongQuan from '@/components/member/tong-quan/TheSoDuTongQuan.vue'
import { fetchHoSo } from '@/api/hoSo'
import { fetchNapTienCuaToi } from '@/api/napTien'
import { fetchLichSuKhaoSat } from '@/api/phienKhaoSat'
import { fetchLichSuTimTruongCuaToi, fetchLuotTimTruong } from '@/api/timTruongPhuHop'
import { TRANG_THAI_NAP_TIEN, hienThoiGian, hienTien, timTheoGiaTri } from '@/data/napTien'
import { useAuthStore } from '@/stores/auth'

defineOptions({ name: 'MemberTongQuan' })

const SO_MUC = 5
const LOAI_LUOT = {
  mien_phi: { nhan: 'Miễn phí', loai: 'success' },
  tra_phi: { nhan: 'Trả phí', loai: 'warning' },
  khuyen_mai: { nhan: 'Khuyến mãi', loai: 'primary' },
}

const auth = useAuthStore()
const router = useRouter()
const soDu = ref(null)
const loiSoDu = ref('')
const luotMienPhi = ref(null)
const timTruong = reactive({ items: [], dangTai: false, loi: '' })
const khaoSat = reactive({ items: [], dangTai: false, loi: '' })
const napTien = reactive({ items: [], dangTai: false, loi: '' })

// Tải một danh sách gần đây vào `khoi` (items/dangTai/loi), chuyển từng dòng bằng `chuyen`.
async function taiGanDay(khoi, goi, chuyen, thongBaoLoi) {
  khoi.dangTai = true
  khoi.loi = ''
  try {
    const data = await goi()
    khoi.items = (data.items || []).map(chuyen)
  } catch {
    khoi.loi = thongBaoLoi
  } finally {
    khoi.dangTai = false
  }
}

function dongTimTruong(item) {
  const luot = LOAI_LUOT[item.loai_luot]
  return {
    key: item.id,
    ten: item.ten_nganh || item.ma_nganh,
    phu: `${item.so_truong_phu_hop_so_bo}/${item.so_truong_tim_thay} trường phù hợp · năm ${item.nam_tuyen_sinh}`,
    nhan: luot?.nhan,
    nhanLoai: luot?.loai,
    thoiGian: hienThoiGian(item.ngay_tao),
  }
}

function dongKhaoSat(item) {
  return {
    key: item.ssid,
    ten: item.ma_noi_bat ? `Khảo sát Holland · ${item.ma_noi_bat}` : 'Khảo sát Holland',
    phu: `Đã trả lời ${item.so_da_tra_loi}/${item.so_cau_hoi} câu`,
    nhan: item.da_xong ? 'Hoàn thành' : 'Đang làm',
    nhanLoai: item.da_xong ? 'success' : 'warning',
    thoiGian: hienThoiGian(item.created_at),
  }
}

function dongNapTien(item) {
  const trangThai = timTheoGiaTri(TRANG_THAI_NAP_TIEN, item.trang_thai)
  return {
    key: item.id,
    ten: item.ten_goi_cuoc,
    phu: `${hienTien(item.so_tien_nap)} · ${item.ma_giao_dich}`,
    nhan: trangThai.label,
    nhanLoai: trangThai.tag,
    thoiGian: hienThoiGian(item.created_at),
  }
}

async function taiSoDu() {
  try {
    soDu.value = await fetchHoSo({ skipLoading: true })
  } catch {
    loiSoDu.value = 'Không tải được số dư tài khoản.'
  }
}

async function taiLuotMienPhi() {
  try {
    luotMienPhi.value = await fetchLuotTimTruong()
  } catch {
    luotMienPhi.value = null
  }
}

onMounted(() => {
  const trang = { page: 1, page_size: SO_MUC }
  taiSoDu()
  taiLuotMienPhi()
  taiGanDay(timTruong, () => fetchLichSuTimTruongCuaToi(trang), dongTimTruong, 'Không tải được lịch sử tìm trường.')
  taiGanDay(
    khaoSat,
    () => fetchLichSuKhaoSat(trang, { skipLoading: true }),
    dongKhaoSat,
    'Không tải được lịch sử khảo sát.',
  )
  taiGanDay(napTien, () => fetchNapTienCuaToi(trang), dongNapTien, 'Không tải được lịch sử nạp tiền.')
})
</script>

<style scoped>
.tong-quan {
  display: grid;
  gap: 16px;
}

.tong-quan__dau {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.tong-quan__tieu-de {
  margin: 0 0 4px;
  font-size: 20px;
  line-height: 1.4;
}

.tong-quan__phu,
.tong-quan__loi {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.tong-quan__hanh-dong {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tong-quan__gan-day {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}
</style>
