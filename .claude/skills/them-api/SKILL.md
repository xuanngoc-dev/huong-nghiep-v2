---
name: them-api
description: Checklist thêm một resource/API mới đầy đủ backend + frontend (model, schema, endpoint, router, migration, api js, view, route, menu, API.md). Dùng khi thêm bảng/danh mục/chức năng CRUD mới.
---

Thêm resource `$ARGUMENTS` theo đúng các bước dưới. Mẫu tham khảo: `git show a34d06a` (cấu hình `ht_cau_hinh_enduser`). Đặt tên tiếng Việt không dấu, chọn tiền tố `dm_`/`dats_`/`ht_`/`tn_` phù hợp.

## Backend (`backend/app/`)

1. **Model** `models/<ten_bang>.py` (SQLAlchemy 2) và import trong `models/__init__.py`.
2. **Schema** `schemas/<ten_bang>.py`: Create/Update/Public và Page `{items, total, page, page_size}`.
3. **Endpoint** `api/v1/endpoints/<ten_bang>.py`:
   - List nhận `q`, `page`, `page_size`; dùng `_like_pattern` như các file cùng loại. Lấy bản ghi theo id dùng helper `_get_or_400` (xem quy tắc không tìm thấy id bên dưới), không viết thêm `_get_or_404`.
   - Phân quyền: danh mục `dm_*` → GET danh sách không cần login, GET chi tiết dùng `get_current_user`, ghi dùng `get_admin_user` (kiểm bởi `tests/test_phan_quyen.py`). Router chỉ cho admin → `APIRouter(dependencies=[Depends(get_admin_user)])`.
   - Có route public lẫn admin → tách `public_router`, include trước admin router.
   - Lỗi `detail` bằng tiếng Việt.
   - **Không có dữ liệu KHÔNG phải lỗi**: luôn trả 200 đúng cấu trúc với giá trị rỗng, không trả 404. 404 chỉ dành cho trường hợp không tìm thấy API (sai đường dẫn).
     - API danh sách có phân trang → `{"items": [], "total": 0, "page": <page>, "page_size": <page_size>}`.
     - API trả mảng (lựa chọn, dropdown, thống kê) → `[]`; API trả một đối tượng tổng hợp → đủ các trường, số = 0, mảng = `[]`, đối tượng con = `null`.
     - API lấy dữ liệu đang áp dụng (cấu hình hoạt động, ...) mà chưa có → 200 với `null` (khai báo `response_model=... | None`), frontend tự xử lý trường hợp rỗng.
     - Xóa nhiều mà không id nào tồn tại → 200 `{"deleted": 0}`.
   - **Không tìm thấy id/mã cụ thể** (GET/PUT/PATCH/DELETE `/{item_id}`, tra theo mã): KHÔNG trả 404. Trả `400` với `detail` nêu rõ đối tượng và id để frontend hiện thẳng thông báo (frontend đọc `error.response.data.detail`):
     ```python
     def _get_or_400(db: Session, item_id: int) -> HtCauHinhGoiCuoc:
         """Lấy một bản ghi theo id. Không có thì trả 400 kèm thông báo cụ thể."""
         item = db.get(HtCauHinhGoiCuoc, item_id)
         if item is None:
             raise HTTPException(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 detail=f"Không tìm thấy gói cước có id = {item_id}",
             )
         return item
     ```
     Thông báo dạng `Không tìm thấy <tên đối tượng> có <id|mã> = <giá trị>`; với bản ghi liên kết (ngành cha, trường, đề án...) nêu rõ đối tượng liên kết nào không tồn tại.
   - Khi viết test cho endpoint: kiểm tra danh sách rỗng trả 200 đúng cấu trúc và id không tồn tại trả 400 kèm `detail`. `tests/test_khong_tra_404.py` tự kiểm mọi endpoint không còn `_get_or_404` và `_get_or_400` trả 400 có id trong `detail`.
   - Frontend: lỗi không tìm thấy là 400, đọc `error.response.data.detail` để hiện; KHÔNG kiểm `status === 404`. API trả `null` (dữ liệu đang áp dụng) thì dùng `data?.truong`.
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
    - **Placeholder** (bắt buộc): MỌI ô nhập đều có `placeholder` — `CustomInput` (kể cả textarea, mật khẩu), `CustomInputNumber`, `MoneyInput`, `CustomSelect`, `CustomDatePicker`, ô lọc/tìm kiếm và ô nằm trong bảng; chỉ bỏ qua ô `disabled`/`readonly`. Viết theo nhãn của ô:
      - Ô nhập chữ/số: `Nhập <nhãn viết thường>` (bỏ phần đơn vị trong ngoặc), ví dụ `placeholder="Nhập điểm cộng"`; có ràng buộc đáng nói thì thêm vào, ví dụ `Nhập mật khẩu mới (ít nhất 6 ký tự)`.
      - Select: `Chọn <nhãn viết thường>`, ví dụ `placeholder="Chọn trạng thái"`; ngày: `Chọn ngày`; khoảng ngày dùng `start-placeholder="Từ ngày"` / `end-placeholder="Đến ngày"`.
      - Ô tìm kiếm: `Tìm theo <các trường được tìm>`, ví dụ `placeholder="Tìm theo mã, tên"`.
      - Nhãn động (`v-for`): ``:placeholder="`Nhập ${item.nhan.toLowerCase()}`"``.
    - Kiểm tra: `npx vite build` không lỗi; nếu chạy được app thì thử ở bề rộng 375px và 1440px.
11. **Cột thao tác và tooltip** (bắt buộc, làm luôn không cần hỏi):
    - Cột "Thao tác" của bảng dùng **icon** của `@element-plus/icons-vue` (đã đăng ký global, không import), KHÔNG dùng button có chữ. Mỗi icon đặt trong `CustomButton link` (giữ được focus/bàn phím) kèm `aria-label`, bọc trong `.row-actions`:
      ```vue
      <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <CustomTooltip content="Sửa" placement="top">
              <CustomButton link type="primary" aria-label="Sửa" @click="openEdit(row)">
                <CustomIcon><Edit /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
            <CustomTooltip content="Xóa" placement="top">
              <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row)">
                <CustomIcon><Delete /></CustomIcon>
              </CustomButton>
            </CustomTooltip>
          </div>
        </template>
      </CustomTableColumn>
      ```
    - Icon gợi ý: xem `View`, sửa `Edit`, xóa `Delete`, thêm `Plus`, sao chép `CopyDocument`, tải xuống `Download`, tải lên `Upload`, xác nhận `CircleCheck`, từ chối/hủy `CircleClose`, khóa/mở khóa `Lock`/`Unlock`, thanh toán `Wallet`, liên kết ngoài `Link`. `type`: `primary` mặc định, `danger` cho xóa/hủy, `success` cho xác nhận. Độ rộng cột ≈ 50px mỗi icon (tối thiểu 80px).
    - **Tooltip**: mọi nút chỉ có icon, nút thao tác, liên kết icon đều bọc `CustomTooltip` với `content` trùng `aria-label`. `CustomTooltip` tự tắt trên mobile (< 768px) và thiết bị cảm ứng không có hover, nên KHÔNG tự viết `v-if`/`:disabled` theo màn hình và KHÔNG dùng thẳng `el-tooltip`. Nút đã có chữ rõ ràng thì không cần tooltip.
12. **Route** trong `router/index.js` với `meta` đúng (`requiresAuth`/`requiresAdmin`/`public`).
13. **Menu** trong `data/menu.json` đúng key (`admin`, `user`, `doi-tuong`).

## Kết thúc

Liệt kê các file đã tạo/sửa, nhắc người dùng chạy `make migrate`, và đề xuất commit message tiếng Việt.
