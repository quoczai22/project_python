from datetime import datetime
from models.DuAn import DuAn
from models.CongViec import CongViec, CongViecKhan, CongViecThuong
from models.BinhLuan import BinhLuan
from exceptions import (
    DuLieuKhongHopLeError,
    KhongTimThayError,
    KhongCoQuyenError,
    LoiLuuTruError
)
from logger import logger


class CongViecService:
    """
    Dịch vụ quản lý các thao tác trên công việc Kanban (CRUD, chuyển cột, bình luận, lọc).
    Tích hợp cơ chế Rollback đảm bảo tính toàn vẹn dữ liệu.
    """

    def __init__(self, du_an_service, xac_thuc_service, bo_luu_tru):
        self.du_an_service = du_an_service
        self.xac_thuc_service = xac_thuc_service
        self.bo_luu_tru = bo_luu_tru

    def tao_cong_viec(self, du_an: DuAn, du_lieu: dict, la_cong_viec_khan: bool = False):
        """Tạo mới công việc kèm kiểm tra quyền, validation và Rollback nếu lưu lỗi."""
        self.xac_thuc_service.kiem_tra_quyen_du_an(du_an, bat_loi=True)

        if not isinstance(du_lieu, dict):
            raise DuLieuKhongHopLeError("Dữ liệu công việc phải là dictionary")

        ma_cong_viec = du_lieu.get("ma_cong_viec", du_lieu.get("MaCongViec"))
        tieu_de = du_lieu.get("tieu_de", du_lieu.get("TieuDe"))
        mo_ta = du_lieu.get("mo_ta", du_lieu.get("MoTa", ""))
        nguoi_phu_trach = du_lieu.get("nguoi_phu_trach", du_lieu.get("NguoiPhuTrach"))
        ngay_bat_dau = du_lieu.get("ngay_bat_dau", du_lieu.get("NgayBatDau"))
        ngay_ket_thuc = du_lieu.get("ngay_ket_thuc", du_lieu.get("NgayKetThuc"))
        trang_thai = du_lieu.get("trang_thai", du_lieu.get("TrangThai", "Cần làm"))
        muc_uu_tien = du_lieu.get("muc_uu_tien", du_lieu.get("MucUuTien", "Trung bình"))
        nhan = du_lieu.get("nhan", du_lieu.get("Nhan", "Backend"))

        if la_cong_viec_khan or muc_uu_tien == "Khẩn":
            cv = CongViecKhan(
                ma_cong_viec=ma_cong_viec,
                tieu_de=tieu_de,
                mo_ta=mo_ta,
                nguoi_phu_trach=nguoi_phu_trach,
                ngay_bat_dau=ngay_bat_dau,
                ngay_ket_thuc=ngay_ket_thuc,
                trang_thai=trang_thai,
                nhan=nhan
            )
        else:
            cv = CongViecThuong(
                ma_cong_viec=ma_cong_viec,
                tieu_de=tieu_de,
                mo_ta=mo_ta,
                nguoi_phu_trach=nguoi_phu_trach,
                ngay_bat_dau=ngay_bat_dau,
                ngay_ket_thuc=ngay_ket_thuc,
                trang_thai=trang_thai,
                muc_uu_tien=muc_uu_tien,
                nhan=nhan
            )

        du_an.them_cong_viec(cv)

        try:
            self.du_an_service.luu_du_lieu()
            logger.info(f"Đã thêm công việc '{cv.ma_cong_viec}' vào dự án '{du_an.ma_du_an}'")
            return cv
        except Exception as err:
            du_an.xoa_cong_viec(cv.ma_cong_viec)  # ROLLBACK
            logger.error(f"Rollback: Đã gỡ bỏ công việc '{cv.ma_cong_viec}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Không thể lưu công việc mới: {err}", loi_goc=err)

    def cap_nhat_cong_viec(self, du_an: DuAn, ma_cong_viec: str, du_lieu_moi: dict):
        """Cập nhật công việc, kiểm tra quyền và ROLLBACK snapshot nếu lưu file lỗi."""
        if du_an is None:
            raise DuLieuKhongHopLeError("Đối tượng dự án không được là None")

        cv = du_an.tim_cong_viec_theo_ma(ma_cong_viec)
        if cv is None:
            raise KhongTimThayError(
                f"Không tìm thấy công việc '{ma_cong_viec}' trong dự án '{du_an.ma_du_an}'",
                loai_tai_nguyen="CongViec",
                khoa_tim_kiem=ma_cong_viec
            )

        self.xac_thuc_service.kiem_tra_quyen_cong_viec(cv, bat_loi=True)

        snapshot_cu = cv.to_dict()
        cv.cap_nhat_cong_viec(du_lieu_moi)

        try:
            self.du_an_service.luu_du_lieu()
            logger.info(f"Đã cập nhật công việc '{ma_cong_viec}' thành công")
            return cv
        except Exception as err:
            cv.cap_nhat_cong_viec(snapshot_cu)  # ROLLBACK
            logger.error(f"Rollback: Đã khôi phục trạng thái cũ cho '{ma_cong_viec}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Cập nhật công việc thất bại: {err}", loi_goc=err)

    def xoa_cong_viec(self, du_an: DuAn, ma_cong_viec: str):
        """Xóa công việc khỏi dự án, kiểm tra quyền quản trị và ROLLBACK nếu lưu file lỗi."""
        if not self.xac_thuc_service.co_quyen_xoa():
            raise KhongCoQuyenError(
                "Chỉ quản trị viên mới có quyền xóa công việc",
                nguoi_dung=getattr(self.xac_thuc_service.nguoi_dung_hien_tai, "ten_dang_nhap", ""),
                hanh_dong="XOA_CONG_VIEC"
            )

        if du_an is None:
            raise DuLieuKhongHopLeError("Đối tượng dự án không được là None")

        cv_bi_xoa = du_an.xoa_cong_viec(ma_cong_viec)

        try:
            self.du_an_service.luu_du_lieu()
            logger.info(f"Đã xóa công việc '{ma_cong_viec}' khỏi dự án '{du_an.ma_du_an}'")
            return cv_bi_xoa
        except Exception as err:
            du_an.them_cong_viec(cv_bi_xoa)  # ROLLBACK
            logger.error(f"Rollback: Đã khôi phục công việc '{ma_cong_viec}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Xóa công việc thất bại: {err}", loi_goc=err)

    def chuyen_trang_thai(self, du_an: DuAn, ma_cong_viec: str, trang_thai_moi: str):
        """Chuyển cột Kanban, ghi nhật ký và ROLLBACK nếu lưu thất bại."""
        if du_an is None:
            raise DuLieuKhongHopLeError("Đối tượng dự án không được là None")

        cv = du_an.tim_cong_viec_theo_ma(ma_cong_viec)
        if cv is None:
            raise KhongTimThayError(f"Không tìm thấy công việc '{ma_cong_viec}'", loai_tai_nguyen="CongViec", khoa_tim_kiem=ma_cong_viec)

        self.xac_thuc_service.kiem_tra_quyen_cong_viec(cv, bat_loi=True)

        trang_thai_cu, trang_thai_cap_nhat = cv.chuyen_trang_thai(trang_thai_moi)

        ten_dang_nhap = getattr(self.xac_thuc_service.nguoi_dung_hien_tai, "ten_dang_nhap", "unknown")
        du_lieu_log = {
            "ten_dang_nhap": ten_dang_nhap,
            "thoi_gian": datetime.now().isoformat(),
            "ma_cong_viec": ma_cong_viec,
            "trang_thai_cu": trang_thai_cu,
            "trang_thai_moi": trang_thai_cap_nhat,
        }
        self.bo_luu_tru.ghi_nhat_ky(du_lieu_log)

        try:
            self.du_an_service.luu_du_lieu()
            logger.info(f"Đã chuyển công việc '{ma_cong_viec}' từ '{trang_thai_cu}' sang '{trang_thai_cap_nhat}'")
            return trang_thai_cu, trang_thai_cap_nhat
        except Exception as err:
            cv.trang_thai = trang_thai_cu  # ROLLBACK
            logger.error(f"Rollback: Đã phục hồi trạng thái cũ cho '{ma_cong_viec}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Chuyển trạng thái thất bại: {err}", loi_goc=err)

    def them_binh_luan_cong_viec(self, du_an: DuAn, ma_cong_viec: str, noi_dung: str):
        """Thêm bình luận vào công việc; kiểm tra quyền và Rollback nếu lưu lỗi."""
        self.xac_thuc_service.kiem_tra_quyen_du_an(du_an, bat_loi=True)

        cv = du_an.tim_cong_viec_theo_ma(ma_cong_viec)
        if cv is None:
            raise KhongTimThayError(
                f"Không tìm thấy công việc '{ma_cong_viec}' trong dự án '{du_an.ma_du_an}'",
                loai_tai_nguyen="CongViec",
                khoa_tim_kiem=ma_cong_viec
            )

        nguoi_gui = getattr(self.xac_thuc_service.nguoi_dung_hien_tai, "ten_dang_nhap", "")
        bl = BinhLuan(nguoi_gui=nguoi_gui, noi_dung=noi_dung)
        cv.them_binh_luan(bl)

        try:
            self.du_an_service.luu_du_lieu()
            logger.info(f"Người dùng '{bl.nguoi_gui}' đã bình luận trên công việc '{ma_cong_viec}'")
            return bl
        except Exception as err:
            cv.xoa_binh_luan(bl.ma_binh_luan)  # ROLLBACK
            logger.error(f"Rollback: Đã gỡ bỏ bình luận '{bl.ma_binh_luan}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Thêm bình luận thất bại: {err}", loi_goc=err)

    def xoa_binh_luan_cong_viec(self, du_an: DuAn, ma_cong_viec: str, ma_binh_luan: str):
        """Xóa bình luận khỏi công việc (người tạo hoặc quản trị viên có quyền)."""
        self.xac_thuc_service.kiem_tra_quyen_du_an(du_an, bat_loi=True)

        cv = du_an.tim_cong_viec_theo_ma(ma_cong_viec)
        if cv is None:
            raise KhongTimThayError(f"Không tìm thấy công việc '{ma_cong_viec}'", loai_tai_nguyen="CongViec", khoa_tim_kiem=ma_cong_viec)

        bl = next((b for b in cv.danh_sach_binh_luan if b.ma_binh_luan == ma_binh_luan), None)
        if bl is None:
            raise KhongTimThayError(f"Không tìm thấy bình luận '{ma_binh_luan}'", loai_tai_nguyen="BinhLuan", khoa_tim_kiem=ma_binh_luan)

        nguoi_hien_tai = getattr(self.xac_thuc_service.nguoi_dung_hien_tai, "ten_dang_nhap", "")
        if bl.nguoi_gui != nguoi_hien_tai and not self.xac_thuc_service.co_quyen_xoa():
            raise KhongCoQuyenError(
                f"Người dùng '{nguoi_hien_tai}' không có quyền xóa bình luận này",
                nguoi_dung=nguoi_hien_tai,
                hanh_dong="XOA_BINH_LUAN"
            )

        bl_bi_xoa = cv.xoa_binh_luan(ma_binh_luan)

        try:
            self.du_an_service.luu_du_lieu()
            logger.info(f"Đã xóa bình luận '{ma_binh_luan}' khỏi công việc '{ma_cong_viec}'")
            return bl_bi_xoa
        except Exception as err:
            cv.them_binh_luan(bl_bi_xoa)  # ROLLBACK
            logger.error(f"Rollback: Đã khôi phục bình luận '{ma_binh_luan}' do lỗi lưu trữ: {err}")
            raise LoiLuuTruError(f"Xóa bình luận thất bại: {err}", loi_goc=err)

    def tim_kiem_cong_viec(self, du_an: DuAn, tu_khoa: str):
        """Tìm kiếm công việc theo từ khóa tiêu đề hoặc mã việc trong dự án."""
        if du_an is None or not hasattr(du_an, "danh_sach_cong_viec"):
            return []

        if not tu_khoa or not str(tu_khoa).strip():
            return list(du_an.danh_sach_cong_viec)

        tu_khoa_str = str(tu_khoa).lower().strip()
        return [
            cv for cv in du_an.danh_sach_cong_viec
            if tu_khoa_str in str(cv.tieu_de or "").lower()
            or tu_khoa_str in str(cv.ma_cong_viec or "").lower()
        ]

    def loc_theo_thanh_vien(self, du_an: DuAn, ten_dang_nhap: str):
        """Lọc danh sách công việc theo tên người phụ trách trong dự án."""
        if du_an is None or not hasattr(du_an, "danh_sach_cong_viec") or not ten_dang_nhap:
            return []

        user_str = str(ten_dang_nhap).strip().lower()
        return [
            cv for cv in du_an.danh_sach_cong_viec
            if str(cv.nguoi_phu_trach or "").strip().lower() == user_str
        ]

    def loc_theo_nhan(self, du_an: DuAn, ten_nhan: str):
        """Lọc danh sách công việc theo nhãn trong dự án."""
        if du_an is None or not hasattr(du_an, "danh_sach_cong_viec") or not ten_nhan:
            return []

        return [
            cv for cv in du_an.danh_sach_cong_viec
            if cv.nhan == ten_nhan
        ]

    def loc_theo_muc_uu_tien(self, du_an: DuAn, muc_uu_tien: str):
        """Lọc danh sách công việc theo mức ưu tiên trong dự án."""
        if du_an is None or not hasattr(du_an, "danh_sach_cong_viec") or not muc_uu_tien:
            return []

        return [
            cv for cv in du_an.danh_sach_cong_viec
            if cv.muc_uu_tien == muc_uu_tien
        ]
