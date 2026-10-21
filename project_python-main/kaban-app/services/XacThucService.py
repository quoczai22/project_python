from models.NguoiDung import NguoiDung
from exceptions import KhongTimThayError, XacThucThatBaiError, KhongCoQuyenError
from logger import logger


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
