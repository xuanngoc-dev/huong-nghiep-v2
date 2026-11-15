---
name: them-api
description: Checklist thêm một resource/API mới đầy đủ backend + frontend (model, schema, endpoint, router, migration, api js, view, route, menu, API.md). Dùng khi thêm bảng/danh mục/chức năng CRUD mới.
---

Thêm resource `$ARGUMENTS` theo đúng các bước dưới. Mẫu tham khảo: `git show a34d06a` (cấu hình `ht_cau_hinh_enduser`). Đặt tên tiếng Việt không dấu, chọn tiền tố `dm_`/`dats_`/`ht_`/`tn_` phù hợp.

## Backend (`backend/app/`)

1. **Model** `models/<ten_bang>.py` (SQLAlchemy 2) và import trong `models/__init__.py`.
2. **Schema** `schemas/<ten_bang>.py`: Create/Update/Public và Page `{items, total, page, page_size}`.
3. **Endpoint** `api/v1/endpoints/<ten_bang>.py`:
   - List nhận `q`, `page`, `page_size`; dùng `_like_pattern`, `_get_or_404` như các file cùng loại.
   - Phân quyền: danh mục `dm_*` → GET danh sách không cần login, GET chi tiết dùng `get_current_user`, ghi dùng `get_admin_user` (kiểm bởi `tests/test_phan_quyen.py`). Router chỉ cho admin → `APIRouter(dependencies=[Depends(get_admin_user)])`.
   - Có route public lẫn admin → tách `public_router`, include trước admin router.
   - Lỗi `detail` bằng tiếng Việt.
4. **Đăng ký** trong `api/v1/router.py`.
5. **Migration** viết tay `backend/alembic/versions/YYYYMMDD_NNNN_slug.py`:
   - Lấy head hiện tại: `ls backend/alembic/versions | sort | tail -1` → `down_revision`; NNNN = số tiếp theo.
   - `revision = "YYYYMMDD_NNNN"`, có cả `upgrade()` và `downgrade()`, bảng utf8mb4.
   - KHÔNG chạy migrate — DB dùng chung; báo người dùng tự chạy `make migrate`.
6. **Test** (nếu có logic đáng kể) trong `backend/tests/`, chạy `cd backend && .venv/bin/python -B -m unittest discover -s tests -v`.
7. Sinh lại docs: `cd backend && .venv/bin/python -m app.scripts.xuat_danh_sach_api`.

## Frontend (`frontend/src/`)

8. **API** `api/<tenCamelCase>.js` dùng instance trong `api/axios.js`.
9. **View** trong `views/admin/...` (hoặc khu vực tương ứng), Element Plus (auto-import, không import tay).
10. **Responsive** (bắt buộc, làm luôn không cần hỏi) cho mọi form trong view, kể cả form trong dialog:
    - Dùng lưới `form-grid` trong `styles/form-grid.css`, KHÔNG dùng `CustomRow`/`CustomCol` với `:span`/`:xs`/`:md` cho form: breakpoint của `el-col` theo viewport nên sai trong dialog (dialog hẹp hơn màn hình và kéo đổi cỡ được). `form-grid` dùng container query nên số cột theo bề rộng thực của khung chứa form.
    - Số cột tự đổi: khung ≥1200px → 6 ô/hàng, ≥960px → 4, ≥720px → 3, nhỏ hơn (mobile) → 2.
      ```vue
      <CustomForm ref="formRef" class="form-grid" :model="form" :rules="rules" label-position="top">
        <div class="form-grid__body">
          <CustomFormItem label="Mã" prop="ma">...</CustomFormItem>
          <CustomFormItem class="form-grid__span-2" label="Tên" prop="ten">...</CustomFormItem>
          <CustomFormItem class="form-grid__full" label="Ghi chú" prop="ghi_chu">...</CustomFormItem>
        </div>
      </CustomForm>
      ```
    - Ô ngắn (mã, số, select, ngày, trạng thái) để 1 cột; ô tên/tiêu đề dài dùng `form-grid__span-2`; textarea, JSON, upload dùng `form-grid__full`. Không dùng span lớn hơn 2 (mobile chỉ có 2 cột).
    - Chọn `width` dialog theo số ô (đã trừ padding dialog ~32px): ≤ 6 ô → `800px` (3 ô/hàng); 7–12 ô → `1040px` (4 ô/hàng); nhiều hơn → mặc định `90%` (6 ô/hàng trên màn ≥ 1400px). Form 1–4 ô có thể dùng `560px` (2 ô/hàng). Màn nhỏ hoặc người dùng kéo hẹp dialog thì lưới tự giảm cột.
    - `CustomInputNumber`/`CustomSelect`/`CustomDatePicker` trong `form-grid` đã tự rộng 100%, không cần `style="width: 100%"`.
    - Thanh lọc (`.filters`) giữ kiểu flex + class `filter-search`/`filter-status` có sẵn (đã tự giãn 100% trên mobile).
    - Kiểm tra: `npx vite build` không lỗi; nếu chạy được app thì thử ở bề rộng 375px và 1440px.
11. **Route** trong `router/index.js` với `meta` đúng (`requiresAuth`/`requiresAdmin`/`public`).
12. **Menu** trong `data/menu.json` đúng key (`admin`, `user`, `doi-tuong`).

## Kết thúc

Liệt kê các file đã tạo/sửa, nhắc người dùng chạy `make migrate`, và đề xuất commit message tiếng Việt.
