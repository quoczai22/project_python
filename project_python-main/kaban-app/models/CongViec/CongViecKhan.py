from .CongViecBase import CongViec
from exceptions import DuLieuKhongHopLeError


class CongViecKhan(CongViec):
    """
    Lớp công việc khẩn cấp.
    
    1. TÍNH KẾ THỪA (Inheritance):
       - Kế thừa toàn bộ logic từ CongViec.
       - Tái sử dụng `super().__init__(...)`.
       
    2. TÍNH ĐÓNG GÓI & XỬ LÝ LỖI (Encapsulation & Error Handling):
       - Đóng gói thuộc tính `muc_uu_tien`: Luôn luôn là 'Khẩn'.
       - Nếu cố tình đổi sang mức khác ngoài 'Khẩn', ném ngoại lệ DuLieuKhongHopLeError.
         
    3. TÍNH ĐA HÌNH (Polymorphism):
       - Ghi đè (override) phương thức `canh_bao()` với các cấp độ báo động nghiêm ngặt
         (QUÁ HẠN, KHẨN CẤP, CẢNH BÁO ĐỎ).
    """

    def __init__(self, ma_cong_viec, tieu_de, mo_ta, nguoi_phu_trach,
                 ngay_bat_dau, ngay_ket_thuc, trang_thai="Cần làm",
                 nhan="Backend", danh_sach_binh_luan=None):
        super().__init__(
            ma_cong_viec=ma_cong_viec,
            tieu_de=tieu_de,
            mo_ta=mo_ta,
            nguoi_phu_trach=nguoi_phu_trach,
            ngay_bat_dau=ngay_bat_dau,
            ngay_ket_thuc=ngay_ket_thuc,
            trang_thai=trang_thai,
            muc_uu_tien="Khẩn",
            nhan=nhan,
            danh_sach_binh_luan=danh_sach_binh_luan
        )

    @CongViec.muc_uu_tien.setter
    def muc_uu_tien(self, muc_uu_tien):
        if muc_uu_tien != "Khẩn":
            raise DuLieuKhongHopLeError(
                f"Không thể đổi mức ưu tiên '{muc_uu_tien}' cho Công Việc Khẩn (bắt buộc phải là 'Khẩn')",
                truong_loi="muc_uu_tien",
                gia_tri=muc_uu_tien
            )
        self._muc_uu_tien = "Khẩn"

    def lay_loai_cong_viec(self) -> str:
        return "Công việc khẩn"

    def canh_bao(self) -> str:
        """ĐA HÌNH: Cảnh báo mức độ khẩn cấp."""
        if self.da_qua_han():
            return "QUÁ HẠN - CẦN XỬ LÝ NGAY"

        so_ngay = self.tinh_ngay_con_lai()
        if so_ngay is None:
            return "Chưa xác định thời hạn"

        if so_ngay <= 1:
            return "KHẨN CẤP - HẠN CHÓT CÒN RẤT ÍT"

        if so_ngay <= 3:
            return "CẢNH BÁO ĐỎ - SẮP ĐẾN HẠN"

        return "Công việc khẩn đang trong hạn"
