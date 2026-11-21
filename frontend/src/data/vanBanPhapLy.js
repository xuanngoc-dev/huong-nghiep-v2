// Nội dung trang Chính sách bảo mật và Điều khoản sử dụng (khu vực khách).
// Mỗi mục: { id (neo #), tieuDe, doan: [đoạn văn], ds: [gạch đầu dòng], sau: [đoạn văn sau danh sách] } (đều tùy chọn).
// Nội dung mô tả đúng dữ liệu hệ thống đang thu thập (bảng nguoi_dung, nguoi_dung_thong_tin, hs_ho_so,
// chat_*, tn_*, ht_lich_su_nap_tien). Khi thêm tính năng thu thập dữ liệu mới, cập nhật lại tại đây.
// Lưu ý: bản nháp do đội phát triển soạn, cần bộ phận pháp chế rà soát trước khi công bố chính thức.

export const EMAIL_HO_TRO = 'hotro@dinhhuongnghe.vn'

export const CHINH_SACH_BAO_MAT = {
  ma: 'chinh-sach-bao-mat',
  tieuDe: 'Chính sách bảo mật',
  moTa: 'Định hướng nghề thu thập những dữ liệu nào, dùng để làm gì, chia sẻ với ai và bạn có những quyền gì đối với dữ liệu của mình.',
  capNhat: '2026-11-21',
  muc: [
    {
      id: 'pham-vi',
      tieuDe: 'Phạm vi áp dụng',
      doan: [
        'Chính sách này áp dụng cho website Định hướng nghề và các tính năng đi kèm: chọn đối tượng và hướng đi, trắc nghiệm Holland, tra cứu trường – ngành, tìm trường phù hợp, trợ lý AI, hồ sơ năng lực và nạp lượt sử dụng.',
        'Chúng tôi xử lý dữ liệu cá nhân theo Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân và các quy định pháp luật Việt Nam liên quan.',
      ],
    },
    {
      id: 'du-lieu-thu-thap',
      tieuDe: 'Dữ liệu chúng tôi thu thập',
      doan: ['Chúng tôi chỉ thu thập dữ liệu bạn chủ động cung cấp hoặc phát sinh khi bạn sử dụng tính năng:'],
      ds: [
        'Tài khoản: họ tên, email, số điện thoại và mật khẩu. Mật khẩu được mã hóa một chiều (bcrypt), chúng tôi không xem được mật khẩu gốc.',
        'Thông tin cá nhân bạn điền thêm: giới tính, ngày sinh, tỉnh thành, khu vực ưu tiên, đối tượng ưu tiên, trình độ học vấn, khả năng tài chính.',
        'Hồ sơ năng lực: trường THPT, năm tốt nghiệp, điểm học tập theo môn và học kỳ, điểm các kỳ thi, chứng chỉ ngoại ngữ, thành tích, ngân sách học phí dự kiến.',
        'Kết quả sử dụng: câu trả lời và kết quả trắc nghiệm, lịch sử tìm trường phù hợp, các lựa chọn hướng đi.',
        'Hội thoại với trợ lý AI: câu hỏi bạn gửi, câu trả lời của trợ lý, đối tượng bạn chọn (học sinh, phụ huynh…) và số token đã dùng. Khách chưa đăng nhập được gắn một mã khách ngẫu nhiên, không gắn với danh tính.',
        'Giao dịch nạp lượt: mã giao dịch, gói đã chọn, số tiền, ngân hàng nhận, nội dung chuyển khoản và trạng thái xác nhận. Chúng tôi không lưu số thẻ hay thông tin đăng nhập ngân hàng của bạn.',
      ],
    },
    {
      id: 'du-lieu-nhay-cam',
      tieuDe: 'Dữ liệu cá nhân nhạy cảm',
      doan: [
        'Một số trường như dân tộc, tôn giáo và tình trạng sức khỏe thể chất là dữ liệu cá nhân nhạy cảm theo Nghị định 13/2023/NĐ-CP. Các trường này không bắt buộc. Bạn chỉ điền khi muốn được tư vấn sát hơn, ví dụ để xét đối tượng ưu tiên hoặc ngành có yêu cầu sức khỏe.',
        'Bạn có thể sửa hoặc xóa các thông tin này bất kỳ lúc nào trong trang Thông tin cá nhân (dân tộc, tôn giáo) và Hồ sơ năng lực (sức khỏe).',
      ],
    },
    {
      id: 'muc-dich',
      tieuDe: 'Mục đích sử dụng',
      ds: [
        'Tạo và quản lý tài khoản, đăng nhập, khôi phục truy cập.',
        'Gợi ý hướng đi, ngành và trường phù hợp dựa trên kết quả trắc nghiệm và hồ sơ năng lực của bạn.',
        'Để trợ lý AI trả lời theo đúng hoàn cảnh của bạn (đối tượng, điểm, chứng chỉ, khu vực).',
        'Lưu lịch sử trắc nghiệm, tìm trường và hội thoại để bạn xem lại.',
        'Xác nhận giao dịch nạp lượt và cộng lượt sử dụng vào tài khoản.',
        'Phát hiện lạm dụng (ví dụ gửi quá nhiều yêu cầu), xử lý sự cố và cải thiện chất lượng dịch vụ.',
      ],
      sau: ['Chúng tôi không bán dữ liệu cá nhân và không dùng dữ liệu của bạn cho quảng cáo.'],
    },
    {
      id: 'tro-ly-ai',
      tieuDe: 'Trợ lý AI và bên xử lý dữ liệu',
      doan: [
        'Để tạo câu trả lời, nội dung câu hỏi cùng phần thông tin hồ sơ liên quan được gửi tới nhà cung cấp mô hình AI mà hệ thống đang dùng, như Google (Gemini) hoặc OpenAI. Các nhà cung cấp này xử lý dữ liệu theo chính sách của họ.',
        'Vì vậy, bạn không nên nhập vào khung chat các thông tin không cần cho việc tư vấn như số căn cước, mật khẩu hay thông tin tài khoản ngân hàng.',
        'Câu trả lời của trợ lý AI chỉ mang tính tham khảo và có thể chưa chính xác. Hãy đối chiếu với thông báo tuyển sinh chính thức của trường trước khi quyết định.',
      ],
    },
    {
      id: 'chia-se',
      tieuDe: 'Chia sẻ dữ liệu',
      doan: ['Dữ liệu của bạn chỉ được chia sẻ trong các trường hợp:'],
      ds: [
        'Với nhà cung cấp mô hình AI, như mô tả ở mục Trợ lý AI.',
        'Với đơn vị cung cấp hạ tầng máy chủ, lưu trữ để vận hành hệ thống.',
        'Khi có yêu cầu của cơ quan nhà nước có thẩm quyền theo quy định pháp luật.',
        'Khi bạn đồng ý rõ ràng, ví dụ khi sau này có tính năng kết nối với nhà trường hoặc nhà tuyển dụng.',
      ],
    },
    {
      id: 'luu-tru-trinh-duyet',
      tieuDe: 'Lưu trữ trên trình duyệt',
      doan: [
        'Website dùng bộ nhớ của trình duyệt (localStorage, sessionStorage) để giữ phiên đăng nhập và nhớ các lựa chọn của bạn như đối tượng, hướng đi đang xem và câu trả lời tự đánh giá đang làm dở.',
        'Website không dùng cookie quảng cáo và không gắn công cụ theo dõi của bên thứ ba. Bạn có thể xóa dữ liệu này trong phần cài đặt của trình duyệt; khi đó bạn sẽ bị đăng xuất và các lựa chọn được đặt lại.',
      ],
    },
    {
      id: 'luu-giu-bao-ve',
      tieuDe: 'Thời gian lưu giữ và bảo vệ dữ liệu',
      doan: [
        'Dữ liệu được lưu trong thời gian tài khoản còn hoạt động. Khi bạn yêu cầu xóa tài khoản, dữ liệu cá nhân sẽ được xóa, trừ phần chúng tôi phải giữ lại theo quy định pháp luật, ví dụ chứng từ giao dịch.',
        'Kết nối tới website được mã hóa, mật khẩu được mã hóa một chiều, và chỉ người có thẩm quyền quản trị mới truy cập được dữ liệu phục vụ vận hành và hỗ trợ.',
      ],
    },
    {
      id: 'quyen-cua-ban',
      tieuDe: 'Quyền của bạn',
      doan: ['Theo Nghị định 13/2023/NĐ-CP, bạn có quyền:'],
      ds: [
        'Được biết dữ liệu nào đang được xử lý và vì sao.',
        'Xem, chỉnh sửa thông tin cá nhân và hồ sơ năng lực trong khu vực thành viên.',
        'Rút lại sự đồng ý, yêu cầu hạn chế hoặc phản đối việc xử lý dữ liệu.',
        'Yêu cầu xóa dữ liệu hoặc xóa tài khoản.',
        'Khiếu nại, tố cáo theo quy định pháp luật.',
      ],
    },
    {
      id: 'tre-em',
      tieuDe: 'Người dùng chưa đủ 16 tuổi',
      doan: [
        'Nhiều người dùng của Định hướng nghề là học sinh THCS và THPT. Nếu bạn chưa đủ 16 tuổi, hãy đăng ký tài khoản và cung cấp thông tin khi có sự đồng ý của cha mẹ hoặc người giám hộ.',
        'Cha mẹ, người giám hộ có thể liên hệ chúng tôi để xem, chỉnh sửa hoặc yêu cầu xóa dữ liệu của con.',
      ],
    },
    {
      id: 'lien-he',
      tieuDe: 'Liên hệ và thay đổi chính sách',
      doan: [
        `Mọi yêu cầu về dữ liệu cá nhân xin gửi về ${EMAIL_HO_TRO}. Chúng tôi phản hồi trong thời hạn pháp luật quy định.`,
        'Khi chính sách thay đổi, ngày cập nhật ở đầu trang sẽ được đổi. Thay đổi quan trọng sẽ được thông báo trên website trước khi áp dụng.',
      ],
    },
  ],
}

export const DIEU_KHOAN_SU_DUNG = {
  ma: 'dieu-khoan-su-dung',
  tieuDe: 'Điều khoản sử dụng',
  moTa: 'Các điều khoản khi bạn dùng Định hướng nghề: tài khoản, lượt sử dụng, trợ lý AI, nội dung và trách nhiệm của mỗi bên.',
  capNhat: '2026-11-21',
  muc: [
    {
      id: 'chap-nhan',
      tieuDe: 'Chấp nhận điều khoản',
      doan: [
        'Khi truy cập hoặc đăng ký tài khoản Định hướng nghề, bạn đồng ý với các điều khoản này và Chính sách bảo mật. Nếu không đồng ý, vui lòng ngừng sử dụng dịch vụ.',
        'Người chưa đủ 16 tuổi cần có sự đồng ý của cha mẹ hoặc người giám hộ khi đăng ký và nạp lượt sử dụng.',
      ],
    },
    {
      id: 'dich-vu',
      tieuDe: 'Dịch vụ',
      doan: [
        'Định hướng nghề hỗ trợ học sinh, phụ huynh và người trẻ tìm hiểu hướng đi sau lớp 9, lớp 12: so sánh các hướng đi, làm trắc nghiệm Holland, tra cứu trường, ngành, phương thức tuyển sinh, tìm trường phù hợp và hỏi trợ lý AI.',
        'Một số tính năng có thể đang phát triển, được đánh dấu "Sắp ra mắt", và có thể thay đổi hoặc tạm ngừng để bảo trì.',
      ],
    },
    {
      id: 'tai-khoan',
      tieuDe: 'Tài khoản',
      ds: [
        'Cung cấp thông tin đăng ký chính xác và cập nhật khi có thay đổi.',
        'Tự bảo mật mật khẩu đăng nhập và mật khẩu thanh toán; không chia sẻ tài khoản cho người khác.',
        'Thông báo ngay cho chúng tôi nếu nghi ngờ tài khoản bị truy cập trái phép.',
        'Bạn chịu trách nhiệm về các hoạt động diễn ra trong tài khoản của mình.',
      ],
    },
    {
      id: 'tham-khao',
      tieuDe: 'Thông tin mang tính tham khảo',
      doan: [
        'Kết quả trắc nghiệm, gợi ý ngành, trường và câu trả lời của trợ lý AI là thông tin tham khảo để bạn cân nhắc, không phải quyết định thay bạn và không bảo đảm kết quả trúng tuyển hay việc làm.',
        'Dữ liệu tuyển sinh như điểm chuẩn, chỉ tiêu, học phí, phương thức xét tuyển được tổng hợp từ đề án và thông báo công khai của các trường, và có thể thay đổi. Hãy đối chiếu với thông báo chính thức của trường trước khi nộp hồ sơ.',
      ],
    },
    {
      id: 'luot-su-dung',
      tieuDe: 'Lượt sử dụng và thanh toán',
      ds: [
        'Một số tính năng có giới hạn lượt dùng miễn phí, ví dụ số lượt tìm trường phù hợp mỗi ngày hoặc số token trợ lý AI. Khi hết lượt miễn phí, bạn có thể nạp thêm lượt.',
        'Lượt mua thêm được cộng vào tài khoản sau khi giao dịch chuyển khoản được xác nhận. Vui lòng chuyển đúng số tiền và nội dung chuyển khoản hệ thống cung cấp.',
        'Giá, số lượt của từng gói được hiển thị tại trang Nạp tiền trước khi bạn thanh toán và có thể được điều chỉnh cho các giao dịch sau.',
        `Nếu giao dịch đã chuyển khoản nhưng chưa được cộng lượt, hoặc có sai sót, hãy gửi mã giao dịch về ${EMAIL_HO_TRO} để được kiểm tra.`,
      ],
    },
    {
      id: 'hanh-vi',
      tieuDe: 'Hành vi không được phép',
      ds: [
        'Dùng công cụ tự động để thu thập dữ liệu hàng loạt, hoặc gửi yêu cầu nhằm làm quá tải hệ thống.',
        'Tìm cách vượt qua giới hạn lượt sử dụng, truy cập trái phép tài khoản hay dữ liệu của người khác.',
        'Gửi cho trợ lý AI nội dung vi phạm pháp luật, xúc phạm người khác, hoặc cố ý khiến trợ lý tạo nội dung có hại.',
        'Sao chép, bán lại dữ liệu hoặc nội dung của website cho mục đích thương mại khi chưa được đồng ý bằng văn bản.',
      ],
      sau: ['Khi phát hiện vi phạm, chúng tôi có thể tạm khóa hoặc chấm dứt tài khoản.'],
    },
    {
      id: 'so-huu-tri-tue',
      tieuDe: 'Sở hữu trí tuệ',
      doan: [
        'Giao diện, bài viết, bộ câu hỏi trắc nghiệm và cách tổng hợp dữ liệu trên website thuộc quyền của Định hướng nghề hoặc đơn vị cung cấp hợp pháp. Tên, logo của các trường thuộc về trường đó.',
        'Bạn được dùng nội dung cho mục đích học tập, tìm hiểu cá nhân. Khi trích dẫn, vui lòng ghi nguồn Định hướng nghề.',
      ],
    },
    {
      id: 'gioi-han-trach-nhiem',
      tieuDe: 'Giới hạn trách nhiệm',
      doan: [
        'Chúng tôi nỗ lực để dịch vụ hoạt động ổn định và thông tin chính xác, nhưng không chịu trách nhiệm về quyết định chọn trường, chọn ngành của bạn, hay thiệt hại phát sinh từ việc dựa hoàn toàn vào thông tin tham khảo trên website.',
        'Chúng tôi không chịu trách nhiệm về nội dung của website bên ngoài, kể cả website của các trường được dẫn link.',
      ],
    },
    {
      id: 'thay-doi',
      tieuDe: 'Thay đổi điều khoản và liên hệ',
      doan: [
        'Điều khoản có thể được cập nhật khi dịch vụ thay đổi; ngày cập nhật ghi ở đầu trang. Việc bạn tiếp tục sử dụng sau khi điều khoản thay đổi được hiểu là bạn đồng ý với nội dung mới.',
        `Điều khoản được điều chỉnh theo pháp luật Việt Nam. Câu hỏi về điều khoản xin gửi về ${EMAIL_HO_TRO}.`,
      ],
    },
  ],
}
