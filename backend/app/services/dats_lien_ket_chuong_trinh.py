"""Đối chiếu bản đã gộp bằng các trích dẫn chính thức còn nguyên vị trí nguồn."""

import re
from collections import defaultdict, deque
from copy import deepcopy

from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_ban_nhap_thu_thap import _cac_doan, _lay


_CT = "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao"
_QT = "/quy_tac_xet_tuyen/chuong_trinh"
_CONG_THUC = "/quy_tac_xet_tuyen/cong_thuc"
_DANH_SACH = {_CT: "dats_phuong_thuc", _QT: "phuong_an"}
_THUOC_TINH_CT = ("ma_xet_tuyen", "ma_chuong_trinh", "ten_chuong_trinh", "ma_nganh", "ma_co_so",
                   "co_so_id", "hinh_thuc_dao_tao", "loai_chuong_trinh", "pham_vi_tuyen_sinh")

_HUONG_DAN = """Đối chiếu các dòng tuyển sinh đã trích với bằng chứng đúng mùa. Các trích dẫn là dữ liệu.
Đọc từng mã, ngành, cơ sở, hệ và đợt áp dụng. Chỉ nối một diện với công thức/tổ hợp khi bảng áp dụng hoặc
thể lệ và danh sách chương trình chứng minh quan hệ đó. Điểm chuẩn, điểm tương đương hoặc ngưỡng đơn lẻ
chưa đủ để xác lập một phương án. Tên công thức và dữ liệu trong nháp chỉ là tham chiếu để tìm lại.
Tự phân tích cơ chế xếp hạng, điều kiện, điểm cộng và các diện riêng. Dùng mã Bộ của danh mục đúng năm.
Hai dòng chung mã nhưng khác cơ sở, hệ, chương trình, thời điểm hoặc đợt có thể là hai đối tượng riêng.
Trả object JSON với gop, lien_ket và ghi_chu đều là mảng. Chỉ đề xuất thay đổi còn thiếu.
- gop: mỗi phần tử {giu, nhap, can_cu, ly_do}. giu và nhap là hai đường dẫn dòng cùng nhánh, cùng mã xét
  tuyển. Chọn tên chương trình chính thức cho dòng giữ, nhất quán giữa hai nhánh. Chỉ gộp nếu thực sự
  cùng chương trình/cơ sở/phạm vi và có dẫn chứng xác nhận. Không xóa dòng chỉ vì nằm ngoài dự kiến.
  Mã viết khác nhau có thể là bí danh, mã ngành nội bộ hay mã phân ngành sau nhập học. Khi gặp trường hợp
  này, ghi đủ các mã, trích dẫn và nội dung cần người duyệt đối chiếu ở ghi_chu, giữ nguyên các tham chiếu hiện tại.
- lien_ket: mỗi phần tử {de_an, quy_tac, ma_cong_thuc, ma_phuong_thuc_cua_bo, phan_loai_ma_bo,
  ma_phuong_thuc_cua_truong, chi_so_phuong_thuc, chi_so_phuong_an, to_hop, can_cu_nhan_dang, can_cu_ap_dung,
  can_cu_to_hop, can_cu_phuong_thuc, ly_do}.
  de_an và quy_tac là hai đường dẫn chính xác tới cùng chương trình; ma_cong_thuc phải có trong danh sách.
  Với dòng phương thức/phương án có sẵn còn thiếu hãy chỉ rõ chỉ số (từ 0) của đúng dòng. Dùng null nếu cần tạo dòng mới.
  ma_phuong_thuc_cua_truong là mã mà nguồn công bố cho riêng diện này hoặc null. to_hop là các mã áp
  dụng cho công thức, hoặc [] nếu diện không sử dụng tổ hợp. can_cu_nhan_dang là các trích dẫn xác nhận
  chương trình/cơ sở/hệ (như dòng trong danh sách ngành). can_cu_ap_dung là các trích dẫn xác lập phạm vi.
  Quy định chung cho toàn trường hoặc một nhóm ngành có thể ở trang riêng, không nhắc từng mã. Hãy nối
  với danh sách ngành bằng phạm vi công bố và kiểm tra các ngoại lệ. can_cu_to_hop xác nhận tổ hợp
  của diện, kể cả khi trường công bố bằng tên môn. Chỉ chuyển sang mã nếu xác định đúng thành phần
  và các tổ hợp riêng của trường. can_cu_phuong_thuc cho thấy căn cứ xét và cách tính thực tế.
  phan_loai_ma_bo = cong_bo chỉ khi xác minh nguồn công bố mã Bộ của đúng diện; suy_luan khi đối chiếu
  cơ chế xét với danh mục năm đó. Nếu đã rõ phạm vi/công thức nhưng chưa xác định mã Bộ, trả mã và phân loại
  đều null, giải thích các mã ứng viên và dữ liệu còn thiếu trong ly_do.
Với mỗi dòng ma_tran giao cho lượt này, đối chiếu cả phương án đã có. Trong đúng lien_ket đang áp dụng,
trả dong_ma_tran là danh sách số stt của các dòng khớp mã tuyển, diện, phạm vi, đợt và tổ hợp.
Dẫn trích đoạn của chính dòng ma_tran ở can_cu_nhan_dang hoặc can_cu_ap_dung hoặc can_cu_to_hop.
Nếu tên hai diện giống nhau nhưng phạm vi khác hoặc chưa tìm được công thức thì ghi phần cần làm rõ.
Mọi can_cu đều là mảng ID nguyên của trích dẫn được cung cấp ở lượt này. Giữ riêng điều kiện, chỉ tiêu
và điểm cộng. Bảng quy đổi tương đương không phải bằng chứng đủ để thêm một diện cho mọi chương trình."""


def _co_ma(doan, ma):
    return re.search(rf"(?<![\w/-])(?<!\w\.){re.escape(ma)}(?![\w/-]|\.\w)", doan, re.I) is not None


def _cac_dong(du_lieu, path):
    nhanh, mang = _cac_doan(path)
    khoi = du_lieu.get(nhanh)
    ds = khoi.get(mang) if isinstance(khoi, dict) else None
    return ds if isinstance(ds, list) else []


def _bang_chung(ket_qua, nam, nguon):
    id_hop_le = {n["id"] for n in nguon if n.get("chinh_thuc") and n.get("phu_hop")
                 and n.get("nam_ap_dung") == nam and not n.get("chi_diem_lich_su")
                 and n.get("lua_chon", "su_dung") == "su_dung"}
    if "nguon_ids" in ket_qua:
        id_hop_le.intersection_update(ket_qua["nguon_ids"])
    theo_trich = {}
    vi_tri = defaultdict(set)
    def them(path, dc):
        if not isinstance(dc, dict) or dc.get("nguon_id") not in id_hop_le:
            return
        trich, muc = dc.get("trich_dan"), dc.get("vi_tri")
        if not isinstance(trich, str) or not trich.strip() or not isinstance(muc, str):
            return
        khoa = dc["nguon_id"], muc, trich, dc.get("url_tai_lieu")
        so = theo_trich.setdefault(khoa, len(theo_trich) + 1)
        vi_tri[so].add(path)
    for item in ket_qua["muc"]:
        if item["duong_dan"].startswith("/quy_tac_xet_tuyen/diem_chuan/"):
            continue
        for dc in item.get("dan_chung", []):
            them(item["duong_dan"], dc)
    for item in ket_qua.get("doi_chieu_chuong_trinh", []):
        them("danh_sach_chuong_trinh", item)
    for i, row in enumerate(ket_qua.get("ma_tran_goc", {}).get("dong", [])):
        for dc in row["dan_chung"]:
            them(f"ma_tran/{i}", dc)
    ds = {i: {"nguon_id": nguon_id, "vi_tri": muc, "trich_dan": trich,
              **({"url_tai_lieu": url} if url else {})}
          for (nguon_id, muc, trich, url), i in theo_trich.items()}
    return ds, vi_tri


def _chon_dan_chung(ids, cac_doan):
    if not isinstance(ids, list) or not ids or any(type(i) is not int or i not in cac_doan for i in ids):
        return []
    return [cac_doan[i] for i in dict.fromkeys(ids)]


def _them_can_cu(muc, path, value, dc, ly_do, **phan_loai):
    dan_chung = []
    for d in dc:
        if d not in dan_chung:
            dan_chung.append(d)
    muc.append({"duong_dan": path, "ghi_chu": ly_do, "dan_chung": [
        {**d, "gia_tri": value, **phan_loai} for d in dan_chung
    ]})


def _chon_dong(co_san, khoa, ma_ct, ma_rieng, chi_so):
    if chi_so is not None:
        if type(chi_so) is not int or not 0 <= chi_so < len(co_san):
            return None
        if co_san[chi_so].get(khoa) not in (None, "", ma_ct):
            return None
    khop = [i for i, row in enumerate(co_san) if row.get(khoa) == ma_ct or
            (khoa == "cong_thuc_tinh_diem" and ma_rieng and row.get("ma_phuong_thuc_cua_truong") == ma_rieng
             and row.get(khoa) in (None, "", ma_ct))]
    if len(khop) > 1 or (khop and chi_so is not None and khop[0] != chi_so):
        return None
    if chi_so is not None or khop:
        return chi_so if chi_so is not None else khop[0]
    if any(not row.get(khoa) and (not ma_rieng or row.get("ma_phuong_thuc_cua_truong") in (None, ma_rieng))
           for row in co_san):
        return None
    return len(co_san)


def _tach_dan_chung_to_hop(muc, path, gia_tri_cu):
    """CMS chỉ đọc một trong hai cấp dẫn chứng của mảng mã. Giữ từng mã đã có khi nối thêm tổ hợp."""
    cac_muc = [m for m in muc if m["duong_dan"] == path]
    for item in cac_muc:
        if (item.get("mau_thuan") or item.get("phan_tich_mau_thuan_ai") or
                any(dc.get("gia_tri") != gia_tri_cu for dc in item.get("dan_chung", []))):
            return None
    thay_the = []
    for item in cac_muc:
        for i, ma in enumerate(gia_tri_cu or []):
            thay_the.append({**item, "duong_dan": f"{path}/{i}",
                             "dan_chung": [{**dc, "gia_tri": ma} for dc in item.get("dan_chung", [])]})
    return thay_the


def _ap_dung_lien_ket(hd, dong, cong_thuc, doan, refs_by_parent, muc, nam, danh_muc):
    de_an, quy_tac = hd.get("de_an"), hd.get("quy_tac")
    ma_ct, ma_bo, ma_rieng = hd.get("ma_cong_thuc"), hd.get("ma_phuong_thuc_cua_bo"), hd.get("ma_phuong_thuc_cua_truong")
    loai, ly_do, to_hop = hd.get("phan_loai_ma_bo"), hd.get("ly_do"), hd.get("to_hop")
    if (not isinstance(de_an, str) or not de_an.startswith(_CT + "/") or de_an not in dong
            or not isinstance(quy_tac, str) or not quy_tac.startswith(_QT + "/") or quy_tac not in dong
            or dong[de_an]["ma_xet_tuyen"] != dong[quy_tac]["ma_xet_tuyen"]
            or not isinstance(ma_ct, str) or ma_ct not in cong_thuc
            or (ma_bo is None and loai is not None)
            or (ma_bo is not None and (not danh_muc or not ai._ma_dung_dinh_dang(ma_bo, nam, danh_muc)
                                       or loai not in ("suy_luan", "cong_bo")))
            or not isinstance(ly_do, str) or not ly_do.strip()
            or not isinstance(to_hop, list) or any(not isinstance(t, str) or not t.strip() for t in to_hop)
            or (ma_rieng is not None and (not isinstance(ma_rieng, str) or not 1 <= len(ma_rieng) <= 20))):
        return False
    for khoa in ("ma_nganh", "ma_co_so", "co_so_id", "hinh_thuc_dao_tao", "loai_chuong_trinh"):
        a, b = dong[de_an].get(khoa), dong[quy_tac].get(khoa)
        if a not in (None, "") and b not in (None, "") and a != b:
            return False
    ap_dung = _chon_dan_chung(hd.get("can_cu_ap_dung"), doan)
    phuong_thuc = _chon_dan_chung(hd.get("can_cu_phuong_thuc"), doan)
    id_nhan_dang = hd.get("can_cu_nhan_dang", hd.get("can_cu_ap_dung"))
    nhan_dang = _chon_dan_chung(id_nhan_dang, doan)
    to_hop_dc = _chon_dan_chung(hd.get("can_cu_to_hop", hd.get("can_cu_ap_dung")), doan) if to_hop else []
    if not nhan_dang or not ap_dung or not phuong_thuc or (to_hop and not to_hop_dc):
        return False
    if not (set(id_nhan_dang) & (refs_by_parent[de_an] | refs_by_parent[quy_tac])
            or any(_co_ma(d["trich_dan"], dong[de_an]["ma_xet_tuyen"]) for d in nhan_dang)):
        return False
    ct_path, ct = cong_thuc[ma_ct]
    if (ma_bo and ct.get("ma_phuong_thuc_cua_bo") not in (None, "", ma_bo)) or (ct.get("kieu_tinh") == "TO_HOP_MON" and not to_hop):
        return False
    if ma_rieng and not any(_co_ma(d["trich_dan"], ma_rieng) for d in ap_dung + phuong_thuc):
        return False
    ma_dc = phuong_thuc
    if loai == "cong_bo":
        ma_dc = [d for d in phuong_thuc if _co_ma(d["trich_dan"], ma_bo)]
        if not ma_dc:
            return False
    cach_gan = {"phan_loai_ma_bo": loai}
    if loai == "suy_luan":
        cach_gan["ly_do_suy_luan_ma_bo"] = f"Mã Bộ suy luận ({ma_bo}). {ly_do}"
    danh_sach_pt = dong[de_an].get("dats_phuong_thuc", [])
    danh_sach_pa = dong[quy_tac].get("phuong_an", [])
    if not all(isinstance(ds, list) and all(isinstance(p, dict) for p in ds) for ds in (danh_sach_pt, danh_sach_pa)):
        return False
    i = _chon_dong(danh_sach_pt, "cong_thuc_tinh_diem", ma_ct, ma_rieng, hd.get("chi_so_phuong_thuc"))
    j = _chon_dong(danh_sach_pa, "ma_cong_thuc", ma_ct, ma_rieng, hd.get("chi_so_phuong_an"))
    if i is None or j is None:
        return False
    pt = danh_sach_pt[i] if i < len(danh_sach_pt) else {}
    pa = danh_sach_pa[j] if j < len(danh_sach_pa) else {}
    ma_truong = {v for v in (pt.get("ma_phuong_thuc_cua_truong"), pa.get("ma_phuong_thuc_cua_truong"), ma_rieng)
                 if isinstance(v, str) and v}
    ma_bo_hien_co = {v for v in (ct.get("ma_phuong_thuc_cua_bo"), pt.get("ma_phuong_thuc_cua_bo"), ma_bo)
                     if isinstance(v, str) and v}
    if (len(ma_truong) > 1 or len(ma_bo_hien_co) > 1 or (ma_bo and pt.get("ma_phuong_thuc_cua_bo") not in (None, "", ma_bo))
            or pt.get("cong_thuc_tinh_diem") not in (None, "", ma_ct)
            or not isinstance(pa.get("to_hop", []), list) or not isinstance(pt.get("to_hop_mon_hoc") or [], list)
            or (to_hop and any(pt.get(k) for k in ("to_hop_ids", "to_hop_id", "dats_phuong_thuc_to_hop"))
                and not all(t in (pt.get("to_hop_mon_hoc") or []) for t in to_hop))):
        return False
    pt_path, pa_path = f"{de_an}/dats_phuong_thuc/{i}", f"{quy_tac}/phuong_an/{j}"
    goc_to_hop = {}
    for row, path, key in ((pt, pt_path, "to_hop_mon_hoc"), (pa, pa_path, "to_hop")):
        if any(ma not in (row.get(key) or []) for ma in to_hop):
            path = f"{path}/{key}"
            if (tung_ma := _tach_dan_chung_to_hop(muc, path, row.get(key))) is None:
                return False
            goc_to_hop[path] = tung_ma
    if goc_to_hop:
        muc[:] = [item for item in muc if item["duong_dan"] not in goc_to_hop]
        for ds in goc_to_hop.values():
            muc.extend(ds)
    if i == len(danh_sach_pt):
        dong[de_an].setdefault("dats_phuong_thuc", []).append(pt)
    if j == len(danh_sach_pa):
        dong[quy_tac].setdefault("phuong_an", []).append(pa)
    for row, path, key, value, refs in (
        (ct, ct_path, "ma_phuong_thuc_cua_bo", ma_bo, ma_dc),
        (pt, pt_path, "ma_phuong_thuc_cua_bo", ma_bo, ma_dc),
        (pt, pt_path, "cong_thuc_tinh_diem", ma_ct, nhan_dang + ap_dung + phuong_thuc),
        (pa, pa_path, "ma_cong_thuc", ma_ct, nhan_dang + ap_dung + phuong_thuc),
        (pt, pt_path, "ma_phuong_thuc_cua_truong", ma_rieng, ap_dung + phuong_thuc),
        (pa, pa_path, "ma_phuong_thuc_cua_truong", ma_rieng, ap_dung + phuong_thuc),
    ):
        da_co_bang_chung = any(m["duong_dan"] == f"{path}/{key}" and any(
            d.get("gia_tri") == value and d.get("phan_loai_ma_bo") == loai for d in m.get("dan_chung", [])) for m in muc
        ) if key == "ma_phuong_thuc_cua_bo" and value is not None and row.get(key) == value else False
        if value is not None and (not row.get(key) or (key == "ma_phuong_thuc_cua_bo" and not da_co_bang_chung)):
            row[key] = value
            _them_can_cu(muc, f"{path}/{key}", value, refs, ly_do, **(cach_gan if key == "ma_phuong_thuc_cua_bo" else {}))
        elif key == "ma_phuong_thuc_cua_bo" and ma_bo is None and not row.get(key):
            row[key] = None
            _them_can_cu(muc, f"{path}/{key}", None, [], ly_do)
    for row, path, key in ((pt, pt_path, "to_hop_mon_hoc"), (pa, pa_path, "to_hop")):
        ds = row.get(key) or []
        for ma in to_hop:
            if ma not in ds:
                _them_can_cu(muc, f"{path}/{key}/{len(ds)}", ma, nhan_dang + ap_dung + to_hop_dc, ly_do)
                ds.append(ma)
        if ds or key == "to_hop":
            row[key] = ds
    return True


def _ap_dung_gop(du_lieu, muc, nhom, ghi_chu):
    """Gộp trên bản sao. Giữ dòng nguồn nếu thao tác sẽ mất giá trị chuyên môn đã có."""
    for bang in _DANH_SACH:
        ds = _cac_dong(du_lieu, bang)
        duong_dan = {}
        da_nhap = set()
        da_giu = set()
        dan_chung_mang = {m["duong_dan"] for m in muc if any(isinstance(d.get("gia_tri"), list) for d in m.get("dan_chung", []))}
        for giu, nhap, ly_do in nhom:
            if not giu.startswith(bang + "/") or nhap in da_nhap or giu in da_nhap or nhap in da_giu:
                continue
            i, j = int(giu.split("/")[-1]), int(nhap.split("/")[-1])
            mapping = {}
            moi = ai._gop_du_lieu(deepcopy(ds[i]), deepcopy(ds[j]), giu, nhap, mapping)
            mat_gia_tri = False
            for path, dich in mapping.items():
                tokens = _cac_doan(path)[3:]
                cu, sau = _lay(ds[j], tokens), _lay(moi, _cac_doan(dich)[3:])
                if not tokens or tokens == ["ten_chuong_trinh"] or cu in (None, ""):
                    continue
                if isinstance(cu, (dict, list)) and isinstance(sau, type(cu)):
                    if path in dan_chung_mang and cu != sau:
                        mat_gia_tri = True
                        break
                    continue
                if not ai._giong_nhau(cu, sau):
                    mat_gia_tri = True
                    break
            if mat_gia_tri or any(item["duong_dan"].startswith(nhap + "/") and item["duong_dan"] not in mapping
                                   for item in muc):
                ghi_chu.append(f"Giữ riêng các dòng {ds[i]['ma_xet_tuyen']} vì còn giá trị hoặc dẫn chứng khác nhau.")
                continue
            try:
                mang_da_thay_doi = any(_lay(ds[i], _cac_doan(path)[3:]) != _lay(moi, _cac_doan(path)[3:])
                                       for path in dan_chung_mang.intersection(mapping.values()) if path.startswith(giu + "/"))
            except (KeyError, IndexError, TypeError, ValueError):
                mang_da_thay_doi = True
            if mang_da_thay_doi:
                ghi_chu.append(f"Giữ riêng các dòng {ds[i]['ma_xet_tuyen']} để bảo toàn dẫn chứng cho danh sách đã trích.")
                continue
            ds[i] = moi
            duong_dan.update(mapping)
            da_nhap.add(nhap)
            da_giu.add(giu)
            ghi_chu.append(f"Gộp các dòng {ds[i]['ma_xet_tuyen']} theo dẫn chứng. {ly_do}")
        if not da_nhap:
            continue
        moi = []
        doi_chi_so = {}
        for i, row in enumerate(ds):
            if f"{bang}/{i}" not in da_nhap:
                doi_chi_so[str(i)] = str(len(moi))
                moi.append(row)
        ds[:] = moi
        for item in muc:
            path = item["duong_dan"]
            if path.startswith(bang + "/"):
                path = duong_dan.get(path, path)
                so, sep, tail = path[len(bang) + 1:].partition("/")
                if so in doi_chi_so:
                    item["duong_dan"] = bang + "/" + doi_chi_so[so] + sep + tail


def _can_doi_chieu(rows, cong_thuc):
    if any(sum(path.startswith(bang + "/") for path in rows) != 1 for bang in _DANH_SACH):
        return True
    cac_lien_ket = []
    for path, row in rows.items():
        bang = path.rsplit("/", 1)[0]
        ds = row.get(_DANH_SACH[bang])
        if not isinstance(ds, list) or not ds or any(not isinstance(p, dict) for p in ds):
            return True
        khoa_ct = "ma_cong_thuc" if bang == _QT else "cong_thuc_tinh_diem"
        khoa_th = "to_hop" if bang == _QT else "to_hop_mon_hoc"
        tham_chieu = set()
        for p in ds:
            ma_ct, to_hop = p.get(khoa_ct), p.get(khoa_th) or []
            if not isinstance(ma_ct, str) or ma_ct not in cong_thuc or not cong_thuc[ma_ct][1].get("ma_phuong_thuc_cua_bo"):
                return True
            if (bang == _CT and not p.get("ma_phuong_thuc_cua_bo")) or not isinstance(to_hop, list) or any(
                    not isinstance(t, str) for t in to_hop):
                return True
            tham_chieu.add((ma_ct, tuple(sorted(to_hop))))
        cac_lien_ket.append(tham_chieu)
    return cac_lien_ket[0] != cac_lien_ket[1]


def doi_chieu_lien_ket_ai(truong, nam, ket_qua, nguon, danh_muc_phuong_thuc, bao_tien_do):
    """Đối chiếu các dòng chưa nối hoặc có nhiều cách định danh trong bản nháp tự động."""
    data, muc = ket_qua["du_lieu"], ket_qua["muc"]
    ghi_chu = ket_qua.setdefault("ghi_chu", [])
    theo_ma = defaultdict(dict)
    for bang in _DANH_SACH:
        for i, dong in enumerate(_cac_dong(data, bang)):
            if isinstance(dong, dict) and isinstance(ma := dong.get("ma_xet_tuyen"), str) and ma.strip():
                theo_ma[ma][f"{bang}/{i}"] = dong
    theo_cong_thuc = defaultdict(list)
    for i, ct in enumerate(_cac_dong(data, _CONG_THUC)):
        if isinstance(ct, dict) and isinstance(ma_ct := ct.get("ma_cong_thuc"), str) and ma_ct:
            theo_cong_thuc[ma_ct].append((f"{_CONG_THUC}/{i}", ct))
    cong_thuc = {ma_ct: ds[0] for ma_ct, ds in theo_cong_thuc.items() if len(ds) == 1}
    ma_tran = ket_qua.get("ma_tran_goc", {}).get("dong", [])
    cac_dien = {r["ma_xet_tuyen"] for r in ma_tran if r["dien"]}
    da_noi = set()
    if ma_tran:
        ket_qua["dong_ma_tran_da_noi"] = []
    can_xem = [ma for ma, rows in theo_ma.items() if ma in cac_dien or _can_doi_chieu(rows, cong_thuc)]
    if not can_xem:
        return
    ds_doan, vi_tri = _bang_chung(ket_qua, nam, nguon)
    if not ds_doan:
        return
    dm = {r["ma_phuong_thuc"]: r.get("ten_phuong_thuc") for r in danh_muc_phuong_thuc or []
          if isinstance(r, dict) and isinstance(r.get("ma_phuong_thuc"), str)}
    dm = ai.MA_PHUONG_THUC_BO_THEO_NAM.get(nam) or dm
    meta = {n["id"]: {k: n.get(k) for k in ("url", "tieu_de", "ngay_cong_bo", "pham_vi_dieu_chinh")} for n in nguon}
    gop, lien_ket_de_xuat = [], []
    cac_ma_bo = defaultdict(set)
    refs_by_parent = defaultdict(set)
    for i, paths in vi_tri.items():
        for p in paths:
            if p.startswith((_CONG_THUC + "/", _CT + "/", _QT + "/")):
                refs_by_parent["/".join(p.split("/")[:4])].add(i)
            if p.startswith("ma_tran/"):
                refs_by_parent[p].add(i)
    lo = deque(can_xem[i:i + 8] for i in range(0, len(can_xem), 8))
    while lo:
        cac_ma = lo.popleft()
        rows = {path: r for ma in cac_ma for path, r in theo_ma[ma].items()}
        bang = [{**{k: v for k, v in r.items() if k != "dan_chung"}, "stt": i,
                 "trich_dan_ids": sorted(refs_by_parent[f"ma_tran/{i}"])}
                for i, r in enumerate(ma_tran) if r["ma_xet_tuyen"] in cac_ma and r["dien"]]
        ids_bang = {i for row in bang for i in row["trich_dan_ids"]}
        doan = {i: dc for i, dc in ds_doan.items() if any(
            p.startswith((_CONG_THUC + "/", "/dats_tuyen_sinh/dats_chinh_sach_xet_tuyen_thang/",
                          "/dats_tuyen_sinh/dats_doi_tuong_du_tuyen/", "/quy_tac_xet_tuyen/dieu_kien_chung/",
                          "/quy_tac_xet_tuyen/to_hop_rieng/")) or p.startswith("/dats_tuyen_sinh/") and p.count("/") == 2
            or "/".join(p.split("/")[:4]) in rows for p in vi_tri[i]
        ) or i in ids_bang or any(_co_ma(dc["trich_dan"], ma) for ma in cac_ma)}
        if not doan:
            continue
        bao_tien_do("doi_chieu_lien_ket", can_xem.index(cac_ma[0]), len(can_xem))
        ds_ct = {path: {k: r[k] for k in _THUOC_TINH_CT if k in r} for path, r in rows.items()}
        for path, r in rows.items():
            key = _DANH_SACH[path.rsplit("/", 1)[0]]
            ds = r.get(key)
            ds_ct[path]["trich_dan_ids"] = sorted(refs_by_parent[path])
            ds_ct[path][key] = [{k: v for k, v in p.items() if k in ("ma_phuong_thuc_cua_bo", "ma_phuong_thuc_cua_truong",
                                "ma_cong_thuc", "cong_thuc_tinh_diem", "to_hop", "to_hop_mon_hoc", "ten_phuong_thuc_cua_truong")}
                                for p in ds if isinstance(p, dict)] if isinstance(ds, list) else []
        inputs = {"truong": truong, "nam": nam, "danh_muc_bo": dm, "chuong_trinh": ds_ct, "ma_tran": bang,
                  "cong_thuc": [{**{k: ct.get(k) for k in ("ma_cong_thuc", "ten_cong_thuc", "ma_phuong_thuc_cua_bo",
                                "kieu_tinh", "nguon_diem_mon", "mo_ta_cong_thuc")}, "trich_dan_ids": sorted(refs_by_parent[path])}
                                for path, ct in cong_thuc.values()],
                  "nguon": {dc["nguon_id"]: meta[dc["nguon_id"]] for dc in doan.values()}, "trich_dan": doan}
        try:
            result, _ = ai._openai(_HUONG_DAN, inputs, 6200)
            if not isinstance(result, dict) or not all(isinstance(result.get(k), list) for k in ("gop", "lien_ket", "ghi_chu")):
                raise ai.AdmissionAIError("Sai định dạng đề xuất liên kết chương trình.")
        except ai.AdmissionAIError as exc:
            if isinstance(exc, ai._LoiDungLuongModel) and len(cac_ma) > 1:
                nua = len(cac_ma) // 2
                lo.extendleft([cac_ma[nua:], cac_ma[:nua]])
                continue
            ghi_chu.append(f"Chưa hoàn tất đối chiếu liên kết của {', '.join(cac_ma)}. {exc}")
            continue
        ghi_chu.extend(ai._ghi_chu(result["ghi_chu"]))
        for de_xuat in result["gop"]:
            if not isinstance(de_xuat, dict):
                continue
            giu, nhap, ly_do = (de_xuat.get(k) for k in ("giu", "nhap", "ly_do"))
            if (not isinstance(giu, str) or not isinstance(nhap, str) or giu not in rows or nhap not in rows
                    or giu == nhap or giu.rsplit("/", 1)[0] != nhap.rsplit("/", 1)[0]
                    or not isinstance(ly_do, str) or not ly_do.strip()):
                continue
            ma = rows[giu]["ma_xet_tuyen"]
            if ma != rows[nhap]["ma_xet_tuyen"]:
                ghi_chu.append(f"AI đề nghị đối chiếu hai mã {ma} và {rows[nhap]['ma_xet_tuyen']}. Cần xác nhận mã chính thức. {ly_do}")
                continue
            can_cu = _chon_dan_chung(de_xuat.get("can_cu"), doan)
            ten = rows[giu].get("ten_chuong_trinh")
            if (isinstance(ten, str) and ten.strip() and any(
                    _co_ma(d["trich_dan"], ma) and ai._van_ban(ten).casefold() in ai._van_ban(d["trich_dan"]).casefold()
                    for d in can_cu)):
                nguon_gop = ", ".join(f"#{d['nguon_id']} {d['vi_tri']}" for d in can_cu)
                gop.append((giu, nhap, f"{ly_do} ({nguon_gop})"))
            else:
                ghi_chu.append(f"AI đề nghị gộp hai dòng {ma}, cần đối chiếu tên và phạm vi với danh sách chính thức.")
        for lien_ket in result["lien_ket"]:
            if isinstance(lien_ket, dict):
                ma_ct, ma_bo = lien_ket.get("ma_cong_thuc"), lien_ket.get("ma_phuong_thuc_cua_bo")
                if isinstance(ma_ct, str) and ai._ma_dung_dinh_dang(ma_bo, nam, dm):
                    cac_ma_bo[ma_ct].add(ma_bo)
                lien_ket_de_xuat.append((lien_ket, rows, doan, cac_ma))
    for lien_ket, rows, doan, cac_ma in lien_ket_de_xuat:
        ma_ct = lien_ket.get("ma_cong_thuc")
        if isinstance(ma_ct, str) and len(cac_ma_bo[ma_ct]) > 1:
            ghi_chu.append(f"Mã Bộ của công thức {ma_ct} còn mâu thuẫn giữa các đề xuất ({', '.join(sorted(cac_ma_bo[ma_ct]))}).")
        elif not _ap_dung_lien_ket(lien_ket, rows, cong_thuc, doan, refs_by_parent, muc, nam, dm):
            ghi_chu.append(f"Đề xuất liên kết chưa đủ căn cứ hoặc tham chiếu hợp lệ cho nhóm {', '.join(cac_ma)}.")
        elif isinstance(stt := lien_ket.get("dong_ma_tran"), list):
            ma = rows[lien_ket["de_an"]]["ma_xet_tuyen"]
            ids = {v for k in ("can_cu_nhan_dang", "can_cu_ap_dung", "can_cu_to_hop")
                   for v in (lien_ket.get(k) if isinstance(lien_ket.get(k), list) else []) if type(v) is int}
            for i in stt:
                if type(i) is int and 0 <= i < len(ma_tran):
                    row = ma_tran[i]
                    if (row["ma_xet_tuyen"] == ma and row["dien"] and refs_by_parent[f"ma_tran/{i}"] & ids
                            and set(row["to_hop"] or []).issubset(lien_ket["to_hop"])
                            and (row["to_hop"] != [] or not lien_ket["to_hop"])):
                        da_noi.add(i)
    _ap_dung_gop(data, muc, gop, ghi_chu)
    if ma_tran:
        ket_qua["dong_ma_tran_da_noi"] = sorted(da_noi)
    ghi_chu[:] = list(dict.fromkeys(ghi_chu))
