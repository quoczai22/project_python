from .CongViecThuong import CongViecThuong


class CongViecKhan(CongViecThuong):
    """Công việc ưu tiên khẩn, cảnh báo hạn chót sớm hơn việc thường."""

    def __init__(self, ma_cong_viec, tieu_de, mo_ta, nguoi_phu_trach, ngay_bat_dau, ngay_ket_thuc, trang_thai="Cần làm", nhan="Backend"):
        # Công việc thuộc class này luôn có mức ưu tiên Khẩn.
        super().__init__(ma_cong_viec, tieu_de, mo_ta, nguoi_phu_trach, ngay_bat_dau, ngay_ket_thuc, trang_thai, "Khẩn", nhan)

    def canh_bao(self):
        if self.da_qua_han():
            return "QUÁ HẠN - CẦN XỬ LÝ NGAY"
    
        so_ngay = self.tinh_ngay_con_lai()
        if so_ngay is None:
            return None

        if so_ngay <= 1:
            return "KHẨN CẤP - HẠN CHÓT CÒN RẤT ÍT"

        if so_ngay <= 3:
            return "CẢNH BÁO ĐỎ - SẮP ĐẾN HẠN"

        return "Công việc khẩn đang trong hạn"
