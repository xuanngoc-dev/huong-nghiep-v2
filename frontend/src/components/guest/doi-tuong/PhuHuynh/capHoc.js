import thcsImage from '@/assets/guest/thcs.jpg'
import thptImage from '@/assets/guest/thpt.jpg'
import sinhVienImage from '@/assets/guest/sinh-vien.jpg'
import phanVanImage from '@/assets/guest/phan-van.jpg'

export const GIAI_DOAN_CON_KEY = 'giai_doan_con'

// Cấp học của con mà phụ huynh chọn; cấp nào có `lop` thì sang màn của cấp đó để chọn tiếp lớp.
// `giaiDoan` khớp `meta.giaiDoanCon` trong routes.js để chuyển sang màn tương ứng.
export const capHocList = [
  {
    code: 'thcs',
    giaiDoan: 'thcs',
    name: 'Trung học cơ sở',
    nhan: 'Lớp 6 – 9',
    description: 'Cùng con khám phá sở thích, năng lực để chọn hướng phù hợp khi lên THPT.',
    image: thcsImage,
  },
  {
    code: 'thpt',
    giaiDoan: 'thpt',
    name: 'Trung học phổ thông',
    nhan: 'Lớp 10 – 12',
    description: 'Cùng con chọn ngành học, trường học và hướng đi sau khi tốt nghiệp.',
    image: thptImage,
    lop: [
      {
        code: '10-11',
        giaiDoan: 'thpt-10-11',
        name: 'Lớp 10 và lớp 11',
        description: 'Còn thời gian để con tìm hiểu bản thân, chọn tổ hợp môn và định hình nhóm ngành yêu thích.',
        image: thptImage,
      },
      {
        code: '12',
        giaiDoan: 'thpt-12',
        name: 'Lớp 12',
        description: 'Giai đoạn nước rút: cùng con chốt ngành, chọn trường và chuẩn bị hồ sơ xét tuyển.',
        image: phanVanImage,
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
  },
]
