# Danh sách API

Tự sinh từ code lúc 15/11/2026 17:59 bằng `python -m app.scripts.xuat_danh_sach_api`. Không sửa tay, chạy lại lệnh khi thêm hoặc đổi API.

Tiền tố chung: `/api/v1`. Tổng cộng **268** API.

Đăng nhập bằng header `Authorization: Bearer <access_token>` lấy từ API đăng nhập.

| Nhóm | Số API | Yêu cầu đăng nhập |
|---|---:|---|
| [Quản trị (admin)](#quan_tri) | 153 | Bắt buộc đăng nhập bằng tài khoản quản trị. Thiếu token trả 401, không phải admin trả 403. |
| [Thành viên (user)](#thanh_vien) | 72 | Bắt buộc đăng nhập. Thiếu hoặc sai token trả 401. |
| [Khách vãng lai](#khach) | 43 | Không cần đăng nhập. Các API ghi “Tùy chọn” vẫn nhận token: có token hợp lệ thì xử lý theo tài khoản. |

<a id="quan_tri"></a>

## Quản trị (admin)

Bắt buộc đăng nhập bằng tài khoản quản trị. Thiếu token trả 401, không phải admin trả 403.

### `danh-muc/bai-thi-danh-gia-nang-luc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/bai-thi-danh-gia-nang-luc` | Bắt buộc (admin) | Thêm một bài thi đánh giá năng lực. Từ chối nếu mã đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/bai-thi-danh-gia-nang-luc` | Bắt buộc (admin) | Xóa nhiều bài thi đánh giá năng lực theo danh sách id. |
| `POST` | `/api/v1/danh-muc/bai-thi-danh-gia-nang-luc/bulk` | Bắt buộc (admin) | Thêm nhiều bài thi đánh giá năng lực cùng lúc. |
| `PUT` | `/api/v1/danh-muc/bai-thi-danh-gia-nang-luc/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một bài thi đánh giá năng lực theo id. |
| `DELETE` | `/api/v1/danh-muc/bai-thi-danh-gia-nang-luc/{item_id}` | Bắt buộc (admin) | Xóa một bài thi đánh giá năng lực theo id. |

### `danh-muc/bang-cap-chung-chi`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/bang-cap-chung-chi` | Bắt buộc (admin) | Thêm một chứng chỉ ngoại ngữ. Từ chối nếu mã đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/bang-cap-chung-chi` | Bắt buộc (admin) | Xóa nhiều chứng chỉ ngoại ngữ theo danh sách id. |
| `POST` | `/api/v1/danh-muc/bang-cap-chung-chi/bulk` | Bắt buộc (admin) | Thêm nhiều chứng chỉ ngoại ngữ cùng lúc. |
| `PUT` | `/api/v1/danh-muc/bang-cap-chung-chi/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một chứng chỉ ngoại ngữ theo id. |
| `DELETE` | `/api/v1/danh-muc/bang-cap-chung-chi/{item_id}` | Bắt buộc (admin) | Xóa một chứng chỉ ngoại ngữ theo id. |

### `danh-muc/chuyen-nganh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/chuyen-nganh` | Bắt buộc (admin) | Thêm một chuyên ngành. Từ chối nếu mã đã tồn tại, ngành cha hoặc mã Holland không tồn tại. |
| `DELETE` | `/api/v1/danh-muc/chuyen-nganh` | Bắt buộc (admin) | Xóa nhiều chuyên ngành theo danh sách id. |
| `POST` | `/api/v1/danh-muc/chuyen-nganh/bulk` | Bắt buộc (admin) | Thêm nhiều chuyên ngành cùng lúc. Từ chối nếu mã trùng, ngành cha hoặc mã Holland không tồn tại. |
| `PUT` | `/api/v1/danh-muc/chuyen-nganh/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một chuyên ngành theo id. |
| `DELETE` | `/api/v1/danh-muc/chuyen-nganh/{item_id}` | Bắt buộc (admin) | Xóa một chuyên ngành theo id. |

### `danh-muc/dan-toc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/dan-toc` | Bắt buộc (admin) | Thêm một dân tộc. Từ chối nếu mã dân tộc đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/dan-toc` | Bắt buộc (admin) | Xóa nhiều dân tộc theo danh sách id. |
| `POST` | `/api/v1/danh-muc/dan-toc/bulk` | Bắt buộc (admin) | Thêm nhiều dân tộc cùng lúc. Từ chối nếu mã dân tộc trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/dan-toc/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một dân tộc theo id. |
| `DELETE` | `/api/v1/danh-muc/dan-toc/{item_id}` | Bắt buộc (admin) | Xóa một dân tộc theo id. |

### `danh-muc/doi-tuong-uu-tien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/doi-tuong-uu-tien` | Bắt buộc (admin) | Thêm một đối tượng ưu tiên. Từ chối nếu mã đối tượng đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/doi-tuong-uu-tien` | Bắt buộc (admin) | Xóa nhiều đối tượng ưu tiên theo danh sách id. |
| `POST` | `/api/v1/danh-muc/doi-tuong-uu-tien/bulk` | Bắt buộc (admin) | Thêm nhiều đối tượng ưu tiên cùng lúc. Từ chối nếu mã đối tượng trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/doi-tuong-uu-tien/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một đối tượng ưu tiên theo id. |
| `DELETE` | `/api/v1/danh-muc/doi-tuong-uu-tien/{item_id}` | Bắt buộc (admin) | Xóa một đối tượng ưu tiên theo id. |

### `danh-muc/khu-vuc-uu-tien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/khu-vuc-uu-tien` | Bắt buộc (admin) | Thêm một khu vực ưu tiên. Từ chối nếu mã khu vực đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/khu-vuc-uu-tien` | Bắt buộc (admin) | Xóa nhiều khu vực ưu tiên theo danh sách id. |
| `POST` | `/api/v1/danh-muc/khu-vuc-uu-tien/bulk` | Bắt buộc (admin) | Thêm nhiều khu vực ưu tiên cùng lúc. Từ chối nếu mã khu vực trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/khu-vuc-uu-tien/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một khu vực ưu tiên theo id. |
| `DELETE` | `/api/v1/danh-muc/khu-vuc-uu-tien/{item_id}` | Bắt buộc (admin) | Xóa một khu vực ưu tiên theo id. |

### `danh-muc/linh-vuc-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/linh-vuc-dao-tao` | Bắt buộc (admin) | Thêm một lĩnh vực đào tạo. Từ chối nếu mã lĩnh vực đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/linh-vuc-dao-tao` | Bắt buộc (admin) | Xóa nhiều lĩnh vực đào tạo theo danh sách id. Từ chối nếu còn nhóm ngành thuộc các lĩnh vực đó. |
| `POST` | `/api/v1/danh-muc/linh-vuc-dao-tao/bulk` | Bắt buộc (admin) | Thêm nhiều lĩnh vực cùng lúc. Từ chối nếu mã lĩnh vực trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/linh-vuc-dao-tao/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một lĩnh vực đào tạo theo id. |
| `DELETE` | `/api/v1/danh-muc/linh-vuc-dao-tao/{item_id}` | Bắt buộc (admin) | Xóa một lĩnh vực đào tạo theo id. Từ chối nếu còn nhóm ngành thuộc lĩnh vực đó. |

### `danh-muc/loai-cau-hoi`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/loai-cau-hoi` | Bắt buộc (admin) | Thêm một loại câu hỏi. Từ chối nếu thứ tự ưu tiên đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/loai-cau-hoi` | Bắt buộc (admin) | Xóa nhiều loại câu hỏi theo danh sách id. |
| `POST` | `/api/v1/danh-muc/loai-cau-hoi/bulk` | Bắt buộc (admin) | Thêm nhiều loại câu hỏi cùng lúc. Từ chối nếu thứ tự ưu tiên trùng trong dữ liệu hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/loai-cau-hoi/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một loại câu hỏi theo id. |
| `DELETE` | `/api/v1/danh-muc/loai-cau-hoi/{item_id}` | Bắt buộc (admin) | Xóa một loại câu hỏi theo id. |

### `danh-muc/mon-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/mon-hoc` | Bắt buộc (admin) | Thêm một môn học. Từ chối nếu mã môn đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/mon-hoc` | Bắt buộc (admin) | Xóa nhiều môn học theo danh sách id. |
| `POST` | `/api/v1/danh-muc/mon-hoc/bulk` | Bắt buộc (admin) | Thêm nhiều môn học cùng lúc. Từ chối nếu mã môn trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/mon-hoc/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một môn học theo id. |
| `DELETE` | `/api/v1/danh-muc/mon-hoc/{item_id}` | Bắt buộc (admin) | Xóa một môn học theo id. |

### `danh-muc/nganh-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/nganh-dao-tao` | Bắt buộc (admin) | Thêm một ngành đào tạo. Từ chối nếu mã đã tồn tại, nhóm ngành cha hoặc mã Holland không tồn tại. |
| `DELETE` | `/api/v1/danh-muc/nganh-dao-tao` | Bắt buộc (admin) | Xóa nhiều ngành theo danh sách id. Từ chối nếu còn chuyên ngành thuộc các ngành đó. |
| `POST` | `/api/v1/danh-muc/nganh-dao-tao/bulk` | Bắt buộc (admin) | Thêm nhiều ngành cùng lúc. Từ chối nếu mã trùng, nhóm ngành cha hoặc mã Holland không tồn tại. |
| `PUT` | `/api/v1/danh-muc/nganh-dao-tao/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một ngành đào tạo theo id. |
| `DELETE` | `/api/v1/danh-muc/nganh-dao-tao/{item_id}` | Bắt buộc (admin) | Xóa một ngành đào tạo theo id. Từ chối nếu còn chuyên ngành thuộc ngành đó. |

### `danh-muc/nganh-hoc-theo-truong`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/nganh-hoc-theo-truong` | Bắt buộc (admin) | Thêm một ngành đào tạo cho trường. Từ chối nếu trùng mã xét tuyển ở cùng trường và năm học. |
| `DELETE` | `/api/v1/danh-muc/nganh-hoc-theo-truong` | Bắt buộc (admin) | Xóa nhiều ngành đào tạo theo danh sách id. |
| `POST` | `/api/v1/danh-muc/nganh-hoc-theo-truong/bulk` | Bắt buộc (admin) | Import ngành theo trường từ JSON. |
| `POST` | `/api/v1/danh-muc/nganh-hoc-theo-truong/bulk/kiem-tra` | Bắt buộc (admin) | Trả về các mã trường chưa có trong dm_truong, để kiểm tra trước khi import theo lô. |
| `GET` | `/api/v1/danh-muc/nganh-hoc-theo-truong/{item_id}` | Bắt buộc (admin) | Lấy chi tiết một ngành đào tạo theo id. |
| `PUT` | `/api/v1/danh-muc/nganh-hoc-theo-truong/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một ngành đào tạo theo id. |
| `DELETE` | `/api/v1/danh-muc/nganh-hoc-theo-truong/{item_id}` | Bắt buộc (admin) | Xóa một ngành đào tạo theo id. |

### `danh-muc/nhom-nganh-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/nhom-nganh-dao-tao` | Bắt buộc (admin) | Thêm một nhóm ngành đào tạo. Từ chối nếu mã đã tồn tại hoặc lĩnh vực cha không tồn tại. |
| `DELETE` | `/api/v1/danh-muc/nhom-nganh-dao-tao` | Bắt buộc (admin) | Xóa nhiều nhóm ngành theo danh sách id. Từ chối nếu còn ngành thuộc các nhóm đó. |
| `POST` | `/api/v1/danh-muc/nhom-nganh-dao-tao/bulk` | Bắt buộc (admin) | Thêm nhiều nhóm ngành cùng lúc. Từ chối nếu mã trùng hoặc lĩnh vực cha không tồn tại. |
| `PUT` | `/api/v1/danh-muc/nhom-nganh-dao-tao/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một nhóm ngành đào tạo theo id. |
| `DELETE` | `/api/v1/danh-muc/nhom-nganh-dao-tao/{item_id}` | Bắt buộc (admin) | Xóa một nhóm ngành đào tạo theo id. Từ chối nếu còn ngành thuộc nhóm đó. |

### `danh-muc/nhom-tinh-cach-holland`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/nhom-tinh-cach-holland` | Bắt buộc (admin) | Thêm một nhóm tính cách Holland. Từ chối nếu mã nhóm đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/nhom-tinh-cach-holland` | Bắt buộc (admin) | Xóa nhiều nhóm tính cách Holland theo danh sách id. |
| `POST` | `/api/v1/danh-muc/nhom-tinh-cach-holland/bulk` | Bắt buộc (admin) | Thêm nhiều nhóm Holland cùng lúc. Từ chối nếu mã nhóm trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/nhom-tinh-cach-holland/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một nhóm tính cách Holland theo id. |
| `DELETE` | `/api/v1/danh-muc/nhom-tinh-cach-holland/{item_id}` | Bắt buộc (admin) | Xóa một nhóm tính cách Holland theo id. |

### `danh-muc/phuong-thuc-tuyen-sinh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/phuong-thuc-tuyen-sinh` | Bắt buộc (admin) | Thêm một phương thức tuyển sinh. Từ chối nếu mã phương thức đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/phuong-thuc-tuyen-sinh` | Bắt buộc (admin) | Xóa nhiều phương thức tuyển sinh theo danh sách id. |
| `POST` | `/api/v1/danh-muc/phuong-thuc-tuyen-sinh/bulk` | Bắt buộc (admin) | Thêm nhiều phương thức tuyển sinh cùng lúc. Từ chối nếu mã phương thức trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/phuong-thuc-tuyen-sinh/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một phương thức tuyển sinh theo id. |
| `DELETE` | `/api/v1/danh-muc/phuong-thuc-tuyen-sinh/{item_id}` | Bắt buộc (admin) | Xóa một phương thức tuyển sinh theo id. |

### `danh-muc/thanh-tich-hoc-tap-nghien-cuu`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/thanh-tich-hoc-tap-nghien-cuu` | Bắt buộc (admin) | Thêm một thành tích học tập, nghiên cứu. Từ chối nếu mã đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/thanh-tich-hoc-tap-nghien-cuu` | Bắt buộc (admin) | Xóa nhiều thành tích học tập, nghiên cứu theo danh sách id. |
| `POST` | `/api/v1/danh-muc/thanh-tich-hoc-tap-nghien-cuu/bulk` | Bắt buộc (admin) | Thêm nhiều thành tích học tập, nghiên cứu cùng lúc. |
| `PUT` | `/api/v1/danh-muc/thanh-tich-hoc-tap-nghien-cuu/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một thành tích học tập, nghiên cứu theo id. |
| `DELETE` | `/api/v1/danh-muc/thanh-tich-hoc-tap-nghien-cuu/{item_id}` | Bắt buộc (admin) | Xóa một thành tích học tập, nghiên cứu theo id. |

### `danh-muc/tinh-thanh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/tinh-thanh` | Bắt buộc (admin) | Thêm một tỉnh thành. Từ chối nếu mã tỉnh đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/tinh-thanh` | Bắt buộc (admin) | Xóa nhiều tỉnh thành theo danh sách id. |
| `POST` | `/api/v1/danh-muc/tinh-thanh/bulk` | Bắt buộc (admin) | Thêm nhiều tỉnh thành cùng lúc. Từ chối nếu mã tỉnh trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/tinh-thanh/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một tỉnh thành theo id. |
| `DELETE` | `/api/v1/danh-muc/tinh-thanh/{item_id}` | Bắt buộc (admin) | Xóa một tỉnh thành theo id. |

### `danh-muc/to-hop-mon-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/to-hop-mon-hoc` | Bắt buộc (admin) | Thêm một tổ hợp môn học. Từ chối nếu mã tổ hợp đã tồn tại hoặc mã môn không có trong danh mục. |
| `DELETE` | `/api/v1/danh-muc/to-hop-mon-hoc` | Bắt buộc (admin) | Xóa nhiều tổ hợp môn học theo danh sách id. |
| `POST` | `/api/v1/danh-muc/to-hop-mon-hoc/bulk` | Bắt buộc (admin) | Thêm nhiều tổ hợp cùng lúc. Từ chối nếu mã tổ hợp trùng hoặc mã môn học không có trong danh mục. |
| `PUT` | `/api/v1/danh-muc/to-hop-mon-hoc/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một tổ hợp môn học theo id. |
| `DELETE` | `/api/v1/danh-muc/to-hop-mon-hoc/{item_id}` | Bắt buộc (admin) | Xóa một tổ hợp môn học theo id. |

### `danh-muc/ton-giao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/ton-giao` | Bắt buộc (admin) | Thêm một tôn giáo. Từ chối nếu mã tôn giáo đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/ton-giao` | Bắt buộc (admin) | Xóa nhiều tôn giáo theo danh sách id. |
| `POST` | `/api/v1/danh-muc/ton-giao/bulk` | Bắt buộc (admin) | Thêm nhiều tôn giáo cùng lúc. Từ chối nếu mã tôn giáo trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/ton-giao/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một tôn giáo theo id. |
| `DELETE` | `/api/v1/danh-muc/ton-giao/{item_id}` | Bắt buộc (admin) | Xóa một tôn giáo theo id. |

### `danh-muc/truong-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/danh-muc/truong-hoc` | Bắt buộc (admin) | Thêm một trường học. Từ chối nếu mã trường đã tồn tại. |
| `DELETE` | `/api/v1/danh-muc/truong-hoc` | Bắt buộc (admin) | Xóa nhiều trường học theo danh sách id. |
| `POST` | `/api/v1/danh-muc/truong-hoc/bulk` | Bắt buộc (admin) | Thêm nhiều trường học cùng lúc. Từ chối nếu mã trường trùng trong dữ liệu hoặc đã có trong hệ thống. |
| `PUT` | `/api/v1/danh-muc/truong-hoc/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một trường học theo id. |
| `DELETE` | `/api/v1/danh-muc/truong-hoc/{item_id}` | Bắt buộc (admin) | Xóa một trường học theo id. |

### `he-thong/cau-hinh-enduser`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/cau-hinh-enduser` | Bắt buộc (admin) | Lấy danh sách cấu hình EndUser có phân trang. Lọc theo từ khóa (tên, mô tả), kiểu trả lời và trạng thái. |
| `POST` | `/api/v1/he-thong/cau-hinh-enduser` | Bắt buộc (admin) | Thêm một cấu hình EndUser. |
| `DELETE` | `/api/v1/he-thong/cau-hinh-enduser` | Bắt buộc (admin) | Xóa nhiều cấu hình EndUser theo danh sách id. |
| `GET` | `/api/v1/he-thong/cau-hinh-enduser/{item_id}` | Bắt buộc (admin) | Lấy chi tiết một cấu hình EndUser theo id. |
| `PUT` | `/api/v1/he-thong/cau-hinh-enduser/{item_id}` | Bắt buộc (admin) | Cập nhật thông tin một cấu hình EndUser theo id. Trường không gửi lên (vd. noi_dung_cau_hinh) được giữ nguyên. |
| `DELETE` | `/api/v1/he-thong/cau-hinh-enduser/{item_id}` | Bắt buộc (admin) | Xóa một cấu hình EndUser theo id. |
| `PATCH` | `/api/v1/he-thong/cau-hinh-enduser/{item_id}/trang-thai` | Bắt buộc (admin) | Bật/tắt nhanh trạng thái của một cấu hình EndUser. |

### `he-thong/cau-hinh-goi-cuoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/cau-hinh-goi-cuoc` | Bắt buộc (admin) | Lấy danh sách gói cước có phân trang. |
| `POST` | `/api/v1/he-thong/cau-hinh-goi-cuoc` | Bắt buộc (admin) | Thêm một gói cước. Từ chối nếu trùng mã gói cước. |
| `DELETE` | `/api/v1/he-thong/cau-hinh-goi-cuoc` | Bắt buộc (admin) | Xóa nhiều gói cước theo danh sách id. |
| `GET` | `/api/v1/he-thong/cau-hinh-goi-cuoc/{item_id}` | Bắt buộc (admin) | Lấy chi tiết một gói cước theo id. |
| `PUT` | `/api/v1/he-thong/cau-hinh-goi-cuoc/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một gói cước theo id. |
| `DELETE` | `/api/v1/he-thong/cau-hinh-goi-cuoc/{item_id}` | Bắt buộc (admin) | Xóa một gói cước theo id. |
| `PATCH` | `/api/v1/he-thong/cau-hinh-goi-cuoc/{item_id}/trang-thai` | Bắt buộc (admin) | Bật/tắt nhanh trạng thái hoạt động của một gói cước. |

### `he-thong/cau-hinh-tra-cuu`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/cau-hinh-tra-cuu` | Bắt buộc (admin) | Lấy danh sách cấu hình tra cứu, cấu hình đang áp dụng đứng đầu. |
| `POST` | `/api/v1/he-thong/cau-hinh-tra-cuu` | Bắt buộc (admin) | Thêm một cấu hình tra cứu. Nếu đặt đang áp dụng thì các cấu hình khác chuyển sang ngừng. |
| `DELETE` | `/api/v1/he-thong/cau-hinh-tra-cuu` | Bắt buộc (admin) | Xóa nhiều cấu hình tra cứu theo danh sách id. |
| `GET` | `/api/v1/he-thong/cau-hinh-tra-cuu/{item_id}` | Bắt buộc (admin) | Lấy chi tiết một cấu hình tra cứu theo id. |
| `PUT` | `/api/v1/he-thong/cau-hinh-tra-cuu/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ một cấu hình tra cứu theo id. |
| `DELETE` | `/api/v1/he-thong/cau-hinh-tra-cuu/{item_id}` | Bắt buộc (admin) | Xóa một cấu hình tra cứu theo id. Không cho xóa cấu hình đang áp dụng cuối cùng. |
| `PATCH` | `/api/v1/he-thong/cau-hinh-tra-cuu/{item_id}/trang-thai` | Bắt buộc (admin) | Bật/tắt nhanh một cấu hình. Bật cấu hình này thì các cấu hình khác tự tắt. |

### `he-thong/giao-dich-ngan-hang`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/giao-dich-ngan-hang` | Bắt buộc (admin) | Lịch sử giao dịch ngân hàng (tiền vào/ra), mới nhất trước. |

### `he-thong/lich-su-nap-tien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/lich-su-nap-tien` | Bắt buộc (admin) | Toàn bộ lịch sử nạp tiền, mới nhất trước. |
| `POST` | `/api/v1/he-thong/lich-su-nap-tien/{item_id}/tu-choi` | Bắt buộc (admin) | Từ chối giao dịch đang chờ (không nhận được tiền): chuyển sang thất bại, không cộng số dư. |
| `POST` | `/api/v1/he-thong/lich-su-nap-tien/{item_id}/xac-nhan` | Bắt buộc (admin) | Xác nhận đã nhận tiền: chuyển sang thành công và cộng Edu coin/lượt cho người nạp. |

### `he-thong/ngan-hang-thanh-toan`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/ngan-hang-thanh-toan` | Bắt buộc (admin) | Lấy danh sách ngân hàng thanh toán có phân trang. |
| `POST` | `/api/v1/he-thong/ngan-hang-thanh-toan` | Bắt buộc (admin) | Thêm một tài khoản ngân hàng thanh toán. Từ chối nếu trùng số tài khoản ở cùng ngân hàng. |
| `DELETE` | `/api/v1/he-thong/ngan-hang-thanh-toan` | Bắt buộc (admin) | Xóa nhiều ngân hàng thanh toán theo danh sách id. |
| `GET` | `/api/v1/he-thong/ngan-hang-thanh-toan/lua-chon` | Bắt buộc (admin) | Các ngân hàng (theo tên viết tắt) đang có trong bảng, dùng cho bộ lọc. |
| `GET` | `/api/v1/he-thong/ngan-hang-thanh-toan/{item_id}` | Bắt buộc (admin) | Lấy chi tiết một ngân hàng thanh toán theo id. |
| `PUT` | `/api/v1/he-thong/ngan-hang-thanh-toan/{item_id}` | Bắt buộc (admin) | Cập nhật toàn bộ thông tin một ngân hàng thanh toán theo id. |
| `DELETE` | `/api/v1/he-thong/ngan-hang-thanh-toan/{item_id}` | Bắt buộc (admin) | Xóa một ngân hàng thanh toán theo id. |
| `PATCH` | `/api/v1/he-thong/ngan-hang-thanh-toan/{item_id}/trang-thai` | Bắt buộc (admin) | Bật/tắt nhanh trạng thái hoạt động của một ngân hàng thanh toán. |

### `he-thong/nguoi-dung`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/nguoi-dung` | Bắt buộc (admin) | Danh sách tài khoản có phân trang. Lọc theo từ khóa, vai trò, trạng thái. |
| `POST` | `/api/v1/he-thong/nguoi-dung` | Bắt buộc (admin) | — |
| `DELETE` | `/api/v1/he-thong/nguoi-dung` | Bắt buộc (admin) | — |
| `GET` | `/api/v1/he-thong/nguoi-dung/{item_id}` | Bắt buộc (admin) | — |
| `PUT` | `/api/v1/he-thong/nguoi-dung/{item_id}` | Bắt buộc (admin) | — |
| `DELETE` | `/api/v1/he-thong/nguoi-dung/{item_id}` | Bắt buộc (admin) | — |

### `tai-lieu`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/tai-lieu` | Bắt buộc (admin) | Danh sách file json/txt trong thư mục tài liệu. |
| `POST` | `/api/v1/tai-lieu` | Bắt buộc (admin) | Tải một file .json hoặc .txt vào thư mục tài liệu. |
| `DELETE` | `/api/v1/tai-lieu/{ten}` | Bắt buộc (admin) | Xóa một file tài liệu theo tên. |

### `thu-vien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/thu-vien` | Bắt buộc (admin) | Danh sách file và thư mục trong một cấp của thư viện. |
| `POST` | `/api/v1/thu-vien` | Bắt buộc (admin) | Tải một ảnh, video hoặc file nén vào thư mục hiện tại. Không ghi database. |
| `DELETE` | `/api/v1/thu-vien` | Bắt buộc (admin) | Xóa một file hoặc cả thư mục. |
| `POST` | `/api/v1/thu-vien/di-chuyen` | Bắt buộc (admin) | Di chuyển các mục đã chọn vào thư mục đích. |
| `POST` | `/api/v1/thu-vien/doi-ten` | Bắt buộc (admin) | Đổi tên một file hoặc thư mục. |
| `POST` | `/api/v1/thu-vien/giai-nen` | Bắt buộc (admin) | Giải nén một file ZIP hoặc TAR vào thư mục cùng cấp. |
| `POST` | `/api/v1/thu-vien/nen` | Bắt buộc (admin) | Nén các mục đang chọn trong thư mục hiện tại thành một file ZIP. |
| `POST` | `/api/v1/thu-vien/sao-chep` | Bắt buộc (admin) | Sao chép các mục đã chọn vào thư mục đích. |
| `POST` | `/api/v1/thu-vien/thu-muc` | Bắt buộc (admin) | Tạo thư mục con trong thư mục hiện tại. |
| `POST` | `/api/v1/thu-vien/tu-url` | Bắt buộc (admin) | Tải file từ URL về thư mục hiện tại và trả đường dẫn như upload từ thiết bị. |
| `POST` | `/api/v1/thu-vien/xoa` | Bắt buộc (admin) | Xóa nhiều file hoặc thư mục. Thư mục bị xóa cùng toàn bộ nội dung bên trong. |

### `tim-truong-phu-hop`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/tim-truong-phu-hop/quan-tri` | Bắt buộc (admin) | Lịch sử tìm trường phù hợp của mọi tài khoản, mới nhất trước. |
| `GET` | `/api/v1/tim-truong-phu-hop/quan-tri/{item_id}` | Bắt buộc (admin) | Chi tiết một lượt tìm trường: dữ liệu năng lực, tài chính, tiêu chí và kết quả. |

### `trac-nghiem`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/trac-nghiem/phien/quan-tri` | Bắt buộc (admin) | Tất cả phiên khảo sát cho quản trị, mới nhất trước. |

<a id="thanh_vien"></a>

## Thành viên (user)

Bắt buộc đăng nhập. Thiếu hoặc sai token trả 401.

### `auth`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/auth/me` | Bắt buộc | Trả về thông tin tài khoản đang đăng nhập. |

### `chuong-trinh-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/chuong-trinh-dao-tao` | Bắt buộc | Lấy danh sách chương trình có phân trang. Lọc theo từ khóa, trường và năm của đề án. |
| `POST` | `/api/v1/chuong-trinh-dao-tao` | Bắt buộc | Thêm một chương trình đào tạo vào đề án đã chọn. |
| `DELETE` | `/api/v1/chuong-trinh-dao-tao` | Bắt buộc | Xóa nhiều chương trình đào tạo theo danh sách id. |
| `POST` | `/api/v1/chuong-trinh-dao-tao/import` | Bắt buộc | Nhập một mảng chương trình vào đúng đề án đã chọn. id trong JSON không được lưu. |
| `GET` | `/api/v1/chuong-trinh-dao-tao/{item_id}` | Bắt buộc | Lấy chi tiết một chương trình đào tạo theo id. |
| `PUT` | `/api/v1/chuong-trinh-dao-tao/{item_id}` | Bắt buộc | Cập nhật một chương trình đào tạo. Có thể chuyển sang đề án khác. |
| `DELETE` | `/api/v1/chuong-trinh-dao-tao/{item_id}` | Bắt buộc | Xóa một chương trình đào tạo theo id. |

### `danh-muc/bai-thi-danh-gia-nang-luc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/bai-thi-danh-gia-nang-luc/{item_id}` | Bắt buộc | Lấy chi tiết một bài thi đánh giá năng lực theo id. |

### `danh-muc/bang-cap-chung-chi`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/bang-cap-chung-chi/{item_id}` | Bắt buộc | Lấy chi tiết một chứng chỉ ngoại ngữ theo id. |

### `danh-muc/chuyen-nganh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/chuyen-nganh/{item_id}` | Bắt buộc | Lấy chi tiết một chuyên ngành theo id, kèm tên ngành cha. |

### `danh-muc/dan-toc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/dan-toc/{item_id}` | Bắt buộc | Lấy chi tiết một dân tộc theo id. |

### `danh-muc/doi-tuong-uu-tien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/doi-tuong-uu-tien/{item_id}` | Bắt buộc | Lấy chi tiết một đối tượng ưu tiên theo id. |

### `danh-muc/khu-vuc-uu-tien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/khu-vuc-uu-tien/{item_id}` | Bắt buộc | Lấy chi tiết một khu vực ưu tiên theo id. |

### `danh-muc/linh-vuc-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/linh-vuc-dao-tao/{item_id}` | Bắt buộc | Lấy chi tiết một lĩnh vực đào tạo theo id. |

### `danh-muc/loai-cau-hoi`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/loai-cau-hoi/{item_id}` | Bắt buộc | Lấy chi tiết một loại câu hỏi theo id. |

### `danh-muc/mon-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/mon-hoc/{item_id}` | Bắt buộc | Lấy chi tiết một môn học theo id. |

### `danh-muc/nganh-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/nganh-dao-tao/{item_id}` | Bắt buộc | Lấy chi tiết một ngành đào tạo theo id, kèm tên nhóm ngành cha. |

### `danh-muc/nhom-nganh-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/nhom-nganh-dao-tao/{item_id}` | Bắt buộc | Lấy chi tiết một nhóm ngành đào tạo theo id, kèm tên lĩnh vực cha. |

### `danh-muc/nhom-tinh-cach-holland`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/nhom-tinh-cach-holland/{item_id}` | Bắt buộc | Lấy chi tiết một nhóm tính cách Holland theo id. |

### `danh-muc/phuong-thuc-tuyen-sinh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/phuong-thuc-tuyen-sinh/{item_id}` | Bắt buộc | Lấy chi tiết một phương thức tuyển sinh theo id. |

### `danh-muc/thanh-tich-hoc-tap-nghien-cuu`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/thanh-tich-hoc-tap-nghien-cuu/{item_id}` | Bắt buộc | Lấy chi tiết một thành tích học tập, nghiên cứu theo id. |

### `danh-muc/tinh-thanh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/tinh-thanh/{item_id}` | Bắt buộc | Lấy chi tiết một tỉnh thành theo id. |

### `danh-muc/to-hop-mon-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/to-hop-mon-hoc/{item_id}` | Bắt buộc | Lấy chi tiết một tổ hợp môn học theo id. |

### `danh-muc/ton-giao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/ton-giao/{item_id}` | Bắt buộc | Lấy chi tiết một tôn giáo theo id. |

### `danh-muc/truong-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/truong-hoc/{item_id}` | Bắt buộc | Lấy chi tiết một trường học theo id. |

### `de-an-tuyen-sinh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/de-an-tuyen-sinh` | Bắt buộc | Lấy danh sách đề án tuyển sinh có phân trang. Lọc theo từ khóa, trường, năm và trạng thái. |
| `POST` | `/api/v1/de-an-tuyen-sinh` | Bắt buộc | Thêm một đề án tuyển sinh. Từ chối nếu trường học không tồn tại. |
| `DELETE` | `/api/v1/de-an-tuyen-sinh` | Bắt buộc | Xóa nhiều đề án tuyển sinh theo danh sách id. |
| `POST` | `/api/v1/de-an-tuyen-sinh/bulk` | Bắt buộc | Thêm nhiều đề án cùng lúc. Từ chối nếu trường học không tồn tại. |
| `POST` | `/api/v1/de-an-tuyen-sinh/import` | Bắt buộc | Nhập một đề án và các bảng dats_ lồng trong JSON, trong một transaction. |
| `GET` | `/api/v1/de-an-tuyen-sinh/{item_id}` | Bắt buộc | Lấy chi tiết một đề án tuyển sinh theo id, kèm tên trường. |
| `PUT` | `/api/v1/de-an-tuyen-sinh/{item_id}` | Bắt buộc | Cập nhật toàn bộ thông tin một đề án tuyển sinh theo id. |
| `DELETE` | `/api/v1/de-an-tuyen-sinh/{item_id}` | Bắt buộc | Xóa một đề án tuyển sinh theo id. |
| `GET` | `/api/v1/de-an-tuyen-sinh/{item_id}/chi-tiet` | Bắt buộc | Lấy đề án và mọi bảng dats_ liên quan để xem chi tiết. |

### `he-thong/cau-hinh-goi-cuoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/cau-hinh-goi-cuoc/dang-ban` | Bắt buộc | Các gói cước đang hoạt động để thành viên chọn nạp, sắp theo loại rồi giá gốc. Chưa có gói thì trả []. |

### `he-thong/ngan-hang-thanh-toan`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/ngan-hang-thanh-toan/dang-hoat-dong` | Bắt buộc | Các tài khoản ngân hàng đang hoạt động để thành viên chuyển khoản nạp tiền. |

### `tai-khoan`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/tai-khoan/ho-so` | Bắt buộc | Lấy toàn bộ hồ sơ của tài khoản đang đăng nhập: thông tin cá nhân, hồ sơ năng lực, Edu coin và số lượt còn lại. |
| `PUT` | `/api/v1/tai-khoan/ho-so` | Bắt buộc | Cập nhật toàn bộ hồ sơ: thông tin cá nhân và hồ sơ năng lực dùng cho phân tích hướng nghiệp. |
| `GET` | `/api/v1/tai-khoan/nap-tien` | Bắt buộc | Lịch sử nạp tiền của tài khoản đang đăng nhập, mới nhất trước. Lọc theo mã giao dịch/tên gói, trạng thái, loại. |
| `POST` | `/api/v1/tai-khoan/nap-tien` | Bắt buộc | Đăng ký gói cước: tạo giao dịch chờ thanh toán với mã giao dịch làm nội dung chuyển khoản. |
| `PATCH` | `/api/v1/tai-khoan/nap-tien/{item_id}` | Bắt buộc | Đổi ngân hàng chuyển khoản hoặc báo đã chuyển khoản cho giao dịch đang chờ của mình. |
| `POST` | `/api/v1/tai-khoan/nap-tien/{item_id}/huy` | Bắt buộc | Hủy giao dịch đang chờ thanh toán của mình. |
| `PUT` | `/api/v1/tai-khoan/thong-tin-ca-nhan` | Bắt buộc | Chỉ cập nhật thông tin cá nhân (họ tên, liên hệ, nhân thân, diện ưu tiên); giữ nguyên hồ sơ năng lực. |

### `tim-truong-phu-hop`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/tim-truong-phu-hop/cua-toi` | Bắt buộc | Lịch sử tìm trường phù hợp của tài khoản đang đăng nhập, mới nhất trước. |
| `GET` | `/api/v1/tim-truong-phu-hop/cua-toi/{item_id}` | Bắt buộc | Chi tiết một lượt tìm trường của chính tài khoản đang đăng nhập. |

### `trac-nghiem`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/trac-nghiem/cau-hoi` | Bắt buộc | Lấy danh sách câu hỏi trắc nghiệm có phân trang, kèm đáp án. Lọc theo từ khóa, mã Holland, loại và trạng thái. |
| `POST` | `/api/v1/trac-nghiem/cau-hoi` | Bắt buộc | Thêm một câu hỏi trắc nghiệm và các đáp án đi kèm. |
| `DELETE` | `/api/v1/trac-nghiem/cau-hoi` | Bắt buộc | Xóa nhiều câu hỏi theo danh sách id. Đáp án của các câu hỏi đó bị xóa theo. |
| `POST` | `/api/v1/trac-nghiem/cau-hoi/bulk` | Bắt buộc | Thêm nhiều câu hỏi cùng đáp án. Từ chối nếu mã Holland hoặc loại câu hỏi không tồn tại. |
| `GET` | `/api/v1/trac-nghiem/cau-hoi/{item_id}` | Bắt buộc | Lấy chi tiết một câu hỏi trắc nghiệm kèm danh sách đáp án. |
| `PUT` | `/api/v1/trac-nghiem/cau-hoi/{item_id}` | Bắt buộc | Cập nhật câu hỏi và đồng bộ toàn bộ đáp án theo danh sách gửi lên. |
| `DELETE` | `/api/v1/trac-nghiem/cau-hoi/{item_id}` | Bắt buộc | Xóa một câu hỏi trắc nghiệm theo id. Đáp án của câu hỏi bị xóa theo. |
| `GET` | `/api/v1/trac-nghiem/cau-hoi/{item_id}/cau-tra-loi` | Bắt buộc | Lấy danh sách đáp án của một câu hỏi. |
| `POST` | `/api/v1/trac-nghiem/cau-hoi/{item_id}/cau-tra-loi` | Bắt buộc | Thêm một đáp án cho câu hỏi. |
| `PUT` | `/api/v1/trac-nghiem/cau-hoi/{item_id}/cau-tra-loi/{answer_id}` | Bắt buộc | Cập nhật nội dung và điểm của một đáp án. |
| `DELETE` | `/api/v1/trac-nghiem/cau-hoi/{item_id}/cau-tra-loi/{answer_id}` | Bắt buộc | Xóa một đáp án của câu hỏi. |
| `GET` | `/api/v1/trac-nghiem/phien/lich-su` | Bắt buộc | Lịch sử các phiên khảo sát của người dùng đang đăng nhập, mới nhất trước. |

### `tru-so`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/tru-so` | Bắt buộc | Lấy danh sách trụ sở có phân trang. Lọc theo từ khóa, trường, năm và đề án. |
| `POST` | `/api/v1/tru-so` | Bắt buộc | Thêm một trụ sở vào đề án đã chọn. |
| `DELETE` | `/api/v1/tru-so` | Bắt buộc | Xóa nhiều trụ sở theo danh sách id. |
| `POST` | `/api/v1/tru-so/import` | Bắt buộc | Nhập một mảng trụ sở vào đúng đề án đã chọn. id trong JSON không được lưu. |
| `GET` | `/api/v1/tru-so/{item_id}` | Bắt buộc | Lấy chi tiết một trụ sở theo id. |
| `PUT` | `/api/v1/tru-so/{item_id}` | Bắt buộc | Cập nhật một trụ sở. Có thể chuyển sang đề án khác. |
| `DELETE` | `/api/v1/tru-so/{item_id}` | Bắt buộc | Xóa một trụ sở theo id. |

### `website`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/website` | Bắt buộc | Lấy danh sách website có phân trang. Lọc theo từ khóa, trường, năm và đề án. |
| `POST` | `/api/v1/website` | Bắt buộc | Thêm một website vào đề án đã chọn. |
| `DELETE` | `/api/v1/website` | Bắt buộc | Xóa nhiều website theo danh sách id. |
| `POST` | `/api/v1/website/import` | Bắt buộc | Nhập một mảng website vào đúng đề án đã chọn. id trong JSON không được lưu. |
| `GET` | `/api/v1/website/{item_id}` | Bắt buộc | Lấy chi tiết một website theo id. |
| `PUT` | `/api/v1/website/{item_id}` | Bắt buộc | Cập nhật một website. Có thể chuyển sang đề án khác. |
| `DELETE` | `/api/v1/website/{item_id}` | Bắt buộc | Xóa một website theo id. |

<a id="khach"></a>

## Khách vãng lai

Không cần đăng nhập. Các API ghi “Tùy chọn” vẫn nhận token: có token hợp lệ thì xử lý theo tài khoản.

### `auth`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Không | Đăng nhập bằng email và mật khẩu, trả về token. Từ chối nếu sai thông tin hoặc tài khoản bị khóa. |
| `POST` | `/api/v1/auth/register` | Không | Đăng ký tài khoản mới và cấp token đăng nhập. Từ chối nếu email hoặc số điện thoại đã được dùng. |

### `chat`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/chat/hoi` | Không | Hỏi đáp dựa trên các file json/txt trong thư mục tài liệu. |
| `POST` | `/api/v1/chat/hoi/stream` | Không | — |
| `GET` | `/api/v1/chat/model` | Không | Danh sách model hỏi đáp và trạng thái đã có API key. |
| `GET` | `/api/v1/chat/nguon/{ten}` | Không | Nguồn dữ liệu công khai dùng để đối chiếu câu trả lời tuyển sinh. |

### `danh-muc/bai-thi-danh-gia-nang-luc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/bai-thi-danh-gia-nang-luc` | Không | Lấy danh sách bài thi đánh giá năng lực có phân trang, không cần đăng nhập. |

### `danh-muc/bang-cap-chung-chi`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/bang-cap-chung-chi` | Không | Lấy danh sách chứng chỉ ngoại ngữ có phân trang, không cần đăng nhập. |

### `danh-muc/chuyen-nganh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/chuyen-nganh` | Không | Lấy danh sách chuyên ngành có phân trang. Lọc theo từ khóa, trạng thái và ngành cha. Không cần đăng nhập. |

### `danh-muc/dan-toc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/dan-toc` | Không | Lấy danh sách dân tộc có phân trang. Lọc theo từ khóa (tên, mã, tên gọi khác) và trạng thái. Không cần đăng nhập. |

### `danh-muc/doi-tuong-uu-tien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/doi-tuong-uu-tien` | Không | Lấy danh sách đối tượng ưu tiên có phân trang. Lọc theo từ khóa (tên, mã) và trạng thái. Không cần đăng nhập. |

### `danh-muc/khu-vuc-uu-tien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/khu-vuc-uu-tien` | Không | Lấy danh sách khu vực ưu tiên có phân trang. Lọc theo từ khóa (tên, mã) và trạng thái. Không cần đăng nhập. |

### `danh-muc/linh-vuc-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/linh-vuc-dao-tao` | Không | Lấy danh sách lĩnh vực đào tạo có phân trang. Lọc theo từ khóa (tên, mã, tên tiếng Anh) và trạng thái. Không cần đăng nhập. |

### `danh-muc/loai-cau-hoi`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/loai-cau-hoi` | Không | Lấy danh sách loại câu hỏi có phân trang, sắp theo thứ tự ưu tiên. Lọc theo tên và trạng thái. Không cần đăng nhập. |

### `danh-muc/mon-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/mon-hoc` | Không | Lấy danh sách môn học có phân trang. Lọc theo từ khóa (tên, mã, tên viết tắt, nhóm môn) và trạng thái. Không cần đăng nhập. |

### `danh-muc/nganh-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/nganh-dao-tao` | Không | Lấy danh sách ngành đào tạo có phân trang, không cần đăng nhập. |

### `danh-muc/nganh-hoc-theo-truong`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/nganh-hoc-theo-truong` | Không | Lấy danh sách ngành đào tạo theo trường có phân trang. Không cần đăng nhập. |
| `GET` | `/api/v1/danh-muc/nganh-hoc-theo-truong/nam-hoc` | Không | Các năm học đang có dữ liệu, mới nhất trước, dùng cho bộ lọc. Không cần đăng nhập. |
| `GET` | `/api/v1/danh-muc/nganh-hoc-theo-truong/truong-dao-tao` | Không | Liệt kê trường đào tạo một ngành trong năm học, dựa trên dm_nganh_hoc_theo_truong. |

### `danh-muc/nhom-nganh-dao-tao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/nhom-nganh-dao-tao` | Không | Lấy danh sách nhóm ngành có phân trang, không cần đăng nhập. Lọc theo từ khóa, trạng thái và lĩnh vực cha. |

### `danh-muc/nhom-tinh-cach-holland`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/nhom-tinh-cach-holland` | Không | Lấy danh sách nhóm Holland có phân trang, không cần đăng nhập. |

### `danh-muc/phuong-thuc-tuyen-sinh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/phuong-thuc-tuyen-sinh` | Không | Lấy danh sách phương thức tuyển sinh có phân trang. Lọc theo từ khóa (tên, mã) và trạng thái. Không cần đăng nhập. |

### `danh-muc/thanh-tich-hoc-tap-nghien-cuu`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/thanh-tich-hoc-tap-nghien-cuu` | Không | Lấy danh sách thành tích học tập, nghiên cứu có phân trang, không cần đăng nhập. |

### `danh-muc/tinh-thanh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/tinh-thanh` | Không | Lấy danh sách tỉnh thành có phân trang, không cần đăng nhập. |

### `danh-muc/to-hop-mon-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/to-hop-mon-hoc` | Không | Lấy danh sách tổ hợp môn học có phân trang. Lọc theo từ khóa (tên, mã, mã môn) và trạng thái. Không cần đăng nhập. |

### `danh-muc/ton-giao`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/ton-giao` | Không | Lấy danh sách tôn giáo có phân trang. Lọc theo từ khóa (tên, mã) và trạng thái. Không cần đăng nhập. |

### `danh-muc/truong-hoc`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/danh-muc/truong-hoc` | Không | Lấy danh sách trường học từ dm_truong, có phân trang, không cần đăng nhập. |

### `de-an-tuyen-sinh`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/de-an-tuyen-sinh/truong-dao-tao` | Không | Liệt kê trường có chương trình của ngành trong một năm tuyển sinh. Không cần đăng nhập. |

### `he-thong/cau-hinh-enduser`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/he-thong/cau-hinh-enduser/dang-ap-dung` | Không | Cấu hình EndUser đang áp dụng: bản ghi hoạt động được cập nhật gần nhất, chưa có thì trả null. Không cần đăng nhập. |

### `health`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/health` | Không | Kiểm tra API còn hoạt động. |
| `GET` | `/api/v1/health/db` | Không | Kiểm tra kết nối cơ sở dữ liệu. Trả 503 nếu không kết nối được. |

### `kiem-tra-du-lieu`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/kiem-tra-du-lieu/noi-dung` | Không | Toàn bộ JSON tuyển sinh của một file trường. |
| `GET` | `/api/v1/kiem-tra-du-lieu/truong` | Không | Danh sách trường đọc từ các file JSON trong TAI_LIEU_DIR. |

### `thu-vien`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `GET` | `/api/v1/thu-vien/tep/{duong_dan:path}` | Không | Đường dẫn công khai để dùng file đã tải lên. |

### `tim-truong-phu-hop`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/tim-truong-phu-hop` | Tùy chọn | Ghi một lượt tìm trường phù hợp vào tn_lich_su_tim_truong_phu_hop. |
| `GET` | `/api/v1/tim-truong-phu-hop/luot` | Tùy chọn | Hạn mức tìm trường phù hợp trong ngày theo cấu hình đang áp dụng, kèm số lượt đã dùng. |
| `GET` | `/api/v1/tim-truong-phu-hop/truong` | Không | Danh sách trường phù hợp của một ngành, lấy từ dm_nganh_hoc_theo_truong. |

### `trac-nghiem`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/trac-nghiem/phien` | Tùy chọn | Tạo phiên khảo sát Holland và gán danh sách câu hỏi cho phiên đó. |
| `GET` | `/api/v1/trac-nghiem/phien/{ssid}` | Không | Lấy danh sách câu hỏi đã gán cho một phiên, sắp theo thứ tự loại câu hỏi. |
| `PUT` | `/api/v1/trac-nghiem/phien/{ssid}/chi-tiet/{chi_tiet_id}` | Không | Lưu đáp án của một câu trong phiên và điểm tương ứng. |
| `GET` | `/api/v1/trac-nghiem/phien/{ssid}/ket-qua` | Không | Cộng điểm Holland của phiên theo đáp án đã lưu. |
| `GET` | `/api/v1/trac-nghiem/phien/{ssid}/nganh-phu-hop` | Không | Ngành đào tạo khớp các mã Holland nổi bật của phiên. |

### `webhook`

| Method | Đường dẫn | Đăng nhập | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/webhook/giao-dich-ngan-hang` | Không | Nhận webhook biến động số dư (SePay), lưu vào lịch sử giao dịch ngân hàng và tự đối soát nạp tiền. |
