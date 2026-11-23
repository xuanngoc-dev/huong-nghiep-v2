"""Lưu phần AI tự rà điểm chuẩn và kiểm tra liên kết với nguồn, bản nháp."""


def can_cu_nam_diem(dc: dict, doc) -> dict | None:
    """AI xác định năm áp dụng, chương trình kiểm tra đoạn dẫn ở đúng tài liệu."""
    cc = dc.get("can_cu_nam")
    if not isinstance(cc, dict) or type(cc.get("nam_tuyen_sinh")) is not int:
        return None
    if not doc.doi_chieu(cc.get("vi_tri"), cc.get("trich_dan")):
        return None
    return {k: cc[k] for k in ("nam_tuyen_sinh", "vi_tri", "trich_dan")}


def nhan_ra_soat_diem(cac_phan, tai_lieu, nguon_chua_doc_het, so_muc_truoc):
    """Mỗi phần nguồn phải có phản hồi riêng, kể cả khi AI tìm thấy 0 điểm."""
    da_ra_soat = {}
    can_lam_ro, da_giai_quyet = [], []
    for ids, data in cac_phan:
        bao_cao = data.get("ra_soat_diem_chuan")
        for nguon_id in ids:
            if nguon_id not in tai_lieu:
                continue
            cac_ban = [bc for bc in bao_cao if isinstance(bc, dict) and type(bc.get("nguon_id")) is int
                       and bc["nguon_id"] == nguon_id] if isinstance(bao_cao, list) else []
            bc = cac_ban[0] if len(cac_ban) == 1 else {}
            hop_le = bc.get("da_doc_het") is True
            doc = tai_lieu[nguon_id]
            for nhom in ("can_lam_ro", "da_giai_quyet"):
                danh_sach = bc.get(nhom, [] if nhom == "da_giai_quyet" else None)
                if not isinstance(danh_sach, list):
                    hop_le = False
                    continue
                for item in danh_sach:
                    if not isinstance(item, dict) or not doc.doi_chieu(item.get("vi_tri"), item.get("trich_dan")):
                        hop_le = False
                        continue
                    vi_tri, trich_dan = item["vi_tri"], item["trich_dan"]
                    if nhom == "da_giai_quyet":
                        stt = item.get("stt")
                        if type(stt) is int and 1 <= stt <= so_muc_truoc:
                            if stt not in da_giai_quyet:
                                da_giai_quyet.append(stt)
                        else:
                            hop_le = False
                        continue
                    pham_vi, ly_do = item.get("pham_vi"), item.get("ly_do")
                    if not all(isinstance(s, str) and s.strip() for s in (pham_vi, ly_do)):
                        hop_le = False
                        continue
                    muc = {"nguon_id": nguon_id, "vi_tri": vi_tri, "trich_dan": trich_dan,
                           "pham_vi": pham_vi.strip(), "ly_do": ly_do.strip()}
                    if muc not in can_lam_ro:
                        can_lam_ro.append(muc)
            da_ra_soat[nguon_id] = da_ra_soat.get(nguon_id, True) and hop_le
    return {
        "nguon": [{"nguon_id": i, "da_ra_soat": da_ra_soat.get(i, False) and i not in nguon_chua_doc_het}
                  for i in tai_lieu],
        "can_lam_ro": can_lam_ro, "da_giai_quyet": da_giai_quyet,
    }


def gop_ra_soat_diem(cu, moi):
    """Chỉ bỏ câu hỏi trước khi AI dẫn nguồn cho lời giải ở lượt bổ sung."""
    cu, moi = cu or {}, moi or {}
    da_giai_quyet = set(moi.get("da_giai_quyet", []))
    cho = [q for i, q in enumerate(cu.get("can_lam_ro", []), 1) if i not in da_giai_quyet]
    cho.extend(q for q in moi.get("can_lam_ro", []) if q not in cho)
    nguon = {n["nguon_id"]: n for n in [*cu.get("nguon", []), *moi.get("nguon", [])]}
    return {"nguon": list(nguon.values()), "can_lam_ro": cho}


def bao_cao_diem_ai(ra_soat, du_lieu, muc):
    """Đếm các dòng do AI trả và các dẫn chứng đang được người duyệt chọn."""
    can_tim = [f"{q['pham_vi']} (nguồn #{q['nguon_id']}, {q['vi_tri']}). {q['ly_do']}" for q in ra_soat["can_lam_ro"]]
    so_dong = so_khop = 0
    theo_path = {m["duong_dan"]: m for m in muc}
    for i, dong in enumerate(du_lieu["quy_tac_xet_tuyen"].get("diem_chuan") or []):
        if not isinstance(dong, dict):
            continue
        so_dong += 1
        item = theo_path.get(f"/quy_tac_xet_tuyen/diem_chuan/{i}/diem_chuan", {})
        da_chon = set(item.get("dan_chung_ids") or [])
        if dong.get("diem_chuan") is not None and (not item.get("mau_thuan") or item.get("da_kiem_tra")) and any(
            dc.get("gia_tri") == dong["diem_chuan"] and dc.get("id") in da_chon for dc in item.get("dan_chung", [])
        ):
            so_khop += 1
        else:
            can_tim.append(f"Điểm chuẩn dòng {i + 1} ({dong.get('ma_xet_tuyen') or 'chưa có mã'}): cần đối chiếu dẫn chứng.")
    nguon = ra_soat["nguon"]
    for n in nguon:
        if not n["da_ra_soat"]:
            can_tim.append(f"Nguồn #{n['nguon_id']}: AI chưa hoàn tất rà soát điểm chuẩn của toàn bộ phần tài liệu đã đọc.")
    return {"mode_ai": True, "da_ra_soat": bool(nguon) and all(n["da_ra_soat"] for n in nguon),
            "so_o_nhan_dien": so_dong, "so_o_da_khop": so_khop,
            "so_vi_tri_chua_ro": len(ra_soat["can_lam_ro"]), "can_doi_chieu": can_tim}
