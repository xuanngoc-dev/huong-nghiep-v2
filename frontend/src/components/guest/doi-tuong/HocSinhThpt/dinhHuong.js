import diLamImage from '@/assets/guest/nha-tuyen-dung.jpg'
import duHocNgheImage from '@/assets/guest/nha-truong.jpg'
import duHocImage from '@/assets/guest/sinh-vien.jpg'
import thiDaiHocImage from '@/assets/guest/thpt.jpg'
import khoiNghiepImage from '@/assets/guest/thanh-nien.jpg'
import xuatKhauImage from '@/assets/guest/thcs.jpg'

export const DINH_HUONG_THPT_KEY = 'dinh_huong_thpt'

// `moTruyCap: false`: hướng chưa làm xong — vẫn hiển thị nhưng không cho bấm, vào thẳng URL sẽ về trang chọn hướng.
export const dinhHuongThptList = [
  {
    code: 'thi-dai-hoc',
    moTruyCap: true,
    name: 'Thi Đại học & cao đẳng',
    description: 'Ôn thi và chọn ngành, trường trong nước.',
    image: thiDaiHocImage,
  },
  {
    code: 'di-lam',
    moTruyCap: true,
    name: 'Đi làm ngay sau khi tốt nghiệp',
    description: 'Bắt đầu làm việc sớm và tích lũy kinh nghiệm thay vì học tiếp.',
    image: diLamImage,
  },
  {
    code: 'du-hoc-nghe',
    moTruyCap: false,
    name: 'Du học nghề',
    description: 'Học nghề ở nước ngoài, vừa đào tạo vừa thực hành.',
    image: duHocNgheImage,
  },
  {
    code: 'du-hoc',
    moTruyCap: false,
    name: 'Du học',
    description: 'Học đại học hoặc cao đẳng tại nước ngoài.',
    image: duHocImage,
  },
  {
    code: 'khoi-nghiep',
    moTruyCap: false,
    name: 'Khởi nghiệp',
    description: 'Tự xây dựng ý tưởng và bắt đầu công việc của riêng bạn.',
    image: khoiNghiepImage,
  },
  {
    code: 'xuat-khau-lao-dong',
    moTruyCap: false,
    name: 'Xuất khẩu lao động',
    description: 'Đi làm việc có thời hạn ở nước ngoài theo chương trình lao động.',
    image: xuatKhauImage,
  },
]

export function laDinhHuongMo(code) {
  return !!dinhHuongThptList.find((item) => item.code === code)?.moTruyCap
}
