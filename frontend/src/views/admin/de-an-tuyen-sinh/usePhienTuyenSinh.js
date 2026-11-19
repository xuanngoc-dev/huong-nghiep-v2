import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { layPhienTuyenSinh } from '@/api/thuThapTuyenSinh'
import { loiPhien } from './thu-thap-du-lieu'

function soNguyenDuong(giaTri) {
  const so = typeof giaTri === 'string' && /^\d+$/.test(giaTri) ? Number(giaTri) : 0
  return Number.isSafeInteger(so) && so > 0 ? so : null
}

export function usePhienTuyenSinh(choPhepChonPhienBan = false, dangGuiBanNhap = () => false) {
  const route = useRoute()
  const id = computed(() => soNguyenDuong(route.query.phien))
  const phienBan = computed(() => choPhepChonPhienBan ? soNguyenDuong(route.query.phien_ban) : null)
  const chiTiet = ref(null)
  const dangTai = ref(false)
  const loiTai = ref('')
  const dangKiemTraBanNhap = ref(false)
  const dangTaoBanNhap = computed(() => Boolean(id.value && (chiTiet.value?.dang_tao_ban_nhap || dangGuiBanNhap(id.value))))
  let thuTuTai = 0

  async function tai({ amTham = false } = {}) {
    if (amTham && dangTai.value) return
    const thuTu = ++thuTuTai
    if (!amTham) {
      loiTai.value = ''
      dangTai.value = Boolean(id.value)
      chiTiet.value = null
    }
    if (!id.value) return
    try {
      const ketQua = await layPhienTuyenSinh(id.value, phienBan.value || undefined)
      if (thuTu === thuTuTai && ketQua.id === id.value) {
        chiTiet.value = ketQua
        dangKiemTraBanNhap.value = false
        return ketQua
      }
    } catch (error) {
      if (!amTham && thuTu === thuTuTai) loiTai.value = loiPhien(error).noiDung
    } finally {
      if (thuTu === thuTuTai) dangTai.value = false
    }
  }

  function kiemTraLaiBanNhap(mayChuDangTao) {
    if (mayChuDangTao && chiTiet.value) {
      chiTiet.value = { ...chiTiet.value, dang_tao_ban_nhap: true }
    }
    dangKiemTraBanNhap.value = true
    return tai({ amTham: true })
  }

  function apDung(ketQua) {
    if (ketQua.id !== id.value || phienBan.value) return false
    thuTuTai += 1
    chiTiet.value = ketQua
    dangTai.value = false
    loiTai.value = ''
    dangKiemTraBanNhap.value = false
    return true
  }

  watch([id, phienBan], () => {
    dangKiemTraBanNhap.value = false
    tai()
  }, { immediate: true })

  watch([id, phienBan, () => dangTaoBanNhap.value || dangKiemTraBanNhap.value], ([phienId, , theoDoi], _, onCleanup) => {
    if (!phienId || !theoDoi) return
    let conTheoDoi = true
    let henGio
    async function capNhat() {
      await tai({ amTham: true })
      if (conTheoDoi) henGio = setTimeout(capNhat, 2000)
    }
    henGio = setTimeout(capNhat, 2000)
    onCleanup(() => {
      conTheoDoi = false
      clearTimeout(henGio)
    })
  }, { immediate: true })

  return { id, phienBan, chiTiet, dangTai, loiTai, dangTaoBanNhap, dangKiemTraBanNhap, tai, kiemTraLaiBanNhap, apDung }
}
