import chuaCoImage from '@/assets/guest/thanh-nien.jpg'
import daCoImage from '@/assets/guest/sinh-vien.jpg'
import phanVanImage from '@/assets/guest/phu-huynh.jpg'

export const GIAI_DOAN_THI_DAI_HOC_KEY = 'giai_doan_thi_dai_hoc'

export const giaiDoanThiDaiHocList = [
  {
    code: 'chua-co',
    name: 'Chưa có ngành nghề phù hợp',
    description: 'Bạn chưa xác định ngành muốn theo và cần gợi ý từ sở thích, năng lực.',
    image: '/api/v1/thu-vien/tep/images/nganh_nghe/chuaCoNganhNghe.webp' + '?v=' + new Date().getTime(),
  },
  {
    code: 'da-co',
    name: 'Đã có ngành nghề mong muốn',
    description: 'Bạn đã chọn ngành và muốn đối chiếu trường, tổ hợp môn và cách xét tuyển.',
    image: '/api/v1/thu-vien/tep/images/nganh_nghe/daCoNganhNghe.webp' + '?v=' + new Date().getTime(),
  },
  {
    code: 'phan-van',
    name: 'Đang phân vân giữa vài ngành nghề',
    description: 'Bạn đang cân nhắc một vài ngành và cần so sánh để chốt hướng.',
    image: '/api/v1/thu-vien/tep/images/nganh_nghe/phanVanNganhNghe.webp' + '?v=' + new Date().getTime(),
  },
]
