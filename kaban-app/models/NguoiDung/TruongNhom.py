from .ThanhVien import ThanhVien


class TruongNhom(ThanhVien):
    """Leader chỉ quản lý thành viên trong nhóm được gán ở từng dự án."""

    def __init__(self, ten_dang_nhap, mat_khau, ho_ten="", email="", da_bam=False):
        super().__init__(ten_dang_nhap, mat_khau, ho_ten, email, da_bam=da_bam)
        self._vai_tro = "truong_nhom"
