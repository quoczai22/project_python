from models.DuAn import DuAn
from exceptions import XungDotDuLieuError, KhongTimThayError, LoiLuuTruError, KhongCoQuyenError
from logger import logger


class DuAnService:
    """
    Dịch vụ quản lý các thao tác CRUD và thành viên dự án.
    Tích hợp cơ chế Rollback đảm bảo tính toàn vẹn dữ liệu.
    """

    def __init__(self, bo_luu_tru):
        self.bo_luu_tru = bo_luu_tru
        self.danh_sach_du_an = self._nap_du_lieu()

    def _nap_du_lieu(self):
        try:
            du_lieu = self.bo_luu_tru.doc_json("du_an.json")
            if not isinstance(du_lieu, list):
                return []
            danh_sach = []
            for item in du_lieu:
                if isinstance(item, dict):
                    da = DuAn.from_dict(item)
                    if da is not None:
                        danh_sach.append(da)
            return danh_sach
        except Exception as loi:
            logger.error(f"Lỗi khi nạp dữ liệu dự án: {loi}")
            return []

    def luu_du_lieu(self):
        """Lưu toàn bộ danh sách dự án hiện tại xuống tầng lưu trữ."""
        du_lieu = [du_an.to_dict() for du_an in self.danh_sach_du_an]
        self.bo_luu_tru.ghi_json("du_an.json", du_lieu)
        return True

    def tao_du_an(self, ma_du_an: str, ten_du_an: str, danh_sach_cot=None):
        """Tạo mới một dự án, ném ngoại lệ nếu trùng mã hoặc lưu thất bại (kèm Rollback)."""
        if self.tim_du_an_theo_ma(ma_du_an) is not None:
            raise XungDotDuLieuError(
                f"Mã dự án '{ma_du_an}' đã tồn tại trong hệ thống",
                khoa_trung="ma_du_an",
                gia_tri=ma_du_an
            )

        du_an = DuAn(ma_du_an=ma_du_an, ten_du_an=ten_du_an, danh_sach_cot=danh_sach_cot)
        self.danh_sach_du_an.append(du_an)

        try:
            self.luu_du_lieu()
            logger.info(f"Đã tạo thành công dự án mới '{ma_du_an} - {ten_du_an}'")
            return du_an
        except Exception as err:
            self.danh_sach_du_an.remove(du_an)  # ROLLBACK
            logger.error(f"Rollback: Đã hủy dự án '{ma_du_an}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Tạo dự án thất bại do lỗi lưu trữ: {err}", loi_goc=err)

    def tim_du_an_theo_ma(self, ma_du_an: str):
        """Tìm kiếm dự án theo mã; nếu không có trả về None."""
        for du_an in self.danh_sach_du_an:
            if du_an.ma_du_an == ma_du_an:
                return du_an
        return None

    def tim_du_an_hoac_loi(self, ma_du_an: str) -> DuAn:
        """Tìm dự án theo mã, ném KhongTimThayError nếu không tìm thấy."""
        du_an = self.tim_du_an_theo_ma(ma_du_an)
        if du_an is None:
            raise KhongTimThayError(
                f"Không tìm thấy dự án có mã '{ma_du_an}'",
                loai_tai_nguyen="DuAn",
                khoa_tim_kiem=ma_du_an
            )
        return du_an

    def xoa_du_an(self, ma_du_an: str, nguoi_dung):
        """Xóa dự án khỏi hệ thống; chỉ quản trị viên có quyền (kèm Rollback)."""
        if nguoi_dung is None:
            raise KhongCoQuyenError("Bạn chưa đăng nhập", hanh_dong="XOA_DU_AN")

        if not getattr(nguoi_dung, "co_quyen_xoa_cong_viec", lambda: False)():
            raise KhongCoQuyenError(
                f"Người dùng '{getattr(nguoi_dung, 'ten_dang_nhap', '')}' không có quyền xóa dự án",
                nguoi_dung=getattr(nguoi_dung, "ten_dang_nhap", ""),
                hanh_dong="XOA_DU_AN"
            )

        du_an = self.tim_du_an_hoac_loi(ma_du_an)
        self.danh_sach_du_an.remove(du_an)

        try:
            self.luu_du_lieu()
            logger.info(f"Đã xóa thành công dự án '{ma_du_an}' khỏi hệ thống")
            return du_an
        except Exception as err:
            self.danh_sach_du_an.append(du_an)  # ROLLBACK
            logger.error(f"Rollback: Đã khôi phục dự án '{ma_du_an}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Xóa dự án thất bại: {err}", loi_goc=err)

    def them_thanh_vien_du_an(self, du_an: DuAn, ten_dang_nhap: str):
        """Thêm thành viên vào dự án và đồng bộ lưu trữ file (kèm Rollback)."""
        danh_sach_tv = self.bo_luu_tru.doc_danh_sach_thanh_vien()
        if not any(tv.ten_dang_nhap == ten_dang_nhap for tv in danh_sach_tv):
            raise KhongTimThayError(
                f"Không tìm thấy người dùng '{ten_dang_nhap}' trong hệ thống",
                loai_tai_nguyen="ThanhVien",
                khoa_tim_kiem=ten_dang_nhap
            )

        du_an.them_thanh_vien(ten_dang_nhap)

        try:
            self.luu_du_lieu()
            logger.info(f"Đã thêm thành viên '{ten_dang_nhap}' vào dự án '{du_an.ma_du_an}'")
            return True
        except Exception as err:
            du_an.xoa_thanh_vien(ten_dang_nhap)  # ROLLBACK
            logger.error(f"Rollback: Đã gỡ bỏ thành viên '{ten_dang_nhap}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Thêm thành viên vào dự án thất bại: {err}", loi_goc=err)

    def xoa_thanh_vien_du_an(self, du_an: DuAn, ten_dang_nhap: str):
        """Xóa thành viên khỏi dự án và đồng bộ lưu trữ file (kèm Rollback)."""
        du_an.xoa_thanh_vien(ten_dang_nhap)

        try:
            self.luu_du_lieu()
            logger.info(f"Đã xóa thành viên '{ten_dang_nhap}' khỏi dự án '{du_an.ma_du_an}'")
            return True
        except Exception as err:
            du_an.them_thanh_vien(ten_dang_nhap)  # ROLLBACK
            logger.error(f"Rollback: Đã khôi phục thành viên '{ten_dang_nhap}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Xóa thành viên khỏi dự án thất bại: {err}", loi_goc=err)
