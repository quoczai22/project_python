from abc import ABC, abstractmethod
from datetime import datetime
import re
from config import NHAN_HOP_LE, MUC_UU_TIEN_HOP_LE, TRANG_THAI_HOP_LE
from exceptions import DuLieuKhongHopLeError, KhongTimThayError


class CongViec(ABC):
    """
    Lớp cơ sở trừu tượng (Abstract Base Class) đại diện cho một công việc.
    
    1. TÍNH TRỪU TƯỢNG (Abstraction):
       - Định nghĩa giao diện chung cho mọi loại công việc qua abc.ABC.
       - Chứa các phương thức trừu tượng (@abstractmethod) như `canh_bao()` và `lay_loai_cong_viec()`.
       
    2. TÍNH ĐÓNG GÓI (Encapsulation) & XỬ LÝ LỖI (Error Handling):
       - Toàn bộ dữ liệu được lưu ở các biến nội bộ có tiền tố gạch dưới (_ma_cong_viec, _tieu_de,...).
       - Quản lý danh sách bình luận (BinhLuan) trên thẻ công việc.
       - Kiểm tra hợp lệ nghiêm ngặt và ném DuLieuKhongHopLeError.
    """

    def __init__(self, ma_cong_viec, tieu_de, mo_ta, nguoi_phu_trach,
                 ngay_bat_dau, ngay_ket_thuc, trang_thai="Cần làm",
                 muc_uu_tien="Trung bình", nhan="Backend", danh_sach_binh_luan=None):
        # Đóng gói: khởi tạo thông qua setters để kích hoạt validation
        self.ma_cong_viec = ma_cong_viec
        self.tieu_de = tieu_de
        self.mo_ta = mo_ta
        self.nguoi_phu_trach = nguoi_phu_trach
        self.ngay_bat_dau = ngay_bat_dau
        self.ngay_ket_thuc = ngay_ket_thuc
        self.trang_thai = trang_thai
        self.muc_uu_tien = muc_uu_tien
        self.nhan = nhan
        self.danh_sach_binh_luan = danh_sach_binh_luan if danh_sach_binh_luan is not None else []

    # ==================== ĐÓNG GÓI & VALIDATION (PROPERTIES) ====================
    @property
    def ma_cong_viec(self):
        return getattr(self, "_ma_cong_viec", None)

    @ma_cong_viec.setter
    def ma_cong_viec(self, ma_cong_viec):
        if not ma_cong_viec or not re.match(r"^CV-\d{3,}$", str(ma_cong_viec)):
            raise DuLieuKhongHopLeError(
                f"Mã công việc '{ma_cong_viec}' sai định dạng. Yêu cầu định dạng 'CV-xxx' (VD: CV-001)",
                truong_loi="ma_cong_viec",
                gia_tri=ma_cong_viec
            )
        self._ma_cong_viec = str(ma_cong_viec)

    @property
    def tieu_de(self):
        return getattr(self, "_tieu_de", "")

    @tieu_de.setter
    def tieu_de(self, tieu_de):
        if not tieu_de or not str(tieu_de).strip():
            raise DuLieuKhongHopLeError(
                "Tiêu đề công việc không được để trống",
                truong_loi="tieu_de",
                gia_tri=tieu_de
            )
        self._tieu_de = str(tieu_de).strip()

    @property
    def mo_ta(self):
        return getattr(self, "_mo_ta", "")

    @mo_ta.setter
    def mo_ta(self, mo_ta):
        self._mo_ta = str(mo_ta) if mo_ta is not None else ""

    @property
    def nguoi_phu_trach(self):
        return getattr(self, "_nguoi_phu_trach", "")

    @nguoi_phu_trach.setter
    def nguoi_phu_trach(self, nguoi_phu_trach):
        if not nguoi_phu_trach or not str(nguoi_phu_trach).strip():
            raise DuLieuKhongHopLeError(
                "Người phụ trách công việc không được để trống",
                truong_loi="nguoi_phu_trach",
                gia_tri=nguoi_phu_trach
            )
        self._nguoi_phu_trach = str(nguoi_phu_trach).strip()

    @property
    def ngay_bat_dau(self):
        return getattr(self, "_ngay_bat_dau", None)

    @ngay_bat_dau.setter
    def ngay_bat_dau(self, ngay_bat_dau):
        if not ngay_bat_dau or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngay_bat_dau)):
            raise DuLieuKhongHopLeError(
                f"Ngày bắt đầu '{ngay_bat_dau}' không hợp lệ. Yêu cầu định dạng YYYY-MM-DD",
                truong_loi="ngay_bat_dau",
                gia_tri=ngay_bat_dau
            )
        try:
            datetime.strptime(str(ngay_bat_dau), "%Y-%m-%d")
        except ValueError as loi:
            raise DuLieuKhongHopLeError(
                f"Ngày bắt đầu không tồn tại trong lịch: {loi}",
                truong_loi="ngay_bat_dau",
                gia_tri=ngay_bat_dau
            )
        self._ngay_bat_dau = str(ngay_bat_dau)

    @property
    def ngay_ket_thuc(self):
        return getattr(self, "_ngay_ket_thuc", None)

    @ngay_ket_thuc.setter
    def ngay_ket_thuc(self, ngay_ket_thuc):
        if not ngay_ket_thuc or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngay_ket_thuc)):
            raise DuLieuKhongHopLeError(
                f"Ngày kết thúc '{ngay_ket_thuc}' không hợp lệ. Yêu cầu định dạng YYYY-MM-DD",
                truong_loi="ngay_ket_thuc",
                gia_tri=ngay_ket_thuc
            )
        try:
            ngay_ket_thuc_val = datetime.strptime(str(ngay_ket_thuc), "%Y-%m-%d").date()
        except ValueError as loi:
            raise DuLieuKhongHopLeError(
                f"Ngày kết thúc không tồn tại trong lịch: {loi}",
                truong_loi="ngay_ket_thuc",
                gia_tri=ngay_ket_thuc
            )

        if hasattr(self, "_ngay_bat_dau") and self._ngay_bat_dau:
            ngay_bat_dau_val = datetime.strptime(self._ngay_bat_dau, "%Y-%m-%d").date()
            if ngay_ket_thuc_val < ngay_bat_dau_val:
                raise DuLieuKhongHopLeError(
                    f"Ngày kết thúc ({ngay_ket_thuc}) không được trước ngày bắt đầu ({self._ngay_bat_dau})",
                    truong_loi="ngay_ket_thuc",
                    gia_tri=ngay_ket_thuc
                )

        self._ngay_ket_thuc = str(ngay_ket_thuc)

    @property
    def trang_thai(self):
        return getattr(self, "_trang_thai", "Cần làm")

    @trang_thai.setter
    def trang_thai(self, trang_thai):
        if trang_thai not in TRANG_THAI_HOP_LE:
            raise DuLieuKhongHopLeError(
                f"Trạng thái '{trang_thai}' không hợp lệ. Giá trị hợp lệ: {', '.join(TRANG_THAI_HOP_LE)}",
                truong_loi="trang_thai",
                gia_tri=trang_thai
            )
        self._trang_thai = trang_thai

    @property
    def muc_uu_tien(self):
        return getattr(self, "_muc_uu_tien", "Trung bình")

    @muc_uu_tien.setter
    def muc_uu_tien(self, muc_uu_tien):
        if muc_uu_tien not in MUC_UU_TIEN_HOP_LE:
            raise DuLieuKhongHopLeError(
                f"Mức ưu tiên '{muc_uu_tien}' không hợp lệ. Giá trị hợp lệ: {', '.join(MUC_UU_TIEN_HOP_LE)}",
                truong_loi="muc_uu_tien",
                gia_tri=muc_uu_tien
            )
        self._muc_uu_tien = muc_uu_tien

    @property
    def nhan(self):
        return getattr(self, "_nhan", None)

    @nhan.setter
    def nhan(self, nhan):
        if nhan is not None and nhan not in NHAN_HOP_LE:
            raise DuLieuKhongHopLeError(
                f"Nhãn '{nhan}' không hợp lệ. Giá trị hợp lệ: {', '.join(NHAN_HOP_LE)}",
                truong_loi="nhan",
                gia_tri=nhan
            )
        self._nhan = nhan

    @property
    def danh_sach_binh_luan(self):
        return getattr(self, "_danh_sach_binh_luan", [])

    @danh_sach_binh_luan.setter
    def danh_sach_binh_luan(self, value):
        if not isinstance(value, list):
            raise DuLieuKhongHopLeError("Danh sách bình luận phải là list", truong_loi="danh_sach_binh_luan")
        self._danh_sach_binh_luan = value

    # ==================== PHƯƠNG THỨC BÌNH LUẬN ====================
    def them_binh_luan(self, binh_luan):
        """Thêm một đối tượng BinhLuan vào thẻ công việc."""
        from models.BinhLuan import BinhLuan
        if not isinstance(binh_luan, BinhLuan):
            raise DuLieuKhongHopLeError("Bình luận thêm vào phải là đối tượng BinhLuan")
        self._danh_sach_binh_luan.append(binh_luan)
        return True

    def xoa_binh_luan(self, ma_binh_luan: str):
        """Xóa bình luận theo mã."""
        bl = next((b for b in self._danh_sach_binh_luan if b.ma_binh_luan == ma_binh_luan), None)
        if bl is None:
            raise KhongTimThayError(
                f"Không tìm thấy bình luận '{ma_binh_luan}' trong công việc '{self.ma_cong_viec}'",
                loai_tai_nguyen="BinhLuan",
                khoa_tim_kiem=ma_binh_luan
            )
        self._danh_sach_binh_luan.remove(bl)
        return bl

    # ==================== TÍNH TRỪU TƯỢNG & ĐA HÌNH ====================
    @abstractmethod
    def canh_bao(self) -> str:
        """Phương thức trừu tượng cảnh báo thời hạn. Các lớp con bắt buộc phải triển khai."""
        pass

    @abstractmethod
    def lay_loai_cong_viec(self) -> str:
        """Trả về tên phân loại của công việc."""
        pass

    # ==================== PHƯƠNG THỨC NGHIỆP VỤ ====================
    def cap_nhat_cong_viec(self, data: dict):
        """Cập nhật dữ liệu công việc từ dictionary."""
        if not isinstance(data, dict):
            raise DuLieuKhongHopLeError("Dữ liệu cập nhật công việc phải là dictionary")

        if "TieuDe" in data or "tieu_de" in data:
            self.tieu_de = data.get("TieuDe", data.get("tieu_de"))
        if "MoTa" in data or "mo_ta" in data:
            self.mo_ta = data.get("MoTa", data.get("mo_ta"))
        if "NguoiPhuTrach" in data or "nguoi_phu_trach" in data:
            self.nguoi_phu_trach = data.get("NguoiPhuTrach", data.get("nguoi_phu_trach"))
        if "NgayBatDau" in data or "ngay_bat_dau" in data:
            self.ngay_bat_dau = data.get("NgayBatDau", data.get("ngay_bat_dau"))
        if "NgayKetThuc" in data or "ngay_ket_thuc" in data:
            self.ngay_ket_thuc = data.get("NgayKetThuc", data.get("ngay_ket_thuc"))
        if "TrangThai" in data or "trang_thai" in data:
            self.trang_thai = data.get("TrangThai", data.get("trang_thai"))
        if "MucUuTien" in data or "muc_uu_tien" in data:
            self.muc_uu_tien = data.get("MucUuTien", data.get("muc_uu_tien"))
        if "Nhan" in data or "nhan" in data:
            self.nhan = data.get("Nhan", data.get("nhan"))

    def to_dict(self):
        """Chuyển đổi thông tin đối tượng sang dictionary để lưu trữ."""
        return {
            "LoaiCongViec": self.__class__.__name__,
            "MaCongViec": self.ma_cong_viec,
            "TieuDe": self.tieu_de,
            "MoTa": self.mo_ta,
            "NguoiPhuTrach": self.nguoi_phu_trach,
            "NgayBatDau": self.ngay_bat_dau,
            "NgayKetThuc": self.ngay_ket_thuc,
            "TrangThai": self.trang_thai,
            "MucUuTien": self.muc_uu_tien,
            "Nhan": self.nhan,
            "DanhSachBinhLuan": [bl.to_dict() for bl in self.danh_sach_binh_luan]
        }

    @classmethod
    def from_dict(cls, data):
        """Factory Method: Khởi tạo đối tượng cụ thể phù hợp từ dictionary."""
        if not isinstance(data, dict):
            raise DuLieuKhongHopLeError("Dữ liệu công việc phải là dictionary")

        from models.BinhLuan import BinhLuan
        du_lieu_bl = data.get("DanhSachBinhLuan", [])
        danh_sach_bl = []
        if isinstance(du_lieu_bl, list):
            for bl_item in du_lieu_bl:
                if isinstance(bl_item, dict):
                    danh_sach_bl.append(BinhLuan.from_dict(bl_item))

        loai = data.get("LoaiCongViec")
        muc_uu_tien = data.get("MucUuTien")

        if loai == "CongViecKhan" or muc_uu_tien == "Khẩn":
            from .CongViecKhan import CongViecKhan
            return CongViecKhan(
                ma_cong_viec=data.get("MaCongViec"),
                tieu_de=data.get("TieuDe"),
                mo_ta=data.get("MoTa", ""),
                nguoi_phu_trach=data.get("NguoiPhuTrach"),
                ngay_bat_dau=data.get("NgayBatDau"),
                ngay_ket_thuc=data.get("NgayKetThuc"),
                trang_thai=data.get("TrangThai", "Cần làm"),
                nhan=data.get("Nhan"),
                danh_sach_binh_luan=danh_sach_bl
            )

        from .CongViecThuong import CongViecThuong
        return CongViecThuong(
            ma_cong_viec=data.get("MaCongViec"),
            tieu_de=data.get("TieuDe"),
            mo_ta=data.get("MoTa", ""),
            nguoi_phu_trach=data.get("NguoiPhuTrach"),
            ngay_bat_dau=data.get("NgayBatDau"),
            ngay_ket_thuc=data.get("NgayKetThuc"),
            trang_thai=data.get("TrangThai", "Cần làm"),
            muc_uu_tien=data.get("MucUuTien", "Trung bình"),
            nhan=data.get("Nhan"),
            danh_sach_binh_luan=danh_sach_bl
        )

    def chuyen_trang_thai(self, trang_thai_moi):
        trang_thai_cu = self.trang_thai
        self.trang_thai = trang_thai_moi
        return trang_thai_cu, trang_thai_moi

    def tinh_ngay_con_lai(self):
        if not self.ngay_ket_thuc:
            return None
        hom_nay = datetime.now().date()
        ket_thuc = datetime.strptime(self.ngay_ket_thuc, "%Y-%m-%d").date()
        return (ket_thuc - hom_nay).days

    def tinh_ngay_da_qua(self):
        if not self.ngay_bat_dau:
            return None
        hom_nay = datetime.now().date()
        bat_dau = datetime.strptime(self.ngay_bat_dau, "%Y-%m-%d").date()
        return (hom_nay - bat_dau).days

    def da_qua_han(self):
        ngay_con_lai = self.tinh_ngay_con_lai()
        return ngay_con_lai is not None and ngay_con_lai < 0

    def is_hoan_thanh(self):
        return self.trang_thai.lower() == "hoàn thành"

    def __str__(self):
        return (f"{self.__class__.__name__}(MaCongViec={self.ma_cong_viec}, "
                f"TieuDe='{self.tieu_de}', TrangThai='{self.trang_thai}', "
                f"MucUuTien='{self.muc_uu_tien}', Nhan='{self.nhan}', "
                f"SoBinhLuan={len(self.danh_sach_binh_luan)})")

    def __repr__(self):
        return self.__str__()
