import diLamImage from '@/assets/guest/nha-tuyen-dung.jpg'
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
  // Gộp du học nghề, du học học thuật và chuyển tiếp; chi tiết từng hướng lấy từ danh mục dm_thpt_duhoc_huong_di.
  {
    code: 'du-hoc',
    moTruyCap: true,
    name: 'Du học',
    description: 'Du học nghề, đại học/cao đẳng hoặc chuyển tiếp ở nước ngoài.',
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
    moTruyCap: true,
    name: 'Xuất khẩu lao động',
    description: 'Đi làm việc có thời hạn ở nước ngoài theo chương trình lao động.',
    image: xuatKhauImage,
  },
]

export function laDinhHuongMo(code) {
  return !!dinhHuongThptList.find((item) => item.code === code)?.moTruyCap
}
