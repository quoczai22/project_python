from .CongViecBase import CongViec


class CongViecThuong(CongViec):
    """
    Lớp công việc thông thường.
    
    1. TÍNH KẾ THỪA (Inheritance):
       - Kế thừa toàn bộ thuộc tính, phương thức quản lý trạng thái, hạn chót từ lớp cha CongViec.
       - Tái sử dụng hàm khởi tạo của lớp cha qua `super().__init__(...)`.
       
    2. TÍNH ĐA HÌNH (Polymorphism):
       - Cài đặt (override) phương thức `canh_bao()` và `lay_loai_cong_viec()`.
       - Hành vi cảnh báo được tùy biến theo mức độ của một công việc thông thường.
    """

    def __init__(self, ma_cong_viec, tieu_de, mo_ta, nguoi_phu_trach,
                 ngay_bat_dau, ngay_ket_thuc, trang_thai="Cần làm",
                 muc_uu_tien="Trung bình", nhan="Backend", danh_sach_binh_luan=None):
        super().__init__(
            ma_cong_viec=ma_cong_viec,
            tieu_de=tieu_de,
            mo_ta=mo_ta,
            nguoi_phu_trach=nguoi_phu_trach,
            ngay_bat_dau=ngay_bat_dau,
            ngay_ket_thuc=ngay_ket_thuc,
            trang_thai=trang_thai,
            muc_uu_tien=muc_uu_tien,
            nhan=nhan,
            danh_sach_binh_luan=danh_sach_binh_luan
        )

    def lay_loai_cong_viec(self) -> str:
        return "Công việc thường"

    def canh_bao(self) -> str:
        """ĐA HÌNH: Cảnh báo mức độ thông thường."""
        if self.da_qua_han():
            return "Công việc đã quá hạn hoàn thành!"
        ngay_con_lai = self.tinh_ngay_con_lai()
        if ngay_con_lai is None:
            return "Chưa xác định thời hạn"
        return f"Còn {ngay_con_lai} ngày để hoàn thành công việc"
