# Định hướng nghề

Backend Python (FastAPI) và frontend Vue 3 giao tiếp qua REST API.

## Cấu trúc

```
backend/          API FastAPI
  app/
    api/v1/       router và endpoint
    core/         cấu hình
    db/           kết nối MySQL (SQLAlchemy)
    schemas/      schema request/response
    models/       model dữ liệu
    services/     nghiệp vụ
frontend/         Vue 3 + Vite
  src/
    api/          Axios client + module theo domain
    components/   UI dùng chung
    composables/  hook Composition API (use*)
    data/         config tĩnh (menu, …)
    layouts/      layout (MainLayout)
    router/       định tuyến + guard
    stores/       Pinia (auth, layout)
    styles/       CSS/SCSS global
    utils/        helper thuần
    views/        trang theo nghiệp vụ
```

Khi dev, Vite chuyển mọi request `/api` sang `http://127.0.0.1:3060`. Prefix API là `/api/v1`.

## Khởi động nhanh trên Windows (1-Click)

Chỉ cần double-click file:
- `start-dev.bat`: Tự động khởi động cả Backend (FastAPI :3060) và Frontend (Vite :5173), sau đó mở trình duyệt.
- `stop-dev.bat`: Tắt nhanh các tiến trình đang chạy trên cổng 3060 và 5173.

## Lệnh tiện lợi (Makefile / Linux / WSL)

Từ thư mục gốc project:

```bash
make help          # danh sách lệnh
make install       # cài backend + frontend
make be            # chạy API (port trong .env, mặc định 3060)
make fe            # chạy frontend
make migrate       # alembic upgrade head
make migrate-down  # rollback 1 bước
make migrate-new m="mo ta"
make db-check      # kiểm tra MySQL
```

Hoặc nạp alias shell (mỗi session hoặc thêm vào `~/.zshrc`):

```bash
source scripts/aliases.sh
dh-be              # chạy backend
dh-fe              # chạy frontend
dh-migrate         # migrate
dh-db              # check DB
```

## Cài lần đầu

```bash
cd backend
python3 -m venv .venv
cp .env.example .env   # chỉnh DB_* nếu cần
cd ..
make install
```

Tài liệu API: http://127.0.0.1:3060/docs  
Frontend: http://localhost:5173

## Chatbot tuyển sinh

- Tra cứu theo trường/cơ sở, ngành/chương trình, tổ hợp, điểm, chỉ tiêu và điều kiện. Hỗ trợ câu hỏi không dấu, tên viết tắt và câu hỏi nối tiếp. Tên trường mơ hồ được hỏi lại.
- AI đọc hội thoại, ngữ cảnh đã lưu và danh mục trường/cơ sở để lập kế hoạch tra cứu JSON. Backend kiểm tra schema/mã trường rồi thực hiện các bộ lọc và cách sắp xếp AI chọn. Khi có điểm mục tiêu và không yêu cầu khoảng điểm riêng, mặc định chỉ lấy điểm chuẩn trong khoảng điểm mục tiêu ± `CHAT_SCORE_MARGIN`; cấu hình này giúp danh sách tập trung vào ngành gần mức điểm người hỏi.
- JSON được đọc vào bộ nhớ đệm; thêm/sửa/xóa tài liệu tự làm mới bộ đệm theo tên, kích thước và thời gian sửa. Truy vấn tổng quan dùng bảng gọn có đủ phương thức, thang điểm, điểm chuẩn, điểm sàn và tổ hợp; yêu cầu chi tiết lấy thêm điều kiện/công thức. Chỉ tính ghi chú/nguồn của bản ghi thực sự gửi, không cắt giữa bản ghi. Nếu vượt dung lượng, thông báo số bản ghi đã gửi và số khớp bộ lọc, không gọi toàn bộ kết quả là phù hợp với thí sinh.
- `POST /api/v1/chat/hoi/stream` trả SSE với các sự kiện `meta`, `model`, `delta`, `done` hoặc `error`. `done` chứa câu trả lời và nguồn đầy đủ. Endpoint JSON `/chat/hoi` vẫn được hỗ trợ.
- Hai giao diện dùng chung hội thoại và lưu tối đa 100 tin nhắn trong trình duyệt, theo tài khoản/khách. Ngữ cảnh trường/ngành/năm, điểm, tổ hợp, khu vực và tóm tắt sở thích do AI cập nhật được lưu riêng để tiếp tục tra cứu khi lượt ban đầu đã ra ngoài cửa sổ lịch sử. Dừng hoặc tạo hội thoại mới sẽ hủy yêu cầu đang chạy; phản hồi cũ không được thêm lại.
- Nguồn hiển thị trường, năm tuyển sinh, thời gian cập nhật file dữ liệu và liên kết xem dữ liệu. Chỉ hiển thị liên kết đề án gốc khi có trường URL hợp lệ trong metadata (`url_nguon`, `nguon_url`, `url`, `link_de_an`). Thời gian sửa file không phải ngày ban hành đề án.
- Quản lý tài liệu (`GET/POST/DELETE /tai-lieu`) yêu cầu tài khoản quản trị (`vai_tro=1`). Đọc nguồn tham khảo `/chat/nguon/{ten}` là công khai, chỉ cho phép JSON/TXT trong thư mục tài liệu.
- API chỉ chấp nhận model đã cấu hình. Các biến `CHAT_*` trong `.env.example` điều chỉnh timeout, giới hạn lượt theo IP và số yêu cầu đồng thời. Hạn mức lưu trong bộ nhớ của **từng worker**; nếu triển khai nhiều worker/máy cần thay bộ giới hạn bằng kho dùng chung như Redis. Cấu hình reverse proxy phải chuyển tiếp đúng IP và không buffer SSE; timeout proxy nên lớn hơn timeout chat.
- Middleware không ghi nội dung chat vào log và không gom các phần SSE trước khi trả cho trình duyệt. Log chat chỉ giữ model, số nguồn, thời gian và lượng token do nhà cung cấp báo về.

Giới hạn chat mặc định:

| Cấu hình | Mặc định | Mục đích |
| --- | --- | --- |
| `CHAT_CONTEXT_MAX_CHARS` | 60.000 ký tự JSON | Trần bản tổng quan gọn sau khi AI chọn bộ lọc/sắp xếp; không phải giới hạn token của model. |
| `CHAT_DETAIL_CONTEXT_MAX_CHARS` | 100.000 ký tự JSON | Trần riêng cho điều kiện/công thức chi tiết; tăng khi cần giữ nhiều chương trình chi tiết hơn, theo dõi chi phí/độ trễ. |
| `CHAT_PLANNING_TIMEOUT_SECONDS` | 20 giây | Trần cho bước AI lập kế hoạch, nằm trong timeout chung. Kế hoạch sai schema/hết thời gian chuyển sang tổng quan, không áp bộ lọc suy đoán. |
| `CHAT_SCORE_MARGIN` | 1.0 điểm | Biên mỗi phía quanh điểm mục tiêu. Ví dụ 28 điểm lấy ngành có điểm chuẩn từ 27 đến 29; đặt `0.5` để thu hẹp khoảng từ 27.5 đến 28.5. |
| `CHAT_TIMEOUT_SECONDS` | 75 giây | Tổng thời gian lập kế hoạch và trả lời. |
| Lịch sử gửi mỗi lần | 30 tin nhắn / 24.000 ký tự | Ngữ cảnh có cấu trúc lưu riêng, không cần tăng lịch sử để giữ điểm/sở thích. |
| Câu trả lời | 4.096 token / 16.000 ký tự | Giữ câu trả lời chat gọn; danh sách tư vấn do AI tự chọn theo nhu cầu. |

Một lượt có thể gọi model hai lần (lập kế hoạch và trả lời), có thêm chi phí/độ trễ so với một lần gọi. Log `planning_usage` riêng để theo dõi và điều chỉnh dung lượng theo thực tế. Không ghi prompt hay nội dung kế hoạch vào log.

Kiểm thử không gọi API AI bên ngoài:

```powershell
cd backend
python -B -m unittest discover -s tests -v
cd ../frontend
npm test
npm run build
```
