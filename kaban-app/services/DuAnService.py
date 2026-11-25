from models.DuAn import DuAn
from exceptions import XungDotDuLieuError, KhongTimThayError, LoiLuuTruError, KhongCoQuyenError, DuLieuKhongHopLeError
from logger import logger


class DuAnService:
    """
    Dịch vụ quản lý các thao tác CRUD và thành viên dự án.
    Tích hợp cơ chế Rollback đảm bảo tính toàn vẹn dữ liệu.
    """

    def __init__(self, bo_luu_tru, xac_thuc_service=None):
        self.bo_luu_tru = bo_luu_tru
        self.xac_thuc_service = xac_thuc_service
        self.danh_sach_du_an = self._nap_du_lieu()

    def _nap_du_lieu(self):
        try:
            ten_file = getattr(self.bo_luu_tru, "ten_file_du_an", "du_an.json")
            du_lieu = self.bo_luu_tru.doc_json(ten_file)
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
        ten_file = getattr(self.bo_luu_tru, "ten_file_du_an", "du_an.json")
        self.bo_luu_tru.ghi_json(ten_file, du_lieu)
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
        nd = getattr(self.xac_thuc_service, "nguoi_dung_hien_tai", None)
        la_leader = nd is not None and nd.vai_tro == "truong_nhom" and nd.ten_dang_nhap in du_an.nhom
        if nd is None or (nd.vai_tro != "quan_tri" and not la_leader):
            raise KhongCoQuyenError("Chỉ admin hoặc leader dự án được thêm thành viên")
        danh_sach_tv = self.bo_luu_tru.doc_danh_sach_thanh_vien()
        if not any(tv.ten_dang_nhap == ten_dang_nhap for tv in danh_sach_tv):
            raise KhongTimThayError(
                f"Không tìm thấy người dùng '{ten_dang_nhap}' trong hệ thống",
                loai_tai_nguyen="ThanhVien",
                khoa_tim_kiem=ten_dang_nhap
            )
        if la_leader and any(tv.ten_dang_nhap == ten_dang_nhap and tv.vai_tro == "truong_nhom"
                             for tv in danh_sach_tv):
            raise KhongCoQuyenError("Leader không được thêm Leader khác")

        du_an.them_thanh_vien(ten_dang_nhap)
        da_tung_roi = ten_dang_nhap in du_an.thanh_vien_da_roi
        if da_tung_roi:
            du_an.thanh_vien_da_roi.remove(ten_dang_nhap)
        if la_leader:
            du_an.nhom[nd.ten_dang_nhap].append(ten_dang_nhap)

        try:
            self.luu_du_lieu()
            self.bo_luu_tru.ghi_nhat_ky({"hanh_dong": "them_thanh_vien", "ma_du_an": du_an.ma_du_an,
                                        "ten_dang_nhap": nd.ten_dang_nhap, "thanh_vien": ten_dang_nhap})
            logger.info(f"Đã thêm thành viên '{ten_dang_nhap}' vào dự án '{du_an.ma_du_an}'")
            return True
        except Exception as err:
            du_an.xoa_thanh_vien(ten_dang_nhap)  # ROLLBACK
            if da_tung_roi:
                du_an.thanh_vien_da_roi.append(ten_dang_nhap)
            if la_leader:
                du_an.nhom[nd.ten_dang_nhap].remove(ten_dang_nhap)
            logger.error(f"Rollback: Đã gỡ bỏ thành viên '{ten_dang_nhap}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Thêm thành viên vào dự án thất bại: {err}", loi_goc=err)

    def xoa_thanh_vien_du_an(self, du_an: DuAn, ten_dang_nhap: str):
        """Xóa thành viên khỏi dự án và đồng bộ lưu trữ file (kèm Rollback)."""
        nguoi_dung = getattr(self.xac_thuc_service, "nguoi_dung_hien_tai", None)
        la_admin = nguoi_dung is not None and nguoi_dung.vai_tro == "quan_tri"
        la_leader_nhom = (nguoi_dung is not None and nguoi_dung.vai_tro == "truong_nhom" and
                          ten_dang_nhap in du_an.nhom.get(nguoi_dung.ten_dang_nhap, []))
        if not (la_admin or la_leader_nhom):
            raise KhongCoQuyenError("Không có quyền gỡ thành viên này", hanh_dong="XOA_THANH_VIEN")
        if ten_dang_nhap in du_an.nhom and du_an.nhom[ten_dang_nhap]:
            raise DuLieuKhongHopLeError("Phải chuyển thành viên trong nhóm trước khi gỡ leader")
        viec_chua_xong = [cv.ma_cong_viec for cv in du_an.cong_viec
                         if cv.nguoi_phu_trach == ten_dang_nhap and cv.trang_thai in ("Cần làm", "Đang làm", "Kiểm tra")]
        if viec_chua_xong:
            raise DuLieuKhongHopLeError(
                f"Cần bàn giao công việc chưa hoàn thành trước khi gỡ thành viên: {', '.join(viec_chua_xong)}",
                truong_loi="ten_dang_nhap", gia_tri=ten_dang_nhap)
        du_an.xoa_thanh_vien(ten_dang_nhap)
        da_co_trong_da_roi = ten_dang_nhap in du_an.thanh_vien_da_roi
        if not da_co_trong_da_roi:
            du_an.thanh_vien_da_roi.append(ten_dang_nhap)
        nhom_cu = {leader: list(ds) for leader, ds in du_an.nhom.items()}
        for ds in du_an.nhom.values():
            if ten_dang_nhap in ds:
                ds.remove(ten_dang_nhap)
        du_an.nhom.pop(ten_dang_nhap, None)

        try:
            self.luu_du_lieu()
            self.bo_luu_tru.ghi_nhat_ky({"hanh_dong": "go_thanh_vien", "ma_du_an": du_an.ma_du_an,
                                        "ten_dang_nhap": nguoi_dung.ten_dang_nhap, "thanh_vien": ten_dang_nhap})
            logger.info(f"Đã xóa thành viên '{ten_dang_nhap}' khỏi dự án '{du_an.ma_du_an}'")
            return True
        except Exception as err:
            du_an.them_thanh_vien(ten_dang_nhap)  # ROLLBACK
            du_an.nhom = nhom_cu
            if not da_co_trong_da_roi and ten_dang_nhap in du_an.thanh_vien_da_roi:
                du_an.thanh_vien_da_roi.remove(ten_dang_nhap)
            logger.error(f"Rollback: Đã khôi phục thành viên '{ten_dang_nhap}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Xóa thành viên khỏi dự án thất bại: {err}", loi_goc=err)
