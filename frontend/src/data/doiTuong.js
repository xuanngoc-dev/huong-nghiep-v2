export const DOI_TUONG_KEY = 'doi_tuong'

// `moTruyCap: false`: đối tượng chưa làm xong — vẫn hiển thị nhưng không cho bấm vào, vào thẳng URL sẽ về trang chọn đối tượng.
export const doiTuongList = [
  {
    ma: 'THCS',
    code: 'hoc-sinh-thcs',
    moTruyCap: true,
    name: 'Học sinh THCS',
    description: 'Bạn đang học cấp trung học cơ sở và băn khoăn sau lớp 9 nên vào THPT, học nghề hay hướng khác. Tìm hiểu ưu, nhược điểm và chi phí của từng hướng đi để chọn đúng ngay từ đầu.',
  },
  {
    ma: 'THPT',
    code: 'hoc-sinh-thpt',
    moTruyCap: true,
    name: 'Học sinh THPT',
    description: 'Bạn đang học cấp trung học phổ thông và cần chọn ngành, chọn trường phù hợp với năng lực và đam mê. So sánh các hướng thi đại học, du học, đi làm hay xuất khẩu lao động.',
  },
  {
    ma: 'PH',
    code: 'phu-huynh',
    moTruyCap: true,
    name: 'Phụ huynh',
    description: 'Bạn đang cùng con tìm hiểu năng lực, sở thích và cân nhắc ngành học, trường học phù hợp. Nắm rõ các lựa chọn, chi phí dự kiến để đồng hành và hỗ trợ con ra quyết định.',
  },
  {
    ma: 'NTR',
    code: 'nha-truong',
    moTruyCap: false,
    name: 'Nhà trường',
    description: 'Bạn là giáo viên hoặc cán bộ nhà trường, muốn hỗ trợ học sinh trong hoạt động hướng nghiệp. Theo dõi kết quả trắc nghiệm, xu hướng lựa chọn của học sinh để tư vấn sát hơn.',
  },
  {
    ma: 'SV',
    code: 'sinh-vien',
    moTruyCap: false,
    name: 'Sinh viên',
    description: 'Bạn đang học cao đẳng hoặc đại học và muốn đối chiếu ngành đang học với năng lực của mình. Khám phá cơ hội việc làm, học lên cao hoặc chuyển sang hướng phù hợp hơn.',
  },
  {
    ma: 'TN',
    code: 'thanh-nien-ngoai-truong',
    moTruyCap: false,
    name: 'Thanh niên ngoài trường',
    description: 'Bạn hiện không đi học và đang tìm hướng nghề để học tiếp hoặc bắt đầu đi làm. Tìm hiểu các khóa học nghề ngắn hạn, cơ hội việc làm và xuất khẩu lao động phù hợp với bạn.',
  },
  {
    ma: 'NTD',
    code: 'nha-tuyen-dung',
    moTruyCap: false,
    name: 'Nhà tuyển dụng',
    description: 'Bạn đại diện đơn vị tuyển dụng và muốn tìm hiểu định hướng, nhóm tính cách của ứng viên. Kết nối với nguồn nhân lực trẻ có năng lực phù hợp với vị trí cần tuyển.',
  },
]

export function laDoiTuongMo(code) {
  return !!doiTuongList.find((item) => item.code === code)?.moTruyCap
}
