from copy import deepcopy
from unittest.mock import Mock, patch

import pytest

from app.services import dats_lien_ket_chuong_trinh as lk
from app.services.dats_ban_nhap_thu_thap import lap_muc_ban_nhap


DE_AN = "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao"
QUY_TAC = "/quy_tac_xet_tuyen/chuong_trinh"
CONG_THUC = "/quy_tac_xet_tuyen/cong_thuc/0"
NGUON = [{"id": i, "url": f"https://example.edu.vn/{i}", "nam_ap_dung": 2026, "chinh_thuc": True,
          "phu_hop": True, "lua_chon": "su_dung"} for i in (1, 2)]


def muc(path, gia_tri, nguon_id, vi_tri, trich_dan):
    return {"duong_dan": path, "dan_chung": [{"gia_tri": gia_tri, "nguon_id": nguon_id,
            "vi_tri": vi_tri, "trich_dan": trich_dan, "url_tai_lieu": f"https://example.edu.vn/chi-tiet/{nguon_id}"}]}


def ban_nhap():
    return {
        "du_lieu": {
            "thong_tin_import": {},
            "dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [
                {"ma_xet_tuyen": "N1", "ten_chuong_trinh": "Ngôn ngữ học", "dats_phuong_thuc": []}]},
            "quy_tac_xet_tuyen": {
                "cong_thuc": [{"ma_cong_thuc": "F01", "ten_cong_thuc": "Tổng điểm ba môn", "kieu_tinh": "TO_HOP_MON",
                               "nguon_diem_mon": "THI_THPT", "thang_diem": 30}],
                "chuong_trinh": [{"ma_xet_tuyen": "N1", "ten_chuong_trinh": "Ngôn ngữ học", "phuong_an": []}],
            },
        },
        "muc": [
            muc(f"{DE_AN}/0/ma_xet_tuyen", "N1", 1, "Bảng ngành", "N1 | Ngôn ngữ học | thi tốt nghiệp | A00, D01"),
            muc(f"{CONG_THUC}/nguon_diem_mon", "THI_THPT", 2, "Căn cứ xếp hạng", "Diện thi tốt nghiệp dùng tổng điểm ba môn thi THPT."),
        ],
        "doi_chieu_chuong_trinh": [],
        "ghi_chu": [],
    }


def lien_ket(**them):
    return {"de_an": f"{DE_AN}/0", "quy_tac": f"{QUY_TAC}/0", "ma_cong_thuc": "F01",
            "ma_phuong_thuc_cua_bo": "100", "phan_loai_ma_bo": "suy_luan", "ma_phuong_thuc_cua_truong": None,
            "to_hop": ["A00", "D01"], "can_cu_ap_dung": [1], "can_cu_phuong_thuc": [2],
            "ly_do": "Bảng ngành áp dụng diện xếp hạng bằng tổng ba điểm thi tốt nghiệp.", **them}


def test_ma_tran_chi_tinh_lien_ket_khop_chuong_trinh_to_hop_va_dan_chung():
    nhap = ban_nhap()
    dc = nhap["muc"][0]["dan_chung"][0]
    row = {"ma_xet_tuyen": "N1", "ten_chuong_trinh": "Ngôn ngữ học", "dien": "Thi tốt nghiệp",
           "chi_tieu": None, "pham_vi": None, "to_hop": ["A00", "D01"], "dan_chung": [dc]}
    nhap["ma_tran_goc"] = {"dong": [row, {**row, "to_hop": ["K01"]}]}
    chay(nhap, [lien_ket(dong_ma_tran=[0, 1, 9])])
    assert nhap["dong_ma_tran_da_noi"] == [0]


def chay(nhap, lien_ket=(), gop=(), nguon=NGUON):
    kq = {"gop": list(gop), "lien_ket": list(lien_ket), "ghi_chu": []}
    with patch.object(lk.ai, "_openai", return_value=(kq, [])) as model:
        lk.doi_chieu_lien_ket_ai({"ten_truong": "Trường Mẫu"}, 2026, nhap, nguon, None, Mock())
    return model


def test_noi_hai_nguon_suy_luan_ma_bo_va_bao_toan_dan_chung_cho_nguoi_duyet():
    nhap = ban_nhap()
    model = chay(nhap, [lien_ket()])
    du_lieu = nhap["du_lieu"]
    (pt,) = du_lieu["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][0]["dats_phuong_thuc"]
    (pa,) = du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"]
    assert pt == {"ma_phuong_thuc_cua_bo": "100", "cong_thuc_tinh_diem": "F01", "to_hop_mon_hoc": ["A00", "D01"]}
    assert pa == {"ma_cong_thuc": "F01", "to_hop": ["A00", "D01"]}
    assert du_lieu["quy_tac_xet_tuyen"]["cong_thuc"][0]["ma_phuong_thuc_cua_bo"] == "100"
    assert model.call_args.args[1]["cong_thuc"][0]["trich_dan_ids"] == [2]
    reviewed = {m["duong_dan"]: m for m in lap_muc_ban_nhap(du_lieu, nhap["muc"], NGUON, 2026)}
    ma_bo = reviewed[f"{DE_AN}/0/dats_phuong_thuc/0/ma_phuong_thuc_cua_bo"]
    assert ma_bo["dan_chung"][0]["phan_loai_ma_bo"] == "suy_luan"
    assert ma_bo["dan_chung"][0]["url_tai_lieu"].endswith("/2")
    assert "Mã Bộ suy luận (100)" in ma_bo["ghi_chu"] and ma_bo["dan_chung_ids"] == []
    assert {d["nguon_id"] for d in reviewed[f"{QUY_TAC}/0/phuong_an/0/ma_cong_thuc"]["dan_chung"]} == {1, 2}
    chay(nhap, [lien_ket()]).assert_not_called()


@pytest.mark.parametrize("thay_doi", [
    {"phan_loai_ma_bo": "cong_bo"},
    {"ma_phuong_thuc_cua_bo": "PT100"},
    {"ma_phuong_thuc_cua_bo": "408"},
    {"ma_cong_thuc": "F02"},
    {"can_cu_ap_dung": [2]},
    {"can_cu_phuong_thuc": [3]},
    {"can_cu_to_hop": []},
    {"ma_phuong_thuc_cua_truong": "THPT-3"},
    {"chi_so_phuong_an": -1},
])
def test_bo_de_xuat_sai_nhung_khong_pha_nhap(thay_doi):
    nhap = ban_nhap()
    cu = deepcopy(nhap["du_lieu"])
    chay(nhap, [lien_ket(**thay_doi)])
    assert nhap["du_lieu"] == cu and len(nhap["muc"]) == 2 and nhap["ghi_chu"]


def test_nguon_cong_bo_ma_bo_hoac_chua_xac_dinh():
    nhap = ban_nhap()
    nhap["muc"][1]["dan_chung"][0]["trich_dan"] += " Mã phương thức Bộ GDĐT 100."
    chay(nhap, [lien_ket(phan_loai_ma_bo="cong_bo")])
    reviewed = {m["duong_dan"]: m for m in lap_muc_ban_nhap(nhap["du_lieu"], nhap["muc"], NGUON, 2026)}
    ma = reviewed[f"{CONG_THUC}/ma_phuong_thuc_cua_bo"]
    assert ma["dan_chung"][0]["phan_loai_ma_bo"] == "cong_bo" and ma["dan_chung_ids"] == ["1"]

    nhap = ban_nhap()
    chay(nhap, [lien_ket(ma_phuong_thuc_cua_bo=None, phan_loai_ma_bo=None, ly_do="Chưa rõ tiêu chí cuối cùng; xem 100 và 407.")])
    (pt,) = nhap["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][0]["dats_phuong_thuc"]
    assert pt["ma_phuong_thuc_cua_bo"] is None and pt["cong_thuc_tinh_diem"] == "F01"
    assert any(m["duong_dan"].endswith("/ma_phuong_thuc_cua_bo") and "407" in m["ghi_chu"] for m in nhap["muc"])


def test_dong_chua_co_ma_cong_thuc_duoc_ai_chi_ro_va_bo_sung_tai_cho():
    nhap = ban_nhap()
    ds = nhap["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][0]["dats_phuong_thuc"]
    ds.append({"ten_phuong_thuc_cua_truong": "Tổng ba môn", "chi_tieu_phuong_thuc": 12})
    chay(nhap, [lien_ket()])
    assert len(ds) == 1 and "cong_thuc_tinh_diem" not in ds[0]
    chay(nhap, [lien_ket(chi_so_phuong_thuc=0)])
    assert len(ds) == 1 and ds[0]["cong_thuc_tinh_diem"] == "F01" and ds[0]["chi_tieu_phuong_thuc"] == 12


def test_quy_dinh_chung_khac_trang_co_the_noi_bang_danh_sach_nganh_va_ten_mon():
    nhap = ban_nhap()
    nhap["muc"][0]["dan_chung"][0]["trich_dan"] = "N1 | Ngôn ngữ học | Khoa Ngôn ngữ"
    nhap["muc"].append(muc("/dats_tuyen_sinh/ghi_chu", "Thể lệ", 2, "Phạm vi",
                             "Mọi ngành của Khoa Ngôn ngữ xét thi tốt nghiệp với Toán, Văn, Anh."))
    chay(nhap, [lien_ket(can_cu_nhan_dang=[1], can_cu_ap_dung=[3], can_cu_to_hop=[3], to_hop=["D01"])])
    pa = nhap["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"]
    assert pa == [{"ma_cong_thuc": "F01", "to_hop": ["D01"]}]
    to_hop = next(m for m in nhap["muc"] if m["duong_dan"] == f"{QUY_TAC}/0/phuong_an/0/to_hop/0")
    assert [dc["vi_tri"] for dc in to_hop["dan_chung"]] == ["Bảng ngành", "Phạm vi"]


def test_bo_sung_to_hop_vao_mang_cu_giu_dan_chung_theo_tung_ma():
    nhap = ban_nhap()
    nhap["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"] = [{"ma_cong_thuc": "F01", "to_hop": ["A00"]}]
    path = f"{QUY_TAC}/0/phuong_an/0/to_hop"
    nhap["muc"].append(muc(path, ["A00"], 1, "Bảng cũ", "N1 nhận A00"))
    chay(nhap, [lien_ket()])
    reviewed = {m["duong_dan"]: m for m in lap_muc_ban_nhap(nhap["du_lieu"], nhap["muc"], NGUON, 2026)}
    assert reviewed[path + "/0"]["dan_chung"][0]["vi_tri"] == "Bảng cũ"
    assert reviewed[path + "/1"]["dan_chung"][0]["vi_tri"] == "Bảng ngành"


def test_chung_ma_khac_co_so_khong_noi_nham_hai_bang():
    nhap = ban_nhap()
    nhap["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][0]["ma_co_so"] = "CS1"
    nhap["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"][0]["ma_co_so"] = "CS2"
    cu = deepcopy(nhap["du_lieu"])
    chay(nhap, [lien_ket()])
    assert nhap["du_lieu"] == cu and nhap["ghi_chu"]


def test_nguon_sai_nam_va_dong_diem_hoi_cuu_khong_dung_de_gan_ma():
    nhap = ban_nhap()
    nhap["muc"].append(muc("/quy_tac_xet_tuyen/diem_chuan/0/diem_chuan", 23, 1, "Điểm 2024", "N1 từng nhận A00, D01."))
    model = chay(nhap, [lien_ket()], nguon=[NGUON[0], {**NGUON[1], "chi_diem_lich_su": True}])
    assert list(model.call_args.args[1]["trich_dan"]) == [1]
    assert nhap["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"] == []


def test_gop_dong_cung_ma_doi_dung_duong_dan_cua_dong_gop_va_dong_ke_tiep():
    nhap = ban_nhap()
    rows = nhap["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]
    rows.extend([{"ma_xet_tuyen": "N1", "ten_chuong_trinh": "Ngôn ngữ", "chi_tieu_tuyen_sinh": 15,
                  "dats_phuong_thuc": [{"cong_thuc_tinh_diem": "F01", "chi_tieu_phuong_thuc": 10}]},
                 {"ma_xet_tuyen": "N2", "ten_chuong_trinh": "Sư phạm"}])
    nhap["muc"].extend([
        muc(f"{DE_AN}/1/dats_phuong_thuc/0/chi_tieu_phuong_thuc", 10, 2, "Thể lệ", "N1 có 10 chỉ tiêu phương thức."),
        muc(f"{DE_AN}/2/ma_xet_tuyen", "N2", 1, "Bảng", "N2 | Sư phạm"),
    ])
    gop = {"giu": f"{DE_AN}/0", "nhap": f"{DE_AN}/1", "can_cu": [1], "ly_do": "Trường viết tắt cùng ngành ở bảng phụ."}
    chay(nhap, gop=[gop])
    assert [row["ma_xet_tuyen"] for row in rows] == ["N1", "N2"]
    assert rows[0]["ten_chuong_trinh"] == "Ngôn ngữ học" and rows[0]["chi_tieu_tuyen_sinh"] == 15
    assert rows[0]["dats_phuong_thuc"][0]["chi_tieu_phuong_thuc"] == 10
    assert [m["duong_dan"] for m in nhap["muc"][-2:]] == [
        f"{DE_AN}/0/dats_phuong_thuc/0/chi_tieu_phuong_thuc", f"{DE_AN}/1/ma_xet_tuyen"]
    assert "#1 Bảng ngành" in nhap["ghi_chu"][0]


def test_khong_gop_mat_id_co_so_hoac_du_lieu_con():
    nhap = ban_nhap()
    rows = nhap["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]
    rows[0]["dats_phuong_thuc"].append({"cong_thuc_tinh_diem": "F01", "id": 10, "chi_tieu_phuong_thuc": 25})
    rows.append({**deepcopy(rows[0]), "ten_chuong_trinh": "Ngôn ngữ"})
    rows[1]["dats_phuong_thuc"][0]["id"] = 11
    truoc = deepcopy(rows)
    chay(nhap, gop=[{"giu": f"{DE_AN}/0", "nhap": f"{DE_AN}/1", "can_cu": [1], "ly_do": "Tên rút gọn."}])
    assert rows == truoc and nhap["ghi_chu"]


def test_bi_danh_khac_ma_chi_ghi_nhan_de_nguoi_duyet():
    nhap = ban_nhap()
    ds = nhap["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]
    ds.append({**deepcopy(ds[0]), "ma_xet_tuyen": "N-1"})
    chay(nhap, gop=[{"giu": f"{DE_AN}/0", "nhap": f"{DE_AN}/1", "ly_do": "Có thể trường ghi hai cách.", "can_cu": [1]}])
    assert [r["ma_xet_tuyen"] for r in ds] == ["N1", "N-1"]
    assert "N1 và N-1" in nhap["ghi_chu"][0]


def test_loi_ai_va_ma_bo_mau_thuan_de_lai_ban_nhap():
    nhap = ban_nhap()
    cu = deepcopy(nhap["du_lieu"])
    chay(nhap, [lien_ket(), lien_ket(ma_phuong_thuc_cua_bo="407")])
    assert nhap["du_lieu"] == cu and "mâu thuẫn" in nhap["ghi_chu"][0]
    with patch.object(lk.ai, "_openai", side_effect=lk.ai.AdmissionAIError("Lỗi kết nối")):
        lk.doi_chieu_lien_ket_ai({}, 2026, nhap, NGUON, None, Mock())
    assert nhap["du_lieu"] == cu and "Lỗi kết nối" in nhap["ghi_chu"][-1]
