"""Hồ sơ xét tuyển hs_* (bước 4.3 KE_HOACH_TRIEN_KHAI.md): đọc, ghi, và ghi song song với JSON cũ.

Trong thời gian chuyển đổi, hồ sơ năng lực tồn tại ở hai nơi:
- bảng hs_* (đầy đủ: hạn chứng chỉ, môn đạt giải, mức giải, nguyện vọng...), dùng cho bộ tính xét tuyển;
- JSON `nguoi_dung_thong_tin.trinh_do_hoc_van` cùng khu vực / đối tượng / tỉnh, còn dùng cho chat và màn hình cũ.
Lưu ở nơi nào cũng cập nhật nơi kia để hai nơi khớp nhau:
- `luu_ho_so` (API mới) ghi hs_* rồi ghi lại phần tương ứng của JSON;
- `dong_bo_tu_json` (sau khi lưu hồ sơ năng lực cũ) cập nhật hs_* từ JSON, giữ các thông tin chỉ hs_* mới có
  (hạn chứng chỉ, môn đạt giải, nguyện vọng, ngân sách...).
"""

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_bang_cap_chung_chi import DmBangCapChungChi
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_thanh_tich_hoc_tap_nghien_cuu import DmThanhTichHocTapNghienCuu
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.hs_ho_so import (
    HsChungChi,
    HsDiemBaiThi,
    HsDiemMon,
    HsHoSo,
    HsKetQuaNamHoc,
    HsThanhTich,
    HsTieuChiMongMuon,
)
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin
from app.schemas.hs_ho_so import (
    ChungChiWrite,
    DiemBaiThiWrite,
    DiemMonWrite,
    HoSoXetTuyenPublic,
    HoSoXetTuyenWrite,
    KetQuaNamHocWrite,
    MongMuonWrite,
    ThanhTichWrite,
)
from app.services.xet_tuyen.chuyen_ho_so import DanhMucHoSo, tu_ho_so_thanh_vien

HANH_KIEM_THEO_REN_LUYEN = {4: "Tốt", 3: "Khá", 2: "Trung bình", 1: "Yếu"}
NHAN_GIAI = {1: "Giải Nhất", 2: "Giải Nhì", 3: "Giải Ba", 4: "Giải Khuyến khích", 9: "Tham gia"}
_CON = (HsKetQuaNamHoc, HsDiemMon, HsDiemBaiThi, HsChungChi, HsThanhTich, HsTieuChiMongMuon)


class HoSoXetTuyenError(ValueError):
    """Hồ sơ tham chiếu mã không có trong danh mục; thông điệp dành cho người dùng."""


@dataclass
class DanhMucMa:
    """Mã ↔ id các danh mục mà hồ sơ tham chiếu."""

    mon: dict[str, int] = field(default_factory=dict)
    bai_thi: dict[str, int] = field(default_factory=dict)
    chung_chi: dict[str, int] = field(default_factory=dict)
    thanh_tich: dict[str, int] = field(default_factory=dict)
    tinh: dict[str, int] = field(default_factory=dict)
    khu_vuc: dict[str, int] = field(default_factory=dict)
    doi_tuong: dict[str, int] = field(default_factory=dict)

    @classmethod
    def tu_csdl(cls, db: Session) -> "DanhMucMa":
        return cls(
            mon=dict(db.execute(select(DmMonHoc.ma_mon_hoc, DmMonHoc.id)).all()),
            bai_thi=dict(db.execute(select(DmBaiThiDanhGia.ma_bai_thi, DmBaiThiDanhGia.id)).all()),
            chung_chi=dict(db.execute(select(DmBangCapChungChi.ma_chung_chi, DmBangCapChungChi.id)).all()),
            thanh_tich=dict(
                db.execute(select(DmThanhTichHocTapNghienCuu.ma_thanh_tich, DmThanhTichHocTapNghienCuu.id)).all()
            ),
            tinh=dict(db.execute(select(DmTinhThanh.ma_tinh, DmTinhThanh.id)).all()),
            khu_vuc=dict(db.execute(select(DmKhuVucUuTien.ma_khu_vuc, DmKhuVucUuTien.id)).all()),
            doi_tuong=dict(db.execute(select(DmDoiTuongUuTien.ma_doi_tuong, DmDoiTuongUuTien.id)).all()),
        )

    def nguoc(self, loai: str) -> dict[int, str]:
        return {v: k for k, v in getattr(self, loai).items()}


def ho_so_chinh(db: Session, nguoi_dung_id: int) -> HsHoSo | None:
    return db.scalar(
        select(HsHoSo)
        .where(HsHoSo.nguoi_dung_id == nguoi_dung_id)
        .order_by(HsHoSo.la_ho_so_chinh.desc(), HsHoSo.cap_nhat_luc.desc(), HsHoSo.id.desc())
    )


def _f(value) -> float | None:
    return None if value is None else float(value)


def doc_ho_so(db: Session, hs: HsHoSo, dm: DanhMucMa) -> HoSoXetTuyenPublic:
    mon, bai_thi, chung_chi = dm.nguoc("mon"), dm.nguoc("bai_thi"), dm.nguoc("chung_chi")
    thanh_tich, tinh = dm.nguoc("thanh_tich"), dm.nguoc("tinh")

    def con(model):
        return list(db.scalars(select(model).where(model.ho_so_id == hs.id).order_by(model.id)))

    return HoSoXetTuyenPublic(
        id=hs.id,
        la_ho_so_chinh=bool(hs.la_ho_so_chinh),
        cap_nhat_luc=hs.cap_nhat_luc,
        ten_ho_so=hs.ten_ho_so,
        nam_tot_nghiep=hs.nam_tot_nghiep,
        da_tot_nghiep=bool(hs.da_tot_nghiep),
        chuong_trinh_thpt=hs.chuong_trinh_thpt,
        he_chuyen=bool(hs.he_chuyen),
        ma_mon_chuyen=mon.get(hs.mon_chuyen_id),
        ten_truong_thpt=hs.ten_truong_thpt,
        ma_tinh=tinh.get(hs.tinh_thanh_id),
        ma_khu_vuc_uu_tien=dm.nguoc("khu_vuc").get(hs.khu_vuc_uu_tien_id),
        ma_doi_tuong_uu_tien=dm.nguoc("doi_tuong").get(hs.doi_tuong_uu_tien_id),
        ngan_sach_hoc_phi_nam=_f(hs.ngan_sach_hoc_phi_nam),
        ket_qua_nam_hoc=[
            KetQuaNamHocWrite(lop=k.lop, diem_tb_chung=_f(k.diem_tb_chung), hoc_luc=k.hoc_luc, ren_luyen=k.ren_luyen)
            for k in sorted(con(HsKetQuaNamHoc), key=lambda k: k.lop)
        ],
        diem_mon=[
            DiemMonWrite(
                ma_mon=mon[d.mon_hoc_id],
                nguon_diem=d.nguon_diem,
                lop=d.lop,
                hoc_ky=d.hoc_ky,
                diem=float(d.diem),
                nam=d.nam,
                la_du_kien=bool(d.la_du_kien),
            )
            for d in con(HsDiemMon)
        ],
        diem_bai_thi=[
            DiemBaiThiWrite(
                ma_bai_thi=bai_thi[b.bai_thi_id],
                nam_thi=b.nam_thi,
                dot_thi=b.dot_thi,
                ngay_thi=b.ngay_thi,
                diem=float(b.diem),
                phan_tu_chon=b.phan_tu_chon,
            )
            for b in con(HsDiemBaiThi)
        ],
        chung_chi=[
            ChungChiWrite(
                ma_chung_chi=chung_chi[c.chung_chi_id],
                diem=_f(c.diem),
                cap_do=c.cap_do,
                ngay_cap=c.ngay_cap,
                ngay_het_han=c.ngay_het_han,
            )
            for c in con(HsChungChi)
        ],
        thanh_tich=[
            ThanhTichWrite(
                ma_thanh_tich=thanh_tich[t.thanh_tich_id],
                ma_mon=mon.get(t.mon_hoc_id),
                linh_vuc=t.linh_vuc,
                muc_giai=t.muc_giai,
                nam_dat_giai=t.nam_dat_giai,
                lop=t.lop,
            )
            for t in con(HsThanhTich)
        ],
        mong_muon=[MongMuonWrite(loai=m.loai, gia_tri=m.gia_tri) for m in con(HsTieuChiMongMuon)],
    )


def _kiem_ma(payload: HoSoXetTuyenWrite, dm: DanhMucMa) -> None:
    thieu: list[str] = []

    def co(loai: str, ma: str | None, ten: str) -> None:
        if ma is not None and ma not in getattr(dm, loai):
            thieu.append(f'{ten} "{ma}"')

    co("mon", payload.ma_mon_chuyen, "môn chuyên")
    co("tinh", payload.ma_tinh, "tỉnh/thành")
    co("khu_vuc", payload.ma_khu_vuc_uu_tien, "khu vực ưu tiên")
    co("doi_tuong", payload.ma_doi_tuong_uu_tien, "đối tượng ưu tiên")
    for d in payload.diem_mon:
        co("mon", d.ma_mon, "môn")
    for b in payload.diem_bai_thi:
        co("bai_thi", b.ma_bai_thi, "bài thi")
    for c in payload.chung_chi:
        co("chung_chi", c.ma_chung_chi, "chứng chỉ")
    for t in payload.thanh_tich:
        co("thanh_tich", t.ma_thanh_tich, "thành tích")
        co("mon", t.ma_mon, "môn đạt giải")
    if thieu:
        raise HoSoXetTuyenError("Không có trong danh mục: " + ", ".join(dict.fromkeys(thieu)))


def ghi_ho_so(db: Session, hs: HsHoSo, payload: HoSoXetTuyenWrite, dm: DanhMucMa) -> None:
    """Ghi đè toàn bộ hồ sơ hs (bản ghi chính và các bảng con). Không commit."""
    _kiem_ma(payload, dm)
    hs.ten_ho_so = payload.ten_ho_so
    hs.nam_tot_nghiep = payload.nam_tot_nghiep
    hs.da_tot_nghiep = payload.da_tot_nghiep
    hs.chuong_trinh_thpt = payload.chuong_trinh_thpt
    hs.he_chuyen = payload.he_chuyen
    hs.mon_chuyen_id = dm.mon.get(payload.ma_mon_chuyen) if payload.ma_mon_chuyen else None
    hs.ten_truong_thpt = payload.ten_truong_thpt
    hs.tinh_thanh_id = dm.tinh.get(payload.ma_tinh) if payload.ma_tinh else None
    hs.khu_vuc_uu_tien_id = dm.khu_vuc.get(payload.ma_khu_vuc_uu_tien) if payload.ma_khu_vuc_uu_tien else None
    hs.doi_tuong_uu_tien_id = dm.doi_tuong.get(payload.ma_doi_tuong_uu_tien) if payload.ma_doi_tuong_uu_tien else None
    hs.ngan_sach_hoc_phi_nam = payload.ngan_sach_hoc_phi_nam
    hs.cap_nhat_luc = datetime.now()
    db.flush()
    for model in _CON:
        db.execute(delete(model).where(model.ho_so_id == hs.id).execution_options(synchronize_session=False))
    db.add_all(
        HsKetQuaNamHoc(
            ho_so_id=hs.id, lop=k.lop, diem_tb_chung=k.diem_tb_chung, hoc_luc=k.hoc_luc, ren_luyen=k.ren_luyen
        )
        for k in payload.ket_qua_nam_hoc
    )
    db.add_all(
        HsDiemMon(
            ho_so_id=hs.id,
            mon_hoc_id=dm.mon[d.ma_mon],
            nguon_diem=d.nguon_diem,
            lop=d.lop,
            hoc_ky=d.hoc_ky,
            diem=d.diem,
            nam=d.nam,
            la_du_kien=d.la_du_kien,
        )
        for d in payload.diem_mon
    )
    db.add_all(
        HsDiemBaiThi(
            ho_so_id=hs.id,
            bai_thi_id=dm.bai_thi[b.ma_bai_thi],
            nam_thi=b.nam_thi,
            dot_thi=b.dot_thi,
            ngay_thi=b.ngay_thi,
            diem=b.diem,
            phan_tu_chon=b.phan_tu_chon,
        )
        for b in payload.diem_bai_thi
    )
    db.add_all(
        HsChungChi(
            ho_so_id=hs.id,
            chung_chi_id=dm.chung_chi[c.ma_chung_chi],
            diem=c.diem,
            cap_do=c.cap_do,
            ngay_cap=c.ngay_cap,
            ngay_het_han=c.ngay_het_han,
        )
        for c in payload.chung_chi
    )
    db.add_all(
        HsThanhTich(
            ho_so_id=hs.id,
            thanh_tich_id=dm.thanh_tich[t.ma_thanh_tich],
            mon_hoc_id=dm.mon.get(t.ma_mon) if t.ma_mon else None,
            linh_vuc=t.linh_vuc,
            muc_giai=t.muc_giai,
            nam_dat_giai=t.nam_dat_giai,
            lop=t.lop,
        )
        for t in payload.thanh_tich
    )
    db.add_all(HsTieuChiMongMuon(ho_so_id=hs.id, loai=m.loai, gia_tri=m.gia_tri) for m in payload.mong_muon)
    db.flush()


def sang_trinh_do_hoc_van(
    payload: HoSoXetTuyenWrite, json_cu: dict | None, ma_mon_hop_le: set[str] | None = None
) -> dict | None:
    """Phần hồ sơ năng lực cũ (JSON) tương ứng với hồ sơ hs_*; giữ nguyên các khối JSON khác (sức khỏe...).

    Điểm của môn ngoài danh mục (CN, GDDP...) không lưu được ở hs_* nên giữ nguyên từ JSON cũ.
    """
    cu = json_cu or {}
    ket_qua = {k: v for k, v in cu.items() if k == "suc_khoe_the_chat"}

    def ngoai_danh_muc(diem: dict | None) -> dict:
        if ma_mon_hop_le is None:
            return {}
        return {ma: v for ma, v in (diem or {}).items() if ma not in ma_mon_hop_le}

    thpt = ngoai_danh_muc((cu.get("diem_thi_thpt_quoc_gia") or {}).get("du_kien"))
    thpt.update({d.ma_mon: d.diem for d in payload.diem_mon if d.nguon_diem == "THI_THPT"})
    if thpt:
        ket_qua["diem_thi_thpt_quoc_gia"] = {"du_kien": thpt}
    hoc_ba: dict[str, dict[str, float]] = {}
    for lop, theo_mon in (cu.get("diem_trung_binh_hoc_ba") or {}).items():
        if isinstance(theo_mon, dict) and (giu := ngoai_danh_muc(theo_mon)):
            hoc_ba[str(lop)] = giu
    for d in payload.diem_mon:
        if d.nguon_diem == "HOC_BA" and d.hoc_ky == 0:
            hoc_ba.setdefault(str(d.lop), {})[d.ma_mon] = d.diem
    if hoc_ba:
        ket_qua["diem_trung_binh_hoc_ba"] = hoc_ba
    tb = {str(k.lop): k.diem_tb_chung for k in payload.ket_qua_nam_hoc if k.diem_tb_chung is not None}
    if tb:
        ket_qua["hoc_luc_trung_binh"] = tb
    hanh_kiem = {str(k.lop): HANH_KIEM_THEO_REN_LUYEN[k.ren_luyen] for k in payload.ket_qua_nam_hoc if k.ren_luyen}
    if hanh_kiem:
        ket_qua["hanh_kiem"] = hanh_kiem
    if payload.chung_chi:
        ket_qua["chung_chi_ngoai_ngu"] = [
            {
                "ma": c.ma_chung_chi,
                "thanh_tich": f"{c.diem:g}" if c.diem is not None else c.cap_do,
                "thoi_gian_cap": c.ngay_cap.isoformat() if c.ngay_cap else None,
            }
            for c in payload.chung_chi
        ]
    if payload.diem_bai_thi:
        ket_qua["bai_thi_danh_gia_nang_luc"] = [
            {
                "ma": b.ma_bai_thi,
                "thanh_tich": f"{b.diem:g}",
                "thoi_gian_cap": b.ngay_thi.isoformat() if b.ngay_thi else None,
            }
            for b in payload.diem_bai_thi
        ]
    if payload.thanh_tich:
        ket_qua["thanh_tich_hoc_tap_nghien_cuu"] = [
            {"ma": t.ma_thanh_tich, "thanh_tich": NHAN_GIAI[t.muc_giai]} for t in payload.thanh_tich
        ]
    return ket_qua or None


def tu_trinh_do_hoc_van(
    profile: NguoiDungThongTin | None, *, nam_tuyen_sinh: int, danh_muc: DanhMucHoSo
) -> HoSoXetTuyenWrite:
    """Hồ sơ hs_* dựng từ hồ sơ năng lực cũ, theo các quy tắc chuyển đã chốt (bước 3.3 / 4.1)."""
    kq = tu_ho_so_thanh_vien(
        profile.trinh_do_hoc_van if profile else None,
        nam_tuyen_sinh=nam_tuyen_sinh,
        danh_muc=danh_muc,
        khu_vuc_uu_tien_id=profile.khu_vuc_uu_tien_id if profile else None,
        doi_tuong_uu_tien_id=profile.doi_tuong_uu_tien_id if profile else None,
        tinh_thanh_id=profile.tinh_thanh_id if profile else None,
        kha_nang_tai_chinh=profile.kha_nang_tai_chinh if profile else None,
    )
    hs = kq.ho_so
    ngay_cap = {}
    for c in (profile.trinh_do_hoc_van or {}).get("chung_chi_ngoai_ngu") or [] if profile else []:
        ngay_cap.setdefault(str(c.get("ma", "")).upper(), c.get("thoi_gian_cap"))
    return HoSoXetTuyenWrite(
        nam_tot_nghiep=hs.nam_tot_nghiep,
        da_tot_nghiep=hs.da_tot_nghiep,
        ma_tinh=hs.mong_muon_tinh[0] if hs.mong_muon_tinh else None,
        ma_khu_vuc_uu_tien=hs.khu_vuc,
        ma_doi_tuong_uu_tien=hs.doi_tuong,
        ngan_sach_hoc_phi_nam=hs.ngan_sach,
        ket_qua_nam_hoc=[
            KetQuaNamHocWrite(lop=lop, diem_tb_chung=k.tbc, hoc_luc=k.hoc_luc, ren_luyen=k.ren_luyen)
            for lop, k in sorted(hs.nam_hoc.items())
        ],
        diem_mon=[
            DiemMonWrite(ma_mon=ma, nguon_diem="THI_THPT", diem=d, nam=nam_tuyen_sinh, la_du_kien=True)
            for ma, d in hs.diem_thpt.items()
        ]
        + [
            DiemMonWrite(ma_mon=ma, nguon_diem="HOC_BA", lop=lop, diem=d)
            for ma, theo_lop in hs.hoc_ba.items()
            for lop, d in sorted(theo_lop.items())
        ],
        diem_bai_thi=[
            DiemBaiThiWrite(ma_bai_thi=b.ma, nam_thi=b.nam or nam_tuyen_sinh, diem=b.diem)
            for b in hs.bai_thi
            if b.diem is not None
        ],
        chung_chi=[
            ChungChiWrite(ma_chung_chi=c.ma, diem=c.diem, cap_do=c.cap_do, ngay_cap=ngay_cap.get(c.ma))
            for c in hs.chung_chi
            if c.diem is not None or c.cap_do
        ],
        thanh_tich=[ThanhTichWrite(ma_thanh_tich=t.ma, muc_giai=t.muc_giai) for t in hs.thanh_tich],
        mong_muon=[MongMuonWrite(loai="TINH_THANH", gia_tri=ma) for ma in hs.mong_muon_tinh],
    )


def _hop_nhat(cu: HoSoXetTuyenWrite, moi: HoSoXetTuyenWrite) -> HoSoXetTuyenWrite:
    """Phần JSON cũ quản lý lấy theo `moi`; thông tin chỉ hs_* có (hạn chứng chỉ, môn đạt giải...) giữ từ `cu`."""
    chung_chi_cu = {c.ma_chung_chi: c for c in cu.chung_chi}
    bai_thi_cu = {b.ma_bai_thi: b for b in cu.diem_bai_thi}
    thanh_tich_cu = {t.ma_thanh_tich: t for t in cu.thanh_tich}
    diem_mon_cu = {(d.nguon_diem, d.ma_mon, d.lop, d.hoc_ky): d for d in cu.diem_mon}
    return cu.model_copy(
        update={
            "ma_tinh": moi.ma_tinh,
            "ma_khu_vuc_uu_tien": moi.ma_khu_vuc_uu_tien,
            "ma_doi_tuong_uu_tien": moi.ma_doi_tuong_uu_tien,
            "ket_qua_nam_hoc": [
                k.model_copy(update={"hoc_luc": next((c.hoc_luc for c in cu.ket_qua_nam_hoc if c.lop == k.lop), k.hoc_luc)})
                for k in moi.ket_qua_nam_hoc
            ],
            "diem_mon": [
                m.model_copy(update={"nam": c.nam, "la_du_kien": c.la_du_kien})
                if (c := diem_mon_cu.get((m.nguon_diem, m.ma_mon, m.lop, m.hoc_ky)))
                else m
                for m in moi.diem_mon
            ]
            # Điểm học kỳ chỉ hs_* có.
            + [d for d in cu.diem_mon if d.hoc_ky != 0],
            "diem_bai_thi": [
                c.model_copy(update={"diem": b.diem}) if (c := bai_thi_cu.get(b.ma_bai_thi)) else b
                for b in moi.diem_bai_thi
            ],
            "chung_chi": [
                c.model_copy(update={"diem": m.diem, "cap_do": m.cap_do, "ngay_cap": m.ngay_cap or c.ngay_cap})
                if (c := chung_chi_cu.get(m.ma_chung_chi))
                else m
                for m in moi.chung_chi
            ],
            "thanh_tich": [
                c.model_copy(update={"muc_giai": t.muc_giai}) if (c := thanh_tich_cu.get(t.ma_thanh_tich)) else t
                for t in moi.thanh_tich
            ],
        }
    )


def luu_ho_so(
    db: Session, nguoi_dung_id: int, payload: HoSoXetTuyenWrite, dm: DanhMucMa | None = None
) -> HsHoSo:
    """Lưu hồ sơ chính của thành viên vào hs_* và ghi song song sang hồ sơ năng lực cũ. Không commit."""
    dm = dm or DanhMucMa.tu_csdl(db)
    hs = ho_so_chinh(db, nguoi_dung_id)
    if hs is None:
        hs = HsHoSo(nguoi_dung_id=nguoi_dung_id, la_ho_so_chinh=True)
        db.add(hs)
    ghi_ho_so(db, hs, payload, dm)
    profile = db.scalar(select(NguoiDungThongTin).where(NguoiDungThongTin.nguoi_dung_id == nguoi_dung_id))
    if profile is None:
        profile = NguoiDungThongTin(nguoi_dung_id=nguoi_dung_id)
        db.add(profile)
    profile.trinh_do_hoc_van = sang_trinh_do_hoc_van(payload, profile.trinh_do_hoc_van, set(dm.mon))
    profile.tinh_thanh_id = hs.tinh_thanh_id
    profile.khu_vuc_uu_tien_id = hs.khu_vuc_uu_tien_id
    profile.doi_tuong_uu_tien_id = hs.doi_tuong_uu_tien_id
    db.flush()
    return hs


def dong_bo_tu_json(
    db: Session, profile: NguoiDungThongTin, *, nam_tuyen_sinh: int, dm: DanhMucMa | None = None
) -> HsHoSo | None:
    """Sau khi lưu hồ sơ năng lực cũ: cập nhật hồ sơ hs_* chính (nếu đã có) cho khớp. Không commit."""
    hs = ho_so_chinh(db, profile.nguoi_dung_id)
    if hs is None:
        return None
    dm = dm or DanhMucMa.tu_csdl(db)
    moi = tu_trinh_do_hoc_van(profile, nam_tuyen_sinh=nam_tuyen_sinh, danh_muc=DanhMucHoSo.tu_csdl(db))
    cu = doc_ho_so(db, hs, dm)
    hop_nhat = HoSoXetTuyenWrite.model_validate(_hop_nhat(cu, moi).model_dump(include=set(HoSoXetTuyenWrite.model_fields)))
    # Bỏ mã không còn trong danh mục (JSON cũ có thể chứa mã môn ngoài danh mục như CN, GDDP).
    hop_nhat = hop_nhat.model_copy(
        update={
            "diem_mon": [d for d in hop_nhat.diem_mon if d.ma_mon in dm.mon],
            "chung_chi": [c for c in hop_nhat.chung_chi if c.ma_chung_chi in dm.chung_chi],
            "diem_bai_thi": [b for b in hop_nhat.diem_bai_thi if b.ma_bai_thi in dm.bai_thi],
            "thanh_tich": [t for t in hop_nhat.thanh_tich if t.ma_thanh_tich in dm.thanh_tich],
        }
    )
    ghi_ho_so(db, hs, hop_nhat, dm)
    return hs
