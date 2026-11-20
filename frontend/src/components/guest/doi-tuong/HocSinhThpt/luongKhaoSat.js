import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { fetchNganhPhuHop, fetchNhomNghePhuHop } from '@/api/phienKhaoSat'

// Luồng khảo sát Holland theo hướng đi (route.meta.dinhHuong). Tên route viết theo nhánh học sinh (`thpt-...`),
// component đổi sang nhánh đang đứng bằng tenRoute. `buocCuoi`: các bước sau phần câu hỏi; bước đầu tiên là nơi
// chuyển tới khi phân tích xong, `phanTich` gọi trước để chắc chắn API kết quả chạy được.
export const LUONG_KHAO_SAT = {
  'thi-dai-hoc': {
    huongDan: 'thpt-thi-dai-hoc-huong-dan-khao-sat',
    lamBai: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    phanTich: fetchNganhPhuHop,
    buocCuoi: [
      { id: 'nganh-phu-hop', ten: 'Ngành phù hợp', route: 'thpt-thi-dai-hoc-nganh-phu-hop' },
      { id: 'ket-qua', ten: 'Kết quả', route: 'thpt-thi-dai-hoc-ket-qua' },
    ],
  },
  'di-lam': {
    huongDan: 'thpt-di-lam-huong-dan-khao-sat',
    lamBai: 'thpt-di-lam-lam-trac-nghiem',
    phanTich: fetchNhomNghePhuHop,
    buocCuoi: [{ id: 'nhom-nghe-phu-hop', ten: 'Nhóm nghề phù hợp', route: 'thpt-di-lam-nhom-nghe-phu-hop' }],
  },
}

export function layLuongKhaoSat(dinhHuong) {
  return LUONG_KHAO_SAT[dinhHuong] || LUONG_KHAO_SAT['thi-dai-hoc']
}

export function useLuongKhaoSat() {
  const route = useRoute()
  const luong = computed(() => layLuongKhaoSat(route.meta.dinhHuong))
  const idBuocCuoi = computed(() => new Set(luong.value.buocCuoi.map((step) => step.id)))

  // Bước phần câu hỏi (id là id loại câu hỏi), khác các bước kết quả ở cuối.
  function laBuocCauHoi(step) {
    return !idBuocCuoi.value.has(step.id)
  }

  function timBuocCuoi(id) {
    return luong.value.buocCuoi.find((step) => step.id === id) || null
  }

  return { luong, laBuocCauHoi, timBuocCuoi }
}
