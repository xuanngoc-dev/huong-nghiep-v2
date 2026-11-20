"""Bộ import quy tắc xét tuyển, phần ghi (bước 2.4 KE_HOACH_TRIEN_KHAI.md).

`nhap_quy_tac(db, du_lieu, ...)` kiểm tra file bằng `chuan_bi_nhap` (lỗi thì chưa ghi gì) rồi ghi vào CSDL, thay
toàn bộ quy tắc xét tuyển cũ của đề án. Hàm không commit: người gọi commit, lỗi giữa chừng thì rollback để không còn
dòng nào được ghi.

Thứ tự ghi: đề án → cơ sở → tổ hợp riêng → bảng quy đổi → công thức → chương trình → phương án → nhóm điều kiện →
điểm cộng → học phí → điểm chuẩn → nhật ký import.

- Đề án tìm theo (mã trường, năm); chưa có thì tạo. Thông tin mô tả đã có không bị ghi đè.
- Cơ sở khớp theo tên; chương trình khớp theo (mã xét tuyển, tên), không khớp thì theo mã xét tuyển nếu mã đó chỉ
  có một chương trình, còn lại tạo mới. Ngành, cơ sở, chỉ tiêu đã nhập tay chỉ bị thay khi file có giá trị.
- Chương trình đang có trong đề án mà file không nhắc tới được giữ nguyên, chỉ báo trong cảnh báo.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from unicodedata import normalize

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_to_hop_mon_hoc_chi_tiet import DmToHopMonHocChiTiet
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucHeSoMon, XtCongThucThanhPhan
from app.models.xt_diem_chuan import XtDiemChuan
from app.models.xt_dieu_kien import XtDiemCong, XtDieuKien, XtNhomDieuKien
from app.models.xt_lich_su_import import XtLichSuImport
from app.models.xt_phuong_an import XtPhuongAn
from app.services.xet_tuyen_import import DanhMucXetTuyen, KeHoachNhap, XetTuyenImportError, chuan_bi_nhap
from app.services.xt_quy_tac import delete_quy_tac_xet_tuyen

# trang_thai_xet_tuyen của đề án
CHUA_CHUAN_HOA, THU_NGHIEM, DANG_AP_DUNG = 0, 1, 2


@dataclass
class KetQuaNhap:
    de_an_id: int
    tao_de_an: bool
    so_dong: dict[str, int]
    canh_bao: list[str] = field(default_factory=list)
    quy_dinh_chua_mo_hinh_hoa: list[dict] = field(default_factory=list)
    lich_su_id: int | None = None


def nhap_quy_tac(
    db: Session,
    du_lieu,
    *,
    ten_file: str | None = None,
    ma_bam: str | None = None,
    nguoi_import_id: int | None = None,
    danh_muc: DanhMucXetTuyen | None = None,
    tu_dong_chuan_hoa: bool = True,
    giu_diem_chuan_ngoai_file: bool = False,
    phuong_thuc_theo_phuong_an: dict[tuple[str, str], tuple[int, int]] | None = None,
) -> KetQuaNhap:
    """Ghi quy tắc xét tuyển, dùng cặp ID phương thức và chương trình đã đối chiếu khi được cung cấp."""
    ke_hoach = chuan_bi_nhap(
        du_lieu, danh_muc or DanhMucXetTuyen.tu_csdl(db), tu_dong_chuan_hoa=tu_dong_chuan_hoa
    )
    return _Ghi(db, ke_hoach, phuong_thuc_theo_phuong_an).chay(
        ten_file=ten_file,
        ma_bam=ma_bam,
        nguoi_import_id=nguoi_import_id,
        giu_diem_chuan_ngoai_file=giu_diem_chuan_ngoai_file,
    )


class _Ghi:
    def __init__(
        self, db: Session, ke_hoach: KeHoachNhap, phuong_thuc_theo_phuong_an: dict[tuple[str, str], tuple[int, int]] | None
    ):
        self.db = db
        self.kh = ke_hoach
        self.phuong_thuc_theo_phuong_an = phuong_thuc_theo_phuong_an
        self.now = datetime.now()
        self.dem: Counter[str] = Counter()
        self.canh_bao = list(ke_hoach.canh_bao)

    def _them(self, obj) -> object:
        self.db.add(obj)
        self.dem[obj.__tablename__] += 1
        return obj

    def chay(self, *, ten_file, ma_bam, nguoi_import_id, giu_diem_chuan_ngoai_file: bool) -> KetQuaNhap:
        de_an, tao_moi = self._de_an()
        delete_quy_tac_xet_tuyen(self.db, [de_an.id], giu_lich_su=True)
        co_so = self._co_so(de_an)
        to_hop = self._to_hop_rieng()
        bang = self._bang_quy_doi(de_an)
        cong_thuc = self._cong_thuc(de_an, bang)
        chuong_trinh = self._chuong_trinh(de_an, co_so)
        self._phuong_an(de_an, cong_thuc, chuong_trinh, to_hop)
        self._nhom_dieu_kien(de_an, cong_thuc, chuong_trinh)
        self._diem_cong(de_an, cong_thuc)
        self._hoc_phi(de_an, chuong_trinh)
        self._diem_chuan(to_hop, giu_diem_chuan_ngoai_file)
        self.db.flush()
        so_dong = dict(sorted(self.dem.items()))
        lich_su = XtLichSuImport(
            de_an_id=de_an.id,
            ten_file=ten_file,
            ma_bam=ma_bam,
            phien_ban_chuan=self.kh.phien_ban,
            so_dong=so_dong,
            quy_dinh_chua_mo_hinh_hoa=self.kh.quy_dinh_chua_mo_hinh_hoa,
            nguoi_import_id=nguoi_import_id,
            tao_luc=self.now,
        )
        self.db.add(lich_su)
        self.db.flush()
        return KetQuaNhap(
            de_an_id=de_an.id,
            tao_de_an=tao_moi,
            so_dong=so_dong,
            canh_bao=self.canh_bao,
            quy_dinh_chua_mo_hinh_hoa=self.kh.quy_dinh_chua_mo_hinh_hoa,
            lich_su_id=lich_su.id,
        )

    def _de_an(self) -> tuple[DatsTuyenSinh, bool]:
        thong_tin = self.kh.de_an
        de_an = self.db.scalar(
            select(DatsTuyenSinh).where(
                DatsTuyenSinh.ma_truong == self.kh.ma_truong, DatsTuyenSinh.nam_tuyen_sinh == self.kh.nam_tuyen_sinh
            )
        )
        tao_moi = de_an is None
        if tao_moi:
            ghi_chu = thong_tin["ghi_chu"]
            if thong_tin["so_quyet_dinh"]:
                ghi_chu = f"Quyết định {thong_tin['so_quyet_dinh']}" + (f". {ghi_chu}" if ghi_chu else "")
            de_an = DatsTuyenSinh(
                ma_truong=self.kh.ma_truong,
                nam_tuyen_sinh=self.kh.nam_tuyen_sinh,
                ten_de_an=thong_tin["ten_de_an"],
                ngay_cong_bo=thong_tin["ngay_cong_bo"],
                nguon_du_lieu_url=thong_tin["nguon_du_lieu_url"],
                ghi_chu=ghi_chu,
                tao_luc=self.now,
            )
            self.db.add(de_an)
        else:
            # Chỉ điền chỗ còn trống, không ghi đè mô tả đã nhập.
            for cot in ("ten_de_an", "ngay_cong_bo", "nguon_du_lieu_url"):
                if getattr(de_an, cot) in (None, "") and thong_tin[cot]:
                    setattr(de_an, cot, thong_tin[cot])
        if de_an.trang_thai_xet_tuyen in (None, CHUA_CHUAN_HOA):
            de_an.trang_thai_xet_tuyen = THU_NGHIEM
        de_an.cap_nhat_luc = self.now
        self.db.flush()
        return de_an, tao_moi

    def _co_so(self, de_an: DatsTuyenSinh) -> dict[str | None, int]:
        """Mã cơ sở trong file → id dats_tru_so; khóa None = trụ sở chính."""
        def khoa_ten(ten: str) -> str:
            return " ".join(normalize("NFC", ten).split()) if self.phuong_thuc_theo_phuong_an is not None else ten

        hien_co = {
            khoa_ten(cs.ten_co_so): cs for cs in self.db.scalars(select(DatsTruSo).where(DatsTruSo.de_an_id == de_an.id))
        }
        theo_ma: dict[str | None, int] = {}
        for dong in self.kh.co_so:
            khoa = khoa_ten(dong["ten_co_so"])
            cs = hien_co.get(khoa)
            if cs is None:
                if self.phuong_thuc_theo_phuong_an is not None:
                    raise XetTuyenImportError([f"co_so {dong['ma_co_so']}: không tìm được cơ sở đã đối chiếu"])
                cs = self._them(DatsTruSo(de_an_id=de_an.id, ten_co_so=dong["ten_co_so"]))
                cs.loai_co_so = "tru_so" if dong["vai_tro"] == "chinh" else "co_so"
            cs.vai_tro = dong["vai_tro"]
            if dong["tinh_thanh_id"] is not None:
                cs.tinh_thanh_id = dong["tinh_thanh_id"]
            if dong["dia_chi"]:
                cs.dia_chi = dong["dia_chi"]
            self.db.flush()
            hien_co[khoa] = cs
            theo_ma[dong["ma_co_so"]] = cs.id
        chinh = [cs.id for cs in hien_co.values() if cs.vai_tro == "chinh"]
        theo_ma[None] = chinh[0] if len(chinh) == 1 else None
        return theo_ma

    def _to_hop_rieng(self) -> dict[str, int]:
        """Mã tổ hợp riêng (đã gắn tiền tố) → id; tạo hoặc cập nhật tổ hợp và thay chi tiết vị trí môn."""
        theo_ma: dict[str, int] = {}
        for dong in self.kh.to_hop_rieng:
            to_hop = self.db.scalar(select(DmToHopMonHoc).where(DmToHopMonHoc.ma_to_hop == dong["ma_to_hop"]))
            if to_hop is None:
                to_hop = self._them(
                    DmToHopMonHoc(ma_to_hop=dong["ma_to_hop"], ten_to_hop=dong["ten_to_hop"], ds_mon_hoc=[], trang_thai=1)
                )
            to_hop.ten_to_hop = dong["ten_to_hop"]
            to_hop.ds_mon_hoc = dong["ds_mon_hoc"]
            to_hop.ghi_chu = f"Tổ hợp riêng của trường {self.kh.ma_truong} (mã trong đề án: {dong['ma_goc']})"
            self.db.flush()
            self.db.execute(delete(DmToHopMonHocChiTiet).where(DmToHopMonHocChiTiet.to_hop_id == to_hop.id))
            for mon_hoc_id, thu_tu in dong["chi_tiet"]:
                self._them(DmToHopMonHocChiTiet(to_hop_id=to_hop.id, mon_hoc_id=mon_hoc_id, thu_tu_mon=thu_tu))
            theo_ma[dong["ma_to_hop"]] = to_hop.id
        self.db.flush()
        return theo_ma

    def _bang_quy_doi(self, de_an: DatsTuyenSinh) -> dict[str, int]:
        theo_ma: dict[str, int] = {}
        for dong in self.kh.bang_quy_doi:
            bang = self._them(
                XtBangQuyDoi(
                    de_an_id=de_an.id,
                    ma_bang=dong["ma_bang"],
                    ten_bang=dong["ten_bang"],
                    thang_diem_dich=dong["thang_diem_dich"],
                    ghi_chu=dong["ghi_chu"],
                )
            )
            self.db.flush()
            for muc in dong["muc"]:
                self._them(XtBangQuyDoiChiTiet(bang_quy_doi_id=bang.id, **muc))
            theo_ma[dong["ma_bang"]] = bang.id
        return theo_ma

    def _cong_thuc(self, de_an: DatsTuyenSinh, bang: dict[str, int]) -> dict[str, XtCongThuc]:
        theo_ma: dict[str, XtCongThuc] = {}
        for dong in self.kh.cong_thuc:
            gia_tri = {k: v for k, v in dong.items() if k not in ("he_so_mon", "thanh_phan", "ma_bang_quy_doi_ngoai_ngu")}
            ct = self._them(
                XtCongThuc(
                    de_an_id=de_an.id,
                    bang_quy_doi_ngoai_ngu_id=bang.get(dong["ma_bang_quy_doi_ngoai_ngu"]),
                    **gia_tri,
                )
            )
            self.db.flush()
            for he_so in dong["he_so_mon"]:
                self._them(XtCongThucHeSoMon(cong_thuc_id=ct.id, **he_so))
            for tp in dong["thanh_phan"]:
                gia_tri_tp = {k: v for k, v in tp.items() if k != "ma_bang_quy_doi"}
                self._them(
                    XtCongThucThanhPhan(
                        cong_thuc_id=ct.id, bang_quy_doi_id=bang.get(tp["ma_bang_quy_doi"]), **gia_tri_tp
                    )
                )
            theo_ma[dong["ma_cong_thuc"]] = ct
        return theo_ma

    def _chuong_trinh(self, de_an: DatsTuyenSinh, co_so: dict[str | None, int]) -> dict[str, int]:
        """Mã chương trình trong file → id dats_chuong_trinh_dao_tao (khớp chương trình có sẵn hoặc tạo mới)."""
        hien_co = list(
            self.db.scalars(select(DatsChuongTrinhDaoTao).where(DatsChuongTrinhDaoTao.de_an_id == de_an.id))
        )
        theo_cap = {(ct.ma_xet_tuyen, ct.ten_chuong_trinh): ct for ct in hien_co}
        dem_ma = Counter(ct.ma_xet_tuyen for ct in hien_co)
        theo_ma_xt = {ct.ma_xet_tuyen: ct for ct in hien_co if dem_ma[ct.ma_xet_tuyen] == 1}
        theo_id = {ct.id: ct for ct in hien_co}
        chuong_trinh_da_doi_chieu = (
            {ma: ct_id for (ma, _), (_, ct_id) in self.phuong_thuc_theo_phuong_an.items()}
            if self.phuong_thuc_theo_phuong_an is not None else None
        )
        da_dung: set[int] = set()
        theo_ma: dict[str, int] = {}
        for dong in self.kh.chuong_trinh:
            ma = dong["ma_chuong_trinh"]
            if chuong_trinh_da_doi_chieu is not None:
                ct = theo_id.get(chuong_trinh_da_doi_chieu.get(ma))
                if ct is None or ct.id in da_dung:
                    raise XetTuyenImportError([f"chuong_trinh {ma}: không tìm được chương trình đã đối chiếu"])
            else:
                ct = theo_cap.get((dong["ma_xet_tuyen"], dong["ten_chuong_trinh"]))
                if ct is None or ct.id in da_dung:
                    ct = theo_ma_xt.get(dong["ma_xet_tuyen"])
                if ct is not None and ct.id in da_dung:
                    ct = None
            if ct is None:
                ct = self._them(
                    DatsChuongTrinhDaoTao(
                        de_an_id=de_an.id, ma_xet_tuyen=dong["ma_xet_tuyen"], ten_chuong_trinh=dong["ten_chuong_trinh"]
                    )
                )
            co_so_id = co_so.get(dong["ma_co_so"]) if dong["ma_co_so"] is not None else co_so.get(None)
            if co_so_id is not None:
                ct.co_so_id = co_so_id
            if dong["nganh_dao_tao_id"] is not None:
                ct.nganh_dao_tao_id = dong["nganh_dao_tao_id"]
            if dong["chi_tieu_tuyen_sinh"] is not None:
                ct.chi_tieu_tuyen_sinh = dong["chi_tieu_tuyen_sinh"]
            self.db.flush()
            da_dung.add(ct.id)
            theo_ma[ma] = ct.id
        ngoai_file = [ct for ct in hien_co if ct.id not in da_dung]
        if ngoai_file:
            ds = ", ".join(ct.ma_xet_tuyen or ct.ten_chuong_trinh for ct in ngoai_file[:10])
            self.canh_bao.append(
                f"{len(ngoai_file)} chương trình đang có trong đề án nhưng không có trong file, sẽ không có phương án "
                f"xét tuyển: {ds}{'...' if len(ngoai_file) > 10 else ''}"
            )
        return theo_ma

    def _phuong_an(self, de_an, cong_thuc: dict[str, XtCongThuc], chuong_trinh: dict[str, int], to_hop: dict) -> None:
        # Các phương thức riêng (như TSA và SPT) có thể dùng chung một mã Bộ.
        phuong_thuc: dict[tuple[int, str], int] = {}
        pt_theo_cong_thuc: dict[tuple[int, str, str], int] = {}
        pt_theo_ma_truong: dict[tuple[int, str, str], list[int]] = defaultdict(list)
        if self.phuong_thuc_theo_phuong_an is None:
            for pt_id, ct_id, ma_pt, ma_cong_thuc, ma_pt_truong in self.db.execute(
                select(
                    DatsPhuongThuc.id,
                    DatsPhuongThuc.de_an_chuong_trinh_id,
                    DatsPhuongThuc.ma_phuong_thuc_cua_bo,
                    DatsPhuongThuc.cong_thuc_tinh_diem,
                    DatsPhuongThuc.ma_phuong_thuc_cua_truong,
                )
                .where(DatsPhuongThuc.de_an_chuong_trinh_id.in_(set(chuong_trinh.values())))
                .order_by(DatsPhuongThuc.id)
            ):
                phuong_thuc.setdefault((ct_id, ma_pt), pt_id)
                if ma_cong_thuc:
                    pt_theo_cong_thuc.setdefault((ct_id, ma_pt, ma_cong_thuc), pt_id)
                if ma_pt_truong:
                    pt_theo_ma_truong[(ct_id, ma_pt, ma_pt_truong)].append(pt_id)
        for dong in self.kh.phuong_an:
            ct = cong_thuc[dong["ma_cong_thuc"]]
            ma_chuong_trinh = dong["ma_chuong_trinh"]
            ct_id = chuong_trinh[ma_chuong_trinh]
            ma_pt_truong = dong.get("ma_phuong_thuc_cua_truong")
            if self.phuong_thuc_theo_phuong_an is not None:
                da_doi_chieu = self.phuong_thuc_theo_phuong_an.get((ma_chuong_trinh, ct.ma_cong_thuc))
                if da_doi_chieu is None or da_doi_chieu[1] != ct_id:
                    raise XetTuyenImportError([
                        f"chuong_trinh {ma_chuong_trinh}: chưa đối chiếu phương thức của {ct.ma_cong_thuc}"
                    ])
                pt_id = da_doi_chieu[0]
            elif ma_pt_truong is not None:
                cac_pt = pt_theo_ma_truong[(ct_id, ct.ma_phuong_thuc_cua_bo, ma_pt_truong)]
                if len(cac_pt) != 1:
                    raise XetTuyenImportError([
                        f"chuong_trinh {ma_chuong_trinh}: cần đúng một dòng cho mã phương thức của trường {ma_pt_truong}"
                    ])
                pt_id = cac_pt[0]
            else:
                pt_id = pt_theo_cong_thuc.get(
                    (ct_id, ct.ma_phuong_thuc_cua_bo, ct.ma_cong_thuc),
                    phuong_thuc.get((ct_id, ct.ma_phuong_thuc_cua_bo)),
                )
            self._them(
                XtPhuongAn(
                    de_an_id=de_an.id,
                    de_an_chuong_trinh_id=ct_id,
                    de_an_phuong_thuc_id=pt_id,
                    cong_thuc_id=ct.id,
                    to_hop_id=dong["to_hop_id"] or to_hop.get(dong["ma_to_hop"]),
                )
            )

    def _nhom_dieu_kien(self, de_an, cong_thuc: dict[str, XtCongThuc], chuong_trinh: dict[str, int]) -> None:
        for dong in self.kh.nhom_dieu_kien:
            nhom = self._them(
                XtNhomDieuKien(
                    de_an_id=de_an.id,
                    cong_thuc_id=cong_thuc[dong["ma_cong_thuc"]].id if dong["ma_cong_thuc"] else None,
                    de_an_chuong_trinh_id=chuong_trinh[dong["ma_chuong_trinh"]] if dong["ma_chuong_trinh"] else None,
                    ma_nhom=dong["ma_nhom"],
                    ten_nhom=dong["ten_nhom"],
                    mo_ta=dong["mo_ta"],
                    bat_buoc=dong["bat_buoc"],
                )
            )
            self.db.flush()
            for dk in dong["dieu_kien"]:
                self._them(XtDieuKien(nhom_dieu_kien_id=nhom.id, **dk))

    def _diem_cong(self, de_an, cong_thuc: dict[str, XtCongThuc]) -> None:
        for dong in self.kh.diem_cong:
            gia_tri = {k: v for k, v in dong.items() if k != "ma_cong_thuc"}
            cong_thuc_id = cong_thuc[dong["ma_cong_thuc"]].id if dong["ma_cong_thuc"] else None
            self._them(XtDiemCong(de_an_id=de_an.id, cong_thuc_id=cong_thuc_id, **gia_tri))

    def _hoc_phi(self, de_an, chuong_trinh: dict[str, int]) -> None:
        for dong in self.kh.chuong_trinh:
            if dong["hoc_phi"]:
                self._them(
                    DatsHocPhi(de_an_id=de_an.id, de_an_chuong_trinh_id=chuong_trinh[dong["ma_chuong_trinh"]], **dong["hoc_phi"])
                )

    def _diem_chuan(self, to_hop: dict[str, int], giu_diem_chuan_ngoai_file: bool) -> None:
        """Thay điểm chuẩn theo khóa hoặc theo cả năm, tùy chế độ nhập."""
        if not self.kh.diem_chuan:
            return
        nam = {d["nam_tuyen_sinh"] for d in self.kh.diem_chuan}
        pham_vi = (XtDiemChuan.ma_truong == self.kh.ma_truong, XtDiemChuan.nam_tuyen_sinh.in_(nam))
        moi = [
            XtDiemChuan(
                ma_truong=self.kh.ma_truong,
                to_hop_id=dong["to_hop_id"] or to_hop.get(dong["ma_to_hop"]),
                tao_luc=self.now,
                cap_nhat_luc=self.now,
                **{k: v for k, v in dong.items() if k not in ("ma_to_hop", "to_hop_id")},
            )
            for dong in self.kh.diem_chuan
        ]
        xoa = delete(XtDiemChuan).where(*pham_vi)
        if giu_diem_chuan_ngoai_file:
            def khoa(dong: XtDiemChuan) -> tuple:
                return dong.nam_tuyen_sinh, dong.ma_xet_tuyen, dong.ma_phuong_thuc_cua_bo, dong.to_hop_id

            khoa_moi = {khoa(dong) for dong in moi}
            id_thay = [
                dong.id
                for dong in self.db.scalars(select(XtDiemChuan).where(*pham_vi).with_for_update())
                if khoa(dong) in khoa_moi
            ]
            xoa = xoa.where(XtDiemChuan.id.in_(id_thay))
        self.db.execute(xoa.execution_options(synchronize_session=False))
        for dong in moi:
            self._them(dong)
