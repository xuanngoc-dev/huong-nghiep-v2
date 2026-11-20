import thcsImage from '@/assets/guest/thcs.jpg'
import thptImage from '@/assets/guest/thpt.jpg'
import sinhVienImage from '@/assets/guest/sinh-vien.jpg'
import phanVanImage from '@/assets/guest/phan-van.jpg'

export const GIAI_DOAN_CON_KEY = 'giai_doan_con'

// Cấp học của con mà phụ huynh chọn; cấp nào có `lop` thì sang màn của cấp đó để chọn tiếp lớp.
// `giaiDoan` khớp `meta.giaiDoanCon` trong routes.js để chuyển sang màn tương ứng.
// `moTruyCap: false`: giai đoạn chưa triển khai — vẫn hiển thị nhưng không cho bấm, vào thẳng URL sẽ về trang phụ huynh.
export const capHocList = [
  {
    code: 'thcs',
    giaiDoan: 'thcs',
    name: 'Trung học cơ sở',
    nhan: 'Lớp 6 – 9',
    description: 'Cùng con khám phá sở thích, năng lực để chọn hướng phù hợp khi lên THPT.',
    image: thcsImage,
    moTruyCap: true,
  },
  {
    code: 'thpt',
    giaiDoan: 'thpt',
    name: 'Trung học phổ thông',
    nhan: 'Lớp 10 – 12',
    description: 'Cùng con chọn ngành học, trường học và hướng đi sau khi tốt nghiệp.',
    image: thptImage,
    moTruyCap: true,
    lop: [
      {
        code: '10-11',
        giaiDoan: 'thpt-10-11',
        name: 'Lớp 10 và lớp 11',
        description: 'Còn thời gian để con tìm hiểu bản thân, chọn tổ hợp môn và định hình nhóm ngành yêu thích.',
        image: thptImage,
        moTruyCap: false,
      },
      {
        code: '12',
        giaiDoan: 'thpt-12',
        name: 'Lớp 12',
        description: 'Giai đoạn nước rút: cùng con chốt ngành, chọn trường và chuẩn bị hồ sơ xét tuyển.',
        image: phanVanImage,
        moTruyCap: true,
      },
    ],
  },
  {
    code: 'da-tot-nghiep',
    giaiDoan: 'da-tot-nghiep',
    name: 'Đã tốt nghiệp THPT',
    nhan: 'Học tiếp hoặc đi làm',
    description: 'Cùng con đối chiếu ngành đang học hoặc tìm hướng việc làm phù hợp.',
    image: sinhVienImage,
    moTruyCap: false,
  },
]

// Cấp học và từng lớp của cấp học trải phẳng thành các giai đoạn riêng.
export const giaiDoanList = capHocList.flatMap((cap) => [cap, ...(cap.lop || [])])

export function laGiaiDoanMo(giaiDoan) {
  return !!giaiDoanList.find((item) => item.giaiDoan === giaiDoan)?.moTruyCap
}
