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
