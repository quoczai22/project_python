from abc import ABC, abstractmethod
from exceptions import DuLieuKhongHopLeError, XacThucThatBaiError


class NguoiDung(ABC):
    """
    Lớp cơ sở trừu tượng đại diện cho một người dùng trong hệ thống.
    
    1. TÍNH TRỪU TƯỢNG (Abstraction):
       - Định nghĩa giao diện chung cho người dùng và các quyền hạn.
       - Các phương thức trừu tượng: `kiem_tra_quyen_du_an`, `kiem_tra_quyen_cong_viec`, `co_quyen_xoa_cong_viec`.
       
    2. TÍNH ĐÓNG GÓI & XỬ LÝ LỖI (Encapsulation & Error Handling):
       - Mật khẩu và thông tin được đóng gói nội bộ, không phơi bày trực tiếp.
       - Phương thức xác thực `kiem_tra_mat_khau()` và đổi mật khẩu an toàn ném ngoại lệ chuẩn.
    """

    def __init__(self, ten_dang_nhap, mat_khau, ho_ten="", email="", vai_tro="thanh_vien"):
        self.ten_dang_nhap = ten_dang_nhap
        self._mat_khau = str(mat_khau)
        self.ho_ten = ho_ten
        self.email = email
        self._vai_tro = vai_tro

    # ==================== ĐÓNG GÓI THUỘC TÍNH ====================
    @property
    def ten_dang_nhap(self):
        return getattr(self, "_ten_dang_nhap", "")

    @ten_dang_nhap.setter
    def ten_dang_nhap(self, value):
        if not value or not str(value).strip():
            raise DuLieuKhongHopLeError("Tên đăng nhập không được để trống", truong_loi="ten_dang_nhap")
        self._ten_dang_nhap = str(value).strip()

    @property
    def ho_ten(self):
        return getattr(self, "_ho_ten", "")

    @ho_ten.setter
    def ho_ten(self, value):
        self._ho_ten = str(value).strip() if value else ""

    @property
    def email(self):
        return getattr(self, "_email", "")

    @email.setter
    def email(self, value):
        self._email = str(value).strip() if value else ""

    @property
    def vai_tro(self):
        return self._vai_tro

    def kiem_tra_mat_khau(self, mat_khau):
        """Xác thực mật khẩu - Đóng gói logic bảo mật."""
        return self._mat_khau == str(mat_khau)

    def doi_mat_khau(self, mat_khau_cu, mat_khau_moi):
        """Đổi mật khẩu an toàn, ném ngoại lệ nếu vi phạm."""
        if not self.kiem_tra_mat_khau(mat_khau_cu):
            raise XacThucThatBaiError("Mật khẩu cũ không chính xác")
        if not mat_khau_moi or len(str(mat_khau_moi)) < 6:
            raise DuLieuKhongHopLeError(
                "Mật khẩu mới phải có ít nhất 6 ký tự",
                truong_loi="mat_khau_moi"
            )
        self._mat_khau = str(mat_khau_moi)
        return True

    # ==================== TÍNH TRỪU TƯỢNG & ĐA HÌNH ====================
    @abstractmethod
    def kiem_tra_quyen_du_an(self, du_an) -> bool:
        """Kiểm tra quyền truy cập dự án."""
        pass

    @abstractmethod
    def kiem_tra_quyen_cong_viec(self, cong_viec) -> bool:
        """Kiểm tra quyền thao tác trên công việc."""
        pass

    @abstractmethod
    def co_quyen_xoa_cong_viec(self) -> bool:
        """Kiểm tra quyền được xóa công việc khỏi dự án."""
        pass

    def to_dict(self):
        return {
            "ten_dang_nhap": self.ten_dang_nhap,
            "mat_khau": self._mat_khau,
            "ho_ten": self.ho_ten,
            "email": self.email,
            "vai_tro": self.vai_tro
        }

    @classmethod
    def from_dict(cls, data):
        """Factory Method: Khởi tạo đúng loại người dùng (QuanTriVien hoặc ThanhVien)."""
        if not isinstance(data, dict):
            raise DuLieuKhongHopLeError("Dữ liệu người dùng phải là dictionary")
        vai_tro = data.get("vai_tro", "thanh_vien")
        if vai_tro == "quan_tri":
            from .QuanTriVien import QuanTriVien
            return QuanTriVien(
                ten_dang_nhap=data.get("ten_dang_nhap"),
                mat_khau=data.get("mat_khau"),
                ho_ten=data.get("ho_ten", ""),
                email=data.get("email", "")
            )
        from .ThanhVien import ThanhVien
        return ThanhVien(
            ten_dang_nhap=data.get("ten_dang_nhap"),
            mat_khau=data.get("mat_khau"),
            ho_ten=data.get("ho_ten", ""),
            email=data.get("email", "")
        )

    def __str__(self):
        return f"{self.__class__.__name__}(ten_dang_nhap='{self.ten_dang_nhap}', vai_tro='{self.vai_tro}')"

    def __repr__(self):
        return self.__str__()
