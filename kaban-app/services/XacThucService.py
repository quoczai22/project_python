import re
from models.NguoiDung import NguoiDung, ThanhVien
from exceptions import (
    KhongTimThayError, XacThucThatBaiError, KhongCoQuyenError,
    DuLieuKhongHopLeError, XungDotDuLieuError, LoiLuuTruError
)
from config import MAT_KHAU_TOI_THIEU, MAU_TEN_DANG_NHAP, MAU_EMAIL
from logger import logger

_REGEX_TEN_DANG_NHAP = re.compile(MAU_TEN_DANG_NHAP)
_REGEX_EMAIL = re.compile(MAU_EMAIL)


class XacThucService:
    """
    Dịch vụ quản lý xác thực đăng nhập và phiên làm việc của người dùng.
    """

    def __init__(self):
        self._nguoi_dung_hien_tai: NguoiDung = None

    @property
    def nguoi_dung_hien_tai(self) -> NguoiDung:
        return self._nguoi_dung_hien_tai

    @nguoi_dung_hien_tai.setter
    def nguoi_dung_hien_tai(self, user: NguoiDung):
        self._nguoi_dung_hien_tai = user

    def dang_nhap(self, ten_dang_nhap: str, mat_khau: str, bo_luu_tru):
        """Xác thực đăng nhập người dùng; ném ngoại lệ chuẩn xác khi thất bại."""
        danh_sach_thanh_vien = bo_luu_tru.doc_danh_sach_thanh_vien()

        thanh_vien = next(
            (tv for tv in danh_sach_thanh_vien if tv.ten_dang_nhap == ten_dang_nhap),
            None
        )
        if thanh_vien is None:
            raise KhongTimThayError(
                f"Tài khoản '{ten_dang_nhap}' không tồn tại trong hệ thống",
                loai_tai_nguyen="ThanhVien",
                khoa_tim_kiem=ten_dang_nhap
            )

        if not thanh_vien.kiem_tra_mat_khau(mat_khau):
            raise XacThucThatBaiError("Mật khẩu không chính xác")

        self._nguoi_dung_hien_tai = thanh_vien
        logger.info(f"Người dùng '{ten_dang_nhap}' ({thanh_vien.vai_tro}) đã đăng nhập thành công")
        return self._nguoi_dung_hien_tai

    def dang_ky(self, ten_dang_nhap: str, mat_khau: str, ho_ten: str, email: str, bo_luu_tru):
        """
        Tạo tài khoản mới (luôn là vai trò 'thanh_vien', không cho tự đăng ký quản trị).
        Kiểm tra: tên đăng nhập hợp lệ + không trùng, mật khẩu đủ dài, email đúng regex + không trùng.
        Ném DuLieuKhongHopLeError / XungDotDuLieuError / LoiLuuTruError; thành công trả về ThanhVien mới.
        """
        ten_dang_nhap = (ten_dang_nhap or "").strip()
        ho_ten = (ho_ten or "").strip()
        email = (email or "").strip()
        mat_khau = mat_khau or ""

        if not _REGEX_TEN_DANG_NHAP.fullmatch(ten_dang_nhap):
            raise DuLieuKhongHopLeError(
                "Tên đăng nhập gồm 3-20 ký tự: chữ không dấu, số hoặc dấu gạch dưới",
                truong_loi="ten_dang_nhap", gia_tri=ten_dang_nhap
            )
        if len(mat_khau) < MAT_KHAU_TOI_THIEU:
            raise DuLieuKhongHopLeError(
                f"Mật khẩu phải có ít nhất {MAT_KHAU_TOI_THIEU} ký tự",
                truong_loi="mat_khau"
            )
        if email and not _REGEX_EMAIL.fullmatch(email):
            raise DuLieuKhongHopLeError(
                "Email không đúng định dạng (ví dụ: ten@gmail.com)",
                truong_loi="email", gia_tri=email
            )

        danh_sach = bo_luu_tru.doc_danh_sach_thanh_vien()
        if any(tv.ten_dang_nhap.lower() == ten_dang_nhap.lower() for tv in danh_sach):
            raise XungDotDuLieuError(
                f"Tên đăng nhập '{ten_dang_nhap}' đã tồn tại",
                khoa_trung="ten_dang_nhap", gia_tri=ten_dang_nhap
            )
        if email and any((tv.email or "").lower() == email.lower() for tv in danh_sach):
            raise XungDotDuLieuError(
                f"Email '{email}' đã được dùng cho tài khoản khác",
                khoa_trung="email", gia_tri=email
            )

        thanh_vien_moi = ThanhVien(ten_dang_nhap, mat_khau, ho_ten, email)  # mật khẩu được băm SHA-256 ở đây
        try:
            bo_luu_tru.ghi_danh_sach_thanh_vien(danh_sach + [thanh_vien_moi])
        except LoiLuuTruError:
            logger.error(f"Không thể lưu tài khoản mới '{ten_dang_nhap}'")
            raise
        except Exception as err:
            logger.error(f"Không thể lưu tài khoản mới '{ten_dang_nhap}': {err}")
            raise LoiLuuTruError(f"Không thể lưu tài khoản mới: {err}", loi_goc=err)

        logger.info(f"Đã tạo tài khoản mới '{ten_dang_nhap}' (thanh_vien)")
        return thanh_vien_moi

    def dang_xuat(self):
        """Đăng xuất tài khoản hiện tại."""
        user = self._nguoi_dung_hien_tai
        self._nguoi_dung_hien_tai = None
        if user:
            logger.info(f"Người dùng '{user.ten_dang_nhap}' đã đăng xuất")

    def kiem_tra_quyen_du_an(self, du_an, bat_loi: bool = False) -> bool:
        """ĐA HÌNH: Kiểm tra quyền truy cập dự án của người dùng hiện tại."""
        if self._nguoi_dung_hien_tai is None:
            if bat_loi:
                raise KhongCoQuyenError("Bạn chưa đăng nhập vào hệ thống", hanh_dong="TRUY_CAP_DU_AN")
            return False

        co_quyen = self._nguoi_dung_hien_tai.kiem_tra_quyen_du_an(du_an)
        if not co_quyen and bat_loi:
            raise KhongCoQuyenError(
                f"Người dùng '{self._nguoi_dung_hien_tai.ten_dang_nhap}' không có quyền truy cập dự án '{getattr(du_an, 'ma_du_an', '')}'",
                nguoi_dung=self._nguoi_dung_hien_tai.ten_dang_nhap,
                hanh_dong="TRUY_CAP_DU_AN"
            )
        return co_quyen

    def kiem_tra_quyen_cong_viec(self, cong_viec, bat_loi: bool = False) -> bool:
        """ĐA HÌNH: Kiểm tra quyền thao tác trên công việc của người dùng hiện tại."""
        if self._nguoi_dung_hien_tai is None:
            if bat_loi:
                raise KhongCoQuyenError("Bạn chưa đăng nhập vào hệ thống", hanh_dong="THAO_TAC_CONG_VIEC")
            return False

        co_quyen = self._nguoi_dung_hien_tai.kiem_tra_quyen_cong_viec(cong_viec)
        if not co_quyen and bat_loi:
            raise KhongCoQuyenError(
                f"Người dùng '{self._nguoi_dung_hien_tai.ten_dang_nhap}' không có quyền thao tác trên công việc '{getattr(cong_viec, 'ma_cong_viec', '')}'",
                nguoi_dung=self._nguoi_dung_hien_tai.ten_dang_nhap,
                hanh_dong="THAO_TAC_CONG_VIEC"
            )
        return co_quyen

    def co_quyen_xoa(self) -> bool:
        """Kiểm tra quyền xóa (chỉ quản trị viên có quyền)."""
        if self._nguoi_dung_hien_tai is None:
            return False
        return self._nguoi_dung_hien_tai.co_quyen_xoa_cong_viec()
