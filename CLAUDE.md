# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Monorepo: `backend/` (FastAPI + SQLAlchemy 2 + Alembic, MySQL) và `frontend/` (Vue 3 + Vite + Element Plus + Pinia). Lệnh chạy xem `make help` (Makefile ở root).

## An toàn — bắt buộc

- `backend/.env` trỏ tới **DB remote dùng chung**, `frontend/.env` mặc định trỏ API production. KHÔNG tự chạy `make migrate`, `make migrate-down`, `make stamp`, `alembic upgrade/downgrade/stamp` — viết migration xong thì báo người dùng chạy.
- KHÔNG deploy: không chạy `./build_and_push.sh`, `docker push`.

## Test

- Backend (unittest, không phải pytest): `cd backend && .venv/bin/python -B -m unittest discover -s tests -v`; một test: `.venv/bin/python -m unittest tests.<module>.<Class>.<test>`.
- Frontend (`node --test`): `cd frontend && npm test`; một file: `node --test tests/chat.test.js`.
- Test không gọi API AI thật (Gemini/OpenAI) — giữ nguyên như vậy.
- Lint sau khi sửa: `cd backend && .venv/bin/ruff check <file>` (cài: `pip install -r requirements-dev.txt`), `cd frontend && npx eslint <file>`. Code cũ còn lỗi lint sẵn — chỉ cần không thêm lỗi mới ở file đang sửa.

## Quy ước

- Mọi thứ bằng tiếng Việt: định danh không dấu (`list_dan_toc`, `ten_cau_hinh`), docstring/comment, `detail` lỗi, text UI, commit message.
- Tiền tố bảng/file: `dm_` danh mục, `dats_` đề án tuyển sinh, `ht_` hệ thống/cấu hình, `tn_` trắc nghiệm/khảo sát.
- Endpoint viết query SQLAlchemy trực tiếp (`_get_or_404`, `_like_pattern`); không có tầng repository, `app/services/` chỉ cho logic phức tạp.
- API danh sách nhận `q`, `page`, `page_size` và trả `{items, total, page, page_size}`. Path tiếng Việt kebab-case (`/danh-muc/...`, `/he-thong/...`).
- Model mới phải import trong `app/models/__init__.py`.
- Migration viết tay trong `backend/alembic/versions/`, tên `YYYYMMDD_NNNN_slug.py`, `revision = "YYYYMMDD_NNNN"`, `down_revision` = head hiện tại (số NNNN tăng liên tục toàn repo). Không dùng `make migrate-new` (autogenerate kết nối DB chung và sinh revision hex).
- Sau khi thêm/sửa API: chạy `cd backend && .venv/bin/python -m app.scripts.xuat_danh_sach_api` để sinh lại `backend/API.md` (không sửa tay file này).
- Thêm một resource đầy đủ: dùng skill `/them-api`.

## Phân quyền

- `app/api/deps.py`: `get_current_user` (401/403 nếu khóa), `get_admin_user` (`vai_tro == 1`), `get_optional_user`.
- Danh mục `dm_*`: GET danh sách không cần đăng nhập; GET chi tiết `/{item_id}` dùng `get_current_user`; POST/PUT/PATCH/DELETE dùng `get_admin_user`. Quy tắc này được kiểm bởi `backend/tests/test_phan_quyen.py`.
- Resource vừa có route public vừa admin: tách `public_router` và include **trước** admin router, nếu không `/{item_id}` sẽ bắt mất path public (xem `ht_cau_hinh_enduser.py`).
- Sắp có thêm vai trò ngoài admin/user: dùng dependency trong `deps.py` (backend) và store `auth` (frontend), không rải thêm `vai_tro == 1` hard-code.
- Frontend: guard trong `src/router/index.js` dùng `meta.requiresAuth|requiresAdmin|guest|public`; menu sidebar lấy từ `src/data/menu.json` (key `admin`, `user`, `doi-tuong`).

## Gotchas

- Frontend auto-import Element Plus và API vue/router/pinia; `src/auto-imports.d.ts`, `src/components.d.ts` là file sinh tự động.
- `VITE_API_BASE_URL` gắn lúc build. Image Docker frontend không build — phải `npm run build` trước.
- Docker build backend dùng context là root repo (cần `data_dh_json/`).
- Rate limit chat lưu in-memory theo từng worker.
