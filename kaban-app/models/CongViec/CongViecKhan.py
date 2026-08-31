from .CongViecThuong import CongViecThuong


class CongViecKhan(CongViecThuong):
    """Công việc ưu tiên khẩn, cảnh báo hạn chót sớm hơn việc thường."""

    def __init__(self, maCongViec, tieuDe, moTa, nguoiPhuTrach, ngayBatDau, ngayKetThuc, trangThai="Cần làm", mucUuTien="Khẩn", nhan="Backend"):
        super().__init__(maCongViec, tieuDe, moTa, nguoiPhuTrach, ngayBatDau, ngayKetThuc, trangThai, mucUuTien, nhan)

    def CanhBao(self):
        if self.DaQuaHan():
            return "QUÁ HẠN - CẦN XỬ LÝ NGAY"
    
        soNgay = self.TinhNgayConLai()
        if soNgay is None:
            return None

        if soNgay <= 1:
            return "KHẨN CẤP - HẠN CHÓT CÒN RẤT ÍT"

        if soNgay <= 3:
            return "CẢNH BÁO ĐỎ - SẮP ĐẾN HẠN"

        return "Công việc khẩn đang trong hạn"
