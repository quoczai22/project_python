from .NguoiDungBase import NguoiDung


class ThanhVien(NguoiDung):
    """
    Lớp thành viên thông thường trong dự án.
    KẾ THỪA (Inheritance) từ NguoiDung và cài đặt phương thức ĐA HÌNH (Polymorphism).
    """

    def __init__(self, ten_dang_nhap, mat_khau, ho_ten="", email="", vai_tro="thanh_vien", da_bam=False):
        super().__init__(ten_dang_nhap, mat_khau, ho_ten, email, vai_tro="thanh_vien", da_bam=da_bam)

    def kiem_tra_quyen_du_an(self, du_an) -> bool:
        """ĐA HÌNH: Chỉ có quyền nếu tên đăng nhập nằm trong danh sách thành viên tham gia."""
        if du_an is None:
            return False
        thanh_vien_tham_gia = getattr(du_an, "thanh_vien_tham_gia", []) or []
        return self.ten_dang_nhap in thanh_vien_tham_gia

    def kiem_tra_quyen_cong_viec(self, cong_viec) -> bool:
        """ĐA HÌNH: Thành viên chỉ được thao tác trên công việc được phân công cho mình."""
        if cong_viec is None:
            return False
        return getattr(cong_viec, "nguoi_phu_trach", None) == self.ten_dang_nhap

    def co_quyen_xoa_cong_viec(self) -> bool:
        """ĐA HÌNH: Thành viên thường không có quyền xóa công việc."""
        return False
