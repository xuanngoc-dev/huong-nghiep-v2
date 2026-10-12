import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { DOI_TUONG_KEY, doiTuongList } from '@/data/doiTuong'
import thcsImage from '@/assets/guest/thcs.jpg'
import thptImage from '@/assets/guest/thpt.jpg'
import phuHuynhImage from '@/assets/guest/phu-huynh.jpg'
import nhaTruongImage from '@/assets/guest/nha-truong.jpg'
import sinhVienImage from '@/assets/guest/sinh-vien.jpg'
import thanhNienImage from '@/assets/guest/thanh-nien.jpg'
import nhaTuyenDungImage from '@/assets/guest/nha-tuyen-dung.jpg'

const images = {
  'hoc-sinh-thcs': thcsImage,
  'hoc-sinh-thpt': thptImage,
  'phu-huynh': phuHuynhImage,
  'nha-truong': nhaTruongImage,
  'sinh-vien': sinhVienImage,
  'thanh-nien-ngoai-truong': thanhNienImage,
  'nha-tuyen-dung': nhaTuyenDungImage,
}

export function useDoiTuongAudiences() {
  const router = useRouter()
  const audiences = doiTuongList.map((item) => ({
    ...item,
    image: images[item.code],
  }))
  const selectedCode = ref(sessionStorage.getItem(DOI_TUONG_KEY) || '')

  function chonDoiTuong(audience) {
    selectedCode.value = audience.code
    sessionStorage.setItem(DOI_TUONG_KEY, audience.code)
    router.push({ name: audience.code })
  }

  return { audiences, selectedCode, chonDoiTuong }
}
