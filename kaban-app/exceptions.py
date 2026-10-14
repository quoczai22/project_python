class KanbanException(Exception):
    """Lớp cơ sở trừu tượng cho toàn bộ ngoại lệ trong hệ thống Kanban."""
    def __init__(self, thong_diep: str, ma_loi: str = "KANBAN_ERROR", chi_tiet: dict = None):
        super().__init__(thong_diep)
        self.thong_diep = thong_diep
        self.ma_loi = ma_loi
        self.chi_tiet = chi_tiet or {}

    def to_dict(self):
        """Chuyển đổi ngoại lệ thành dictionary phù hợp cho phản hồi API/Backend."""
        return {
            "thanh_cong": False,
            "ma_loi": self.ma_loi,
            "thong_diep": self.thong_diep,
            "chi_tiet": self.chi_tiet
        }

    def __str__(self):
        return f"[{self.ma_loi}] {self.thong_diep}"


class DuLieuKhongHopLeError(KanbanException):
    """Ngoại lệ khi dữ liệu đầu vào vi phạm quy tắc validation (Validation Error)."""
    def __init__(self, thong_diep: str, truong_loi: str = None, gia_tri=None):
        chi_tiet = {}
        if truong_loi:
            chi_tiet["truong_loi"] = truong_loi
        if gia_tri is not None:
            chi_tiet["gia_tri"] = str(gia_tri)
        super().__init__(thong_diep, ma_loi="VALIDATION_ERROR", chi_tiet=chi_tiet)


class KhongTimThayError(KanbanException):
    """Ngoại lệ khi không tìm thấy tài nguyên (Not Found Error: Dự án, Công việc, Thành viên)."""
    def __init__(self, thong_diep: str, loai_tai_nguyen: str = None, khoa_tim_kiem=None):
        chi_tiet = {}
        if loai_tai_nguyen:
            chi_tiet["loai_tai_nguyen"] = loai_tai_nguyen
        if khoa_tim_kiem is not None:
            chi_tiet["khoa_tim_kiem"] = str(khoa_tim_kiem)
        super().__init__(thong_diep, ma_loi="NOT_FOUND", chi_tiet=chi_tiet)


class KhongCoQuyenError(KanbanException):
    """Ngoại lệ khi người dùng không đủ quyền thực hiện hành động (Permission/Authorization Error)."""
    def __init__(self, thong_diep: str, nguoi_dung: str = None, hanh_dong: str = None):
        chi_tiet = {}
        if nguoi_dung:
            chi_tiet["nguoi_dung"] = nguoi_dung
        if hanh_dong:
            chi_tiet["hanh_dong"] = hanh_dong
        super().__init__(thong_diep, ma_loi="FORBIDDEN", chi_tiet=chi_tiet)


class XungDotDuLieuError(KanbanException):
    """Ngoại lệ khi dữ liệu bị xung đột hoặc trùng lặp (Conflict Error: Trùng ID, trùng tên)."""
    def __init__(self, thong_diep: str, khoa_trung: str = None, gia_tri=None):
        chi_tiet = {}
        if khoa_trung:
            chi_tiet["khoa_trung"] = khoa_trung
        if gia_tri is not None:
            chi_tiet["gia_tri"] = str(gia_tri)
        super().__init__(thong_diep, ma_loi="DATA_CONFLICT", chi_tiet=chi_tiet)


class XacThucThatBaiError(KanbanException):
    """Ngoại lệ khi xác thực thông tin đăng nhập thất bại (Authentication Error)."""
    def __init__(self, thong_diep: str = "Tên đăng nhập hoặc mật khẩu không chính xác"):
        super().__init__(thong_diep, ma_loi="UNAUTHORIZED")


class LoiLuuTruError(KanbanException):
    """Ngoại lệ khi thao tác với tầng lưu trữ thất bại (Storage/IO Error)."""
    def __init__(self, thong_diep: str, ten_nguon: str = None, loi_goc: Exception = None):
        chi_tiet = {}
        if ten_nguon:
            chi_tiet["ten_nguon"] = ten_nguon
        if loi_goc:
            chi_tiet["chi_tiet_loi"] = str(loi_goc)
        super().__init__(thong_diep, ma_loi="STORAGE_ERROR", chi_tiet=chi_tiet)
