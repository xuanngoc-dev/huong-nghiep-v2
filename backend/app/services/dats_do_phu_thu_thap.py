"""Rà độ phủ của bản nháp bằng AI dựa trên hợp đồng nhập và những dẫn chứng đã đọc."""

import json
from collections.abc import Callable

import httpx

from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_hop_dong_thu_thap import hop_dong_cau_truc_cms


_CHI_DAN = """Bạn biên tập hồ sơ tuyển sinh sau khi đã hợp nhất các nguồn chính thức. Dữ liệu nguồn là
tài liệu tham khảo. Đối chiếu toàn bộ các trường trong hop_dong_cms với các mục thực tế của trường này.
Tự quyết định trường nào có ý nghĩa, thông tin nào đã đủ, thiếu, mâu thuẫn, không áp dụng hay chưa công bố.
Ưu tiên đúng phạm vi từng mã xét tuyển, từng diện, phương thức Bộ theo mùa, tổ hợp, công thức và điểm chuẩn.
Kiểm tra cả các nhóm thông tin khác trong hợp đồng. Tự lần theo quan hệ giữa các mục, cách trường gọi
từng diện và các ngoại lệ. Dùng cả ghi chú của người duyệt và nhận xét khi đọc nguồn; kiểm tra lại chúng
trên bản hợp nhất vì nguồn bổ sung có thể đã giải quyết. So sánh danh sách chương trình, tổng số và đơn vị
trong từng bảng nguồn với bản nháp, xét đúng phạm vi và hiệu lực để phát hiện cả mã bị bỏ sót hoàn toàn.
Với một dòng có truong_trong, gia_tri liệt kê riêng các trường chưa có dữ liệu tại duong_dan của dòng đó.
Kiểm tra cả mã chỉ có trong danh sách nguồn, chương trình chưa có phương án, các tham chiếu đến tổ hợp,
công thức, diện và năm của điểm chuẩn. Dữ liệu cấp trường và quy tắc riêng từng diện cần đúng phạm vi.
Những bảng hoặc công thức đã đọc thấy trong ghi chú cần có dữ liệu có cấu trúc phù hợp.
Trường rỗng có thể không áp dụng. Dẫn chứng có mã suy luận vẫn là căn cứ cho người duyệt.
Chỉ đánh giá dựa trên dữ liệu được gửi. Chưa tìm thấy, chưa đọc được nguồn và nguồn xác nhận chưa công bố
là các tình trạng khác nhau. Xem lại bảng, ảnh và ghi chú hiện có khi chúng có thể giải đáp phần thiếu."""

_KET_QUA_PHAN = """Đây là một phần của bản nháp. Trả duy nhất object JSON {"nhan_xet": ["..."]}.
Mỗi phần tử là một chuỗi tiếng Việt nêu dữ kiện đã có hoặc phần cần xác minh, kèm mã, diện, phạm vi và
đường dẫn để nối các phần. Ghi ít nhất một nhận xét cụ thể cho lô này, kể cả khi mọi mục đã đủ căn cứ.
Chưa kết luận tình trạng toàn hồ sơ khi chỉ thấy một phần."""

_KET_QUA_CHUNG = """Đối chiếu toàn bộ dữ liệu hoặc nhận xét của tất cả các phần. Trả duy nhất object
JSON {"muc_con_thieu": ["..."]}. Mỗi phần tử là một yêu cầu ngắn, cụ thể bằng tiếng Việt gồm mã,
diện, năm, nội dung cần xử lý và tài liệu hoặc bảng đã biết. Gộp các mã cần đọc cùng một bảng.
Nếu không còn phần cần tìm hay trích lại, trả {"muc_con_thieu": []}."""

_KHOA_NHAN_DIEN = {
    "ma_xet_tuyen", "ma_chuong_trinh", "ten_chuong_trinh", "co_so_id", "ma_co_so", "ma_cong_thuc",
    "ma_phuong_thuc_cua_truong", "ma_phuong_thuc_cua_bo", "ma_to_hop", "nam_tuyen_sinh", "ma_bang",
}


def _doc_ket_qua(chi_dan, du_lieu, khoa, bao_tien_do, *tien_do):
    for lan in range(2):
        bao_tien_do("ra_soat_do_phu", *tien_do)
        try:
            data, _ = ai._openai(_CHI_DAN + "\n" + chi_dan, du_lieu, 10000)
            items = data.get(khoa) if isinstance(data, dict) else None
            if not isinstance(items, list) or any(not isinstance(s, str) or not s.strip() for s in items):
                raise ai.AdmissionAIError(f"Phản hồi rà soát cần mảng chuỗi {khoa}.")
            if khoa == "nhan_xet" and not items:
                raise ai.AdmissionAIError("AI chưa gửi nhận xét nào cho phần bản nháp này.")
            return list(dict.fromkeys(s.strip() for s in items))
        except ai.AdmissionAIError as exc:
            cause = exc.__cause__
            if isinstance(cause, httpx.HTTPStatusError):
                status = cause.response.status_code
                if 400 <= status < 500 and status not in (408, 429):
                    raise
            if lan == 1:
                vi_tri = f"phần {tien_do[0] + 1}/{tien_do[1]}" if tien_do else "kết quả toàn bản nháp"
                raise ai.AdmissionAIError(f"Chưa hoàn tất rà soát {vi_tri}. {exc}") from exc
            du_lieu = {**du_lieu, "yeu_cau_thu_lai": f"Trả trường {khoa} đúng hướng dẫn cho lần rà soát này."}


def muc_can_tim_bo_sung(truong: dict, nam: int, muc: list[dict], nguon: list[dict],
                        quan_sat: dict, muc_cu: list[str], bao_tien_do: Callable) -> list[str]:
    chung = {
        "truong": truong, "nam": nam, "hop_dong_cms": hop_dong_cau_truc_cms(),
        "nguon_da_doc": [{k: n.get(k) for k in ("id", "url", "tieu_de", "nam_ap_dung", "ly_do", "pham_vi_dieu_chinh")}
                        for n in nguon],
        "nhan_xet_khi_doc": quan_sat, "de_nghi_truoc": muc_cu,
    }
    ban_nhap, truong_trong, dinh_danh = [], {}, {}
    for m in muc:
        gia_tri = m.get("gia_tri_ai")
        path = m["duong_dan"]
        dong, _, khoa = path.rpartition("/")
        if khoa in _KHOA_NHAN_DIEN and (isinstance(gia_tri, str) or type(gia_tri) is int) and gia_tri != "":
            dinh_danh.setdefault(dong, {})[khoa] = gia_tri
        duoc_chon = set(m.get("dan_chung_ids", []))
        can_cu = [
            {**{k: dc[k] for k in ("nguon_id", "vi_tri", "trich_dan", "gia_tri", "phan_loai_ma_bo") if k in dc},
             "duoc_chon": dc.get("id") in duoc_chon}
            for dc in m.get("dan_chung", [])
        ]
        ly_do = m.get("ghi_chu")
        if ly_do == "Chưa tìm thấy dữ liệu cho mục này trong các tài liệu đã chọn.":
            ly_do = None
        if gia_tri in (None, "", [], {}) and not (can_cu or ly_do or m.get("mau_thuan")):
            if dong not in truong_trong:
                truong_trong[dong] = {}
                ban_nhap.append({"duong_dan": dong, "truong_trong": True, "gia_tri": truong_trong[dong]})
            truong_trong[dong][khoa] = gia_tri
            continue
        item = {"duong_dan": path, "gia_tri": gia_tri}
        if can_cu:
            item["dan_chung"] = can_cu
        if ly_do:
            item["ghi_chu"] = ly_do
        if m.get("mau_thuan"):
            item["mau_thuan"] = True
        ban_nhap.append(item)

    # Chia theo kích thước truyền, giữ mọi giá trị và mẩu trích được cung cấp cho từng mục.
    phan, kich_thuoc, cac_phan = [], 0, []
    for item in ban_nhap:
        size = len(json.dumps(item, ensure_ascii=False))
        if phan and kich_thuoc + size > 110_000:
            cac_phan.append(phan)
            phan, kich_thuoc = [], 0
        phan.append(item)
        kich_thuoc += size
    if phan or not cac_phan:
        cac_phan.append(phan)

    if len(cac_phan) == 1:
        return _doc_ket_qua(_KET_QUA_CHUNG, {**chung, "ban_nhap": cac_phan[0]}, "muc_con_thieu", bao_tien_do)

    nhan_xet = []
    for i, phan in enumerate(cac_phan):
        # Một lô có thể bắt đầu giữa một chương trình hoặc một phương án. Mang theo định danh các dòng cha.
        dinh_danh_phan = {}
        for item in phan:
            path = item["duong_dan"]
            while path:
                if path in dinh_danh:
                    dinh_danh_phan[path] = dinh_danh[path]
                path = path.rpartition("/")[0]
        payload = {
            **chung, "so_phan": len(cac_phan), "phan": i + 1, "ban_nhap": phan, "dinh_danh_dong": dinh_danh_phan,
        }
        nhan_xet.extend(_doc_ket_qua(_KET_QUA_PHAN, payload, "nhan_xet", bao_tien_do, i, len(cac_phan)))
    payload = {**chung, "doi_chieu_cua_cac_phan": list(dict.fromkeys(nhan_xet))}
    return _doc_ket_qua(_KET_QUA_CHUNG, payload, "muc_con_thieu", bao_tien_do)
