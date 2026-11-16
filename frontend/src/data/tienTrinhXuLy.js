// Các bước hiển thị trong dialog tiến trình xử lý (TienTrinhXuLyDialog); bước cuối là hoàn tất.
export const BUOC_TIEN_TRINH = [
  { step: 1, text: 'Đang tiếp nhận yêu cầu của bạn...' },
  { step: 2, text: 'Đang tìm hiểu nội dung câu hỏi...' },
  { step: 3, text: 'Đang tìm kiếm thông tin liên quan...' },
  { step: 4, text: 'Đang thu thập và tổng hợp dữ liệu...' },
  { step: 5, text: 'Đang phân tích và đối chiếu thông tin...' },
  { step: 6, text: 'Đang đánh giá các phương án phù hợp...' },
  { step: 7, text: 'Đang xây dựng gợi ý...' },
  { step: 8, text: 'Đang hoàn thiện câu trả lời...' },
  { step: 9, text: 'Kết quả của bạn đã sẵn sàng!' },
]

// Thời gian hiển thị mỗi bước (ms).
export const THOI_GIAN_MOI_BUOC = 1000

// Giữ bước hoàn tất ("Kết quả của bạn đã sẵn sàng!") bao lâu rồi mới đóng dialog (ms).
export const THOI_GIAN_HOAN_TAT = 3000
