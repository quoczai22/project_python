from datetime import datetime
import re
from config import NHAN_HOP_LE, MUC_UU_TIEN_HOP_LE, TRANG_THAI_HOP_LE

class CongViecThuong:
    def __init__(self, ma_cong_viec, tieu_de, mo_ta, nguoi_phu_trach, ngay_bat_dau, ngay_ket_thuc, trang_thai, muc_uu_tien, nhan):
        self.ma_cong_viec = ma_cong_viec
        self.tieu_de = tieu_de
        self.mo_ta = mo_ta
        self.nguoi_phu_trach = nguoi_phu_trach
        self.ngay_bat_dau = ngay_bat_dau
        self.ngay_ket_thuc = ngay_ket_thuc
        self.trang_thai = trang_thai
        self.muc_uu_tien = muc_uu_tien
        self.nhan = nhan  # Lọc công việc theo nhãn

    def __str__(self):  # Chuyển thành dạng chuỗi
        return f"CongViec(MaCongViec={self.ma_cong_viec}, TieuDe={self.tieu_de}, MoTa={self.mo_ta}, NguoiPhuTrach={self.nguoi_phu_trach}, NgayBatDau={self.ngay_bat_dau}, NgayKetThuc={self.ngay_ket_thuc}, TrangThai={self.trang_thai}, MucUuTien={self.muc_uu_tien}, Nhan={self.nhan})"

    def __repr__(self): #return ra object
        return self.__str__()

    # Getter / Setter 
    @property
    def ma_cong_viec(self):
        return getattr(self, "_ma_cong_viec", None)

    @ma_cong_viec.setter
    def ma_cong_viec(self, ma_cong_viec):
        if not ma_cong_viec or not re.match(r"^CV-\d{3,}$", str(ma_cong_viec)):
            print(f"Mã công việc {ma_cong_viec} sai định dạng (VD: CV-001)")
            self._ma_cong_viec = None
            return
        self._ma_cong_viec = str(ma_cong_viec)

    @property
    def tieu_de(self):
        return getattr(self, "_tieu_de", None)

    @tieu_de.setter
    def tieu_de(self, tieu_de):
        if not tieu_de or not str(tieu_de).strip():
            print("Tiêu đề không được để trống")
            self._tieu_de = ""
            return
        self._tieu_de = str(tieu_de).strip()

    @property
    def mo_ta(self):
        return getattr(self, "_mo_ta", "")

    @mo_ta.setter
    def mo_ta(self, mo_ta):
        self._mo_ta = mo_ta if mo_ta else ""

    @property
    def nguoi_phu_trach(self):
        return getattr(self, "_nguoi_phu_trach", None)

    @nguoi_phu_trach.setter
    def nguoi_phu_trach(self, nguoi_phu_trach):
        if not nguoi_phu_trach or not str(nguoi_phu_trach).strip():
            print("Người phụ trách không được để trống")
            self._nguoi_phu_trach = ""
            return
        self._nguoi_phu_trach = str(nguoi_phu_trach).strip()

    @property
    def ngay_bat_dau(self):
        return getattr(self, "_ngay_bat_dau", None)

    @ngay_bat_dau.setter
    def ngay_bat_dau(self, ngay_bat_dau):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngay_bat_dau)):
                print("Ngày bắt đầu phải có dạng YYYY-MM-DD")
                self._ngay_bat_dau = None
                return
            datetime.strptime(str(ngay_bat_dau), "%Y-%m-%d")
            self._ngay_bat_dau = str(ngay_bat_dau)
        except ValueError as loi:
            print(f"Ngày bắt đầu không hợp lệ: {loi}")
            self._ngay_bat_dau = None

    @property
    def ngay_ket_thuc(self):
        return getattr(self, "_ngay_ket_thuc", None)

    @ngay_ket_thuc.setter
    def ngay_ket_thuc(self, ngay_ket_thuc):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngay_ket_thuc)):
                print("Ngày kết thúc phải có dạng YYYY-MM-DD")
                self._ngay_ket_thuc = None
                return

            ngay_ket_thuc_val = datetime.strptime(
                str(ngay_ket_thuc), "%Y-%m-%d"
            ).date()

            if hasattr(self, "_ngay_bat_dau"):
                ngay_bat_dau_val = datetime.strptime(
                    self._ngay_bat_dau, "%Y-%m-%d"
                ).date()
                if ngay_ket_thuc_val < ngay_bat_dau_val:
                    print("Ngày kết thúc không được trước ngày bắt đầu")
                    self._ngay_ket_thuc = None
                    return

            self._ngay_ket_thuc = str(ngay_ket_thuc)
        except ValueError as loi:
            print(f"Ngày kết thúc không hợp lệ: {loi}")
            self._ngay_ket_thuc = None

    @property
    def trang_thai(self):
        return getattr(self, "_trang_thai", "Cần làm")

    @trang_thai.setter
    def trang_thai(self, trang_thai):
        if trang_thai not in TRANG_THAI_HOP_LE:
            print("Trạng thái không hợp lệ. Giá trị hợp lệ: "
                  + ", ".join(TRANG_THAI_HOP_LE))
            self._trang_thai = TRANG_THAI_HOP_LE[0]
            return
        self._trang_thai = trang_thai

    @property
    def muc_uu_tien(self):
        return getattr(self, "_muc_uu_tien", "Trung bình")

    @muc_uu_tien.setter
    def muc_uu_tien(self, muc_uu_tien):
        if muc_uu_tien not in MUC_UU_TIEN_HOP_LE:
            print("Mức ưu tiên không hợp lệ. Giá trị hợp lệ: "
                  + ", ".join(MUC_UU_TIEN_HOP_LE))
            self._muc_uu_tien = "Trung bình"
            return
        self._muc_uu_tien = muc_uu_tien

    @property
    def nhan(self):
        return getattr(self, "_nhan", None)

    @nhan.setter
    def nhan(self, nhan):
        if nhan not in NHAN_HOP_LE:
            print("Nhãn không hợp lệ. Giá trị hợp lệ: "
                  + ", ".join(NHAN_HOP_LE))
            self._nhan = NHAN_HOP_LE[0]
            return
        self._nhan = nhan

    def cap_nhat_cong_viec(self, data):
        if not isinstance(data, dict):
            print("Dữ liệu cập nhật không hợp lệ")
            return
        self.tieu_de = data.get("TieuDe", self.tieu_de)
        self.mo_ta = data.get("MoTa", self.mo_ta)
        self.nguoi_phu_trach = data.get("NguoiPhuTrach", self.nguoi_phu_trach)
        self.ngay_bat_dau = data.get("NgayBatDau", self.ngay_bat_dau)
        self.ngay_ket_thuc = data.get("NgayKetThuc", self.ngay_ket_thuc)
        self.trang_thai = data.get("TrangThai", self.trang_thai)
        self.muc_uu_tien = data.get("MucUuTien", self.muc_uu_tien)
        self.nhan = data.get("Nhan", self.nhan)

    def to_dict(self):
        return {
            "LoaiCongViec": self.__class__.__name__,
            "MaCongViec": self.ma_cong_viec,
            "TieuDe": self.tieu_de,
            "MoTa": self.mo_ta,
            "NguoiPhuTrach": self.nguoi_phu_trach,
            "NgayBatDau": self.ngay_bat_dau,
            "NgayKetThuc": self.ngay_ket_thuc,
            "TrangThai": self.trang_thai,
            "MucUuTien": self.muc_uu_tien,
            "Nhan": self.nhan
        }

    @classmethod #tạo 1 object từ dict
    def from_dict(cls, data): 
        if not isinstance(data, dict):
            print("Dữ liệu công việc phải là dictionary")
            return None

        if (data.get("LoaiCongViec") == "CongViecKhan"
                or data.get("MucUuTien") == "Khẩn"):
            # Import cục bộ để tránh vòng lặp import giữa hai class.
            from .CongViecKhan import CongViecKhan
            return CongViecKhan(
                ma_cong_viec=data.get("MaCongViec"),
                tieu_de=data.get("TieuDe"),
                mo_ta=data.get("MoTa", ""),
                nguoi_phu_trach=data.get("NguoiPhuTrach"),
                ngay_bat_dau=data.get("NgayBatDau"),
                ngay_ket_thuc=data.get("NgayKetThuc"),
                trang_thai=data.get("TrangThai", "Cần làm"),
                nhan=data.get("Nhan")
            )

        return cls(
            ma_cong_viec=data.get("MaCongViec"),
            tieu_de=data.get("TieuDe"),
            mo_ta=data.get("MoTa", ""),
            nguoi_phu_trach=data.get("NguoiPhuTrach"),
            ngay_bat_dau=data.get("NgayBatDau"),
            ngay_ket_thuc=data.get("NgayKetThuc"),
            trang_thai=data.get("TrangThai", "Cần làm"),
            muc_uu_tien=data.get("MucUuTien", "Trung bình"),
            nhan=data.get("Nhan")
        )

    def chuyen_trang_thai(self, trang_thai_moi):
        trang_thai_cu = self.trang_thai
        self.trang_thai = trang_thai_moi
        print(f"Đã chuyển {self.ma_cong_viec} từ {trang_thai_cu} sang {trang_thai_moi}")
        return trang_thai_cu, trang_thai_moi

    def tinh_ngay_con_lai(self):
        if not self.ngay_ket_thuc:
            return None

        hom_nay=datetime.now().date()
        ket_thuc=datetime.strptime(self.ngay_ket_thuc,"%Y-%m-%d").date()
        so_ngay=(ket_thuc-hom_nay).days
        return so_ngay

    def tinh_ngay_da_qua(self):
        if not self.ngay_bat_dau:
            return None
         
        hom_nay=datetime.now().date()
        bat_dau=datetime.strptime(self.ngay_bat_dau,"%Y-%m-%d").date()
        so_ngay=(hom_nay-bat_dau).days
        return so_ngay

    def canh_bao(self):
        ngay_con_lai=self.tinh_ngay_con_lai()
        if ngay_con_lai is None:
            return None
        return f"Còn {ngay_con_lai} ngày để hoàn thành công việc"

    def da_qua_han(self):
        ngay_con_lai=self.tinh_ngay_con_lai()
        return ngay_con_lai is not None and ngay_con_lai<0
    
    def is_hoan_thanh(self):
        return self.trang_thai.lower() == "hoàn thành"


CongViec = CongViecThuong
