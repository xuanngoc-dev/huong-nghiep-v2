from app.models.chat_conversations import ChatConversation
from app.models.chat_messages import ChatMessage
from app.models.dm_chuyen_nganh import DmChuyenNganh
from app.models.dm_dan_toc import DmDanToc
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_linh_vuc_dao_tao import DmLinhVucDaoTao
from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_muc_diem_uu_tien import DmMucDiemUuTien
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_nganh_hoc_theo_truong import DmNganhHocTheoTruong
from app.models.dm_nhom_nganh_dao_tao import DmNhomNganhDaoTao
from app.models.dm_nhom_nghe_di_lam import DmNgheCuTheDiLam, DmNhomNgheDiLam, DmNhomNgheTieuChi, DmTieuChiGoiY
from app.models.dm_nhom_tinh_cach_holland import DmNhomTinhCachHolland
from app.models.dm_thcs_huong_di import (
    DmThcsHuongDi,
    DmThcsHuongDiTieuChi,
    DmThcsLoiKhuyenLuuY,
    DmThcsTieuChi,
    DmThcsUuNhuocDiem,
)
from app.models.dm_thpt_duhoc import (
    DmThptDuhocChiPhi,
    DmThptDuhocHuongDi,
    DmThptDuhocKenhKetNoi,
    DmThptDuhocNganh,
    DmThptDuhocQuocGia,
    DmThptDuhocThuTuc,
)
from app.models.dm_thpt_xkld import (
    DmThptXkldChiPhi,
    DmThptXkldKenhKetNoi,
    DmThptXkldNgheCuThe,
    DmThptXkldNhomNghe,
    DmThptXkldThiTruong,
    DmThptXkldThuTuc,
)
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_thanh_tich_hoc_tap_nghien_cuu import DmThanhTichHocTapNghienCuu
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_ton_giao import DmTonGiao
from app.models.nguoi_dung import NguoiDung
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin
from app.models.ht_cau_hinh_enduser import HtCauHinhEnduser
from app.models.ht_cau_hinh_goi_cuoc import HtCauHinhGoiCuoc
from app.models.ht_cau_hinh_tra_cuu import HtCauHinhTraCuu
from app.models.ht_lich_su_giao_dich_ngan_hang import HtLichSuGiaoDichNganHang
from app.models.ht_lich_su_nap_tien import HtLichSuNapTien
from app.models.ht_ngan_hang_thanh_toan import HtNganHangThanhToan
from app.models.tin_tuc import TinTucBaiViet, TinTucNhomTin
from app.models.tn_cau_hoi_trac_nghiem import TnCauHoiTracNghiem
from app.models.tn_cau_tra_loi import TnCauTraLoi
from app.models.tn_chi_tiet_tra_loi import TnChiTietTraLoi
from app.models.tn_lich_su_tim_truong_phu_hop import TnLichSuTimTruongPhuHop
from app.models.tn_phien_khao_sat import TnPhienKhaoSat
from app.models.truong_hoc_tuyen_sinh_theo_nam import TruongHocTuyenSinhTheoNam

from app.models.dm_van_ban import DmVanBan
from app.models.dm_truong import DmTruong
from app.models.dm_bang_cap_chung_chi import DmBangCapChungChi
from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_thanh_tich_hoc_tap import DmThanhTichHocTap
from app.models.dm_to_hop_mon_hoc_chi_tiet import DmToHopMonHocChiTiet
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dats_thu_thap import DatsBanNhapThuThap, DatsNhatKyThuThap, DatsPhienThuThap
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_website import DatsWebsite
from app.models.dats_lien_he_tuyen_sinh import DatsLienHeTuyenSinh
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_ke_hoach_tuyen_sinh import DatsKeHoachTuyenSinh
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_phuong_thuc_to_hop import DatsPhuongThucToHop
from app.models.dats_nhan_su import DatsNhanSu
from app.models.dats_co_so_vat_chat import DatsCoSoVatChat
from app.models.dats_quy_mo_dao_tao import DatsQuyMoDaoTao
from app.models.dats_ty_le_viec_lam import DatsTyLeViecLam
from app.models.dats_trinh_do_nganh import DatsTrinhDoNganh
from app.models.dats_doi_tuong_du_tuyen import DatsDoiTuongDuTuyen
from app.models.dats_dieu_kien_du_tuyen import DatsDieuKienDuTuyen
from app.models.dats_tieu_chi_xet_tuyen import DatsTieuChiXetTuyen
from app.models.dats_diem_cong import DatsDiemCong
from app.models.dats_quy_tac_phan_bo import DatsQuyTacPhanBo
from app.models.dats_ho_so_du_tuyen import DatsHoSoDuTuyen
from app.models.dats_quy_doi_nguong_dau_vao import DatsQuyDoiNguongDauVao
from app.models.dats_quy_doi_diem_trung_tuyen import DatsQuyDoiDiemTrungTuyen
from app.models.dats_chinh_sach_xet_tuyen_thang import DatsChinhSachXetTuyenThang
from app.models.dats_chinh_sach_uu_tien_xet_tuyen import DatsChinhSachUuTienXetTuyen
from app.models.xt_diem_chuan import XtDiemChuan
from app.models.dm_chi_so_xet_tuyen import DmChiSoXetTuyen
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucHeSoMon, XtCongThucThanhPhan
from app.models.xt_phuong_an import XtPhuongAn
from app.models.xt_dieu_kien import XtDiemCong, XtDieuKien, XtNhomDieuKien
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.xt_bo_tieu_chi import XtBoTieuChi, XtMucPhuHop, XtTieuChiPhuHop
from app.models.xt_lich_su_import import XtLichSuImport
from app.models.xt_ket_qua import XtKetQuaChuongTrinh, XtKetQuaPhuongAn, XtLanDanhGia
from app.models.hs_ho_so import (
    HsChungChi,
    HsDiemBaiThi,
    HsDiemMon,
    HsHoSo,
    HsKetQuaNamHoc,
    HsThanhTich,
    HsTieuChiMongMuon,
)

__all__ = [
    "DmChuyenNganh",
    "DmDanToc",
    "DmDoiTuongUuTien",
    "DmKhuVucUuTien",
    "DmLinhVucDaoTao",
    "DmLoaiCauHoi",
    "DmMonHoc",
    "DmMucDiemUuTien",
    "DmNganhDaoTao",
    "DmNhomNganhDaoTao",
    "DmNhomNgheDiLam",
    "DmNgheCuTheDiLam",
    "DmTieuChiGoiY",
    "DmNhomNgheTieuChi",
    "DmNhomTinhCachHolland",
    "DmThcsHuongDi",
    "DmThcsUuNhuocDiem",
    "DmThcsTieuChi",
    "DmThcsHuongDiTieuChi",
    "DmThcsLoiKhuyenLuuY",
    "DmThptDuhocHuongDi",
    "DmThptDuhocQuocGia",
    "DmThptDuhocNganh",
    "DmThptDuhocChiPhi",
    "DmThptDuhocThuTuc",
    "DmThptDuhocKenhKetNoi",
    "DmThptXkldNhomNghe",
    "DmThptXkldThiTruong",
    "DmThptXkldNgheCuThe",
    "DmThptXkldChiPhi",
    "DmThptXkldThuTuc",
    "DmThptXkldKenhKetNoi",
    "DmPhuongThucTuyenSinh",
    "DmThanhTichHocTapNghienCuu",
    "DmTinhThanh",
    "DmToHopMonHoc",
    "DmTonGiao",
    "NguoiDung",
    "NguoiDungThongTin",
    "HtCauHinhEnduser",
    "HtCauHinhGoiCuoc",
    "HtCauHinhTraCuu",
    "HtLichSuGiaoDichNganHang",
    "HtLichSuNapTien",
    "HtNganHangThanhToan",
    "TinTucBaiViet",
    "TinTucNhomTin",
    "TnCauHoiTracNghiem",
    "TnCauTraLoi",
    "TnChiTietTraLoi",
    "TnLichSuTimTruongPhuHop",
    "TnPhienKhaoSat",
    "TruongHocTuyenSinhTheoNam",
    "DmVanBan",
    "DmTruong",
    "DmBangCapChungChi",
    "DmBaiThiDanhGia",
    "DmThanhTichHocTap",
    "DmToHopMonHocChiTiet",
    "DatsTuyenSinh",
    "DatsPhienThuThap",
    "DatsBanNhapThuThap",
    "DatsNhatKyThuThap",
    "DatsTruSo",
    "DatsWebsite",
    "DatsLienHeTuyenSinh",
    "DatsChuongTrinhDaoTao",
    "DatsKeHoachTuyenSinh",
    "DatsPhuongThuc",
    "DatsPhuongThucToHop",
    "DatsNhanSu",
    "DatsCoSoVatChat",
    "DatsQuyMoDaoTao",
    "DatsTyLeViecLam",
    "DatsTrinhDoNganh",
    "DatsDoiTuongDuTuyen",
    "DatsDieuKienDuTuyen",
    "DatsTieuChiXetTuyen",
    "DatsDiemCong",
    "DatsQuyTacPhanBo",
    "DatsHoSoDuTuyen",
    "DatsQuyDoiNguongDauVao",
    "DatsQuyDoiDiemTrungTuyen",
    "DatsChinhSachXetTuyenThang",
    "DatsChinhSachUuTienXetTuyen",
    "XtDiemChuan",
    "DmChiSoXetTuyen",
    "XtBangQuyDoi",
    "XtBangQuyDoiChiTiet",
    "XtCongThuc",
    "XtCongThucHeSoMon",
    "XtCongThucThanhPhan",
    "XtPhuongAn",
    "XtNhomDieuKien",
    "XtDieuKien",
    "XtDiemCong",
    "DatsHocPhi",
    "XtBoTieuChi",
    "XtTieuChiPhuHop",
    "XtMucPhuHop",
    "XtLichSuImport",
    "XtLanDanhGia",
    "XtKetQuaPhuongAn",
    "XtKetQuaChuongTrinh",
    "HsHoSo",
    "HsKetQuaNamHoc",
    "HsDiemMon",
    "HsDiemBaiThi",
    "HsChungChi",
    "HsThanhTich",
    "HsTieuChiMongMuon",
    "ChatConversation",
    "ChatMessage",
]
