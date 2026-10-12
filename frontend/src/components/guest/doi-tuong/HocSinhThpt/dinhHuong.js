import diLamImage from '@/assets/guest/nha-tuyen-dung.jpg'
import duHocNgheImage from '@/assets/guest/nha-truong.jpg'
import duHocImage from '@/assets/guest/sinh-vien.jpg'
import thiDaiHocImage from '@/assets/guest/thpt.jpg'
import khoiNghiepImage from '@/assets/guest/thanh-nien.jpg'
import xuatKhauImage from '@/assets/guest/thcs.jpg'

export const DINH_HUONG_THPT_KEY = 'dinh_huong_thpt'

export const dinhHuongThptList = [
  {
    code: 'di-lam',
    name: 'Đi làm ngay sau khi tốt nghiệp',
    description: 'Bắt đầu làm việc sớm và tích lũy kinh nghiệm thay vì học tiếp.',
    image: diLamImage,
  },
  {
    code: 'du-hoc-nghe',
    name: 'Du học nghề',
    description: 'Học nghề ở nước ngoài, vừa đào tạo vừa thực hành.',
    image: duHocNgheImage,
  },
  {
    code: 'du-hoc',
    name: 'Du học',
    description: 'Học đại học hoặc cao đẳng tại nước ngoài.',
    image: duHocImage,
  },
  {
    code: 'thi-dai-hoc',
    name: 'Thi Đại học & cao đẳng',
    description: 'Ôn thi và chọn ngành, trường trong nước.',
    image: thiDaiHocImage,
  },
  {
    code: 'khoi-nghiep',
    name: 'Khởi nghiệp',
    description: 'Tự xây dựng ý tưởng và bắt đầu công việc của riêng bạn.',
    image: khoiNghiepImage,
  },
  {
    code: 'xuat-khau-lao-dong',
    name: 'Xuất khẩu lao động',
    description: 'Đi làm việc có thời hạn ở nước ngoài theo chương trình lao động.',
    image: xuatKhauImage,
  },
]
