from datetime import datetime
import re
from config import NHAN_HOP_LE, MUC_UU_TIEN_HOP_LE, TRANG_THAI_HOP_LE

class CongViecThuong:
    def __init__(self, maCongViec, tieuDe, moTa, nguoiPhuTrach, ngayBatDau, ngayKetThuc, trangThai, mucUuTien, nhan):
        self.MaCongViec = maCongViec
        self.TieuDe = tieuDe
        self.MoTa = moTa
        self.NguoiPhuTrach = nguoiPhuTrach
        self.NgayBatDau = ngayBatDau
        self.NgayKetThuc = ngayKetThuc
        self.TrangThai = trangThai
        self.MucUuTien = mucUuTien
        self.Nhan = nhan  # Lọc công việc theo nhãn

    def __str__(self):  # Chuyển thành dạng chuỗi
        return f"CongViec(MaCongViec={self.MaCongViec}, TieuDe={self.TieuDe}, MoTa={self.MoTa}, NguoiPhuTrach={self.NguoiPhuTrach}, NgayBatDau={self.NgayBatDau}, NgayKetThuc={self.NgayKetThuc}, TrangThai={self.TrangThai}, MucUuTien={self.MucUuTien}, Nhan={self.Nhan})"

    def __repr__(self): #return ra object
        return self.__str__()

    # Getter / Setter 
    @property
    def MaCongViec(self):
        return getattr(self, "_maCongViec", None)

    @MaCongViec.setter
    def MaCongViec(self, maCongViec):
        if not maCongViec or not re.match(r"^CV-\d{3,}$", str(maCongViec)):
            print(f"Mã công việc {maCongViec} sai định dạng (VD: CV-001)")
            self._maCongViec = None
            return
        self._maCongViec = str(maCongViec)

    @property
    def TieuDe(self):
        return getattr(self, "_tieuDe", None)

    @TieuDe.setter
    def TieuDe(self, tieuDe):
        if not tieuDe or not str(tieuDe).strip():
            print("Tiêu đề không được để trống")
            self._tieuDe = ""
            return
        self._tieuDe = str(tieuDe).strip()

    @property
    def MoTa(self):
        return getattr(self, "_moTa", "")

    @MoTa.setter
    def MoTa(self, moTa):
        self._moTa = moTa if moTa else ""

    @property
    def NguoiPhuTrach(self):
        return getattr(self, "_nguoiPhuTrach", None)

    @NguoiPhuTrach.setter
    def NguoiPhuTrach(self, nguoiPhuTrach):
        if not nguoiPhuTrach or not str(nguoiPhuTrach).strip():
            print("Người phụ trách không được để trống")
            self._nguoiPhuTrach = ""
            return
        self._nguoiPhuTrach = str(nguoiPhuTrach).strip()

    @property
    def NgayBatDau(self):
        return getattr(self, "_ngayBatDau", None)

    @NgayBatDau.setter
    def NgayBatDau(self, ngayBatDau):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngayBatDau)):
                print("Ngày bắt đầu phải có dạng YYYY-MM-DD")
                self._ngayBatDau = None
                return
            datetime.strptime(str(ngayBatDau), "%Y-%m-%d")
            self._ngayBatDau = str(ngayBatDau)
        except ValueError as loi:
            print(f"Ngày bắt đầu không hợp lệ: {loi}")
            self._ngayBatDau = None

    @property
    def NgayKetThuc(self):
        return getattr(self, "_ngayKetThuc", None)

    @NgayKetThuc.setter
    def NgayKetThuc(self, ngayKetThuc):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngayKetThuc)):
                print("Ngày kết thúc phải có dạng YYYY-MM-DD")
                self._ngayKetThuc = None
                return

            ngay_ket_thuc = datetime.strptime(
                str(ngayKetThuc), "%Y-%m-%d"
            ).date()

            if hasattr(self, "_ngayBatDau"):
                ngay_bat_dau = datetime.strptime(
                    self._ngayBatDau, "%Y-%m-%d"
                ).date()
                if ngay_ket_thuc < ngay_bat_dau:
                    print("Ngày kết thúc không được trước ngày bắt đầu")
                    self._ngayKetThuc = None
                    return

            self._ngayKetThuc = str(ngayKetThuc)
        except ValueError as loi:
            print(f"Ngày kết thúc không hợp lệ: {loi}")
            self._ngayKetThuc = None

    @property
    def TrangThai(self):
        return getattr(self, "_trangThai", "Cần làm")

    @TrangThai.setter
    def TrangThai(self, trangThai):
        if trangThai not in TRANG_THAI_HOP_LE:
            print("Trạng thái không hợp lệ. Giá trị hợp lệ: "
                  + ", ".join(TRANG_THAI_HOP_LE))
            self._trangThai = TRANG_THAI_HOP_LE[0]
            return
        self._trangThai = trangThai

    @property
    def MucUuTien(self):
        return getattr(self, "_mucUuTien", "Trung bình")

    @MucUuTien.setter
    def MucUuTien(self, mucUuTien):
        if mucUuTien not in MUC_UU_TIEN_HOP_LE:
            print("Mức ưu tiên không hợp lệ. Giá trị hợp lệ: "
                  + ", ".join(MUC_UU_TIEN_HOP_LE))
            self._mucUuTien = "Trung bình"
            return
        self._mucUuTien = mucUuTien

    @property
    def Nhan(self):
        return getattr(self, "_nhan", None)

    @Nhan.setter
    def Nhan(self, nhan):
        if nhan not in NHAN_HOP_LE:
            print("Nhãn không hợp lệ. Giá trị hợp lệ: "
                  + ", ".join(NHAN_HOP_LE))
            self._nhan = NHAN_HOP_LE[0]
            return
        self._nhan = nhan

    def CapNhatCongViec(self, data):
        if not isinstance(data, dict):
            print("Dữ liệu cập nhật không hợp lệ")
            return
        self.TieuDe = data.get("TieuDe", self.TieuDe)
        self.MoTa = data.get("MoTa", self.MoTa)
        self.NguoiPhuTrach = data.get("NguoiPhuTrach", self.NguoiPhuTrach)
        self.NgayBatDau = data.get("NgayBatDau", self.NgayBatDau)
        self.NgayKetThuc = data.get("NgayKetThuc", self.NgayKetThuc)
        self.TrangThai = data.get("TrangThai", self.TrangThai)
        self.MucUuTien = data.get("MucUuTien", self.MucUuTien)
        self.Nhan = data.get("Nhan", self.Nhan)

    def toDict(self):
        return {
            "LoaiCongViec": self.__class__.__name__,
            "MaCongViec": self.MaCongViec,
            "TieuDe": self.TieuDe,
            "MoTa": self.MoTa,
            "NguoiPhuTrach": self.NguoiPhuTrach,
            "NgayBatDau": self.NgayBatDau,
            "NgayKetThuc": self.NgayKetThuc,
            "TrangThai": self.TrangThai,
            "MucUuTien": self.MucUuTien,
            "Nhan": self.Nhan
        }

    @classmethod #tạo 1 object từ dict
    def fromDict(cls, data): 
        if not isinstance(data, dict):
            print("Dữ liệu công việc phải là dictionary")
            return None

        if (data.get("LoaiCongViec") == "CongViecKhan"
                or data.get("MucUuTien") == "Khẩn"):
            # Import cục bộ để tránh vòng lặp import giữa hai class.
            from .CongViecKhan import CongViecKhan
            return CongViecKhan(
                maCongViec=data.get("MaCongViec"),
                tieuDe=data.get("TieuDe"),
                moTa=data.get("MoTa", ""),
                nguoiPhuTrach=data.get("NguoiPhuTrach"),
                ngayBatDau=data.get("NgayBatDau"),
                ngayKetThuc=data.get("NgayKetThuc"),
                trangThai=data.get("TrangThai", "Cần làm"),
                nhan=data.get("Nhan")
            )

        return cls(
            maCongViec=data.get("MaCongViec"),
            tieuDe=data.get("TieuDe"),
            moTa=data.get("MoTa", ""),
            nguoiPhuTrach=data.get("NguoiPhuTrach"),
            ngayBatDau=data.get("NgayBatDau"),
            ngayKetThuc=data.get("NgayKetThuc"),
            trangThai=data.get("TrangThai", "Cần làm"),
            mucUuTien=data.get("MucUuTien", "Trung bình"),
            nhan=data.get("Nhan")
        )

    def ChuyenTrangThai(self, trangThaiMoi):
        trangThaiCu = self.TrangThai
        self.TrangThai = trangThaiMoi
        print(f"Đã chuyển {self.MaCongViec} từ {trangThaiCu} sang {trangThaiMoi}")
        return trangThaiCu,trangThaiMoi

    def TinhNgayConLai(self):
        if not self.NgayKetThuc:
            return None

        homNay=datetime.now().date()
        ketThuc=datetime.strptime(self.NgayKetThuc,"%Y-%m-%d").date()
        soNgay=(ketThuc-homNay).days
        return soNgay

    def TinhNgayDaQua(self):
        if not self.NgayBatDau:
            return None
         
        homNay=datetime.now().date()
        batDau=datetime.strptime(self.NgayBatDau,"%Y-%m-%d").date()
        soNgay=(homNay-batDau).days
        return soNgay

    def CanhBao(self):
        ngayConLai=self.TinhNgayConLai()
        if ngayConLai is None:
            return None
        return f"Còn {ngayConLai} ngày để hoàn thành công việc"

    def DaQuaHan(self):
        ngayConLai=self.TinhNgayConLai()
        return ngayConLai is not None and ngayConLai<0
    
    def IsHoanThanh(self):
        return self.TrangThai.lower() == "hoàn thành"


