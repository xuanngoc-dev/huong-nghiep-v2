import thptImage from '@/assets/guest/thpt.jpg'
import sinhVienImage from '@/assets/guest/sinh-vien.jpg'
import thanhNienImage from '@/assets/guest/thanh-nien.jpg'
import phuHuynhImage from '@/assets/guest/phu-huynh.jpg'
import nhaTruongImage from '@/assets/guest/nha-truong.jpg'
import nhaTuyenDungImage from '@/assets/guest/nha-tuyen-dung.jpg'
import thcsImage from '@/assets/guest/thcs.jpg'
import phanVanImage from '@/assets/guest/phan-van.jpg'
import hollandR from '@/assets/guest/holland/r.svg'
import hollandI from '@/assets/guest/holland/i.svg'
import hollandA from '@/assets/guest/holland/a.svg'
import hollandS from '@/assets/guest/holland/s.svg'
import hollandE from '@/assets/guest/holland/e.svg'
import hollandC from '@/assets/guest/holland/c.svg'

// Ảnh Unsplash dùng cho chủ đề chưa có ảnh nội bộ; luôn kèm `fallback` là ảnh trong dự án.
const unsplash = (id, w = 900) =>
  `https://images.unsplash.com/photo-${id}?auto=format&fit=crop&w=${w}&h=${Math.round(w * 0.66)}&q=70`

export const heroSlides = [
  {
    id: 'dinh-huong',
    eyebrow: 'Nền tảng định hướng nghề nghiệp',
    title: 'Khám phá bản thân – Định hướng tương lai – Kiến tạo sự nghiệp',
    text: 'Đồng hành cùng bạn trên hành trình thấu hiểu bản thân, lựa chọn ngành học, khám phá nghề nghiệp và phát triển sự nghiệp phù hợp.',
    image: thcsImage,
    alt: 'Học sinh mặc đồng phục cùng học tập trong lớp',
    primary: { label: 'Bắt đầu định hướng', to: { name: 'chon-doi-tuong' } },
    secondary: { label: 'Khám phá nghề nghiệp', to: { name: 'chon-doi-tuong' } },
  },
  {
    id: 'holland',
    eyebrow: 'Trắc nghiệm Holland RIASEC',
    title: 'Hiểu rõ nhóm tính cách nghề nghiệp của chính bạn',
    text: 'Sáu nhóm tính cách Holland giúp bạn nhận diện sở thích, điểm mạnh và môi trường làm việc phù hợp trước khi chọn ngành.',
    image: phanVanImage,
    alt: 'Bạn trẻ đang suy nghĩ và trao đổi về lựa chọn của mình',
    primary: { label: 'Làm trắc nghiệm', to: { name: 'thpt-thi-dai-hoc-chua-co' } },
    secondary: { label: 'Tìm hiểu RIASEC', to: { name: 'home' }, hash: '#holland' },
  },
  {
    id: 'tra-cuu',
    eyebrow: 'Tra cứu trường & ngành',
    title: 'Chọn đúng ngành, đúng trường với thông tin rõ ràng',
    text: 'So sánh ngành đào tạo, phương thức tuyển sinh và trường phù hợp với năng lực, sở thích và mục tiêu của bạn.',
    image: thptImage,
    alt: 'Giảng đường đại học đông sinh viên đang nghe giảng',
    primary: { label: 'Tra cứu ngay', to: { name: 'thpt-thi-dai-hoc' } },
    secondary: { label: 'Xem các lộ trình', to: { name: 'home' }, hash: '#lo-trinh-hoc' },
  },
  {
    id: 'phu-huynh',
    eyebrow: 'Dành cho phụ huynh',
    title: 'Đồng hành cùng con trong quyết định chọn ngành',
    text: 'Hiểu năng lực và sở thích của con để cùng trao đổi, lựa chọn trường và ngành học một cách sáng suốt, không áp đặt.',
    image: phuHuynhImage,
    alt: 'Mẹ và con trai cùng xem tài liệu chọn ngành học',
    primary: { label: 'Giải pháp cho phụ huynh', to: { name: 'phu-huynh' } },
    secondary: { label: 'Hỏi trợ lý AI', to: { name: 'demo-chat' } },
  },
]

export const navLinks = [
  { label: 'Khám phá nghề nghiệp', to: { name: 'chon-doi-tuong' } },
  { label: 'Trắc nghiệm Holland', to: { name: 'thpt-thi-dai-hoc-chua-co' } },
  { label: 'Tra cứu trường/ngành', to: { name: 'thpt-thi-dai-hoc' } },
]

export const audiences = [
  {
    id: 'hoc-sinh',
    name: 'Học sinh',
    route: 'hoc-sinh-thpt',
    image: thptImage,
    short: 'Khám phá sở thích, năng lực và lựa chọn ngành học phù hợp.',
    description:
      'Hỗ trợ học sinh THPT hiểu bản thân, làm rõ định hướng và chọn đường đi sau tốt nghiệp.',
    benefits: [
      'Trắc nghiệm Holland RIASEC chuẩn hóa',
      'Gợi ý ngành học và trường phù hợp',
      'Lộ trình chuẩn bị thi đại học / cao đẳng',
    ],
    cta: 'Bắt đầu với học sinh',
  },
  {
    id: 'sinh-vien',
    name: 'Sinh viên',
    route: 'sinh-vien',
    image: sinhVienImage,
    short: 'Định vị nghề nghiệp, phát triển kỹ năng và chuẩn bị việc làm.',
    description:
      'Giúp sinh viên đối chiếu ngành đang học, tìm cơ hội thực tập và xây dựng hồ sơ nghề nghiệp.',
    benefits: [
      'Đánh giá kỹ năng và xu hướng nghề',
      'Gợi ý thực tập và cơ hội việc làm',
      'Lộ trình phát triển nghề trong 1–3 năm',
    ],
    cta: 'Khám phá cho sinh viên',
  },
  {
    id: 'nguoi-di-lam',
    name: 'Người đi làm',
    route: 'thanh-nien-ngoai-truong',
    image: thanhNienImage,
    short: 'Đánh giá kỹ năng, chuyển nghề và nâng cấp năng lực dài hạn.',
    description:
      'Đồng hành cùng người đi làm khi cần chuyển hướng, học thêm hoặc hoạch định sự nghiệp dài hạn.',
    benefits: [
      'Đánh giá kỹ năng hiện tại',
      'Khám phá hướng chuyển nghề khả thi',
      'Gợi ý khóa học và lộ trình upskill',
    ],
    cta: 'Lập kế hoạch sự nghiệp',
  },
  {
    id: 'phu-huynh',
    name: 'Phụ huynh',
    route: 'phu-huynh',
    image: phuHuynhImage,
    short: 'Hiểu con hơn để đồng hành chọn ngành và trường phù hợp.',
    description:
      'Cung cấp góc nhìn rõ ràng về năng lực của con, giúp phụ huynh hỗ trợ quyết định giáo dục sáng suốt.',
    benefits: [
      'Hiểu nhóm tính cách và sở thích của con',
      'Đối chiếu ngành học – trường – chi phí',
      'Gợi ý cách đồng hành không áp đặt',
    ],
    cta: 'Đồng hành cùng con',
  },
  {
    id: 'nha-truong',
    name: 'Nhà trường',
    route: 'nha-truong',
    image: nhaTruongImage,
    short: 'Công cụ hướng nghiệp và insight hỗ trợ tư vấn học sinh.',
    description:
      'Giải pháp hỗ trợ nhà trường tổ chức hướng nghiệp, theo dõi xu hướng lựa chọn và tư vấn học sinh hiệu quả.',
    benefits: [
      'Bộ công cụ đánh giá hướng nghiệp',
      'Báo cáo insight theo nhóm học sinh',
      'Hỗ trợ tư vấn viên và giáo viên chủ nhiệm',
    ],
    cta: 'Giải pháp cho nhà trường',
  },
  {
    id: 'nha-tuyen-dung',
    name: 'Nhà tuyển dụng',
    route: 'nha-tuyen-dung',
    image: nhaTuyenDungImage,
    short: 'Kết nối nhân tài và truyền thông nhu cầu kỹ năng thực tế.',
    description:
      'Giúp doanh nghiệp giới thiệu nghề nghiệp, chia sẻ yêu cầu kỹ năng và kết nối với thế hệ lao động tương lai.',
    benefits: [
      'Giới thiệu cơ hội nghề nghiệp',
      'Truyền thông nhu cầu kỹ năng',
      'Kết nối giáo dục – việc làm',
    ],
    cta: 'Kết nối nhân tài',
  },
]

export const features = [
  {
    id: 'holland',
    image: phanVanImage,
    alt: 'Bạn trẻ đang suy nghĩ về định hướng của bản thân',
    title: 'Trắc nghiệm Holland RIASEC',
    description: 'Khám phá sở thích nghề nghiệp và nhóm tính cách phù hợp với môi trường làm việc.',
    icon: 'Compass',
    to: { name: 'thpt-thi-dai-hoc-chua-co' },
  },
  {
    id: 'nghe',
    image: thanhNienImage,
    alt: 'Nhóm bạn trẻ thực hành kỹ thuật',
    title: 'Khám phá ngành nghề',
    description: 'Tìm hiểu mô tả công việc, kỹ năng cần có, môi trường làm việc và cơ hội phát triển.',
    icon: 'Briefcase',
    to: { name: 'chon-doi-tuong' },
  },
  {
    id: 'truong',
    image: thptImage,
    alt: 'Giảng đường đại học',
    title: 'Tra cứu trường đại học',
    description: 'Tìm kiếm trường, ngành đào tạo và thông tin tuyển sinh theo nhu cầu của bạn.',
    icon: 'School',
    to: { name: 'thpt-thi-dai-hoc' },
  },
  {
    id: 'ai',
    image: sinhVienImage,
    alt: 'Sinh viên học tập cùng máy tính xách tay',
    title: 'Tư vấn hướng nghiệp bằng AI',
    description: 'Trò chuyện với trợ lý AI để nhận gợi ý định hướng mang tính cá nhân hóa.',
    icon: 'ChatDotRound',
    to: { name: 'demo-chat' },
  },
  {
    id: 'lo-trinh',
    image: nhaTuyenDungImage,
    alt: 'Trao đổi về kế hoạch phát triển sự nghiệp',
    title: 'Xây dựng lộ trình nghề nghiệp',
    description: 'Lập kế hoạch học tập và phát triển sự nghiệp theo từng giai đoạn rõ ràng.',
    icon: 'MapLocation',
    to: { name: 'chon-doi-tuong' },
  },
  {
    id: 'hoc-tap',
    image: thcsImage,
    alt: 'Học sinh cùng học trong lớp',
    title: 'Khám phá cơ hội học tập',
    description: 'Tìm hiểu đại học, giáo dục nghề nghiệp và các hướng du học phù hợp.',
    icon: 'Reading',
    to: { name: 'thpt-du-hoc' },
  },
]

export const steps = [
  {
    step: 1,
    icon: 'User',
    title: 'Khám phá bản thân',
    text: 'Bắt đầu bằng việc hiểu sở thích, giá trị và động lực nghề nghiệp của bạn.',
  },
  {
    step: 2,
    icon: 'DataAnalysis',
    title: 'Đánh giá năng lực và sở thích',
    text: 'Làm trắc nghiệm Holland và đối chiếu với điểm mạnh học tập, kỹ năng mềm.',
  },
  {
    step: 3,
    icon: 'School',
    title: 'Khám phá ngành nghề và trường học',
    text: 'So sánh ngành nghề, chương trình đào tạo và môi trường học tập phù hợp.',
  },
  {
    step: 4,
    icon: 'Promotion',
    title: 'Xây dựng lộ trình học tập và sự nghiệp',
    text: 'Chốt hướng đi và lập kế hoạch hành động theo từng cột mốc cụ thể.',
  },
]

export const hollandGroups = [
  {
    code: 'R',
    en: 'Realistic',
    name: 'Kỹ thuật',
    color: '#0f766e',
    image: hollandR,
    text: 'Thích làm việc thực tế, máy móc, kỹ thuật và môi trường năng động.',
  },
  {
    code: 'I',
    en: 'Investigative',
    name: 'Nghiên cứu',
    color: '#1d4ed8',
    image: hollandI,
    text: 'Yêu thích phân tích, khám phá, khoa học và giải quyết vấn đề.',
  },
  {
    code: 'A',
    en: 'Artistic',
    name: 'Nghệ thuật',
    color: '#7c3aed',
    image: hollandA,
    text: 'Sáng tạo, thẩm mỹ, thích tự do thể hiện ý tưởng và cảm xúc.',
  },
  {
    code: 'S',
    en: 'Social',
    name: 'Xã hội',
    color: '#059669',
    image: hollandS,
    text: 'Quan tâm giúp đỡ người khác, giáo dục, chăm sóc và kết nối cộng đồng.',
  },
  {
    code: 'E',
    en: 'Enterprising',
    name: 'Quản lý',
    color: '#c2410c',
    image: hollandE,
    text: 'Năng động, thuyết phục, dẫn dắt và hướng đến mục tiêu kinh doanh.',
  },
  {
    code: 'C',
    en: 'Conventional',
    name: 'Nghiệp vụ',
    color: '#334155',
    image: hollandC,
    text: 'Có tổ chức, tỉ mỉ, thích dữ liệu, quy trình và công việc hành chính.',
  },
]

export const careerCategories = [
  {
    id: 'cntt',
    image: unsplash('1517694712202-14dd9538aa97', 640),
    fallback: sinhVienImage,
    alt: 'Máy tính xách tay hiển thị mã nguồn lập trình',
    title: 'Công nghệ thông tin',
    meta: 'Lập trình · Dữ liệu · An ninh mạng',
    tag: 'Phổ biến',
  },
  {
    id: 'y-te',
    image: unsplash('1576091160550-2173dba999ef', 640),
    fallback: thanhNienImage,
    alt: 'Ống nghe y tế đặt cạnh máy tính',
    title: 'Y tế & Chăm sóc sức khỏe',
    meta: 'Y khoa · Điều dưỡng · Dược',
    tag: 'Ổn định',
  },
  {
    id: 'kinh-te',
    image: unsplash('1552664730-d307ca884978', 640),
    fallback: nhaTuyenDungImage,
    alt: 'Nhóm làm việc trình bày kế hoạch kinh doanh',
    title: 'Kinh tế & Quản trị',
    meta: 'Tài chính · Marketing · Logistics',
    tag: 'Đa dạng',
  },
  {
    id: 'su-pham',
    image: unsplash('1524178232363-1fb2b075b655', 640),
    fallback: nhaTruongImage,
    alt: 'Giảng viên đứng lớp trước học viên',
    title: 'Giáo dục & Xã hội',
    meta: 'Sư phạm · Tâm lý · Công tác xã hội',
    tag: 'Ý nghĩa',
  },
  {
    id: 'ky-thuat',
    image: unsplash('1581091226825-a6a2a5aee158', 640),
    fallback: thanhNienImage,
    alt: 'Kỹ sư làm việc trong phòng thí nghiệm kỹ thuật',
    title: 'Kỹ thuật & Công nghiệp',
    meta: 'Cơ khí · Điện · Xây dựng',
    tag: 'Thực tiễn',
  },
  {
    id: 'sang-tao',
    image: unsplash('1561070791-2526d30994b5', 640),
    fallback: sinhVienImage,
    alt: 'Bảng màu và bản phác thảo thiết kế đồ họa',
    title: 'Truyền thông & Sáng tạo',
    meta: 'Thiết kế · Media · Nội dung số',
    tag: 'Sáng tạo',
  },
]

export const studyPaths = [
  {
    id: 'dai-hoc',
    title: 'Thi Đại học & Cao đẳng',
    text: 'Tra cứu ngành, trường và phương thức xét tuyển phù hợp với năng lực của bạn.',
    tag: 'Phổ biến nhất',
    image: unsplash('1562774053-701939374585'),
    fallback: thptImage,
    alt: 'Khuôn viên một trường đại học với tòa nhà chính và bãi cỏ',
    to: { name: 'thpt-thi-dai-hoc' },
  },
  {
    id: 'da-co-nganh',
    title: 'Đã có ngành mong muốn',
    text: 'Đối chiếu ngành bạn chọn với danh sách trường đào tạo và tổ hợp xét tuyển.',
    tag: 'Chọn trường',
    image: unsplash('1427504494785-3a9ca7044f45'),
    fallback: sinhVienImage,
    alt: 'Sinh viên đi giữa các kệ sách trong thư viện',
    to: { name: 'thpt-thi-dai-hoc-da-co' },
  },
  {
    id: 'phan-van',
    title: 'Đang phân vân giữa vài ngành',
    text: 'So sánh các lựa chọn theo sở thích, kỹ năng và cơ hội nghề nghiệp để ra quyết định.',
    tag: 'So sánh',
    image: phanVanImage,
    alt: 'Bạn trẻ đang cân nhắc giữa các lựa chọn ngành học',
    to: { name: 'thpt-thi-dai-hoc-phan-van' },
  },
  {
    id: 'du-hoc',
    title: 'Du học',
    text: 'Khám phá chương trình đào tạo quốc tế và chuẩn bị hồ sơ du học phù hợp.',
    tag: 'Quốc tế',
    image: unsplash('1541339907198-e08756dedf3f'),
    fallback: thptImage,
    alt: 'Nhóm tân cử nhân tung mũ tốt nghiệp',
    to: { name: 'thpt-du-hoc' },
  },
  {
    id: 'du-hoc-nghe',
    title: 'Du học nghề',
    text: 'Tìm hiểu các chương trình học nghề kết hợp làm việc tại nước ngoài.',
    tag: 'Học nghề',
    image: thanhNienImage,
    alt: 'Học viên thực hành lắp ráp thiết bị kỹ thuật',
    to: { name: 'thpt-du-hoc-nghe' },
  },
  {
    id: 'di-lam',
    title: 'Đi làm sau tốt nghiệp',
    text: 'Định hướng công việc phù hợp và kỹ năng cần chuẩn bị để bước vào thị trường lao động.',
    tag: 'Việc làm',
    image: nhaTuyenDungImage,
    alt: 'Buổi phỏng vấn tuyển dụng giữa ứng viên và nhà tuyển dụng',
    to: { name: 'thpt-di-lam' },
  },
  {
    id: 'khoi-nghiep',
    title: 'Khởi nghiệp',
    text: 'Đánh giá tố chất khởi nghiệp và các bước chuẩn bị kiến thức, kỹ năng cần thiết.',
    tag: 'Chủ động',
    image: unsplash('1454165804606-c3d57bc86b40'),
    fallback: sinhVienImage,
    alt: 'Lên kế hoạch kinh doanh bên máy tính xách tay',
    to: { name: 'thpt-khoi-nghiep' },
  },
]

export const exploreTabs = [
  { id: 'nghe', label: 'Ngành nghề phổ biến' },
  { id: 'nganh', label: 'Ngành đào tạo' },
  { id: 'truong', label: 'Trường đại học' },
  { id: 'ky-nang', label: 'Kỹ năng nghề' },
  { id: 'lo-trinh', label: 'Lộ trình học tập' },
]

export const explorePreview = {
  nghe: [
    'Kỹ sư phần mềm',
    'Chuyên viên phân tích dữ liệu',
    'Điều dưỡng viên',
    'Chuyên viên marketing số',
  ],
  nganh: ['Công nghệ thông tin', 'Quản trị kinh doanh', 'Y khoa', 'Thiết kế đồ họa'],
  truong: ['Đại học Bách khoa', 'Đại học Kinh tế', 'Đại học Y Dược', 'Đại học Sư phạm'],
  'ky-nang': ['Tư duy phản biện', 'Giao tiếp', 'Phân tích dữ liệu', 'Làm việc nhóm'],
  'lo-trinh': ['Đại học chính quy', 'Cao đẳng nghề', 'Du học', 'Vừa học vừa làm'],
}

export const aiPrompts = [
  'Em thiên về nhóm Social và Artistic, nên chọn ngành nào?',
  'So sánh ngành Công nghệ thông tin và Kinh tế số giúp em.',
  'Phụ huynh cần hỏi gì trước khi con chọn trường?',
  'Làm sao xây lộ trình 3 năm để chuyển sang nghề dữ liệu?',
]

export const aiMessages = [
  {
    role: 'user',
    text: 'Em đang phân vân giữa ngành Công nghệ thông tin và Marketing số.',
  },
  {
    role: 'assistant',
    text: 'Dựa trên sở thích phân tích và sáng tạo của bạn, có thể ưu tiên các ngành giao thoa như Sản phẩm số, Phân tích marketing hoặc UX. Bạn muốn mình đối chiếu theo kỹ năng, môi trường làm việc hay cơ hội việc làm?',
  },
]

export const schoolBenefits = [
  'Hỗ trợ tư vấn hướng nghiệp cho học sinh',
  'Công cụ đánh giá nghề nghiệp chuẩn hóa',
  'Insight tổng hợp giúp cán bộ tư vấn',
  'Đồng hành phát triển nghề nghiệp học sinh',
]

export const employerBenefits = [
  'Khám phá và tiếp cận nhân tài tiềm năng',
  'Giới thiệu cơ hội nghề nghiệp thực tế',
  'Truyền thông nhu cầu kỹ năng lao động',
  'Kết nối giáo dục với tuyển dụng',
]

export const testimonials = [
  {
    id: 1,
    image: thcsImage,
    quote:
      'Sau khi làm trắc nghiệm Holland, em hiểu rõ hơn vì sao mình hợp với ngành thiết kế hơn là kế toán.',
    name: 'Minh Anh',
    role: 'Học sinh lớp 12',
    note: 'Ví dụ minh họa',
  },
  {
    id: 2,
    image: sinhVienImage,
    quote:
      'Nền tảng giúp mình đối chiếu ngành đang học với định hướng việc làm, từ đó điều chỉnh kỹ năng thực tế.',
    name: 'Hoàng Long',
    role: 'Sinh viên năm 3',
    note: 'Ví dụ minh họa',
  },
  {
    id: 3,
    image: phuHuynhImage,
    quote:
      'Tôi dùng kết quả đánh giá để trò chuyện với con theo cách xây dựng hơn, thay vì chỉ dựa vào điểm số.',
    name: 'Chị Hạnh',
    role: 'Phụ huynh',
    note: 'Ví dụ minh họa',
  },
  {
    id: 4,
    image: nhaTruongImage,
    quote:
      'Nhà trường cần công cụ thống nhất để tổ chức hướng nghiệp. Đây là hướng tiếp cận rõ ràng và dễ triển khai.',
    name: 'Thầy Quang',
    role: 'Đối tác giáo dục',
    note: 'Ví dụ minh họa',
  },
]

export const faqs = [
  {
    id: 'mien-phi',
    question: 'Tôi có cần trả phí để sử dụng nền tảng không?',
    answer:
      'Bạn có thể đăng ký tài khoản và bắt đầu khám phá miễn phí, bao gồm trắc nghiệm Holland, tra cứu ngành học và trường đào tạo.',
  },
  {
    id: 'holland',
    question: 'Trắc nghiệm Holland RIASEC là gì và có chính xác không?',
    answer:
      'Holland RIASEC là mô hình phân loại sở thích nghề nghiệp thành sáu nhóm: Kỹ thuật, Nghiên cứu, Nghệ thuật, Xã hội, Quản lý và Nghiệp vụ. Kết quả mang tính tham khảo, giúp bạn hiểu khuynh hướng của mình; nên kết hợp với năng lực học tập và trao đổi cùng gia đình, thầy cô.',
  },
  {
    id: 'doi-tuong',
    question: 'Nền tảng phù hợp với những ai?',
    answer:
      'Nền tảng hỗ trợ học sinh THCS, THPT, sinh viên, người đi làm muốn chuyển hướng, phụ huynh, nhà trường và nhà tuyển dụng. Mỗi nhóm có lộ trình và công cụ riêng.',
  },
  {
    id: 'ket-qua',
    question: 'Kết quả trắc nghiệm của tôi được lưu ở đâu?',
    answer:
      'Khi đăng nhập, lịch sử trắc nghiệm và hồ sơ được lưu trong khu vực thành viên để bạn xem lại, so sánh và tiếp tục hành trình định hướng bất cứ lúc nào.',
  },
  {
    id: 'ai',
    question: 'Trợ lý AI có thay thế chuyên gia tư vấn hướng nghiệp không?',
    answer:
      'Không. Trợ lý AI giúp bạn đặt câu hỏi nhanh và nhận gợi ý ban đầu. Với những quyết định quan trọng, bạn nên tham khảo thêm ý kiến của thầy cô, chuyên gia và gia đình.',
  },
  {
    id: 'to-chuc',
    question: 'Nhà trường hoặc doanh nghiệp hợp tác với nền tảng như thế nào?',
    answer:
      'Nhà trường có thể dùng bộ công cụ đánh giá và báo cáo tổng hợp để tổ chức hướng nghiệp; doanh nghiệp có thể giới thiệu nghề nghiệp và nhu cầu kỹ năng. Liên hệ hotro@dinhhuongnghe.vn để được tư vấn.',
  },
]

export const articles = [
  {
    id: 'a1',
    category: 'Hướng nghiệp',
    title: 'Cách đọc kết quả Holland để chọn ngành học',
    summary: 'Hiểu mã RIASEC và đối chiếu với nhóm ngành đào tạo phù hợp năng lực.',
    date: '2026-10-02',
    image: thptImage,
  },
  {
    id: 'a2',
    category: 'Tuyển sinh',
    title: 'Checklist chuẩn bị hồ sơ xét tuyển đại học',
    summary: 'Những việc cần làm trước kỳ xét tuyển để tránh bỏ sót thông tin quan trọng.',
    date: '2026-09-28',
    image: nhaTruongImage,
  },
  {
    id: 'a3',
    category: 'Phát triển nghề',
    title: 'Kỹ năng mềm nhà tuyển dụng đang tìm kiếm',
    summary: 'Tổng hợp các năng lực chuyển đổi giúp ứng viên nổi bật hơn trong hồ sơ.',
    date: '2026-09-18',
    image: sinhVienImage,
  },
  {
    id: 'a4',
    category: 'Thị trường lao động',
    title: 'Xu hướng việc làm xanh và công nghệ tại Việt Nam',
    summary: 'Góc nhìn ngắn về nhu cầu nhân lực và ngành nghề đang tăng trưởng.',
    date: '2026-09-10',
    image: thanhNienImage,
  },
]

export const footerColumns = [
  {
    title: 'Điều hướng',
    links: [
      { label: 'Trang chủ', to: { name: 'home' } },
      { label: 'Chọn đối tượng', to: { name: 'chon-doi-tuong' } },
      { label: 'Trắc nghiệm Holland', to: { name: 'thpt-thi-dai-hoc-chua-co' } },
      { label: 'Trợ lý AI', to: { name: 'demo-chat' } },
    ],
  },
  {
    title: 'Dịch vụ hướng nghiệp',
    links: [
      { label: 'Khám phá nghề nghiệp', to: { name: 'chon-doi-tuong' } },
      { label: 'Tra cứu trường/ngành', to: { name: 'thpt-thi-dai-hoc' } },
      { label: 'Du học', to: { name: 'thpt-du-hoc' } },
      { label: 'Định hướng đi làm', to: { name: 'thpt-di-lam' } },
    ],
  },
  {
    title: 'Hỗ trợ',
    links: [
      { label: 'Cẩm nang', to: { name: 'home' }, hash: '#cam-nang' },
      { label: 'Câu hỏi thường gặp', to: { name: 'home' }, hash: '#hoi-dap' },
      { label: 'Đăng nhập', to: { name: 'login' } },
      { label: 'Đăng ký', to: { name: 'register' } },
      { label: 'Liên hệ', href: 'mailto:hotro@dinhhuongnghe.vn' },
    ],
  },
]
