import re
from datetime import datetime
from config import TRANG_THAI_HOP_LE

class DuAn:
    def __init__(self, ma_du_an, ten_du_an, danh_sach_cot=None, thanh_vien_tham_gia=None, danh_sach_cong_viec=None, ngay_tao=None):
        self.ma_du_an = ma_du_an
        self.ten_du_an = ten_du_an
        self.danh_sach_cot = danh_sach_cot if danh_sach_cot is not None else list(TRANG_THAI_HOP_LE)
        self.thanh_vien_tham_gia = thanh_vien_tham_gia if thanh_vien_tham_gia is not None else []
        self.danh_sach_cong_viec = danh_sach_cong_viec if danh_sach_cong_viec is not None else []
        self.ngay_tao = ngay_tao if ngay_tao is not None else datetime.now().strftime("%Y-%m-%d")
        
    def __str__(self):
        return f"DuAn(MaDuAn={self.ma_du_an}, TenDuAn={self.ten_du_an}, DanhSachCot={self.danh_sach_cot}, ThanhVienThamGia={self.thanh_vien_tham_gia}, DanhSachCongViec={self.danh_sach_cong_viec}, NgayTao={self.ngay_tao})"
    
    def __repr__(self):
        return self.__str__()

    @property
    def ma_du_an(self):
        return getattr(self, "_ma_du_an", None)

    @ma_du_an.setter
    def ma_du_an(self, ma_du_an):
        if not ma_du_an or not re.match(r"^DA-\d{3,}$", str(ma_du_an)):
            print(f"Mã dự án {ma_du_an} sai định dạng (VD: DA-001)")
            self._ma_du_an = None
            return
        self._ma_du_an = str(ma_du_an)

    @property
    def ten_du_an(self):
        return getattr(self, "_ten_du_an", None)

    @ten_du_an.setter
    def ten_du_an(self, ten_du_an):
        if not ten_du_an or not str(ten_du_an).strip():
            print("Tên dự án không được để trống")
            self._ten_du_an = ""
            return
        self._ten_du_an = str(ten_du_an).strip()
    
    @property
    def ngay_tao(self):
        return getattr(self, "_ngay_tao", None)

    @ngay_tao.setter
    def ngay_tao(self, ngay_tao):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngay_tao)):
                print("Ngày tạo phải có dạng YYYY-MM-DD")
                self._ngay_tao = None
                return
            datetime.strptime(str(ngay_tao), "%Y-%m-%d")
            self._ngay_tao = str(ngay_tao)
        except ValueError as loi:
            print(f"Ngày tạo không hợp lệ: {loi}")
            self._ngay_tao = None

    @property
    def thanh_vien_tham_gia(self):
        return getattr(self, "_thanh_vien_tham_gia", None)

    @thanh_vien_tham_gia.setter
    def thanh_vien_tham_gia(self, thanh_vien_tham_gia):
        if not isinstance(thanh_vien_tham_gia, list):
            print("Danh sách thành viên phải là list")
            self._thanh_vien_tham_gia = []
            return
        if any(not isinstance(thanh_vien, str) or not thanh_vien.strip()
               for thanh_vien in thanh_vien_tham_gia):
            print("Mỗi thành viên phải là tên đăng nhập không rỗng")
            self._thanh_vien_tham_gia = []
            return
        if len(thanh_vien_tham_gia) != len(set(thanh_vien_tham_gia)):
            print("Danh sách thành viên không được trùng")
            self._thanh_vien_tham_gia = []
            return
        self._thanh_vien_tham_gia = thanh_vien_tham_gia

    @property
    def danh_sach_cong_viec(self):
        return getattr(self, "_danh_sach_cong_viec", None)

    @danh_sach_cong_viec.setter
    def danh_sach_cong_viec(self, danh_sach_cong_viec):
        if not isinstance(danh_sach_cong_viec, list):
            print("Danh sách công việc phải là list")
            self._danh_sach_cong_viec = []
            return
        self._danh_sach_cong_viec = danh_sach_cong_viec

    @property
    def cong_viec(self):
        return self.danh_sach_cong_viec


    @property
    def danh_sach_cot(self):
        return getattr(self, "_danh_sach_cot", None)

    @danh_sach_cot.setter
    def danh_sach_cot(self, danh_sach_cot):
        if not isinstance(danh_sach_cot, list) or not danh_sach_cot:
            print("Danh sách cột phải là list không rỗng")
            self._danh_sach_cot = list(TRANG_THAI_HOP_LE)
            return
        if len(danh_sach_cot) != len(set(danh_sach_cot)):
            print("Danh sách cột không được trùng")
            self._danh_sach_cot = list(TRANG_THAI_HOP_LE)
            return
        if any(cot not in TRANG_THAI_HOP_LE for cot in danh_sach_cot):
            print("Danh sách cột có trạng thái không hợp lệ")
            self._danh_sach_cot = list(TRANG_THAI_HOP_LE)
            return
        self._danh_sach_cot = danh_sach_cot

    def them_cong_viec(self, cong_viec):
        """Thêm công việc vào dự án, kiểm tra trùng mã."""
        from models.CongViec import CongViec

        if not isinstance(cong_viec, CongViec):
            print("Công việc phải là object CongViec")
            return False

        if self.tim_cong_viec_theo_ma(cong_viec.ma_cong_viec) is not None:
            print(f"Mã công việc '{cong_viec.ma_cong_viec}' đã tồn tại")
            return False
        self._danh_sach_cong_viec.append(cong_viec)
        return True

    def xoa_cong_viec(self, ma_cong_viec):
        """Xóa công việc theo mã; trả về True nếu tìm thấy và xóa thành công."""
        cong_viec = self.tim_cong_viec_theo_ma(ma_cong_viec)
        if cong_viec is None:
            return False
        self._danh_sach_cong_viec.remove(cong_viec)
        return True

    def tim_cong_viec_theo_ma(self, ma_cong_viec):
        """Tìm và trả về công việc theo mã; không có thì trả về None."""
        for cong_viec in self._danh_sach_cong_viec:
            if cong_viec.ma_cong_viec == ma_cong_viec:
                return cong_viec
        return None

    def them_thanh_vien(self, ten_dang_nhap):
        """Thêm username thành viên vào dự án."""
        if not isinstance(ten_dang_nhap, str) or not ten_dang_nhap.strip():
            print("Tên đăng nhập không được để trống")
            return False
        if ten_dang_nhap in self._thanh_vien_tham_gia:
            print(f"Thành viên '{ten_dang_nhap}' đã có trong dự án")
            return False
        self._thanh_vien_tham_gia.append(ten_dang_nhap)
        return True

    def xoa_thanh_vien(self, ten_dang_nhap):
        """Xóa username khỏi dự án; trả về True nếu tìm thấy và xóa thành công."""
        if ten_dang_nhap not in self._thanh_vien_tham_gia:
            return False
        self._thanh_vien_tham_gia.remove(ten_dang_nhap)
        return True

    def lay_cong_viec_theo_trang_thai(self, trang_thai):
        """Lấy các công việc đang thuộc một cột Kanban."""
        if trang_thai not in self.danh_sach_cot:
            print(f"Trạng thái '{trang_thai}' không thuộc dự án")
            return []
        return [
            cong_viec for cong_viec in self._danh_sach_cong_viec
            if cong_viec.trang_thai == trang_thai
        ]

    def to_dict(self):
        """Chuyển dự án thành dictionary để lưu JSON."""
        return {
            "MaDuAn": self.ma_du_an,
            "TenDuAn": self.ten_du_an,
            "DanhSachCot": self.danh_sach_cot,
            "ThanhVienThamGia": self.thanh_vien_tham_gia,
            "DanhSachCongViec": [
                cong_viec.to_dict() for cong_viec in self.danh_sach_cong_viec
            ],
            "NgayTao": self.ngay_tao,
        }

    @classmethod
    def from_dict(cls, data):
        """Tạo dự án và các object công việc từ dữ liệu JSON """
        if not isinstance(data, dict):
            print("Dữ liệu dự án phải là dictionary")
            return None

        from models.CongViec import CongViec

        du_lieu_cong_viec = data.get("DanhSachCongViec", [])
        if not isinstance(du_lieu_cong_viec, list):
            print("DanhSachCongViec trong JSON phải là list")
            return None

        return cls(
            ma_du_an=data.get("MaDuAn"),
            ten_du_an=data.get("TenDuAn"),
            danh_sach_cot=data.get("DanhSachCot"),
            thanh_vien_tham_gia=data.get("ThanhVienThamGia", []),
            danh_sach_cong_viec=[
                CongViec.from_dict(cong_viec)
                for cong_viec in du_lieu_cong_viec
            ],
            ngay_tao=data.get("NgayTao"),
        )
