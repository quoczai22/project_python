class ThanhVien:
    """Model thành viên / người dùng hệ thống."""
    def __init__(self, ten_dang_nhap, mat_khau, ho_ten="", email="", vai_tro="thanh_vien"):
        self.ten_dang_nhap = ten_dang_nhap
        self.mat_khau = mat_khau
        self.ho_ten = ho_ten
        self.email = email
        self.vai_tro = vai_tro

    def __str__(self):
        return f"ThanhVien(ten_dang_nhap='{self.ten_dang_nhap}', vai_tro='{self.vai_tro}')"

    def __repr__(self):
        return self.__str__()

    def kiem_tra_mat_khau(self, mat_khau):
        return self.mat_khau == mat_khau

    def to_dict(self):
        return {
            "ten_dang_nhap": self.ten_dang_nhap,
            "mat_khau": self.mat_khau,
            "ho_ten": self.ho_ten,
            "email": self.email,
            "vai_tro": self.vai_tro
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return None
        return cls(
            ten_dang_nhap=data.get("ten_dang_nhap"),
            mat_khau=data.get("mat_khau"),
            ho_ten=data.get("ho_ten", ""),
            email=data.get("email", ""),
            vai_tro=data.get("vai_tro", "thanh_vien")
        )
