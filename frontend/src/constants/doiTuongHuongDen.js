// Đối tượng hướng đến của cuộc hội thoại với trợ lý (chat_conversations.doi_tuong_huong_den).
// Khớp backend/app/constants/doi_tuong_huong_den.py (backend giữ đoạn ngữ cảnh đưa vào lời nhắc AI).
// Mã lưu trong CSDL: chỉ thêm mã mới, không đổi/xóa mã đã dùng.
export const DOI_TUONG_HUONG_DEN = [
  { ma: 'thpt-thi-dai-hoc', label: 'Học sinh THPT thi đại học & cao đẳng' },
  { ma: 'thpt-du-hoc', label: 'Học sinh THPT dự định du học' },
  { ma: 'thpt-di-lam', label: 'Học sinh THPT đi làm ngay sau tốt nghiệp' },
  { ma: 'thpt-khoi-nghiep', label: 'Học sinh THPT khởi nghiệp' },
  { ma: 'thpt-xuat-khau-lao-dong', label: 'Học sinh THPT xuất khẩu lao động' },
  { ma: 'hoc-nghe', label: 'Người học nghề' },
  { ma: 'hoc-sinh-thcs', label: 'Học sinh THCS' },
  { ma: 'phu-huynh', label: 'Phụ huynh' },
  { ma: 'sinh-vien', label: 'Sinh viên' },
  { ma: 'thanh-nien-ngoai-truong', label: 'Thanh niên ngoài trường' },
]

export const DOI_TUONG_HUONG_DEN_MAC_DINH = 'thpt-thi-dai-hoc'

// Câu hỏi gợi ý của khung chat khi hội thoại chưa có câu hỏi nào, theo đối tượng hướng đến.
const CAU_HOI_MAU = {
  'thpt-thi-dai-hoc': [
    'Phương thức xét tuyển ngành Marketing trường NEU 2026?',
    'Bách khoa Hà Nội có những ngành nào?',
    'Những trường nào có ngành Công nghệ thông tin hoặc Logistics?',
  ],
  'thpt-du-hoc': [
    'Du học đại học cần chuẩn bị những gì từ lớp 11?',
    'Nên chọn du học Úc, Canada hay Nhật Bản?',
    'Cần IELTS bao nhiêu để du học ngành Kinh doanh?',
  ],
  'thpt-di-lam': [
    'Tốt nghiệp THPT có thể làm những nghề gì?',
    'Có khóa học ngắn hạn nào giúp em đi làm nhanh?',
    'Đi làm trước rồi học đại học sau có được không?',
  ],
  'thpt-khoi-nghiep': [
    'Học sinh THPT có thể bắt đầu khởi nghiệp từ đâu?',
    'Ngành học nào hỗ trợ tốt cho việc khởi nghiệp?',
    'Khởi nghiệp với vốn nhỏ cần lưu ý những rủi ro gì?',
  ],
  'thpt-xuat-khau-lao-dong': [
    'Đi xuất khẩu lao động Nhật Bản cần điều kiện gì?',
    'Nên chọn thị trường xuất khẩu lao động nào?',
    'Làm sao nhận biết công ty xuất khẩu lao động uy tín?',
  ],
  'hoc-nghe': [
    'Nghề nào dễ xin việc và thu nhập ổn định?',
    'Học trung cấp nghề có liên thông lên đại học được không?',
    'Học nghề mất bao lâu và chi phí khoảng bao nhiêu?',
  ],
  'hoc-sinh-thcs': [
    'Sau lớp 9 em nên vào THPT hay học nghề?',
    'Làm sao biết mình hợp với khối tự nhiên hay xã hội?',
    'Học nghề sau lớp 9 có những ưu, nhược điểm gì?',
  ],
  'phu-huynh': [
    'Làm sao giúp con chọn ngành phù hợp với năng lực?',
    'Con học lớp 12 cần chuẩn bị gì cho kỳ xét tuyển đại học?',
    'Chi phí học đại học một năm khoảng bao nhiêu?',
  ],
  'sinh-vien': [
    'Em thấy không hợp ngành đang học, có nên chuyển ngành?',
    'Học văn bằng hai có lợi gì khi đi làm?',
    'Nên học thạc sĩ ngay hay đi làm trước?',
  ],
  'thanh-nien-ngoai-truong': [
    'Không học đại học thì nên học nghề gì?',
    'Có chương trình vừa học vừa làm nào phù hợp?',
    'Xuất khẩu lao động có phải lựa chọn tốt cho tôi?',
  ],
}

export function cauHoiMau(ma) {
  return CAU_HOI_MAU[ma] || CAU_HOI_MAU[DOI_TUONG_HUONG_DEN_MAC_DINH]
}

export function laDoiTuongHuongDen(ma) {
  return DOI_TUONG_HUONG_DEN.some((item) => item.ma === ma)
}

export function tenDoiTuongHuongDen(ma) {
  return DOI_TUONG_HUONG_DEN.find((item) => item.ma === ma)?.label || ''
}

// Đối tượng chính (data/doiTuong.js `code`) → đối tượng hướng đến mặc định.
const THEO_DOI_TUONG = {
  'hoc-sinh-thpt': 'thpt-thi-dai-hoc',
  'hoc-sinh-thcs': 'hoc-sinh-thcs',
  'phu-huynh': 'phu-huynh',
  'sinh-vien': 'sinh-vien',
  'thanh-nien-ngoai-truong': 'thanh-nien-ngoai-truong',
}

/**
 * Đối tượng hướng đến theo trang đang xem (route.meta), để mặc định cho cuộc hội thoại mới.
 * Trang của phụ huynh (meta.giaiDoanCon / meta.goc `phu-huynh-...`) → phụ huynh; hướng đi THPT (meta.dinhHuong) → `thpt-<hướng>`;
 * trang đối tượng (meta.doiTuong / doiTuongCha / goc). Trang khác dùng đối tượng người dùng đã chọn ở trang chủ (doiTuongDaChon).
 */
export function doiTuongTheoTrang(meta = {}, doiTuongDaChon = '') {
  if (meta.giaiDoanCon || String(meta.goc || '').startsWith('phu-huynh')) return 'phu-huynh'
  if (meta.dinhHuong && laDoiTuongHuongDen(`thpt-${meta.dinhHuong}`)) return `thpt-${meta.dinhHuong}`
  const doiTuong = meta.doiTuong || meta.doiTuongCha || meta.goc || doiTuongDaChon
  return THEO_DOI_TUONG[doiTuong] || DOI_TUONG_HUONG_DEN_MAC_DINH
}
