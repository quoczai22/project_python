import hashlib
import hmac
import re
import secrets
from abc import ABC, abstractmethod
from exceptions import DuLieuKhongHopLeError, XacThucThatBaiError
from config import MAT_KHAU_TOI_THIEU

# Mật khẩu lưu dưới dạng "<salt 32 ký tự hex>$<sha256 64 ký tự hex>"
_MAU_MAT_KHAU_DA_BAM = re.compile(r"[0-9a-f]{32}\$[0-9a-f]{64}")


def bam_mat_khau(mat_khau, salt=None) -> str:
    """Băm mật khẩu bằng SHA-256 kèm salt ngẫu nhiên. Trả về chuỗi 'salt$hash'."""
    salt = salt or secrets.token_hex(16)
    ban_bam = hashlib.sha256((salt + str(mat_khau)).encode("utf-8")).hexdigest()
    return f"{salt}${ban_bam}"


def la_mat_khau_da_bam(gia_tri) -> bool:
    """True nếu chuỗi đã đúng định dạng 'salt$sha256' (tức không phải mật khẩu thô)."""
    return isinstance(gia_tri, str) and _MAU_MAT_KHAU_DA_BAM.fullmatch(gia_tri) is not None


def doi_chieu_mat_khau(mat_khau, chuoi_da_bam: str) -> bool:
    """So khớp mật khẩu nhập vào với chuỗi đã băm (so sánh thời gian không đổi)."""
    if not la_mat_khau_da_bam(chuoi_da_bam):
        return False
    salt = chuoi_da_bam.split("$", 1)[0]
    return hmac.compare_digest(bam_mat_khau(mat_khau, salt), chuoi_da_bam)


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

    def __init__(self, ten_dang_nhap, mat_khau, ho_ten="", email="", vai_tro="thanh_vien", da_bam=False):
        """
        da_bam=False: `mat_khau` là mật khẩu thô -> băm SHA-256 ngay khi tạo đối tượng.
        da_bam=True : `mat_khau` đã là chuỗi 'salt$hash' (đọc từ file) -> giữ nguyên, không băm lại.
        """
        self.ten_dang_nhap = ten_dang_nhap
        if da_bam:
            if not la_mat_khau_da_bam(mat_khau):
                raise DuLieuKhongHopLeError("Mật khẩu đã băm sai định dạng", truong_loi="mat_khau")
            self._mat_khau = str(mat_khau)
        else:
            self._mat_khau = bam_mat_khau(mat_khau)
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
        """Xác thực mật khẩu - so sánh bản băm SHA-256, không bao giờ giữ mật khẩu thô."""
        return doi_chieu_mat_khau(mat_khau, self._mat_khau)

    def doi_mat_khau(self, mat_khau_cu, mat_khau_moi):
        """Đổi mật khẩu an toàn, ném ngoại lệ nếu vi phạm."""
        if not self.kiem_tra_mat_khau(mat_khau_cu):
            raise XacThucThatBaiError("Mật khẩu cũ không chính xác")
        if not mat_khau_moi or len(str(mat_khau_moi)) < MAT_KHAU_TOI_THIEU:
            raise DuLieuKhongHopLeError(
                f"Mật khẩu mới phải có ít nhất {MAT_KHAU_TOI_THIEU} ký tự",
                truong_loi="mat_khau_moi"
            )
        self._mat_khau = bam_mat_khau(mat_khau_moi)
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
            "mat_khau": self._mat_khau,  # luôn là chuỗi đã băm salt$sha256
            "ho_ten": self.ho_ten,
            "email": self.email,
            "vai_tro": self.vai_tro
        }

    @classmethod
    def from_dict(cls, data):
        """Factory Method: Khởi tạo đúng loại người dùng (QuanTriVien hoặc ThanhVien)."""
        if not isinstance(data, dict):
            raise DuLieuKhongHopLeError("Dữ liệu người dùng phải là dictionary")
        mat_khau = data.get("mat_khau")
        if mat_khau is None or str(mat_khau) == "":
            raise DuLieuKhongHopLeError("Tài khoản thiếu mật khẩu", truong_loi="mat_khau")
        # File cũ có thể còn mật khẩu thô -> băm ngay khi nạp; file mới đã là 'salt$hash'.
        da_bam = la_mat_khau_da_bam(mat_khau)
        vai_tro = data.get("vai_tro", "thanh_vien")
        if vai_tro == "quan_tri":
            from .QuanTriVien import QuanTriVien
            return QuanTriVien(
                ten_dang_nhap=data.get("ten_dang_nhap"),
                mat_khau=mat_khau,
                ho_ten=data.get("ho_ten", ""),
                email=data.get("email", ""),
                da_bam=da_bam
            )
        from .ThanhVien import ThanhVien
        return ThanhVien(
            ten_dang_nhap=data.get("ten_dang_nhap"),
            mat_khau=mat_khau,
            ho_ten=data.get("ho_ten", ""),
            email=data.get("email", ""),
            da_bam=da_bam
        )

    def __str__(self):
        return f"{self.__class__.__name__}(ten_dang_nhap='{self.ten_dang_nhap}', vai_tro='{self.vai_tro}')"

    def __repr__(self):
        return self.__str__()
