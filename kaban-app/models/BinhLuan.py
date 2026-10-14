from datetime import datetime
import re
from exceptions import DuLieuKhongHopLeError


class BinhLuan:
    """
    Model Bình Luận (Comments) trên thẻ công việc Kanban.
    
    TÍNH ĐÓNG GÓI & XỬ LÝ LỖI (Encapsulation & Error Handling):
    - Đóng gói thông tin bình luận (_ma_binh_luan, _nguoi_gui, _noi_dung, _thoi_gian).
    - Validation dữ liệu: người gửi và nội dung không được để trống.
    """

    def __init__(self, nguoi_gui: str, noi_dung: str, ma_binh_luan: str = None, thoi_gian: str = None):
        self.ma_binh_luan = ma_binh_luan or f"BL-{int(datetime.now().timestamp() * 1000) % 1000000:06d}"
        self.nguoi_gui = nguoi_gui
        self.noi_dung = noi_dung
        self.thoi_gian = thoi_gian or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ==================== GETTER / SETTER VALIDATION ====================
    @property
    def ma_binh_luan(self):
        return getattr(self, "_ma_binh_luan", "")

    @ma_binh_luan.setter
    def ma_binh_luan(self, value):
        if not value or not str(value).strip():
            raise DuLieuKhongHopLeError("Mã bình luận không được để trống", truong_loi="ma_binh_luan")
        self._ma_binh_luan = str(value).strip()

    @property
    def nguoi_gui(self):
        return getattr(self, "_nguoi_gui", "")

    @nguoi_gui.setter
    def nguoi_gui(self, value):
        if not value or not str(value).strip():
            raise DuLieuKhongHopLeError("Người gửi bình luận không được để trống", truong_loi="nguoi_gui")
        self._nguoi_gui = str(value).strip()

    @property
    def noi_dung(self):
        return getattr(self, "_noi_dung", "")

    @noi_dung.setter
    def noi_dung(self, value):
        if not value or not str(value).strip():
            raise DuLieuKhongHopLeError("Nội dung bình luận không được để trống", truong_loi="noi_dung")
        self._noi_dung = str(value).strip()

    @property
    def thoi_gian(self):
        return getattr(self, "_thoi_gian", "")

    @thoi_gian.setter
    def thoi_gian(self, value):
        self._thoi_gian = str(value) if value else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """Chuyển đổi thành dictionary để lưu trữ JSON."""
        return {
            "MaBinhLuan": self.ma_binh_luan,
            "NguoiGui": self.nguoi_gui,
            "NoiDung": self.noi_dung,
            "ThoiGian": self.thoi_gian
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Khởi tạo đối tượng BinhLuan từ dictionary."""
        if not isinstance(data, dict):
            raise DuLieuKhongHopLeError("Dữ liệu bình luận phải là dictionary")
        return cls(
            ma_binh_luan=data.get("MaBinhLuan"),
            nguoi_gui=data.get("NguoiGui"),
            noi_dung=data.get("NoiDung"),
            thoi_gian=data.get("ThoiGian")
        )

    def __str__(self):
        return f"[{self.thoi_gian}] {self.nguoi_gui}: {self.noi_dung}"

    def __repr__(self):
        return f"BinhLuan(Ma='{self.ma_binh_luan}', NguoiGui='{self.nguoi_gui}', ThoiGian='{self.thoi_gian}')"
