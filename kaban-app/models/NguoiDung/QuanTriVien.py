from .NguoiDungBase import NguoiDung


class QuanTriVien(NguoiDung):
    """
    Lớp Quản trị viên hệ thống.
    KẾ THỪA (Inheritance) từ NguoiDung và cài đặt phương thức ĐA HÌNH (Polymorphism) toàn quyền.
    """

    def __init__(self, ten_dang_nhap, mat_khau, ho_ten="", email="", vai_tro="quan_tri", da_bam=False):
        super().__init__(ten_dang_nhap, mat_khau, ho_ten, email, vai_tro="quan_tri", da_bam=da_bam)

    def kiem_tra_quyen_du_an(self, du_an) -> bool:
        """ĐA HÌNH: Quản trị viên có toàn quyền truy cập mọi dự án."""
        return True

    def kiem_tra_quyen_cong_viec(self, cong_viec) -> bool:
        """ĐA HÌNH: Quản trị viên có toàn quyền thao tác trên mọi công việc."""
        return True

    def co_quyen_xoa_cong_viec(self) -> bool:
        """ĐA HÌNH: Quản trị viên có quyền xóa công việc."""
        return True
