import re
from datetime import datetime
from config import TRANG_THAI_HOP_LE
from models.CongViec import CongViec
from exceptions import DuLieuKhongHopLeError, KhongTimThayError, XungDotDuLieuError


class DuAn:
    """
    Model Dự án trong hệ thống Kanban.
    
    TÍNH ĐÓNG GÓI & XỬ LÝ LỖI (Encapsulation & Error Handling):
    - Dữ liệu dự án (_ma_du_an, _ten_du_an, _danh_sach_cong_viec,...) được bảo vệ nội bộ.
    - Truy xuất và sửa đổi được kiểm soát thông qua @property và @setter.
    - Ném ngoại lệ chuẩn (DuLieuKhongHopLeError, XungDotDuLieuError, KhongTimThayError) khi gặp lỗi dữ liệu.
    """

    def __init__(self, ma_du_an, ten_du_an, danh_sach_cot=None, thanh_vien_tham_gia=None,
                 danh_sach_cong_viec=None, ngay_tao=None):
        self.ma_du_an = ma_du_an
        self.ten_du_an = ten_du_an
        self.danh_sach_cot = danh_sach_cot if danh_sach_cot is not None else list(TRANG_THAI_HOP_LE)
        self.thanh_vien_tham_gia = thanh_vien_tham_gia if thanh_vien_tham_gia is not None else []
        self.danh_sach_cong_viec = danh_sach_cong_viec if danh_sach_cong_viec is not None else []
        self.ngay_tao = ngay_tao if ngay_tao is not None else datetime.now().strftime("%Y-%m-%d")

    # ==================== ĐÓNG GÓI THUỘC TÍNH (PROPERTIES) ====================
    @property
    def ma_du_an(self):
        return getattr(self, "_ma_du_an", None)

    @ma_du_an.setter
    def ma_du_an(self, ma_du_an):
        if not ma_du_an or not re.match(r"^DA-\d{3,}$", str(ma_du_an)):
            raise DuLieuKhongHopLeError(
                f"Mã dự án '{ma_du_an}' sai định dạng. Yêu cầu định dạng 'DA-xxx' (VD: DA-001)",
                truong_loi="ma_du_an",
                gia_tri=ma_du_an
            )
        self._ma_du_an = str(ma_du_an)

    @property
    def ten_du_an(self):
        return getattr(self, "_ten_du_an", None)

    @ten_du_an.setter
    def ten_du_an(self, ten_du_an):
        if not ten_du_an or not str(ten_du_an).strip():
            raise DuLieuKhongHopLeError(
                "Tên dự án không được để trống",
                truong_loi="ten_du_an",
                gia_tri=ten_du_an
            )
        self._ten_du_an = str(ten_du_an).strip()

    @property
    def ngay_tao(self):
        return getattr(self, "_ngay_tao", None)

    @ngay_tao.setter
    def ngay_tao(self, ngay_tao):
        if not ngay_tao or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngay_tao)):
            raise DuLieuKhongHopLeError(
                f"Ngày tạo '{ngay_tao}' không hợp lệ. Yêu cầu định dạng YYYY-MM-DD",
                truong_loi="ngay_tao",
                gia_tri=ngay_tao
            )
        try:
            datetime.strptime(str(ngay_tao), "%Y-%m-%d")
        except ValueError as loi:
            raise DuLieuKhongHopLeError(
                f"Ngày tạo không hợp lệ trong lịch: {loi}",
                truong_loi="ngay_tao",
                gia_tri=ngay_tao
            )
        self._ngay_tao = str(ngay_tao)

    @property
    def thanh_vien_tham_gia(self):
        return getattr(self, "_thanh_vien_tham_gia", [])

    @thanh_vien_tham_gia.setter
    def thanh_vien_tham_gia(self, thanh_vien_tham_gia):
        if not isinstance(thanh_vien_tham_gia, list):
            raise DuLieuKhongHopLeError("Danh sách thành viên phải là list", truong_loi="thanh_vien_tham_gia")
        if any(not isinstance(tv, str) or not tv.strip() for tv in thanh_vien_tham_gia):
            raise DuLieuKhongHopLeError("Mỗi thành viên tham gia phải là tên đăng nhập không rỗng", truong_loi="thanh_vien_tham_gia")
        if len(thanh_vien_tham_gia) != len(set(thanh_vien_tham_gia)):
            raise DuLieuKhongHopLeError("Danh sách thành viên không được có phần tử trùng nhau", truong_loi="thanh_vien_tham_gia")
        self._thanh_vien_tham_gia = thanh_vien_tham_gia

    @property
    def danh_sach_cong_viec(self):
        return getattr(self, "_danh_sach_cong_viec", [])

    @danh_sach_cong_viec.setter
    def danh_sach_cong_viec(self, danh_sach_cong_viec):
        if not isinstance(danh_sach_cong_viec, list):
            raise DuLieuKhongHopLeError("Danh sách công việc phải là list", truong_loi="danh_sach_cong_viec")
        self._danh_sach_cong_viec = danh_sach_cong_viec

    @property
    def cong_viec(self):
        """Alias cho danh_sach_cong_viec để tương thích UI."""
        return self.danh_sach_cong_viec

    @property
    def danh_sach_cot(self):
        return getattr(self, "_danh_sach_cot", list(TRANG_THAI_HOP_LE))

    @danh_sach_cot.setter
    def danh_sach_cot(self, danh_sach_cot):
        if not isinstance(danh_sach_cot, list) or not danh_sach_cot:
            raise DuLieuKhongHopLeError("Danh sách cột trạng thái phải là list không rỗng", truong_loi="danh_sach_cot")
        if len(danh_sach_cot) != len(set(danh_sach_cot)):
            raise DuLieuKhongHopLeError("Danh sách cột không được trùng nhau", truong_loi="danh_sach_cot")
        if any(cot not in TRANG_THAI_HOP_LE for cot in danh_sach_cot):
            raise DuLieuKhongHopLeError("Danh sách cột chứa trạng thái không hợp lệ trong cấu hình", truong_loi="danh_sach_cot")
        self._danh_sach_cot = danh_sach_cot

    # ==================== PHƯƠNG THỨC NGHIỆP VỤ ĐÓNG GÓI ====================
    def them_cong_viec(self, cong_viec: CongViec):
        """Thêm công việc vào dự án, ném ngoại lệ nếu trùng mã hoặc sai kiểu."""
        if not isinstance(cong_viec, CongViec):
            raise DuLieuKhongHopLeError("Công việc thêm vào phải là đối tượng kế thừa từ CongViec")

        if self.tim_cong_viec_theo_ma(cong_viec.ma_cong_viec) is not None:
            raise XungDotDuLieuError(
                f"Mã công việc '{cong_viec.ma_cong_viec}' đã tồn tại trong dự án '{self.ma_du_an}'",
                khoa_trung="ma_cong_viec",
                gia_tri=cong_viec.ma_cong_viec
            )
        self._danh_sach_cong_viec.append(cong_viec)
        return True

    def xoa_cong_viec(self, ma_cong_viec: str):
        """Xóa công việc theo mã; ném KhongTimThayError nếu không tìm thấy."""
        cong_viec = self.tim_cong_viec_theo_ma(ma_cong_viec)
        if cong_viec is None:
            raise KhongTimThayError(
                f"Không tìm thấy công việc có mã '{ma_cong_viec}' trong dự án '{self.ma_du_an}'",
                loai_tai_nguyen="CongViec",
                khoa_tim_kiem=ma_cong_viec
            )
        self._danh_sach_cong_viec.remove(cong_viec)
        return cong_viec

    def tim_cong_viec_theo_ma(self, ma_cong_viec: str):
        """Tìm và trả về đối tượng công việc theo mã; nếu không có trả về None."""
        for cong_viec in self._danh_sach_cong_viec:
            if cong_viec.ma_cong_viec == ma_cong_viec:
                return cong_viec
        return None

    def them_thanh_vien(self, ten_dang_nhap: str):
        """Thêm username thành viên vào dự án."""
        if not isinstance(ten_dang_nhap, str) or not ten_dang_nhap.strip():
            raise DuLieuKhongHopLeError("Tên đăng nhập thành viên không được để trống", truong_loi="ten_dang_nhap")
        ten = ten_dang_nhap.strip()
        if ten in self._thanh_vien_tham_gia:
            raise XungDotDuLieuError(f"Thành viên '{ten}' đã có trong dự án '{self.ma_du_an}'", khoa_trung="ten_dang_nhap", gia_tri=ten)
        self._thanh_vien_tham_gia.append(ten)
        return True

    def xoa_thanh_vien(self, ten_dang_nhap: str):
        """Xóa username khỏi dự án."""
        ten = str(ten_dang_nhap).strip()
        if ten not in self._thanh_vien_tham_gia:
            raise KhongTimThayError(f"Thành viên '{ten}' không có trong dự án '{self.ma_du_an}'", loai_tai_nguyen="ThanhVien", khoa_tim_kiem=ten)
        self._thanh_vien_tham_gia.remove(ten)
        return True

    def lay_cong_viec_theo_trang_thai(self, trang_thai: str):
        """Lấy danh sách các công việc thuộc một cột trạng thái nhất định."""
        if trang_thai not in self.danh_sach_cot:
            raise DuLieuKhongHopLeError(f"Trạng thái '{trang_thai}' không nằm trong danh sách cột của dự án", truong_loi="trang_thai", gia_tri=trang_thai)
        return [
            cong_viec for cong_viec in self._danh_sach_cong_viec
            if cong_viec.trang_thai == trang_thai
        ]

    def tinh_tien_do(self):
        """Tính phần trăm tiến độ hoàn thành của dự án."""
        if not self._danh_sach_cong_viec:
            return 0.0
        so_luong_hoan_thanh = sum(
            1 for cv in self._danh_sach_cong_viec if cv.is_hoan_thanh()
        )
        return round((so_luong_hoan_thanh / len(self._danh_sach_cong_viec)) * 100, 2)

    def lay_danh_sach_canh_bao(self):
        """
        ĐA HÌNH: Lấy cảnh báo cho toàn bộ công việc trong dự án.
        Mỗi công việc (thường hoặc khẩn) tự động gọi phương thức `canh_bao()` của riêng nó.
        """
        ket_qua = []
        for cv in self._danh_sach_cong_viec:
            ket_qua.append({
                "ma_cong_viec": cv.ma_cong_viec,
                "tieu_de": cv.tieu_de,
                "loai": cv.lay_loai_cong_viec(),
                "canh_bao": cv.canh_bao()
            })
        return ket_qua

    def to_dict(self):
        """Chuyển đổi dự án thành dictionary để lưu trữ JSON."""
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
        """Tạo đối tượng dự án từ dictionary."""
        if not isinstance(data, dict):
            raise DuLieuKhongHopLeError("Dữ liệu dự án phải là dictionary")

        du_lieu_cong_viec = data.get("DanhSachCongViec", [])
        if not isinstance(du_lieu_cong_viec, list):
            raise DuLieuKhongHopLeError("DanhSachCongViec trong JSON phải là list", truong_loi="DanhSachCongViec")

        danh_sach_cv = []
        for cv_data in du_lieu_cong_viec:
            cv = CongViec.from_dict(cv_data)
            if cv is not None:
                danh_sach_cv.append(cv)

        return cls(
            ma_du_an=data.get("MaDuAn"),
            ten_du_an=data.get("TenDuAn"),
            danh_sach_cot=data.get("DanhSachCot"),
            thanh_vien_tham_gia=data.get("ThanhVienThamGia", []),
            danh_sach_cong_viec=danh_sach_cv,
            ngay_tao=data.get("NgayTao"),
        )

    def __str__(self):
        return (f"DuAn(MaDuAn={self.ma_du_an}, TenDuAn='{self.ten_du_an}', "
                f"SoLuongCongViec={len(self.danh_sach_cong_viec)}, TienDo={self.tinh_tien_do()}%)")

    def __repr__(self):
        return self.__str__()
