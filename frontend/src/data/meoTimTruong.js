/**
 * Mẹo nhỏ hiển thị ở trang Trường phù hợp trước khi bấm Tìm kiếm; mỗi lần vào trang hiện ngẫu nhiên 1 mẹo.
 * Thêm / sửa mẹo trực tiếp trong danh sách dưới.
 */
export const MEO_TIM_TRUONG = [
  'Bổ sung điểm thi THPT (hoặc điểm dự kiến) trong hồ sơ để hệ thống tìm được trường có điểm chuẩn phù hợp với bạn.',
  'Bạn sợ chi phí học tập và sinh hoạt vượt quá khả năng? Đừng lo, hãy cho chúng tôi biết mức học phí bạn có thể chi trả, chúng tôi sẽ tìm trường phù hợp với yêu cầu của bạn.',
  'Nhiều trường xét tuyển bằng học bạ. Cập nhật điểm trung bình các môn lớp 10, 11, 12 để không bỏ lỡ phương thức này.',
  'Đừng quên khai báo khu vực và đối tượng ưu tiên: điểm cộng ưu tiên có thể giúp bạn vượt qua điểm chuẩn.',
  'Có chứng chỉ ngoại ngữ như IELTS, TOEFL? Thêm vào hồ sơ, nhiều trường quy đổi điểm hoặc cộng điểm cho chứng chỉ này.',
  'Đã thi đánh giá năng lực hay đánh giá tư duy? Nhập kết quả vào hồ sơ để xem thêm trường xét tuyển bằng bài thi này.',
  'Giải học sinh giỏi, giải khoa học kỹ thuật có thể giúp bạn được tuyển thẳng hoặc ưu tiên xét tuyển. Hãy thêm thành tích vào hồ sơ.',
  'Một số ngành như công an, quân đội có yêu cầu về sức khỏe. Cập nhật chiều cao, cân nặng để kết quả gợi ý sát thực tế hơn.',
  'Học gần nhà giúp tiết kiệm chi phí sinh hoạt. Cập nhật tỉnh/thành nơi ở để dễ so sánh các trường theo khu vực.',
  'Không thấy trường mong muốn? Thử nới rộng bộ lọc hoặc chọn thêm tổ hợp môn bạn có thế mạnh.',
]

/** Một mẹo ngẫu nhiên trong danh sách. */
export function meoNgauNhien(danhSach = MEO_TIM_TRUONG) {
  return danhSach[Math.floor(Math.random() * danhSach.length)] || ''
}
