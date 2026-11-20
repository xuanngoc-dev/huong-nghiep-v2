export const DOI_TUONG_KEY = 'doi_tuong'

// `moTruyCap: false`: đối tượng chưa làm xong — vẫn hiển thị nhưng không cho bấm vào, vào thẳng URL sẽ về trang chọn đối tượng.
export const doiTuongList = [
  {
    ma: 'THCS',
    code: 'hoc-sinh-thcs',
    moTruyCap: true,
    name: 'Học sinh THCS',
    description: 'Bạn đang học cấp trung học cơ sở và muốn chọn hướng đi phù hợp sau lớp 9.',
  },
  {
    ma: 'THPT',
    code: 'hoc-sinh-thpt',
    moTruyCap: true,
    name: 'Học sinh THPT',
    description: 'Lựa chọn ngành học phù hợp với năng lực và đam mê.',
  },
  {
    ma: 'PH',
    code: 'phu-huynh',
    moTruyCap: true,
    name: 'Phụ huynh',
    description: 'Bạn đang cùng con tìm hiểu năng lực và cân nhắc ngành học, trường học phù hợp.',
  },
  {
    ma: 'NTR',
    code: 'nha-truong',
    moTruyCap: false,
    name: 'Nhà trường',
    description: 'Bạn là giáo viên hoặc cán bộ nhà trường, muốn hỗ trợ học sinh trong hoạt động hướng nghiệp.',
  },
  {
    ma: 'SV',
    code: 'sinh-vien',
    moTruyCap: false,
    name: 'Sinh viên',
    description: 'Bạn đang học cao đẳng hoặc đại học và muốn đối chiếu ngành đang học hoặc tìm hướng phù hợp hơn.',
  },
  {
    ma: 'TN',
    code: 'thanh-nien-ngoai-truong',
    moTruyCap: false,
    name: 'Thanh niên ngoài trường',
    description: 'Bạn hiện không đi học và đang tìm hướng nghề để học tiếp hoặc bắt đầu đi làm.',
  },
  {
    ma: 'NTD',
    code: 'nha-tuyen-dung',
    moTruyCap: false,
    name: 'Nhà tuyển dụng',
    description: 'Bạn đại diện đơn vị tuyển dụng và muốn tìm hiểu định hướng, nhóm tính cách của ứng viên.',
  },
]

export function laDoiTuongMo(code) {
  return !!doiTuongList.find((item) => item.code === code)?.moTruyCap
}
