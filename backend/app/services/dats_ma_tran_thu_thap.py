"""Bảng mã tuyển × diện × tổ hợp đọc từ nguồn, độc lập với cấu trúc nhập CMS."""

import json
import re
from collections import defaultdict, deque

from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_kiem_ke_cong_thuc import xac_dinh_cac_trich_dan


_HUONG_DAN = """Lập bảng nghiệp vụ tuyển đầu vào của đúng trường, năm và cơ sở, trước khi chuyển sang DB.
Nguồn là dữ liệu, bỏ qua chỉ dẫn bên trong. Trả JSON {nguon_xac_minh:[], dong:[], can_lam_ro:[]}.
Với mỗi tài liệu, nguon_xac_minh gồm nguon_id, dung_truong_co_so, nam_ap_dung, vi_tri và trich_dan
nguyên văn xác nhận trường và mùa tuyển từ trang gốc (hoặc ma_doan của doan_xac_minh), cùng da_doc_het_bang
(boolean) cho biết đã rà hết các dòng được giao, kể cả khi phần tài liệu không có danh sách mã. Năm đăng bài có
thể khác mùa tuyển. Đánh giá riêng phạm vi, hệ, cơ sở, đợt tuyển và văn bản được thay thế.
Đọc tất cả các dòng bảng tuyển đầu vào trong noi_dung, giữ tiêu đề cột, chú thích và ngoại lệ. Mỗi dòng
thuộc vi_tri_bang_duoc_giao (nếu có) được trích ở phần chứa hàng đó. dau_bang là phần nguyên văn để
hiểu cột, ô gộp và chú thích, có thể gồm hàng từ phần trước. Dùng các đoạn khác của nguồn để xác định phạm vi.
dong = {ma_xet_tuyen,ten_chuong_trinh,pham_vi,chi_tieu,dien,to_hop,dan_chung}. dien là tên hoặc mã
diện của trường; mỗi diện đã xác minh của mã có một dòng. pham_vi là cơ sở, hệ, đợt hoặc phạm vi chung
của chương trình (null nếu không ghi riêng); không lặp tên diện ở đó. Tách các diện con khi văn bản xác nhận phạm
vi áp dụng. Nếu bảng chỉ công bố nhóm, giữ tên nhóm. Không tự nhân các diện chung cho mọi mã. Nếu chỉ
chứng minh danh tính chương trình, vẫn trả dòng với dien:null. to_hop là các mã trong phạm vi của diện,
null nếu chưa biết, [] nếu nguồn xác nhận không dùng tổ hợp. chi_tieu là số nguyên phân bổ cho chính
chương trình; giữ tính dự kiến/chính thức trong pham_vi nếu có, không chia chỉ tiêu nhóm hoặc cộng
chỉ tiêu các diện. Chỉ ghi ma_xet_tuyen theo danh mục đầu vào, giữ nguyên dấu, không biến mã ngành nội
bộ hoặc chương trình dành cho sinh viên đã nhập học thành mã tuyển mới. Không suy luận mã Bộ ở bước này.
dan_chung = [{nguon_id,vi_tri,trich_dan}], chép nguyên nhãn vi_tri trong noi_dung. Hệ thống tự gắn URL.
Dùng đoạn ngắn nguyên văn từ nội dung đã gửi, giữ cả dòng
chương trình và phần xác nhận diện/tổ hợp/chỉ tiêu khi ở vị trí khác. Bảng điểm chuẩn nhiều năm không
tự xác lập phương án cho năm này. can_lam_ro là các câu hỏi cụ thể về dữ kiện đang mâu thuẫn/khó đọc.
Trang chỉ mô tả công thức chung hoặc điểm lịch sử có thể trả dong rỗng."""


# Một hàng nguồn có thể cần trả nhiều diện, mỗi diện kèm nguyên văn dẫn chứng.
_DONG_BANG_MOI_LUOT = 9


def _phan_bang(van_ban):
    """Giữ nguyên dòng, thứ tự, ghi chú và vị trí ô gộp của bảng HTML hoặc bảng OCR."""
    dong = van_ban.splitlines(keepends=True)
    hang = [i for i, s in enumerate(dong) if "|" in s.strip().strip("|")]
    if len(hang) < 3 or not any(all(not s.strip() or s.startswith("[Cấu trúc HTML hàng ") for s in dong[a + 1:b])
                                for a, b in zip(hang, hang[1:])):
        return []
    # Phần đầu nguyên văn cung cấp nhãn cột. Có ô gộp thì giữ cả các dòng tiêu đề liên quan.
    so_dong_dau = 1
    for s in dong[hang[0] + 1:hang[1]]:
        if s.startswith("[Cấu trúc HTML hàng "):
            do_cao = max((int(n) for n in re.findall(r"rowspan=(\d{1,5})\b", s)), default=1)
            so_dong_dau = max(so_dong_dau, do_cao)
            if re.search(r"colspan=(?:[2-9]|\d{2,})\b", s):
                so_dong_dau = max(so_dong_dau, 2)
    so_dong_dau = min(so_dong_dau, len(hang) - 1, _DONG_BANG_MOI_LUOT)
    dau = "".join(dong[:hang[so_dong_dau]]).rstrip("\r\n")
    chu_thich = "".join(s for s in dong[hang[-1] + 1:] if not s.startswith("[Cấu trúc HTML hàng ")).strip("\r\n")
    o_gop = []
    ghi_chu_giua_bang = []
    for h in range(so_dong_dau, len(hang) - 1):
        khoi = dong[hang[h]:hang[h + 1]]
        do_cao = max((int(n) for s in khoi[1:] if s.startswith("[Cấu trúc HTML hàng ")
                      for n in re.findall(r"rowspan=(\d{1,5})\b", s)), default=1)
        if do_cao > 1:
            o_gop.append((h, h + do_cao, "".join(khoi).rstrip("\r\n")))
        if any(s.strip() and not s.startswith("[Cấu trúc HTML hàng ") for s in khoi[1:]):
            ghi_chu_giua_bang.append((h, "".join([*khoi, dong[hang[h + 1]]]).rstrip("\r\n")))
    tach = []
    for i in range(1, len(hang), _DONG_BANG_MOI_LUOT):
        j = i + _DONG_BANG_MOI_LUOT
        cuoi = hang[j] if j < len(hang) else len(dong)
        text = "".join(dong[0 if i == 1 else hang[i]:cuoi]).rstrip("\r\n")
        ngu_canh = [dau]
        # Ô rowspan có thể bắt đầu ở phần trước và còn áp dụng ở phần này.
        ngu_canh.extend(khoi for h, den, khoi in o_gop if h < i < den)
        ngu_canh.extend(khoi for h, khoi in ghi_chu_giua_bang if h < i or h >= j)
        if chu_thich:
            ngu_canh.append(chu_thich)
        tach.append((text, "\n".join(ngu_canh), min(len(hang), j) - i))
    return tach


def _chia_nhom_bang_day(cac_nhom, tai_lieu):
    """Chia theo số hàng cần trả JSON, giữ văn bản ngoài bảng và dẫn chứng của cùng nguồn."""
    da_gui = defaultdict(list)
    for nhom in cac_nhom:
        for n in nhom:
            for vt, s in n["noi_dung"]:
                da_gui[n["id"], vt].append(s)
    # Bộ chia ký tự chung có giao nhau. Chỉ dùng lại toàn bảng khi nhận đủ đúng các lát gốc.
    bang_tron = {}
    for i, doc in tai_lieu.items():
        for vt, s in doc.doan:
            khoa = i, vt
            if len(da_gui.get(khoa, ())) > 1 and da_gui[khoa] == list(ai._cat_van_ban(s, ai._KY_TU_MOI_NHOM // 2)):
                if len(_phan_bang(s)) > 1:
                    bang_tron[khoa] = s
    da_chia = set()
    ket_qua = []
    for nhom in cac_nhom:
        con_lai = []
        so_dong_con_lai = 0
        for n in nhom:
            bang, ngu_canh = [], []
            for vt, s in n["noi_dung"]:
                khoa = n["id"], vt
                if khoa in bang_tron:
                    if khoa in da_chia:
                        continue
                    da_chia.add(khoa)
                    s = bang_tron[khoa]
                if cac_phan := _phan_bang(s):
                    bang.append((vt, s, cac_phan))
                else:
                    ngu_canh.append((vt, s))
            so_dong = sum(so for _, _, cac_phan in bang for _, _, so in cac_phan)
            if so_dong <= _DONG_BANG_MOI_LUOT:
                if so_dong_con_lai + so_dong > _DONG_BANG_MOI_LUOT:
                    ket_qua.append(con_lai)
                    con_lai, so_dong_con_lai = [], 0
                if len(ngu_canh) + len(bang) == len(n["noi_dung"]):
                    con_lai.append(n)
                elif ngu_canh or bang:
                    con_lai.append({**n, "noi_dung": [*ngu_canh, *((vt, s) for vt, s, _ in bang)]})
                so_dong_con_lai += so_dong
                continue
            nhan_canh = {nhan for nhan, _ in ngu_canh}
            dau_canh = {v: t for v, t in n.get("dau_bang", {}).items() if v in nhan_canh}
            for vt, _, cac_phan in bang:
                urls = {v: url for v, url in n.get("url_dan_chung", {}).items() if v == vt or v in nhan_canh}
                for text, dau, _ in cac_phan:
                    phan = {**n, "noi_dung": [*ngu_canh, (vt, text)], "dau_bang": {**dau_canh, vt: dau},
                            "url_dan_chung": urls, "vi_tri_bang_duoc_giao": vt}
                    ket_qua.append([phan])
        if con_lai:
            ket_qua.append(con_lai)
    return ket_qua


def _duy_nhat(ds):
    return list({json.dumps(item, sort_keys=True, ensure_ascii=False): item for item in ds}.values())


def gop_ma_tran(cu, moi):
    cu, moi = cu or {}, moi or {}
    dong = {}
    for row in [*cu.get("dong", []), *moi.get("dong", [])]:
        khoa = json.dumps({k: v for k, v in row.items() if k != "dan_chung"}, ensure_ascii=False, sort_keys=True)
        if khoa in dong:
            dong[khoa]["dan_chung"] = _duy_nhat([*dong[khoa]["dan_chung"], *row["dan_chung"]])
        else:
            dong[khoa] = dict(row)
    loi = {**cu.get("loi_theo_nguon", {}), **moi.get("loi_theo_nguon", {})}
    for i in moi.get("da_doc", []):
        loi.pop(str(i), None)
    cau_hoi = {**cu.get("cau_hoi_theo_nguon", {}), **moi.get("cau_hoi_theo_nguon", {})}
    return {"dong": list(dong.values()), "loi_theo_nguon": loi, "cau_hoi_theo_nguon": cau_hoi,
            "da_doc": sorted((set(cu.get("da_doc", [])) | set(moi.get("da_doc", []))) - {int(i) for i in loi}),
            "can_lam_ro": list(dict.fromkeys(q for ds in cau_hoi.values() for q in ds))}


def _dong_co_can_cu(row, docs):
    if not isinstance(row, dict):
        return None
    ma, ten = row.get("ma_xet_tuyen"), row.get("ten_chuong_trinh")
    if not isinstance(ma, str) or not 0 < len(ma.strip()) <= 20 or not isinstance(ten, str) or not ten.strip():
        return None
    if not isinstance(row.get("dan_chung"), list):
        return None
    dc = []
    co_trich_tach_dong = False
    for item in row["dan_chung"]:
        if not isinstance(item, dict) or type(i := item.get("nguon_id")) is not int or i not in docs:
            return None
        doc, phan = docs[i]
        vt, cac_trich = xac_dinh_cac_trich_dan(phan, doc, item.get("vi_tri"), item.get("trich_dan"))
        if vt is None:
            return None
        co_trich_tach_dong = co_trich_tach_dong or len(cac_trich) > 1
        for trich in cac_trich:
            dc.append({"nguon_id": i, "vi_tri": vt, "trich_dan": trich, "url_tai_lieu": doc.url_dan_chung.get(vt, doc.url)})
    if not dc:
        return None
    # Đối chiếu định danh và số do AI trích với nguyên văn. AI quyết định ý nghĩa và phạm vi của cột.
    trich = " ".join(d["trich_dan"] for d in dc)
    nhan_ma = re.compile(rf"(?<![\w/-]){re.escape(ma.strip())}(?![\w/-])", re.IGNORECASE)
    if not nhan_ma.search(trich):
        return None
    # Với các trích cách nhau, tên và chỉ tiêu ở một dòng của mã khác không chứng minh được dòng này.
    if co_trich_tach_dong:
        trich = " ".join(s for d in dc for s in d["trich_dan"].splitlines() if nhan_ma.search(s))
    if ai._van_ban(ten).casefold() not in ai._van_ban(trich).casefold():
        return None
    to_hop, chi_tieu = row.get("to_hop"), row.get("chi_tieu")
    if to_hop is not None and (not isinstance(to_hop, list) or any(not isinstance(t, str) or not t.strip() for t in to_hop)):
        return None
    if chi_tieu is not None and (type(chi_tieu) is not int or chi_tieu < 0):
        return None
    if chi_tieu is not None:
        cac_so = re.findall(r"(?<!\w)\d+(?:[.,  ]\d{3})*(?!\w)", trich)
        if not any(int(re.sub(r"[.,  ]", "", s)) == chi_tieu for s in cac_so):
            return None
    if any(v is not None and not isinstance(v, str) for v in (row.get("pham_vi"), row.get("dien"))):
        return None
    return {"ma_xet_tuyen": ma.strip(), "ten_chuong_trinh": ten.strip(), "pham_vi": row.get("pham_vi"),
            "chi_tieu": chi_tieu, "dien": row.get("dien"), "to_hop": to_hop, "dan_chung": dc}


def lap_ma_tran_ai(truong, nam, cac_nhom, tai_lieu, doan_goc, bao_tien_do):
    dong, cau_hoi, loi, da_xac_minh = [], defaultdict(list), {}, set()
    cac_nhom = _chia_nhom_bang_day(cac_nhom, tai_lieu)
    for stt, nhom in enumerate(cac_nhom):
        hang_doi = deque([(nhom, 0)])
        while hang_doi:
            phan, lan = hang_doi.popleft()
            bao_tien_do("lap_ma_tran", stt, len(cac_nhom))
            try:
                data, _ = ai._openai(_HUONG_DAN, {"truong": truong, "nam": nam, "tai_lieu": phan}, 10000)
                if not isinstance(data, dict) or any(not isinstance(data.get(k), list) for k in ("nguon_xac_minh", "dong", "can_lam_ro")):
                    raise ai.AdmissionAIError("Lượt lập bảng mã chưa trả đủ ba danh sách.")
            except ai.AdmissionAIError as exc:
                if isinstance(exc, ai._LoiDungLuongModel) and (hai := ai._tach_nhom(phan)):
                    hang_doi.extendleft((p, 0) for p in reversed(hai))
                elif lan == 0:
                    hang_doi.appendleft((phan, 1))
                else:
                    for n in phan:
                        loi[str(n["id"])] = f"Chưa rà xong bảng tuyển của nguồn #{n['id']}. {exc}"
                continue
            xac_minh = {n["nguon_id"]: n for n in data["nguon_xac_minh"]
                        if isinstance(n, dict) and type(n.get("nguon_id")) is int}
            docs = {}
            for n in phan:
                i = n["id"]
                if ly_do := ai._loi_xac_minh_nguon(n, tai_lieu[i], xac_minh, nam, doan_goc[i]):
                    loi[str(i)] = ly_do
                else:
                    da_xac_minh.add(i)
                    docs[i] = tai_lieu[i], n
                    if xac_minh[i].get("da_doc_het_bang") is not True:
                        loi[str(i)] = f"AI chưa xác nhận đã rà hết các dòng bảng của nguồn #{i}."
            for item in data["dong"]:
                if row := _dong_co_can_cu(item, docs):
                    dong.append(row)
                else:
                    for i in docs:
                        loi[str(i)] = f"Đọc lại dòng mã tuyển có dẫn chứng chưa khớp ở nguồn #{i}."
            for i in docs:
                cau_hoi[str(i)].extend(q.strip() for q in data["can_lam_ro"] if isinstance(q, str) and q.strip())
    return gop_ma_tran(None, {"dong": dong, "da_doc": list(da_xac_minh - {int(i) for i in loi}),
                               "loi_theo_nguon": loi, "cau_hoi_theo_nguon": dict(cau_hoi)}), da_xac_minh


_NHANH = (("dats_tuyen_sinh", "dats_chuong_trinh_dao_tao", "chi_tieu_tuyen_sinh"),
          ("quy_tac_xet_tuyen", "chuong_trinh", "chi_tieu"))


def _theo_ma(dong):
    theo_ma = defaultdict(list)
    for row in dong:
        theo_ma[row["ma_xet_tuyen"]].append(row)
    return theo_ma


def chieu_danh_muc(ket_qua):
    """Chuyển định danh và chỉ tiêu đã xác minh vào hai nhánh, giữ xung đột để duyệt."""
    bang = ket_qua["ma_tran_goc"]["dong"]
    for ma, dong in _theo_ma(bang).items():
        ten = {r["ten_chuong_trinh"] for r in dong}
        chi_tieu = {r["chi_tieu"] for r in dong if r["chi_tieu"] is not None}
        if len(ten) != 1 or len({r["pham_vi"] for r in dong if r["pham_vi"]}) > 1:
            continue
        for khoi, mang, khoa_ct in _NHANH:
            cac_dong = ket_qua["du_lieu"][khoi].setdefault(mang, [])
            if not isinstance(cac_dong, list):
                continue
            chi_so = [i for i, r in enumerate(cac_dong) if isinstance(r, dict) and r.get("ma_xet_tuyen") == ma]
            if len(chi_so) > 1:
                continue
            i = chi_so[0] if chi_so else len(cac_dong)
            if not chi_so:
                cac_dong.append({"ma_xet_tuyen": ma, "ten_chuong_trinh": next(iter(ten))})
                if khoi == "quy_tac_xet_tuyen":
                    cac_dong[i]["ma_chuong_trinh"] = ma
            row = cac_dong[i]
            ten_nguon = next(iter(ten))
            ten_da_co = row.get("ten_chuong_trinh")
            if ten_da_co and (not isinstance(ten_da_co, str) or ai._van_ban(ten_da_co).casefold() != ai._van_ban(ten_nguon).casefold()):
                continue
            row["ten_chuong_trinh"] = ten_da_co or ten_nguon
            gia_tri = {"ten_chuong_trinh": row["ten_chuong_trinh"], "ma_xet_tuyen": ma}
            if len(chi_tieu) == 1 and row.get(khoa_ct) in (None, next(iter(chi_tieu))):
                gia_tri[khoa_ct] = row[khoa_ct] = next(iter(chi_tieu))
            for k, v in gia_tri.items():
                dc = _duy_nhat([{**d, "gia_tri": v} for r in dong if k != khoa_ct or r["chi_tieu"] == v for d in r["dan_chung"]])
                muc = {"duong_dan": f"/{khoi}/{mang}/{i}/{k}", "dan_chung": dc}
                if muc not in ket_qua["muc"]:
                    ket_qua["muc"].append(muc)


def bao_cao_ma_tran(ket_qua):
    ma_tran = ket_qua["ma_tran_goc"]
    cac_ma = _theo_ma(ma_tran["dong"])
    du_lieu = ket_qua["du_lieu"]
    nhanh = [(_theo_ma(r for r in du_lieu[k].get(m, []) or [] if isinstance(r, dict)
                        and isinstance(r.get("ma_xet_tuyen"), str)), khoa_ct) for k, m, khoa_ct in _NHANH]
    co_ma = set(cac_ma).intersection(*(bang for bang, _ in nhanh))
    chua_ghi, so_lien_ket, so_da_noi = [], 0, 0
    khop = ket_qua.get("dong_ma_tran_da_noi", set())
    for i, row in enumerate(ma_tran["dong"]):
        ma = row["ma_xet_tuyen"]
        thieu = []
        if ma not in co_ma:
            thieu.append("Chưa có mã ở cả hai danh sách chương trình")
        ten = ai._van_ban(row["ten_chuong_trinh"]).casefold()
        cung_ten = [([r for r in bang[ma] if isinstance(r.get("ten_chuong_trinh"), str)
                      and ai._van_ban(r["ten_chuong_trinh"]).casefold() == ten], khoa_ct) for bang, khoa_ct in nhanh]
        if ma in co_ma and any(len(ds) != 1 for ds, _ in cung_ten):
            thieu.append(f"Cần đối chiếu danh tính hoặc cơ sở của chương trình {row['ten_chuong_trinh']}")
        if row["chi_tieu"] is not None and any(not any(r.get(k) == row["chi_tieu"] for r in ds) for ds, k in cung_ten):
            thieu.append(f"Chỉ tiêu chương trình {row['chi_tieu']} chưa khớp")
        if row["dien"]:
            so_lien_ket += 1
            if i in khop:
                so_da_noi += 1
            else:
                to_hop = ", ".join(row["to_hop"] or [])
                thieu.append(f"Chưa đối chiếu đủ diện {row['dien']}" + (f" và tổ hợp {to_hop}" if to_hop else ""))
        if thieu:
            chua_ghi.append({"ma_xet_tuyen": ma, "noi_dung": ". ".join(thieu), "dan_chung": row["dan_chung"]})
    can_lam_ro = [*ma_tran["loi_theo_nguon"].values(), *ma_tran["can_lam_ro"]]
    danh_muc_goc = [b for b in ket_qua.get("doi_chieu_chuong_trinh", []) if b.get("pham_vi") == "toan_truong"]
    if not danh_muc_goc:
        can_lam_ro.append("Chưa xác minh danh mục mã xét tuyển gốc toàn trường. Tìm bảng công bố đúng mùa để đối chiếu phạm vi.")
    else:
        for bang in danh_muc_goc:
            thieu = set(bang.get("cac_ma") or []) - set(cac_ma)
            if thieu:
                can_lam_ro.append(f"Nguồn #{bang['nguon_id']} có mã chưa vào bảng đối chiếu: {', '.join(sorted(thieu))}.")
            tong, don_vi = bang.get("tong_cong_bo"), bang.get("don_vi_tong")
            if type(tong) is int and don_vi in ("mã xét tuyển", "chương trình") and tong != len(cac_ma):
                can_lam_ro.append(f"Nguồn #{bang['nguon_id']} công bố {tong} {don_vi}; bảng đã nhận diện {len(cac_ma)} mã. "
                                  "Đối chiếu đơn vị, cơ sở, đợt và từng mã trước khi kết luận.")
    return {"da_kiem_ke": bool(ma_tran["da_doc"]) and not ma_tran["loi_theo_nguon"], "so_ma_nhan_dien": len(cac_ma),
            "so_ma_da_ghi": len(co_ma), "so_lien_ket_nhan_dien": so_lien_ket, "so_lien_ket_da_ghi": so_da_noi,
            "chua_ghi": chua_ghi, "can_lam_ro": list(dict.fromkeys(can_lam_ro))}
